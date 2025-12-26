# **Decentralized AI Model Marketplace + Governance**

> **A SOLID-principles-driven AI Model Marketplace** enabling secure model registration, sandboxed evaluation, governance-as-code, pricing strategies, and plugin-based extensibility.

This repository demonstrates how **clean object-oriented design and SOLID principles** can be applied to build a realistic, extensible, and secure software system.
The focus is on **software architecture**, not model training.

---

##  Key Highlights (Why this project stands out)

*  SOLID-compliant architecture (SRP, OCP, LSP, ISP, DIP)
*  Plugin-based evaluator system (no core code changes needed)
*  Sandboxed evaluation (process isolation + timeouts)
*  Governance-as-code (access control & visibility rules)
*  Pricing strategies decoupled from business logic
*  FastAPI-based REST API
*  CLI + minimal frontend UI
*  Docker-ready for consistent deployment

---

##  Architecture Overview

The system is built around **abstractions**, ensuring loose coupling and high extensibility:

```
Client (CLI / Web UI)
        |
      FastAPI
        |
------------------------------------
| Marketplace | Governance | Pricing |
------------------------------------
        |
   Evaluation Engine
        |
   Sandbox Runner
```

**Design principle:**

> High-level modules depend on interfaces, not concrete implementations.

---

## 📦 What’s Included

### Backend

* **FastAPI application** (`backend/app/main.py`)

  * `/register` – Register AI models
  * `/evaluate` – Evaluate models using pluggable strategies
  * `/purchase` – Simulated marketplace purchase
* **Core modules**

  * Evaluation strategies
  * Governance policies
  * Pricing strategies
  * Storage abstraction
* **Sandbox**

  * `SandboxRunner` for process-level isolation
  * `DockerRunner` helper for container-based evaluation (optional)
* **Plugin loader**

  * Add new evaluators via `backend/plugins/` without modifying core code
* **Tests**

  * Pytest-based API tests (`backend/tests/`)

### Frontend

* `frontend/index.html`

  * Minimal UI to register and evaluate models via the API

### DevOps

* Dockerfile
* docker-compose
* `.gitignore`
* MIT License

---

##  Quick Start (Local)

> **Recommended:** Python 3.10 or 3.11

### 1️. Setup virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
```

### 2️. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 3️. Run the API

```bash
uvicorn backend.app.main:app --port 8000
```

### 4️. Open

* API Docs → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Frontend → open `frontend/index.html` in browser

---

## 🔌 Plugin System (Open–Closed Principle in action)

Add new evaluation logic without touching existing code.

### Steps:

1. Create a new `.py` file in:

   ```
   backend/plugins/
   ```
2. Implement `EvaluationStrategy`
3. Define a unique `KEY`

```python
class CustomEvaluator(EvaluationStrategy):
    KEY = "custom_eval"
```

The evaluator is auto-discovered at runtime.

---

## 🛡️ Security & Sandbox Model

* Evaluations run in **separate OS processes**
* Execution timeouts prevent infinite loops
* Output size limits prevent memory abuse
* Optional Docker-based isolation for production

> ⚠️ This is a prototype sandbox.
> Production systems should enforce container-level resource limits and syscall restrictions.

---

## 🧪 Testing

* API-level tests using **pytest**
* FastAPI `TestClient` for endpoint validation
* Modular design enables easy mocking and unit testing

---

## 🐳 Docker (Optional)

Run the API inside a container:

```bash
docker build -t ai_marketplace_demo .
docker run --rm -p 8000:8000 ai_marketplace_demo
```

This avoids local Python version issues and ensures reproducibility.

---

## 📈 Future Enhancements

* JWT-based authentication & user management
* Persistent database (PostgreSQL)
* Reputation leaderboards
* Blockchain-backed audit logs
* Kubernetes deployment
* CI/CD with GitHub Actions

---

## 👤 Author

**Aditya Dukandar**
*Object-Oriented Design • SOLID Principles • Backend Architecture*

---
