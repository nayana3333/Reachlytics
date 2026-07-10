from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.services.persona_service import _fallback_personas  # noqa: E402
from app.simulation.propagation import run_propagation  # noqa: E402

FIELDNAMES = [
    "hook_score",
    "clarity_score",
    "emotional_appeal_score",
    "shareability_score",
    "audience_fit_score",
    "population_size",
    "in_target_percentage",
    "round_count",
    "reach",
    "like_rate",
    "share_rate",
    "comment_rate",
    "out_of_target_rate",
    "cascade_depth",
    "normalized_reach",
    "virality_score",
    "verdict",
]

VERDICT_LABELS = [
    "Low signal",
    "Mixed performance",
    "Niche hit",
    "Out-of-target breakout",
    "Solid in-target performance",
    "Strong in-demo, no breakout",
    "Viral candidate",
]

TARGET_TEMPLATES = [
    "startup founders and small teams testing productivity tools",
    "gamers and esports enthusiasts who care about immersive gear",
    "students learning with low-cost study and focus apps",
    "creators and social media managers growing short-form content",
    "fitness beginners looking for simple home routines",
    "finance-conscious young professionals comparing budgeting tools",
    "designers and product managers evaluating workflow software",
    "parents buying practical household products online",
]

BROAD_DISCOVERY_TARGET = (
    "startups productivity marketing AI tools design creator economy analytics "
    "small business coding finance broad discovery audience"
)


def random_analysis(rng: random.Random, high_share: bool = False) -> dict[str, float]:
    if high_share:
        return {
            "hook_score": round(rng.uniform(0.82, 0.99), 3),
            "clarity_score": round(rng.uniform(0.82, 0.99), 3),
            "emotional_appeal_score": round(rng.uniform(0.82, 0.99), 3),
            "shareability_score": round(rng.uniform(0.9, 1.0), 3),
            "audience_fit_score": round(rng.uniform(0.82, 0.99), 3),
        }

    base = rng.uniform(0.15, 0.9)
    return {
        "hook_score": round(max(0.0, min(1.0, rng.gauss(base, 0.18))), 3),
        "clarity_score": round(max(0.0, min(1.0, rng.gauss(base, 0.16))), 3),
        "emotional_appeal_score": round(max(0.0, min(1.0, rng.uniform(0.05, 0.98))), 3),
        "shareability_score": round(max(0.0, min(1.0, rng.uniform(0.05, 0.99))), 3),
        "audience_fit_score": round(max(0.0, min(1.0, rng.gauss(base, 0.2))), 3),
    }


def set_target_split(personas: list[dict], in_target_percentage: float) -> None:
    in_target_count = int(round(len(personas) * in_target_percentage))
    for index, persona in enumerate(personas):
        persona["in_target"] = index < in_target_count


def scenario_for_label(label: str | None, rng: random.Random) -> tuple[str, dict[str, float], float, int, int]:
    population_size = rng.choice([50, 100, 200])
    round_count = rng.choice([4, 5, 6, 7])
    if label == "Viral candidate":
        target = BROAD_DISCOVERY_TARGET
        analysis = random_analysis(rng, high_share=True)
        return target, analysis, rng.uniform(0.42, 0.56), population_size, round_count
    if label == "Out-of-target breakout":
        target = BROAD_DISCOVERY_TARGET
        analysis = {
            "hook_score": round(rng.uniform(0.65, 0.85), 3),
            "clarity_score": round(rng.uniform(0.65, 0.85), 3),
            "emotional_appeal_score": round(rng.uniform(0.2, 0.65), 3),
            "shareability_score": round(rng.uniform(0.4, 0.7), 3),
            "audience_fit_score": round(rng.uniform(0.65, 0.85), 3),
        }
        return target, analysis, rng.uniform(0.25, 0.48), population_size, round_count
    if label == "Niche hit":
        target = "startup founders productivity marketing AI tools"
        analysis = random_analysis(rng, high_share=True)
        return target, analysis, rng.uniform(0.72, 0.84), population_size, round_count
    if label == "Solid in-target performance":
        target = "startup founders productivity marketing AI tools"
        analysis = {
            "hook_score": round(rng.uniform(0.75, 0.98), 3),
            "clarity_score": round(rng.uniform(0.75, 0.98), 3),
            "emotional_appeal_score": round(rng.uniform(0.55, 0.82), 3),
            "shareability_score": round(rng.uniform(0.5, 0.8), 3),
            "audience_fit_score": round(rng.uniform(0.75, 0.98), 3),
        }
        return target, analysis, rng.uniform(0.72, 0.84), population_size, round_count
    if label == "Strong in-demo, no breakout":
        target = "startup founders productivity tools"
        analysis = {
            "hook_score": round(rng.uniform(0.8, 0.98), 3),
            "clarity_score": round(rng.uniform(0.8, 0.98), 3),
            "emotional_appeal_score": round(rng.uniform(0.45, 0.8), 3),
            "shareability_score": round(rng.uniform(0.45, 0.75), 3),
            "audience_fit_score": round(rng.uniform(0.8, 0.98), 3),
        }
        return target, analysis, rng.uniform(0.68, 0.84), population_size, round_count
    if label == "Mixed performance":
        target = BROAD_DISCOVERY_TARGET
        analysis = {
            "hook_score": round(rng.uniform(0.65, 0.85), 3),
            "clarity_score": round(rng.uniform(0.65, 0.85), 3),
            "emotional_appeal_score": round(rng.uniform(0.2, 0.65), 3),
            "shareability_score": round(rng.uniform(0.4, 0.7), 3),
            "audience_fit_score": round(rng.uniform(0.65, 0.85), 3),
        }
        return target, analysis, rng.uniform(0.55, 0.72), population_size, round_count
    if label == "Low signal":
        target = rng.choice(TARGET_TEMPLATES)
        analysis = {
            "hook_score": round(rng.uniform(0.05, 0.35), 3),
            "clarity_score": round(rng.uniform(0.05, 0.35), 3),
            "emotional_appeal_score": round(rng.uniform(0.05, 0.35), 3),
            "shareability_score": round(rng.uniform(0.05, 0.3), 3),
            "audience_fit_score": round(rng.uniform(0.05, 0.35), 3),
        }
        return target, analysis, rng.uniform(0.6, 0.82), population_size, round_count

    broad_discovery_run = rng.random() < 0.12
    target = BROAD_DISCOVERY_TARGET if broad_discovery_run else rng.choice(TARGET_TEMPLATES)
    analysis = random_analysis(rng, high_share=broad_discovery_run)
    split = rng.uniform(0.45, 0.58) if broad_discovery_run else rng.uniform(0.6, 0.8)
    return target, analysis, split, population_size, round_count


