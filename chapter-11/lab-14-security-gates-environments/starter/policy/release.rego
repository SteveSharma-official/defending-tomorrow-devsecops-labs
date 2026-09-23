# LAB-14 — release decision policy: the deploy gate is a policy decision, not an if-statement.
package release

import rego.v1

required_checks := {"tests", "sast", "sca", "secrets"}

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
