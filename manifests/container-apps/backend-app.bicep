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

resource backendApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'triage-backend'
  location: location
  properties: {
    managedEnvironmentId: environmentId
    configuration: {
      ingress: {
        external: false
        targetPort: 8000
        transport: 'http'
      }
      secrets: [
        { name: 'project-endpoint', value: azureAiProjectEndpoint }
      ]
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: '${acrLoginServer}/triage-backend:${imageTag}'
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
      scale: {
        minReplicas: 1
        maxReplicas: 10
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '20'
              }
            }
          }
        ]
      }
    }
  }
}

output backendFqdn string = backendApp.properties.configuration.ingress.fqdn
output backendName string = backendApp.name
