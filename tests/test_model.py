"""Tests for model training and evaluation."""

from pathlib import Path
import sys

import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from data_loader import load_for_modeling  # noqa: E402
from model import (  # noqa: E402
    build_pipeline,
    cross_validate_model,
    get_estimator,
    train_and_evaluate,
)


@pytest.fixture(scope="module")
def xy() -> tuple[pd.DataFrame, pd.Series]:
    X, y, _ = load_for_modeling()
    return X, y


def test_pipeline_has_imputer_and_model() -> None:
    from sklearn.linear_model import LinearRegression

    pipe = build_pipeline(LinearRegression())
    assert isinstance(pipe, Pipeline)
    assert "imputer" in pipe.named_steps
    assert "model" in pipe.named_steps


def test_cross_validate_returns_expected_keys(xy: tuple[pd.DataFrame, pd.Series]) -> None:
    X, y = xy
    scores = cross_validate_model("Linear Regression", X, y, n_splits=3)
    assert "R2_mean" in scores
    assert "R2_std" in scores
    assert "MAE_mean" in scores
    assert "RMSE_mean" in scores
    assert scores["R2_mean"] > 0.5


def test_train_and_evaluate_returns_all_models(xy: tuple[pd.DataFrame, pd.Series]) -> None:
    X, y = xy
    metrics_df, _, fitted, split = train_and_evaluate(X, y)
    assert len(metrics_df) == 3
    assert set(fitted.keys()) == {"Linear Regression", "Random Forest", "XGBoost"}
    assert len(split) == 4
    assert "R2_mean" in metrics_df.columns
    assert "Test_R2" in metrics_df.columns


def test_imputer_fits_on_train_only(xy: tuple[pd.DataFrame, pd.Series]) -> None:
    X, y = xy
    _, _, fitted, (X_train, X_test, _, _) = train_and_evaluate(X, y)
    pipe = fitted["Linear Regression"]
    imputer = pipe.named_steps["imputer"]
    train_mean = X_train["Healthy life expectancy"].mean()
    assert imputer.statistics_ is not None
    feature_idx = list(X.columns).index("Healthy life expectancy")
    assert imputer.statistics_[feature_idx] == pytest.approx(train_mean, rel=1e-3)


def test_get_estimator_from_pipeline(xy: tuple[pd.DataFrame, pd.Series]) -> None:
    X, y = xy
    _, _, fitted, _ = train_and_evaluate(X, y)
    estimator = get_estimator(fitted["Linear Regression"])
    assert hasattr(estimator, "coef_")
