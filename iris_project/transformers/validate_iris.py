"""Custom C4 block validating the loaded Iris dataset."""

import pandas as pd


def transform(df: pd.DataFrame) -> pd.DataFrame:
    if df.isna().any().any():
        raise ValueError("Iris input contains missing values")
    if df["species"].nunique() != 3:
        raise ValueError("Iris input must contain exactly three classes")
    return df


def test(df: pd.DataFrame) -> None:
    assert not df.isna().any().any()
    assert df["species"].nunique() == 3
