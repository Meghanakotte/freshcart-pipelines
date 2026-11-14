"""Run the local equivalent of the Mage pipeline."""

import argparse
from pathlib import Path

from iris_project.exporters.evaluate_model import evaluate
from iris_project.exporters.export_metrics import export as export_metrics
from iris_project.exporters.save_results import export as save_results
from iris_project.loaders.load_iris import load_data
from iris_project.transformers.prepare_data import transform
from iris_project.transformers.train_model import test as test_model
from iris_project.transformers.train_model import train


def run(max_depth: int = 3, output_dir: str = ".") -> float:
    prepared = transform(load_data())
    result = train(prepared, max_depth=max_depth)
    test_model(result)
    destination = Path(output_dir)
    save_results(result, str(destination / "iris_predictions.csv"))
    metrics = evaluate(result)
    export_metrics(metrics, str(destination / "iris_metrics.csv"))
    return result["test_accuracy"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--output-dir", default=".")
    args = parser.parse_args()
    print(f"test_accuracy={run(args.max_depth, args.output_dir):.4f}")
