"""Load and preprocess World Happiness Report 2023 data."""

from pathlib import Path

import pandas as pd

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


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing numeric values with column means (e.g. Healthy life expectancy)."""
    df = df.copy()
    numeric_cols = df.select_dtypes(include="number").columns
    for col in numeric_cols:
        if df[col].isna().any():
            mean_val = df[col].mean()
            n_missing = int(df[col].isna().sum())
            print(f"Filling {n_missing} missing value(s) in '{col}' with mean={mean_val:.3f}")
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
    missing = [c for c in feature_cols + [target_col, COUNTRY_COLUMN] if c not in df.columns]

    # Some datasets use "Ladder score" instead of "Happiness score"
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


def load_and_prepare(path: Path | str | None = None) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """Full pipeline: load CSV → impute missing → return X, y, meta."""
    df = load_raw_data(path)
    df = handle_missing_values(df)
    return prepare_features(df)


def get_full_dataframe(path: Path | str | None = None) -> pd.DataFrame:
    """Return the cleaned dataframe with features, target, and metadata."""
    X, y, meta = load_and_prepare(path)
    return pd.concat([meta, y.rename(TARGET_COLUMN), X], axis=1)


if __name__ == "__main__":
    X, y, meta = load_and_prepare()
    print(f"Loaded {len(y)} countries")
    print(f"Features: {list(X.columns)}")
    print(f"Target: {TARGET_COLUMN} | mean={y.mean():.3f}, std={y.std():.3f}")
    print(f"Missing values remaining: {X.isna().sum().sum() + y.isna().sum()}")
