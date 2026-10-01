# Governance-Containment Maturity Matrix gate — Chapter 33 §33.4.3.
# Level 3 (act with rollback) is permitted only when every containment dimension is at least the middle level.
package remediation.containment

import rego.v1

dimensions := {"visibility", "revocation", "preservation", "validation"}

gaps contains sprintf("%s is at level %d (minimum 2)", [d, level]) if {
	some d in dimensions
	level := object.get(data.containment_maturity, d, 0)
	level < 2
}

level3_ready if count(gaps) == 0
