import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from app import data
import server

ROOT = Path(__file__).resolve().parent.parent


class TestVercelDeployment(unittest.TestCase):
    def test_vercel_config_routes_api_and_static_files(self):
        config = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
        destinations = {rule["source"]: rule["destination"] for rule in config["rewrites"]}
        self.assertEqual(destinations["/api/(.*)"], "/api/index.py")
        self.assertEqual(destinations["/app.js"], "/static/app.js")
        self.assertEqual(destinations["/style.css"], "/static/style.css")
        self.assertEqual(destinations["/"], "/static/index.html")
        self.assertEqual(config["functions"]["api/index.py"]["maxDuration"], 60)

    def test_postgres_sql_translation(self):
        sql = data._pg_sql(
            "INSERT OR IGNORE INTO sources(kind) VALUES(:kind) "
            "SELECT * FROM sources WHERE kind=?"
        )
        self.assertIn("INSERT INTO sources(kind) VALUES(%(kind)s)", sql)
        self.assertIn("kind=%s", sql)
        self.assertIn("ON CONFLICT DO NOTHING", sql)
        self.assertIn("id SERIAL PRIMARY KEY", data._pg_sql("id INTEGER PRIMARY KEY,"))
        self.assertIn("id SERIAL PRIMARY KEY", data._pg_sql("id INTEGER PRIMARY KEY AUTOINCREMENT"))

    def test_database_url_selects_postgres_mode(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(data.is_postgres())
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}):
            self.assertTrue(data.is_postgres())

    def test_same_origin_accepts_local_http_and_deployed_https(self):
        handler = object.__new__(server.Handler)
        handler.headers = {"Origin": "http://127.0.0.1:8000", "Host": "127.0.0.1:8000"}
        self.assertTrue(handler.same_origin())
        handler.headers = {
            "Origin": "https://example.vercel.app",
            "Host": "example.vercel.app",
        }
        self.assertTrue(handler.same_origin())
        handler.headers = {
            "Origin": "https://evil.example",
            "Host": "example.vercel.app",
        }
        self.assertFalse(handler.same_origin())

    def test_deployed_callback_uses_https(self):
        handler = object.__new__(server.Handler)
        handler.headers = {"Host": "example.vercel.app"}
        self.assertEqual(
            handler.google_redirect_uri(),
            "https://example.vercel.app/api/auth/google/callback",
        )
        handler.headers = {"Host": "localhost:8000"}
        self.assertEqual(
            handler.google_redirect_uri(),
            "http://localhost:8000/api/auth/google/callback",
        )


if __name__ == "__main__":
    unittest.main()
