# Implementation status — V4

## Working locally
- Responsive Arabic/English interface with an off-white light palette and dark-mode toggle.
- Local user accounts: first account is the administrator; later accounts are regular users. Every account has a unique email, and login accepts username or email. Admin role is shown in the header and admin-only tools are server-protected.
- Optional Gmail/Google OAuth sign-in with PKCE for regular accounts, configured through `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` (see `GOOGLE_SIGNIN_SETUP.md`). Local login remains available when Google credentials are absent.
- Admin-only **Users / المستخدمون** tab lists each account's username, email, role, and sign-in method. Signed-in users get a personal **History / السجل** tab with only their own saved searches; guest searches are not stored.
- Legacy single-password admin setup is migrated into an `admin` account on startup.
- Vercel Hobby deployment: `vercel.json` serves the UI from `static/` and routes `/api/*` to `api/index.py`; with `DATABASE_URL` the same code uses free Neon Postgres instead of the local SQLite file. See `VERCEL_DEPLOYMENT.md`.
- Live Shamela search through its official read-only MCP service, strictly scoped to four hadith collections (Sahih al-Bukhari, Sahih Muslim, Sunan Abi Dawud, Jami' at-Tirmidhi). Results are capped at four, preferring one per collection, with book/page citation links.
- Separate **Dorar.net** search scope using the public Dorar hadith service. Results are capped at four and include the narrator, source, page/number, and grade summary with a link back to Dorar. No Dorar data is bundled locally.
- Unified local search across the small built-in demonstration catalog and user-imported book passages.
- Partial and exact text matching; possible matches are labeled, not treated as authenticated.
- Full passage text shown **when that full text was imported**.
- Source book, author, chapter, Hadith number, optional source URL and edition metadata.
- Arabic footnote generation with missing volume/page omitted.
- Manually add quotation metadata with an explicit verification checkbox.
- UTF-8 CSV imports of book passages; source provenance labels; local SQLite storage.
- Four layers: presentation (static/ and server HTTP), application (app/service.py), business logic (app/domain.py), data access (app/data.py).
- Automated unit tests.

## Not implemented; requires licensed or openly reusable source texts and verification
- Complete Kutub al-Sittah or full Shamela/Dorar corpora bundled in the app. Both are queried externally at search time.
- Automatic book downloads, offline Shamela access, or write access to external libraries.
- Independent authenticity judgments, full isnad variant comparison, or authoritative grading aggregation.
- Edition-specific pages for books where none have been supplied.

## Importing real books
Use **My Islamic books** to import CSV rows with fields listed in BOOK_IMPORT_GUIDE.md. One row should contain the full passage, with exact book/edition metadata if known. Use texts you have permission to import. A partial query can then retrieve the full imported passage. Imported material is not automatically verified.

## Security note
Run locally on 127.0.0.1; this is a student MVP and is not designed for public internet deployment. Back up research.db before large imports. Do not use the tool as a source of independent Hadith authentication.
