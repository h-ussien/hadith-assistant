# AI Implementation Prompt — Software Engineering Project

Build a runnable, local-first educational MVP named **Student Islamic Research Assistant: Source Extraction & Attribution Engine** (المساعد البحثي الذكي لعزو الأحاديث وتوثيق النقولات في بحوث التخرج).

**Goal:** Help Sharia and Islamic Studies students locate source references for Hadith excerpts and classical quotations, and generate academic footnotes. The product is a research aid, not an independent authority on Hadith authenticity.

**Architecture:** Use four explicit layers: (1) Presentation for the student UI; (2) Application for coordinating requests and validation; (3) Business Logic for Arabic normalization, text matching, and citation generation; (4) Data Access for indexed Islamic research sources. Keep layer responsibilities separated and document the flow.

**Required MVP features:**
1. Responsive, Arabic-friendly UI with a Hadith search field and clear result cards.
2. Hadith Takhrij Helper: match a full or partial Arabic text against a local catalog, display canonical collection, author, chapter/number where available, and a source link. Distinguish text matches from possible matches.
3. Quote Source Finder: search an indexed catalog of classical quotations, including book/author and edition-specific volume/page where known. Provide a manual catalog-entry workflow for verified quotations.
4. Footnote Generator: build Arabic citations only from metadata actually present; omit unavailable volume/page fields.
5. Show a clear warning that all academic references require independent verification.

**Data integrity constraints:** Never invent Hadith gradings, chains of narrators, citations, edition pages, or source records. Do not claim that matching proves authenticity. Do not fabricate a Shamela integration. Where external datasets or APIs are unavailable, use a small, explicitly labeled demonstration catalog and explain limitations.

**Technical requirements:** Prefer a simple Python standard-library backend, SQLite, and HTML/CSS/JavaScript to ensure a student can run the project without package installation. Implement basic input validation, safe database parameterization, and error handling. Keep any unauthenticated catalog-entry endpoint local-only. Include runnable tests and a README with exact setup steps.

**Deliverables:** Working source code, folder structure reflecting the four layers, local run instructions, tests, and a clear account of completed versus future features. Test Arabic normalization, successful Hadith lookup, missing-source behavior, and quotation insertion. Do not describe future features as already implemented.
