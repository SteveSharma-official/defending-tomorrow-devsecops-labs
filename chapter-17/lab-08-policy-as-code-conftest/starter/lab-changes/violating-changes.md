# LAB-08 Step 7 — make these three edits to plans/plan.json (INTENTIONALLY NON-COMPLIANT)
1. In `aws_s3_bucket.evidence` delete the `"DataClassification": "internal"` tag (remember the comma).
2. In `aws_security_group.web` change the ingress ports from 443/443 to `"from_port": 22, "to_port": 22`.
3. In `aws_kms_key.evidence` set `"enable_key_rotation": false`.
