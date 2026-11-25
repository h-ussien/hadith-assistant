# Alignment with the class diagram in the report

The report's ten classes are implemented in `app/diagram_classes.py`:
`UI`, `User`, `Search`, `TextCleaner`, `QueryGen`, `HadithVi`, `Getresult`, `Citation`, `Takhrij`, `DB`.

The existing website now routes `/api/search` and `/api/search/all` through
`UI.sendText()` -> `Search.processtext()` -> `TextCleaner` / `QueryGen` ->
`Getresult` -> `DB`, with `HadithVi` checking source metadata completeness.
The legacy `app/uml.py` is retained for compatibility with the original UML
and existing administrative operations.

## Limitations of the original project
- `HadithVi.verifySource` checks presence of source metadata, not hadith authenticity.
- The original project does not have a student-user database or persistent
  search history. `DB.findUser()` returns None and `DB.getHistoryUser()` returns []
  rather than pretending those features exist.
- Existing administrator authentication is still handled by the HTTP session API.
- Class and method spellings match the screenshot, including `processtext`,
  `generatQuery`, `Getresult`, `HadithVi`, and `Takhrij`.

## Run
`python server.py` then open `http://localhost:8000`.
Run tests with `python -m unittest discover -s tests`.
