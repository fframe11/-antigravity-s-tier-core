---
name: human-review
description: Use when reviewing completed code, git diffs, or proposing changes in plain, human-friendly language. Translates technical jargon into crystal-clear explanations of what changed, why it matters, trade-offs, and next actions without robotic fluff.
metadata:
  tags: "code-review, human-readable, diff, PR, explanation, communication"
  category: "productivity"
---
# Human-Friendly Code Review & Diff Translation

## Purpose
Transform technical git diffs, code changes, and architecture decisions into explanations that any team member (including non-technical stakeholders) can understand. Focus on **impact**, not implementation details.

## 1. Diff Review Structure
When reviewing a git diff or set of changes, organize the review into these sections:

### Section A: What Changed (1-2 sentences)
- State the **business purpose** of the change, not the technical details
- Example: "Added rate limiting to the login endpoint to prevent brute-force attacks" (not "Added ThrottlerGuard decorator to AuthController.login()")

### Section B: Why It Matters
- **For the user**: How does this affect the end user experience?
- **For the system**: How does this affect reliability, security, or performance?
- **For the team**: How does this affect developer experience or maintenance?

### Section C: What Could Go Wrong
- Identify the **blast radius** — how many users/services are affected if this breaks
- Flag **one-way door decisions** (irreversible changes like DB migrations, API contract breaks)
- Note **two-way door decisions** (easily reversible changes like config tweaks, feature flags)

### Section D: Confidence Level
Rate your confidence in the change:
- 🟢 **High**: Standard patterns, good test coverage, low risk
- 🟡 **Medium**: New patterns, partial test coverage, moderate risk
- 🔴 **Low**: Complex logic, no tests, high blast radius, or unfamiliar domain

### Section E: Recommended Actions
- What should be done **before merging** (fix bugs, add tests, update docs)
- What should be done **after merging** (monitor metrics, communicate to team, update runbooks)

## 2. Communication Rules

### Use Plain Language
| ❌ Don't Say | ✅ Do Say |
|---|---|
| "Refactored the middleware pipeline" | "Changed the order of checks when a request comes in" |
| "Applied the strategy pattern" | "Made it easy to swap out payment providers without changing the checkout code" |
| "Implemented transactional outbox" | "Made sure the database update and the notification always happen together — if one fails, both fail" |
| "Fixed N+1 query" | "The page was making 100 database calls instead of 1 — now it makes 1" |
| "Added BOLA prevention" | "Added a check so users can only see their own data, not other people's" |

### Quantify Impact When Possible
- "This will reduce page load from ~3 seconds to ~200ms"
- "This affects all 50,000 daily login attempts"
- "This migration will lock the users table for ~30 seconds during deploy"
- "Without this fix, an attacker could access any user's data by changing the ID in the URL"

### Flag Non-Obvious Risks
- Race conditions in concurrent operations
- Missing error handling paths (what happens when the external API times out?)
- Implicit assumptions (this code assumes users table has < 1M rows)
- Environment differences (works locally but Cloud Run has different file system)

## 3. PR Description Template
```markdown
## What
[1-2 sentences: what business problem this solves]

## Why Now
[Why this change is needed now, not later]

## How It Works
[Simple explanation of the approach, written for someone who hasn't seen the code]

## What Could Break
[Blast radius, rollback plan, monitoring to watch]

## Testing Done
[What was tested, how, and what the results were]

## Screenshots / Evidence
[Before/after, test output, API response examples]
```

## 4. Review Checklist for Reviewers
When reviewing someone else's code, check:
- [ ] Can I explain what this PR does in one sentence?
- [ ] Are there tests that would catch a regression if I reverted this?
- [ ] Would this change survive a restart? (No in-memory state lost)
- [ ] What happens if the external service this calls is down?
- [ ] Are there any new environment variables or secrets needed?
- [ ] Is there a rollback plan documented?

## 5. Escalation Triggers
Flag for senior review if:
- Change touches authentication, authorization, or payment logic
- Database migration that alters existing columns/constraints
- Breaking change to a public API contract
- New infrastructure dependency (new database, new queue, new external service)
- Change that requires coordinated deployment across multiple services
