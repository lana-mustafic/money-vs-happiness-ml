"""Tests for EDA predictor-redundancy (multicollinearity) checks."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from data_loader import FEATURE_COLUMNS, get_full_dataframe  # noqa: E402
from eda import (  # noqa: E402
    HIGH_CORR_THRESHOLD,
    VIF_HIGH_THRESHOLD,
    analyze_predictor_redundancy,
    compute_vif,
    predictor_pairwise_correlations,
)


def test_pairwise_covers_all_feature_pairs() -> None:
    df = get_full_dataframe(verbose=False)
    pairs = predictor_pairwise_correlations(df)
    n = len(FEATURE_COLUMNS)
    assert len(pairs) == n * (n - 1) // 2
    assert set(pairs["Faktor 1"]) | set(pairs["Faktor 2"]) == set(FEATURE_COLUMNS)


def test_gdp_and_life_expectancy_are_the_closest_pair() -> None:
    df = get_full_dataframe(verbose=False)
    pairs = predictor_pairwise_correlations(df)
    top = pairs.iloc[0]
    names = {top["Faktor 1"], top["Faktor 2"]}
    assert names == {"Logged GDP per capita", "Healthy life expectancy"}
    assert top["|r|"] >= HIGH_CORR_THRESHOLD
    assert pairs["Iznad praga 0.8"].sum() == 1


def test_no_column_is_dropped() -> None:
    df = get_full_dataframe(verbose=False)
    result = analyze_predictor_redundancy(df)
    assert result["dropped_columns"] == []
    vif = compute_vif(df)
    assert (vif["VIF"] < VIF_HIGH_THRESHOLD).all()
    assert list(FEATURE_COLUMNS) == [
        "Logged GDP per capita",
        "Social support",
        "Healthy life expectancy",
        "Freedom to make life choices",
        "Generosity",
        "Perceptions of corruption",
    ]
