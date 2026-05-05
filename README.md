# Azure Container Workshop

This repository is a beginner-friendly Azure container workshop covering
**Azure Kubernetes Service (AKS)** and **Azure Container Apps**. It is built
around official Microsoft Learn guidance and real-world patterns.

The examples use a lightweight healthcare **Patient Triage Assistant** scenario
so the workshop stays consistent across all deployment, scaling, networking,
observability, and job labs.

Workshop site: [beyondelastic.github.io/azure-container-workshop](https://beyondelastic.github.io/azure-container-workshop/)

## What this workshop covers

| # | Lesson | Section |
|---|--------|---------|
| 00 | Prerequisites | — |
| 01 | Your First AKS Deployment | AKS |
| 02 | Services & Networking | AKS |
| 03 | Scaling & Configuration | AKS |
| 04 | Monitoring & Observability | AKS |
| 05 | AKS Automatic | AKS |
| 06 | Your First Container App | Container Apps |
| 07 | Scaling & Revisions | Container Apps |
| 08 | Multi-Container & Dapr | Container Apps |
| 09 | Jobs & Background Processing | Container Apps |

## Design goals

- Keep the flow easy to follow.
- Favour official documentation over custom theory.
- Keep examples short and runnable.
- Use a lightweight docs-first web UI.

## Official sources used

- [AKS documentation](https://learn.microsoft.com/azure/aks/)
- [Azure Container Apps documentation](https://learn.microsoft.com/azure/container-apps/)
- [AKS Automatic overview](https://learn.microsoft.com/azure/aks/aks-automatic-overview)
- [Dapr on Container Apps](https://learn.microsoft.com/azure/container-apps/dapr-overview)
- [Container Apps Jobs](https://learn.microsoft.com/azure/container-apps/jobs)

## Repository layout

```
.
├── docs/           ← lesson pages (served by MkDocs)
├── app/
│   ├── backend/    ← Python FastAPI service
│   ├── frontend/   ← React (Vite) UI
│   └── worker/     ← Python batch worker
├── manifests/
│   ├── aks/        ← Kubernetes YAML manifests
│   └── container-apps/ ← Bicep templates
├── mkdocs.yml
├── requirements.txt
└── SETUP.md
```

## Quick start

1. Create a Python virtual environment.
2. Install dependencies.
3. Sign in to Azure.
4. Copy `.env.example` to `.env` and fill in your values.
5. Start the docs UI with `mkdocs serve`.

Detailed steps are in `SETUP.md`.

## Run the workshop UI

```bash
mkdocs serve
```

Then open the local URL shown in the terminal, usually `http://127.0.0.1:8000`.

## Run the demo app locally

```bash
# Backend
cd app/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8001

# Frontend (separate terminal)
cd app/frontend
npm install
npm run dev
```

## Build container images

```bash
docker build -t triage-backend ./app/backend
docker build -t triage-frontend ./app/frontend
docker build -t triage-worker ./app/worker
```
