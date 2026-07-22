from __future__ import annotations

import argparse
from collections import Counter
import csv
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")  # headless-safe backend; this script never renders a window

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.ml.verdict_classifier import PRE_SIM_FEATURES  # noqa: E402

# The post-simulation model is intentionally an explainer/sanity check: its
# labels are deterministic verdict() outputs from these same metrics, so high
# accuracy means it recovered the rule thresholds, not that it made a new prediction.
POST_SIM_FEATURES = [
    "reach",
    "like_rate",
    "share_rate",
    "comment_rate",
    "out_of_target_rate",
    "cascade_depth",
    "normalized_reach",
]


def load_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))
    if not rows:
        raise ValueError(f"No rows found in {path}")
    return rows


def matrix(rows: list[dict], features: list[str]) -> list[list[float]]:
    import numpy as np

    return np.array([[float(row[feature]) for feature in features] for row in rows])


def labels(rows: list[dict]) -> list[str]:
    return [row["verdict"] for row in rows]


def train_model(name: str, rows: list[dict], features: list[str], output_path: Path) -> tuple[object, list[str], object]:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    from sklearn.model_selection import train_test_split
    import joblib

    y = labels(rows)
    counts = Counter(y)
    if min(counts.values()) < 2:
        raise ValueError(f"Cannot stratify {name}; each verdict needs at least 2 rows. Distribution: {counts}")

    x_train, x_test, y_train, y_test = train_test_split(
        matrix(rows, features),
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )
    model = RandomForestClassifier(
        n_estimators=350,
        max_depth=None,
        min_samples_leaf=2,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=1,
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    print(f"\n=== {name} ===")
    print(f"Features: {', '.join(features)}")
    print(f"Accuracy: {accuracy_score(y_test, predictions):.4f}")
    print("Classification report:")
    print(classification_report(y_test, predictions, zero_division=0))
    print("Confusion matrix:")
    print(confusion_matrix(y_test, predictions, labels=model.classes_))
    print("Labels:", list(model.classes_))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
    print(f"Saved model to {output_path}")
    return model, features, x_test


def save_feature_importance(model: object, features: list[str], output_path: Path) -> None:
    import matplotlib.pyplot as plt

    importances = list(zip(features, model.feature_importances_))
    importances.sort(key=lambda item: item[1], reverse=True)
    print("\nTop 3 features overall:")
    for feature, importance in importances[:3]:
        print(f"  {feature}: {importance:.4f}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(9, 5))
    plt.barh([feature for feature, _ in reversed(importances)], [score for _, score in reversed(importances)])
    plt.xlabel("Random forest feature importance")
    plt.title("Reachlytics verdict classifier feature importance")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()
    print(f"Saved feature-importance fallback plot to {output_path}")


def save_shap_summary(model: object, features: list[str], x_test: object, output_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        import shap

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(x_test)
        if isinstance(shap_values, list):
            shap_matrix = np.mean(np.abs(np.array(shap_values)), axis=0)
        elif getattr(shap_values, "ndim", 0) == 3:
            shap_matrix = np.mean(np.abs(shap_values), axis=2)
        else:
            shap_matrix = shap_values
        importances = list(zip(features, np.mean(np.abs(shap_matrix), axis=0)))
        importances.sort(key=lambda item: item[1], reverse=True)
        print("\nTop 3 SHAP features overall:")
        for feature, importance in importances[:3]:
            print(f"  {feature}: {importance:.4f}")
        shap.summary_plot(shap_matrix, x_test, feature_names=features, show=False)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(output_path, dpi=180)
        plt.close()
        print(f"Saved SHAP summary plot to {output_path}")
    except Exception as exc:
        print(f"SHAP summary failed ({exc}). Saving feature-importance fallback instead.")
        save_feature_importance(model, features, output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Reachlytics verdict classifiers.")
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "training_runs.csv")
    parser.add_argument("--models-dir", type=Path, default=ROOT / "models")
    args = parser.parse_args()

    rows = load_rows(args.input)
    print(f"Loaded {len(rows)} training rows from {args.input}")
    print("Verdict distribution:")
    for label, count in Counter(labels(rows)).most_common():
        print(f"  {label}: {count}")

    pre_model, pre_features, pre_x_test = train_model(
        "Pre-simulation verdict classifier",
        rows,
        PRE_SIM_FEATURES,
        args.models_dir / "verdict_classifier.joblib",
    )
    train_model(
        "Post-simulation verdict explainer classifier",
        rows,
        POST_SIM_FEATURES,
        args.models_dir / "verdict_classifier_post_sim.joblib",
    )
    save_shap_summary(pre_model, pre_features, pre_x_test, args.models_dir / "shap_summary.png")


if __name__ == "__main__":
    main()
