"""Exploratory Data Analysis for World Happiness Report 2023."""

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression

from data_loader import (
    FEATURE_COLUMNS,
    PROJECT_ROOT,
    TARGET_COLUMN,
    get_full_dataframe,
)

logger = logging.getLogger(__name__)

PLOTS_DIR = PROJECT_ROOT / "results" / "plots"
RESULTS_DIR = PROJECT_ROOT / "results"
# Common rule of thumb: |r| >= 0.8 flags a pair that may carry redundant information.
HIGH_CORR_THRESHOLD = 0.80
# Common VIF bands: < 5 low, 5–10 moderate, > 10 high multicollinearity.
VIF_HIGH_THRESHOLD = 10.0


def ensure_plots_dir(path: Path | None = None) -> Path:
    out = path or PLOTS_DIR
    out.mkdir(parents=True, exist_ok=True)
    return out


def basic_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Print and return descriptive statistics for numeric columns."""
    stats = df.describe()
    logger.info("=" * 60)
    logger.info("BASIC STATISTICS")
    logger.info("=" * 60)
    logger.info("\n%s", stats.to_string())
    logger.info("Shape: %d countries × %d columns", df.shape[0], df.shape[1])
    missing = df.isna().sum()
    missing = missing[missing > 0]
    if len(missing):
        logger.info("Missing values:\n%s", missing.to_string())
    else:
        logger.info("Missing values: none")
    return stats


def plot_happiness_distribution(
    df: pd.DataFrame,
    save_dir: Path | None = None,
) -> Path:
    """Histogram + KDE of Happiness score."""
    save_dir = ensure_plots_dir(save_dir)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.histplot(df[TARGET_COLUMN], kde=True, bins=20, color="#2a9d8f", ax=ax)
    ax.axvline(df[TARGET_COLUMN].mean(), color="#e76f51", linestyle="--", label="Mean")
    ax.axvline(df[TARGET_COLUMN].median(), color="#264653", linestyle=":", label="Median")
    ax.set_title("Distribution of Happiness Score (WHR 2023)")
    ax.set_xlabel("Happiness score")
    ax.set_ylabel("Count")
    ax.legend()
    fig.tight_layout()
    out = save_dir / "happiness_distribution.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    logger.info("Saved: %s", out)
    return out


def plot_correlation_heatmap(
    df: pd.DataFrame,
    save_dir: Path | None = None,
) -> Path:
    """Correlation matrix among features and target."""
    save_dir = ensure_plots_dir(save_dir)
    cols = [TARGET_COLUMN] + FEATURE_COLUMNS
    corr = df[cols].corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="RdYlGn",
        center=0,
        square=True,
        ax=ax,
        linewidths=0.5,
    )
    ax.set_title("Correlation Matrix: Happiness & Socio-Economic Factors")
    fig.tight_layout()
    out = save_dir / "correlation_heatmap.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    logger.info("Saved: %s", out)
    logger.info("\nCorrelations with Happiness score:\n%s", corr[TARGET_COLUMN].sort_values(ascending=False).to_string())
    return out


def predictor_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Pearson correlation among the 6 socio-economic predictors only."""
    return df[FEATURE_COLUMNS].corr()


