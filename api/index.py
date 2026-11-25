"""Vercel WSGI entrypoint.

Vercel rewrites ``/api/*`` to this function. The app's real routing already
lives in ``server.Handler``; this small bridge turns a WSGI request into the
BaseHTTPRequestHandler call that Handler expects, so local and deployed runs
share exactly the same code.
"""
from wsgi_bridge import app  # noqa: F401
