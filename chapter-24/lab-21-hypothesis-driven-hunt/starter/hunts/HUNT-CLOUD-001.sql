-- HUNT-CLOUD-001 (DuckDB SQL): principal acting from an IP it has not used in the prior 14 days.
WITH events AS (
    SELECT CAST(replace(eventTime, 'Z', '') AS TIMESTAMP) AS t, userName, sourceIPAddress, eventName, errorCode
    FROM cloudtrail
),
first_seen AS (
    SELECT userName, sourceIPAddress, min(t) AS first_t
    FROM events
    GROUP BY ALL
),
baseline_start AS (
    SELECT min(t) + INTERVAL 14 DAY AS hunt_from FROM events
)
SELECT e.t, e.userName, e.sourceIPAddress, e.eventName, e.errorCode
FROM events e
JOIN first_seen f USING (userName, sourceIPAddress)
CROSS JOIN baseline_start b
WHERE f.first_t >= b.hunt_from                -- this user/IP pair is new after the baseline period
ORDER BY e.t;