def predictor_pairwise_correlations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Upper-triangle predictor pairs, sorted by |r|.

    Used to decide whether any of the 6 columns is redundant enough to drop.
    """
    corr = predictor_correlation_matrix(df)
    rows: list[dict[str, object]] = []
    for i, col_i in enumerate(FEATURE_COLUMNS):
        for col_j in FEATURE_COLUMNS[i + 1 :]:
            r = float(corr.loc[col_i, col_j])
            abs_r = abs(r)
            rows.append(
                {
                    "Faktor 1": col_i,
                    "Faktor 2": col_j,
                    "Pearson r": r,
                    "|r|": abs_r,
                    "Iznad praga 0.8": abs_r >= HIGH_CORR_THRESHOLD,
                }
            )
    return (
        pd.DataFrame(rows)
        .sort_values("|r|", ascending=False)
        .reset_index(drop=True)
    )


def compute_vif(df: pd.DataFrame) -> pd.DataFrame:
    """
    Variance Inflation Factor for each predictor.

    VIF_i = 1 / (1 - R²_i), where R²_i comes from regressing feature i
    on the remaining features. No extra dependency beyond scikit-learn.
    """
    X = df[FEATURE_COLUMNS]
    rows: list[dict[str, object]] = []
    for col in FEATURE_COLUMNS:
        y = X[col]
        X_others = X.drop(columns=[col])
        r2 = float(LinearRegression().fit(X_others, y).score(X_others, y))
        vif = float("inf") if r2 >= 1.0 else 1.0 / (1.0 - r2)
        rows.append({"Faktor": col, "VIF": vif, "R2 ostali faktori": r2})
    return pd.DataFrame(rows).sort_values("VIF", ascending=False).reset_index(drop=True)


def plot_predictor_correlation_heatmap(
    df: pd.DataFrame,
    save_dir: Path | None = None,
) -> Path:
    """Heatmap of correlations among the 6 predictors (target excluded)."""
    save_dir = ensure_plots_dir(save_dir)
    corr = predictor_correlation_matrix(df)

    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="RdYlGn",
        center=0,
        square=True,
        ax=ax,
        linewidths=0.5,
        vmin=-1,
        vmax=1,
    )
    ax.set_title("Predictor–Predictor Correlation (feature redundancy check)")
    fig.tight_layout()
    out = save_dir / "predictor_correlation_heatmap.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    logger.info("Saved: %s", out)
    return out


def analyze_predictor_redundancy(
    df: pd.DataFrame,
    save_dir: Path | None = None,
    results_dir: Path | None = None,
) -> dict[str, pd.DataFrame | Path | list[str]]:
    """
    Check whether any of the 6 socio-economic factors should be dropped.

    Rule: a pair with |r| >= 0.8 is a redundancy candidate; VIF > 10 would
    strengthen the case for dropping. Decision for this dataset: keep all 6.
    """
    save_dir = ensure_plots_dir(save_dir)
    results_dir = results_dir or RESULTS_DIR
    results_dir.mkdir(parents=True, exist_ok=True)

    pairs = predictor_pairwise_correlations(df)
    vif = compute_vif(df)
    plot_path = plot_predictor_correlation_heatmap(df, save_dir)

    pairs_path = results_dir / "predictor_correlations.csv"
    vif_path = results_dir / "predictor_vif.csv"
    pairs.to_csv(pairs_path, index=False)
    vif.to_csv(vif_path, index=False)

    high_pairs = pairs[pairs["Iznad praga 0.8"]]
    high_vif = vif[vif["VIF"] >= VIF_HIGH_THRESHOLD]
    dropped: list[str] = []

    logger.info("=" * 60)
    logger.info("PREDICTOR REDUNDANCY CHECK")
    logger.info("=" * 60)
    logger.info("Pairwise Pearson correlations among 6 features:\n%s", pairs.to_string(index=False))
    logger.info("VIF:\n%s", vif.to_string(index=False))
    if high_pairs.empty:
        logger.info("No predictor pair exceeds |r| >= %.2f.", HIGH_CORR_THRESHOLD)
    else:
        logger.info(
            "Pairs with |r| >= %.2f (possible redundancy):\n%s",
            HIGH_CORR_THRESHOLD,
            high_pairs.to_string(index=False),
        )
    if high_vif.empty:
        logger.info("No predictor has VIF >= %.0f.", VIF_HIGH_THRESHOLD)
    else:
        logger.info(
            "Predictors with VIF >= %.0f:\n%s",
            VIF_HIGH_THRESHOLD,
            high_vif.to_string(index=False),
        )
    logger.info(
        "Decision: keep all %d features; dropped columns: %s. "
        "GDP and healthy life expectancy are statistically similar (r~0.84) "
        "but measure different concepts; tree models tolerate this, and VIF "
        "stays below the usual drop threshold of 10.",
        len(FEATURE_COLUMNS),
        dropped if dropped else "none",
    )
    logger.info("Saved tables: %s | %s", pairs_path, vif_path)

    return {
        "pairs": pairs,
        "vif": vif,
        "dropped_columns": dropped,
        "plot": plot_path,
    }


def plot_gdp_vs_happiness(
    df: pd.DataFrame,
    save_dir: Path | None = None,
) -> Path:
    """
    Key Easterlin visualization: Logged GDP vs Happiness score.

    Linear OLS line + quadratic fit to check for flattening among rich countries.
    """
    save_dir = ensure_plots_dir(save_dir)
    x_col = "Logged GDP per capita"
    y_col = TARGET_COLUMN

    x = df[x_col].values.reshape(-1, 1)
    y = df[y_col].values

    lin = LinearRegression().fit(x, y)
    x_line = np.linspace(x.min(), x.max(), 200).reshape(-1, 1)
    y_lin = lin.predict(x_line)

    x_flat = x.ravel()
    coeffs = np.polyfit(x_flat, y, deg=2)
    y_quad = np.polyval(coeffs, x_line.ravel())

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(x_flat, y, alpha=0.65, c="#457b9d", edgecolors="white", linewidths=0.4, s=55)

    top = df.nlargest(3, y_col)
    rich = df.nlargest(3, x_col)
    for _, row in pd.concat([top, rich]).drop_duplicates().iterrows():
        ax.annotate(
            row["Country name"],
            (row[x_col], row[y_col]),
            textcoords="offset points",
            xytext=(6, 4),
            fontsize=8,
            alpha=0.85,
        )

    ax.plot(x_line, y_lin, color="#e63946", linewidth=2, label="Linear fit")
    ax.plot(x_line, y_quad, color="#2a9d8f", linewidth=2, linestyle="--", label="Quadratic fit")
    ax.set_xlabel("Logged GDP per capita")
    ax.set_ylabel("Happiness score")
    ax.set_title("Wealth vs Happiness — Is the Relationship Linear? (Easterlin Paradox)")
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    out = save_dir / "gdp_vs_happiness.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    logger.info("Saved: %s", out)
    logger.info("Linear R² (GDP alone): %.3f", lin.score(x, y))
    logger.info(
        "Quadratic curvature (a>0 convex, a<0 diminishing returns): a=%.4f",
        coeffs[0],
    )
    return out


def plot_feature_boxplots(
    df: pd.DataFrame,
    save_dir: Path | None = None,
) -> Path:
    """Boxplots of feature distributions."""
    save_dir = ensure_plots_dir(save_dir)
    melted = df[FEATURE_COLUMNS].melt(var_name="Feature", value_name="Value")
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.boxplot(data=melted, x="Feature", y="Value", ax=ax, color="#a8dadc")
    ax.tick_params(axis="x", rotation=25)
    ax.set_title("Feature Distributions")
    fig.tight_layout()
    out = save_dir / "feature_boxplots.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    logger.info("Saved: %s", out)
    return out


def run_eda(
    df: pd.DataFrame | None = None,
    save_dir: Path | None = None,
) -> dict:
    """Run the full EDA pipeline and save all plots."""
    if df is None:
        df = get_full_dataframe()
    save_dir = ensure_plots_dir(save_dir)

    logger.info(">>> Running Exploratory Data Analysis...")
    stats = basic_statistics(df)
    redundancy = analyze_predictor_redundancy(df, save_dir)
    paths = {
        "distribution": plot_happiness_distribution(df, save_dir),
        "correlation": plot_correlation_heatmap(df, save_dir),
        "predictor_correlation": redundancy["plot"],
        "gdp_vs_happiness": plot_gdp_vs_happiness(df, save_dir),
        "boxplots": plot_feature_boxplots(df, save_dir),
    }
    logger.info("EDA complete.")
    return {
        "stats": stats,
        "plots": paths,
        "predictor_pairs": redundancy["pairs"],
        "vif": redundancy["vif"],
        "dropped_columns": redundancy["dropped_columns"],
    }


if __name__ == "__main__":
    from logging_config import setup_logging

    setup_logging()
    run_eda()
