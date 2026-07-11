# Reachlytics

Reachlytics is a full-stack AI and simulation project for predicting how product demo videos may spread across synthetic social audiences.

The project is designed as a serious placement/resume system: it combines authentication, video upload, AI-backed transcript and content analysis, LLM-generated persona generation, graph propagation, PostgreSQL persistence, Redis/Celery background jobs, and a clean analytics UI.

## Core Idea

Users upload a product demo, define a target audience, and run a multi-agent simulation. Reachlytics creates synthetic personas, models watch/like/comment/share behavior, propagates the video through a social graph, and produces a verdict such as `Niche hit`, `Viral candidate`, or `Low signal`.

## Tech Stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS, React Flow
- Backend: FastAPI, Python, SQLAlchemy
- Database: PostgreSQL
- Queue: Redis + Celery
- Simulation: NetworkX-style small-world propagation engine
- AI layer: OpenRouter, Gemini, Anthropic/OpenAI, and offline mock provider modes
- ML: Random Forest verdict classifier with SHAP/feature-importance explainability
- DevOps: Docker Compose

## Architecture

```text
Next.js UI
  |
  | REST API
  v
FastAPI backend
  |
  | SQLAlchemy
  v
PostgreSQL

Redis <-> Celery worker
  |
  v
Transcript -> Content analysis -> Persona generation -> Graph simulation -> Report
```

## Features

- JWT authentication
- Video upload and metadata persistence
- Video extension, content-type, size validation, and optional duration extraction via `ffprobe`
- Transcript generation with provider-assisted video descriptions, Gemini video/audio input, OpenAI Whisper, or deterministic fallback
- Text and multimodal content quality analysis
- 50-500 persona generation
- Graph-based multi-round propagation
- Agent decisions with provider-aware LLM reasons or deterministic fallback reasons
- Metrics: virality score, reach, like rate, comment rate, share rate, cascade depth
- Graph visualization
- Explainable final report
- Swagger API docs at `/docs`
- Alembic database migrations
- Unit tests for scoring and propagation
- Dockerized services
- SQL analytics query pack for decision-science style reporting
- Verdict-space validation across 194,481 metric combinations

## Decision Science Angle

Reachlytics is not only an AI wrapper. It models a business question: "Which audience is most likely to spread this product demo, and why?" The system decomposes that question into measurable parts:

- Content quality: hook, clarity, emotional appeal, shareability, and audience fit
- Audience behavior: watch, like, comment, share, and skip decisions per persona
- Network effects: reach, cascade depth, in-target spread, and out-of-target breakout
- Recommendations: verdict labels, improvement suggestions, and persona-level reasoning

For analytics review, the repo includes:

- `docs/sql_analytics_queries.sql`: PostgreSQL queries for run summaries, verdict distribution, audience comparison, propagation funnels, persona behavior, and AI-source audit
- `docs/model_evaluation.md`: notes explaining the verdict validation, pre-simulation model, post-simulation explainer, and honest resume framing
- `backend/scripts/validate_verdict_space.py`: reproducible validation script for the seven-label verdict logic

## Local Setup

```bash
docker compose up --build
```

Services:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

For local backend-only development:

