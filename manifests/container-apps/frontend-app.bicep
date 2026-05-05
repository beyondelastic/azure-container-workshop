@description('Location for all resources.')
param location string = resourceGroup().location

@description('Container Apps environment resource ID.')
param environmentId string

@description('ACR login server (e.g. myacr.azurecr.io).')
param acrLoginServer string

@description('Container image tag.')
param imageTag string = 'v1'

resource frontendApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'triage-frontend'
  location: location
  properties: {
    managedEnvironmentId: environmentId
    configuration: {
      ingress: {
        external: true
        targetPort: 80
        transport: 'http'
      }
    }
    template: {
      containers: [
        {
          name: 'frontend'
          image: '${acrLoginServer}/triage-frontend:${imageTag}'
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 5
      }
    }
  }
}

output frontendFqdn string = frontendApp.properties.configuration.ingress.fqdn
output frontendUrl string = 'https://${frontendApp.properties.configuration.ingress.fqdn}'
