"""Object-oriented application facade. All original routes delegate to these classes."""
from . import domain, data, auth, accounts
from . import service as legacy

class CitationFormatter:
    def generate_footnote(self, record):
        return domain.footnote(record)

class HadithMatcher:
    def normalize(self, text):
        return domain.normalize(text)
    def score(self, query, passage):
        return domain.score(query, passage)
    def find_hadith(self, query, records):
        return domain.find_matches(query, records)

class CatalogRepository:
    def initialize(self):
        data.initialize(); data.initialize_books()
    def get_all(self, kind):
        return data.get_all(kind)
    def get_imported(self, kind):
        return data.get_book_passages(kind)
    def browse(self, kind, limit=100):
        return data.catalog_browse(kind, limit)
    def store_import(self, records, filename):
        return data.add_book_passages(records, filename)
    def stats(self):
        return data.catalog_stats()
    def import_stats(self):
        return data.book_stats()
    def admin_records(self):
        return data.admin_records()

class ResearchService:
    def __init__(self, repository=None, matcher=None, citation=None):
        self.repository = repository or CatalogRepository()
        self.matcher = matcher or HadithMatcher()
        self.citation = citation or CitationFormatter()
    def search_hadith(self, query):
        return self.search_all('hadith', query)
    def search_quote(self, query):
        return self.search_all('quote', query)
    def search(self, kind, query):
        self._validate(kind, query)
        return self.matcher.find_hadith(query, self.repository.get_all(kind))
    def search_books(self, kind, query):
        self._validate(kind, query)
        return legacy.search_books(kind, query)
    def search_all(self, kind, query):
        self._validate(kind, query)
        base = self.matcher.find_hadith(query, self.repository.get_all(kind))
        imported = self.matcher.find_hadith(query, self.repository.get_imported(kind))
        for row in base: row['provenance'] = 'Demonstration or manually entered local catalog; verify source'
        for row in imported: row['provenance'] = 'User-imported source; verify original edition'
        return sorted(base + imported, key=lambda row: -row['match_score'])[:50]
    def view_source(self, record_id, kind):
        """Look up a selected record, including provenance and bibliographic metadata."""
        if kind not in ('hadith', 'quote'): raise ValueError('Invalid search category')
        for row in self.repository.browse(kind, 100000):
            if str(row['id']) == str(record_id): return row
        raise ValueError('Record not found')
    def generate_footnote(self, record):
        return self.citation.generate_footnote(record)
    @staticmethod
    def _validate(kind, query):
        if kind not in ('hadith', 'quote'): raise ValueError('Invalid search category')
        if not isinstance(query, str) or not 3 <= len(query.strip()) <= 2000:
            raise ValueError('Enter 3–2000 characters')

class CatalogImportService:
    def import_records(self, filename, content):
        return legacy.import_catalog(filename, content)
    def create_quote(self, payload):
        return legacy.create_quote(payload)
    def create_hadith(self, payload):
        return legacy.create_hadith(payload)
    def delete_record(self, payload):
        return legacy.delete_record(payload)

class AdminAuthenticator:
    def initialize(self): return auth.initialize()
    def configured(self): return auth.configured()
    def setup(self, password): return auth.setup(password)
    def login(self, password): return auth.login(password)
    def authorized(self, token): return auth.authorized(token)
    def logout_all(self): return auth.logout_all()

class AccountService:
    """Role-aware user accounts; the first account is the administrator."""
    SESSION_SECONDS = accounts.SESSION_SECONDS
    def initialize(self): return accounts.initialize()
    def count(self): return accounts.count()
    def has_admin(self): return accounts.has_admin()
    def setup_admin(self, username, password, email=None): return accounts.setup_admin(username, password, email)
    def register(self, username, password, email=None): return accounts.register(username, password, email)
    def google_login(self, email, name, subject): return accounts.google_login(email, name, subject)
    def login(self, identifier, password): return accounts.login(identifier, password)
    def identity(self, token): return accounts.identity(token)
    def logout(self, username): return accounts.logout(username)
    def list_accounts(self): return accounts.list_accounts()
    def record_history(self, username, query, scope, result_count): return accounts.record_history(username, query, scope, result_count)
    def history(self, username, limit=100): return accounts.history(username, limit)
    def clear_history(self, username): return accounts.clear_history(username)
