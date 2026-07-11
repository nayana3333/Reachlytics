# Reachlytics Project Report

## 1. Problem Statement

Marketing and product teams often publish demo videos without a structured way to estimate who will engage, who will share, and where the content may lose momentum. Reachlytics turns that uncertainty into a measurable simulation problem.

The core question is:

> Given a product demo video and a target audience, how likely is the content to spread, and which factors explain the outcome?

## 2. Solution Overview

Reachlytics is a full-stack AI and simulation platform. A user uploads a product demo video, selects a target audience, and runs a propagation simulation across synthetic social personas.

The system produces:

- Content-quality scores
- Synthetic persona profiles
- Watch, like, comment, share, and skip decisions
- Round-by-round propagation results
- Graph visualization of spread
- Verdict label and improvement suggestions
- AI-source transparency for real AI vs fallback estimates

## 3. System Architecture

```text
Next.js + React Flow UI
        |
        | REST API
        v
FastAPI Backend
        |
        | SQLAlchemy ORM
        v
PostgreSQL

Redis + Celery
        |
        v
Async simulation jobs

LLM Provider Layer
        |
        v
OpenRouter / Gemini / Anthropic / Mock fallback
```

## 4. Data Model

The database is designed around simulation traceability:

- `users`: authenticated users
- `videos`: uploaded video metadata
- `transcripts`: transcript text and AI-source status
- `content_analyses`: hook, clarity, emotional appeal, shareability, audience fit, and visual description
- `simulations`: target audience, status, top-level metrics, verdict
- `personas`: synthetic audience profiles and behavior traits
- `agent_decisions`: per-persona watch/like/comment/share decisions and reasoning
- `graph_edges`: propagation links between personas
- `simulation_rounds`: round-level reach and engagement
- `reports`: final summary, risks, recommendations, and ML verdict prediction

## 5. Simulation Logic

Reachlytics uses a small-world graph structure to approximate clustered social networks. Each persona receives behavior scores such as engagement tendency, share probability, and skepticism level.

For every reached persona, the simulator computes:

- Watch probability
- Like probability
- Comment probability
- Share probability
- Explanation for the decision

Shares create stronger fanout, while likes and comments create smaller algorithmic pushes. The simulation stops after the configured round limit or when no new personas are reached.

## 6. Analytics Layer

The SQL analytics pack in `docs/sql_analytics_queries.sql` supports business-style analysis:

- Run summaries
- Verdict distribution
- Audience-level performance comparison
- Round-by-round propagation funnel
- Persona behavior by target fit
- AI-source audit
- Content-quality vs outcome diagnostics

These queries make the project suitable for analytics and decision-science interviews, not only software engineering discussions.

## 7. Model Evaluation

Reachlytics includes two ML artifacts:

1. A pre-simulation Random Forest classifier that predicts the expected verdict from content and simulation inputs.
2. A post-simulation explainer classifier that recovers the rule-based verdict from final metrics.

The pre-simulation classifier is the legitimate prediction task. The post-simulation model is intentionally documented as a sanity-check because its labels are generated from the same final metrics used as features.

The verdict logic is also validated across 194,481 metric combinations using:

```bash
cd backend
python scripts/validate_verdict_space.py
```

## 8. Reliability Choices

Reachlytics is designed to run in both real-AI and demo-safe modes:

- Real providers: OpenRouter, Gemini, Anthropic/OpenAI
- Offline fallback: deterministic transcript, analysis, persona, and reasoning paths
- Queue fallback: inline mode when Redis/Celery is not connected
- Alembic schema guard to avoid running against stale database schemas
- Report-generation contract to avoid completed simulations without reports

## 9. Business Interpretation

A marketing or product team can use Reachlytics to compare content ideas before spending on campaigns. For example:

- Test whether a headset demo performs better with gamers, creators, or students
- Identify whether weak spread is caused by low hook quality, low shareability, or poor audience fit
- Inspect which persona types engaged and why
- Use SQL analytics to compare repeated simulation runs

## 10. Resume Framing

Best resume framing:

- Data-driven content strategy
- SQL-backed analytics
- Multi-agent graph simulation
- ML model evaluation
- Explainable AI-assisted reasoning
- Production-style backend architecture

Avoid overclaiming the post-simulation classifier as a predictive model. It is an explainer/sanity-check, while the pre-simulation classifier is the predictive component.
