# Subagent Architecture Migration Specification

**Status:** Draft
**Author:** Claude Code
**Date:** 2025-01-28
**Version:** 1.0

---

## Executive Summary

The pbi-squire-plugin has a sophisticated orchestration system using a **Task Blackboard pattern** (findings.md), but its "agents" are **persona documents** rather than actual Claude Code subagents. This means everything runs in one conversation context, leading to context rot. The reference architecture (claude-sub-agent) demonstrates how to use **actual isolated subagents** with fresh contexts, skill injection, and hooks.

---

## Side-by-Side Comparison

| Aspect | Reference Architecture (claude-sub-agent) | Current pbi-squire | Gap |
|--------|-------------------------------------------|------------------------|-----|
| **Agent Definition** | `.claude/agents/*.md` with frontmatter (actual subagents) | `skills/.../agents/*.md` (persona docs) | **CRITICAL** - Not real subagents |
| **Context Isolation** | Each subagent has fresh context window | All runs in main conversation | Context rot issue |
| **Skill Injection** | `skills:` field loads knowledge into subagent | Skills load into main context | No selective loading |
| **Orchestrator** | Dedicated `spec-orchestrator.md` agent | Workflow documents (implicit) | Works, but verbose |
| **Memory Pattern** | Directory of typed artifacts (`docs/YYYY_MM_DD/specs/`) | Single findings.md with sections | Similar concept, different structure |
| **Quality Gates** | Explicit thresholds (95%, 80%, 75%) | Pass/Fail only | No threshold tuning |
| **Hooks** | `SubagentStart`/`SubagentStop` hooks | `state_manage.ps1` (manual) | Not integrated with Claude Code hooks |
| **Phase Control** | `--phase=planning\|development\|validation` | Implicit in workflow logic | Less flexible |
| **Skip Agents** | `--skip-agent=[name]` | Not supported | No bypass mechanism |

---

## Architecture Diagrams

### Current Architecture (Context Rot Problem)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MAIN CONVERSATION CONTEXT                        │
│  (Everything accumulates here - context rot over long workflows)    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐            │
│  │ SKILL.md     │   │ workflow.md  │   │ agent1.md    │            │
│  │ (loaded)     │   │ (loaded)     │   │ (persona)    │            │
│  └──────────────┘   └──────────────┘   └──────────────┘            │
│                                                                     │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐            │
│  │ agent2.md    │   │ agent3.md    │   │ references   │            │
│  │ (persona)    │   │ (persona)    │   │ (loaded)     │            │
│  └──────────────┘   └──────────────┘   └──────────────┘            │
│                                                                     │
│  + All tool outputs + All file reads + All user messages           │
│  = CONTEXT GROWS UNBOUNDED                                          │
│                                                                     │
│                         ┌─────────────────┐                        │
│                         │  findings.md    │                        │
│                         │  (blackboard)   │                        │
│                         └─────────────────┘                        │
└─────────────────────────────────────────────────────────────────────┘
```

### Target Architecture (Isolated Subagents)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MAIN CONVERSATION (Orchestrator)                 │
│  Loads: SKILL.md + workflow.md only (minimal context)               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Phase 1: Spawn Investigation Subagent(s)                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Task(powerbi-code-locator)     Task(powerbi-visual-locator) │   │
│  │ - Fresh context                - Fresh context              │   │
│  │ - skills: [pbi-squire]    - skills: [pbi-squire]  │   │
│  │ - tools: [Read, Glob, Grep]    - tools: [Read, Glob, Grep]  │   │
│  │ - Writes: Section 1.A          - Writes: Section 1.B        │   │
│  │ - Returns: summary             - Returns: summary           │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ↓                                      │
│  Phase 2: Spawn Planning Subagent                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Task(powerbi-dashboard-planner)                             │   │
│  │ - Fresh context (no investigation noise)                    │   │
│  │ - skills: [pbi-squire]                                 │   │
│  │ - Reads: Section 1.A, 1.B from findings.md                  │   │
│  │ - Writes: Section 2                                         │   │
│  │ - Returns: summary                                          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ↓                                      │
│  Phase 3: Spawn Validation Subagent(s) in PARALLEL                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Task(powerbi-dax-reviewer)     Task(powerbi-pbir-validator) │   │
│  │ - Fresh context                - Fresh context              │   │
│  │ - Reads: Section 2.A           - Reads: Section 2.B         │   │
│  │ - Writes: Section 2.5          - Writes: Section 2.6        │   │
│  │ - Returns: PASS/FAIL + issues  - Returns: PASS/FAIL         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ↓                                      │
│                    findings.md (shared blackboard)                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Reference Architecture: Three-Phase Pipeline

From [claude-sub-agent](https://github.com/zhsama/claude-sub-agent):

```
Phase 1: PLANNING (Quality Gate: 95%)
├── spec-analyst      → requirements.md, user-stories.md
├── spec-architect    → architecture.md, api-specs.md
└── spec-planner      → task-breakdown.md, test-plan.md

