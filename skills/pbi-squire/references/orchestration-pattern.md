# Orchestration Pattern Reference

This document describes the orchestration logic for Power BI workflows. The **main thread** (skill layer) executes this logic directly - it is NOT a subagent.

## Routing & Clarification (First Priority)

Before starting any workflow, classify the user's request and route to the appropriate workflow.

### Decision Tree

```
User Request
    │
    ├─ Contains "fix", "broken", "wrong", "debug", "issue", "error", "not working"
    │  └─► EVALUATE workflow (workflows/evaluate-pbi-project-file.md)
    │
    ├─ Contains "visual", "card", "chart", "page", "dashboard page", "build visual"
    │  └─► CREATE_PAGE workflow ⭐ PRO ONLY (workflows/create-pbi-page-specs.md)
    │      NOTE: Visuals require layout, field bindings, and PBIR generation
    │      CORE FALLBACK: Create measures with CREATE_ARTIFACT, add visuals in PBI Desktop
    │
    ├─ Contains "create measure", "add measure", "new measure", "new column", "new table"
    │  └─► CREATE_ARTIFACT workflow (workflows/create-pbi-artifact-spec.md)
    │      NOTE: Code artifacts only (DAX/M). For visuals → CREATE_PAGE (Developer)
    │
    ├─ Contains "M code", "Power Query", "transform", "ETL", "filter table", "merge tables"
    │  └─► DATA_PREP workflow (workflows/setup-data-anonymization.md for masking, else inline)
    │
    ├─ Contains "explain", "understand", "what does", "document", "tell me about"
    │  └─► SUMMARIZE workflow (inline analysis)
    │
    ├─ Contains "apply", "implement", "deploy", "execute", "make the changes"
    │  └─► IMPLEMENT workflow (workflows/implement-deploy-test-pbi-project-file.md)
    │
    ├─ Contains "compare", "merge", "diff", "sync projects", "combine"
    │  └─► MERGE workflow (workflows/merge-powerbi-projects.md)
    │
    ├─ Contains "version", "update", "edition", "check for updates"
    │  └─► VERSION_CHECK (direct, no subagents needed)
    │
    ├─ Contains "anonymize", "anonymization", "mask sensitive", "data masking", "hide PII"
    │  └─► SETUP_ANONYMIZATION workflow (workflows/setup-data-anonymization.md)
    │
    └─ Unclear / Vague
       └─► ASK CLARIFYING QUESTIONS (see below)
```

**Routing Priority for Ambiguous Requests:**
- "Create a sales card" → CREATE_PAGE (Developer) - visual mentioned
- "Create a YoY measure" → CREATE_ARTIFACT (code artifact)
- "Create a measure and show it on a card" → CREATE_PAGE (Developer) - includes visual
- "Add a calculated column" → CREATE_ARTIFACT (code artifact)

**Analyst Edition Visual Request Handling:**
When a Core user requests visual creation, respond with:
```
Visual creation requires the Developer Edition of PBI Squire.

What I can do for you (Analyst Edition):
1. Create the measures/calculations you need → /create-pbi-artifact-spec
2. You can then add visuals manually in Power BI Desktop

Would you like me to create the underlying measures instead?
```

### Clarification Flow (For Unclear Requests)

When intent is unclear (e.g., "help me with Power BI", "I need assistance"), ask targeted questions:

**Step 1: Determine action type**
```
I can help you with your Power BI project. Are you trying to:

1. **Fix** something that's broken or incorrect?
2. **Create** something new (measure, visual, table)?
3. **Transform** data (Power Query / M code)?
4. **Understand** what a dashboard does?
5. **Apply** changes from a previous analysis?

Which best describes what you need?
```

**Step 2: Gather required information**
Based on their answer, gather:
- Project path (if not already known)
- Specific problem or goal description
- Any relevant file paths or measure names

**Step 3: Confirm before proceeding**
```
I'll use the [WORKFLOW] workflow to [brief description].
This will [what happens next].

Ready to proceed?
```

### Quick Classification Examples

