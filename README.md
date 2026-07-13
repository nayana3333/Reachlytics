# Reachlytics

**AI content analytics platform for simulating product-video virality across synthetic social audiences.**

Reachlytics is a full-stack AI + simulation project built to evaluate how a product demo video may spread across a target audience. It combines video upload, transcript/content analysis, synthetic persona generation, graph-based propagation, SQL-backed analytics, ML verdict prediction, and an explainable report UI.

The project is designed as a placement-ready engineering portfolio project, with attention to backend architecture, database design, background processing, model evaluation, fallback reliability, and decision-science style reporting.

## Repository

- GitHub: https://github.com/nayana3333/Reachlytics
- Project report: [PROJECT_REPORT.md](PROJECT_REPORT.md)
- Deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- SQL analytics pack: [docs/sql_analytics_queries.sql](docs/sql_analytics_queries.sql)
- Model evaluation notes: [docs/model_evaluation.md](docs/model_evaluation.md)

## Problem Statement

Teams often publish product demo videos without a structured way to estimate audience fit, engagement quality, or likely spread. Reachlytics frames this as a measurable decision problem:

> Given a product demo video and a target audience, can we simulate reach, engagement, and spread quality before investing in distribution?

Reachlytics helps answer:

- Which audience segment is most promising?
- Is weak performance caused by hook quality, clarity, shareability, or poor audience fit?
- Does the content stay inside the target audience or break out to unrelated viewers?
- Which persona types engage, skip, or share, and why?

## Core Workflow

1. User registers or logs in.
2. User uploads a product demo video.
3. Backend extracts metadata and transcript/description.
4. AI/content analysis scores the video on hook, clarity, emotional appeal, shareability, and audience fit.
5. System generates synthetic personas for the chosen target audience.
6. A graph propagation engine simulates watch, like, comment, share, and skip behavior across multiple rounds.
7. UI displays metrics, graph spread, agent-level reasoning, AI-source transparency, and final verdict.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | Next.js, React, TypeScript, Tailwind CSS, React Flow |
| Backend | FastAPI, Python, SQLAlchemy |
| Database | PostgreSQL, Alembic migrations |
| Queue | Redis + Celery, with inline fallback mode |
| Simulation | NetworkX-style graph propagation |
| AI Providers | OpenRouter, Gemini, Anthropic/OpenAI, offline mock mode |
| ML | Random Forest classifier, SHAP/feature-importance explainability |
| DevOps | Docker, Docker Compose, Render blueprint, Vercel config |

## Architecture

```text
                    +----------------------+
                    |      Next.js UI      |
                    | Dashboard / Upload   |
                    | Graph / Report       |
                    +----------+-----------+
                               |
                               | REST API
                               v
                    +----------------------+
                    |    FastAPI Backend   |
                    | Auth / Videos / Sims |
                    +----------+-----------+
                               |
              +----------------+----------------+
              |                                 |
              v                                 v
      +---------------+                 +---------------+
      |  PostgreSQL   |                 | Redis + Celery |
      | Persistence   |                 | Async Jobs     |
      +---------------+                 +---------------+
              |
              v
  Transcript -> Content Analysis -> Personas -> Graph Simulation -> Report
```

## Key Features

- JWT-based authentication
- Video upload with validation and metadata persistence
- Transcript generation with real-provider and deterministic fallback paths
- Multimodal-ready content analysis with visual description support
- 50-500 synthetic persona generation
- Persona-level behavior traits: engagement tendency, share probability, skepticism
- Multi-round graph propagation simulation
- Watch, like, comment, share, and skip decision modeling
- Agent-level reasoning panel
- React Flow spread visualization with round replay
- Analytics dashboard and final report
- AI-source transparency badge for real AI vs fallback estimates
- PostgreSQL schema with Alembic migrations
- Swagger API documentation
- Dockerized backend/frontend setup
- Render/Vercel deployment configuration

## Decision Science and Analytics Layer

Reachlytics is not just an AI wrapper. It decomposes content performance into measurable variables:

- Content quality: hook, clarity, emotional appeal, shareability, audience fit
- Audience behavior: watch, like, comment, share, skip
- Network behavior: reach, cascade depth, fanout, out-of-target spread
- Decision output: verdict, improvement suggestions, persona explanations

The SQL analytics pack includes queries for:

- Run-level report summaries
- Verdict distribution
- Audience comparison
- Round-by-round propagation funnels
- Persona behavior by target fit
- AI-source audit
- Content-quality vs outcome diagnostics

See: [docs/sql_analytics_queries.sql](docs/sql_analytics_queries.sql)

## Simulation Engine

Reachlytics uses a small-world graph structure to approximate clustered social networks. Each persona receives profile attributes and behavioral scores. During simulation, reached personas decide whether to watch, like, comment, or share based on:

- Content analysis scores
- Target-audience fit
- Persona interests and pain points
- Engagement tendency
- Share probability
- Skepticism level
- Previous propagation round

Shares create stronger fanout, while likes and comments create smaller algorithmic pushes. The simulation stops when the round limit is reached or no new agents are exposed.

## Verdict Logic

The final verdict is generated from explicit metric thresholds, not a hidden prompt. Supported labels:

- `Viral candidate`
- `Niche hit`
- `Solid in-target performance`
- `Strong in-demo, no breakout`
- `Mixed performance`
- `Low signal`
- `Out-of-target breakout`

