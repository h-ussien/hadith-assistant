"""Concrete OOP classes corresponding to the supplied UML class/sequence diagrams.
CamelCase method names intentionally mirror the submitted PlantUML diagrams.
The existing backend is retained so the web application remains compatible.
"""
from dataclasses import dataclass, field
from typing import Optional
from . import domain, data, service, auth

@dataclass
class User:
    name: str = 'Student'
    role: str = 'student'
    def getName(self): return self.name
    def getRole(self): return self.role

class Admin(User):
    def __init__(self, name='Administrator', database=None):
        super().__init__(name, 'administrator')
        self.database = database or Database()
    def addHadith(self, record, authorized=False):
        if not authorized: raise PermissionError('Administrator authentication required')
        return self.database.addHadith(record)
    def importRecords(self, filename, content, authorized=False):
        if not authorized: raise PermissionError('Administrator authentication required')
        return service.import_catalog(filename, content)

@dataclass
class Hadith:
    text: str
    source: dict = field(default_factory=dict)
    record_id: Optional[int] = None
    def getText(self): return self.text
    def getSource(self): return self.source.copy()
    @classmethod
    def from_record(cls, row):
        return cls(row.get('passage',''), dict(row), row.get('id'))

@dataclass
class Quotation:
    text: str
    source: dict = field(default_factory=dict)
    record_id: Optional[int] = None
    def getText(self): return self.text
    def getSource(self): return self.source.copy()
    @classmethod
    def from_record(cls, row):
        return cls(row.get('passage',''), dict(row), row.get('id'))

class Database:
    def findHadith(self, query):
        self._validate(query)
        rows = data.get_all('hadith') + data.get_book_passages('hadith')
        return [Hadith.from_record(r) for r in domain.find_matches(query, rows)]
    def findQuotation(self, query):
        self._validate(query)
        rows = data.get_all('quote') + data.get_book_passages('quote')
        return [Quotation.from_record(r) for r in domain.find_matches(query, rows)]
    def addHadith(self, record):
        if not isinstance(record, dict): raise ValueError('Hadith record must be an object')
        return service.create_hadith(record)
    @staticmethod
    def _validate(query):
        if not isinstance(query, str) or not 3 <= len(query.strip()) <= 2000:
            raise ValueError('Enter 3–2000 characters')

class Search:
    def __init__(self, database=None): self.database = database or Database()
    def searchHadith(self, query): return self.database.findHadith(query)
    def searchQuotation(self, query): return self.database.findQuotation(query)

class Citation:
    def generateFootnote(self, record):
        if isinstance(record, (Hadith, Quotation)):
            metadata = record.getSource()
            metadata.setdefault('passage', record.getText())
        elif isinstance(record, dict):
            metadata = record
        else: raise TypeError('Expected a Hadith, Quotation, or catalog record')
        if not any(metadata.get(k) for k in ('author','book','reference')):
            return 'Source metadata unavailable; footnote cannot be generated.'
        return domain.footnote(metadata)

class UI:
    """Presentation controller; the browser frontend remains in static/app.js."""
    def __init__(self, search=None, citation=None):
        self.search_service = search or Search()
        self.citation_service = citation or Citation()
    def search(self, query, kind='hadith'):
        if kind == 'hadith': return self.search_service.searchHadith(query)
        if kind == 'quote': return self.search_service.searchQuotation(query)
        raise ValueError('Invalid search category')
    def displayResults(self, results):
        return [{'id':r.record_id,'text':r.getText(),'source':r.getSource()} for r in results]
    def generateFootnote(self, record):
        return self.citation_service.generateFootnote(record)