| User Says | Route To | Rationale |
|-----------|----------|-----------|
| "My YoY measure is showing wrong values" | EVALUATE | Fix existing |
| "Create a profit margin measure" | CREATE_ARTIFACT | Code artifact (DAX) |
| "Add a calculated column for full name" | CREATE_ARTIFACT | Code artifact (DAX) |
| "Create a sales KPI card" | CREATE_PAGE (Developer) | Visual (needs PBIR) |
| "Build a visual showing revenue by region" | CREATE_PAGE (Developer) | Visual (needs layout) |
| "Add a new dashboard page" | CREATE_PAGE (Developer) | Page creation |
| "Create a measure and display it on a card" | CREATE_PAGE (Developer) | Includes visual |
| "Filter the Customers table to active only" | DATA_PREP | M code transformation |
| "Explain how the Sales page works" | SUMMARIZE | Documentation |
| "Apply the fixes we discussed" | IMPLEMENT | Execute changes |
| "Merge my dev branch with production" | MERGE | Project comparison |
| "Set up data anonymization" | SETUP_ANONYMIZATION | Data masking |
| "Mask sensitive columns" | SETUP_ANONYMIZATION | Data masking |
| "Help me with Power BI" | ASK CLARIFICATION | Unclear intent |
| "I have a Power BI question" | ASK CLARIFICATION | Unclear intent |

---

## Phase Execution Pattern

### Phase 0: Setup

1. Create timestamped scratchpad directory:
   ```
   agent_scratchpads/YYYYMMDD-HHMMSS-<task-name>/
   ```

2. Create findings.md with Problem Statement from user request

3. Classify change type based on problem statement:
   - `calc_only` - DAX/M/TMDL changes only
   - `visual_only` - PBIR visual changes only
   - `hybrid` - Both calculation and visual changes

### Phase 1: Investigation (PARALLEL subagents)

Main thread spawns investigation subagents based on change type:

```
IF calc_only OR hybrid:
  Task(powerbi-code-locator)
    Input: Problem Statement
    Output: Section 1.A (Code Investigation)

IF visual_only OR hybrid:
  Task(powerbi-visual-locator)
    Input: Problem Statement, screenshot paths if provided
    Output: Section 1.B (Visual Investigation)

IF data context needed (complex calculations):
  Task(powerbi-data-context-agent)
    Input: Problem Statement
    Output: Section 1.C (Data Context)

IF pattern discovery needed (new artifacts):
  Task(powerbi-pattern-discovery)
    Input: Problem Statement, artifact type
    Output: Section 1.D (Pattern Discovery)
```

**Quality Gate 1:** Main thread reads findings.md and verifies all required sections populated or explicitly marked N/A

### Phase 2: Planning (SEQUENTIAL)

```
Task(powerbi-dashboard-update-planner)
  Input: Reads Section 1.* from findings.md
  Output: Section 2 (Proposed Changes)
  May write: Section 2.A.spec, Section 2.B.spec (specialist work specifications)
```

**After planner returns**, main thread checks for specialist specs:

```
IF Section 2.A.spec exists (DAX work needed):
  Task(powerbi-dax-specialist)
    Input: Reads Section 2.A.spec
    Output: Section 2.A (actual DAX code)

IF Section 2.B.spec exists (M code work needed):
  Task(powerbi-mcode-specialist)
    Input: Reads Section 2.B.spec
    Output: Section 2.A (under M Code subsection)
```

For hybrid changes, calculation changes are planned FIRST, then visual changes reference them.

**Quality Gate 2:** Main thread reads findings.md and verifies Section 2 complete with:
- Section 2.A (Calculation Changes) if calc_only or hybrid
- Section 2.B (Visual Changes) if visual_only or hybrid
- Coordination Summary if hybrid

### Phase 3: Validation (PARALLEL subagents)

Main thread spawns validation subagents:

