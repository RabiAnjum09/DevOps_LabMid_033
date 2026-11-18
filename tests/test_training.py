import json
from pathlib import Path

import pandas as pd


def test_training_dataset():
    config = json.loads(Path("config.json").read_text())
    data = pd.read_csv("dataset/train.csv")

    assert len(data) >= 100
    assert set(config["features"]).issubset(data.columns)
    assert "label" in data.columns
    assert data["label"].nunique() == 2


def test_training_metrics():
    metrics_path = Path("artifacts/metrics.json")
    assert metrics_path.exists()

    metrics = json.loads(metrics_path.read_text())

    assert metrics["student_id"] == "FA23-BDS-033"
    assert metrics["training_rows"] >= 100
    assert 0 <= metrics["accuracy"] <= 1
    assert metrics["model_version"]
