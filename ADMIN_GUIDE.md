# V4 accounts and administrator access

## Students / regular users

Regular users can search Hadith, quotations, and Shamela, read catalogued passages, and copy footnotes without signing in. They can create a local account from **Sign in → No account? Create one** (username, unique email, password) or sign in with Gmail if the server is configured. Signed-in users get a **History / السجل** tab containing only their own searches. They cannot add, import, or delete records.

## Administrator

1. Run `python server.py` and open `http://localhost:8000`.
2. Click **دخول / Sign in**. On first run, create the first account with a username, unique email, and password of at least 12 characters. **The first account is the administrator.** Keep the credentials safe: there is no email recovery.
3. After signing in, the header shows the username with an **Admin / مدير** badge. The **Users / المستخدمون**, **History / السجل**, **Admin / الإدارة**, and **Sources / المصادر** navigation items become available. The Users tab lists every account with username, email, role, and sign-in method.
4. Use **Add verified Hadith** or **Add a source** for checked texts, and **Import a book catalog** for UTF-8 CSV files.
5. Use **Load records** to view and delete catalog entries. Delete is permanent.
6. The administrator panel also lists registered accounts with their roles.
7. Click **Sign out** when finished.

If you already used the older single-password admin setup, the existing password is migrated to an `admin` account automatically on startup; sign in with username `admin` and the same password.

All write operations are checked on the server, not merely hidden in the browser. Passwords are salted and hashed with scrypt; sessions use signed HttpOnly SameSite cookies. The app binds to localhost, not the public internet. Do not expose it online without HTTPS, proper account recovery, rate limiting, backups, and additional security review.

Existing V3 SQLite data (`research.db`) is not bundled in the ZIP. If you want to retain existing local records, copy `research.db` from the old project into this project's root before starting V4, and back it up first. New tables are created automatically.

Administrator access prevents unauthorized edits but does **not** verify Islamic sources automatically. The local catalog is limited; Shamela is queried read-only from the chat view, and no Shamela/Kutub al-Sittah corpus is bundled.

## Gmail sign-in

Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` before starting the server, and register `http://localhost:8000/api/auth/google/callback` as an authorized redirect URI in Google Cloud Console. See `GOOGLE_SIGNIN_SETUP.md`. The Gmail button is hidden until configured; local sign-in continues to work. Google accounts are always regular users, never administrators.

## Language and appearance

Use the **EN / ع** button in the header to switch between English and Arabic. The choice is remembered locally. The light theme uses an off-white palette; the moon/sun button toggles the dark theme.
