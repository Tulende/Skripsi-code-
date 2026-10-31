# PostgreSQL persistence

The app connects to PostgreSQL using `DATABASE_URL` or Streamlit Secrets. Until that is configured, it stays in SQLite transition mode and displays a warning. SQLite files on Streamlit Community Cloud are not durable, so do not use that mode for production data.

## Configure Supabase and Streamlit

1. Create a Supabase project and open **Connect** to copy its PostgreSQL connection string. Use the session pooler URL if the runtime cannot reach the direct IPv6 endpoint.
2. In Streamlit Community Cloud, open the app settings and add this under **Secrets**:

   ```toml
   [postgresql]
   url = "postgresql://USER:PASSWORD@HOST:PORT/postgres?sslmode=require"
   ```

3. Save the Secrets and let Streamlit restart the app. On startup, the app creates the required tables in PostgreSQL.
4. Keep the connection string out of GitHub and chat. The local equivalent is `.streamlit/secrets.toml`, which is ignored by Git.

## Import an existing SQLite backup

Before switching the live app, open **Riwayat** as an admin and download **Unduh backup database SQLite sebelum migrasi**. Keep that file safe. After creating the Supabase project, configure `DATABASE_URL` in your local shell and run:

```powershell
$env:DATABASE_URL = "postgresql://USER:PASSWORD@HOST:PORT/postgres?sslmode=require"
python migrate_sqlite_to_postgres.py "C:\path\to\cobit2019_unklab.db"
```

The importer preserves row IDs and uses upserts, so it can be run again safely. Make a backup of the PostgreSQL project before repeating an import after users have continued entering new data.

The app's SQLite file is excluded from Git and is not present in this workspace. The backup button is provided so data still available in the running app can be exported before migration; this code change cannot recover an SQLite file that is already gone.
