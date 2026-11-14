"""Prepare deterministic train and test splits for Iris."""

import pandas as pd
from sklearn.model_selection import train_test_split


def transform(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        from iris_project.loaders.load_iris import load_data

        df = load_data()
    train, test = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df["species"]
    )
    result = df.copy()
    result["split"] = "test"
    result.loc[train.index, "split"] = "train"
    return result.sort_index().reset_index(drop=True)

