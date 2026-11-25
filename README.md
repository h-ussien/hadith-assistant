# Student Islamic Research Assistant
## المساعد البحثي الذكي لعزو الأحاديث وتوثيق النقولات في بحوث التخرج

A **working educational MVP**, not a production-grade hadith authentication system.

## Run
1. Install Python 3.10+ (no third-party packages needed for local SQLite runs).
2. In this folder run: `python server.py` (on some Macs: `python3 server.py`).
3. Open **http://localhost:8000** in a browser.
4. Test with `إنما الأعمال بالنيات` or `الدين النصيحة`.
5. For quotations, use **Add verified quotation** to enter a reference checked against a real edition, then search for it.

## Tests
`python -m unittest discover -s tests -v`

## Architecture (four layers)
- **Presentation:** `static/` (HTML/CSS/JavaScript UI) and HTTP boundary in `server.py`
- **Application:** `app/service.py` (request coordination and validation)
- **Business Logic:** `app/domain.py` (Arabic text normalization, similarity ranking, footnotes)
- **Data Access:** `app/data.py` (SQLite locally; Neon Postgres when `DATABASE_URL` is set on Vercel)

Flow: browser → HTTP endpoint → service → domain/data → result → browser.

## Current scope and limitations
- Small local seed catalog with a few well-known hadith references; **not** a complete Kutub al-Sittah corpus.
- Exact and approximate text matches are *search aids*, not hadith authentication.
- No chain-of-narration variants or scholar-specific grading analysis yet.
- The default chat search queries the **المكتبة الشاملة (Shamela)** through its official read-only MCP endpoint and returns at most four results, one from each of Sahih al-Bukhari, Sahih Muslim, Sunan Abi Dawud, and Jami' at-Tirmidhi. No book corpus is bundled or copied into this app. The local catalog and imported books remain available as separate scopes.
- A separate **Dorar.net / الدرر السنية** scope searches the public Dorar hadith service and shows the text, source, page/number, narrator, and the scholar's grade summary. It returns at most four results and links back to Dorar; no Dorar data is bundled locally.
- Shamela results show the page reference supplied by Shamela; open the linked page and check the edition before citing. No volume/page details are invented for local records.
- The source URL and hadith numbering should be checked before scholarly submission.
- Local accounts are supported: the first account is the administrator; later accounts are regular users. Each account has a unique email. Optional Gmail/Google OAuth sign-in is available with your own Google client credentials. Signed-in users have a personal search history; admins have a Users tab. Local runs bind to localhost; see `VERCEL_DEPLOYMENT.md` for the free serverless deployment.

## Next implementation stages
1. Import legally licensed/authorized indexed Islamic reference datasets with edition metadata.
2. Add verified isnad and scholarly grading fields with attribution and conflicting-opinion handling.
3. Add edition-aware citation styles and audit trails for every result.
4. Add email recovery, role management screens, rate limiting, and production security before hosting. See `GOOGLE_SIGNIN_SETUP.md` for Gmail sign-in configuration.

## Implementation status (November 2026)
The MVP includes a responsive browser UI, live Shamela search through the official read-only MCP service, a separate Dorar.net search scope, a searchable demonstration Hadith catalog, manual quote-entry form requiring a user verification confirmation, edition-aware footnote output, and automated tests. The confirmation is a user attestation, **not** independent verification by the software. No scholar grading engine is implemented.

## Version 2: searching your own books and full Hadith passages

Select **مساحة العمل / My Islamic books** to import a UTF-8 CSV of complete passages with source metadata. See `BOOK_IMPORT_GUIDE.md` and `sample_import_template.csv`. This workspace stays local; Shamela and Dorar.net are reached only from the chat search and are not bundled into the app.

## Version 4: accounts, Gmail sign-in, administrator role, and English UI

Click **دخول / Sign in** to create the first account (administrator) with a username, unique email, and password. Later local accounts and Gmail accounts are regular users. The administrator is identified by an **Admin / مدير** badge, sees the **Users / المستخدمون**, **Admin / الإدارة**, and **Sources / المصادر** navigation items, and can add verified Hadith, add quotations, import CSV passages, manage records, and view all accounts. Regular users see their own **History / السجل** tab.

Gmail sign-in uses Google OAuth 2.0 with PKCE and requires your own Google client ID/secret; see `GOOGLE_SIGNIN_SETUP.md`. Without those credentials the button is hidden and local login still works.

The interface has an off-white light palette and an **EN / ع** switch for English/Arabic. All tabs live in a slide-out drawer opened from the menu button on the left. The search composer slides down and stays pinned at the bottom while you scroll. The language choice is remembered in the browser. See `ADMIN_GUIDE.md`.

## Hosting on Vercel (free Hobby plan)

`vercel.json` maps the UI to `static/`, `/api/*` to a Python function in `api/index.py`, and adds free Neon Postgres persistence through `DATABASE_URL`. Local `python server.py` behavior is unchanged. See **`VERCEL_DEPLOYMENT.md`** for the complete setup, environment variables, and Hobby limits. This remains an educational MVP, not a production-grade hadith authentication service.
