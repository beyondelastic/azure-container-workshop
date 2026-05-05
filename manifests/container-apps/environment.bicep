@description('Location for all resources.')
param location string = resourceGroup().location

@description('Name of the Container Apps environment.')
param environmentName string = 'cae-triage'

@description('Name of the Log Analytics workspace.')
param logAnalyticsName string = 'law-triage'

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource environment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: environmentName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
    daprAIConnectionString: ''
  }
}

output environmentId string = environment.id
output environmentName string = environment.name