Phase 2: DEVELOPMENT (Quality Gate: 80%)
├── spec-developer    → source code, unit tests
└── spec-tester       → test suites, coverage reports

Phase 3: VALIDATION (Quality Gate: configurable)
├── spec-reviewer     → code review, improvement suggestions
└── spec-validator    → production readiness check
```

**Key Patterns:**
1. **Artifact-driven communication** - Agents produce typed documents, not sections in one file
2. **Quality gates with thresholds** - 95% for planning, 80% for development
3. **Orchestrator agent** - Manages flow, triggers feedback loops on gate failures
4. **Hooks integration** - SubagentStart/Stop for setup/cleanup

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Memory pattern | **findings.md** (single file) | Proven pattern, simpler, subagents read/write sections |
| Delivery mechanism | **Plugin agents/ directory** | Auto-registered, centralized updates, clean for users |
| Orchestrator | **Dedicated orchestrator agent** | Single agent manages phases, spawns subagents, checks gates |
| Conversion scope | **All 22 agents** | Full context isolation, maximum benefit |
| Directory structure | **Subdirectories** (agents/analyst/, agents/developer/) | Clear Core/Pro separation, easy gitignore |

---

## Critical: Core vs Developer Edition Architecture

The plugin uses **two repositories** with cascading branches:

```
Public (Analyst):  cn-dataworks/pbi-squire-plugin     → main branch
Private (Developer):  cn-dataworks/pbi-squire-pro-plugin → pro branch

Changes flow: main → pro (never reverse)
Pro is a SUPERSET of Core
```

### Agent Classification

| Agent | Edition | Category |
|-------|---------|----------|
| powerbi-orchestrator | **Core** | Orchestrator (edition-aware) |
| powerbi-code-locator | Core | Investigation |
| powerbi-visual-locator | Core | Investigation |
| powerbi-data-context-agent | Core | Investigation |
| powerbi-pattern-discovery | Core | Investigation |
| powerbi-dashboard-update-planner | Core | Planning |
| powerbi-dax-specialist | Core | Specialist |
| powerbi-mcode-specialist | Core | Specialist |
| powerbi-dax-review-agent | Core | Validation |
| powerbi-pbir-validator | Core | Validation |
| powerbi-artifact-decomposer | Core | Planning |
| powerbi-data-understanding-agent | Core | Planning |
| powerbi-page-layout-designer | Core | Specialist |
| powerbi-interaction-designer | Core | Specialist |
| powerbi-visual-type-recommender | Core | Planning |
| powerbi-code-implementer-apply | Core | Execution |
| powerbi-visual-implementer-apply | Core | Execution |
| powerbi-code-understander | Core | Analysis |
| powerbi-compare-project-code | Core | Merge |
| power-bi-verification | Core | Validation |
| powerbi-template-harvester | Core | Utility |
| powerbi-pbir-page-generator | Core | Specialist |
| **powerbi-playwright-tester** | **PRO** | Testing |
| **powerbi-ux-reviewer** | **PRO** | QA |
| **powerbi-qa-inspector** | **PRO** | QA |

### Directory Structure with Edition Split

```
pbi-squire-plugin/
├── agents/                          # Plugin subagents (auto-registered)
│   ├── core/                        # Core agents (in both repos)
│   │   ├── powerbi-orchestrator.md
│   │   ├── powerbi-code-locator.md
│   │   ├── powerbi-dax-specialist.md
│   │   └── ... (20 core agents)
│   │
│   └── pro/                         # Pro agents (private repo only)
│       ├── powerbi-playwright-tester.md
│       ├── powerbi-ux-reviewer.md
│       └── powerbi-qa-inspector.md
│
├── skills/
│   └── pbi-squire/
│       ├── SKILL.md
│       └── developer-features.md          # Developer-only (gitignored on main)
│
└── .gitignore                       # On main: ignores agents/developer/*
```

---

## Proposed Phase Structure

```
PHASE 1: INVESTIGATION (Parallel subagents)
├── powerbi-code-locator        → Section 1.A
├── powerbi-visual-locator      → Section 1.B
├── powerbi-data-context-agent  → Section 1.C (Data Context)
└── powerbi-pattern-discovery   → Section 1.D (Patterns)
    Quality Gate: All sections populated or N/A

