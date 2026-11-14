"""Run the assignment's max_depth experiment table."""

import csv
from pathlib import Path

from iris_project.run_pipeline import run


def run_experiments(output_dir: str = "experiments") -> list[dict]:
    root = Path(output_dir)
    rows = []
    for depth in range(1, 6):
        destination = root / f"max-depth-{depth}"
        try:
            accuracy = run(depth, str(destination), test=True)
            rows.append(
                {
                    "max_depth": depth,
                    "test_accuracy": accuracy,
                    "test_passed": True,
                    "predictions_created": (destination / "iris_predictions.csv").exists(),
                }
            )
        except AssertionError:
            rows.append(
                {
                    "max_depth": depth,
                    "test_accuracy": None,
                    "test_passed": False,
                    "predictions_created": (destination / "iris_predictions.csv").exists(),
                }
            )
    root.mkdir(parents=True, exist_ok=True)
    with (root / "experiment_results.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    for row in run_experiments():
        print(row)
