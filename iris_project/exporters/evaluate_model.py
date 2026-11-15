"""Produce a metrics table for the evaluation branch."""

import pandas as pd
from sklearn.metrics import confusion_matrix


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


def confusion_matrix_table(output: dict) -> pd.DataFrame:
    predictions = output["predictions"]
    labels = sorted(predictions["species"].unique())
    matrix = confusion_matrix(
        predictions["species"], predictions["prediction"], labels=labels
    )
    return pd.DataFrame(matrix, index=labels, columns=labels).rename_axis(
        "actual"
    ).reset_index()


def test(metrics: pd.DataFrame) -> None:
    assert 0.0 <= float(metrics.loc[0, "value"]) <= 1.0
