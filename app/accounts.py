"""Role-aware local/Google accounts and signed session tokens.

The first local account created is an administrator; later accounts are regular
users. Google/Gmail accounts are always regular users. The pre-existing
single-password admin setup is migrated on startup so old installations work.
"""
from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import time

from . import data

SESSION_SECONDS = 8 * 3600
USERNAME_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]{1,30}[a-z0-9]$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ROLES = ("admin", "user")
PROVIDERS = ("local", "google")


def initialize():
    """Create/migrate account tables and migrate a legacy admin password."""
    with data.connect() as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS accounts (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                   email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                   salt TEXT NOT NULL,
                   password_hash TEXT NOT NULL,
                   role TEXT NOT NULL CHECK(role IN ('admin','user')),
                   provider TEXT NOT NULL DEFAULT 'local' CHECK(provider IN ('local','google')),
                   google_sub TEXT UNIQUE,
                   session_secret TEXT NOT NULL,
                   created_at REAL NOT NULL
               )"""
        )
        columns = data.table_columns(c, "accounts")
        if "email" not in columns:
            c.execute("ALTER TABLE accounts ADD COLUMN email TEXT")
        if "provider" not in columns:
            c.execute("ALTER TABLE accounts ADD COLUMN provider TEXT NOT NULL DEFAULT 'local'")
        if "google_sub" not in columns:
            c.execute("ALTER TABLE accounts ADD COLUMN google_sub TEXT")
        c.execute("UPDATE accounts SET email=? WHERE email IS NULL OR TRIM(email)=''",
                  (None,))
        rows = c.execute("SELECT id,username,email FROM accounts").fetchall()
        for row in rows:
            if not row["email"]:
                candidate = f"{row['username']}@localhost.local"
                suffix = 1
                while c.execute("SELECT 1 FROM accounts WHERE email=? AND id<>?",
                                (candidate, row["id"])).fetchone():
                    suffix += 1
                    candidate = f"{row['username']}{suffix}@localhost.local"
                c.execute("UPDATE accounts SET email=? WHERE id=?", (candidate, row["id"]))
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS accounts_email_unique ON accounts(email COLLATE NOCASE)")
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS accounts_google_sub_unique ON accounts(google_sub) WHERE google_sub IS NOT NULL")
        c.execute(
            """CREATE TABLE IF NOT EXISTS search_history (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT NOT NULL,
                   query TEXT NOT NULL,
                   scope TEXT NOT NULL,
                   result_count INTEGER NOT NULL DEFAULT 0,
                   created_at REAL NOT NULL
               )"""
        )
        c.execute("CREATE INDEX IF NOT EXISTS search_history_user_time ON search_history(username, created_at DESC)")

    with data.connect() as c:
        legacy = c.execute(
            "SELECT salt,password_hash,session_secret FROM admin_auth WHERE id=1"
        ).fetchone()
    if legacy and not has_admin():
        with data.connect() as c:
            username = "admin"
            if c.execute("SELECT 1 FROM accounts WHERE username=?", (username,)).fetchone():
                username = "legacy-admin"
            email = f"{username}@localhost.local"
            c.execute(
                """INSERT INTO accounts
                   (username,email,salt,password_hash,role,provider,session_secret,created_at)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (username, email, legacy["salt"], legacy["password_hash"], "admin",
                 "local", legacy["session_secret"], time.time()),
            )


def count():
    with data.connect() as c:
        row = c.execute("SELECT COUNT(*) AS total FROM accounts").fetchone()
    return row["total"]


def has_admin():
    with data.connect() as c:
        return c.execute("SELECT 1 FROM accounts WHERE role='admin' LIMIT 1").fetchone() is not None


def _check_username(username):
    if not isinstance(username, str):
        raise ValueError("Username is required")
    normalized = username.strip().lower()
    if not USERNAME_RE.fullmatch(normalized):
        raise ValueError("Username must be 3-32 letters, numbers, dots, dashes, or underscores")
    return normalized


def _check_email(email):
    if not isinstance(email, str) or not email.strip():
        raise ValueError("Email is required")
    normalized = email.strip().lower()
    if len(normalized) > 254 or not EMAIL_RE.fullmatch(normalized):
        raise ValueError("Invalid email address")
    return normalized


def _check_identifier(identifier):
    if not isinstance(identifier, str) or not identifier.strip():
        raise ValueError("Username or email is required")
    value = identifier.strip().lower()
    return _check_email(value) if "@" in value else _check_username(value)


def _check_password(password, minimum):
    if not isinstance(password, str) or not minimum <= len(password) <= 256:
        raise ValueError(f"Password must contain {minimum}-256 characters")


def _hash(password, salt):
    return hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**14, r=8, p=1).hex()


def _user_dict(row):
    return {
        "username": row["username"],
        "email": row["email"],
        "role": row["role"],
        "provider": row["provider"],
        "admin": row["role"] == "admin",
    }


def _token_for(row):
    user = _user_dict(row)
    expires = str(int(time.time()) + SESSION_SECONDS)
    nonce = secrets.token_hex(12)
    message = f"{expires}.{nonce}.{user['username']}.{user['role']}"
    signature = hmac.new(
        bytes.fromhex(row["session_secret"]), message.encode(), "sha256"
    ).hexdigest()
    return f"{message}.{signature}", user


