"""The ten classes and operations from the report's UML screenshot.
Existing storage and HTTP endpoints are retained for compatibility.
"""
import re
from dataclasses import dataclass, field
from . import data, domain, auth

@dataclass
class User:
    userID: int = 0
    Name: str = 'Student'
    password: str = ''

class TextCleaner:
    def __init__(self, rules=None):
        self.rules = rules or []
    def cleanText(self, text: str) -> str:
        if not isinstance(text, str):
            raise ValueError('Text must be a string')
        cleaned = re.sub(r'\s+', ' ', text).strip()
        for pattern, replacement in self.rules:
            cleaned = re.sub(pattern, replacement, cleaned)
        return cleaned

class QueryGen:
    def __init__(self, cleaner=None):
        self.cleaner = cleaner or TextCleaner()
        self.converText = ''
    def generatQuery(self, text=None):
        if text is not None:
            self.converText = self.cleaner.cleanText(text)
        return self.converText

class DB:
    def __init__(self, connectString='local SQLite'):
        self.connectString = connectString
    def findUser(self, user_id):
        # The existing application has admin sessions, not a student-account table.
        return None
    def findHadith(self, query):
        return domain.find_matches(query, data.get_all('hadith') + data.get_book_passages('hadith'))
    def inputHadith(self, record):
        from . import service
        return service.create_hadith(record)
    def getHistoryUser(self, user_id):
        return []  # No per-user history persistence in the original database.
    def findTkhrij(self, query):
        return self.findHadith(query)
    def findQuotation(self, query):
        return domain.find_matches(query, data.get_all('quote') + data.get_book_passages('quote'))

class HadithVi:
    def __init__(self, database=None):
        self.database = database or DB()
        self.match = ''
    def verifySource(self, record):
        """Report presence of metadata; NOT independent authenticity verification."""
        return bool(record.get('book') and record.get('author') and (record.get('reference') or record.get('hadith_number')))

class Getresult:
    def __init__(self, database=None, verifier=None):
        self.database = database or DB()
        self.verifier = verifier or HadithVi(self.database)
        self.getResult = ''
    def fetch(self, query, kind='hadith'):
        rows = self.database.findHadith(query) if kind == 'hadith' else self.database.findQuotation(query)
        return [dict(row, source_metadata_present=self.verifier.verifySource(row)) for row in rows]

class Citation:
    def __init__(self, templet='{author}, {book}, {reference}', rules='Use available source metadata'):
        self.templet = templet
        self.rules = rules
    def generate(self, record):
        if not isinstance(record, dict):
            raise TypeError('Citation requires a source record')
        if not (record.get('book') or record.get('author')):
            return 'Source metadata unavailable; footnote cannot be generated.'
        return domain.footnote(record)

class Takhrij:
    def __init__(self, database=None):
        self.database = database or DB()
        self.TargetHadith = []
    def names(self, query):
        self.TargetHadith = self.database.findTkhrij(query)
        return sorted({r.get('book', '') for r in self.TargetHadith if r.get('book')})
    def othersRoute(self, query):
        self.TargetHadith = self.database.findTkhrij(query)
        return self.TargetHadith

class Search:
    def __init__(self, database=None, cleaner=None, query_gen=None, result=None):
        self.database = database or DB()
        self.cleaner = cleaner or TextCleaner()
        self.query_gen = query_gen or QueryGen(self.cleaner)
        self.result = result or Getresult(self.database)
        self.query = ''
    def processtext(self, text=None, kind='hadith'):
        if text is not None:
            self.query = self.query_gen.generatQuery(self.cleaner.cleanText(text))
        if not 3 <= len(self.query) <= 2000:
            raise ValueError('Enter 3–2000 characters')
        if kind not in ('hadith', 'quote'):
            raise ValueError('Invalid search category')
        return self.result.fetch(self.query, kind)

class UI:
    def __init__(self, search=None, user=None, database=None):
        self.database = database or DB()
        self.search_service = search or Search(self.database)
        self.user = user or User()
        self.inputText = ''
    def sendText(self, text, kind='hadith'):
        self.inputText = text
        return self.search_service.processtext(text, kind)
    def output(self, results):
        return results
    def login(self, password):
        # Admin authentication is handled by the existing session-based API.
        return auth.verify_password(password) if hasattr(auth, 'verify_password') else False
    def history(self):
        return self.database.getHistoryUser(self.user.userID)
