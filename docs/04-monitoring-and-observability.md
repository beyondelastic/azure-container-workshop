# 04 Monitoring & Observability

## Goal

Enable monitoring for the AKS cluster and application using Azure Monitor
Container Insights, query logs, and set up alerts.

## Estimated time

15 minutes.

## Official references

- [Container Insights overview](https://learn.microsoft.com/azure/azure-monitor/containers/container-insights-overview)
- [Enable Container Insights on AKS](https://learn.microsoft.com/azure/azure-monitor/containers/container-insights-enable-aks)
- [Log queries for Container Insights](https://learn.microsoft.com/azure/azure-monitor/containers/container-insights-log-query)
- [Recommended metric alerts for AKS](https://learn.microsoft.com/azure/azure-monitor/containers/container-insights-metric-alerts)

## Key concepts

| Concept | Purpose |
|---------|---------|
| **Container Insights** | Collects performance and log data from AKS clusters. |
| **Log Analytics workspace** | Stores and queries container logs with KQL. |
| **Prometheus metrics** | AKS can emit metrics in Prometheus format for Grafana/Azure Monitor. |
| **Alerts** | Notify on pod restarts, high CPU, node pressure, etc. |

## Exercise

### Step 1 — Enable Container Insights

```bash
az aks enable-addons \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER_NAME \
  --addons monitoring
```

This creates a Log Analytics workspace (or attaches to an existing one) and
deploys the monitoring agent to your cluster.

### Step 2 — Verify the monitoring agent

```bash
kubectl get pods -n kube-system | grep ama-
```

You should see `ama-logs` and `ama-metrics` pods running.

### Step 3 — View live metrics in the Azure Portal

1. Open the [Azure Portal](https://portal.azure.com).
2. Navigate to your AKS cluster.
3. Click **Monitoring → Insights**.
4. Explore the **Cluster**, **Nodes**, **Controllers**, and **Containers** tabs.

### Step 4 — Query container logs with KQL

In the Azure Portal:

1. Navigate to your AKS cluster → **Monitoring → Logs**.
2. Run this query to see recent backend logs:

```kql
ContainerLogV2
| where ContainerName == "backend"
| where LogMessage contains "triage"
| project TimeGenerated, LogMessage
| order by TimeGenerated desc
| take 20
```

### Step 5 — Query pod restart events

```kql
KubeEvents
| where Reason == "BackOff" or Reason == "Unhealthy" or Reason == "Failed"
| where Namespace == "triage"
| project TimeGenerated, Name, Reason, Message
| order by TimeGenerated desc
| take 10
```

### Step 6 — Check resource utilisation

```kql
InsightsMetrics
| where Namespace == "container.azm.ms/cpuUsage"
| where Name == "cpuUsageNanoCores"
| extend Pod = tostring(parse_json(Tags).podName)
| where Pod contains "triage-backend"
| summarize AvgCPU = avg(Val) by bin(TimeGenerated, 5m)
| render timechart
```

!!! note
    CPU metrics may take 10–15 minutes to appear after enabling the monitoring
    addon. If the query returns no results, verify data is flowing with:
    `InsightsMetrics | where TimeGenerated > ago(15m) | take 5`

### Step 7 — Create a basic alert (Portal)

1. Navigate to your Log Analytics workspace → **Logs**.
2. Run this query:

```kql
KubeEvents
| where Namespace == "triage"
| where Reason == "BackOff" or Reason == "Unhealthy" or Reason == "Failed"
```

3. Click **New alert rule** (top menu).
4. Set condition: results greater than 0, evaluation period 5 minutes.
5. Choose an action group (or create one with your email).
6. Name the rule `triage-pod-failures` and create it.

!!! tip
    Log-based alerts query the Log Analytics workspace directly and don't
    require Prometheus metric collection to be fully warmed up.

### Step 8 — View metrics from the CLI

```bash
kubectl top nodes
kubectl top pods -n triage
```

## What this lab demonstrates

1. Enabling Container Insights with a single CLI command.
2. Browsing live cluster metrics in the Azure Portal.
3. Querying structured container logs with KQL.
4. Setting up alerts for pod failures.
5. Using `kubectl top` for quick resource checks.

## Expected result

Container Insights is active on the cluster. You can see live metrics in the
Portal, query logs with KQL, and an alert rule fires if any pod enters a failed
state.

## Verification

- [ ] `kubectl get pods -n kube-system | grep ama-` shows monitoring agent pods.
- [ ] Azure Portal → AKS cluster → Insights shows live cluster data.
- [ ] A KQL query in the Logs blade returns container logs.
- [ ] An alert rule named `triage-pod-failures` exists.
- [ ] `kubectl top pods -n triage` shows CPU and memory usage.
