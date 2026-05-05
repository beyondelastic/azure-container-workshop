# Setup

Complete these steps before starting the workshop.

## 1. Prerequisites

| Tool | Minimum version | Install link |
|------|----------------|--------------|
| Azure CLI | 2.60+ | [Install Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) |
| Docker Desktop | 24+ | [Install Docker](https://docs.docker.com/get-docker/) |
| kubectl | 1.28+ | `az aks install-cli` |
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| Bicep CLI | 0.25+ | `az bicep install` |

## 2. Azure subscription

You need an Azure subscription with permission to create resource groups,
AKS clusters, Container Apps environments, and an Azure Container Registry.

A free trial subscription works for most exercises.

## 3. Microsoft Foundry project

Create a Microsoft Foundry project with a GPT model deployed (e.g. `gpt-4.1-mini`). Note the:
- Project endpoint (e.g. `https://<your-project>.services.ai.azure.com/api/projects/<name>`)
- Model deployment name

Authentication uses `DefaultAzureCredential` (via `az login` or managed identity).

## 4. Clone the repository

```bash
git clone https://github.com/beyondelastic/azure-container-workshop.git
cd azure-container-workshop
```

## 5. Python environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

## 6. Environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your Foundry project values.

## 7. Sign in to Azure

```bash
az login
az account set --subscription "<your-subscription-id>"
```

## 8. Verify

```bash
az account show --query name -o tsv
docker --version
kubectl version --client
python --version
node --version
```

All commands should succeed without errors.

## 9. Run the docs site

```bash
mkdocs serve
```

Open `http://127.0.0.1:8000` and confirm the workshop pages load.
