# Student Islamic Research Assistant — Object-Oriented Edition

This is a refactoring of the original Python/JavaScript website. `server.py` uses object instances from `app/oop.py` for search, citations, catalog, imports and authentication. Existing original domain, data, and validation functions remain in place and are delegated to by the new classes, to preserve behavior and reduce regression risk. It is **not** a wholesale conversion of every function to a method.

## Run
From this folder: `python3 server.py`, then open `http://localhost:8000`.

## Test
`python3 -m unittest discover -s tests -v`

## Class-to-diagram correspondence
- `Handler` in `server.py`: browser/API requests (presentation boundary).
- `ResearchService`: `search_hadith`, `search`, `search_all`, `view_source`, `generate_footnote`.
- `HadithMatcher`: `normalize`, `score`, `find_hadith`.
- `CitationFormatter`: `generate_footnote`.
- `CatalogRepository`: `get_all`, `get_imported`, `browse`, `store_import`, `stats`.
- `CatalogImportService`: `import_records`, `create_quote`, `create_hadith`, `delete_record`.
- `AdminAuthenticator`: `setup`, `login`, `authorized`, `logout_all`.

Note: The browser currently displays source metadata and generated footnotes from search result records. `view_source` is an OOP API method but no dedicated `/api/source` endpoint was added. Import parsing is delegated to the original validated implementation. The diagrams are logical flows and show these delegation boundaries.
