# The decision the remediation agent receives: the §33.6.2 autonomy policy, plus the §33.4.3 containment
# prerequisite for Level 3 and above.
package remediation.decision

import data.remediation.containment
import data.remediation.policy
import rego.v1

default allow := false

allow if {
	policy.allow
	input.action.requested_level < 3
}

allow if {
	policy.allow
	input.action.requested_level >= 3
	containment.level3_ready
}

reasons contains r if some r in policy.escalations

reasons contains "requested level exceeds the level assigned to this action class" if {
	input.action.requested_level > object.get(policy.autonomy_levels, input.action.action_class, 0)
}

reasons contains "blast radius exceeds the limit for this action class" if {
	input.action.affected_count > object.get(policy.blast_radius_limits, input.action.action_class, 0)
}

reasons contains "rollback not verified" if input.action.rollback_verified != true

reasons contains sprintf("containment not ready for Level 3: %s", [g]) if {
	input.action.requested_level >= 3
	some g in containment.gaps
}
