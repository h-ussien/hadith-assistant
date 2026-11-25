"""Data access layer: local SQLite catalog, or Postgres when deployed serverless.

Local runs use ``research.db`` exactly as before. On Vercel the filesystem is
read-only, so setting ``DATABASE_URL`` (or the Neon/Vercel equivalents) switches
this module to Postgres without changing any caller.
"""
import os
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "research.db"
SEED = [
    ('hadith','إنما الأعمال بالنيات','صحيح البخاري','محمد بن إسماعيل البخاري','1','كتاب بدء الوحي','1',None,'https://sunnah.com/bukhari:1','Sahih al-Bukhari 1; verify edition-specific page separately'),
    ('hadith','إنما الأعمال بالنيات','صحيح مسلم','مسلم بن الحجاج','1907','كتاب الإمارة','1907',None,'https://sunnah.com/muslim:1907a','Sahih Muslim 1907a; numbering may vary by edition'),
    ('hadith','من كان يؤمن بالله واليوم الآخر فليقل خيرا أو ليصمت','صحيح البخاري','محمد بن إسماعيل البخاري','6018','كتاب الأدب','6018',None,'https://sunnah.com/bukhari:6018','verify exact wording and edition'),
    ('hadith','الدين النصيحة','صحيح مسلم','مسلم بن الحجاج','55','كتاب الإيمان','55',None,'https://sunnah.com/muslim:55a','Sahih Muslim 55a; verify exact wording and edition'),
]

_PSYCOPG = None
_PG_IMPORT_ERROR = None


def _database_url():
    """Pick up the connection string injected by Vercel/Neon integrations."""
    for name in ("DATABASE_URL", "POSTGRES_URL", "NEON_DATABASE_URL"):
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""


def _psycopg():
    global _PSYCOPG, _PG_IMPORT_ERROR
    if _PSYCOPG is None and _PG_IMPORT_ERROR is None:
        try:
            import psycopg
            from psycopg.rows import dict_row
            _PSYCOPG = (psycopg, dict_row)
        except ImportError as exc:  # pragma: no cover - depends on deployment env
            _PG_IMPORT_ERROR = exc
    if _PG_IMPORT_ERROR is not None:
        raise RuntimeError(
            "DATABASE_URL is set but psycopg is not installed. "
            "Add psycopg[binary] to requirements.txt."
        ) from _PG_IMPORT_ERROR
    return _PSYCOPG


def _pg_sql(sql):
    """Translate the small SQLite dialect used here into Postgres SQL."""
    value = re.sub(r":([a-zA-Z_]\w*)", r"%(\1)s", sql)
    value = value.replace("?", "%s")
    value = value.replace("id INTEGER PRIMARY KEY AUTOINCREMENT", "id SERIAL PRIMARY KEY")
    value = value.replace("id INTEGER PRIMARY KEY,", "id SERIAL PRIMARY KEY,")
    value = value.replace(" COLLATE NOCASE", "")
    if "INSERT OR IGNORE INTO" in value:
        value = value.replace("INSERT OR IGNORE INTO", "INSERT INTO")
        value = value.rstrip().rstrip(";") + " ON CONFLICT DO NOTHING"
    return value


class _PgConnection:
    """Minimal adapter so existing sqlite3-style callers work on Postgres."""

    def __init__(self, connection):
        self._connection = connection

    def execute(self, sql, params=()):
        return self._connection.execute(_pg_sql(sql), tuple(params) if params else None)

    def executemany(self, sql, rows):
        return self._connection.executemany(_pg_sql(sql), rows)

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()


def is_postgres():
    return bool(_database_url())


@contextmanager
def connect():
    """Yield a row-capable connection, commit on success, and always close it.

    SQLite's built-in ``with`` support commits/rolls back but does not close the
    connection, which leaves the database file locked on Windows until garbage
    collection. Every caller uses this helper as a context manager, so closing
    here keeps temporary test databases and the running app deterministic.
    """
    url = _database_url()
    if url:
        driver, dict_row = _psycopg()
        raw = driver.connect(url, row_factory=dict_row)
        con = _PgConnection(raw)
    else:
        raw = sqlite3.connect(DB)
        raw.row_factory = sqlite3.Row
        con = raw
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def table_columns(connection, table):
    """Column names for migration checks on either database backend."""
    if isinstance(connection, _PgConnection):
        rows = connection.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name=%s",
            (table,),
        ).fetchall()
        return {row["column_name"] for row in rows}
    return {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}


