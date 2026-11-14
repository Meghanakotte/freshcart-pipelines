import pandas as pd

from iris_project.transformers.prepare_data import transform


def test_split_is_80_20_and_has_three_classes():
    result = transform(pd.DataFrame())

    assert len(result) == 150
    assert (result["split"] == "train").sum() == 120
    assert (result["split"] == "test").sum() == 30
    assert result["species"].nunique() == 3


def test_split_is_reproducible():
    first = transform(pd.DataFrame())
    second = transform(pd.DataFrame())

    pd.testing.assert_frame_equal(first, second)
