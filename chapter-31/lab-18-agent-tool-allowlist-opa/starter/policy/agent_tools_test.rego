package agent.tools_test

import rego.v1

import data.agent.tools

req(agent, tool, params) := {"agent_id": agent, "tool": tool, "params": params, "session": {"calls_last_hour": 1}}

test_permitted_read_tool_is_allowed if {
	tools.allow with input as req("support-agent-v1", "orders.lookup", {"customer": "alice"})
}

test_tool_outside_allowlist_is_denied if {
	not tools.allow with input as req("support-agent-v1", "orders.delete", {"customer": "alice"})
}

test_injection_in_parameter_is_denied if {
	not tools.allow with input as req("support-agent-v1", "orders.lookup", {"customer": "alice' OR '1'='1"})
}

test_unexpected_parameter_is_denied if {
	not tools.allow with input as req("support-agent-v1", "kb.search", {"export_all": true})
}

test_unknown_agent_is_denied if {
	"unknown agent identity" in tools.deny_reasons with input as req("shadow-agent", "kb.search", {})
}

test_write_without_approval_is_denied if {
	not tools.allow with input as req("support-agent-v1", "tickets.comment", {"ticket_id": "TCK-42"})
}

test_write_with_approval_is_allowed if {
	tools.allow with input as object.union(req("support-agent-v1", "tickets.comment", {"ticket_id": "TCK-42"}), {"approval": {"approved_by": "analyst@example.com"}})
}

test_rate_limit_is_enforced if {
	not tools.allow with input as object.union(req("support-agent-v1", "orders.lookup", {"customer": "bob"}), {"session": {"calls_last_hour": 200}})
}

test_rollback_outside_allowed_namespace_is_denied if {
	not tools.allow with input as object.union(req("remediation-agent-v1", "k8s.rollback_deployment", {"namespace": "production"}), {"approval": {"approved_by": "sre@example.com"}})
}

test_no_wildcard_bindings if {
	count(tools.wildcard_bindings) == 0
}
