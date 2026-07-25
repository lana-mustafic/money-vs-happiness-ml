"""Train, evaluate, and interpret ML models for Happiness score prediction."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from data_loader import FEATURE_COLUMNS, PROJECT_ROOT, TARGET_COLUMN, load_and_prepare

PLOTS_DIR = PROJECT_ROOT / "results" / "plots"
RESULTS_DIR = PROJECT_ROOT / "results"
RANDOM_STATE = 42
TEST_SIZE = 0.2


def ensure_dirs() -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def split_data(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
):
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def build_models() -> dict:
    """Return the three regressors to compare."""
    return {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=200,
            max_depth=8,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "XGBoost": XGBRegressor(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=RANDOM_STATE,
            n_jobs=-1,
            verbosity=0,
        ),
    }


def evaluate_model(model, X_test, y_test) -> dict:
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    r2 = r2_score(y_test, preds)
    return {"R2": r2, "MAE": mae, "RMSE": rmse, "predictions": preds}


def train_and_evaluate(
    X: pd.DataFrame | None = None,
    y: pd.Series | None = None,
) -> tuple[pd.DataFrame, dict, object, object]:
    """
    Train all models and return metrics table, fitted models, and test split.
    """
    if X is None or y is None:
        X, y, _ = load_and_prepare()

    X_train, X_test, y_train, y_test = split_data(X, y)
    models = build_models()
    metrics_rows = []
    fitted = {}

    print("=" * 60)
    print("MODEL TRAINING & EVALUATION")
    print("=" * 60)
    print(f"Train size: {len(X_train)} | Test size: {len(X_test)}\n")

    for name, model in models.items():
        model.fit(X_train, y_train)
        scores = evaluate_model(model, X_test, y_test)
        fitted[name] = model
        metrics_rows.append(
            {
                "Model": name,
                "R2": scores["R2"],
                "MAE": scores["MAE"],
                "RMSE": scores["RMSE"],
            }
        )
        print(
            f"{name:20s}  R2={scores['R2']:.4f}  "
            f"MAE={scores['MAE']:.4f}  RMSE={scores['RMSE']:.4f}"
        )

    metrics_df = pd.DataFrame(metrics_rows).sort_values("R2", ascending=False)
    print("\n--- Ranked by R2 ---")
    print(metrics_df.to_string(index=False))
    return metrics_df, fitted, (X_train, X_test, y_train, y_test)


def plot_model_comparison(metrics_df: pd.DataFrame, save_dir: Path | None = None) -> Path:
    save_dir = save_dir or PLOTS_DIR
    ensure_dirs()
    melted = metrics_df.melt(id_vars="Model", var_name="Metric", value_name="Value")

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, metric in zip(axes, ["R2", "MAE", "RMSE"]):
        subset = melted[melted["Metric"] == metric]
        sns.barplot(data=subset, x="Model", y="Value", ax=ax, color="#457b9d")
        ax.set_title(metric)
        ax.set_xlabel("")
        ax.tick_params(axis="x", rotation=20)
        for p in ax.patches:
            ax.annotate(
                f"{p.get_height():.3f}",
                (p.get_x() + p.get_width() / 2, p.get_height()),
                ha="center",
                va="bottom",
                fontsize=8,
            )
    fig.suptitle("Model Comparison on Test Set")
    fig.tight_layout()
    out = save_dir / "model_comparison.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


def get_feature_importance(model, feature_names: list[str]) -> pd.Series | None:
    if hasattr(model, "feature_importances_"):
        return pd.Series(model.feature_importances_, index=feature_names).sort_values(
            ascending=False
        )
    if hasattr(model, "coef_"):
        return pd.Series(np.abs(model.coef_), index=feature_names).sort_values(
            ascending=False
        )
    return None


def plot_feature_importance(
    fitted_models: dict,
    feature_names: list[str] | None = None,
    save_dir: Path | None = None,
) -> Path:
    """Bar charts of feature importance for RF and XGBoost."""
    feature_names = feature_names or FEATURE_COLUMNS
    save_dir = save_dir or PLOTS_DIR
    ensure_dirs()

    tree_models = {
        k: v
        for k, v in fitted_models.items()
        if k in ("Random Forest", "XGBoost") and hasattr(v, "feature_importances_")
    }

    fig, axes = plt.subplots(1, len(tree_models), figsize=(12, 5), sharey=True)
    if len(tree_models) == 1:
        axes = [axes]

    for ax, (name, model) in zip(axes, tree_models.items()):
        imp = get_feature_importance(model, feature_names)
        imp_sorted = imp.sort_values(ascending=True)
        ax.barh(imp_sorted.index, imp_sorted.values, color="#2a9d8f")
        ax.set_title(name)
        ax.set_xlabel("Importance")
        print(f"\n{name} feature importance:")
        print(imp.to_string())

    fig.suptitle("Feature Importance — What Drives Happiness Predictions?")
    fig.tight_layout()
    out = save_dir / "feature_importance.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


def run_clustering(
    X: pd.DataFrame | None = None,
    y: pd.Series | None = None,
    meta: pd.DataFrame | None = None,
    n_clusters: int = 3,
    save_dir: Path | None = None,
) -> pd.DataFrame:
    """
    K-Means clustering on socio-economic profiles.
    Groups countries by happiness-related factor patterns.
    """
    if X is None or y is None or meta is None:
        X, y, meta = load_and_prepare()

    save_dir = save_dir or PLOTS_DIR
    ensure_dirs()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=n_clusters, random_state=RANDOM_STATE, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    clustered = meta.copy()
    clustered[TARGET_COLUMN] = y.values
    clustered["Cluster"] = labels
    clustered["Logged GDP per capita"] = X["Logged GDP per capita"].values

    # Order clusters by mean happiness for readable labels
    order = clustered.groupby("Cluster")[TARGET_COLUMN].mean().sort_values().index
    remap = {old: new for new, old in enumerate(order)}
    clustered["Cluster"] = clustered["Cluster"].map(remap)
    labels_ordered = clustered["Cluster"].values

    cluster_names = {0: "Lower happiness", 1: "Mid happiness", 2: "Higher happiness"}
    if n_clusters == 3:
        clustered["Cluster label"] = clustered["Cluster"].map(cluster_names)

    print("\n" + "=" * 60)
    print("K-MEANS CLUSTERING")
    print("=" * 60)
    summary = clustered.groupby("Cluster")[TARGET_COLUMN].agg(["count", "mean", "std"])
    print(summary.to_string())

    fig, ax = plt.subplots(figsize=(10, 6))
    palette = {0: "#e76f51", 1: "#e9c46a", 2: "#2a9d8f"}
    for c in sorted(clustered["Cluster"].unique()):
        subset = clustered[clustered["Cluster"] == c]
        label = cluster_names.get(c, f"Cluster {c}")
        ax.scatter(
            subset["Logged GDP per capita"],
            subset[TARGET_COLUMN],
            c=palette.get(c, "#457b9d"),
            label=label,
            alpha=0.75,
            s=60,
            edgecolors="white",
            linewidths=0.4,
        )
    ax.set_xlabel("Logged GDP per capita")
    ax.set_ylabel("Happiness score")
    ax.set_title("Country Clusters by Socio-Economic Profile (K-Means)")
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    out = save_dir / "kmeans_clusters.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")

    return clustered


def save_metrics(metrics_df: pd.DataFrame) -> Path:
    ensure_dirs()
    out = RESULTS_DIR / "model_metrics.csv"
    metrics_df.to_csv(out, index=False)
    print(f"Saved metrics: {out}")
    return out


def run_full_pipeline() -> dict:
    """End-to-end: train models, plot comparisons, feature importance, clustering."""
    ensure_dirs()
    X, y, meta = load_and_prepare()
    metrics_df, fitted, split = train_and_evaluate(X, y)
    save_metrics(metrics_df)
    plot_model_comparison(metrics_df)
    plot_feature_importance(fitted, list(X.columns))
    clustered = run_clustering(X, y, meta)
    return {
        "metrics": metrics_df,
        "models": fitted,
        "split": split,
        "clusters": clustered,
    }


if __name__ == "__main__":
    run_full_pipeline()
