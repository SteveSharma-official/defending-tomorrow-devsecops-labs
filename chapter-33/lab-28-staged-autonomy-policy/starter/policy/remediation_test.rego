package remediation.decision_test

import data.remediation.decision
import data.remediation.policy
import rego.v1

base := {
	"action_class": "workload_isolation",
	"requested_level": 3,
	"affected_count": 1,
	"rollback_verified": true,
	"accumulated_actions": 1,
	"session_duration_seconds": 120,
	"previous_rollback_failed": false,
	"cascading_indicators": [],
}

ready := {"visibility": 3, "revocation": 2, "preservation": 2, "validation": 2}

test_level3_isolation_allowed_when_containment_ready if {
	decision.allow with input.action as base with data.containment_maturity as ready
}

test_level_above_assignment_denied if {
	not decision.allow with input.action as object.union(base, {"action_class": "firewall_rule_change"})
		with data.containment_maturity as ready
}

test_blast_radius_limit_enforced if {
	not decision.allow with input.action as object.union(base, {"affected_count": 4})
		with data.containment_maturity as ready
}

test_unlisted_action_class_denied if {
	not decision.allow with input.action as object.union(base, {"action_class": "drop_database"})
		with data.containment_maturity as ready
}

test_escalation_trigger_overrides_assignment if {
	not decision.allow with input.action as object.union(base, {"cascading_indicators": ["neighbour pod compromised"]})
		with data.containment_maturity as ready
	"cascading indicators present" in decision.reasons with input.action as object.union(base, {"cascading_indicators": ["x"]})
		with data.containment_maturity as ready
}

test_unverified_rollback_denied if {
	not decision.allow with input.action as object.union(base, {"rollback_verified": false})
		with data.containment_maturity as ready
}

test_level3_denied_when_containment_untested if {
	not decision.allow with input.action as base
		with data.containment_maturity as object.union(ready, {"validation": 1})
}

test_level2_unaffected_by_containment_maturity if {
	decision.allow with input.action as object.union(base, {"requested_level": 2})
		with data.containment_maturity as object.union(ready, {"validation": 1})
}

# Invariants: properties that must survive any edit to the autonomy table.
test_invariant_data_deletion_never_autonomous if {
	policy.autonomy_levels.data_deletion == 1
}

test_invariant_no_class_above_level3 if {
	every _, level in policy.autonomy_levels {
		level <= 3
	}
}
