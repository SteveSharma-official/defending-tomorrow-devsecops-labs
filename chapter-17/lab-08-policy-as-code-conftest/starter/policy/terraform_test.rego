package main

import rego.v1

bucket(tags) := {"resource_changes": [{
	"address": "aws_s3_bucket.b",
	"type": "aws_s3_bucket",
	"change": {"actions": ["create"], "after": {"tags": tags}},
}]}

sg(cidr, from, to) := {"resource_changes": [{
	"address": "aws_security_group.s",
	"type": "aws_security_group",
	"change": {"actions": ["create"], "after": {"ingress": [{"cidr_blocks": [cidr], "from_port": from, "to_port": to}]}},
}]}

test_bucket_with_all_tags_is_allowed if {
	count(deny) == 0 with input as bucket({"CostCenter": "cc-1", "DataClassification": "internal"})
}

test_bucket_missing_tag_is_denied if {
	count(deny) == 1 with input as bucket({"CostCenter": "cc-1"})
}

test_default_tags_in_tags_all_are_accepted if {
	count(deny) == 0 with input as {"resource_changes": [{
		"address": "aws_s3_bucket.b",
		"type": "aws_s3_bucket",
		"change": {"actions": ["create"], "after": {"tags": null, "tags_all": {"CostCenter": "cc", "DataClassification": "internal"}}},
	}]}
}

test_ssh_from_internet_is_denied if {
	count(deny) == 1 with input as sg("0.0.0.0/0", 22, 22)
}

test_port_range_covering_rdp_is_denied if {
	count(deny) == 1 with input as sg("0.0.0.0/0", 3000, 4000)
}

test_https_from_internet_is_allowed if {
	count(deny) == 0 with input as sg("0.0.0.0/0", 443, 443)
}

test_ssh_from_private_range_is_allowed if {
	count(deny) == 0 with input as sg("10.0.0.0/8", 22, 22)
}

test_kms_without_rotation_is_denied if {
	count(deny) == 1 with input as {"resource_changes": [{
		"address": "aws_kms_key.k",
		"type": "aws_kms_key",
		"change": {"actions": ["create"], "after": {"enable_key_rotation": false}},
	}]}
}