```
IF Section 2.A exists (calculation changes):
  Task(powerbi-dax-review-agent)
    Input: Section 2.A
    Output: Section 2.5 (DAX Review)

IF Section 2.B exists (visual changes):
  Task(powerbi-pbir-validator)
    Input: Section 2.B, project path
    Output: Section 2.6 (PBIR Validation)

ALWAYS (for calculation changes):
  Validate TMDL using MCP (if available) or Claude-native validation
    Output: Section 2.7 (TMDL Validation)
```

**Quality Gate 3:** Main thread reads validation sections and checks for PASS (threshold: 100%)

If any validator returns FAIL:
1. Document errors in findings.md Section 9: Errors
2. Report to user with specific issues
3. Offer to revise plan or exit workflow

### Phase 4: Completion

1. Display findings.md summary to user
2. Explain proposed changes
3. Suggest next command (`/implement-deploy-test-pbi-project-file`)

---

## Subagent Invocation Pattern

When spawning subagents from the main thread, provide a clear task prompt:

```
Task(powerbi-code-locator):
  "Locate DAX code for the calculation mentioned in the Problem Statement.

   Task memory: agent_scratchpads/20250128-143000-fix-yoy/findings.md

   Read: Problem Statement section
   Write: Section 1.A

   Project path: C:/Projects/SalesReport/SalesReport.pbip

   Focus on: [specific guidance based on problem statement]"
```

---

## Quality Gate Checks

After each phase, the main thread verifies completion:

1. Read findings.md
2. Check expected sections exist and have content
3. Parse for PASS/FAIL verdicts in validation sections
4. If FAIL:
   - Extract specific error messages
   - Report to user
   - Offer options: revise, retry, or abort
5. If PASS: Proceed to next phase

---

## Error Handling

### Subagent Failure
If a subagent fails or returns incomplete results:
1. Read any partial output
2. Document error in findings.md Section 9: Errors
3. Ask user if they want to:
   - Retry the subagent
   - Provide additional context
   - Skip this phase (if optional)
   - Abort workflow

### Quality Gate Failure
If a quality gate fails:
1. Present specific validation errors
2. Offer to:
   - Revise the plan (return to planning phase)
   - Override (if warnings only)
   - Abort workflow

### User Abandonment
If user wants to stop:
1. Update findings.md with ABANDONED status
2. Archive the scratchpad
3. Confirm workflow stopped

---

## findings.md Template

Create findings.md with this structure:

```markdown
# Power BI Analysis: [Task Name]

**Created:** YYYY-MM-DD HH:MM:SS
**Status:** IN_PROGRESS | COMPLETE | ABANDONED
**Workflow:** EVALUATE | CREATE_ARTIFACT | IMPLEMENT | MERGE
**Change Type:** calc_only | visual_only | hybrid
**Project Path:** [path to .pbip]

---

## Problem Statement

[User's original request]

---

## Section 1: Investigation

### 1.A Code Investigation
*Written by: powerbi-code-locator*

[Content written by code-locator subagent]

### 1.B Visual Investigation
*Written by: powerbi-visual-locator*

[Content written by visual-locator subagent]

### 1.C Data Context
*Written by: powerbi-data-context-agent*

[Content written by data-context subagent]

### 1.D Pattern Discovery
*Written by: powerbi-pattern-discovery*

[Content written by pattern-discovery subagent]

---

## Section 2: Proposed Changes

[If hybrid: Coordination Summary here]

### 2.A Calculation Changes
*Written by: powerbi-dashboard-update-planner or powerbi-dax-specialist*

[Proposed DAX/M/TMDL changes]

### 2.A.spec DAX Specialist Work Specification (if applicable)
*Written by: powerbi-dashboard-update-planner*

[Specification for DAX specialist - consumed by main thread]

### 2.B Visual Changes
*Written by: powerbi-dashboard-update-planner*

[Proposed PBIR changes with XML edit plan]

### 2.B.spec M Code Specialist Work Specification (if applicable)
*Written by: powerbi-dashboard-update-planner*

[Specification for M code specialist - consumed by main thread]

---

## Section 2.5: DAX Review
*Written by: powerbi-dax-review-agent*

**Status:** PASS | WARNINGS | FAIL

[Validation results]

---

## Section 2.6: PBIR Validation
*Written by: powerbi-pbir-validator*

**Status:** PASS | WARNINGS | FAIL

[Validation results]

---

## Section 2.7: TMDL Validation
*Written by: MCP validation or Claude-native structural check*

**Status:** PASS | WARNINGS | FAIL

[Validation results]

---

## Section 3: Test Cases
*For testing phase*

[Test case definitions]

---

## Section 4: Implementation Results
*Written by: implementer agents*

[Results of applying changes]

---

## Section 5: Test Results
*Written by: powerbi-playwright-tester (Developer)*

[Test execution results]

---

## Section 9: Errors

[Any errors encountered during workflow]

---

## Next Steps

[Suggested actions based on current state]
```

