# 09 Jobs & Background Processing

## Goal

Run batch workloads with Azure Container Apps Jobs. Create a scheduled job
that batch-processes the triage queue and a manual-trigger job for on-demand
report generation.

## Estimated time

15 minutes.

## Official references

- [Jobs in Azure Container Apps](https://learn.microsoft.com/azure/container-apps/jobs)
- [Create a job with the Azure CLI](https://learn.microsoft.com/azure/container-apps/jobs-get-started-cli)
- [Scheduled jobs](https://learn.microsoft.com/azure/container-apps/tutorial-jobs-scheduled)
- [Manual trigger jobs](https://learn.microsoft.com/azure/container-apps/jobs-get-started-cli#create-a-manual-job)

## Key concepts

| Concept | Purpose |
|---------|---------|
| **Container Apps Job** | A container that runs to completion (not a long-running service). |
| **Scheduled trigger** | Runs on a cron schedule (e.g. nightly batch). |
| **Manual trigger** | Runs on demand via CLI or API. |
| **Event trigger** | Runs in response to events (queue messages, etc.). |
| **Execution** | A single run of a job — has its own logs and exit code. |

## Exercise

### Step 1 — Create a scheduled job

Deploy the batch worker as a scheduled job that runs at 2 AM UTC daily:

```bash
source .env

# Enable admin credentials on ACR (needed for job registry auth)
az acr update --name $ACR_NAME --admin-enabled true

az containerapp job create \
  --name triage-batch-job \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINERAPPS_ENVIRONMENT \
  --image $ACR_NAME.azurecr.io/triage-worker:v1 \
  --registry-server $ACR_NAME.azurecr.io \
  --registry-username $ACR_NAME \
  --registry-password "$(az acr credential show --name $ACR_NAME --query 'passwords[0].value' -o tsv)" \
  --trigger-type Schedule \
  --cron-expression "0 2 * * *" \
  --replica-timeout 600 \
  --replica-retry-limit 1 \
  --cpu 0.5 \
  --memory 1Gi \
  --secrets "project-endpoint=$AZURE_AI_PROJECT_ENDPOINT" \
  --env-vars "AZURE_AI_PROJECT_ENDPOINT=secretref:project-endpoint" \
             "AZURE_AI_MODEL_DEPLOYMENT=$AZURE_AI_MODEL_DEPLOYMENT"
```

### Step 2 — Trigger the scheduled job manually (for testing)

Don't wait until 2 AM — start an execution now:

```bash
az containerapp job start \
  --name triage-batch-job \
  --resource-group $RESOURCE_GROUP
```

### Step 3 — View execution history

```bash
az containerapp job execution list \
  --name triage-batch-job \
  --resource-group $RESOURCE_GROUP \
  -o table
```

### Step 4 — View job logs

```bash
az containerapp job logs show \
  --name triage-batch-job \
  --resource-group $RESOURCE_GROUP \
  --follow
```

You should see the batch triage report with urgency classifications for the
sample patients.

### Step 5 — Create a manual-trigger job

Create a second job that runs only when explicitly triggered — useful for
on-demand reports:

```bash
az containerapp job create \
  --name triage-report-job \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINERAPPS_ENVIRONMENT \
  --image $ACR_NAME.azurecr.io/triage-worker:v1 \
  --registry-server $ACR_NAME.azurecr.io \
  --registry-username $ACR_NAME \
  --registry-password "$(az acr credential show --name $ACR_NAME --query 'passwords[0].value' -o tsv)" \
  --trigger-type Manual \
  --replica-timeout 600 \
  --replica-retry-limit 1 \
  --cpu 0.5 \
  --memory 1Gi \
  --secrets "project-endpoint=$AZURE_AI_PROJECT_ENDPOINT" \
  --env-vars "AZURE_AI_PROJECT_ENDPOINT=secretref:project-endpoint" \
             "AZURE_AI_MODEL_DEPLOYMENT=$AZURE_AI_MODEL_DEPLOYMENT"
```

### Step 6 — Run the manual job

```bash
az containerapp job start \
  --name triage-report-job \
  --resource-group $RESOURCE_GROUP
```

### Step 7 — Compare execution history

```bash
# Scheduled job
az containerapp job execution list \
  --name triage-batch-job \
  --resource-group $RESOURCE_GROUP \
  -o table

# Manual job
az containerapp job execution list \
  --name triage-report-job \
  --resource-group $RESOURCE_GROUP \
  -o table
```

### Step 8 — List all jobs in the environment

```bash
az containerapp job list \
  --resource-group $RESOURCE_GROUP \
  -o table
```

## Jobs vs Container Apps

| Aspect | Container App | Container Apps Job |
|--------|--------------|-------------------|
| **Lifecycle** | Long-running (always on or scaled to zero) | Runs to completion, then exits |
| **Trigger** | HTTP requests, TCP, events | Schedule, manual, event |
| **Scaling** | 0–N replicas based on load | 0–N executions based on trigger |
| **Use case** | APIs, web apps, microservices | Batch processing, ETL, reports |
| **Cost** | Per-second while running | Per-second per execution |

## What this lab demonstrates

1. Creating scheduled and manual-trigger Container Apps Jobs.
2. Running a batch AI workload (triage classification).
3. Viewing execution history and logs.
4. Understanding when to use Jobs vs always-on Container Apps.

## Expected result

Two jobs exist in the environment. The scheduled job runs nightly (and can be
triggered manually). The manual job runs on demand. Both process patient
records through Microsoft Foundry and output a triage report.

## Verification

- [ ] `az containerapp job list --resource-group $RESOURCE_GROUP -o table` shows both jobs.
- [ ] Manual execution of `triage-batch-job` completes successfully.
- [ ] Job logs show the batch triage report with patient classifications.
- [ ] `triage-report-job` can be triggered and shows execution history.