```bash
docker compose up postgres redis
cd backend
copy .env.example .env
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Copying `.env.example` to `.env` makes local `uvicorn` use the same PostgreSQL and Redis URLs as Docker Compose. If you skip `.env`, the backend falls back to local SQLite for quick experiments, and that data will not appear in the Docker/Postgres environment.

When SQLAlchemy models change, create and apply a migration from `backend/`:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Migration note: after pulling any update that adds a file under `backend/migrations/versions/`, run `alembic upgrade head` before starting the backend. The API performs a startup schema check and will fail loudly if required tables or columns are missing, instead of silently running against a stale database.

After pulling updates, always check for new migration files before restarting backend or worker processes:

```bash
cd backend
alembic upgrade head
```

If the database is not at the latest Alembic revision, the API refuses to start with a clear migration error. This prevents simulations from partially completing against a stale schema and producing missing reports, personas, rounds, or graph edges.

For local frontend-only development:

```bash
cd frontend
npm install
npm run dev
```

## Known Issues / Windows Notes

On some Windows setups, especially when this project is inside a OneDrive-synced folder, `npm run dev` can fail with a Next.js `spawn EPERM` error. This appears to be a local file-watching/process-spawn permission issue rather than an application runtime bug.

Working demo workaround:

```bash
cd frontend
npm run build
npm run start
```

If possible, run the project from a non-OneDrive folder or exclude the project directory from OneDrive sync before a live demo.

## Environment Variables

Backend values live in `backend/.env.example`.

Important values:

- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET_KEY`
- `AI_PROVIDER`
- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`
- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

AI provider modes:

- `AI_PROVIDER=openrouter`: recommended for local demos and testing. OpenRouter is a free-tier-eligible API gateway that routes to multiple underlying models including free options, so no payment method is required to test real AI behavior. Get a free key at https://openrouter.ai/. Set `OPENROUTER_API_KEY` and optionally `OPENROUTER_MODEL`.
- `AI_PROVIDER=gemini`: Google AI Studio path. Set `GEMINI_API_KEY`. `GEMINI_MODEL` defaults to `gemini-2.5-flash-lite`, which is configurable because Google model availability changes over time.
- `AI_PROVIDER=anthropic`: original paid provider path. Set `ANTHROPIC_API_KEY` for content/personas/reasoning and `OPENAI_API_KEY` for Whisper transcription.
- `AI_PROVIDER=mock`: fully offline deterministic fallback. No API keys are required, and the UI marks reports as fallback estimates.

The report badge shows which stages used real AI and which used fallback logic, including whether content analysis used visual inspection.

## API Routes

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/videos/upload`
- `GET /api/videos`
- `POST /api/simulations`
- `GET /api/simulations`
- `GET /api/simulations/{id}`
- `GET /api/simulations/{id}/status`
- `GET /api/simulations/{id}/metrics`
- `GET /api/simulations/{id}/graph`
- `GET /api/simulations/{id}/rounds`
- `GET /api/simulations/{id}/personas`
- `GET /api/simulations/{id}/report`

## Simulation Engine

Reachlytics uses a small-world social graph to approximate clustered social networks. Personas receive interests, pain points, content preferences, engagement tendency, skepticism, and share probability. Each reached agent receives watch, like, comment, and share decisions based on content quality, audience fit, interest match, and behavioral traits.

Shares create stronger fanout. Likes and comments create smaller algorithmic pushes. The simulation stops when the round limit is reached or no new agents are exposed.

## ML Verdict Classifier

Reachlytics includes an offline-trained Random Forest classifier for verdict prediction. Training data is generated by running the existing propagation simulator and saving both pre-simulation inputs and post-simulation metrics to `backend/data/training_runs.csv`.

There are two model variants:

- `backend/models/verdict_classifier.joblib`: the legitimate pre-simulation model. It predicts the expected verdict from content scores, population size, and in-target percentage before propagation runs.
- `backend/models/verdict_classifier_post_sim.joblib`: a post-simulation explainer/sanity-check model. Its labels are generated by the deterministic `verdict()` function from the same final metrics used as features, so high accuracy here is expected and circular. Do not present this as a meaningful predictive achievement; it only shows that a simple model can recover the rule-based labeling boundaries.

Current balanced training run: 600 simulator-generated rows with at least 40 examples per verdict class. The pre-simulation model reached 78.33% accuracy; rare-class recall improved after balancing, especially `Out-of-target breakout` from 0.00 to 0.60.

## Regenerating ML Models

Generated model artifacts are intentionally excluded from Git to keep the repository lightweight. To recreate them locally:

```bash
cd backend
python scripts/generate_training_data.py
python scripts/train_verdict_classifier.py
```

This regenerates `backend/data/training_runs.csv`, `backend/models/verdict_classifier.joblib`, `backend/models/verdict_classifier_post_sim.joblib`, and the SHAP/feature-importance plot.

## Resume Bullets

**Reachlytics | FastAPI, Next.js, PostgreSQL, Redis, Celery, NetworkX, SQL, ML, LLM APIs** - 2026

- Built an AI content analytics platform for data-driven content strategy decisions, simulating video spread across 200+ synthetic personas using NetworkX graph propagation and PostgreSQL-backed analytics
- Designed a SQL-backed analytics schema and validated rule-based verdict logic across 194,481 input combinations; trained a Random Forest verdict classifier achieving 78% accuracy with SHAP-based explainability
- Integrated LLM APIs for persona generation, content analysis, and transcript-aware reasoning with deterministic fallback for reliable offline demos

## Future Improvements

- WebSocket progress updates
- PDF report export
- A/B testing between two videos
- CI/CD deployment
