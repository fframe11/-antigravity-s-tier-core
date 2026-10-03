---
name: on-call-runbooks
description: Use when creating incident response procedures, runbooks, postmortems, or on-call playbooks. Covers PagerDuty/OpsGenie integration, escalation policies, and structured incident management.
---

# On-Call Runbooks & Incident Management Guide

This skill provides operational protocols for handling production alerts, orchestrating incident responses, configuring escalation policies, structuring runbooks, and leading blameless postmortems.

## When to Use This Skill
- Designing alert-linked runbooks for engineering teams and on-call rotations.
- Establishing incident response protocols, severity tiers, and escalation policies (PagerDuty/OpsGenie).
- Triaging active outages, orchestrating incident roles, and executing rollback decisions.
- Conducting blameless postmortems and tracking preventative action items.
- Structuring on-call shift handoffs and establishing SLI/SLO/SLA baselines.

## Core Principles & Reliability Metrics

### Service Level Definitions
- **SLI (Service Level Indicator)**: Quantifiable real-time metric (e.g., successful request ratio, p99 latency < 250ms).
- **SLO (Service Level Objective)**: Internal reliability target agreed upon with product teams (e.g., 99.9% availability per rolling 30-day window).
- **SLA (Service Level Agreement)**: Contractual commitment with customer penalties for breach (e.g., 99.5% uptime or service credits).
- **Error Budget**: Allowable downtime `(100% - SLO)`. Trigger SEV1 response when 1-hour burn rate consumes > 14.4x of the monthly budget.

### Incident Severity Levels & Response Targets
| Severity | Description | Target Ack | Comms Cadence | Escalation Path |
| :--- | :--- | :--- | :--- | :--- |
| **SEV-1 (Critical)** | Complete service outage, data loss risk, severe business impact. | < 5 mins | Every 15-30 mins | Page Secondary, Eng VP, Execs |
| **SEV-2 (Major)** | Major functionality degraded; no workaround; high customer blast radius. | < 15 mins | Every 30-45 mins | Page Secondary, Tech Lead |
| **SEV-3 (Minor)** | Degraded non-critical feature with viable workaround. | < 1 hour | Daily or at resolve | Slack alert; team queue |
| **SEV-4 (Low)** | Cosmetic bug, minor internal tool issue, zero user impact. | Next business day | On resolution | Backlog ticket |

### Incident Commander (IC) Framework
- **Incident Commander (IC)**: Holds exclusive operational authority. Assigns roles, makes final rollback calls, and prevents distractions. The IC does **not** debug or run commands.
- **Operations / Triage Lead**: Hands on keyboard. Executes diagnostics, mitigations, database isolations, and rollbacks.
- **Communications Lead**: Posts updates to status pages, executive channels, customer support, and partners.

### Escalation Policies (PagerDuty / OpsGenie)
1. **Tier 1 (Primary On-Call)**: Alerted immediately via push/phone. Ack timeout: 5 minutes.
2. **Tier 2 (Secondary / Backup)**: Alerted if Tier 1 does not acknowledge within 10 minutes.
3. **Tier 3 (Engineering Manager / Lead)**: Paged if unacknowledged after 20 minutes.
4. **Heartbeat Monitoring**: Alert routing services must trigger external fallback SMS if health check endpoints fail.

## Implementation Patterns & Concrete Runbooks

### 1. Standard Runbook Template
Every production alert must include a direct URL to a runbook matching this 4-section format:
```yaml
id: RUNBOOK-SVC-REDIS-001
alert_name: RedisMemoryHighUtilization
threshold: "redis_memory_used_bytes / redis_memory_max_bytes > 0.85"
symptoms:
  - Cache writes rejected with OOM command errors
  - API p99 latency spikes from 45ms to 2500ms
diagnosis:
  - Run: "redis-cli -h $REDIS_HOST info memory | grep -E 'used_memory_human|maxmemory_human'"
  - Identify top keys: "redis-cli -h $REDIS_HOST --bigkeys"
mitigation:
  - Scale Redis cluster memory: "aws elasticache modify-cache-cluster --cache-cluster-id auth-cache --cache-node-type cache.r6g.xlarge"
  - Flush volatile evicted keys: "redis-cli -h $REDIS_HOST config set maxmemory-policy allkeys-lru"
resolution:
  - Audit TTL enforcement on caching decorators in authentication service
```

### 2. Common Production Failure Modes & Fast Mitigations

#### Out Of Memory (OOM / Pod Evictions)
```bash
# 1. Identify failing pods and exit code 137 (OOMKilled)
kubectl get pods -n prod -l app=order-api -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[0].lastState.terminated.reason}{"\n"}{end}'

# 2. Mitigate: Scale replicas immediately to spread traffic load and double memory limit
kubectl scale deployment/order-api -n prod --replicas=12
kubectl set resources deployment/order-api -n prod --limits=memory=2Gi --requests=memory=1Gi
```

#### Connection Pool Exhaustion
```sql
-- 1. Identify active long-running queries consuming connections (PostgreSQL)
SELECT pid, now() - query_start AS duration, state, query 
FROM pg_stat_activity 
WHERE state != 'idle' AND (now() - query_start) > interval '10 seconds'
ORDER BY duration DESC;

-- 2. Mitigate: Terminate blocking zombie connections to free up pool capacity
SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
WHERE state = 'idle in transaction' AND (now() - state_change) > interval '30 seconds';
```

#### TLS/SSL Certificate Expiry
```bash
# 1. Check expiration date on production domain
echo | openssl s_client -servername api.example.com -connect api.example.com:443 2>/dev/null | openssl x509 -noout -dates

# 2. Mitigate: Force certbot renewal and perform hot reload of ingress/proxy
certbot renew --force-renewal
kubectl rollout restart deployment/ingress-nginx-controller -n ingress-nginx
```

