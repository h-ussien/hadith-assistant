# Book and full Hadith text support (Version 2)

This version supports **searching complete Hadith passages and classical book quotations that you import**. It does **not** include a copyrighted book collection or automatically download Islamic books. The chat view can separately search Shamela through its official read-only MCP service; this import workspace remains local. Imported texts and metadata must be checked by the student against the named source/edition.

## Import

1. Run `python3 server.py` and open `http://localhost:8000`.
2. Select **My Islamic books**.
3. Create a UTF-8 CSV with the following header:

```csv
kind,passage,book,author,chapter,hadith_number,volume,page,edition,url,note
```

4. Add one row per complete Hadith or quotation, with source metadata you can substantiate. `kind` must be `hadith` or `quote`. Leave unknown fields empty. Quoted CSV values containing commas must be surrounded with double quotes.
5. Upload the CSV. Then search an Arabic excerpt; matching records display the **complete imported passage** and a footnote based only on available metadata.

For demonstration, `sample_import_template.csv` has **headers only**, not invented source records. Do not use unverified texts for scholarly citations.

## Limitations

- Local-first: this workspace works offline with imported passages. Shamela search is available only in the chat view and needs network access; no Shamela text is stored in this app.
- Search uses Arabic text normalization and similarity matching. A match does **not** establish authenticity or verify a chain of narration.
- A CSV row's `edition`, `volume`, and `page` are supplied by the importer and are **not independently verified**.
- The small built-in Hadith catalog remains a labeled demonstration.
- To add real books, obtain a legally usable dataset with full text and reliable bibliographic metadata, then convert it to this CSV schema.
