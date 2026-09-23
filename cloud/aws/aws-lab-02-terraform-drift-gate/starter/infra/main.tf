# AWS-LAB-02 — the LAB-07 evidence bucket, now actually deployed through a gated pipeline.
terraform {
  required_version = ">= 1.10"
  backend "s3" {
    # bucket and region are supplied at init time: terraform init -backend-config=...
    key          = "dt-aws-lab-02/terraform.tfstate"
    encrypt      = true
    use_lockfile = true # S3-native state locking (Terraform >= 1.10); no DynamoDB table needed
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      CostCenter         = "security-lab"
      DataClassification = "internal"
      Lab                = "dt-aws-lab-02"
    }
  }
}

variable "region" {
  type    = string
  default = "ap-southeast-2"
}

variable "bucket_name" {
  type        = string
  description = "Globally unique bucket name, e.g. dt-lab-07-evidence-<your-initials>-<random>"
  # no default: supplied by the pipeline from a repository variable
}

resource "aws_kms_key" "evidence" {
  #checkov:skip=CKV2_AWS_64:Lab uses the default key policy; production keys need an explicit least-privilege policy (Chapter 8, section 8.4)
  description             = "CMK for AWS-LAB-02 evidence bucket"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

resource "aws_s3_bucket" "evidence" {
  #checkov:skip=CKV_AWS_18:Short-lived lab bucket; production evidence buckets log to a central access-log bucket (Chapter 22)
  #checkov:skip=CKV2_AWS_62:No event consumers in this lab
  #checkov:skip=CKV_AWS_144:Cross-region replication is a resilience decision out of scope for this lab (Chapter 26)
  bucket = var.bucket_name
}

resource "aws_s3_bucket_public_access_block" "evidence" {
  bucket                  = aws_s3_bucket.evidence.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.evidence.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_versioning" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  rule {
    id     = "expire-lab-evidence"
    status = "Enabled"
    filter {}
    expiration {
      days = 30
    }
    noncurrent_version_expiration {
      noncurrent_days = 7
    }
    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }
}

data "aws_iam_policy_document" "tls_only" {
  statement {
    sid     = "DenyInsecureTransport"
    effect  = "Deny"
    actions = ["s3:*"]
    resources = [
      aws_s3_bucket.evidence.arn,
      "${aws_s3_bucket.evidence.arn}/*",
    ]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_s3_bucket_policy" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  policy = data.aws_iam_policy_document.tls_only.json
}

output "bucket_name" {
  value = aws_s3_bucket.evidence.id
}
