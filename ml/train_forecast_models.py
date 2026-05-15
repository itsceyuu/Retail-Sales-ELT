"""Train retail sales forecasting models from engineered monthly features.

This script is the Person 3 modeling step. It reads the feature dataset created
by the feature engineering notebook, rebuilds a clean time-based train/test
split, trains three models, and writes model outputs for dashboard integration.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

try:
    from xgboost import XGBRegressor
except ImportError:  # pragma: no cover - handled at runtime for local setup.
    XGBRegressor = None


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
FEATURE_PATH = DATA_DIR / "forecast_features.csv"
METRICS_PATH = DATA_DIR / "model_metrics.csv"
TEST_PREDICTIONS_PATH = DATA_DIR / "sales_forecast_test_predictions.csv"
FUTURE_FORECAST_PATH = DATA_DIR / "sales_forecast_future.csv"
REGION_MAPPING_PATH = DATA_DIR / "region_mapping.json"

TARGET_COL = "total_sales"
FEATURE_COLS = [
    "region_encoded",
    "year",
    "month",
    "lag_1_sales",
    "lag_2_sales",
    "lag_3_sales",
    "rolling_avg_3",
    "rolling_avg_6",
]


def load_features() -> pd.DataFrame:
    """Load feature data and add a proper monthly date column."""
    if not FEATURE_PATH.exists():
        raise FileNotFoundError(
            f"Feature file not found: {FEATURE_PATH}. "
            "Run notebooks/feature_engineering.ipynb first."
        )

    df = pd.read_csv(FEATURE_PATH)
    df["order_month"] = pd.to_datetime(
        df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2) + "-01"
    )
    return df.sort_values(["region", "order_month"]).reset_index(drop=True)


def split_by_time(df: pd.DataFrame, test_months: int = 6) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Use the last N calendar months as test data for every region."""
    max_month = df["order_month"].max()
    cutoff = max_month - pd.DateOffset(months=test_months - 1)

    train_df = df[df["order_month"] < cutoff].copy()
    test_df = df[df["order_month"] >= cutoff].copy()

    if train_df.empty or test_df.empty:
        raise ValueError("Train/test split produced an empty dataset.")

    return train_df, test_df


def mape(y_true: pd.Series, y_pred: np.ndarray) -> float:
    """Mean absolute percentage error, guarded for zero actuals."""
    denominator = np.where(y_true.to_numpy() == 0, 1, y_true.to_numpy())
    return float(np.mean(np.abs((y_true.to_numpy() - y_pred) / denominator)) * 100)


def evaluate(y_true: pd.Series, y_pred: np.ndarray, model_name: str) -> dict[str, float | str]:
    """Return standard forecast evaluation metrics."""
    return {
        "model_name": model_name,
        "mae": round(mean_absolute_error(y_true, y_pred), 2),
        "rmse": round(np.sqrt(mean_squared_error(y_true, y_pred)), 2),
        "mape": round(mape(y_true, y_pred), 2),
    }


def build_models() -> dict[str, object]:
    """Create forecasting model candidates."""
    models: dict[str, object] = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=300,
            min_samples_leaf=2,
            random_state=42,
        ),
    }

    if XGBRegressor is not None:
        models["XGBoost"] = XGBRegressor(
            objective="reg:squarederror",
            n_estimators=400,
            learning_rate=0.03,
            max_depth=3,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
        )

    return models


def forecast_future(
    model: object,
    history: pd.DataFrame,
    horizon_months: int = 6,
) -> pd.DataFrame:
    """Recursively forecast future monthly sales per region."""
    forecasts = []

    for region, region_history in history.groupby("region"):
        region_history = region_history.sort_values("order_month").copy()
        sales_history = region_history[TARGET_COL].tolist()
        last_month = region_history["order_month"].max()
        region_encoded = int(region_history["region_encoded"].iloc[-1])

        for step in range(1, horizon_months + 1):
            forecast_month = last_month + pd.DateOffset(months=step)
            recent_sales = sales_history[-6:]

            row = {
                "region_encoded": region_encoded,
                "year": forecast_month.year,
                "month": forecast_month.month,
                "lag_1_sales": sales_history[-1],
                "lag_2_sales": sales_history[-2],
                "lag_3_sales": sales_history[-3],
                "rolling_avg_3": float(np.mean(sales_history[-3:])),
                "rolling_avg_6": float(np.mean(recent_sales)),
            }

            prediction = float(model.predict(pd.DataFrame([row], columns=FEATURE_COLS))[0])
            prediction = max(prediction, 0.0)
            sales_history.append(prediction)

            forecasts.append(
                {
                    "region": region,
                    "order_month": forecast_month.date().isoformat(),
                    "forecast_sales": round(prediction, 2),
                }
            )

    return pd.DataFrame(forecasts)


def main() -> None:
    df = load_features()
    train_df, test_df = split_by_time(df)

    x_train = train_df[FEATURE_COLS]
    y_train = train_df[TARGET_COL]
    x_test = test_df[FEATURE_COLS]
    y_test = test_df[TARGET_COL]

    metrics = []
    test_predictions = []
    future_predictions = []
    models = build_models()

    for model_name, model in models.items():
        model.fit(x_train, y_train)

        y_pred = model.predict(x_test)
        metrics.append(evaluate(y_test, y_pred, model_name))

        model_test_predictions = test_df[
            ["region", "order_month", TARGET_COL]
        ].copy()
        model_test_predictions["model_name"] = model_name
        model_test_predictions["forecast_sales"] = np.round(y_pred, 2)
        model_test_predictions = model_test_predictions.rename(
            columns={TARGET_COL: "actual_sales"}
        )
        test_predictions.append(model_test_predictions)

        model_future = forecast_future(model, df)
        model_future["model_name"] = model_name
        future_predictions.append(model_future)

    metrics_df = pd.DataFrame(metrics).sort_values("rmse")
    test_predictions_df = pd.concat(test_predictions, ignore_index=True)
    future_predictions_df = pd.concat(future_predictions, ignore_index=True)

    metrics_df.to_csv(METRICS_PATH, index=False)
    test_predictions_df.to_csv(TEST_PREDICTIONS_PATH, index=False)
    future_predictions_df.to_csv(FUTURE_FORECAST_PATH, index=False)

    if REGION_MAPPING_PATH.exists():
        region_mapping = json.loads(REGION_MAPPING_PATH.read_text())
    else:
        region_mapping = dict(
            zip(df["region"].unique().tolist(), df["region_encoded"].unique().tolist())
        )

    print("Retail sales forecasting models trained.")
    print()
    print("Region mapping:")
    print(region_mapping)
    print()
    print("Train period:", train_df["order_month"].min().date(), "to", train_df["order_month"].max().date())
    print("Test period :", test_df["order_month"].min().date(), "to", test_df["order_month"].max().date())
    print()
    print(metrics_df.to_string(index=False))
    print()
    print("Files written:")
    print(f"- {METRICS_PATH.relative_to(ROOT_DIR)}")
    print(f"- {TEST_PREDICTIONS_PATH.relative_to(ROOT_DIR)}")
    print(f"- {FUTURE_FORECAST_PATH.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
