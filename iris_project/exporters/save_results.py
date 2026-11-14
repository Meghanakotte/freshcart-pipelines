"""Persist predictions only after the training test passes."""

from pathlib import Path

import pandas as pd


def export(output: dict, path: str = "iris_predictions.csv") -> pd.DataFrame:
    if output["test_accuracy"] < 0.8:
        raise ValueError("test accuracy gate failed; predictions were not saved")
    predictions = output["predictions"]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(path, index=False)
    return predictions


def test(output: dict) -> None:
    assert output["test_accuracy"] >= 0.8
