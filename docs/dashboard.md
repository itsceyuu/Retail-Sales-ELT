# Dashboard Implementation Documentation — Retail Sales Dashboard

## Overview

Dokumentasi ini menjelaskan proses implementasi dashboard Business Intelligence pada proyek **Retail-Sales-ELT** menggunakan:

* ClickHouse sebagai data warehouse
* dbt sebagai transformation layer
* Metabase sebagai visualization & dashboard BI tool

Dashboard dibuat menggunakan data dari layer `gold` yang telah diproses oleh Analytics Engineer.

---

# Dashboard Objectives

Dashboard ini bertujuan untuk:

* Menampilkan KPI utama bisnis retail
* Membantu monitoring performa penjualan
* Menyediakan insight berdasarkan region, product, dan category
* Mendukung exploratory analysis menggunakan fitur drill-down

---

# Dashboard KPI

Lihat definisi detail tiap KPI di [`kpi-definition.md`](kpi-definition.md).

| KPI                   | Description                            |
| --------------------- | -------------------------------------- |
| Total Sales           | Total keseluruhan nilai penjualan      |
| Total Profit          | Total keuntungan bisnis                |
| Profit Margin         | Persentase profit terhadap total sales |
| Monthly Sales Trend   | Tren penjualan bulanan                 |
| Product Performance   | Top 5 product berdasarkan sales        |
| Sales Per Region      | Distribusi sales berdasarkan region    |
| Detailed Transactions | Drill-down transaction analysis        |

---

# Data Sources

Semua visualisasi dashboard menggunakan tabel dari schema `gold`.

| Table                    | Usage                     |
| ------------------------ | ------------------------- |
| gold.kpi_summary         | KPI Cards                 |
| gold.monthly_sales_trend | Sales Trend Chart         |
| gold.product_performance | Product Performance Chart |
| gold.region_sales        | Region Analysis           |
| gold.gold_orders         | Detailed Drill-down Table |
| gold.gold_orders         | Sales per Category Chart  |

---

# Dashboard Layout

## Section 1 — KPI Cards

Menampilkan:

* Total Sales
* Total Profit
* Profit Margin

Visualization Type:

* Number Cards

---

## Section 2 — Main Analytics

Menampilkan:

* Monthly Sales Trend
* Product Performance
* Sales Per Region
* Category Analysis

Visualization Type:

* Line Chart
* Horizontal Bar Chart
* Vertical Bar Chart
* Donut Chart

---

## Section 3 — Drill Down Analysis

Menampilkan:

* Detailed transaction table
* Filtered insights berdasarkan interaksi user

Visualization Type:

* Table

---

# SQL Queries Used

## 1. KPI Summary

Source Table:

```sql
SELECT *
FROM gold.kpi_summary
```

Used For:

* Total Sales
* Total Profit
* Profit Margin

Visualization:

* Number Card

---

## 2. Monthly Sales Trend

Query:

```sql
SELECT
    order_month,
    total_sales
FROM gold.monthly_sales_trend
ORDER BY order_month
```

Visualization:

* Line Chart

Purpose:

* Menampilkan tren penjualan bulanan

---

## 3. Product Performance

Query:

```sql
SELECT
    product_name,
    total_sales
FROM gold.product_performance
ORDER BY total_sales DESC
LIMIT 5
```

Visualization:

* Horizontal Bar Chart

Purpose:

* Menampilkan Top 5 product berdasarkan sales

---

## 4. Sales Per Region

Query:

```sql
SELECT
    region,
    total_sales
FROM gold.region_sales
ORDER BY total_sales DESC
```

Visualization:

* Vertical Bar Chart

Purpose:

* Membandingkan performa sales antar region

---

## 5. Detailed Transactions (Drill Down Analysis)

Query:

```sql
SELECT
    order_id,
    order_date,
    product_name,
    category,
    region,
    sales,
    profit,
    ROUND(profit / sales * 100, 2) AS profit_margin_pct
FROM gold.gold_orders
ORDER BY order_date DESC
LIMIT 100
```

Visualization:

* Table

Purpose:

* Menampilkan detail transaksi berdasarkan hasil filter dan interaksi dashboard

---

# Dashboard Filters

Dashboard menggunakan beberapa filter interaktif:

| Filter     | Description                        |
| ---------- | ---------------------------------- |
| Region     | Filter berdasarkan wilayah         |
| Category   | Filter berdasarkan kategori produk |
| Order Date | Filter berdasarkan periode waktu   |

---

# Drill Down Implementation

Dashboard menggunakan fitur:

* Cross-filtering
* Dashboard filter interaction
* Click behavior

Flow implementasi:

1. User memilih salah satu chart
2. Metabase mengaktifkan filter dashboard
3. Seluruh chart otomatis menyesuaikan filter
4. Detailed transaction table berubah sesuai hasil filter

Contoh:

```text
Klik Region = West
↓
Semua chart berubah menjadi data Region West
↓
Detailed Transactions hanya menampilkan transaksi West
```

---

# Visualization Design Decisions

| Visualization        | Reason                                |
| -------------------- | ------------------------------------- |
| KPI Card             | Menampilkan metric utama secara cepat |
| Line Chart           | Cocok untuk time-series analysis      |
| Horizontal Bar Chart | Mudah membaca ranking product         |
| Vertical Bar Chart   | Efektif membandingkan region          |
| Donut Chart          | Menampilkan distribusi category       |
| Table                | Detail eksplorasi transaksi           |

---

# Metabase Implementation Steps

## 1. Connect Database

Hubungkan Metabase ke ClickHouse — lihat konfigurasi koneksi lengkap di [README.md → Membuka Metabase](../README.md#4-membuka-metabase).

## 2. Create Questions

Membuat query untuk setiap KPI dan chart menggunakan SQL queries di atas.

## 3. Save Questions

Menyimpan setiap visualisasi sebagai reusable question.

## 4. Create Dashboard

Menggabungkan seluruh question ke dashboard utama.

## 5. Add Filters

Menambahkan region, category, dan date filter.

## 6. Enable Drill Down

Mengaktifkan click behavior dan cross-filtering.

---

# Final Result

Dashboard berhasil menyediakan:

* Executive KPI monitoring
* Interactive filtering
* Product & regional analysis
* Monthly sales monitoring
* Detailed transaction exploration
* Drill-down business analysis

---

# Conclusion

Dashboard Business Intelligence berhasil diimplementasikan menggunakan arsitektur Medallion (Bronze → Silver → Gold) dengan Metabase sebagai visualization layer.

Dashboard mendukung:

* KPI monitoring
* Interactive analysis
* Drill-down exploration
* Executive reporting

serta memberikan insight bisnis yang lebih cepat dan mudah dipahami oleh stakeholder.
