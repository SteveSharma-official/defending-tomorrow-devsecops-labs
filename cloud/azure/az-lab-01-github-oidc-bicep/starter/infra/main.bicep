// AZ-LAB-01 — secure-by-default storage account and Key Vault (RBAC mode) for the lab resource group.
targetScope = 'resourceGroup'

@description('Azure region; defaults to the resource group location')
param location string = resourceGroup().location

@description('Short unique suffix, lowercase letters/digits (3-8 chars)')
@minLength(3)
@maxLength(8)
param suffix string

var tags = {
  Lab: 'dt-az-lab-01'
  CostCenter: 'security-lab'
  DataClassification: 'internal'
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  // checkov:skip=CKV_AZURE_43:Name is built from a validated parameter (3-8 chars) and cannot be evaluated statically
  // checkov:skip=CKV_AZURE_206:LRS chosen to minimise lab cost; production replication is a resilience decision (Chapter 26)
  name: 'dtazlab01${suffix}'
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    defaultToOAuthAuthentication: true
    publicNetworkAccess: 'Disabled' // data plane unreachable from the internet; the lab only uses the control plane
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
    encryption: {
      keySource: 'Microsoft.Storage'
      requireInfrastructureEncryption: true
      services: {
        blob: { enabled: true }
        file: { enabled: true }
      }
    }
  }
}

resource vault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  // checkov:skip=CKV_AZURE_110:Purge protection off ONLY so the lab can be fully deleted; it is irreversible once enabled
  // checkov:skip=CKV_AZURE_42:Soft delete is on (7 days); this check also requires purge protection - see CKV_AZURE_110
  name: 'kv-dtazlab01-${suffix}'
  location: location
  tags: tags
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true      // Azure RBAC, not legacy access policies (Appendix B mixes both)
    enableSoftDelete: true
    softDeleteRetentionInDays: 7       // shortest retention, so lab cleanup completes quickly
    // enablePurgeProtection is deliberately omitted for the lab ONLY; set it to true in production (irreversible)
    publicNetworkAccess: 'Disabled'
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
  }
}

output storageAccountName string = storage.name
output keyVaultName string = vault.name
