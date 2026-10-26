---
name: paep-long-loop-manager
description: Plan bounded multi-stage engineering loops with owners, evidence gates and explicit stop conditions for PAEP tasks.
metadata:
  version: 1.1.0
  owner: paep-user
  category: project
---

# paep-long-loop-manager

Translate the goal into stages with observable evidence, a current owner and a stop condition. State completion criteria and failure/blocked outcomes for each stage. Require review before scope or permissions expand. Recommend the next stage based on actual evidence; elapsed time alone never proves completion. Produce a loop plan, not an autonomous infinite retry or background scheduler.

## Inputs

- `repository_path` (required, path): absolute project directory within configured PAEP roots. Read-only.
- `brief` (optional, string): the goal to decompose, plus any interruption/resumption record to plan from.

## Output

`artifacts/long-loop-report.md` — the loop plan in the structure below.

## Stage structure

Every stage in the plan carries all five fields; a stage missing any field is not plannable:

```text
Stage N — <name>
  entry evidence : what recorded facts authorize starting this stage
  work           : what is done, within which exact paths/permissions
  exit evidence  : artifacts/checks that must exist afterwards, with locations
  owner          : one executor or approver
  stop condition : proceed / blocked / fail — each defined by observable evidence
```

Stages form a sequence the reader can resume; no stage may depend on evidence that does not yet have a planned location.

## Handoff inputs

A loop handoff (to the next executor or the next session) must carry:

1. The plan artifact path and its digest or the plan section quoted verbatim.
2. Last completed stage with its exit evidence paths.
3. Current stage and the exact point of interruption, if any.
4. Permissions already granted and their exact scope (paths, allowed operations).
5. Items explicitly left undecided, with the decision owner.

The receiving side re-derives state from these inputs; if any of the five is missing, record `HANDOFF_INCOMPLETE` and stop — do not guess.

## Recovery checks

When planning resumption from an interruption record, verify before recommending continuation:

- The claimed last-completed stage's exit evidence exists on disk at the recorded paths (check, don't trust the record).
- No stage marked completed has later-modified inputs that invalidate its evidence.
- Permissions and approvals named in the plan are still the ones in force.
- A plan that says a stage ran is not evidence the stage ran; only exit evidence is.

If verification fails, the recovery plan starts at re-verification of that stage, not at the next stage.

## Stop conditions

The whole loop stops, and says so in the report, when any of these holds:

- All stages have exit evidence recorded and verified.
- A stop condition fires and its blocked/fail branch is confirmed by evidence.
- Scope, permissions or budget would need to expand beyond the approved plan.
- Remaining work needs a decision that no recorded authority grants.

Elapsed time, retry counts and monitor cycles are never stop-or-continue evidence by themselves.

## Example invocation

```markdown
# Goal
Resume the paused V17 monitoring loop from its interruption record without
treating the plan as executed.

# Context
Interruption record and last checkpoint live under the repository.

# Constraints
Read-only; produce a plan; no automation may be created by this task.

# Acceptance criteria
- Every stage has entry/exit evidence, owner and stop condition.
- Recovery checks verify claimed completion against on-disk evidence.
```

## Combination with professional skills

Use `paep-project-manager` output as the entry evidence for stage 1; hand implementation stages to `paep-agent-handoff` packages; use `debugging-strategies` for failure-branch investigation and `experimental-design` for validation stages. The loop plan references them; it does not restate their procedures.

## Handoff convention

The plan artifact is the single source for loop state. Later executors append progress records beside it (never edit the plan retroactively); a stage is complete only when its exit evidence paths are recorded next to the plan and verifiable.

## Execution boundary

Use the PAEP task/result protocol and the declared Markdown output in skill.yaml.
The runtime uses a reviewed external codex handoff. Writes, network,
shell commands, credentials and production mutations are outside this skill's
permissions. If evidence is missing, report it and stop; do not broaden access.
