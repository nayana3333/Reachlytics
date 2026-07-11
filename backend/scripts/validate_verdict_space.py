from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.simulation.propagation import verdict  # noqa: E402

VALID_LABELS = {
    "Viral candidate",
    "Niche hit",
    "Solid in-target performance",
    "Strong in-demo, no breakout",
    "Mixed performance",
    "Low signal",
    "Out-of-target breakout",
}


def stepped_values() -> list[float]:
    return [round(index * 0.05, 2) for index in range(21)]


def main() -> None:
    labels: Counter[str] = Counter()
    checked = 0
    failures: list[tuple[dict, str]] = []

    for share_rate in stepped_values():
        for out_of_target_rate in stepped_values():
            for like_rate in stepped_values():
                for normalized_reach in stepped_values():
                    metrics = {
                        "share_rate": share_rate,
                        "out_of_target_rate": out_of_target_rate,
                        "like_rate": like_rate,
                        "normalized_reach": normalized_reach,
                        "comment_rate": 0.0,
                        "cascade_depth": 1,
                        "cascade_depth_score": 0.2,
                        "audience_fit_score": 0.7,
                        "predicted_reach": int(normalized_reach * 200),
                    }
                    checked += 1
                    try:
                        label = verdict(metrics)
                    except Exception as exc:  # noqa: BLE001
                        failures.append((metrics, f"exception: {exc}"))
                        continue
                    if label not in VALID_LABELS:
                        failures.append((metrics, f"unexpected label: {label}"))
                        continue
                    labels[label] += 1

    print(f"Checked {checked} metric combinations.")
    if failures:
        print(f"Found {len(failures)} failures.")
        for metrics, reason in failures[:10]:
            print(f"  {reason}: {metrics}")
        raise SystemExit(1)

    print("No gaps or unexpected labels found.")
    print("Verdict distribution:")
    for label in sorted(VALID_LABELS):
        print(f"  {label}: {labels[label]}")


if __name__ == "__main__":
    main()
