---
name: agent-governance
description: Use to check authorization, assess risks, audit permissions, enforce the E2E verification loop, retry limits, and production hardening constraints.
---
# AI Agent Governance & Safety Guide
This skill governs safe execution of actions and tool interactions in Antigravity.

## 1. Risk Classification Matrix
Prior to calling any tool or command, classify the risk level:
* **READ (Low Risk)**: File reading, log inspection, status checks. *Action: Auto-execute.*
* **ANALYZE (Medium Risk)**: Running brainstorm tools, diagram designers. *Action: Auto-execute.*
* **WRITE/MODIFY (High Risk)**: Editing source files or configurations. *Action: Auto-execute only after verifying the target scope and blast radius. For changes to production, infrastructure, security, CI/CD, or critical configurations that can materially affect availability, security, or deployment behavior, require additional verification and human approval.*
* **DELETE / DEPLOY (Critical Risk)**: Dropping production databases, deploying services, formatting system drives, running host-level system-wide operations (like `docker system prune -a --volumes -f`), or other host-level/production-impacting actions. (Safe local cleanup of disposable test resources, like local test container removal, is excluded). *Action: MUST halt execution and request explicit user confirmation in the chat.*

## 2. Post-Execution Verification Loop
Do not claim task completion immediately after coding. You MUST execute the following verification loop:
1. **Test**: Run automated test suites (e.g., pytest).
2. **Security Scan**: Run security scans (e.g., Bandit, OWASP checklists).
3. **Diff Review**: Review diffs (e.g., git diff status) to verify no unrelated changes were made.
4. **Retry Limit**: If verification fails, diagnose and retry. Limit automatic retries to a **maximum of 3 attempts**. If it still fails, stop execution, report the root cause, and request human intervention.

## 3. The 5 Production Hardening Pillars (measurable DoD)
When preparing applications for production, adhere to these strictly:
1. **Supply-Chain Security**:
   * Generate Software Bill of Materials (SBOM) using tools like Syft.
   * Perform container image vulnerability scans (e.g., Trivy).
   * Check dependencies for licensing compliance and secrets leakage.
2. **CI/CD Quality Gate**:
   * Enforce quality gates where failures in tests or security scans block merging.
3. **Kubernetes Production Layer**:
   * Ensure K8s manifests include resource Requests/Limits, Liveness/Readiness Probes, NetworkPolicies, Horizontal Pod Autoscalers (HPA), and PodDisruptionBudgets (PDB).
4. **Agent Evaluation Benchmark**:
   * Test changes against a standard benchmark of 20–50 scenarios.
   * Collect metrics: Task Success Rate, Tool Routing Accuracy, Security Detection Rate, Retry Rate.
5. **Agent Decision Observability**:
   * Collect decision trace telemetry (Task Classification -> Selected Skills -> Selected MCP -> Tool Calls -> Retry Count) via OpenTelemetry.

## 4. Data-Driven Expansion Principle
* **No New Skills or MCPs Without Benchmark Evidence**: Do not add random tools or skills. Only add or update capabilities when benchmarking proves it provides a measurable improvement in task success rate or latency reduction.
