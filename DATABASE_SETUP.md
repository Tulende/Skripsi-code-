# PostgreSQL persistence

The app connects to PostgreSQL using `DATABASE_URL` or Streamlit Secrets. Until that is configured, it stays in SQLite transition mode and displays a warning. SQLite files on Streamlit Community Cloud are not durable, so do not use that mode for production data.

## Prepare Supabase

1. Create a Supabase project and open **Connect** to copy its PostgreSQL connection string. Use the session pooler URL if the runtime cannot reach the direct IPv6 endpoint.
2. Keep the connection string private. Do not add it to Streamlit Cloud until the SQLite backup has been imported.

## Switch Streamlit to PostgreSQL

After the import completes, open the app settings in Streamlit Community Cloud and add this under **Secrets**:

   ```toml
   [postgresql]
   url = "postgresql://USER:PASSWORD@HOST:PORT/postgres?sslmode=require"
   ```

Save the Secrets and let Streamlit restart the app. Keep the connection string out of GitHub and chat. The local equivalent is `.streamlit/secrets.toml`, which is ignored by Git.

## Import an existing SQLite backup

Before switching the live app, open **Riwayat** as an admin and download **Unduh backup database SQLite sebelum migrasi**. Keep that file safe. Then create `.streamlit/secrets.toml` locally (this file is ignored by Git) with the connection string from Supabase:

```toml
[postgresql]
url = "postgresql://USER:PASSWORD@HOST:PORT/postgres?sslmode=require"
```

Run the importer using the downloaded backup path:

```powershell
python migrate_sqlite_to_postgres.py "C:\path\to\cobit2019_unklab_backup.db"
```

The importer preserves row IDs and uses upserts, so it can be run again safely. Make a backup of the PostgreSQL project before repeating an import after users have continued entering new data.

The app's SQLite file is excluded from Git and is not present in this workspace. The backup button is provided so data still available in the running app can be exported before migration; this code change cannot recover an SQLite file that is already gone. After the import completes, add the same `[postgresql]` section to Streamlit Cloud's **Secrets** settings to switch the deployed app to PostgreSQL.
