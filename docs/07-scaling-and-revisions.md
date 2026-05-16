# 07 Scaling & Revisions

## Goal

Configure HTTP-based auto-scaling, deploy a new revision with a code change,
and split traffic between revisions for a blue-green deployment.

## Estimated time

15 minutes.

## Official references

- [Set scaling rules in Container Apps](https://learn.microsoft.com/azure/container-apps/scale-app)
- [Revisions in Container Apps](https://learn.microsoft.com/azure/container-apps/revisions)
- [Traffic splitting](https://learn.microsoft.com/azure/container-apps/traffic-splitting)
- [Blue-green deployment](https://learn.microsoft.com/azure/container-apps/blue-green-deployment)

## Key concepts

| Concept | Purpose |
|---------|---------|
| **Revision** | An immutable snapshot of a Container App version. |
| **Scaling rule** | Defines when to add/remove replicas (HTTP, CPU, custom). |
| **Traffic splitting** | Route a percentage of traffic to different revisions. |
| **Blue-green** | Run two versions simultaneously and shift traffic gradually. |

## Exercise

### Step 1 — Review current scaling

```bash
az containerapp show \
  --name triage-backend \
  --resource-group $RESOURCE_GROUP \
  --query properties.template.scale
```

### Step 2 — Add an HTTP scaling rule

Scale the backend based on concurrent HTTP requests:

```bash
az containerapp update \
  --name triage-backend \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 1 \
  --max-replicas 10 \
  --scale-rule-name http-scaling \
  --scale-rule-type http \
  --scale-rule-http-concurrency 20
```

This means: when each replica handles more than 20 concurrent requests, add
another replica.

### Step 3 — Observe in-memory state inconsistency

With multiple replicas, the backend's in-memory patient store becomes
unreliable. Each replica has its own memory — data submitted to one replica is
invisible to the other.

Force two replicas to make this observable:

```bash
az containerapp update \
  --name triage-backend \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 2 \
  --max-replicas 10
```

Now open the frontend UI and submit a new patient. Refresh the patient list
several times — you will see the patient appear and disappear depending on
which replica handles the request.

!!! warning "Why does this happen?"
    Each replica runs its own Python process with a separate in-memory `dict`.
    The load balancer round-robins between them, so reads may hit a different
    replica than the one that received the write.

    We fix this in **Lesson 08** by adding a shared Redis state store via Dapr,
    so all replicas read/write from the same backing store.

### Step 4 — Enable multiple revisions

By default, Container Apps operates in single-revision mode. Enable
multi-revision mode to support traffic splitting:

```bash
az containerapp revision set-mode \
  --name triage-backend \
  --resource-group $RESOURCE_GROUP \
  --mode multiple
```

### Step 5 — Note the current revision name

```bash
az containerapp revision list \
  --name triage-backend \
  --resource-group $RESOURCE_GROUP \
  --query "[].name" -o tsv
```

Save this — it is the "blue" revision.

### Step 6 — Deploy a new revision (green)

Deploy with a revision suffix and a new environment variable to distinguish it:

```bash
az containerapp update \
  --name triage-backend \
  --resource-group $RESOURCE_GROUP \
  --revision-suffix green \
  --set-env-vars "APP_VERSION=v2"
```

### Step 7 — List revisions

```bash
az containerapp revision list \
  --name triage-backend \
  --resource-group $RESOURCE_GROUP \
  -o table
```

You should see two active revisions.

### Step 8 — Split traffic 80/20

```bash
BLUE_REVISION=$(az containerapp revision list \
  --name triage-backend \
  --resource-group $RESOURCE_GROUP \
  --query "[?contains(name, 'green') == \`false\`].name" -o tsv | head -1)

GREEN_REVISION=$(az containerapp revision list \
  --name triage-backend \
  --resource-group $RESOURCE_GROUP \
  --query "[?contains(name, 'green')].name" -o tsv)

az containerapp ingress traffic set \
  --name triage-backend \
  --resource-group $RESOURCE_GROUP \
  --revision-weight "$BLUE_REVISION=80" "$GREEN_REVISION=20"
```

### Step 9 — Verify traffic split

```bash
az containerapp ingress traffic show \
  --name triage-backend \
  --resource-group $RESOURCE_GROUP
```

### Step 10 — Promote green to 100%

Once satisfied, shift all traffic to the green revision:

```bash
az containerapp ingress traffic set \
  --name triage-backend \
  --resource-group $RESOURCE_GROUP \
  --revision-weight "$GREEN_REVISION=100"
```

### Step 11 — Deactivate the old revision

```bash
az containerapp revision deactivate \
  --name triage-backend \
  --resource-group $RESOURCE_GROUP \
  --revision $BLUE_REVISION
```

## What this lab demonstrates

1. HTTP-based auto-scaling rules.
2. Multi-revision mode for side-by-side deployments.
3. Traffic splitting for canary/blue-green patterns.
4. Zero-downtime deployment workflow.

## Expected result

The backend auto-scales based on concurrent requests. Two revisions exist
simultaneously with traffic split 80/20, then promoted to 100% on the new
revision.

## Verification

- [ ] `az containerapp show ... --query properties.template.scale` shows the HTTP rule.
- [ ] Two revisions are listed with `az containerapp revision list`.
- [ ] Traffic split shows 80/20, then 100/0 after promotion.
- [ ] The old revision is deactivated.
