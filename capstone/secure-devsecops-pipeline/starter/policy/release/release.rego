# CAPSTONE — release decision policy (extends LAB-14): the deploy gate is a policy decision, not an if-statement.
package release

import rego.v1

required_checks := {"threat_model", "workflow_lint", "secrets", "sast", "sca", "tests", "k8s_policy", "build_scan"}

default allow := false

allow if {
	count(violations) == 0
}

violations contains msg if {
	some check in required_checks
	object.get(input.checks, check, "missing") != "success"
	msg := sprintf("required check '%s' is %s", [check, object.get(input.checks, check, "missing")])
}

violations contains msg if {
	input.environment == "production"
	input.ref != "refs/heads/main"
	msg := sprintf("production releases must come from main, not %s", [input.ref])
}
