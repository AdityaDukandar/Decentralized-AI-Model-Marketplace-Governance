# AI Model Marketplace (MVP)

This repository contains a prototype of a **Decentralized AI Model Marketplace + Governance** designed to demonstrate SOLID principles and a realistic, extensible architecture.

## What is included
- Backend: FastAPI application (backend/app/main.py) implementing register, evaluate, and purchase endpoints.
- Core modules: abstractions and implementations for evaluators, storage, governance, pricing.
- Plugin loader: place Python files into `backend/plugins/` to add new evaluator classes.
- Sandbox: `SandboxRunner` executes evaluators in a separate process with timeout and size limits. `DockerRunner` constructs Docker commands for isolated evaluation (requires Docker to run).
- Frontend: `frontend/index.html` — a minimal demo UI to interact with the API.
- Dockerfile and docker-compose for running the API in a container.
- Tests: simple pytest tests (backend/tests).

## Quick start (local)
1. Create a virtualenv and install requirements:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r backend/requirements.txt
   ```
2. Run the API:
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```
3. Open `frontend/index.html` in a browser (update API URL if needed) or use the API directly via curl/Postman.

## Plugins
Drop `.py` files into `backend/plugins/`. Each plugin can define an evaluator class inheriting from `core.interfaces.EvaluationStrategy` and should set a `KEY` attribute to be discoverable.

## Docker (optional)
Build & run the API container:
```bash
docker build -t ai_marketplace_demo .
docker run --rm -p 8000:8000 ai_marketplace_demo
```

## Notes on security
The sandbox uses process isolation and timeouts for prototype safety. For production, run evaluations inside containers with strict resource limits, use seccomp profiles or gVisor, and validate all uploaded content.

## Next steps / Extensions
- Add persistent database (Postgres) and authentication (JWT).
- Harden sandbox: run Docker containers for each evaluation with read-only mounts.
- Add reputation leaderboards & billing integration.
- Add CI and more comprehensive tests.
