# Retail-Sales-ELT

Pipeline ELT end-to-end untuk mengolah data penjualan retail **Superstore** (Kaggle) menjadi insight bisnis yang siap divisualisasikan. <br>Proyek ini memakai **Medallion Architecture** (Bronze -> Silver -> Gold) dengan ClickHouse sebagai data warehouse dan Metabase sebagai dashboard BI.

![Tech Stack](https://go-skill-icons.vercel.app/api/icons?i=kaggle,clickhouse,metabase,dbtlabs,python,pandas,scikitlearn,docker,jupyter&titles=true)

## 📊 Stack

Teknologi utama yang dipakai di proyek ini.

| Komponen             | Tool                                       |
| -------------------- | ------------------------------------------ |
| **Data Source**      | Kaggle Superstore                          |
| **Data Warehouse**   | ClickHouse 24.3                            |
| **ETL**              | Python 3.12+, pandas 3.0,<br>dbt Core 1.11 |
| **Machine Learning** | scikit-learn 1.8, XGBoost 3.2              |
| **Visualization**    | Metabase 0.60.1                            |
| **Container**        | Docker Compose                             |
| **Exploration**      | Jupyter 1.1.1, notebook 7.2.0              |

## 🏗️ Arsitektur Proyek

Diagram alur data utama dari sumber CSV sampai visualisasi di Metabase.

<img src="docs/architecture.png" alt="Architecture Diagram" width="800"/>

## 📁 Struktur Proyek

Daftar folder dan file utama di repositori ini.

```bash
retail-sales-elt/
├── data/
│   ├── samplesuperstore.csv                # Dataset Kaggle
│   ├── forecast_features.csv               # Fitur untuk model ML
│   ├── forecast_train.csv                  # Data training forecast
│   ├── forecast_test.csv                   # Data testing forecast
│   ├── model_metrics.csv                   # Metrik evaluasi model ML
│   ├── region_mapping.json                 # Mapping region ke kode
│   ├── sales_forecast_test_predictions.csv # Prediksi test set
│   └── sales_forecast_future.csv           # Prediksi masa depan
│
├── docs/
│   ├── architecture.png            # Diagram arsitektur proyek
│   ├── dashboard.md                # Dokumentasi implementasi dashboard Metabase
│   ├── kpi-definition.md           # Definisi KPI bisnis
│   └── ml-forecast.md              # Dokumentasi pipeline ML forecasting
│
├── etl/
│   ├── init_clickhouse.py          # Membuat database bronze/silver/gold
│   ├── load_bronze.py              # Load CSV -> layer Bronze
│   ├── load_forecast.py            # Load hasil forecast ML ke Gold
│   └── utils.py                    # Koneksi ClickHouse dan helper
│
├── macros/
│   └── generate_schema_name.sql    # Macro dbt
│
├── metabase-backup/
│   ├── metabase.db.mv.db           # Backup database Metabase
│   └── metabase.db.trace.db        # Trace log Metabase
│
├── ml/
│   └── train_forecast_models.py    # Training model ML (scikit-learn, XGBoost)
│
├── models/
│   ├── schema.yml                  # Definisi source dan model dbt
│   ├── silver/
│   │   └── silver_orders.sql       # Pembersihan dan cast tipe data
│   └── gold/
│       ├── forecast_training_monthly.sql # Data training forecast per bulan
│       ├── gold_orders.sql               # Agregasi per region dan bulan
│       ├── kpi_summary.sql               # KPI utama
│       ├── monthly_sales_trend.sql       # Tren penjualan bulanan
│       ├── product_performance.sql       # Performa produk terbaik
│       └── region_sales.sql              # Ringkasan sales per region
│
├── notebooks/
│   ├── bronze_verification.ipynb       # Validasi hasil load Bronze
│   ├── feature_engineering.ipynb       # Feature engineering untuk model ML
│   ├── forecast_model_evaluation.ipynb # Evaluasi performa model forecast
│   └── kpi_data_checks.ipynb           # Pemeriksaan data KPI
│
├── .env.example                    # Template environment variable
├── .gitignore                      # Daftar file/folder yang diabaikan Git
├── README.md                       # Dokumentasi utama proyek
├── dbt_project.yml                 # Konfigurasi dbt
├── docker-compose.yml              # ClickHouse + Metabase
├── profiles.yml                    # Konfigurasi koneksi dbt lokal
└── requirements.txt                # Dependency Python
```

## 📋 Model dbt

Daftar model transformasi yang membentuk layer Silver dan Gold di dbt.

| Model                       | Layer  | Description                                                     |
| --------------------------- | ------ | --------------------------------------------------------------- |
| `silver_orders`             | Silver | membersihkan dan mengetik ulang data Bronze.                    |
| `gold_orders`               | Gold   | agregasi sales per `region` dan `order_month`.                  |
| `kpi_summary`               | Gold   | KPI card values untuk Total Sales, Total Profit, Profit Margin. |
| `monthly_sales_trend`       | Gold   | tren penjualan bulanan untuk Sales Trend.                       |
| `product_performance`       | Gold   | ringkasan top products untuk Product Performance.               |
| `region_sales`              | Gold   | summary sales per region untuk dashboard Region.                |
| `forecast_training_monthly` | Gold   | data training agregat bulanan untuk model forecast ML.          |

## 📂 Dokumentasi

Dokumentasi teknis proyek tersimpan di folder `docs/`.

| File                                               | Deskripsi                                                                 |
| -------------------------------------------------- | ------------------------------------------------------------------------- |
| [`docs/dashboard.md`](docs/dashboard.md)           | Implementasi dashboard Metabase — layout, SQL queries, filter, drill-down |
| [`docs/kpi-definition.md`](docs/kpi-definition.md) | Definisi KPI bisnis — formula, granularity, dimensi, dan edge cases       |
| [`docs/ml-forecast.md`](docs/ml-forecast.md)       | Pipeline ML forecasting — fitur, model, evaluasi, dan cara menjalankan    |

## 🚀 Langkah-Langkah

### 1) Requirements
- Docker untuk ClickHouse dan Metabase
- Python 3.12+ (3.14 belum didukung dbt pada saat README ini ditulis)
- File `samplesuperstore.csv` dari Kaggle sudah ada di folder `data/`

### 2) Persiapan

```bash
# Clone repo
git clone https://github.com/itsceyuu/Retail-Sales-ELT
cd Retail-Sales-ELT

cp .env.example .env            # Copy .env.example to .env dan edit jika diperlukan

pip install -r requirements.txt # Install dependency Python

# (Opsional) Pake virtual environment, direkomendasikan kalo pke Linux
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

docker compose up -d            # Jalankan ClickHouse dan Metabase
```
### 3) Memuat Data dan Menjalankan transformasi

```bash
python etl/init_clickhouse.py   # Inisialisasi database (bronze, silver, gold)
python etl/load_bronze.py       # Load data ke Bronze

dbt run                         # Jalankan transformasi dbt untuk Silver dan Gold

python etl/load_forecast.py     # Load hasil forecast ML ke Gold
```

### 4) Membuka Metabase
- Buka browser ke `http://localhost:3000`
- Selesaikan setup awal Metabase (email dan password)
- Hubungkan ke ClickHouse:

| Field    | Nilai                |
| -------- | -------------------- |
| Type     | ClickHouse           |
| Host     | `clickhouse`         |
| Port     | `8123`               |
| Database | `bronze/silver/gold` |
| Username | `admin`              |
| Password | `admin123`           |

> Untuk detail lengkap implementasi dashboard (queries, layout, filter, drill-down), lihat [`docs/dashboard.md`](docs/dashboard.md).

## 📚 Referensi

- [dbt Documentation](https://docs.getdbt.com)
- [ClickHouse Docs](https://clickhouse.com/docs)
- [Metabase Setup](https://www.metabase.com/docs/latest)
- [Kaggle Superstore Dataset](https://www.kaggle.com/datasets/brittabegley/superstore-sales)
