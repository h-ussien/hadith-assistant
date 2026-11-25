# UML-to-code implementation guide

The supplied diagrams are copied unchanged to `docs/`. Their class names and method names are implemented in `app/uml.py`.

| UML class | Implemented methods |
|---|---|
| User | `getName()`, `getRole()` |
| Admin (extends User) | `addHadith(record, authorized=...)`, `importRecords(filename, content, authorized=...)` |
| Hadith | `getText()`, `getSource()` |
| Quotation | `getText()`, `getSource()` |
| Citation | `generateFootnote(record)` |
| Search | `searchHadith(query)`, `searchQuotation(query)` |
| Database | `findHadith(query)`, `findQuotation(query)`, `addHadith(record)` |
| UI | `search(query, kind)`, `displayResults(results)`, `generateFootnote(record)` |

## Sequence diagram mapping

1. **Search Hadith:** `UI.search(query)` → `Search.searchHadith(query)` → `Database.findHadith(query)` → `Hadith.getText()` / `getSource()` → `UI.displayResults(results)`.
2. **Generate Footnote:** `Citation.generateFootnote(hadith)` → `Hadith.getText()` / `getSource()` → Arabic footnote. Missing source fields are never invented.
3. **Admin Add Hadith:** authenticated HTTP request in `server.py` → `Admin.addHadith(record, authorized=True)` → `Database.addHadith(record)` → existing validation/storage service.

**Runtime integration:** Existing browser routes remain operational. The HTTP `/api/admin/hadith` route is wired to `Admin.addHadith` and the `/api/books/import` route is wired to `Admin.importRecords`. The existing frontend search routes are wired to the UML `Search`/`UI` objects. Existing search results retain the original JSON structure to avoid breaking the website.

**Run:** `python3 server.py` from the extracted project folder, then open `http://localhost:8000`. Run tests with `python3 -m unittest discover -s tests -v`.
