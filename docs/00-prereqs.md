# 00 Prerequisites

## Goal

Set up your local environment and Azure resources so every subsequent lesson
runs without blockers.

## Estimated time

20 minutes.

## Official references

- [Install Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [Install Docker Desktop](https://docs.docker.com/get-docker/)
- [Install kubectl](https://learn.microsoft.com/azure/aks/tutorial-kubernetes-deploy-cluster?tabs=azure-cli#install-the-kubernetes-cli)
- [Create a Microsoft Foundry project](https://learn.microsoft.com/azure/ai-foundry/how-to/create-projects)

## Required tools

| Tool | Minimum version | Install |
|------|----------------|---------|
| Azure CLI | 2.60+ | `curl -sL https://aka.ms/InstallAzureCLIDeb \| sudo bash` |
| Docker Desktop | 24+ | [docs.docker.com/get-docker](https://docs.docker.com/get-docker/) |
| kubectl | 1.28+ | `az aks install-cli` |
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| Bicep CLI | 0.25+ | `az bicep install` |

## Exercise

### Step 1 — Sign in to Azure

```bash
az login
az account set --subscription "<your-subscription-id>"
```

### Step 2 — Register required providers

```bash
az provider register --namespace Microsoft.ContainerService
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
```

### Step 3 — Create a resource group

```bash
export RESOURCE_GROUP=rg-container-workshop
export LOCATION=eastus2

az group create --name $RESOURCE_GROUP --location $LOCATION
```

### Step 4 — Create an Azure Container Registry

```bash
export ACR_NAME=acrtriage$RANDOM

az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic
```

### Step 5 — Microsoft Foundry resource and project

Create a Foundry resource with project management enabled, a project, and a
model deployment. You can do this via the
[Microsoft Foundry portal](https://ai.azure.com) or the CLI:

```bash
# Create the Foundry resource with project management
az cognitiveservices account create \
  --name ai-triage \
  --resource-group $RESOURCE_GROUP \
  --kind AIServices \
  --sku S0 \
  --location $LOCATION \
  --allow-project-management

# Assign a stable custom subdomain
az cognitiveservices account update \
  --name ai-triage \
  --resource-group $RESOURCE_GROUP \
  --custom-domain ai-triage

# Create a Foundry project inside the resource
az cognitiveservices account project create \
  --name ai-triage \
  --resource-group $RESOURCE_GROUP \
  --project-name triage-project \
  --location $LOCATION

# Deploy a model
az cognitiveservices account deployment create \
  --name ai-triage \
  --resource-group $RESOURCE_GROUP \
  --deployment-name gpt-4.1-mini \
  --model-name gpt-4.1-mini \
  --model-version "2025-04-14" \
  --model-format OpenAI \
  --sku-name Standard \
  --sku-capacity 30
```

!!! tip
    If `az cognitiveservices account create` reports
    `unrecognized arguments: --allow-project-management`, run `az upgrade` and
    retry.

Copy the **project endpoint** from the Foundry portal (Home → open your
project → the endpoint shown for SDK/API usage):

```
# Format: https://<your-ai-service>.services.ai.azure.com/api/projects/<your-project-name>
```

!!! note
    The app uses `DefaultAzureCredential` for authentication. Make sure you are
    signed in with `az login` and have the **Cognitive Services OpenAI User**
    role on the Foundry resource.

### Step 6 — Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```
AZURE_AI_PROJECT_ENDPOINT=https://<your-ai-service>.services.ai.azure.com/api/projects/<your-project-name>
AZURE_AI_MODEL_DEPLOYMENT=gpt-4.1-mini
ACR_NAME=<your-acr-name>
RESOURCE_GROUP=rg-container-workshop
LOCATION=eastus2
```

### Step 7 — Build and push container images

```bash
az acr login --name $ACR_NAME

docker build -t $ACR_NAME.azurecr.io/triage-backend:v1 ./app/backend
docker build -t $ACR_NAME.azurecr.io/triage-frontend:v1 ./app/frontend
docker build -t $ACR_NAME.azurecr.io/triage-worker:v1 ./app/worker

docker push $ACR_NAME.azurecr.io/triage-backend:v1
docker push $ACR_NAME.azurecr.io/triage-frontend:v1
docker push $ACR_NAME.azurecr.io/triage-worker:v1
```

### Step 8 — Test locally (optional)

```bash
# Backend
cd app/backend
pip install -r requirements.txt
source ../../.env
uvicorn main:app --reload --port 8001

# Frontend (new terminal)
cd app/frontend
npm install
npm run dev
```

Open `http://localhost:3000` to see the Patient Triage UI.

## Verification

- [ ] `az account show` prints your subscription name.
- [ ] `docker --version` shows 24+.
- [ ] `kubectl version --client` shows 1.28+.
- [ ] `python --version` shows 3.11+.
- [ ] `node --version` shows 18+.
- [ ] Resource group `rg-container-workshop` exists in Azure.
- [ ] ACR exists and `az acr login` succeeds.
- [ ] Foundry project endpoint is set in `.env`.
- [ ] All three images are pushed to ACR.
