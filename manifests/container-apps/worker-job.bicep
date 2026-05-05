@description('Location for all resources.')
param location string = resourceGroup().location

@description('Container Apps environment resource ID.')
param environmentId string

@description('ACR login server (e.g. myacr.azurecr.io).')
param acrLoginServer string

@description('Container image tag.')
param imageTag string = 'v1'

@description('Microsoft Foundry project endpoint.')
@secure()
param azureAiProjectEndpoint string

@description('Model deployment name.')
param azureAiModelDeployment string = 'gpt-4.1-mini'

@description('Cron expression for the scheduled job (UTC).')
param cronExpression string = '0 2 * * *'

resource triageJob 'Microsoft.App/jobs@2024-03-01' = {
  name: 'triage-worker-job'
  location: location
  properties: {
    environmentId: environmentId
    configuration: {
      replicaTimeout: 600
      replicaRetryLimit: 1
      triggerType: 'Schedule'
      scheduleTriggerConfig: {
        cronExpression: cronExpression
      }
      secrets: [
        { name: 'project-endpoint', value: azureAiProjectEndpoint }
      ]
    }
    template: {
      containers: [
        {
          name: 'worker'
          image: '${acrLoginServer}/triage-worker:${imageTag}'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'AZURE_AI_PROJECT_ENDPOINT', secretRef: 'project-endpoint' }
            { name: 'AZURE_AI_MODEL_DEPLOYMENT', value: azureAiModelDeployment }
          ]
        }
      ]
    }
  }
}

output jobName string = triageJob.name
