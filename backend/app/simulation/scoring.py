def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def watch_score(persona: dict, analysis: dict, interest_match: float) -> float:
    return clamp(
        0.25 * analysis["hook_score"]
        + 0.2 * interest_match
        + 0.2 * analysis["audience_fit_score"]
        + 0.15 * analysis["clarity_score"]
        + 0.1 * analysis["emotional_appeal_score"]
        + 0.1 * persona["engagement_tendency"]
        - 0.12 * persona["skepticism_level"]
    )


def engagement_score(persona: dict, analysis: dict, interest_match: float) -> float:
    return clamp(
        0.3 * watch_score(persona, analysis, interest_match)
        + 0.25 * analysis["shareability_score"]
        + 0.2 * persona["share_probability"]
        + 0.15 * persona["engagement_tendency"]
        + 0.1 * interest_match
    )


def virality_score(metrics: dict) -> float:
    return round(
        100
        * clamp(
            0.25 * metrics["normalized_reach"]
            + 0.2 * metrics["share_rate"]
            + 0.15 * metrics["like_rate"]
            + 0.15 * metrics["comment_rate"]
            + 0.15 * metrics["cascade_depth_score"]
            + 0.1 * metrics["audience_fit_score"]
        ),
        2,
    )
