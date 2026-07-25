"""Exploratory Data Analysis for World Happiness Report 2023."""

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

PLOTS_DIR = PROJECT_ROOT / "results" / "plots"


def ensure_plots_dir(path: Path | None = None) -> Path:
    out = path or PLOTS_DIR
    out.mkdir(parents=True, exist_ok=True)
    return out


def basic_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Print and return descriptive statistics for numeric columns."""
    stats = df.describe()
    print("=" * 60)
    print("BASIC STATISTICS")
    print("=" * 60)
    print(stats.to_string())
    print()
    print(f"Shape: {df.shape[0]} countries × {df.shape[1]} columns")
    print(f"Missing values:\n{df.isna().sum()[df.isna().sum() > 0]}")
    return stats


def plot_happiness_distribution(df: pd.DataFrame, save_dir: Path | None = None) -> Path:
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
    print(f"Saved: {out}")
    return out


def plot_correlation_heatmap(df: pd.DataFrame, save_dir: Path | None = None) -> Path:
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
    print(f"Saved: {out}")
    print("\nCorrelations with Happiness score:")
    print(corr[TARGET_COLUMN].sort_values(ascending=False).to_string())
    return out


def plot_gdp_vs_happiness(df: pd.DataFrame, save_dir: Path | None = None) -> Path:
    """
    Key Easterlin visualization: Logged GDP vs Happiness score.

    Linear OLS line + LOWESS-style quadratic fit to check for flattening
    among the richest countries.
    """
    save_dir = ensure_plots_dir(save_dir)
    x_col = "Logged GDP per capita"
    y_col = TARGET_COLUMN

    x = df[x_col].values.reshape(-1, 1)
    y = df[y_col].values

    lin = LinearRegression().fit(x, y)
    x_line = np.linspace(x.min(), x.max(), 200).reshape(-1, 1)
    y_lin = lin.predict(x_line)

    # Quadratic fit to reveal potential diminishing returns
    x_flat = x.ravel()
    coeffs = np.polyfit(x_flat, y, deg=2)
    y_quad = np.polyval(coeffs, x_line.ravel())

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(x_flat, y, alpha=0.65, c="#457b9d", edgecolors="white", linewidths=0.4, s=55)

    # Annotate a few extremes for context
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
    print(f"Saved: {out}")
    print(f"Linear R² (GDP alone): {lin.score(x, y):.3f}")
    print("Quadratic curvature (a>0 convex, a<0 diminishing returns): "
          f"a={coeffs[0]:.4f}")
    return out


def plot_feature_boxplots(df: pd.DataFrame, save_dir: Path | None = None) -> Path:
    """Boxplots of standardized feature distributions."""
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
    print(f"Saved: {out}")
    return out


def run_eda(df: pd.DataFrame | None = None, save_dir: Path | None = None) -> dict:
    """Run the full EDA pipeline and save all plots."""
    if df is None:
        df = get_full_dataframe()
    save_dir = ensure_plots_dir(save_dir)

    print("\n>>> Running Exploratory Data Analysis...\n")
    stats = basic_statistics(df)
    paths = {
        "distribution": plot_happiness_distribution(df, save_dir),
        "correlation": plot_correlation_heatmap(df, save_dir),
        "gdp_vs_happiness": plot_gdp_vs_happiness(df, save_dir),
        "boxplots": plot_feature_boxplots(df, save_dir),
    }
    print("\nEDA complete.")
    return {"stats": stats, "plots": paths}


if __name__ == "__main__":
    run_eda()