def initialize():
    with connect() as c:
        c.execute('''CREATE TABLE IF NOT EXISTS sources (id INTEGER PRIMARY KEY, kind TEXT NOT NULL, passage TEXT NOT NULL, book TEXT NOT NULL, author TEXT NOT NULL, reference TEXT, chapter TEXT, hadith_number TEXT, volume TEXT, page TEXT, url TEXT, note TEXT, UNIQUE(kind,passage,book,reference))''')
        for kind,passage,book,author,ref,chapter,num,page,url,note in SEED:
            c.execute('''INSERT OR IGNORE INTO sources(kind,passage,book,author,reference,chapter,hadith_number,page,url,note) VALUES(?,?,?,?,?,?,?,?,?,?)''',(kind,passage,book,author,ref,chapter,num,page,url,note))

def get_all(kind):
    with connect() as c:
        return [dict(x) for x in c.execute('SELECT * FROM sources WHERE kind=? ORDER BY id',(kind,))]

def add_quote(passage,book,author,volume,page,reference,url,note):
    with connect() as c:
        c.execute('INSERT INTO sources(kind,passage,book,author,volume,page,reference,url,note) VALUES(?,?,?,?,?,?,?,?,?)',('quote',passage,book,author,volume,page,reference,url,note))

# User-imported, locally indexed book passages. No external corpus is bundled.
def initialize_books():
    with connect() as c:
        c.execute('''CREATE TABLE IF NOT EXISTS book_passages (id INTEGER PRIMARY KEY, kind TEXT NOT NULL, passage TEXT NOT NULL, book TEXT NOT NULL, author TEXT NOT NULL, chapter TEXT, hadith_number TEXT, volume TEXT, page TEXT, edition TEXT, url TEXT, note TEXT, import_name TEXT NOT NULL)''')
        c.execute('CREATE INDEX IF NOT EXISTS idx_book_kind ON book_passages(kind)')

def add_book_passages(records, import_name):
    with connect() as c:
        c.executemany('''INSERT INTO book_passages(kind,passage,book,author,chapter,hadith_number,volume,page,edition,url,note,import_name) VALUES(:kind,:passage,:book,:author,:chapter,:hadith_number,:volume,:page,:edition,:url,:note,:import_name)''', [dict(r,import_name=import_name) for r in records])

def get_book_passages(kind):
    with connect() as c:
        return [dict(r) for r in c.execute('SELECT * FROM book_passages WHERE kind=? ORDER BY id',(kind,))]

def book_stats():
    with connect() as c:
        return [dict(r) for r in c.execute('SELECT import_name,kind,COUNT(*) AS count FROM book_passages GROUP BY import_name,kind ORDER BY import_name')]


def catalog_stats():
    with connect() as c:
        base=[dict(r) for r in c.execute('SELECT kind, COUNT(*) AS count FROM sources GROUP BY kind')]
        imports=[dict(r) for r in c.execute('SELECT kind, COUNT(*) AS count FROM book_passages GROUP BY kind')]
    return {'demonstration_and_manual':base,'imported':imports}

def catalog_browse(kind,limit=100):
    with connect() as c:
        base=[dict(r) for r in c.execute('SELECT * FROM sources WHERE kind=? ORDER BY id LIMIT ?', (kind,limit))]
        imported=[dict(r) for r in c.execute('SELECT * FROM book_passages WHERE kind=? ORDER BY id LIMIT ?', (kind,limit))]
    for row in base:row['provenance']='local demonstration or manually added record'
    for row in imported:row['provenance']='user-imported; not independently verified'
    return (base+imported)[:limit]

def add_hadith(passage,book,author,reference,chapter,hadith_number,url,note):
    with connect() as c:
        c.execute('INSERT INTO sources(kind,passage,book,author,reference,chapter,hadith_number,url,note) VALUES(?,?,?,?,?,?,?,?,?)',('hadith',passage,book,author,reference,chapter,hadith_number,url,note))

def admin_records():
    with connect() as c:
        return [dict(r) for r in c.execute('SELECT id,kind,book,author,passage,reference FROM sources ORDER BY id DESC LIMIT 250')]

def delete_record(record_id):
    with connect() as c:
        result=c.execute('DELETE FROM sources WHERE id=?',(record_id,))
        return result.rowcount
