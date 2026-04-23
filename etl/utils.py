"""Utilitas ETL."""

import os
import clickhouse_connect
from dotenv import load_dotenv

load_dotenv()

def get_clickhouse_client():
    """Buat koneksi ClickHouse dari .env."""
    client = clickhouse_connect.get_client(
        host=os.getenv("CH_HOST"),
        port=int(os.getenv("CH_PORT")),
        username=os.getenv("CH_USER"),
        password=os.getenv("CH_PASSWORD"),
    )
    return client


def normalize_columns(df):
    """Normalisasi nama kolom DataFrame."""
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w]+", "_", regex=True)
    )
    return df
