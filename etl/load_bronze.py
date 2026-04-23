"""Load CSV Superstore ke bronze.bronze_orders."""

import os
import sys
import pandas as pd
from utils import get_clickhouse_client, normalize_columns

# Konfigurasi
RAW_DIR    = os.getenv("RAW_DIR")
CSV_FILE   = os.path.join(RAW_DIR, "samplesuperstore.csv")
DB         = "bronze"
TABLE      = "bronze_orders"
FULL_TABLE = f"{DB}.{TABLE}"


def load_csv(path: str) -> pd.DataFrame:
    """Baca CSV dengan encoding UTF-8."""
    df = pd.read_csv(path, encoding="utf-8")

    df = normalize_columns(df)

    print(f"  File     : {path}")
    print(f"  Shape    : {df.shape[0]:,} baris x {df.shape[1]} kolom")
    print(f"  Kolom    : {df.columns.tolist()}")
    return df


def create_table(client, df: pd.DataFrame):
    """Buat tabel bronze_orders dari kolom DataFrame."""
    columns_ddl = ",\n    ".join(
        f"`{col}` String" for col in df.columns
    )

    ddl = f"""
        CREATE TABLE IF NOT EXISTS {FULL_TABLE} (
            {columns_ddl}
        ) ENGINE = MergeTree()
        ORDER BY tuple()
        COMMENT 'Bronze layer — raw data dari superstore.csv'
    """

    client.command(f"DROP TABLE IF EXISTS {FULL_TABLE}")
    client.command(ddl)
    print(f"  [OK] tabel '{FULL_TABLE}' dibuat")


def insert_data(client, df: pd.DataFrame):
    """Insert seluruh DataFrame ke ClickHouse."""
    # Bronze simpan semua nilai sebagai string.
    df = df.astype(str).replace("nan", "")
    client.insert_df(FULL_TABLE, df)
    print(f"  [OK] {len(df):,} baris diinsert")


def verify(client, expected_rows: int):
    """Verifikasi row count di ClickHouse vs jumlah baris CSV."""
    result = client.query(f"SELECT count() FROM {FULL_TABLE}")
    actual_rows = result.result_rows[0][0]

    status = "[OK]" if actual_rows == expected_rows else "[MISMATCH]"
    print(f"  {status} row count ClickHouse : {actual_rows:,}")
    print(f"  {status} row count CSV        : {expected_rows:,}")

    if actual_rows != expected_rows:
        print()
        print("  PERINGATAN: jumlah baris tidak sesuai, cek log di atas.")
        sys.exit(1)


def main():
    """Entry point proses load bronze."""
    print("=" * 50)
    print("  Load Bronze — Superstore")
    print("=" * 50)

    # 1) Validasi env dan file
    if not RAW_DIR:
        print("\n  ERROR: RAW_DIR belum di-set di .env")
        sys.exit(1)

    if not os.path.exists(CSV_FILE):
        print(f"\n  ERROR: file tidak ditemukan:{CSV_FILE}")
        print("  Pastikan samplesuperstore.csv ada di folder data/")
        sys.exit(1)

    # 2) Load CSV
    print("\n[1/4] Membaca CSV ...")
    df = load_csv(CSV_FILE)
    csv_row_count = len(df)

    # 3) Koneksi ClickHouse
    print("\n[2/4] Koneksi ke ClickHouse ...")
    client = get_clickhouse_client()
    print("  [OK] terhubung")

    # 4) Buat tabel
    print("\n[3/4] Membuat tabel ...")
    create_table(client, df)

    # 5) Insert data
    print("\n[4/4] Insert data ...")
    insert_data(client, df)

    # 6) Verifikasi
    print("\n[Verifikasi]")
    verify(client, csv_row_count)

    print()
    print("=" * 50)
    print("  Bronze layer selesai.")
    print(f"  Tabel : {FULL_TABLE}")
    print(f"  Rows  : {csv_row_count:,}")
    print("=" * 50)


if __name__ == "__main__":
    main()
