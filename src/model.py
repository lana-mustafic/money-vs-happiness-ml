"""Train, evaluate, and interpret ML models for Happiness score prediction."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.base import BaseEstimator
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, silhouette_score
from sklearn.model_selection import (
    GridSearchCV,
    KFold,
    cross_validate,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from data_loader import FEATURE_COLUMNS, PROJECT_ROOT, TARGET_COLUMN, load_for_modeling

logger = logging.getLogger(__name__)

PLOTS_DIR = PROJECT_ROOT / "results" / "plots"
RESULTS_DIR = PROJECT_ROOT / "results"
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5
KMEANS_K_RANGE = range(2, 8)

SplitTuple = tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]


def ensure_dirs() -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def build_pipeline(estimator: BaseEstimator) -> Pipeline:
    """Wrap an estimator with mean imputation (fit on train only)."""
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="mean")),
            ("model", estimator),
        ]
    )


def get_estimator(fitted: Pipeline | BaseEstimator) -> BaseEstimator:
    """Extract the regressor from a fitted Pipeline."""
    if isinstance(fitted, Pipeline):
        return fitted.named_steps["model"]
    return fitted


def build_base_estimators() -> dict[str, BaseEstimator]:
    """Return base regressors before hyperparameter tuning."""
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


def tune_hyperparameters(
    name: str,
    X_train: pd.DataFrame,
    y_train: pd.Series,
) -> Pipeline:
    """GridSearchCV on train set for tree-based models; LR uses defaults."""
    base = build_base_estimators()[name]
    pipeline = build_pipeline(base)

    if name == "Linear Regression":
        pipeline.fit(X_train, y_train)
        return pipeline

    param_grids: dict[str, dict[str, list[Any]]] = {
        "Random Forest": {
            "model__n_estimators": [100, 200],
            "model__max_depth": [4, 8, None],
        },
        "XGBoost": {
            "model__n_estimators": [100, 200],
            "model__max_depth": [3, 4, 6],
            "model__learning_rate": [0.05, 0.1],
        },
    }

    grid = GridSearchCV(
        pipeline,
        param_grids[name],
        cv=3,
        scoring="r2",
        n_jobs=-1,
        refit=True,
    )
    grid.fit(X_train, y_train)
    logger.info(
        "%s best params: %s (CV R2=%.4f)",
        name,
        grid.best_params_,
        grid.best_score_,
    )
    return grid.best_estimator_


def split_data(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
) -> SplitTuple:
    return train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )


def evaluate_model(
    model: Pipeline | BaseEstimator,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict[str, float | np.ndarray]:
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    r2 = r2_score(y_test, preds)
    return {"R2": r2, "MAE": mae, "RMSE": rmse, "predictions": preds}


def cross_validate_model(
    name: str,
    X: pd.DataFrame,
    y: pd.Series,
    n_splits: int = CV_FOLDS,
) -> dict[str, float]:
    """K-fold cross-validation with imputation inside each fold."""
    pipeline = build_pipeline(build_base_estimators()[name])
    cv = KFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    scores = cross_validate(
        pipeline,
        X,
        y,
        cv=cv,
        scoring={
            "r2": "r2",
            "mae": "neg_mean_absolute_error",
            "rmse": "neg_root_mean_squared_error",
        },
        n_jobs=-1,
    )
    return {
        "R2_mean": float(scores["test_r2"].mean()),
        "R2_std": float(scores["test_r2"].std()),
        "MAE_mean": float(-scores["test_mae"].mean()),
        "MAE_std": float(scores["test_mae"].std()),
        "RMSE_mean": float(-scores["test_rmse"].mean()),
        "RMSE_std": float(scores["test_rmse"].std()),
    }


def train_and_evaluate(
    X: pd.DataFrame | None = None,
    y: pd.Series | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Pipeline], SplitTuple]:
    """
    Cross-validate, tune, and evaluate all models.

    Returns metrics (CV + holdout test), fitted pipelines, and the test split.
    """
    if X is None or y is None:
        X, y, _ = load_for_modeling()

    X_train, X_test, y_train, y_test = split_data(X, y)
    fitted: dict[str, Pipeline] = {}
    cv_rows: list[dict[str, Any]] = []
    test_rows: list[dict[str, Any]] = []

    logger.info("=" * 60)
    logger.info("MODEL TRAINING & EVALUATION")
    logger.info("=" * 60)
    logger.info("Train size: %d | Test size: %d", len(X_train), len(X_test))

    for name in build_base_estimators():
        cv_scores = cross_validate_model(name, X, y)
        cv_rows.append({"Model": name, **cv_scores})
        logger.info(
            "%s CV (%d-fold): R2=%.4f±%.4f  MAE=%.4f±%.4f  RMSE=%.4f±%.4f",
            name,
            CV_FOLDS,
            cv_scores["R2_mean"],
            cv_scores["R2_std"],
            cv_scores["MAE_mean"],
            cv_scores["MAE_std"],
            cv_scores["RMSE_mean"],
            cv_scores["RMSE_std"],
        )

        model = tune_hyperparameters(name, X_train, y_train)
        fitted[name] = model
        test_scores = evaluate_model(model, X_test, y_test)
        test_rows.append(
            {
                "Model": name,
                "Test_R2": test_scores["R2"],
                "Test_MAE": test_scores["MAE"],
                "Test_RMSE": test_scores["RMSE"],
            }
        )
        logger.info(
            "%s Test:  R2=%.4f  MAE=%.4f  RMSE=%.4f",
            name,
            test_scores["R2"],
            test_scores["MAE"],
            test_scores["RMSE"],
        )

    cv_df = pd.DataFrame(cv_rows).sort_values("R2_mean", ascending=False)
    test_df = pd.DataFrame(test_rows).sort_values("Test_R2", ascending=False)
    metrics_df = cv_df.merge(test_df, on="Model").sort_values("R2_mean", ascending=False)

    logger.info("--- Ranked by CV R2 ---")
    logger.info("\n%s", metrics_df.to_string(index=False))
    return metrics_df, cv_df, fitted, (X_train, X_test, y_train, y_test)


def plot_model_comparison(
    metrics_df: pd.DataFrame,
    save_dir: Path | None = None,
) -> Path:
    save_dir = save_dir or PLOTS_DIR
    ensure_dirs()

    plot_cols = ["R2_mean", "MAE_mean", "RMSE_mean"]
    melted = metrics_df.melt(
        id_vars="Model", value_vars=plot_cols, var_name="Metric", value_name="Value"
    )
    melted["Metric"] = melted["Metric"].str.replace("_mean", "")

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, metric in zip(axes, ["R2", "MAE", "RMSE"]):
        subset = melted[melted["Metric"] == metric]
        sns.barplot(data=subset, x="Model", y="Value", ax=ax, color="#457b9d")
        ax.set_title(f"{metric} (5-fold CV mean)")
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
    fig.suptitle("Model Comparison — Cross-Validated Metrics")
    fig.tight_layout()
    out = save_dir / "model_comparison.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    logger.info("Saved: %s", out)
    return out


def get_feature_importance(
    model: Pipeline | BaseEstimator,
    feature_names: list[str],
) -> pd.Series | None:
    estimator = get_estimator(model)
    if hasattr(estimator, "feature_importances_"):
        return pd.Series(estimator.feature_importances_, index=feature_names).sort_values(
            ascending=False
        )
    if hasattr(estimator, "coef_"):
        return pd.Series(np.abs(estimator.coef_), index=feature_names).sort_values(
            ascending=False
        )
    return None


def plot_feature_importance(
    fitted_models: dict[str, Pipeline],
    feature_names: list[str] | None = None,
    save_dir: Path | None = None,
) -> Path:
    feature_names = feature_names or FEATURE_COLUMNS
    save_dir = save_dir or PLOTS_DIR
    ensure_dirs()

    tree_models = {
        k: v
        for k, v in fitted_models.items()
        if k in ("Random Forest", "XGBoost")
        and hasattr(get_estimator(v), "feature_importances_")
    }

    fig, axes = plt.subplots(1, len(tree_models), figsize=(12, 5), sharey=True)
    if len(tree_models) == 1:
        axes = [axes]

    for ax, (name, model) in zip(axes, tree_models.items()):
        imp = get_feature_importance(model, feature_names)
        if imp is None:
            continue
        imp_sorted = imp.sort_values(ascending=True)
        ax.barh(imp_sorted.index, imp_sorted.values, color="#2a9d8f")
        ax.set_title(name)
        ax.set_xlabel("Importance")
        logger.info("\n%s feature importance:\n%s", name, imp.to_string())

    fig.suptitle("Feature Importance — What Drives Happiness Predictions?")
    fig.tight_layout()
    out = save_dir / "feature_importance.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    logger.info("Saved: %s", out)
    return out


def analyze_kmeans_k(
    X_imputed: np.ndarray,
    k_range: range = KMEANS_K_RANGE,
    save_dir: Path | None = None,
) -> tuple[int, pd.DataFrame]:
    """
    Elbow + silhouette analysis to choose cluster count.

    Returns recommended k and a summary table of inertia / silhouette scores.
    """
    save_dir = save_dir or PLOTS_DIR
    ensure_dirs()

    rows: list[dict[str, float | int]] = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
        labels = km.fit_predict(X_imputed)
        rows.append(
            {
                "k": k,
                "inertia": km.inertia_,
                "silhouette": silhouette_score(X_imputed, labels),
            }
        )

    summary = pd.DataFrame(rows)
    best_k = int(summary.loc[summary["silhouette"].idxmax(), "k"])

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].plot(summary["k"], summary["inertia"], marker="o", color="#457b9d")
    axes[0].set_xlabel("Number of clusters (k)")
    axes[0].set_ylabel("Inertia")
    axes[0].set_title("Elbow Method")
    axes[0].grid(True, alpha=0.25)

    axes[1].plot(summary["k"], summary["silhouette"], marker="o", color="#2a9d8f")
    axes[1].axvline(best_k, color="#e76f51", linestyle="--", label=f"Best k={best_k}")
    axes[1].set_xlabel("Number of clusters (k)")
    axes[1].set_ylabel("Silhouette score")
    axes[1].set_title("Silhouette Analysis")
    axes[1].legend()
    axes[1].grid(True, alpha=0.25)

    fig.suptitle("K-Means: Choosing the Number of Clusters")
    fig.tight_layout()
    out = save_dir / "kmeans_elbow.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    logger.info("Saved: %s", out)
    logger.info("K-Means k analysis:\n%s", summary.to_string(index=False))
    logger.info("Recommended k (best silhouette): %d", best_k)
    return best_k, summary


def run_clustering(
    X: pd.DataFrame | None = None,
    y: pd.Series | None = None,
    meta: pd.DataFrame | None = None,
    n_clusters: int | None = None,
    save_dir: Path | None = None,
) -> pd.DataFrame:
    """
    K-Means clustering on scaled socio-economic profiles.

    Imputation for clustering uses full-dataset means (unsupervised EDA).
    """
    if X is None or y is None or meta is None:
        X, y, meta = load_for_modeling()

    save_dir = save_dir or PLOTS_DIR
    ensure_dirs()

    imputer = SimpleImputer(strategy="mean")
    X_imputed = imputer.fit_transform(X)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)

    if n_clusters is None:
        n_clusters, _ = analyze_kmeans_k(X_scaled, save_dir=save_dir)

    kmeans = KMeans(n_clusters=n_clusters, random_state=RANDOM_STATE, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    clustered = meta.copy()
    clustered[TARGET_COLUMN] = y.values
    clustered["Cluster"] = labels
    clustered["Logged GDP per capita"] = X["Logged GDP per capita"].values

    order = clustered.groupby("Cluster")[TARGET_COLUMN].mean().sort_values().index
    remap = {old: new for new, old in enumerate(order)}
    clustered["Cluster"] = clustered["Cluster"].map(remap)

    cluster_names = {0: "Lower happiness", 1: "Mid happiness", 2: "Higher happiness"}
    if n_clusters == 3:
        clustered["Cluster label"] = clustered["Cluster"].map(cluster_names)

    logger.info("=" * 60)
    logger.info("K-MEANS CLUSTERING (k=%d)", n_clusters)
    logger.info("=" * 60)
    summary = clustered.groupby("Cluster")[TARGET_COLUMN].agg(["count", "mean", "std"])
    logger.info("\n%s", summary.to_string())

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
    ax.set_title(f"Country Clusters by Socio-Economic Profile (K-Means, k={n_clusters})")
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    out = save_dir / "kmeans_clusters.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    logger.info("Saved: %s", out)

    return clustered


def save_metrics(metrics_df: pd.DataFrame) -> Path:
    ensure_dirs()
    out = RESULTS_DIR / "model_metrics.csv"
    metrics_df.to_csv(out, index=False)
    logger.info("Saved metrics: %s", out)
    return out


def run_full_pipeline() -> dict[str, Any]:
    """End-to-end: train models, plot comparisons, feature importance, clustering."""
    ensure_dirs()
    X, y, meta = load_for_modeling()
    metrics_df, cv_df, fitted, split = train_and_evaluate(X, y)
    save_metrics(metrics_df)
    plot_model_comparison(metrics_df)
    plot_feature_importance(fitted, list(X.columns))
    clustered = run_clustering(X, y, meta)
    return {
        "metrics": metrics_df,
        "cv_metrics": cv_df,
        "models": fitted,
        "split": split,
        "clusters": clustered,
    }


if __name__ == "__main__":
    from logging_config import setup_logging

    setup_logging()
    run_full_pipeline()
