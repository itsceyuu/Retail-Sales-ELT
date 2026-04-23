"""Inisialisasi database bronze/silver/gold di ClickHouse."""

from utils import get_clickhouse_client

DATABASES = ["bronze", "silver", "gold"]

def init_databases(client):
    """Buat database bronze, silver, dan gold jika belum ada."""
    for db in DATABASES:
        client.command(f"CREATE DATABASE IF NOT EXISTS {db}")
        print(f"  [OK] database '{db}' siap")


def main():
    """Entry point inisialisasi database ClickHouse."""
    print("=" * 50)
    print("  Inisialisasi ClickHouse Databases")
    print("=" * 50)

    client = get_clickhouse_client()
    init_databases(client)

    print()
    print("Semua database berhasil dibuat.")


if __name__ == "__main__":
    main()
