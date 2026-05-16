# ML Forecast Documentation — Retail Sales Forecasting

Dokumen ini menjelaskan pipeline Machine Learning yang digunakan untuk memprediksi penjualan bulanan per region pada proyek Retail-Sales-ELT.

# Tujuan

Membangun model forecasting untuk memprediksi `total_sales` per region untuk **6 bulan ke depan**, menggunakan data historis penjualan dari layer Gold.
Output forecast diintegrasikan kembali ke ClickHouse (layer Gold) dan divisualisasikan di Metabase.

# Alur Pipeline ML

```text
[gold.forecast_training_monthly]
            ↓
notebooks/feature_engineering.ipynb   → data/forecast_features.csv
            ↓
ml/train_forecast_models.py
            ↓
  ┌─────────────────────────────────────────┐
  │  data/model_metrics.csv                 │  ← metrik evaluasi tiap model
  │  data/sales_forecast_test_predictions.csv│  ← prediksi vs aktual (test set)
  │  data/sales_forecast_future.csv          │  ← forecast 6 bulan ke depan
  └─────────────────────────────────────────┘
            ↓
etl/load_forecast.py                   → gold.sales_forecast (ClickHouse)
            ↓
         Metabase
```

# Feature Engineering

Fitur dihasilkan oleh `notebooks/feature_engineering.ipynb` dari tabel `gold.forecast_training_monthly`.

| Fitur            | Tipe    | Deskripsi                                     |
| ---------------- | ------- | --------------------------------------------- |
| `region_encoded` | Numerik | Encoding label dari kolom `region`            |
| `year`           | Numerik | Tahun dari `order_month`                      |
| `month`          | Numerik | Bulan dari `order_month` (1–12)               |
| `lag_1_sales`    | Numerik | Total sales 1 bulan sebelumnya (per region)   |
| `lag_2_sales`    | Numerik | Total sales 2 bulan sebelumnya (per region)   |
| `lag_3_sales`    | Numerik | Total sales 3 bulan sebelumnya (per region)   |
| `rolling_avg_3`  | Numerik | Rata-rata sales 3 bulan terakhir (per region) |
| `rolling_avg_6`  | Numerik | Rata-rata sales 6 bulan terakhir (per region) |

**Target:** `total_sales` (agregat bulanan per region)


# Train/Test Split

Strategi split: **time-based** (bukan random) untuk menghindari data leakage.

```text
Timeline data: ──────────────────────────────────────────────
                [       TRAIN        ] [    TEST (6 bulan)   ]
                                      ↑
                                   cutoff
```

* **Test set**: 6 bulan terakhir dari data historis
* **Train set**: semua data sebelum cutoff
* Split dilakukan **per region** secara konsisten

> ⚠️ Random split tidak digunakan karena data time-series memiliki ketergantungan temporal.

# Model Candidates

Tiga model dilatih dan dibandingkan secara bersamaan:

| Model             | Library      | Hyperparameter Utama                                                     |
| ----------------- | ------------ | ------------------------------------------------------------------------ |
| Linear Regression | scikit-learn | Default                                                                  |
| Random Forest     | scikit-learn | `n_estimators=300`, `min_samples_leaf=2`, `random_state=42`              |
| XGBoost           | xgboost      | `n_estimators=400`, `learning_rate=0.03`, `max_depth=3`, `subsample=0.9` |

Model terbaik dipilih berdasarkan nilai **RMSE terendah** pada test set.



# Metrik Evaluasi

| Metrik   | Formula                             | Keterangan                |
| -------- | ----------------------------------- | ------------------------- |
| **MAE**  | `mean(                              | actual - predicted        | )`                | Rata-rata error absolut |
| **RMSE** | `sqrt(mean((actual - predicted)²))` | Sensitif terhadap outlier |
| **MAPE** | `mean(                              | actual - predicted        | / actual) × 100%` | Error dalam persen      |

Hasil evaluasi tersimpan di `data/model_metrics.csv` dan diurutkan berdasarkan RMSE terkecil.



# Future Forecasting

Setelah training, model terbaik digunakan untuk memprediksi 6 bulan ke depan menggunakan strategi **recursive forecasting**:

```text
Bulan N+1:  prediksi menggunakan lag dari data historis asli
Bulan N+2:  prediksi menggunakan hasil prediksi N+1 sebagai lag
Bulan N+3:  prediksi menggunakan hasil prediksi N+1 dan N+2 sebagai lag
...
```

Prediksi dilakukan **per region** secara terpisah.



# Output Files

| File                                       | Deskripsi                                           |
| ------------------------------------------ | --------------------------------------------------- |
| `data/model_metrics.csv`                   | MAE, RMSE, MAPE tiap model — diurutkan dari terbaik |
| `data/sales_forecast_test_predictions.csv` | Prediksi vs aktual per region, per bulan, per model |
| `data/sales_forecast_future.csv`           | Forecast 6 bulan ke depan per region, per model     |


# Cara Menjalankan

### 1) Pastikan data gold tersedia

```bash
dbt run   # Pastikan model forecast_training_monthly sudah ter-run
```

### 2) Jalankan feature engineering

Buka dan run seluruh cell di:

```
notebooks/feature_engineering.ipynb
```

Notebook ini menghasilkan `data/forecast_features.csv`.

### 3) Training model

```bash
python ml/train_forecast_models.py
```

Output yang dihasilkan:

```
data/model_metrics.csv
data/sales_forecast_test_predictions.csv
data/sales_forecast_future.csv
```

### 4) Load hasil forecast ke ClickHouse

```bash
python etl/load_forecast.py
```