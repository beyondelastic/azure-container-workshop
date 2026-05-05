# 02 Services & Networking

## Goal

Expose the Patient Triage app to the internet using Kubernetes Services and an
Ingress controller with path-based routing.

## Estimated time

15 minutes.

## Official references

- [Use an NGINX Ingress controller in AKS](https://learn.microsoft.com/azure/aks/app-routing)
- [Kubernetes Service types](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types)
- [Kubernetes Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)

## Key concepts

| Concept | Purpose |
|---------|---------|
| **ClusterIP** | Default Service type. Accessible only inside the cluster. |
| **LoadBalancer** | Provisions an Azure Load Balancer with a public IP. |
| **Ingress** | Layer-7 routing (host/path based) via a reverse proxy. |
| **Ingress Controller** | The actual NGINX (or other) pod that fulfils Ingress rules. |

## Exercise

### Step 1 — Enable the app-routing add-on

AKS provides a managed NGINX Ingress controller through the **app-routing**
add-on:

```bash
az aks approuting enable \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER_NAME
```

Verify the Ingress controller pods are running:

```bash
kubectl get pods -n app-routing-system
```

### Step 2 — Understand the existing Services

In lesson 01 we created two ClusterIP Services. Review them:

```bash
kubectl get svc -n triage
```

Both are `ClusterIP` — accessible inside the cluster only.

### Step 3 — Apply the Ingress resource

The Ingress routes external traffic to the correct backend:

- `/api/*` → `triage-backend:80`
- `/*` → `triage-frontend:80`

```bash
kubectl apply -f manifests/aks/ingress.yaml
```

### Step 4 — Get the external IP

Wait for the Ingress to be assigned an external address:

```bash
kubectl get ingress -n triage --watch
```

Once the `ADDRESS` column shows an IP, press `Ctrl+C` and open it in a browser:

```bash
export INGRESS_IP=$(kubectl get ingress triage-ingress -n triage -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Open http://$INGRESS_IP in your browser"
```

### Step 5 — Test the routes

```bash
# Frontend — should return HTML
curl -s http://$INGRESS_IP/ | head -5

# Backend API — should return JSON
curl -s http://$INGRESS_IP/api/health
```

### Step 6 — Test the triage flow

Open `http://<INGRESS_IP>` in your browser. Submit a patient with symptoms and
confirm you see a triage result with an urgency classification.

## What this lab demonstrates

1. The difference between ClusterIP, LoadBalancer, and Ingress.
2. Enabling the managed AKS app-routing NGINX Ingress controller.
3. Path-based routing with a single external IP.
4. End-to-end connectivity from browser → Ingress → Service → Pod.

## Expected result

A single public IP that routes `/api/*` to the backend and everything else to
the frontend. The Patient Triage UI loads in the browser and can submit patients.

## Verification

- [ ] `kubectl get ingress -n triage` shows an external IP.
- [ ] `curl http://$INGRESS_IP/api/health` returns `{"status": "healthy"}`.
- [ ] Opening the IP in a browser shows the Patient Triage UI.
- [ ] Submitting a patient returns an urgency classification.
