import random

from app.simulation.graph_builder import build_social_graph
from app.simulation.scoring import engagement_score, virality_score, watch_score


def _interest_match(persona: dict, target_audience: str) -> float:
    target = target_audience.lower()
    matches = sum(1 for interest in persona["interests"] if interest.lower() in target)
    base = 0.68 if persona["in_target"] else 0.36
    return min(1.0, base + matches * 0.12)


def _reason(persona: dict, action: str, score: float) -> str:
    if action == "shared":
        return f"{persona['name']} shared because the demo matched their workflow and felt useful to their network."
    if action == "commented":
        return f"{persona['name']} engaged with a question because the product was relevant but needed more proof."
    if action == "liked":
        return f"{persona['name']} liked the demo because the hook was clear and practical."
    if action == "watched":
        return f"{persona['name']} watched but did not engage; the idea was understandable but not urgent enough."
    return f"{persona['name']} skipped because the topic did not strongly match their interests or trust threshold."


def run_propagation(personas: list[dict], analysis: dict, target_audience: str, max_rounds: int) -> dict:
    random.seed(f"{len(personas)}:{target_audience}:{max_rounds}")
    graph = build_social_graph(personas)
    seed_count = max(5, int(len(personas) * 0.08))
    ranked = sorted(
        range(len(personas)),
        key=lambda idx: (_interest_match(personas[idx], target_audience), personas[idx]["engagement_tendency"]),
        reverse=True,
    )
    active = set(ranked[:seed_count])
    reached: set[int] = set()
    decisions = []
    spread_edges = []
    rounds = []

    for round_number in range(1, max_rounds + 1):
        if not active:
            break
        next_active: set[int] = set()
        likes = comments = shares = 0
        newly_reached = 0

        for node in active:
            if node in reached:
                continue
            reached.add(node)
            newly_reached += 1
            persona = personas[node]
            interest = _interest_match(persona, target_audience)
            watched_score = watch_score(persona, analysis, interest)
            engaged_score = engagement_score(persona, analysis, interest)

            watched = watched_score >= 0.48
            liked = watched and engaged_score >= 0.58
            commented = watched and engaged_score >= 0.68 and persona["skepticism_level"] > 0.25
            shared = watched and engaged_score >= 0.74 and persona["share_probability"] >= 0.38
            if liked:
                likes += 1
            if commented:
                comments += 1
            if shared:
                shares += 1

            action = "skipped"
            if shared:
                action = "shared"
            elif commented:
                action = "commented"
            elif liked:
                action = "liked"
            elif watched:
                action = "watched"

            decisions.append(
                {
                    "persona_index": node,
                    "round_number": round_number,
                    "watched": watched,
                    "liked": liked,
                    "commented": commented,
                    "shared": shared,
                    "engagement_score": round(engaged_score, 3),
                    "action": action,
                    "reason": _reason(persona, action, engaged_score),
                }
            )

            if liked or commented or shared:
                fanout = random.randint(4, 6) if shared else random.randint(2, 3)
                neighbors = sorted(
                    graph.neighbors(node),
                    key=lambda n: graph.edges[node, n]["interest_similarity"],
                    reverse=True,
                )
                for target in neighbors[:fanout]:
                    if target not in reached:
                        next_active.add(target)
                        spread_edges.append(
                            {
                                "source": node,
                                "target": target,
                                "type": "direct_share" if shared else "algorithmic_push",
                                "weight": graph.edges[node, target]["relationship_strength"],
                            }
                        )

        rounds.append(
            {
                "round_number": round_number,
                "active_agents": len(active),
                "new_reach": newly_reached,
                "likes": likes,
                "comments": comments,
                "shares": shares,
            }
        )
        active = next_active

    total_reach = len(reached)
    likes = sum(1 for d in decisions if d["liked"])
    comments = sum(1 for d in decisions if d["commented"])
    shares = sum(1 for d in decisions if d["shared"])
    out_of_target_reach = sum(1 for idx in reached if not personas[idx]["in_target"])

    denominator = max(1, total_reach)
    metrics = {
        "predicted_reach": total_reach,
        "out_of_target_rate": round(out_of_target_reach / denominator, 3),
        "like_rate": round(likes / denominator, 3),
        "comment_rate": round(comments / denominator, 3),
        "share_rate": round(shares / denominator, 3),
        "cascade_depth": rounds[-1]["round_number"] if rounds else 0,
        "normalized_reach": total_reach / max(1, len(personas)),
        "cascade_depth_score": (rounds[-1]["round_number"] if rounds else 0) / max_rounds,
        "audience_fit_score": analysis["audience_fit_score"],
    }
    metrics["virality_score"] = virality_score(metrics)
    metrics["verdict"] = verdict(metrics)

    return {
        "personas": personas,
        "decisions": decisions,
        "edges": spread_edges,
        "rounds": rounds,
        "metrics": metrics,
    }


def verdict(metrics: dict) -> str:
    """Return a documented verdict label from explicit metric thresholds.

    Viral candidate: share_rate > 0.15 and out_of_target_rate > 0.40.
    Niche hit: share_rate > 0.10 and out_of_target_rate < 0.30.
    Solid in-target performance: share_rate >= 0.05, out_of_target_rate < 0.30, and like_rate > 0.50.
    Strong in-demo, no breakout: share_rate < 0.05 and like_rate > 0.50.
    Low signal: normalized_reach < 0.20 after higher-engagement labels are ruled out.
    Out-of-target breakout: out_of_target_rate >= 0.30 after viral-candidate conditions are ruled out.
    Mixed performance: normalized_reach >= 0.20, out_of_target_rate < 0.30,
    share_rate <= 0.10, and like_rate <= 0.50.
    """
    if metrics["share_rate"] > 0.15 and metrics["out_of_target_rate"] > 0.4:
        return "Viral candidate"
    if metrics["share_rate"] > 0.1 and metrics["out_of_target_rate"] < 0.3:
        return "Niche hit"
    if (
        metrics["share_rate"] >= 0.05
        and metrics["out_of_target_rate"] < 0.3
        and metrics["like_rate"] > 0.5
    ):
        return "Solid in-target performance"
    if metrics["share_rate"] < 0.05 and metrics["like_rate"] > 0.5:
        return "Strong in-demo, no breakout"
    if metrics["normalized_reach"] < 0.2:
        return "Low signal"
    if metrics["out_of_target_rate"] >= 0.3:
        return "Out-of-target breakout"
    if (
        metrics["normalized_reach"] >= 0.2
        and metrics["out_of_target_rate"] < 0.3
        and metrics["share_rate"] <= 0.1
        and metrics["like_rate"] <= 0.5
    ):
        return "Mixed performance"
    raise ValueError(f"Metrics do not match a documented verdict condition: {metrics}")
