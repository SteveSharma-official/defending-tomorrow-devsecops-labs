// AZ-LAB-02 test fixture — INTENTIONALLY NON-COMPLIANT. Used only to prove the deny policies work.
param location string = resourceGroup().location
param suffix string

resource weak 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'dtazlab02bad${suffix}'
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: true
  }
}