The verdict logic is validated across **194,481 metric combinations** to ensure there are no gaps, silent fallthroughs, or unexpected labels.

Run validation:

```bash
python backend/scripts/validate_verdict_space.py
```

Expected result:

```text
Checked 194481 metric combinations.
No gaps or unexpected labels found.
```

## ML Verdict Classifier

Reachlytics includes an offline-trained Random Forest verdict classifier.

There are two model variants:

- `verdict_classifier.joblib`: pre-simulation classifier that predicts likely verdict from content scores and simulation inputs.
- `verdict_classifier_post_sim.joblib`: post-simulation explainer/sanity-check model that recovers the deterministic verdict from final metrics.

Current documented balanced run:

- 600 simulator-generated rows
- At least 40 examples per verdict class
- Random Forest classifier
- 78.33% pre-simulation accuracy
- SHAP/feature-importance explainability support

Important note: the post-simulation model is intentionally documented as an explainer, not a real predictive achievement, because it learns labels generated from the same final metrics.

Regenerate training data and models:

```bash
cd backend
python scripts/generate_training_data.py
python scripts/train_verdict_classifier.py
```

Generated model artifacts are excluded from Git to keep the repository lightweight.

## AI Provider Strategy

Reachlytics supports multiple AI modes:

| Provider | Use Case |
| --- | --- |
| `mock` | Fully offline deterministic demo |
| `openrouter` | Free-tier-friendly real AI demos |
| `gemini` | Google AI Studio text/vision/audio path |
| `anthropic` | Anthropic reasoning/vision + OpenAI Whisper transcription |

The report UI clearly shows whether each stage used real AI or fallback logic. This avoids pretending that fallback estimates are live AI results.

## Database Design

Core tables:

- `users`
- `videos`
- `transcripts`
- `content_analyses`
- `simulations`
- `personas`
- `agent_decisions`
- `graph_edges`
- `simulation_rounds`
- `reports`

The schema supports full traceability from uploaded video to final verdict, including every persona decision and propagation edge.

## API Surface

Main routes:

```text
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me

POST /api/videos/upload
GET  /api/videos
GET  /api/videos/{video_id}

POST /api/simulations
GET  /api/simulations
GET  /api/simulations/{id}
GET  /api/simulations/{id}/status
GET  /api/simulations/{id}/metrics
GET  /api/simulations/{id}/graph
GET  /api/simulations/{id}/rounds
GET  /api/simulations/{id}/personas
GET  /api/simulations/{id}/report

GET  /health
```

Swagger docs are available at:

```text
http://localhost:8000/docs
```

## Local Development

### Docker Compose

```bash
docker compose up --build
```

Services:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs

### Backend Only

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

Copying `.env.example` to `.env` makes local `uvicorn` use the same PostgreSQL and Redis URLs as Docker Compose. Without `.env`, the backend falls back to local SQLite for quick experiments.

### Frontend Only

```bash
cd frontend
npm install
npm run dev
```

If `npm run dev` fails on Windows with `spawn EPERM`, use:

```bash
npm run build
npm run start
```

This can happen when the project is inside a OneDrive-synced folder.

## Environment Variables

Backend values live in `backend/.env.example`.

Important variables:

```text
DATABASE_URL
REDIS_URL
JWT_SECRET_KEY
FRONTEND_ORIGINS
AI_PROVIDER
OPENROUTER_API_KEY
GEMINI_API_KEY
OPENAI_API_KEY
ANTHROPIC_API_KEY
```

Frontend:

```text
NEXT_PUBLIC_API_URL
```

Never commit `.env` files or API keys.

## Deployment

Deployment config is included:

- `render.yaml` for Render backend + PostgreSQL
- `vercel.json` for Vercel frontend
- `DEPLOYMENT.md` for step-by-step instructions

Recommended first deployment:

- Backend: Render web service
- Database: Render PostgreSQL
- Frontend: Vercel
- Queue: inline mode for reliable uploaded-video processing

Redis/Celery can be enabled later with shared object storage for uploaded videos.

## Testing and Validation

Run verdict-space validation:

```bash
python backend/scripts/validate_verdict_space.py
```

Run backend tests:

```bash
cd backend
python -m pytest tests
```

Run frontend build:

```bash
cd frontend
npm install
npm run build
```

## Suggested Demo Flow

1. Register a test account.
2. Upload a short product demo video.
3. Enter a target audience.
4. Run simulation with 50-100 personas for a quick demo.
5. Show metrics, graph spread, round replay, and agent detail panel.
6. Open the final report and explain the AI-source badge.
7. Discuss SQL analytics and ML evaluation using the docs folder.

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

## Interview Talking Points

- Why graph simulation is useful for modeling content spread
- How persona-level behavior scoring works
- Why fallback logic is necessary for reliable demos
- How SQL queries convert simulation traces into business insights
- Why the post-simulation ML model is an explainer, not a predictive claim
- How schema guards and migrations prevent stale-database failures
- How the system can be scaled with shared storage, Redis, Celery, and managed deployment

## Future Improvements

- WebSocket progress updates
- PDF report export
- A/B comparison between two videos
- Shared object storage for production video uploads
- Redis/Celery production queue with shared upload storage
- CI/CD pipeline with automated backend and frontend checks
