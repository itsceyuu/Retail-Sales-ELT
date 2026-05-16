# KPI Definition — Retail Sales Dashboard

Dokumen ini mendefinisikan Key Performance Indicators (KPI) yang digunakan untuk mengukur performa bisnis pada dashboard Retail Sales.

## Ringkasan KPI

| KPI           | Description                            | Formula                           |
| ------------- | -------------------------------------- | --------------------------------- |
| Total Sales   | Total keseluruhan nilai penjualan      | `SUM(sales)`                      |
| Total Profit  | Total keuntungan bisnis                | `SUM(profit)`                     |
| Profit Margin | Persentase profit terhadap total sales | `SUM(profit) / SUM(sales) * 100%` |
| Total Orders  | Jumlah transaksi unik                  | `COUNT(DISTINCT order_id)`        |

---

## 1. Total Sales

**Deskripsi**
Total nilai penjualan yang dihasilkan dari seluruh transaksi dalam periode tertentu.

**Tujuan**
Mengukur performa pendapatan bisnis secara keseluruhan.

**Formula**

```sql
SUM(sales)
```

**Granularity**
Transaction-level (per order)

**Dimensi Terkait**

* Waktu (harian, bulanan)
* Region
* Product
* Category

**Insight yang Diharapkan**

* Mengetahui total revenue
* Membandingkan performa antar periode
* Mengidentifikasi tren pertumbuhan penjualan

---

## 2. Total Profit

**Deskripsi**
Total keuntungan bersih dari seluruh transaksi setelah dikurangi biaya.

**Tujuan**
Mengukur profitabilitas bisnis.

**Formula**

```sql
SUM(profit)
```

**Granularity**
Transaction-level

**Dimensi Terkait**

* Product
* Category
* Region

**Insight yang Diharapkan**

* Mengetahui apakah bisnis menghasilkan keuntungan
* Mengidentifikasi area yang menghasilkan profit tinggi/rendah

---

## 3. Profit Margin

**Deskripsi**
Persentase keuntungan terhadap total penjualan, yang menunjukkan efisiensi bisnis.

**Tujuan**
Mengukur seberapa efektif bisnis dalam menghasilkan keuntungan dari penjualan.

**Formula**

```
SUM(profit) / SUM(sales) * 100%
```

**Granularity**
Aggregated (periode tertentu)

**Dimensi Terkait**

* Waktu
* Product
* Category

**Insight yang Diharapkan**

* Margin tinggi → bisnis efisien
* Margin rendah → biaya tinggi atau pricing tidak optimal

**Catatan (Edge Case)**

* Jika `SUM(sales) = 0`, maka margin tidak dapat dihitung (hindari division by zero)
* Profit negatif → margin negatif (indikasi kerugian)

---

## 4. Total Orders

**Deskripsi**
Jumlah transaksi unik dalam periode tertentu.

**Tujuan**
Mengukur volume aktivitas penjualan.

**Formula**

```sql
COUNT(DISTINCT order_id)
```

**Granularity**
Order-level

**Dimensi Terkait**

* Waktu
* Region
* Customer

**Insight yang Diharapkan**

* Mengetahui jumlah transaksi
* Mengukur pertumbuhan aktivitas bisnis
* Membandingkan jumlah order dengan total sales (untuk analisis AOV)

---

## Catatan Umum

* Semua KPI dapat difilter berdasarkan dimensi seperti waktu, region, dan kategori produk.
* KPI ini digunakan sebagai dasar dalam pembuatan visualisasi dashboard di Metabase.
* Konsistensi definisi KPI penting untuk memastikan interpretasi data yang akurat antar tim.
