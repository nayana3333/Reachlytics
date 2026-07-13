# Reachlytics Deployment Guide

Reachlytics has five deployable parts:

- Next.js frontend
- FastAPI backend
- PostgreSQL database
- Redis broker
- Celery worker

The cleanest beginner-friendly production setup is:

- Frontend: Vercel
- Backend: Render web service
- Database: Render PostgreSQL or any managed PostgreSQL provider
- Queue: inline mode for the first public demo

Why inline mode first? The current app stores uploaded videos on the backend filesystem. On many cloud hosts, a separate worker service does not automatically share those uploaded files with the web service. Inline mode keeps the upload and simulation in one service, which is more reliable for a first live demo. Redis/Celery can be re-enabled later after moving uploads to shared object storage.

## Required Environment Variables

Backend:

```text
APP_NAME=Reachlytics API
ENVIRONMENT=production
DATABASE_URL=<managed-postgres-url>
REDIS_URL=
JWT_SECRET_KEY=<strong-random-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
UPLOAD_DIR=uploads
MAX_UPLOAD_MB=100
ALLOWED_VIDEO_EXTENSIONS=.mp4,.mov,.webm,.mkv
FRONTEND_ORIGINS=https://your-frontend-domain.vercel.app
AI_PROVIDER=mock
OPENROUTER_API_KEY=
OPENROUTER_MODEL=openrouter/free
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash-lite
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

Frontend:

```text
NEXT_PUBLIC_API_URL=https://your-backend-domain.onrender.com
```

If deploying the frontend with Docker, pass the same value as a build argument because `NEXT_PUBLIC_*` variables are included during the Next.js build:

```bash
docker build --build-arg NEXT_PUBLIC_API_URL=https://your-backend-domain.onrender.com -t reachlytics-frontend ./frontend
```

Use `AI_PROVIDER=mock` for a stable free demo. Switch to `openrouter`, `gemini`, or `anthropic` only after adding the matching API key.

## Backend Deployment With Render Blueprint

This repo includes `render.yaml`, so Render can create the backend and PostgreSQL database from the repository.

Steps:

1. Open Render Dashboard.
2. Choose `New`.
3. Choose `Blueprint`.
4. Select `nayana3333/Reachlytics`.
5. Confirm the generated services.
6. Deploy.
7. Copy the backend URL after deployment.

After Vercel creates the frontend URL, update the Render backend environment variable:

```text
FRONTEND_ORIGINS=https://your-frontend-domain.vercel.app
```

Then redeploy the backend.

## Backend Deployment Manually

Create a Docker-based web service from the GitHub repo:

- Root directory: `backend`
- Dockerfile path: `backend/Dockerfile`
- Health check path: `/health`

The backend Dockerfile already runs:

```bash
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Worker Deployment

For the first hosted demo, skip the worker and Redis so the app runs in inline mode. Add a worker later only after uploads are stored in shared object storage such as S3, Cloudinary, or Render disk storage that both services can access.

When shared storage is available, create a background worker from the same backend image:

- Root directory: `backend`
- Dockerfile path: `backend/Dockerfile`
- Start command:

```bash
celery -A app.workers.celery_app.celery_app worker --loglevel=info
```

Use the same backend environment variables, especially `DATABASE_URL` and `REDIS_URL`.

## Frontend Deployment

Create a Vercel project from the GitHub repo:

- Root directory: `frontend`
- Install command: `npm install`
- Build command: `npm run build`
- Output: Next.js default
- Environment variable: `NEXT_PUBLIC_API_URL=<backend-url>`

Do not set Vercel root directory to `backend`. If the logs mention
`/vercel/path0/backend/package.json` or `/vercel/path0/backend/frontend/package.json`,
the Vercel project is pointed at the wrong folder. Set root directory to `frontend`
and use the normal install/build commands above.

After the frontend URL is created, add it to backend `FRONTEND_ORIGINS`.

## Production Notes

- Do not commit `.env` files or API keys.
- Keep generated model artifacts out of Git; regenerate them locally if needed.
- This first deployment intentionally runs simulations inline for reliability with uploaded video files.
- Production Redis + Celery should be paired with shared video storage.
- For demos, use small persona counts first to avoid long AI/provider calls.
- For uploaded videos, persistent file storage is recommended if the host has ephemeral disks.

## Smoke Test

After deployment:

1. Open backend `/health`.
2. Confirm `status` is `ok`.
3. Open the frontend URL.
4. Register a test account.
5. Upload a small video.
6. Run a simulation with 50-100 personas.
7. Confirm the report, graph, AI-source badge, and agent panel load.
