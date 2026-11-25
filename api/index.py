"""Vercel WSGI entrypoint.

Vercel rewrites ``/api/*`` to this function. The app's real routing already
lives in ``server.Handler``; this small bridge turns a WSGI request into the
BaseHTTPRequestHandler call that Handler expects, so local and deployed runs
share exactly the same code.
"""
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import server  # noqa: E402  (path setup must happen first)

# Serverless functions start cold, so schema creation must not depend on the
# local ``python server.py`` entrypoint.
server.repository.initialize()
server.admin_auth.initialize()
server.account_service.initialize()


class _Socket:
    """Enough of a socket for BaseHTTPRequestHandler to read and write bytes."""

    def __init__(self, request_bytes):
        self._reader = io.BytesIO(request_bytes)
        self.writer = io.BytesIO()

    def makefile(self, mode="r", bufsize=-1):
        return self._reader if "r" in mode else self.writer

    def sendall(self, data):
        # socketserver wraps wfile in a _SocketWriter, which calls sendall().
        self.writer.write(data)


def _request_path(environ):
    # Vercel sets PATH_INFO to the rewritten function path; REQUEST_URI keeps
    # the original route the browser asked for.
    original = environ.get("REQUEST_URI") or environ.get("RAW_URI") or ""
    path = environ.get("PATH_INFO", "") or "/"
    if original and original != path:
        return original
    query = environ.get("QUERY_STRING", "")
    return path + ("?" + query if query else "")


def _raw_request(environ):
    method = environ.get("REQUEST_METHOD", "GET")
    host = environ.get("HTTP_HOST") or environ.get("SERVER_NAME", "localhost")
    headers = [f"{method} {_request_path(environ)} HTTP/1.1", f"Host: {host}"]
    for header, key in (
        ("Content-Type", "CONTENT_TYPE"),
        ("Cookie", "HTTP_COOKIE"),
        ("Origin", "HTTP_ORIGIN"),
        ("Referer", "HTTP_REFERER"),
        ("User-Agent", "HTTP_USER_AGENT"),
        ("Accept", "HTTP_ACCEPT"),
        ("Accept-Language", "HTTP_ACCEPT_LANGUAGE"),
    ):
        value = environ.get(key)
        if value:
            headers.append(f"{header}: {value}")
    size = int(environ.get("CONTENT_LENGTH") or 0)
    body = environ["wsgi.input"].read(size) if size else b""
    headers.append(f"Content-Length: {size}")
    return ("\r\n".join(headers) + "\r\n\r\n").encode("latin-1", "replace") + body


def app(environ, start_response):
    sock = _Socket(_raw_request(environ))
    # BaseHTTPRequestHandler handles one request inside __init__; do not call
    # handle_one_request() again here.
    server.Handler(sock, ("127.0.0.1", 0), None)

    head, _, body = sock.writer.getvalue().partition(b"\r\n\r\n")
    status_line, _, header_lines = head.partition(b"\r\n")
    status = status_line.decode("latin-1").partition(" ")[2] or "500 Internal Server Error"
    response_headers = []
    for line in header_lines.split(b"\r\n"):
        if not line:
            continue
        key, _, value = line.partition(b":")
        response_headers.append((key.decode("latin-1"), value.decode("latin-1").strip()))
    start_response(status, response_headers)
    return [body]
