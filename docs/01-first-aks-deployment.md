# 01 Your First AKS Deployment

## Goal

Create an AKS cluster, connect it to your container registry, and deploy the
Patient Triage backend and frontend as Kubernetes pods.

## Estimated time

20 minutes.

## Official references

- [Quickstart: Deploy an AKS cluster](https://learn.microsoft.com/azure/aks/learn/quick-kubernetes-deploy-cli)
- [Authenticate with ACR from AKS](https://learn.microsoft.com/azure/aks/cluster-container-registry-integration)
- [kubectl cheat sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

## Exercise

### Step 1 — Create the AKS cluster

```bash
source .env

az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER_NAME \
  --node-count 2 \
  --node-vm-size Standard_DS2_v2 \
  --attach-acr $ACR_NAME \
  --generate-ssh-keys
```

The `--attach-acr` flag grants the cluster permission to pull images from your
container registry.

### Step 2 — Get cluster credentials

```bash
az aks get-credentials \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER_NAME
```

Verify the connection:

```bash
kubectl get nodes
```

You should see two nodes in `Ready` status.

### Step 3 — Create the namespace

```bash
kubectl apply -f manifests/aks/namespace.yaml
```

### Step 4 — Create the Secret and ConfigMap

First, update `manifests/aks/secret.yaml` with your base64-encoded project endpoint:

```bash
echo -n "$AZURE_AI_PROJECT_ENDPOINT" | base64
```

Replace the placeholder values in `manifests/aks/secret.yaml`.

Next, grant the AKS kubelet identity access to the AI resource so the backend
pods can authenticate with `DefaultAzureCredential`:

```bash
KUBELET_ID=$(az aks show --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER_NAME \
  --query "identityProfile.kubeletidentity.clientId" -o tsv)

AI_RESOURCE_ID=$(az resource list --resource-group $RESOURCE_GROUP \
  --resource-type "Microsoft.CognitiveServices/accounts" --query "[0].id" -o tsv)

az role assignment create \
  --assignee $KUBELET_ID \
  --role "Cognitive Services OpenAI User" \
  --scope "$AI_RESOURCE_ID"
```

Add the kubelet client ID to the ConfigMap so the SDK knows which managed
identity to use (required when multiple identities exist on the node):

```bash
sed -i "s/AZURE_CLIENT_ID: .*/AZURE_CLIENT_ID: \"$KUBELET_ID\"/" manifests/aks/configmap.yaml
```

Then apply:

```bash
kubectl apply -f manifests/aks/configmap.yaml
kubectl apply -f manifests/aks/secret.yaml
```

### Step 5 — Update image references

Edit `manifests/aks/backend-deployment.yaml` and
`manifests/aks/frontend-deployment.yaml` to replace `<ACR_NAME>` with your
actual ACR name:

```bash
sed -i "s/<ACR_NAME>/$ACR_NAME/g" manifests/aks/backend-deployment.yaml
sed -i "s/<ACR_NAME>/$ACR_NAME/g" manifests/aks/frontend-deployment.yaml
```

### Step 6 — Deploy the application

```bash
kubectl apply -f manifests/aks/backend-deployment.yaml
kubectl apply -f manifests/aks/backend-service.yaml
kubectl apply -f manifests/aks/frontend-deployment.yaml
kubectl apply -f manifests/aks/frontend-service.yaml
```

### Step 7 — Verify the deployment

```bash
kubectl get pods -n triage
kubectl get svc -n triage
```

Test the backend health endpoint via port-forward:

```bash
kubectl port-forward -n triage svc/triage-backend 8000:80 &
curl http://localhost:8000/api/health
```

You should see `{"status": "healthy"}`.

## What this lab demonstrates

1. Creating an AKS cluster with the Azure CLI.
2. Integrating ACR for seamless image pulling.
3. Using `kubectl` to deploy workloads.
4. Kubernetes core concepts: Namespace, Deployment, Pod, Service.
5. Health checks via port-forwarding.

## Expected result

Two backend pods and two frontend pods running in the `triage` namespace.
The backend responds to health checks on port 8000.

## Verification

- [ ] `kubectl get nodes` shows two Ready nodes.
- [ ] `kubectl get pods -n triage` shows 4 pods (2 backend, 2 frontend) all Running.
- [ ] `curl http://localhost:8000/api/health` returns `{"status": "healthy"}`.
