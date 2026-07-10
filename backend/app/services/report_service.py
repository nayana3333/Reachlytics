from sqlalchemy.orm import Session

from app.models.report import Report


def create_report(db: Session, simulation_id: str, metrics: dict, ml_verdict_prediction: str | None = None) -> Report:
    existing = db.query(Report).filter(Report.simulation_id == simulation_id).first()
    if existing:
        if ml_verdict_prediction and not existing.ml_verdict_prediction:
            existing.ml_verdict_prediction = ml_verdict_prediction
            db.commit()
            db.refresh(existing)
        return existing

    verdict = metrics["verdict"]
    summary = (
        f"{verdict}. The simulation reached {metrics['predicted_reach']} personas with "
        f"a {metrics['share_rate'] * 100:.1f}% share rate and cascade depth of "
        f"{metrics['cascade_depth']} rounds."
    )
    report = Report(
        simulation_id=simulation_id,
        summary=summary,
        improvement_suggestions=[
            "Open with a sharper before-after transformation in the first 3 seconds.",
            "Add concrete proof such as metrics, customer quote, or visible output.",
            "Create a variant that directly addresses the highest-fit audience segment.",
        ],
        best_audience_segments=["startup founders", "growth marketers", "small software teams"],
        risk_factors=["May stay niche if the value proposition is too technical", "Weak emotional payoff can reduce shares"],
        ml_verdict_prediction=ml_verdict_prediction,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