#### Disk Full (100% Inode / Disk Pressure)
```bash
# 1. Check storage and inode exhaustion
df -h && df -i

# 2. Mitigate: Safely purge rotated logs and dangling container images
journalctl --vacuum-size=500M
docker system prune -af --volumes || crictl rmi --prune
```

### 3. Rollback Decision Framework
Execute immediate rollback when any of the following occur:
- Error rate > 2% for 5 consecutive minutes following deployment.
- Root cause diagnosis exceeds 10 minutes during an active SEV-1/SEV-2.
- Database migration locks core tables and blocks customer transactions.

**Golden Rule:** Mitigate first, diagnose later. Never write unreviewed hotfixes in production during active outages; roll back to the last known healthy release.

### 4. Incident Communication Templates

#### External Status Page
```markdown
**Investigating** (YYYY-MM-DD 14:15 UTC): We are investigating elevated error rates affecting payment processing. Next update in 20 minutes.
**Identified** (YYYY-MM-DD 14:30 UTC): Root cause identified as upstream connectivity timeout. We are shifting traffic to backup routes.
**Monitoring** (YYYY-MM-DD 14:48 UTC): Traffic shifted. Error rates dropped below 0.05%. We are monitoring system stability.
**Resolved** (YYYY-MM-DD 15:10 UTC): Incident resolved. A blameless postmortem will be completed within 48 hours.
```

#### Internal Slack Incident Channel
```markdown
:rotating_light: *INCIDENT STATUS UPDATE - SEV-1* :rotating_light:
- **Incident Commander:** @alice | **Ops Lead:** @bob | **Comms Lead:** @charlie
- **Impact:** ~35% of checkout requests failing with HTTP 504.
- **Current Hypothesis:** DB connection starvation following release v2.14.0.
- **Immediate Action:** Initiated rollback of release v2.14.0 to v2.13.4.
- **Next Sync:** Live video conference at :30 past the hour.
```

### 5. Blameless Postmortem Template
```markdown
# Incident Postmortem: [SEV-1] Checkout Outage - YYYY-MM-DD

**Date & Duration:** YYYY-MM-DD (42 minutes)  
**Incident Commander:** @alice  
**SLO Impact:** 0.08% monthly error budget consumed  

## Executive Summary
Between 14:10 UTC and 14:52 UTC, checkout transactions failed due to database connection exhaustion following release v2.14.0. Service was restored by rolling back to v2.13.4 and clearing idle connection pools.

## Incident Timeline (UTC)
- 14:10: Deployment v2.14.0 completes.
- 14:14: PagerDuty triggers: `CheckoutLatencyP99High`.
- 14:17: IC declares SEV-1; spins up `#inc-20260921-checkout`.
- 14:25: Ops Lead identifies missing database index on `orders` table.
- 14:32: IC orders rollback to v2.13.4.
- 14:45: Rollback complete; connection pool recovers.
- 14:52: Error rate returns to 0.01%. Incident resolved.

## Root Cause & 5-Whys
1. Why did checkout fail? Database connection pool exhausted.
2. Why was the pool exhausted? Queries hung waiting on sequential scans on `orders`.
3. Why did queries scan sequentially? Index migration was omitted from the release bundle.
4. Why did staging tests not catch it? Staging seed database was too small to expose table scans.
5. Why was deployment permitted? CI lacked query plan regression checks on migrations.

## Preventative Action Items
| Action Item | Type | Owner | Target Date | Ticket |
| :--- | :--- | :--- | :--- | :--- |
| Add `EXPLAIN ANALYZE` linting in CI for migrations | Prevent | @bob | 2026-09-30 | REL-402 |
| Enforce `statement_timeout = 3000ms` on web pools | Mitigate | @alice | 2026-09-25 | DB-119 |
| Automate rollback when p99 latency > 2s for 3 mins | Mitigate | @devops | 2026-10-05 | REL-405 |
```

### 6. On-Call Shift Handoff Process
Conduct a weekly structured handoff covering:
1. **Alert Volume Review**: Review paging volume, false positives, and flaky alerts needing threshold adjustments.
2. **In-Flight Incidents**: Review open SEV-3 tickets and temporary workarounds awaiting permanent fixes.
3. **Upcoming Changes**: Brief the incoming engineer on planned deployments, migrations, or maintenance windows.
4. **Credential & Tooling Check**: Verify incoming engineer has active VPN access, bastion tokens, and PagerDuty overrides.

## Anti-Patterns to Avoid
- **Debugging in Production During Outages**: Attempting to inspect code live rather than immediately mitigating impact via rollback or traffic shifting.
- **Blame-Centric Postmortems**: Asking "Who broke this?" instead of "What systemic guardrail or automated check was missing?"
- **Unlinked Alerts**: Sending alerts without a direct link to an actionable, tested runbook.
- **Alert Desensitization**: Ignoring noisy non-actionable alarms instead of tuning thresholds or deleting them.
- **Solo Heroics**: Engineers making rogue production changes without coordinating through the Incident Commander.

## Verification Checklist
- [ ] Every alert in PagerDuty/OpsGenie links directly to a documented runbook URL.
- [ ] Runbooks contain verified diagnosis commands and copy-paste mitigation steps.
- [ ] Incident commander roles (IC, Ops, Comms) are trained and tested in GameDay simulations.
- [ ] Rollback thresholds (error rate %, latency, diagnosis timeout) are predefined.
- [ ] Postmortem meetings are held within 48-72 hours of any SEV-1 or SEV-2 incident.
- [ ] Shift handoff log is completed and acknowledged by the incoming engineer every rotation.
