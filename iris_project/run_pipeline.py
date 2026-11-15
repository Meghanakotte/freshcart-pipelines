"""Run the local equivalent of the Mage pipeline."""

import argparse
import json
from pathlib import Path

from iris_project.exporters.evaluate_model import confusion_matrix_table, evaluate
from iris_project.exporters.export_metrics import export as export_metrics
from iris_project.exporters.save_results import export as save_results
from iris_project.loaders.load_iris import load_data
from iris_project.transformers.prepare_data import transform
from iris_project.transformers.train_model import test as test_model
from iris_project.transformers.train_model import train
from iris_project.transformers.validate_iris import test as test_iris
from iris_project.transformers.validate_iris import transform as validate_iris


def run(max_depth: int = 3, output_dir: str = ".", test: bool = True) -> float:
    loaded = load_data()
    validated = validate_iris(loaded)
    if test:
        test_iris(validated)
    prepared = transform(validated)
    result = train(prepared, max_depth=max_depth)
    if test:
        test_model(result)
    destination = Path(output_dir)
    save_results(result, str(destination / "iris_predictions.csv"))
    metrics = evaluate(result)
    export_metrics(metrics, str(destination / "iris_metrics.csv"))
    confusion_matrix_table(result).to_csv(
        destination / "iris_confusion_matrix.csv", index=False
    )
    return result["test_accuracy"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--runtime-vars", default=None)
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--output-dir", default=".")
    args = parser.parse_args()
    runtime_vars = json.loads(args.runtime_vars) if args.runtime_vars else {}
    max_depth = int(runtime_vars.get("max_depth", args.max_depth))
    print(f"test_accuracy={run(max_depth, args.output_dir, test=True):.4f}")
