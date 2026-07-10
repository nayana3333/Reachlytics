from app.simulation.scoring import engagement_score, virality_score, watch_score


def test_watch_score_increases_with_interest_match():
    persona = {"engagement_tendency": 0.7, "skepticism_level": 0.2, "share_probability": 0.5}
    analysis = {
        "hook_score": 0.7,
        "audience_fit_score": 0.8,
        "clarity_score": 0.75,
        "emotional_appeal_score": 0.6,
        "shareability_score": 0.7,
    }

    assert watch_score(persona, analysis, 0.9) > watch_score(persona, analysis, 0.2)


def test_engagement_score_is_bounded():
    persona = {"engagement_tendency": 1, "skepticism_level": 0, "share_probability": 1}
    analysis = {
        "hook_score": 1,
        "audience_fit_score": 1,
        "clarity_score": 1,
        "emotional_appeal_score": 1,
        "shareability_score": 1,
    }

    assert engagement_score(persona, analysis, 1) == 1


def test_virality_score_returns_percentage_scale():
    score = virality_score(
        {
            "normalized_reach": 0.5,
            "share_rate": 0.2,
            "like_rate": 0.4,
            "comment_rate": 0.1,
            "cascade_depth_score": 0.5,
            "audience_fit_score": 0.8,
        }
    )

    assert 0 <= score <= 100
