from app.simulation.propagation import verdict


def test_verdict_does_not_call_in_target_performance_out_of_target_breakout():
    result = verdict(
        {
            "share_rate": 0.061,
            "out_of_target_rate": 0.152,
            "like_rate": 0.848,
            "normalized_reach": 0.65,
        }
    )

    assert result == "Solid in-target performance"


def test_out_of_target_breakout_requires_meaningful_out_of_target_reach():
    result = verdict(
        {
            "share_rate": 0.06,
            "out_of_target_rate": 0.36,
            "like_rate": 0.32,
            "normalized_reach": 0.5,
        }
    )

    assert result == "Out-of-target breakout"


def test_mixed_performance_has_explicit_moderate_reach_condition():
    result = verdict(
        {
            "share_rate": 0.0,
            "out_of_target_rate": 0.12,
            "like_rate": 0.43,
            "normalized_reach": 0.21,
        }
    )

    assert result == "Mixed performance"


def test_low_signal_still_catches_low_reach_before_mixed_performance():
    result = verdict(
        {
            "share_rate": 0.0,
            "out_of_target_rate": 0.12,
            "like_rate": 0.43,
            "normalized_reach": 0.19,
        }
    )

    assert result == "Low signal"
