"""Tests for data loading and preprocessing."""

from pathlib import Path
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from data_loader import (  # noqa: E402
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    load_and_prepare,
    load_for_modeling,
    load_raw_data,
    prepare_features,
)


def test_load_raw_data_shape() -> None:
    df = load_raw_data()
    assert len(df) >= 130
    assert "Country name" in df.columns
    assert TARGET_COLUMN in df.columns


def test_feature_columns_present() -> None:
    X, y, meta = load_for_modeling()
    assert list(X.columns) == FEATURE_COLUMNS
    assert len(y) == len(X)
    assert len(meta) == len(X)
    assert "Country name" in meta.columns


def test_imputation_in_eda_path() -> None:
    X, y, _ = load_and_prepare(verbose=False)
    assert X.isna().sum().sum() == 0
    assert y.isna().sum() == 0


def test_modeling_path_preserves_raw_missing() -> None:
    X, _, _ = load_for_modeling()
    raw = load_raw_data()
    X_raw, _, _ = prepare_features(raw)
    assert X.isna().sum().sum() == X_raw.isna().sum().sum()
    assert X_raw["Healthy life expectancy"].isna().any()


def test_prepare_features_renames_ladder_score() -> None:
    df = pd.DataFrame(
        {
            "Country name": ["A", "B"],
            "Ladder score": [5.0, 6.0],
            **{col: [1.0, 2.0] for col in FEATURE_COLUMNS},
        }
    )
    _, y, _ = prepare_features(df)
    assert y.name == TARGET_COLUMN
    assert list(y) == [5.0, 6.0]


def test_missing_columns_raises() -> None:
    df = pd.DataFrame({"Country name": ["A"], "Happiness score": [5.0]})
    with pytest.raises(KeyError, match="Missing expected columns"):
        prepare_features(df)
