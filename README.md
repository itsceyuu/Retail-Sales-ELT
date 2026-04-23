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