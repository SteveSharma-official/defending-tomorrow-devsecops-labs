// AZ-LAB-02 test fixture — compliant counterpart.
param location string = resourceGroup().location
param suffix string

resource good 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'dtazlab02ok${suffix}'
  location: location
  tags: { DataClassification: 'internal' }
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
  }
}
