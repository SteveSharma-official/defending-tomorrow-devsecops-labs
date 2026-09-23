# AZ-LAB-01 Step 7 — INTENTIONALLY INSECURE edits to infra/main.bicep (storage account properties)
    minimumTlsVersion: 'TLS1_0'
    supportsHttpsTrafficOnly: false
    allowBlobPublicAccess: true
    publicNetworkAccess: 'Enabled'
    networkAcls: { defaultAction: 'Allow', bypass: 'AzureServices' }
