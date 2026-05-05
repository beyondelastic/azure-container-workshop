# 06 Your First Container App

## Goal

Deploy the Patient Triage backend and frontend to Azure Container Apps from
your container registry and verify the app is accessible via its
auto-generated FQDN.

## Estimated time

15 minutes.

## Official references

- [Quickstart: Deploy a container app](https://learn.microsoft.com/azure/container-apps/get-started)
- [Azure Container Apps overview](https://learn.microsoft.com/azure/container-apps/overview)
- [Manage secrets in Container Apps](https://learn.microsoft.com/azure/container-apps/manage-secrets)
- [Container Apps environments](https://learn.microsoft.com/azure/container-apps/environment)

## Key concepts

| Concept | Purpose |
|---------|---------|
| **Container Apps Environment** | Shared hosting boundary with logging and networking. |
| **Container App** | A single microservice — can have multiple revisions and replicas. |
| **Ingress** | Built-in HTTP ingress with automatic TLS. |
| **Secrets** | Securely store values and reference them in environment variables. |

## Exercise

### Step 1 — Install the Container Apps CLI extension

```bash
az extension add --name containerapp --upgrade
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
```

### Step 2 — Create the Container Apps Environment

```bash
source .env

az containerapp env create \
  --name $CONTAINERAPPS_ENVIRONMENT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

### Step 3 — Deploy the backend

```bash
az containerapp create \
  --name triage-backend \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINERAPPS_ENVIRONMENT \
  --image $ACR_NAME.azurecr.io/triage-backend:v1 \
  --registry-server $ACR_NAME.azurecr.io \
  --target-port 8000 \
  --ingress internal \
  --min-replicas 1 \
  --max-replicas 10 \
  --secrets "project-endpoint=$AZURE_AI_PROJECT_ENDPOINT" \
  --env-vars "AZURE_AI_PROJECT_ENDPOINT=secretref:project-endpoint" \
             "AZURE_AI_MODEL_DEPLOYMENT=$AZURE_AI_MODEL_DEPLOYMENT"
```

!!! note
    `--ingress internal` means only other apps in the same environment can
    reach the backend. The frontend will be external.

### Step 4 — Deploy the frontend

```bash
az containerapp create \
  --name triage-frontend \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINERAPPS_ENVIRONMENT \
  --image $ACR_NAME.azurecr.io/triage-frontend:v1 \
  --registry-server $ACR_NAME.azurecr.io \
  --target-port 80 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 5
```

### Step 5 — Get the frontend URL

```bash
az containerapp show \
  --name triage-frontend \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv
```

Open the URL in your browser (HTTPS is enabled automatically).

### Step 6 — Test the backend

```bash
BACKEND_FQDN=$(az containerapp show \
  --name triage-backend \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv)

# Internal ingress — test from within the environment or use az containerapp exec
az containerapp exec \
  --name triage-frontend \
  --resource-group $RESOURCE_GROUP \
  --command -- curl -s http://triage-backend/api/health
```

## What this lab demonstrates

1. Creating a Container Apps Environment.
2. Deploying container images from ACR.
3. Configuring secrets and environment variables.
4. Internal vs external ingress.
5. Automatic HTTPS with managed certificates.

## Expected result

The frontend is accessible at a public HTTPS URL. The backend is internal-only.
Both apps are running in the Container Apps environment.

## Verification

- [ ] `az containerapp list --resource-group $RESOURCE_GROUP -o table` shows both apps.
- [ ] The frontend FQDN loads the Patient Triage UI in a browser.
- [ ] The backend health check responds via internal ingress.
