package release

import rego.v1

ok := {c: "success" | some c in required_checks}

test_all_green_main_is_allowed if {
	allow with input as {"checks": ok, "environment": "production", "ref": "refs/heads/main"}
}

test_failed_sast_is_denied if {
	not allow with input as {"checks": object.union(ok, {"sast": "failure"}), "environment": "production", "ref": "refs/heads/main"}
}

test_missing_check_is_denied if {
	not allow with input as {"checks": object.remove(ok, ["secrets"]), "environment": "staging", "ref": "refs/heads/main"}
}

test_feature_branch_to_production_is_denied if {
	not allow with input as {"checks": ok, "environment": "production", "ref": "refs/heads/feature-x"}
}

test_feature_branch_to_staging_is_allowed if {
	allow with input as {"checks": ok, "environment": "staging", "ref": "refs/heads/feature-x"}
}
