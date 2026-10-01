# Staged Autonomy Model enforcement — Chapter 33 §33.6.2 listing (formatted with opa fmt; logic unchanged).

package remediation.policy

import rego.v1

# Maximum autonomy level permitted per action class (Chapter 33 staged autonomy model).
autonomy_levels := {
	"credential_revocation": 3,
	"workload_isolation": 3,
	"deployment_rollback": 3,
	"agent_credential_revocation": 3,
	"firewall_rule_change": 2,
	"iam_policy_change": 2,
	"network_segment_isolation": 2,
	"data_deletion": 1,
}

# Maximum number of affected entities per autonomous action.
blast_radius_limits := {
	"credential_revocation": 1,
	"workload_isolation": 1,
	"network_segment_isolation": 1,
	"deployment_rollback": 1,
}

default allow := false

allow if {
	count(escalations) == 0
	input.action.requested_level <= autonomy_levels[input.action.action_class]
	input.action.affected_count <= object.get(blast_radius_limits, input.action.action_class, 0)
	input.action.rollback_verified == true
}

escalations contains "session exceeded 5 accumulated actions" if input.action.accumulated_actions > 5

escalations contains "session exceeded 30 minutes" if input.action.session_duration_seconds > 1800

escalations contains "previous rollback failed" if input.action.previous_rollback_failed == true

escalations contains "cascading indicators present" if count(input.action.cascading_indicators) > 0