PHASE 2: PLANNING (Sequential, unified)
├── powerbi-dashboard-planner   → Section 2 (reads all of Section 1)
│   ├── Invokes powerbi-dax-specialist if DAX needed
│   └── Invokes powerbi-mcode-specialist if M code needed
    Quality Gate: Section 2 complete with valid structure

PHASE 3: VALIDATION (Parallel subagents)
├── powerbi-dax-review-agent    → Section 2.5 (if Section 2.A exists)
├── powerbi-pbir-validator      → Section 2.6 (if Section 2.B exists)
└── tmdl-format-validator       → Section 2.7 (tool, not agent)
    Quality Gate: All PASS (threshold: 100% for validation)

PHASE 4: IMPLEMENTATION (Sequential)
├── powerbi-code-implementer    → Section 4.A
└── powerbi-visual-implementer  → Section 4.B
    Quality Gate: Changes applied successfully

PHASE 5: TESTING (Optional, Pro only)
└── powerbi-playwright-tester   → Section 5
    Quality Gate: Test pass rate >= threshold
```

---

## Agent Conversion Template

### Current Format (Persona Doc)

Location: `skills/pbi-squire/agents/powerbi-visual-locator.md`

```markdown
---
name: powerbi-visual-locator
description: Use this agent to identify...
model: sonnet
thinking:
  budget_tokens: 16000
color: purple
---
[800+ lines of instructions]
```

### Target Format (Actual Subagent)

Location: `agents/analyst/powerbi-visual-locator.md`

```markdown
---
name: powerbi-visual-locator
description: Locate and document PBIR visuals. Use when investigating visual changes.
model: sonnet
tools: Read, Glob, Grep
skills:
  - pbi-squire
color: purple
---

You are a PBIR Visual Locator subagent.

## Task Memory
- **Input:** Read task prompt for findings.md path and search criteria
- **Output:** Write to Section 1.B of findings.md

## Your Expertise
[CONDENSED - 100-200 lines max, key patterns only]

## Quality Checklist
Before returning:
- [ ] Visual identified with exact path
- [ ] Current properties documented
- [ ] Section 1.B written to findings.md
```

### Key Changes

1. Add `tools:` field (explicit tool access)
2. Add `skills:` field (injects pbi-squire knowledge)
3. Remove `thinking:` (not needed for subagents)
4. Condense instructions (skill provides base knowledge)
5. Add clear input/output contract

---

## Orchestrator Agent Specification

**File:** `agents/analyst/powerbi-orchestrator.md`

```markdown
---
name: powerbi-orchestrator
description: Orchestrate Power BI workflows. Use for evaluate, create, implement, merge commands. Spawns specialized subagents and manages quality gates.
model: sonnet
tools: Read, Write, Edit, Task, Glob, Grep, Bash
skills:
  - pbi-squire
