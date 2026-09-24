# LAB-08 — organisational guardrails evaluated against `terraform show -json` plan output.
# Written in Rego v1 syntax (OPA 1.x default). The book's Chapter 12/15 examples use
# pre-1.0 syntax (`deny[msg] { ... }`), which OPA 1.x rejects unless run with --v0-compatible.
package main

import rego.v1

required_tags := {"CostCenter", "DataClassification"}

admin_ports := {22, 3389}

as_object(x) := x if is_object(x)

as_object(x) := {} if not is_object(x)

creating_or_updating(rc) if {
	some action in rc.change.actions
	action in {"create", "update"}
}

# Rule 1 — every S3 bucket carries the mandatory tags
deny contains msg if {
	some rc in input.resource_changes
	rc.type == "aws_s3_bucket"
	creating_or_updating(rc)

	# provider default_tags appear in tags_all; resource-level tags in tags
	tags := object.union(as_object(object.get(rc.change.after, "tags_all", {})), as_object(object.get(rc.change.after, "tags", {})))
	missing := required_tags - {k | some k, _ in tags}
	count(missing) > 0
	msg := sprintf("POL-TAG-001 %s is missing required tags: %v", [rc.address, sort(missing)])
}

# Rule 2 — no administrative port is reachable from the internet
deny contains msg if {
	some rc in input.resource_changes
	rc.type == "aws_security_group"
	creating_or_updating(rc)
	some rule in rc.change.after.ingress
	"0.0.0.0/0" in rule.cidr_blocks
	some port in admin_ports
	rule.from_port <= port
	port <= rule.to_port
	msg := sprintf("POL-NET-002 %s exposes admin port %d to 0.0.0.0/0", [rc.address, port])
}

# Rule 3 — customer-managed KMS keys must rotate
deny contains msg if {
	some rc in input.resource_changes
	rc.type == "aws_kms_key"
	creating_or_updating(rc)
	not rc.change.after.enable_key_rotation
	msg := sprintf("POL-KMS-003 %s must set enable_key_rotation = true", [rc.address])
}
