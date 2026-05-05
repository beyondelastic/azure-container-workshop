# 03 Scaling & Configuration

## Goal

Auto-scale the backend based on CPU usage and manage application configuration
securely with ConfigMaps and Secrets.

## Estimated time

15 minutes.

## Official references

- [Horizontal Pod Autoscaler in AKS](https://learn.microsoft.com/azure/aks/concepts-scale#horizontal-pod-autoscaler)
- [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Use Azure Key Vault with AKS](https://learn.microsoft.com/azure/aks/csi-secrets-store-driver)

## Key concepts

| Concept | Purpose |
|---------|---------|
| **ConfigMap** | Store non-sensitive key-value pairs (model name, deployment settings). |
| **Secret** | Store sensitive data (API keys, connection strings) — base64 encoded. |
| **HPA** | Horizontal Pod Autoscaler — adjusts pod count based on metrics. |
| **Metrics Server** | Provides CPU/memory metrics for HPA decisions. |

## Exercise

### Step 1 — Review the ConfigMap

The ConfigMap stores the model deployment name:

```bash
kubectl get configmap triage-config -n triage -o yaml
```

You can update the deployment name without rebuilding the container:

```bash
kubectl edit configmap triage-config -n triage
```

### Step 2 — Review the Secret

```bash
kubectl get secret triage-secrets -n triage -o yaml
```

!!! warning "Production note"
    In production, use the [Azure Key Vault CSI driver](https://learn.microsoft.com/azure/aks/csi-secrets-store-driver)
    instead of Kubernetes Secrets. The workshop uses Secrets for simplicity.

### Step 3 — Apply the Horizontal Pod Autoscaler

```bash
kubectl apply -f manifests/aks/hpa.yaml
```

Review the HPA:

```bash
kubectl get hpa -n triage
```

The HPA targets 10% average CPU utilization and scales between 2 and 10
replicas.

!!! info "Scaling and in-memory state"
    The backend stores triage results in an in-memory dictionary. When multiple
    replicas are running, each pod has its own copy — a patient triaged on pod A
    won't appear in responses served by pod B. This is expected and illustrates
    why production workloads need external state (e.g. Redis, a database, or a
    Dapr state store). For this lesson, focus on observing the scaling behaviour
    rather than the UI patient list.

### Step 4 — Verify the Metrics Server

AKS includes a Metrics Server by default:

```bash
kubectl top pods -n triage
```

If you see CPU and memory values, the Metrics Server is working.

### Step 5 — Generate load to trigger scaling

Open a second terminal and send sustained requests:

```bash
export INGRESS_IP=$(kubectl get ingress triage-ingress -n triage -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Sustained load generator — runs until you press Ctrl+C
while true; do
  for i in $(seq 1 20); do
    curl -s -X POST http://$INGRESS_IP/api/triage \
      -H "Content-Type: application/json" \
      -d '{"name":"Load Test","age":40,"symptoms":"headache, fatigue, mild fever"}' > /dev/null &
  done
  sleep 0.5
done
```

### Step 6 — Watch the HPA respond

```bash
kubectl get hpa -n triage --watch
```

Over a few minutes you should see `REPLICAS` increase as CPU usage rises.

```bash
kubectl get pods -n triage -l app=triage-backend
```

### Step 7 — Observe scale-down

Stop the load. After a few minutes the HPA scales back to the minimum:

```bash
kubectl get hpa -n triage --watch
```

## What this lab demonstrates

1. Externalising configuration with ConfigMaps.
2. Managing secrets in Kubernetes (and why Key Vault is better for production).
3. Configuring a Horizontal Pod Autoscaler with CPU targets.
4. Observing automatic scale-out and scale-in under load.

## Expected result

Under load, the backend scales from 2 to more replicas. After load stops, it
scales back to 2. Configuration values are injected from ConfigMap and Secret
without baking them into the image.

## Verification

- [ ] `kubectl get configmap triage-config -n triage` shows the deployment name.
- [ ] `kubectl get hpa -n triage` shows the HPA with targets and current metrics.
- [ ] Under load, `REPLICAS` increases above 2.
- [ ] After load stops, `REPLICAS` returns to 2.