color: blue
---

You are the Power BI Orchestrator. You manage multi-phase workflows by spawning
specialized subagents and coordinating their work through a shared findings.md file.

## Workflow Commands You Handle

| Command | Phases |
|---------|--------|
| /evaluate-pbi-project-file | Investigation → Planning → Validation |
| /create-pbi-artifact-spec | Decomposition → Specification → Planning → Validation |
| /implement-deploy-test | Implementation → Testing |
| /merge-powerbi-projects | Comparison → Analysis → Merge |

## Edition Detection

On startup, check for Pro agents:
1. Check if `agents/developer/` directory exists and has files
2. OR check for Pro indicators in skill config
3. Set `edition = "pro"` or `edition = "core"`

## Phase Execution Pattern

### Phase 1: Setup
1. Create timestamped scratchpad: `agent_scratchpads/YYYYMMDD-HHMMSS-<name>/`
2. Create findings.md with Problem Statement
3. Classify change type: calc_only | visual_only | hybrid

### Phase 2: Investigation (PARALLEL subagents)
IF calc_only or hybrid:
  Task(powerbi-code-locator) → Section 1.A
IF visual_only or hybrid:
  Task(powerbi-visual-locator) → Section 1.B
IF data context needed:
  Task(powerbi-data-context-agent) → Section 1.C

**Quality Gate:** All required sections populated

### Phase 3: Planning (SEQUENTIAL)
Task(powerbi-dashboard-planner)
  - Reads: Section 1.*
  - Writes: Section 2
  - May invoke: powerbi-dax-specialist, powerbi-mcode-specialist

**Quality Gate:** Section 2 complete with valid structure

### Phase 4: Validation (PARALLEL subagents)
IF Section 2.A exists:
  Task(powerbi-dax-reviewer) → Section 2.5
IF Section 2.B exists:
  Task(powerbi-pbir-validator) → Section 2.6
ALWAYS:
  Run tmdl_format_validator.py

**Quality Gate:** All validators PASS

### Phase 5: Completion
- Display findings.md path
- Suggest next command (/implement-deploy-test)

## Subagent Invocation Pattern

When spawning subagents, provide:
1. Task memory path: `findings.md`
2. Input section to read
3. Output section to write
4. Specific task context

Example:
Task(powerbi-code-locator):
  "Locate DAX code for the measure mentioned in the Problem Statement.
   Task memory: agent_scratchpads/20250128-143000-fix-yoy/findings.md
   Read: Problem Statement
   Write: Section 1.A"

## Quality Gate Checks

After each phase, verify:
1. Read findings.md
2. Check expected sections exist
3. Parse for PASS/FAIL verdicts
4. If FAIL: Report specific errors, halt workflow
5. If PASS: Proceed to next phase

## Error Handling

