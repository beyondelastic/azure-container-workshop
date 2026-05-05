#!/usr/bin/env bash
# deploy-aks.sh — Apply AKS manifests with values substituted from .env
# Usage: ./deploy-aks.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
set -a && source "$SCRIPT_DIR/.env" && set +a

# Derive kubelet client ID
KUBELET_ID=$(az aks show --resource-group "$RESOURCE_GROUP" --name "$AKS_CLUSTER_NAME" \
  --query "identityProfile.kubeletidentity.clientId" -o tsv)

echo "Deploying to AKS cluster: $AKS_CLUSTER_NAME (RG: $RESOURCE_GROUP)"
echo "Using ACR: $ACR_NAME | Kubelet Identity: $KUBELET_ID"

# Apply each manifest with substitutions (without modifying files on disk)
for f in manifests/aks/*.yaml; do
  sed \
    -e "s|<ACR_NAME>|$ACR_NAME|g" \
    -e "s|<BASE64_ENCODED_ENDPOINT>|$(echo -n "$AZURE_AI_PROJECT_ENDPOINT" | base64 -w0)|g" \
    -e "s|<KUBELET_MANAGED_IDENTITY_CLIENT_ID>|$KUBELET_ID|g" \
    "$f" | kubectl apply -f -
done

echo "✅ All manifests applied."
