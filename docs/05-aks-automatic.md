# 05 AKS Automatic

## Goal

Experience simplified Kubernetes with AKS Automatic. Deploy the same Patient
Triage app with zero infrastructure tuning and compare it with the standard
AKS cluster from earlier lessons.

## Estimated time

20 minutes.

## Official references

- [AKS Automatic overview](https://learn.microsoft.com/azure/aks/aks-automatic-overview)
- [Create an AKS Automatic cluster](https://learn.microsoft.com/azure/aks/learn/quick-kubernetes-automatic-deploy)
- [AKS Automatic vs Standard comparison](https://learn.microsoft.com/azure/aks/intro-aks#compare-aks-tiers-and-features)

## Key concepts

| Feature | Standard AKS | AKS Automatic |
|---------|-------------|---------------|
| **Node pools** | You create and manage | Auto-provisioned |
| **VM size** | You choose | System selects optimal |
| **Scaling** | You configure HPA + cluster autoscaler | Built-in, always on |
| **Upgrades** | You schedule | Automatic |
| **Monitoring** | You enable Container Insights | Enabled by default |
| **Ingress** | You install controller | App routing built-in |
| **Security** | You configure policies | Best practices enabled |

AKS Automatic is designed for teams that want Kubernetes without the
operational overhead. It applies Microsoft's recommended best practices
automatically.

## Exercise

### Step 1 — Create an AKS Automatic cluster

```bash
source .env

az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_AUTO_CLUSTER_NAME \
  --sku automatic \
  --attach-acr $ACR_NAME
```

!!! note
    AKS Automatic takes a few minutes to provision. The cluster comes with
    node auto-provisioning, monitoring, and app routing enabled by default.

### Step 2 — Get credentials

```bash
az aks get-credentials \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_AUTO_CLUSTER_NAME
```

### Step 3 — Explore what is pre-configured

```bash
# Nodes — provisioned automatically
kubectl get nodes

# Monitoring agent — already running
kubectl get pods -n kube-system | grep ama-

# App routing — already installed
kubectl get pods -n app-routing-system
```

Notice: you did **not** need to configure any of this manually.

### Step 4 — Deploy the same app

Use the same manifests from lesson 01:

```bash
kubectl apply -f manifests/aks/namespace.yaml
kubectl apply -f manifests/aks/configmap.yaml
kubectl apply -f manifests/aks/secret.yaml
kubectl apply -f manifests/aks/backend-deployment.yaml
kubectl apply -f manifests/aks/backend-service.yaml
kubectl apply -f manifests/aks/frontend-deployment.yaml
kubectl apply -f manifests/aks/frontend-service.yaml
kubectl apply -f manifests/aks/ingress.yaml
```

### Step 5 — Verify the deployment

```bash
kubectl get pods -n triage
kubectl get ingress -n triage
```

Get the external IP and test:

```bash
export INGRESS_IP=$(kubectl get ingress triage-ingress -n triage -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$INGRESS_IP/api/health
```

### Step 6 — Compare with standard AKS

Open the Azure Portal and compare both clusters side by side:

| Aspect | Check in Portal |
|--------|----------------|
| Node pools | AKS Automatic → no manual node pool management |
| Monitoring | Insights tab → already active |
| Upgrades | Settings → Auto-upgrade enabled |
| Network policy | Networking → Azure network policy active |

### Step 7 — Observe auto-scaling

AKS Automatic scales nodes automatically based on workload demand. You do not
need to configure a cluster autoscaler:

```bash
# Apply the HPA — pod scaling still works
kubectl apply -f manifests/aks/hpa.yaml

# Check the node count after deploying
kubectl get nodes
```

If you send load (like in lesson 03), AKS Automatic provisions additional
nodes as needed — without any autoscaler configuration.

## What this lab demonstrates

1. Creating an AKS Automatic cluster with a single command.
2. Batteries-included: monitoring, ingress, scaling, upgrades.
3. Deploying the same manifests with zero changes.
4. Reduced operational overhead compared to standard AKS.
5. Node auto-provisioning — the cluster picks VM sizes for you.

## When to use AKS Automatic

- **Choose AKS Automatic** when you want Kubernetes without the ops overhead.
  Ideal for teams new to Kubernetes, dev/test environments, and workloads
  where Microsoft's defaults align with your needs.

- **Choose Standard AKS** when you need fine-grained control over node pools,
  VM SKUs, network plugins, or custom policies.

## Expected result

The Patient Triage app runs on AKS Automatic with the same manifests. The
cluster self-manages nodes, monitoring, ingress, and upgrades.

## Verification

- [ ] `az aks show --name $AKS_AUTO_CLUSTER_NAME --resource-group $RESOURCE_GROUP --query sku` shows Automatic.
- [ ] `kubectl get nodes` shows auto-provisioned nodes.
- [ ] `kubectl get pods -n triage` shows all pods Running.
- [ ] `curl http://$INGRESS_IP/api/health` returns `{"status": "healthy"}`.
- [ ] Container Insights is active without manual setup.

## Cleanup (optional)

If you want to keep only the standard cluster for later lessons:

```bash
az aks delete \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_AUTO_CLUSTER_NAME \
  --yes --no-wait

# Switch back to the standard cluster
az aks get-credentials \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER_NAME
```
