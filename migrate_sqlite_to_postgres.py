"""Copy an existing COBIT SQLite database into the configured PostgreSQL DB."""

import os
import sqlite3
import sys

import psycopg

from engine import get_database_url, init_db


TABLES = (
    "users",
    "respondents",
    "df_responses",
    "capability_assessments",
    "individual_responses",
    "individual_checklist_responses",
)


def main(source_path):
    database_url = os.environ.get("DATABASE_URL") or get_database_url()
    if not database_url:
        raise SystemExit("Set DATABASE_URL to the target PostgreSQL connection string first.")
    if not os.path.isfile(source_path):
        raise SystemExit(f"SQLite backup not found: {source_path}")

    # Ensure the target schema exists before copying rows.
    init_db()
    source = sqlite3.connect(source_path)
    target = psycopg.connect(database_url, connect_timeout=15, sslmode="require")
    try:
        source_tables = {
            row[0]
            for row in source.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        missing = set(TABLES) - source_tables
        if missing:
            raise RuntimeError("SQLite backup is missing tables: " + ", ".join(sorted(missing)))

        with target.cursor() as cursor:
            for table in TABLES:
                rows = source.execute(f'SELECT * FROM "{table}"').fetchall()
                if not rows:
                    continue
                columns = [row[1] for row in source.execute(f'PRAGMA table_info("{table}")')]
                column_sql = ", ".join(f'"{column}"' for column in columns)
                placeholders = ", ".join(["%s"] * len(columns))
                mutable_columns = [column for column in columns if column != "id"]
                updates = ", ".join(
                    f'"{column}" = EXCLUDED."{column}"' for column in mutable_columns
                )
                conflict = f"DO UPDATE SET {updates}" if updates else "DO NOTHING"
                query = (
                    f'INSERT INTO "{table}" ({column_sql}) OVERRIDING SYSTEM VALUE '
                    f'VALUES ({placeholders}) ON CONFLICT (id) {conflict}'
                )
                cursor.executemany(query, rows)
                print(f"{table}: imported {len(rows)} rows")

            # Advance identity sequences so new rows do not reuse imported IDs.
            for table in TABLES:
                cursor.execute(
                    "SELECT setval(pg_get_serial_sequence(%s, 'id'), "
                    f"GREATEST(COALESCE(MAX(id), 1), 1), COUNT(*) > 0) FROM \"{table}\"",
                    (table,),
                )
        target.commit()
        print("SQLite data import completed.")
    except Exception:
        target.rollback()
        raise
    finally:
        source.close()
        target.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python migrate_sqlite_to_postgres.py <sqlite-backup.db>")
    main(sys.argv[1])