- If subagent fails: Read its error, add to findings.md Section 9: Errors
- If quality gate fails: Present errors to user, offer retry option
- If user abandons: Archive findings.md with ABANDONED status
```

---

## Hooks Configuration

**File:** `.claude-plugin/hooks.json`

```json
{
  "hooks": {
    "SubagentStart": [
      {
        "matcher": "powerbi-.*",
        "hooks": [
          {
            "type": "command",
            "command": "pwsh -File tools/hooks/on-subagent-start.ps1 $AGENT_NAME"
          }
        ]
      }
    ],
    "SubagentStop": [
      {
        "matcher": "powerbi-.*",
        "hooks": [
          {
            "type": "command",
            "command": "pwsh -File tools/hooks/on-subagent-stop.ps1 $AGENT_NAME $EXIT_CODE"
          }
        ]
      }
    ]
  }
}
```

---

## Implementation Plan

### Migration Priority

| Priority | Agents | Rationale |
|----------|--------|-----------|
| P0 | powerbi-orchestrator | NEW - enables everything else |
| P1 | Investigation + Validation agents | Highest context savings |
| P2 | Planning + Specialist agents | Core workflow |
| P3 | Utility + QA agents | Lower frequency |

### Migration Order by Branch

**Step 1: Core agents (main branch)**
1. Create `agents/analyst/` directory
2. Convert 20 Core agents + create orchestrator
3. Update SKILL.md to delegate to orchestrator
4. Add `agents/developer/` to `.gitignore`
5. Push to `origin/main`

**Step 2: Cascade to Pro branch**
1. Merge main into pro: `git checkout pro && git merge main`
2. Create `agents/developer/` with 3 Pro agents
3. Update orchestrator with Pro conditionals
4. Push to `pro-origin/main`

---

## Files to Modify

### New Files (Core - main branch)

| File | Purpose |
|------|---------|
| `agents/analyst/powerbi-orchestrator.md` | Central orchestrator (edition-aware) |
| `agents/analyst/powerbi-code-locator.md` | Converted subagent |
| `agents/analyst/powerbi-visual-locator.md` | Converted subagent |
| `agents/analyst/...` | (all 20 core agents) |
| `tools/hooks/on-subagent-start.ps1` | Hook script |
| `tools/hooks/on-subagent-stop.ps1` | Hook script |

### New Files (Pro - pro branch only)

| File | Purpose |
|------|---------|
| `agents/developer/powerbi-playwright-tester.md` | Browser testing subagent |
| `agents/developer/powerbi-ux-reviewer.md` | UX critique subagent |
| `agents/developer/powerbi-qa-inspector.md` | QA inspection subagent |

### Modified Files

| File | Changes |
|------|---------|
| `skills/pbi-squire/SKILL.md` | Delegate to orchestrator |
| `skills/pbi-squire/workflows/*.md` | Simplify - orchestrator handles phases |
| `.claude-plugin/plugin.json` | Add agents directory reference |
| `.gitignore` (main only) | Add `agents/developer/*` |

### Deprecated Files

| File | Status |
|------|--------|
| `skills/pbi-squire/agents/*.md` | Move to `/agents/analyst/` or `/agents/developer/` |

---

## Verification Plan

### Unit Testing (Per Agent)
1. Convert agent to subagent format
2. Create test prompt that exercises key capabilities
3. Verify subagent:
   - Reads correct section from findings.md
   - Writes to correct output section
   - Returns expected summary
   - Doesn't exceed context limits

### Integration Testing (Workflow)
1. Run full `/evaluate-pbi-project-file` workflow
2. Verify orchestrator spawns correct subagents in order
3. Verify findings.md sections populated correctly
4. Verify quality gates triggered at right phases
5. Verify errors propagate correctly

### Regression Testing
1. Run existing test scenarios from current architecture
2. Compare findings.md output structure
3. Verify backward compatibility of findings format

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Subagents can't spawn subagents | Orchestrator spawns all; specialists return to orchestrator |
| Skill injection bloats context | Condense instructions; skill provides base knowledge only |
| findings.md concurrent writes | Orchestrator waits for each subagent to complete before next |
| Breaking existing workflows | Keep old agents/ directory during migration; gradual rollout |

---

## Expected Benefits

1. **Context isolation** - Each subagent gets fresh context (no rot)
2. **Skill injection** - pbi-squire knowledge loaded per subagent
3. **Parallel execution** - Investigation/validation agents run concurrently
4. **Edition-aware** - Orchestrator adapts to Core vs Pro capabilities
5. **Maintainability** - Smaller, focused agent files; centralized orchestration

---

## Sources

- [claude-sub-agent GitHub](https://github.com/zhsama/claude-sub-agent) - Three-phase pipeline pattern
- [Best practices for Claude Code sub-agents](https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/) - HITL, hooks, memory patterns
- [Claude Code Subagents Documentation](https://code.claude.com/docs/en/sub-agents) - Official subagent API
