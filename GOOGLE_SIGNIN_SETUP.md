# Gmail / Google sign-in setup

Gmail sign-in uses Google OAuth 2.0 with PKCE. No credentials are stored in the repository.

## 1. Create a Google OAuth client

1. Open [Google Cloud Console](https://console.cloud.google.com/) → **APIs & Services → Credentials**.
2. Create a project if needed, then choose **Create credentials → OAuth client ID**.
3. Application type: **Web application**.
4. Under **Authorized redirect URIs**, add exactly:

   ```text
   http://localhost:8000/api/auth/google/callback
   ```

   If you open the app at `127.0.0.1:8000`, add that redirect URI too, or set `GOOGLE_REDIRECT_URI` explicitly. For a Vercel deployment also add `https://<your-project>.vercel.app/api/auth/google/callback` and set `GOOGLE_REDIRECT_URI` to that URL.
5. Copy the **Client ID** and **Client secret**.

## 2. Start the server with the credentials

PowerShell:

```powershell
$env:GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
$env:GOOGLE_CLIENT_SECRET="your-client-secret"
python server.py
```

macOS/Linux:

```bash
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret"
python server.py
```

Optional: override the redirect URI when the app is served elsewhere:

```powershell
$env:GOOGLE_REDIRECT_URI="http://localhost:8000/api/auth/google/callback"
```

## 3. Use it

1. On first run, create the **local admin account** via **Sign in → Create admin account**. The first account is the administrator and needs an email.
2. After that, **Continue with Gmail** appears in the sign-in dialog.
3. Google accounts are created as regular users, with a unique email. Gmail must be verified by Google.
4. Signed-in users get a **History** tab with their own saved searches. Admins get a **Users** tab showing username, email, role, and sign-in method.

If the environment variables are absent, the Google button is hidden and local username/email + password login continues to work. Local runs still bind to localhost; on Vercel the same code serves HTTPS and marks cookies `Secure`.
