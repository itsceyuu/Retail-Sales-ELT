"""Load ML forecast results ke gold.sales_forecast_ml."""

import os
import sys
from pathlib import Path

import pandas as pd

# Tambahkan etl/ ke path biar bisa import utils
sys.path.append(str(Path(__file__).resolve().parent))
from utils import get_clickhouse_client

# Konfigurasi
ROOT_DIR  = Path(__file__).resolve().parents[1]
DATA_DIR  = ROOT_DIR / "data"
DB        = "gold"
TABLE     = "sales_forecast_ml"
FULL_TABLE = f"{DB}.{TABLE}"

TEST_PREDICTIONS_PATH = DATA_DIR / "sales_forecast_test_predictions.csv"
FUTURE_FORECAST_PATH  = DATA_DIR / "sales_forecast_future.csv"


def create_table(client):
    """Buat tabel gold.sales_forecast_ml jika belum ada."""
    client.command(f"DROP TABLE IF EXISTS {FULL_TABLE}")
    client.command(f"""
        CREATE TABLE IF NOT EXISTS {FULL_TABLE} (
            region          String,
            order_month     Date,
            actual_sales    Nullable(Float64),
            forecast_sales  Float64,
            model_name      String,
            forecast_type   String
        )
        ENGINE = MergeTree()
        ORDER BY (region, order_month, model_name)
        COMMENT 'Gold layer — hasil forecast ML per region per bulan'
    """)
    print(f"  [OK] tabel '{FULL_TABLE}' dibuat")


def load_test_predictions(client):
    """Load sales_forecast_test_predictions.csv ke ClickHouse."""
    if not TEST_PREDICTIONS_PATH.exists():
        print(f"  [ERROR] file tidak ditemukan: {TEST_PREDICTIONS_PATH}")
        sys.exit(1)

    df = pd.read_csv(TEST_PREDICTIONS_PATH)
    df["forecast_type"] = "test"
    df["order_month"] = pd.to_datetime(df["order_month"]).dt.date
    df = df[["region", "order_month", "actual_sales", "forecast_sales", "model_name", "forecast_type"]]

    client.insert_df(FULL_TABLE, df)
    print(f"  [OK] {len(df):,} baris test predictions diinsert")


def load_future_forecast(client):
    """Load sales_forecast_future.csv ke ClickHouse."""
    if not FUTURE_FORECAST_PATH.exists():
        print(f"  [ERROR] file tidak ditemukan: {FUTURE_FORECAST_PATH}")
        sys.exit(1)

    df = pd.read_csv(FUTURE_FORECAST_PATH)
    df["forecast_type"] = "future"
    df["actual_sales"]  = None
    df["order_month"]   = pd.to_datetime(df["order_month"]).dt.date
    df = df[["region", "order_month", "actual_sales", "forecast_sales", "model_name", "forecast_type"]]

    client.insert_df(FULL_TABLE, df)
    print(f"  [OK] {len(df):,} baris future forecast diinsert")


def verify(client):
    """Verifikasi data berhasil masuk."""
    result = client.query(f"SELECT count() FROM {FULL_TABLE}")
    total  = result.result_rows[0][0]
    print(f"  [OK] total rows di ClickHouse: {total:,}")


def main():
    print("=" * 50)
    print("  Load Forecast — gold.sales_forecast_ml")
    print("=" * 50)

    # 1) Koneksi
    print("\n[1/4] Koneksi ke ClickHouse ...")
    client = get_clickhouse_client()
    print("  [OK] terhubung")

    # 2) Buat tabel
    print("\n[2/4] Membuat tabel ...")
    create_table(client)

    # 3) Insert data
    print("\n[3/4] Insert data ...")
    load_test_predictions(client)
    load_future_forecast(client)

    # 4) Verifikasi
    print("\n[4/4] Verifikasi ...")
    verify(client)

    print()
    print("=" * 50)
    print("  Forecast berhasil diload.")
    print(f"  Tabel : {FULL_TABLE}")
    print("=" * 50)


if __name__ == "__main__":
    main()