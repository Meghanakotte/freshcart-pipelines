"""Produce a metrics table for the evaluation branch."""

import pandas as pd


def evaluate(output: dict) -> pd.DataFrame:
    predictions = output["predictions"]
    return pd.DataFrame(
        [
            {
                "metric": "test_accuracy",
                "value": output["test_accuracy"],
                "correct": int(
                    (predictions["species"] == predictions["prediction"]).sum()
                ),
                "total": len(predictions),
            }
        ]
    )


def test(metrics: pd.DataFrame) -> None:
    assert 0.0 <= float(metrics.loc[0, "value"]) <= 1.0