def candidate_row(index: int, rng: random.Random, target_label: str | None = None) -> dict:
    target_base, analysis, in_target_percentage, population_size, round_count = scenario_for_label(target_label, rng)
    target_audience = f"{target_base} cohort {index}"
    personas = _fallback_personas(population_size, target_audience)
    rng.shuffle(personas)
    set_target_split(personas, in_target_percentage)

    if target_label == "Out-of-target breakout":
        for persona in personas:
            persona["share_probability"] = round(rng.uniform(0.2, 0.6), 2)
            persona["engagement_tendency"] = round(rng.uniform(0.25, 0.55), 2)
            persona["skepticism_level"] = round(rng.uniform(0.3, 0.85), 2)
    elif target_label == "Strong in-demo, no breakout":
        for persona in personas:
            persona["share_probability"] = round(rng.uniform(0.08, 0.35), 2)
    elif target_label == "Solid in-target performance":
        for persona in personas:
            persona["share_probability"] = round(rng.uniform(0.5, 0.9), 2)
            persona["engagement_tendency"] = round(rng.uniform(0.55, 0.8), 2)
    elif target_label == "Mixed performance":
        for persona in personas:
            persona["share_probability"] = round(rng.uniform(0.2, 0.6), 2)
            persona["engagement_tendency"] = round(rng.uniform(0.25, 0.55), 2)
            persona["skepticism_level"] = round(rng.uniform(0.3, 0.85), 2)

    result = run_propagation(personas, analysis, target_audience, round_count)
    metrics = result["metrics"]
    return {
        **analysis,
        "population_size": population_size,
        "in_target_percentage": round(in_target_percentage, 3),
        "round_count": round_count,
        "reach": metrics["predicted_reach"],
        "like_rate": metrics["like_rate"],
        "share_rate": metrics["share_rate"],
        "comment_rate": metrics["comment_rate"],
        "out_of_target_rate": metrics["out_of_target_rate"],
        "cascade_depth": metrics["cascade_depth"],
        "normalized_reach": round(metrics["normalized_reach"], 3),
        "virality_score": metrics["virality_score"],
        "verdict": metrics["verdict"],
    }


def generate_rows(row_count: int, seed: int, min_per_class: int) -> list[dict]:
    rng = random.Random(seed)
    rows: list[dict] = []
    label_counts: Counter[str] = Counter()
    attempts = 0
    max_attempts = row_count * 80

    while attempts < max_attempts and any(label_counts[label] < min_per_class for label in VERDICT_LABELS):
        missing = [label for label in VERDICT_LABELS if label_counts[label] < min_per_class]
        target_label = rng.choice(missing)
        row = candidate_row(attempts, rng, target_label)
        attempts += 1
        if label_counts[row["verdict"]] < min_per_class:
            rows.append(row)
            label_counts[row["verdict"]] += 1

    if any(label_counts[label] < min_per_class for label in VERDICT_LABELS):
        raise RuntimeError(
            f"Could not reach minimum class counts after {attempts} attempts: {dict(label_counts)}"
        )

    while len(rows) < row_count:
        row = candidate_row(attempts, rng)
        attempts += 1
        rows.append(row)

    rng.shuffle(rows)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Reachlytics verdict-classifier training data.")
    parser.add_argument("--rows", type=int, default=600, help="Number of simulated training rows to generate.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--min-per-class", type=int, default=40)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data" / "training_runs.csv",
        help="CSV output path.",
    )
    args = parser.parse_args()

    if args.rows < 500:
        raise ValueError("Generate at least 500 rows for a meaningful train/test split.")

    rows = generate_rows(args.rows, args.seed, args.min_per_class)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    label_counts = Counter(row["verdict"] for row in rows)
    print(f"Wrote {len(rows)} rows to {args.output}")
    print("Verdict distribution:")
    for label, count in label_counts.most_common():
        print(f"  {label}: {count}")


if __name__ == "__main__":
    main()
