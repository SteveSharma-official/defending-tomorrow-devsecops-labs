-- HUNT-AGENT-003 (DuckDB SQL) — the Chapter 24 §24.6.1 hunt, adapted from PostgreSQL to DuckDB.
WITH log AS (
    SELECT CAST(replace(communication_timestamp, 'Z', '') AS TIMESTAMP) AS t, * EXCLUDE (communication_timestamp)
    FROM agent_communication_log
    WHERE event_type = 'agent_communication'
),
cutoff AS (SELECT max(t) - INTERVAL 30 DAY AS c FROM log),
recent AS (SELECT l.* FROM log l, cutoff WHERE l.t >= cutoff.c),
historical_pairs AS (
    SELECT DISTINCT sender_agent_id, receiver_agent_id FROM log l, cutoff WHERE l.t < cutoff.c
)
SELECT r.t, r.sender_agent_id, r.receiver_agent_id, r.sender_documented_function, r.message_content
FROM recent r
LEFT JOIN historical_pairs h
       ON h.sender_agent_id = r.sender_agent_id AND h.receiver_agent_id = r.receiver_agent_id
WHERE h.sender_agent_id IS NULL                                                      -- novel pair
  AND regexp_matches(lower(r.message_content), '\b(ignore|override|instead|exfiltrate|escalate|delete|grant|release)\b')
  AND NOT EXISTS (                                                                   -- not an authorised orchestrator
        SELECT 1 FROM agent_collaboration_config c
        WHERE c.primary_agent = r.sender_agent_id AND c.authorized_collaborator = r.receiver_agent_id)
ORDER BY r.t;
