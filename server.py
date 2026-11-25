"""Presentation/API boundary: run `python server.py` then open http://localhost:8000"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode
import base64
import hashlib
import hmac
import json
import os
import secrets
import ssl
import urllib.request
from http.cookies import SimpleCookie

from app import auth, data, dorar, service, shamela
from app.oop import (ResearchService, CatalogImportService, CatalogRepository,
                     AdminAuthenticator, AccountService)
from app.uml import Admin as UMLAdmin
from app.diagram_classes import UI as DiagramUI

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "").strip()
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"

research = ResearchService()
imports = CatalogImportService()
repository = CatalogRepository()
admin_auth = AdminAuthenticator()
account_service = AccountService()
uml_ui = DiagramUI()
uml_admin = UMLAdmin()
ROOT = Path(__file__).resolve().parent


def google_enabled():
    return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "static"), **kwargs)

    def send_json(self, code, payload, cookies=()):
        b = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        for cookie in cookies:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(b)

    def redirect_to(self, location, cookies=()):
        self.send_response(302)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.send_header("Cache-Control", "no-store")
        for cookie in cookies:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()

    def secure_cookie(self):
        host = self.headers.get("Host", "")
        return "" if host.startswith(("localhost:", "127.0.0.1")) else "; Secure"

    def session_cookie(self, token):
        return (f"account_session={token}; HttpOnly; SameSite=Strict; "
                f"Path=/; Max-Age={account_service.SESSION_SECONDS}{self.secure_cookie()}")

    def oauth_cookie(self, name, value):
        return (f"{name}={value}; HttpOnly; SameSite=Lax; Path=/; Max-Age=600"
                f"{self.secure_cookie()}")

    @property
    def CLEAR_ADMIN_COOKIE(self):
        return f"admin_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0{self.secure_cookie()}"

    @property
    def CLEAR_ACCOUNT_COOKIE(self):
        return f"account_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0{self.secure_cookie()}"

    @property
    def CLEAR_OAUTH_STATE(self):
        return f"google_state=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0{self.secure_cookie()}"

    @property
    def CLEAR_OAUTH_VERIFIER(self):
        return f"google_verifier=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0{self.secure_cookie()}"

    def _cookies(self):
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get("Cookie", ""))
        except Exception:
            return {}
        return cookie

    def current_identity(self):
        cookie = self._cookies()
        if "account_session" in cookie:
            user = account_service.identity(cookie["account_session"].value)
            if user:
                return user
        if "admin_session" in cookie and admin_auth.authorized(cookie["admin_session"].value):
            return {"username": "admin", "email": "admin@localhost.local",
                    "role": "admin", "provider": "local", "admin": True}
        return None

    def is_admin(self):
        user = self.current_identity()
        return bool(user and user.get("admin"))

    def same_origin(self):
        """Allow same-origin fetches on localhost and on a deployed HTTPS host."""
        origin = self.headers.get("Origin")
        if not origin:
            return True
        parsed = urlparse(origin)
        host = self.headers.get("Host", "")
        if parsed.netloc != host:
            return False
        if host.startswith(("localhost:", "127.0.0.1")):
            return parsed.scheme == "http"
        return parsed.scheme == "https"

    def ssl_context(self):
        bundle = ROOT / "app" / "cacert.pem"
        if bundle.exists():
            return ssl.create_default_context(cafile=str(bundle))
        return ssl.create_default_context()

    def google_redirect_uri(self):
        if GOOGLE_REDIRECT_URI:
            return GOOGLE_REDIRECT_URI
        host = self.headers.get("Host", "127.0.0.1:8000")
        scheme = "http" if host.startswith(("localhost:", "127.0.0.1")) else "https"
        return f"{scheme}://{host}/api/auth/google/callback"

    def google_start(self):
        if not google_enabled():
            return self.send_json(503, {"error": "Google sign-in is not configured"})
        state = secrets.token_urlsafe(24)
        verifier = secrets.token_urlsafe(48)
        challenge = base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode()).digest()
        ).decode().rstrip("=")
        params = {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": self.google_redirect_uri(),
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "access_type": "online",
            "prompt": "select_account",
        }
        cookies = (self.oauth_cookie("google_state", state),
                   self.oauth_cookie("google_verifier", verifier))
        return self.send_json(
            200, {"url": GOOGLE_AUTH_URL + "?" + urlencode(params)}, cookies
        )

    def google_callback(self):
        clear = (self.CLEAR_OAUTH_STATE, self.CLEAR_OAUTH_VERIFIER)
        query = parse_qs(urlparse(self.path).query)
        code = (query.get("code") or [""])[0]
        state = (query.get("state") or [""])[0]
        cookies = self._cookies()
        expected = cookies["google_state"].value if "google_state" in cookies else ""
        verifier = cookies["google_verifier"].value if "google_verifier" in cookies else ""
        if not code or not state or not expected or not hmac.compare_digest(state, expected):
            return self.redirect_to("/?auth_error=google_state", clear)
        try:
            token_payload = urlencode({
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": self.google_redirect_uri(),
                "grant_type": "authorization_code",
                "code_verifier": verifier,
            }).encode()
            token_request = urllib.request.Request(
                GOOGLE_TOKEN_URL, data=token_payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            with urllib.request.urlopen(
                token_request, context=self.ssl_context(), timeout=20
            ) as response:
                token_data = json.loads(response.read().decode())
            access_token = token_data["access_token"]

            info_request = urllib.request.Request(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            with urllib.request.urlopen(
                info_request, context=self.ssl_context(), timeout=20
            ) as response:
                info = json.loads(response.read().decode())

            verified = info.get("email_verified") is True or str(
                info.get("email_verified", "")
            ).lower() == "true"
            if not verified or not info.get("email") or not info.get("sub"):
                return self.redirect_to("/?auth_error=google_unverified", clear)

            token, user = account_service.google_login(
                info["email"], info.get("name", ""), info["sub"]
            )
            success_cookies = (self.session_cookie(token), self.CLEAR_ADMIN_COOKIE) + clear
            return self.redirect_to("/?google=ok", success_cookies)
        except Exception:
            return self.redirect_to("/?auth_error=google_failed", clear)

    def do_POST(self):
        path = urlparse(self.path).path
        allowed = (
            "/api/search", "/api/quotes", "/api/books/search", "/api/books/import",
            "/api/search/all", "/api/shamela/search", "/api/dorar/search", "/api/history",
            "/api/history/clear", "/api/auth/setup", "/api/auth/register",
            "/api/auth/login", "/api/auth/logout", "/api/admin/setup",
            "/api/admin/login", "/api/admin/logout", "/api/admin/hadith",
            "/api/admin/delete",
        )
        if path not in allowed:
            return self.send_json(404, {"error": "Not found"})
        if not self.same_origin():
            return self.send_json(403, {"error": "Cross-origin request denied"})
        if path in ("/api/quotes", "/api/books/import", "/api/admin/hadith",
                    "/api/admin/delete", "/api/admin/logout") and not self.is_admin():
            return self.send_json(403, {"error": "Admin login required"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > 2800000:
                return self.send_json(413, {"error": "Invalid request size"})
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                raise ValueError("Expected an object")

            if path == "/api/auth/setup":
                user = account_service.setup_admin(
                    payload.get("username"), payload.get("password"), payload.get("email")
                )
                authenticated = account_service.login(user["username"], payload.get("password"))
                cookies = (self.session_cookie(authenticated[0]),
                           self.CLEAR_ADMIN_COOKIE) if authenticated else ()
                return self.send_json(
                    200, {"message": "Administrator account created", "user": user}, cookies
                )
            elif path == "/api/auth/register":
                user = account_service.register(
                    payload.get("username"), payload.get("password"), payload.get("email")
                )
                authenticated = account_service.login(user["username"], payload.get("password"))
                cookies = (self.session_cookie(authenticated[0]),
                           self.CLEAR_ADMIN_COOKIE) if authenticated else ()
                return self.send_json(
                    200, {"message": "Account created", "user": user}, cookies
                )
            elif path == "/api/auth/login":
                identifier = payload.get("username") or payload.get("email")
                authenticated = account_service.login(identifier, payload.get("password"))
                if not authenticated:
                    return self.send_json(401, {"error": "Incorrect username or password"})
                token, user = authenticated
                return self.send_json(
                    200, {"message": "Logged in", "user": user},
                    (self.session_cookie(token), self.CLEAR_ADMIN_COOKIE)
                )
            elif path == "/api/auth/logout":
                user = self.current_identity()
                if user:
                    account_service.logout(user["username"])
                return self.send_json(
                    200, {"message": "Logged out"},
                    (self.CLEAR_ACCOUNT_COOKIE, self.CLEAR_ADMIN_COOKIE)
                )
            elif path == "/api/history":
                user = self.current_identity()
                if not user:
                    return self.send_json(401, {"error": "Sign-in required"})
                account_service.record_history(
                    user["username"], payload.get("query"),
                    payload.get("scope", "shamela"), payload.get("result_count", 0)
                )
                result = {"message": "Recorded"}
            elif path == "/api/history/clear":
                user = self.current_identity()
                if not user:
                    return self.send_json(401, {"error": "Sign-in required"})
                account_service.clear_history(user["username"])
                result = {"message": "History cleared"}
            elif path == "/api/admin/setup":
                if admin_auth.configured():
                    return self.send_json(403, {"error": "Admin already configured"})
                admin_auth.setup(payload.get("password"))
                result = {"message": "Admin password created. Log in to manage records."}
            elif path == "/api/admin/login":
                token = admin_auth.login(payload.get("password"))
                if not token:
                    return self.send_json(401, {"error": "Incorrect password"})
                cookie = (f"admin_session={token}; HttpOnly; SameSite=Strict; "
                          f"Path=/; Max-Age={auth.SESSION_SECONDS}{self.secure_cookie()}")
                return self.send_json(
                    200, {"message": "Logged in"}, (cookie, self.CLEAR_ACCOUNT_COOKIE)
                )
            elif path == "/api/admin/logout":
                admin_auth.logout_all()
                return self.send_json(
                    200, {"message": "Logged out"},
                    (self.CLEAR_ADMIN_COOKIE, self.CLEAR_ACCOUNT_COOKIE)
                )
            elif path == "/api/admin/hadith":
                result = uml_admin.addHadith(payload, authorized=True)
            elif path == "/api/admin/delete":
                result = imports.delete_record(payload)
            elif path == "/api/search/all":
                result = {"results": uml_ui.sendText(
                    payload.get("query"), payload.get("kind", "hadith")
                )}
            elif path == "/api/shamela/search":
                result = {"results": shamela.search(
                    payload.get("query"), payload.get("kind", "all")
                )}
            elif path == "/api/dorar/search":
                result = {"results": dorar.search(payload.get("query"))}
            elif path == "/api/search":
                result = {"results": uml_ui.sendText(
                    payload.get("query"), payload.get("kind", "hadith")
                )}
            elif path == "/api/books/search":
                result = {"results": research.search_books(
                    payload.get("kind"), payload.get("query")
                )}
            elif path == "/api/books/import":
                result = uml_admin.importRecords(
                    payload.get("filename"), payload.get("content"), authorized=True
                )
            else:
                result = imports.create_quote(payload)
            self.send_json(200, result)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self.send_json(400, {"error": str(exc)})
        except shamela.ShamelaError as exc:
            self.send_json(502, {"error": str(exc)})
        except dorar.DorarError as exc:
            self.send_json(502, {"error": str(exc)})
        except Exception:
            self.send_json(500, {"error": "Unexpected server error"})

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/auth/status":
            user = self.current_identity()
            return self.send_json(200, {
                "user": user,
                "admin": bool(user and user.get("admin")),
                "needsSetup": account_service.count() == 0,
                "configured": account_service.has_admin() or admin_auth.configured(),
                "googleEnabled": google_enabled(),
            })
        if path == "/api/admin/status":
            user = self.current_identity()
            return self.send_json(200, {
                "configured": account_service.has_admin() or admin_auth.configured(),
                "admin": bool(user and user.get("admin")),
                "user": user,
                "needsSetup": account_service.count() == 0,
                "googleEnabled": google_enabled(),
            })
        if path == "/api/auth/google/start":
            return self.google_start()
        if path == "/api/auth/google/callback":
            return self.google_callback()
        if path == "/api/admin/users":
            if not self.is_admin():
                return self.send_json(403, {"error": "Admin login required"})
            return self.send_json(200, {"users": account_service.list_accounts()})
        if path == "/api/history":
            user = self.current_identity()
            if not user:
                return self.send_json(401, {"error": "Sign-in required"})
            return self.send_json(200, {"history": account_service.history(user["username"])})
        if path == "/api/admin/records":
            if not self.is_admin():
                return self.send_json(403, {"error": "Admin login required"})
            return self.send_json(200, {"records": repository.admin_records()})
        if path == "/api/catalog/stats":
            return self.send_json(200, repository.stats())
        if path == "/api/books/stats":
            return self.send_json(200, {"imports": repository.import_stats()})
        if path == "/api/health":
            return self.send_json(200, {"status": "ok"})
        return super().do_GET()


# Vercel can also detect this root file as a Python entrypoint. Exporting the
# same handler keeps that build valid even though vercel.json routes /api/* to
# api/index.py.
handler = Handler


if __name__ == "__main__":
    repository.initialize()
    admin_auth.initialize()
    account_service.initialize()
    port = int(os.environ.get("PORT", "8000"))
    print(f"Open http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
