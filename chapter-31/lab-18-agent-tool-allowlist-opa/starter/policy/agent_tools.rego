# LAB-18 — per-agent tool allowlist evaluated at the MCP gateway (Chapter 31 §31.5; corrected Chapter 0 listing).
# Default deny; every allow is explained; every deny carries a reason for the decision log.
package agent.tools

import rego.v1

default allow := false

binding := data.bindings[input.agent_id]

tool_spec := binding.tools[input.tool]

allow if count(deny_reasons) == 0

deny_reasons contains "unknown agent identity" if not binding

deny_reasons contains sprintf("tool '%s' is not in the allowlist for %s", [input.tool, input.agent_id]) if {
	binding
	not tool_spec
}

deny_reasons contains sprintf("parameter '%s' is not permitted for tool '%s'", [name, input.tool]) if {
	some name, _ in input.params
	tool_spec
	not tool_spec.params[name]
}

deny_reasons contains sprintf("parameter '%s' value is outside its allowed scope", [name]) if {
	some name, value in input.params
	constraint := tool_spec.params[name]
	not satisfies(value, constraint)
}

deny_reasons contains "rate limit exceeded for this tool" if {
	input.session.calls_last_hour >= tool_spec.max_calls_per_hour
}

deny_reasons contains "write action requires recorded human approval" if {
	tool_spec.write
	not input.approval.approved_by
}

satisfies(value, constraint) if regex.match(constraint.pattern, sprintf("%v", [value]))

satisfies(value, constraint) if value in constraint.allowed

# Governance invariant checked in CI: no binding may grant wildcard tools.
wildcard_bindings contains agent if {
	some agent, b in data.bindings
	some tool, _ in b.tools
	contains(tool, "*")
}
