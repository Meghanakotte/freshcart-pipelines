"""Train the decision tree and expose a testable block."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier


FEATURES = [
    "sepal length (cm)",
    "sepal width (cm)",
    "petal length (cm)",
    "petal width (cm)",
]


def train(df: pd.DataFrame, max_depth: int = 3) -> dict:
    if max_depth < 1:
        raise ValueError("max_depth must be at least 1")
    model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    train_rows = df["split"].eq("train")
    test_rows = ~train_rows
    model.fit(df.loc[train_rows, FEATURES], df.loc[train_rows, "species"])
    predictions = model.predict(df.loc[test_rows, FEATURES])
    accuracy = accuracy_score(df.loc[test_rows, "species"], predictions)
    output = df.loc[test_rows, ["species"]].copy()
    output["prediction"] = predictions
    return {"model": model, "predictions": output, "test_accuracy": float(accuracy)}


def test(output: dict) -> None:
    assert output["test_accuracy"] >= 0.8


def save_model(output: dict, path: str = "iris_model.pkl") -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(output["model"], path)