def _unique_username(base):
    cleaned = re.sub(r"[^a-z0-9._-]", "-", base.lower()).strip("._-")
    cleaned = cleaned[:30].strip("._-")
    if len(cleaned) < 3:
        cleaned = "user"
    candidate = cleaned
    suffix = 1
    with data.connect() as c:
        while c.execute("SELECT 1 FROM accounts WHERE username=?", (candidate,)).fetchone():
            suffix += 1
            tail = f"-{suffix}"
            candidate = cleaned[:32 - len(tail)] + tail
    return candidate


def _create(username, email, password, role, minimum, provider="local", google_sub=None):
    normalized = _check_username(username)
    normalized_email = _check_email(email)
    _check_password(password, minimum)
    salt = secrets.token_hex(16)
    with data.connect() as c:
        if c.execute("SELECT 1 FROM accounts WHERE username=?", (normalized,)).fetchone():
            raise ValueError("Username already exists")
        if c.execute("SELECT 1 FROM accounts WHERE email=?", (normalized_email,)).fetchone():
            raise ValueError("Email already registered")
        try:
            c.execute(
                """INSERT INTO accounts
                   (username,email,salt,password_hash,role,provider,google_sub,session_secret,created_at)
                   VALUES(?,?,?,?,?,?,?,?,?)""",
                (normalized, normalized_email, salt, _hash(password, salt), role,
                 provider, google_sub, secrets.token_hex(32), time.time()),
            )
        except Exception as exc:
            if "UNIQUE" in str(exc).upper():
                raise ValueError("Email already registered") from exc
            raise
    return {"username": normalized, "email": normalized_email, "role": role,
            "provider": provider, "admin": role == "admin"}


def register(username, password, email=None):
    """Create the first account as admin; every later account as a normal user."""
    first = count() == 0
    normalized_email = email or f"{_check_username(username)}@localhost.local"
    return _create(username, normalized_email, password,
                   "admin" if first else "user", 12 if first else 8)


def setup_admin(username, password, email=None):
    """Explicitly create the first admin account."""
    if count():
        raise ValueError("Admin account already configured")
    normalized_email = email or f"{_check_username(username)}@localhost.local"
    return _create(username, normalized_email, password, "admin", 12)


def google_login(email, name, subject):
    """Sign in or create a verified Google account. Google users are never admins."""
    normalized_email = _check_email(email)
    if not isinstance(subject, str) or not subject.strip():
        raise ValueError("Invalid Google account")
    subject = subject.strip()
    with data.connect() as c:
        row = c.execute("SELECT * FROM accounts WHERE google_sub=?", (subject,)).fetchone()
        if not row:
            row = c.execute("SELECT * FROM accounts WHERE email=?", (normalized_email,)).fetchone()
        if row and row["role"] != "user":
            raise ValueError("Email already registered")
        if row:
            c.execute(
                """UPDATE accounts SET email=?,google_sub=?,provider='google'
                   WHERE id=?""",
                (normalized_email, subject, row["id"]),
            )
            row = c.execute("SELECT * FROM accounts WHERE id=?", (row["id"],)).fetchone()
    if row:
        return _token_for(row)

    base = _unique_username(normalized_email.split("@")[0] or (name or "").strip())
    random_password = secrets.token_urlsafe(40)
    user = _create(base, normalized_email, random_password, "user", 8,
                   provider="google", google_sub=subject)
    with data.connect() as c:
        row = c.execute("SELECT * FROM accounts WHERE username=?", (user["username"],)).fetchone()
    return _token_for(row)


def login(identifier, password):
    normalized = _check_identifier(identifier)
    with data.connect() as c:
        row = c.execute(
            "SELECT * FROM accounts WHERE username=? OR email=?", (normalized, normalized)
        ).fetchone()
    if not row or not isinstance(password, str) or not hmac.compare_digest(
        _hash(password, row["salt"]), row["password_hash"]
    ):
        return None
    return _token_for(row)


def identity(token):
    try:
        expires, nonce, username, role, signature = token.split(".")
        if role not in ROLES:
            return None
        if int(expires) < time.time() or int(expires) > time.time() + SESSION_SECONDS + 60:
            return None
        with data.connect() as c:
            row = c.execute(
                "SELECT * FROM accounts WHERE username=?", (username,)
            ).fetchone()
        if not row or row["role"] != role:
            return None
        message = f"{expires}.{nonce}.{username}.{role}"
        expected = hmac.new(
            bytes.fromhex(row["session_secret"]), message.encode(), "sha256"
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            return None
        return _user_dict(row)
    except (ValueError, AttributeError, TypeError):
        return None


def logout(username):
    with data.connect() as c:
        c.execute(
            "UPDATE accounts SET session_secret=? WHERE username=?",
            (secrets.token_hex(32), username),
        )


def list_accounts():
    with data.connect() as c:
        rows = c.execute(
            """SELECT id,username,email,role,provider,google_sub,created_at
               FROM accounts ORDER BY role, username"""
        ).fetchall()
    return [dict(row) for row in rows]


def record_history(username, query, scope, result_count):
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query is required")
    with data.connect() as c:
        c.execute(
            """INSERT INTO search_history (username,query,scope,result_count,created_at)
               VALUES(?,?,?,?,?)""",
            (username, query.strip()[:2000], scope[:40], max(0, int(result_count)), time.time()),
        )


def history(username, limit=100):
    with data.connect() as c:
        rows = c.execute(
            """SELECT id,query,scope,result_count,created_at FROM search_history
               WHERE username=? ORDER BY created_at DESC,id DESC LIMIT ?""",
            (username, max(1, min(int(limit), 200))),
        ).fetchall()
    return [dict(row) for row in rows]


def clear_history(username):
    with data.connect() as c:
        c.execute("DELETE FROM search_history WHERE username=?", (username,))