---

## Developer Edition Features

When Pro agents are available, additional capabilities can be used:

### QA Loop
After implementation, offer to run the QA Loop:
1. Deploy via Git commit
2. Monitor deployment status
3. Task(powerbi-qa-inspector) - DOM inspection
4. Task(powerbi-playwright-tester) - Automated tests

### Design Critique
When `--design-critique` flag is used:
1. Task(powerbi-ux-reviewer) - Screenshot analysis
2. Design scoring (1-5 scale)
3. Specific improvement recommendations

---

## Tracing Output

The main thread provides clear progress indicators:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 WORKFLOW: EVALUATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 PHASE 0: Setup
   └─ Created scratchpad: agent_scratchpads/20250128-143000-fix-yoy/
   └─ Created findings.md
   └─ Change type: calc_only

📋 PHASE 1: Investigation
   └─ 🤖 [SUBAGENT] powerbi-code-locator
   └─    Starting: Locate DAX code for YoY measure
   └─ 🤖 [SUBAGENT] powerbi-code-locator complete
   └─    Result: Found measure in Sales.tmdl
   └─    Section 1.A written

   └─ ✅ Quality Gate 1: PASS (1/1 sections complete)

📋 PHASE 2: Planning
   └─ 🤖 [SUBAGENT] powerbi-dashboard-update-planner
   └─    Starting: Diagnose and plan fix
   └─ 🤖 [SUBAGENT] powerbi-dashboard-update-planner complete
   └─    Result: Root cause identified, fix proposed
   └─    Section 2.A written

   └─ ✅ Quality Gate 2: PASS (Section 2.A complete)

📋 PHASE 3: Validation
   └─ 🤖 [SUBAGENT] powerbi-dax-review-agent
   └─    Starting: Review proposed DAX
   └─ 🤖 [SUBAGENT] powerbi-dax-review-agent complete
   └─    Result: PASS - No issues found
   └─    Section 2.5 written

   └─ 🔍 [VALIDATE] TMDL structure
   └─    Method: MCP validation / Claude-native
   └─    Result: PASS - Valid TMDL syntax
   └─    Section 2.7 written

   └─ ✅ Quality Gate 3: PASS (All validators passed)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WORKFLOW COMPLETE: EVALUATE
   └─ Output: agent_scratchpads/20250128-143000-fix-yoy/findings.md
   └─ Next step: Run /implement-deploy-test-pbi-project-file
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Critical Constraints

1. **Main thread orchestrates** - Never delegate orchestration to a subagent
2. **Subagents are leaf nodes** - Subagents do NOT spawn other subagents
3. **Never skip quality gates** - All validations must pass before proceeding
4. **Always use findings.md** - All subagent communication through shared file
5. **Parallel when possible** - Spawn independent subagents concurrently
6. **Sequential when dependent** - Wait for dependencies before next phase
7. **Clear error reporting** - Always explain failures with specific details
8. **User confirmation** - Get approval before implementing changes
9. **Edition awareness** - Only offer Developer features when Pro agents exist

---

## Self-Verification Checklist

Before completing any workflow:

- [ ] Scratchpad directory created with timestamp
- [ ] findings.md has all required sections for workflow type
- [ ] All quality gates passed or user approved override
- [ ] Next steps clearly communicated
- [ ] Errors documented if any occurred
