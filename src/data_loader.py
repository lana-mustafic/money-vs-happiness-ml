"""Load and preprocess World Happiness Report 2023 data."""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "WHR2023.csv"

FEATURE_COLUMNS = [
    "Logged GDP per capita",
    "Social support",
    "Healthy life expectancy",
    "Freedom to make life choices",
    "Generosity",
    "Perceptions of corruption",
]

TARGET_COLUMN = "Happiness score"
COUNTRY_COLUMN = "Country name"
OPTIONAL_COLUMNS = ["Regional indicator", "iso alpha"]


def load_raw_data(path: Path | str | None = None) -> pd.DataFrame:
    """Load the raw WHR2023 CSV file."""
    data_path = Path(path) if path else DEFAULT_DATA_PATH
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at: {data_path}")
    return pd.read_csv(data_path)


def handle_missing_values(
    df: pd.DataFrame,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Fill missing numeric values with column means.

    Used for EDA and dashboard only. Modeling uses sklearn SimpleImputer
    inside a Pipeline fit on the training fold to avoid leakage.
    """
    df = df.copy()
    cols_to_impute = [
        c for c in FEATURE_COLUMNS + [TARGET_COLUMN]
        if c in df.columns and df[c].isna().any()
    ]
    for col in cols_to_impute:
        mean_val = df[col].mean()
        n_missing = int(df[col].isna().sum())
        msg = (
            f"Filling {n_missing} missing value(s) in '{col}' "
            f"with mean={mean_val:.3f}"
        )
        if verbose:
            logger.info(msg)
        df[col] = df[col].fillna(mean_val)
    return df


def prepare_features(
    df: pd.DataFrame,
    feature_cols: list[str] | None = None,
    target_col: str = TARGET_COLUMN,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Select modeling features and target.

    Returns
    -------
    X : feature matrix
    y : target vector (Happiness score)
    meta : country / region metadata for interpretation
    """
    feature_cols = feature_cols or FEATURE_COLUMNS
    missing = [
        c for c in feature_cols + [target_col, COUNTRY_COLUMN] if c not in df.columns
    ]

    if target_col not in df.columns and "Ladder score" in df.columns:
        df = df.rename(columns={"Ladder score": target_col})
        missing = [c for c in missing if c != target_col]

    if missing:
        raise KeyError(f"Missing expected columns: {missing}")

    keep_meta = [c for c in [COUNTRY_COLUMN, *OPTIONAL_COLUMNS] if c in df.columns]
    meta = df[keep_meta].copy()
    X = df[feature_cols].copy()
    y = df[target_col].copy()
    return X, y, meta


def load_for_modeling(
    path: Path | str | None = None,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Load features for ML without imputation.

    Missing values are handled by SimpleImputer inside the sklearn Pipeline,
    fitted only on training data.
    """
    df = load_raw_data(path)
    return prepare_features(df)


def load_and_prepare(
    path: Path | str | None = None,
    verbose: bool = True,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """Full pipeline for EDA/dashboard: load CSV → impute → return X, y, meta."""
    df = load_raw_data(path)
    df = handle_missing_values(df, verbose=verbose)
    return prepare_features(df)


def get_full_dataframe(
    path: Path | str | None = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """Return the cleaned dataframe with features, target, and metadata."""
    X, y, meta = load_and_prepare(path, verbose=verbose)
    return pd.concat([meta, y.rename(TARGET_COLUMN), X], axis=1)


def load_data(path: Path | str | None = None) -> pd.DataFrame:
    """Convenience loader for dashboards / notebooks (quiet by default)."""
    return get_full_dataframe(path, verbose=False)


if __name__ == "__main__":
    from logging_config import setup_logging

    setup_logging()
    X, y, meta = load_and_prepare()
    logger.info("Loaded %d countries", len(y))
    logger.info("Features: %s", list(X.columns))
    logger.info(
        "Target: %s | mean=%.3f, std=%.3f",
        TARGET_COLUMN,
        y.mean(),
        y.std(),
    )
    logger.info(
        "Missing values remaining: %d",
        int(X.isna().sum().sum() + y.isna().sum()),
    )
