"""Export the evaluation branch's metrics."""

from pathlib import Path

import pandas as pd


def export(metrics: pd.DataFrame, path: str = "iris_metrics.csv") -> pd.DataFrame:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(path, index=False)
    return metrics


def test(metrics: pd.DataFrame) -> None:
    assert {"metric", "value", "correct", "total"} <= set(metrics.columns)
