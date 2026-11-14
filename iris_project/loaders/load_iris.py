"""Load the canonical Iris dataset."""

import pandas as pd
from sklearn.datasets import load_iris as sklearn_load_iris


def load_data() -> pd.DataFrame:
    dataset = sklearn_load_iris(as_frame=True)
    frame = dataset.frame.rename(columns={"target": "species"})
    frame["species"] = frame["species"].map(
        dict(enumerate(dataset.target_names))
    )
    return frame


load_iris = load_data
