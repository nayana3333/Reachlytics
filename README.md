# Reachlytics

**Simulates how a product demo video spreads across a target audience before you spend on distribution.**

Most teams post a demo video and hope. Reachlytics turns that into a measurable question: given a video and a target audience, how far does it spread, who engages, and why?

Reachlytics combines content scoring, synthetic persona generation, graph-based propagation simulation, SQL analytics, and an explainable verdict engine. It is built as a full-stack placement project with a production-shaped backend, clean UI, and honest fallback behavior when live AI APIs are unavailable.

> Add a screenshot or short GIF of the dashboard/graph replay here. A visual preview is the highest-impact README upgrade.

## Live Demo

- Frontend: https://reachlytics.vercel.app
- Full-stack local run: `docker compose up --build`
- Backend deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)

The deployed Vercel frontend is live. Login, upload, and simulation require the FastAPI backend, which can be run locally with Docker Compose or deployed separately using the Render guide.

## Highlights

- Simulates spread across **50-500 synthetic personas** using graph propagation with round-by-round replay
- Models persona-level **watch, like, comment, share, and skip** behavior
- Shows an explainable agent detail panel with persona profile, action, and reasoning
- Uses rule-based verdict labels such as `Viral candidate`, `Niche hit`, and `Low signal`
- Validates verdict logic across **194,481 metric combinations** with no gaps or unexpected labels
- Includes a SQL analytics layer for funnels, audience comparison, verdict distribution, and AI-source audit
- Trains a Random Forest verdict classifier with **78.3% documented accuracy** and explainability support
- Tags each simulation stage as **real AI** or **deterministic fallback**, so results are never silently misrepresented

## Tech Stack

| Area | Stack |
| --- | --- |
| Frontend | Next.js, React, TypeScript, Tailwind CSS, React Flow |
| Backend | FastAPI, SQLAlchemy, PostgreSQL, Alembic |
| Async | Redis + Celery, with inline fallback mode |
| Simulation | NetworkX-style graph propagation |
| AI/ML | OpenRouter, Gemini, Anthropic/OpenAI, mock mode, Random Forest, SHAP/feature importance |
| Infra | Docker Compose, Render-ready backend config, Vercel frontend |

## Architecture

```text
Next.js UI  --REST-->  FastAPI Backend  --SQLAlchemy-->  PostgreSQL
                              |
                         Redis + Celery
                              |
              Transcript -> Content Analysis -> Personas -> Graph Simulation -> Report
```

## Core Flow

1. User uploads a product demo video.
2. Backend stores video metadata and extracts transcript/video context.
3. Content analysis scores hook, clarity, emotional appeal, shareability, and audience fit.
4. System generates synthetic personas for the target audience.
5. Graph propagation simulates multi-round exposure and engagement.
6. Final report shows virality score, reach, engagement rates, cascade depth, graph spread, and improvement suggestions.

## Decision Science Angle

Reachlytics is not just an AI wrapper. It decomposes content performance into measurable variables:

- Content quality: hook, clarity, emotional appeal, shareability, audience fit
- Audience behavior: watch, like, comment, share, skip
- Network behavior: reach, cascade depth, fanout, out-of-target spread
- Business output: verdict, risks, improvement suggestions, persona-level explanations

The analytics layer is designed for interview discussion around SQL, model evaluation, and business decision-making.

## Validate the Verdict Logic

```bash
python backend/scripts/validate_verdict_space.py
```

Expected output:

```text
Checked 194481 metric combinations.
No gaps or unexpected labels found.
```

## Quick Start

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs

## Run Tests

```bash
cd backend
python -m pytest tests
```

## Regenerate ML Artifacts

Generated model artifacts are intentionally excluded from Git to keep the repository lightweight.

```bash
cd backend
python scripts/generate_training_data.py
python scripts/train_verdict_classifier.py
```

## Project Docs

- [PROJECT_REPORT.md](PROJECT_REPORT.md): problem framing, data model, simulation logic, business interpretation
- [DEPLOYMENT.md](DEPLOYMENT.md): frontend/backend deployment steps
- [docs/sql_analytics_queries.sql](docs/sql_analytics_queries.sql): SQL analytics query pack
- [docs/model_evaluation.md](docs/model_evaluation.md): ML evaluation and honest model framing

## Resume Bullets

```latex
\resumeProjectHeading
    {\textbf{\href{https://github.com/nayana3333/Reachlytics}{Reachlytics}} $|$ \emph{FastAPI, Next.js, PostgreSQL, Redis, Celery, NetworkX, SQL, ML, LLM APIs}}{2026}
    \resumeItemListStart
      \resumeItem{Built an AI content analytics platform to support \textbf{data-driven content strategy decisions}, simulating product video spread across \textbf{200+ synthetic personas} using \textbf{NetworkX} graph propagation and PostgreSQL-backed analytics}
      \resumeItem{Designed \textbf{SQL}-based analytics workflows for audience comparison, engagement funnels, verdict distribution, and AI-source auditing; validated rule-based verdict logic across \textbf{194,481 metric combinations}}
      \resumeItem{Trained a \textbf{Random Forest} verdict classifier with \textbf{78\% accuracy} and explainability support, while integrating LLM-based persona generation, content analysis, and deterministic fallback for reliable demos}
    \resumeItemListEnd
```

## Future Improvements

- WebSocket progress updates
- PDF report export
- A/B comparison between two videos
- Shared object storage for production video uploads
- Production Redis/Celery queue with shared upload storage
- CI/CD pipeline for backend and frontend checks
