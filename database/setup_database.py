"""Optional helper: create the PostgreSQL database, run schema.sql and load the cleaned CSV files.

Use this if you prefer Python over typing the psql commands (for example on Windows).
Connection settings are read from a .env file (copy .env.example to .env first).

Run from the project root:  python database/setup_database.py
"""
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

BASE_DIR = Path(__file__).resolve().parents[1]
LOAD_ORDER = ["customers", "products", "orders", "order_items", "reviews"]


def get_settings():
    load_dotenv(BASE_DIR / ".env")
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD"),
        "dbname": os.getenv("DB_NAME", "ecommerce_analytics"),
    }


def create_database_if_missing(settings):
    admin_settings = {**settings, "dbname": "postgres"}
    connection = psycopg2.connect(**admin_settings)
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (settings["dbname"],))
        if cursor.fetchone() is None:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(settings["dbname"])))
            print(f"Created database {settings['dbname']}")
        else:
            print(f"Database {settings['dbname']} already exists")
    connection.close()


def run_schema_and_load(settings):
    connection = psycopg2.connect(**settings)
    with connection, connection.cursor() as cursor:
        cursor.execute((BASE_DIR / "database" / "schema.sql").read_text())
        print("Schema created")
        for table in LOAD_ORDER:
            with open(BASE_DIR / "data" / "processed" / f"{table}.csv", encoding="utf-8") as csv_file:
                cursor.copy_expert(f"COPY {table} FROM STDIN WITH (FORMAT csv, HEADER true)", csv_file)
            cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table)))
            print(f"Loaded {table}: {cursor.fetchone()[0]:,} rows")
    connection.close()


def main():
    settings = get_settings()
    if not settings["password"]:
        raise SystemExit("DB_PASSWORD is not set. Copy .env.example to .env and fill in your password.")
    create_database_if_missing(settings)
    run_schema_and_load(settings)
    print("Done. Now run the files in sql/ with psql or pgAdmin.")


if __name__ == "__main__":
    main()
