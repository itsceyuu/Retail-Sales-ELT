# Retail-Sales-ELT

Pipeline ELT end-to-end untuk mengolah data penjualan retail `Superstore` dari Kaggle menjadi insight bisnis yang siap divisualisasikan.<br>Menerapkan Medallion Architecture (Bronze → Silver → Gold) dengan ClickHouse sebagai Data Warehouse dan Metabase sebagai layer dashboard BI.

![My Skills](https://go-skill-icons.vercel.app/api/icons?i=kaggle,clickhouse,metabase,dbtlabs,python,pandas,docker,jupyter&titles=true)

## Stack

| Komponen       | Tool            |
| -------------- | --------------- |
| Data Source    | Kaggle Superstore |
| Data Warehouse | ClickHouse 24.3 |
| ETL            | Python + pandas + dbt Core |
| Visualization    | Metabase        |
| Orchestration       | Docker Compose  |
| Eksplorasi        | Jupyter Notebook    |


## Arsitektur Proyek
<img src="docs/architecture.png" alt="Arsitektur Sistem" width="600"/>

## Struktur Proyek
```
retail-sales-elt/
├── docker-compose.yml              # ClickHouse + Metabase
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── data/
│   └── samplesuperstore.csv        # CSV di sini
│
├── etl/
│   ├── utils.py                    # koneksi ClickHouse & helper
│   ├── init_clickhouse.py          # buat database bronze/silver/gold
│   └── load_bronze.py              # CSV → ClickHouse bronze
│
└── notebooks/
    └── bronze_verification.ipynb   # verifikasi hasil ingestion

├── dbt_project.yml               # dbt project configuration
├── profiles.yml.example          # dbt profile example for ClickHouse
└── models/
    ├── schema.yml                # dbt source/model definitions
    ├── silver/
    │   └── silver_orders.sql     # Silver model
    └── gold/
        └── gold_orders.sql       # Gold model
```

## Cara Menjalankan

### Requirements
- Docker Engine terinstall dan berjalan
- Python 3.11+
- File `samplesuperstore.csv` dari Kaggle sudah ada di `data/`

### Langkah-langkah
```bash
git clone https://github.com/itsceyuu/Retail-Sales-ELT
cd retail-sales-elt

cp .env.example .env # Edit .env jika perlu (opsional)

# Install dependencies Python
pip install -r requirements.txt

# (Opsional) Pake virtual environment, direkomendasikan kalo pke Linux
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

docker compose up -d clickhouse # Jalankan ClickHouse

python etl/init_clickhouse.py # Inisialisasi database
python etl/load_bronze.py # Load data ke Bronze
```

### Opsional (Untuk sekarang)
```bash
docker compose up -d metabase # Jalankan Metabase
# Buka http://localhost:3000 — tunggu kurleb 2 menit
```

Koneksi Metabase ke ClickHouse:

| Field    | Nilai        |
| -------- | ------------ |
| Type     | ClickHouse   |
| Host     | `clickhouse` |
| Port     | `8123`       |
| Database | `bronze`     |
| Username | `admin`      |
| Password | `admin123`   |

## dbt Models

Untuk menjalankan Silver/Gold transformation dengan dbt:

1. Salin `profiles.yml.example` ke `~/.dbt/profiles.yml`.
2. Sesuaikan koneksi ClickHouse di `profiles.yml` jika perlu.
3. Jalankan:

```bash
export CH_HOST=localhost
export CH_PORT=8123
export CH_USER=admin
export CH_PASSWORD=admin123
export CH_DATABASE=bronze

dbt run
```

Model yang dibuat:
- `silver_orders` → membersihkan dan mengetik ulang data Bronze.
- `gold_orders` → agregasi sales per `region` dan `order_month`.
- `kpi_summary` → KPI card values untuk Total Sales, Total Profit, Profit Margin.
- `monthly_sales_trend` → tren penjualan bulanan untuk Sales Trend.
- `product_performance` → ringkasan top products untuk Product Performance.
- `region_sales` → summary sales per region untuk dashboard Region.

Notebook verifikasi KPI:
- `notebooks/kpi_data_checks.ipynb` → memeriksa kondisi data yang mendukung semua KPI.
