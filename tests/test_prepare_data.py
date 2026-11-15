import pandas as pd

from iris_project.loaders.load_iris import load_data
from iris_project.transformers.prepare_data import transform
from iris_project.transformers.validate_iris import test as run_validate_iris_test
from iris_project.transformers.validate_iris import transform as validate_iris


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


def test_custom_iris_validation_block():
    result = validate_iris(load_data())
    run_validate_iris_test(result)
