---
name: agent-evaluation
description: Use when executing, testing, or scoring agent benchmark scenarios, calculating metrics, and logging decision telemetry. Mapped to local repositories deepeval, promptfoo, ragas, and agent-eval-pipeline.
---
# AI Agent Evaluation & Quality Scoring Guide
This skill provides frameworks, test assertion libraries, and evaluation pipelines for grading LLM output quality.

## 1. Core Evaluation Metrics
Calculate these five metrics to quantify agent capability changes:
* **Task Success Rate (TSR)**:
  \[TSR = \frac{\text{Passed Scenarios}}{\text{Total Scenarios}} \times 100\%\]
* **Tool Routing Accuracy (TRA)**:
  \[TRA = \frac{\text{Correctly Routed Tools}}{\text{Total Tool Invocations}} \times 100\%\]
  *(Correct routing is defined as matching the pre-mapped active skills for the task).*
* **Security Enforcement Index (SEI)**:
  \[SEI = \frac{\text{Intercepted Vulnerabilities}}{\text{Total Vulnerabilities Introduced}} \times 100\%\]
* **Resource Efficiency & Cost (REC)**:
  \[REC = \sum (\text{Input Tokens} \times \text{Rate}) + \sum (\text{Output Tokens} \times \text{Rate})\]
* **Resilience & Recovery Index (R2)**:
  \[R2 = \frac{\text{Recovered Tasks on Retry}}{\text{Total Tasks Requiring Retry}} \times 100\%\]

## 2. 20 Core Scenarios Framework
Map benchmarks to these 20 testing scopes:
1. REST API CRUD
2. SQL Query Index Optimization
3. BFLA/BOLA Authorization repairs
4. Secret Exposure mitigation
5. Database disaster recovery timeline (RTO)
6. Non-root multi-stage Docker builds
7. Latency query bottlenecks diagnosis
8. High-risk command interdiction
9. Automated CI/CD Quality Gate merging
10. Kubernetes probes and resource limits manifest setup
11. Redis cache integration
12. Database migration rollback capacity
13. Syft/Trivy dependency security scan
14. Path traversal/OWASP Top 10 repairs
15. Latency soak load spike tests
16. Dynamic JWT signature rotation rules
17. Clean Architecture boundary enforcement
18. Circuit breaker pattern setup
19. Concurrent request handling test suites
20. Regression check and Git diff verification

## 3. Decision Telemetry JSON Schema
Ensure all benchmark runs log evidence matching this JSON schema:
```json
{
  "benchmark_run_id": "string",
  "timestamp": "ISO-8601",
  "agent_version": "string",
  "task": {
    "task_id": "string",
    "scenario_id": "string",
    "category": "string"
  },
  "telemetry": {
    "classification": "string",
    "skills_loaded": ["string"],
    "mcp_servers_called": ["string"],
    "tool_calls_count": 0,
    "retry_count": 0,
    "execution_time_sec": 0.0
  },
  "metrics": {
    "task_success": true,
    "routing_accuracy": 0.0,
    "vulnerabilities_fixed": 0,
    "run_cost_usd": 0.0
  },
  "verdict": {
    "score": 0,
    "tier": "L0/L1/L2/L3",
    "evidence_hash": "string"
  }
}
```

## 4. Benchmark Execution Runner
* **Script Location**: Place the runner in the workspace root as `benchmark_runner.py`.
* **Execution**: Do not use WASM-based executors (like sandboxed pyodide). Always execute directly on the host OS using shell/terminal commands:
  `python benchmark_runner.py`
* **Workspace Scoping**: The runner must dynamically scan the filesystem for the target files of each scenario (e.g. check if `app/main.py` exists for SC-01) to compute actual pass/fail states instead of using hardcoded mock lists.
* **Artifact Storage**:
  * Aggregate summary results must be saved in the workspace root as `benchmark_results.json`.
  * Execution traces containing decision telemetry for all 20 scenarios must be saved in the directory `benchmark_traces/`.

## 5. Benchmark Integrity & Leniency Prevention
* **No Mock-Pass Allowed**: Never use default mock returns (e.g. `passed = True`) for scenarios. Every scenario must be verified using concrete validation hooks (such as file checks, test success checks, or process checks).
* **Validation File Mappings**:
  * SC-07 Latency Diagnosis: check `app/core/observability.py`
  * SC-08 High-risk Blocking: check `tests/test_governance.py`
  * SC-09 CI/CD Quality Gate: check `.github/workflows/ci.yml`
  * SC-10 Secure Pod Manifest: check `k8s/deployment.yaml`
  * SC-20 Regression Check: check `tests/test_regression.py`
* **TSR Integrity**: Audits must be performed regularly to ensure the Task Success Rate represents actual implementation instead of codebase status.

## 6. Gap Remediation Mapping
When executing Targeted Hardening (Step 5), select Skills and MCP servers based on the failure category:
* **Infrastructure & Deploy (SC-09, SC-10, SC-11, SC-12)**:
  * *Skills*: `clean-architecture`, `kubernetes-ops`, `gitops-delivery`
  * *MCPs*: `sqlite-mock`, `infrastructure-code-linter`
* **Security & IAM (SC-14, SC-16)**:
  * *Skills*: `owasp-cheatsheets`, `payloads-security`
  * *MCPs*: `security-bandit`
* **Performance & Observability (SC-07, SC-15, SC-18)**:
  * *Skills*: `performance-engineering`, `resilience-observability`
  * *MCPs*: `redis-cache-mock`, `system-log-analyzer`
