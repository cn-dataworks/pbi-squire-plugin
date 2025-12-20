# Power BI Analyst Plugin: MCP Hybrid Architecture Conversion

## Document Info

- **Created:** 2025-12-19
- **Status:** Draft Specification
- **Goal:** Convert plugin to skill with Power BI Modeling MCP integration

---

## 1. Executive Summary

Convert the Power BI Analyst Plugin from a file-based architecture (parsing TMDL files, using pbi-tools) to a hybrid architecture that uses Microsoft's Power BI Modeling MCP for semantic model operations while retaining LLM-based reasoning agents and PBIR file manipulation for report-side changes.

**Expected Outcomes:**
- Reduce agent count from 27 to ~18 (net reduction of 9)
- Introduce specialized DAX and M-Code agents with focused prompts
- Eliminate file parsing/manipulation for semantic model operations
- Add transaction support (rollback on failure)
- Enable live model editing (Power BI Desktop, Fabric)
- Simplify deployment pipeline
- Implement state.json orchestration for session-level "Global Truth"
- Package as a Claude Code skill

---

## 2. Current State

### 2.1 Agent Inventory (27 total)

**Planning/Reasoning (7 agents):**
- powerbi-dashboard-update-planner
- powerbi-artifact-decomposer
- powerbi-data-understanding-agent
- powerbi-artifact-designer
- power-bi-verification
- powerbi-code-understander
- powerbi-code-fix-identifier (DEPRECATED)

**Investigation (4 agents):**
- powerbi-data-model-analyzer
- powerbi-data-context-agent
- powerbi-code-locator
- powerbi-visual-locator

**Implementation (2 agents):**
- powerbi-code-implementer-apply
- powerbi-visual-implementer-apply

**Validation (4 agents):**
- powerbi-tmdl-syntax-validator
- powerbi-dax-review-agent
- powerbi-pbir-validator
- powerbi-verify-pbiproject-folder-setup

**Page Design (5 agents):**
- powerbi-page-question-analyzer
- powerbi-visual-type-recommender
- powerbi-page-layout-designer
- powerbi-interaction-designer
- powerbi-pbir-page-generator

**Merge Workflow (3 agents):**
- powerbi-compare-project-code
- powerbi-code-understander
- powerbi-code-merger

**Testing (1 agent):**
- powerbi-playwright-tester

**Deprecated (2 agents):**
- powerbi-code-fix-identifier
- pbir-visual-edit-planner

### 2.2 Current Architecture

```
User Request
    |
    v
[LLM Planning Agents]
    |
    v
[File Parsing] --> Parse TMDL files as text
    |
    v
[Code Generation] --> Generate DAX/M/TMDL
    |
    v
[File Writing] --> Write to .tmdl files
    |
    v
[pbi-tools] --> Compile and deploy
    |
    v
[PBIR Editing] --> Modify visual.json files
```

### 2.3 Current Dependencies

- Python 3.x (TMDL parsing, XMLA queries)
- pbi-tools CLI (compilation, deployment)
- PowerShell + MicrosoftPowerBIMgmt (user auth deployment)
- Playwright MCP (browser testing)

---

## 3. Target State

### 3.1 Hybrid Architecture

```
User Request
    |
    v
[LLM Planning Agents] -- KEEP (reasoning layer)
    |
    v
[Power BI Modeling MCP] -- NEW (execution layer)
    |                      - connection_operations
    |                      - table/column/measure_operations
    |                      - dax_query_operations
    |                      - transaction_operations
    |                      - database_operations (deploy)
    |
    v
[PBIR Editing Agents] -- KEEP (MCP can't do reports)
    |
    v
[Testing] -- KEEP
```

### 3.1.1 State Management

The skill maintains a `state.json` in the scratchpad that serves as the "Global Truth" for the current session:

- **Model Schema:** Current tables, columns, measures, relationships
- **Active Tasks Queue:** Pending operations for specialists
- **Validation Status:** Results from DAX/M validation passes
- **MCP Connection:** Connection type, status, target model

Specialists read from `state.json` and write their outputs to `findings.md`. The Orchestrator updates `state.json` after MCP operations complete successfully.

> **Implementation Reference:**
> - See **Appendix C** for the `findings.md` template structure
> - See **Appendix D** for the `state_manage.py` implementation and CLI interface

```
┌─────────────────────────────────────────────────────────────┐
│                      Orchestrator                            │
│              (powerbi-artifact-designer)                     │
│                    manages state.json                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
┌─────────────────┐         ┌─────────────────┐
│  DAX Specialist │         │ M-Code Specialist│
│                 │         │                  │
│ - Time Intel    │         │ - ETL Patterns   │
│ - Filter Context│         │ - Query Folding  │
│ - DIVIDE()      │         │ - Privacy Levels │
│ - KEEPFILTERS() │         │ - Data Types     │
└────────┬────────┘         └────────┬─────────┘
         │                           │
         └─────────────┬─────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Power BI Modeling MCP                     │
│                     (Data Modeler Layer)                     │
│  measure_operations | partition_operations | transactions   │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Target Agent Inventory (18 total)

**Planning/Reasoning - KEEP (6 agents):**
- powerbi-dashboard-update-planner
- powerbi-artifact-decomposer
- powerbi-data-understanding-agent
- powerbi-artifact-designer (becomes Orchestrator for specialists)
- power-bi-verification
- powerbi-code-understander

**Specialists - NEW (2 agents):**
- powerbi-dax-specialist (Time Intelligence, Filter Context, Performance)
- powerbi-mcode-specialist (ETL, Query Folding, Privacy Levels)

**Investigation - REMOVE/REPLACE (0 agents, use MCP):**
- ~~powerbi-data-model-analyzer~~ --> mcp.table/column/measure_operations
- ~~powerbi-data-context-agent~~ --> mcp.dax_query_operations
- ~~powerbi-code-locator~~ --> mcp.measure_operations.get()
- powerbi-visual-locator --> KEEP (PBIR, MCP can't do)

**Implementation - SIMPLIFY (1 agent):**
- ~~powerbi-code-implementer-apply~~ --> mcp.measure_operations + transactions
- powerbi-visual-implementer-apply --> KEEP (PBIR)

**Validation - SIMPLIFY (2 agents):**
- ~~powerbi-tmdl-syntax-validator~~ --> MCP validates implicitly
- powerbi-dax-review-agent --> ENHANCE with mcp.dax_query_operations.validate()
- powerbi-pbir-validator --> KEEP
- ~~powerbi-verify-pbiproject-folder-setup~~ --> mcp.connection_operations

**Page Design - KEEP (5 agents):**
- powerbi-page-question-analyzer
- powerbi-visual-type-recommender
- powerbi-page-layout-designer
- powerbi-interaction-designer
- powerbi-pbir-page-generator

**Merge Workflow - ENHANCE (2 agents):**
- powerbi-compare-project-code --> ENHANCE with MCP model reads
- ~~powerbi-code-merger~~ --> mcp.transaction + operations

**Testing - KEEP (1 agent):**
- powerbi-playwright-tester

### 3.3 Target Dependencies

- Power BI Modeling MCP (required)
- Playwright MCP (for testing)
- Python 3.x (PBIR editing only - may eliminate later)

**Removed:**
- pbi-tools CLI (MCP handles deployment)
- Python XMLA scripts (MCP handles queries)
- Python TMDL parsers (MCP handles model reads)

---

## 4. Work Breakdown

### Phase 1: Cleanup & Preparation

**1.1 Delete Deprecated Agents**
- [ ] Delete `.claude/agents/powerbi-code-fix-identifier.md`
- [ ] Delete `.claude/agents/power-bi-visual-edit-planner.md`
- [ ] Update README.md to remove references
- [ ] Verify no commands reference these agents

**1.2 Document MCP Dependency**
- [ ] Add MCP setup instructions to README.md
- [ ] Document connection methods (Desktop, Fabric, PBIP)
- [ ] Document authentication requirements
- [ ] Add troubleshooting section

**Estimated Effort:** 2-4 hours

---

### Phase 2: Core MCP Integration

**2.1 Create MCP Connection Helper**
- [ ] Create `.claude/helpers/mcp-connection.md` with connection patterns
- [ ] Document connection_operations usage
- [ ] Create connection validation patterns
- [ ] Handle auth failures gracefully

**2.2 Replace powerbi-verify-pbiproject-folder-setup**
- [ ] Create new agent that uses mcp.connection_operations
- [ ] Support all three connection types (Desktop, Fabric, PBIP)
- [ ] Return structured connection status
- [ ] Update commands to use new agent

**2.3 Replace powerbi-data-model-analyzer**
- [ ] Create MCP-based schema extraction
- [ ] Map MCP responses to existing Section 1.1 format
- [ ] Test with all three connection types
- [ ] Update powerbi-artifact-decomposer to use new approach

**2.4 Replace powerbi-data-context-agent**
- [ ] Replace XMLA Python scripts with mcp.dax_query_operations
- [ ] Map MCP query results to existing format
- [ ] Handle query validation
- [ ] Update /evaluate command

**2.5 Replace powerbi-code-locator**
- [ ] Replace file grep with mcp.measure_operations.get()
- [ ] Map MCP responses to Section 1.A format
- [ ] Handle "not found" cases
- [ ] Update commands

**Estimated Effort:** 8-16 hours

---

### Phase 2.5: Specialist Agent Separation

**2.5.1 Create DAX Specialist Agent**
- [ ] Create `.claude/agents/powerbi-dax-specialist.md`
- [ ] Focus areas:
  - Time Intelligence patterns (SAMEPERIODLASTYEAR, DATEADD, etc.)
  - Filter Context awareness (CALCULATE, FILTER, ALL, KEEPFILTERS)
  - Performance patterns (DIVIDE(), SUMX vs SUM, iterator vs aggregator)
  - Relationship-aware calculations (RELATED, RELATEDTABLE, USERELATIONSHIP)
- [ ] Input: Business logic requirements + state.json (model schema)
- [ ] Output: Validated DAX expression written to findings.md
- [ ] Validation: Uses mcp.dax_query_operations.validate() before returning
- [ ] MCP Tools: measure_operations.create/update, dax_query_operations

**2.5.2 Create M-Code Specialist Agent**
- [ ] Create `.claude/agents/powerbi-mcode-specialist.md`
- [ ] Focus areas:
  - ETL patterns (Table.TransformColumns, Table.AddColumn, etc.)
  - Query folding optimization (keep operations foldable)
  - Privacy levels (Organizational, Private, Public)
  - Data type enforcement (type text, type number, etc.)
  - Error handling (try/otherwise patterns)
- [ ] Input: Data source requirements + transformation logic
- [ ] Output: Validated M script written to findings.md
- [ ] MCP Tools: partition_operations, named_expression operations

**2.5.3 Refactor powerbi-artifact-designer as Orchestrator**
- [ ] Update agent to orchestrate DAX/M specialists
- [ ] Add state.json initialization and management
- [ ] Delegate to appropriate specialist based on artifact type:
  - Measures → DAX Specialist
  - Calculated Columns → DAX Specialist
  - Partitions/Tables → M-Code Specialist
  - Calculation Groups → DAX Specialist
- [ ] Coordinate MCP transactions across specialist outputs
- [ ] Update state.json after successful MCP operations

**2.5.4 Define Specialist Handoff Protocol**
- [ ] Document state.json schema
- [ ] Define findings.md output format for specialists
- [ ] Create validation checkpoints between specialists and MCP
- [ ] Handle specialist failures gracefully (no partial state)

**Estimated Effort:** 6-10 hours

---

### Phase 3: Implementation Layer

**3.1 Replace powerbi-code-implementer-apply**
- [ ] Create transaction-based implementation pattern
- [ ] Map Section 2 CREATE/MODIFY to MCP operations:
  - measure_operations.create_measure()
  - measure_operations.update_measure()
  - column_operations.create_calculated_column()
  - table_operations.create_table()
- [ ] Implement rollback on failure
- [ ] Handle deployment via mcp.database_operations
- [ ] Remove pbi-tools dependency for semantic model changes

**3.2 Replace powerbi-tmdl-syntax-validator**
- [ ] Remove agent (MCP validates implicitly)
- [ ] Update /implement command to handle MCP validation errors
- [ ] Map MCP errors to user-friendly messages
- [ ] Remove Python validator scripts (or keep for offline use)

**3.3 Enhance powerbi-dax-review-agent**
- [ ] Add mcp.dax_query_operations.validate() call
- [ ] Keep LLM semantic review
- [ ] Combine MCP syntax + LLM semantic into single report

**Estimated Effort:** 8-16 hours

---

### Phase 4: Merge Workflow

**4.1 Enhance powerbi-compare-project-code**
- [ ] Connect to both models via MCP
- [ ] Use MCP to extract model state (not file parsing)
- [ ] Keep LLM diff logic
- [ ] Update output format

**4.2 Replace powerbi-code-merger**
- [ ] Use MCP transactions for atomic merge
- [ ] Apply decisions via MCP operations
- [ ] Export merged model to TMDL for version control
- [ ] Remove file manipulation code

**Estimated Effort:** 4-8 hours

---

### Phase 5: Pattern Discovery Enhancement

**5.1 Enhance powerbi-pattern-discovery**
- [ ] Use MCP to list all measures
- [ ] Pass to LLM for pattern analysis
- [ ] Remove file scanning code

**Estimated Effort:** 2-4 hours

---

### Phase 6: Command Updates

**6.1 Update /evaluate-pbi-project-file**
- [ ] Add MCP connection step at start
- [ ] Replace agent invocations with MCP-based versions
- [ ] Update error handling for MCP failures
- [ ] Test all three connection types

**6.2 Update /create-pbi-artifact**
- [ ] Add MCP connection step
- [ ] Use MCP for schema extraction
- [ ] Use MCP for implementation
- [ ] Test end-to-end

**6.3 Update /implement-deploy-test-pbi-project-file**
- [ ] Replace code-implementer with MCP operations
- [ ] Use MCP deployment instead of pbi-tools
- [ ] Keep PBIR visual implementation unchanged
- [ ] Update validation flow

**6.4 Update /merge-powerbi-projects**
- [ ] Add MCP connections to both models
- [ ] Use enhanced agents
- [ ] Test merge scenarios

**Estimated Effort:** 8-12 hours

---

### Phase 7: Skill Packaging

> **Note:** The current `skill.md` in this spec folder is a **placeholder skeleton**. It lacks:
> - Enterprise-ready PBIR validation (Legacy vs Enhanced format detection)
> - Schema version checking (`$schema` URL parsing for `1.1.0`, `1.2.0`, etc.)
> - Python guardrails before MCP calls (pre-flight checks)
> - CI/CD testing integration (DAX output validation, visual regression)
> - January 2026 format migration awareness
>
> The skill.md must be expanded to include hybrid Python + MCP validation patterns.

### 7.0 Skill Definition (Complete Specification)

This section provides the complete specification for the skill, derived from readiness_analysis.md Section 1.1.

#### 7.0.1 Skill Metadata Block

```yaml
---
name: powerbi-analyst
description: |
  Expert Power BI development assistant for creating dashboards, diagnosing calculation
  issues, implementing DAX/M code changes, and analyzing existing reports. Uses Microsoft's
  Power BI Modeling MCP for live semantic model editing when available, with automatic
  fallback to file-based TMDL manipulation. Supports Power BI Desktop, Fabric workspaces,
  and .pbip project folders. Orchestrates specialized DAX and M-Code agents for complex
  calculations. Handles PBIR visual editing for report-side changes. Containerized access
  model restricts file operations to user-specified project folders only.

triggers:
  keywords:
    - "Power BI"
    - "PBIX"
    - "PBIP"
    - "DAX"
    - "M code"
    - "Power Query"
    - "semantic model"
    - "measure"
    - "calculated column"
    - "TMDL"
  actions:
    - "create dashboard"
    - "fix measure"
    - "add visual"
    - "deploy report"
    - "analyze dashboard"
    - "merge projects"
  file_patterns:
    - "*.pbip"
    - "*.pbix"
    - "*.tmdl"
    - "*.bim"
    - "*/.SemanticModel/**"
    - "*/.Report/**"

mcp_mode: preferred_with_fallback
  # preferred_with_fallback: Use MCP when available, fall back to file-based agents
  # required: Fail fast if MCP unavailable
  # optional: File-based by default, MCP only if explicitly requested
---
```

#### 7.0.2 Tool Access Model (Containerized Security)

The skill uses a containerized access model where file operations are restricted to user-specified folders.

**Baseline Access (Always Available):**
```yaml
allowed-tools:
  # Web access for documentation lookup
  - WebSearch
  - WebFetch(domain:learn.microsoft.com)
  - WebFetch(domain:dax.guide)
  - WebFetch(domain:www.sqlbi.com)
  - WebFetch(domain:community.fabric.microsoft.com)
  - WebFetch(domain:powerquery.how)

  # MCP tools (all operations)
  - mcp__powerbi-modeling__*

  # State management (skill internals)
  - Read(.claude/**)
  - Write(.claude/**)
  - Edit(.claude/**)

  # Scratchpad for findings
  - Read(agent_scratchpads/**)
  - Write(agent_scratchpads/**)
  - Edit(agent_scratchpads/**)

  # Sub-agent orchestration
  - Task
```

**Project Folder Access (User-Configured):**

Users must configure allowed project folders in their Claude Code settings. The skill gains full access ONLY to folders in this allowlist.

**Settings Configuration (settings.json):**
```json
{
  "skills": {
    "powerbi-analyst": {
      "project_folders": [
        "C:/Users/*/Documents/PowerBI/**",
        "C:/Users/*/Documents/Customer Projects/**/*.Report/**",
        "C:/Users/*/Documents/Customer Projects/**/*.SemanticModel/**"
      ]
    }
  }
}
```

**Dynamic Project Access:**
When the skill is invoked with a `--project` parameter, it validates the path against the allowlist before granting full access:

```
Full access granted to: <project_path>/**
  - Read, Write, Edit (all file operations)
  - Bash(pbi-tools:*) for that folder
  - Bash(python:*) for scripts in that folder
```

**Access Denied Behavior:**
If user provides a path not in the allowlist:
```
⚠️ PROJECT FOLDER NOT IN ALLOWLIST

The folder you specified is not in your configured project folders:
  Requested: C:\SomeOtherFolder\Dashboard

To allow access, add this path (or a parent pattern) to your settings:
  Claude Code → Settings → Skills → powerbi-analyst → project_folders

Or use a folder that matches an existing pattern:
  - C:/Users/*/Documents/PowerBI/**
  - C:/Users/*/Documents/Customer Projects/**
```

#### 7.0.3 MCP Dependency Configuration

```yaml
mcp_dependencies:
  required: false  # Skill works without MCP (fallback mode)
  preferred:
    - name: powerbi-modeling
      source: https://github.com/microsoft/powerbi-modeling-mcp
      capabilities:
        - connection_operations
        - database_operations
        - table_operations
        - column_operations
        - measure_operations
        - relationship_operations
        - dax_query_operations
        - transaction_operations
        - partition_operations
        - calculation_group_operations

  optional:
    - name: playwright
      source: (already configured)
      capabilities:
        - browser testing
        - screenshot capture
```

**MCP Detection Logic:**
```
On skill initialization:
1. Check if mcp__powerbi-modeling__* tools are available
2. If available:
   - Set mode = "mcp"
   - Initialize connection based on user preference
3. If not available:
   - Set mode = "file_fallback"
   - Warn user: "MCP not available. Using file-based mode with reduced capabilities."
   - List reduced capabilities
```

#### 7.0.4 Session Initialization Logic

Defines what happens when the skill is first invoked in a conversation.

**Initialization Sequence:**
```
SKILL INVOCATION
    │
    ▼
┌─────────────────────────────────────────┐
│  Step 1: Project Folder Validation       │
│  ─────────────────────────────────────── │
│  • Check if user provided --project path │
│  • Validate path against settings        │
│    allowlist (project_folders)           │
│  • If not in allowlist → ABORT with      │
│    guidance (see below)                  │
└─────────────────────────────────────────┘
    │ (path validated)
    ▼
┌─────────────────────────────────────────┐
│  Step 2: State Recovery                  │
│  ─────────────────────────────────────── │
│  • Check for existing .claude/state.json │
│  • TODO: Define recovery behavior        │
│    (see state_manage.py for current      │
│    implementation patterns)              │
│  • Options to resolve:                   │
│    - Fresh start always                  │
│    - Resume if recent (<24h)             │
│    - Prompt user to resume or start new  │
│    - Auto-resume silently                │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  Step 3: MCP Availability Check          │
│  ─────────────────────────────────────── │
│  • Check if mcp__powerbi-modeling__*     │
│    tools are available                   │
│  • Set mode flag: "mcp" or "file_fallback"│
│  • DO NOT connect yet (lazy connection)  │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  Step 4: Initialize State Manager        │
│  ─────────────────────────────────────── │
│  • python state_manage.py --summary      │
│  • Load or create state.json             │
│  • Display session status to user        │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  Step 5: Ready for Intent Classification │
│  ─────────────────────────────────────── │
│  • Skill is initialized                  │
│  • Proceed to classify user's request    │
└─────────────────────────────────────────┘
```

**MCP Connection Strategy: Lazy**

MCP connection is NOT established during initialization. Instead:
- Connection is deferred until first operation that requires MCP
- This avoids unnecessary auth prompts for simple requests
- First MCP-requiring operation triggers connection flow

```
When MCP operation needed:
1. Check if already connected
2. If not connected:
   a. Prompt user for connection type (Desktop/Fabric/PBIP)
   b. Attempt connection via mcp.connection_operations
   c. Cache connection for remainder of session
3. Execute operation
```

**Project Folder Validation Failure:**

If user provides a path not in the allowlist, ABORT with clear guidance:

```
❌ PROJECT ACCESS DENIED

The specified folder is not in your allowed project folders:
  📁 Requested: C:\SomeOtherFolder\Dashboard

To fix this, you have two options:

OPTION 1: Add folder to your settings
──────────────────────────────────────
Open Claude Code settings and add this path pattern:
  Settings → Skills → powerbi-analyst → project_folders

Add: "C:/SomeOtherFolder/**"

OPTION 2: Use an already-allowed folder
──────────────────────────────────────
Your current allowed folders are:
  • C:/Users/*/Documents/PowerBI/**
  • C:/Users/*/Documents/Customer Projects/**

Move your project to one of these locations, or use a project already there.

💡 This security restriction ensures the skill can only modify files in
   folders you've explicitly authorized.
```

**State Recovery (TODO):**

> **Decision Required:** How should the skill handle existing state from previous sessions?
>
> The `state_manage.py` implementation currently:
> - Loads existing state.json if present (`_load()` method)
> - Creates fresh state if no file exists
> - Does not implement session timeout or staleness detection
>
> **Options to implement:**
> 1. **Fresh start always** - Ignore existing state, start clean
> 2. **Resume if recent** - Check `last_updated` timestamp, resume if <24h
> 3. **Prompt user** - Ask user if they want to continue previous session
> 4. **Auto-resume silently** - Always resume (current behavior of `_load()`)
>
> **Recommendation:** Option 3 (Prompt user) provides transparency while allowing resumption.
>
> **Implementation location:** Update `state_manage.py` with session timeout logic.

#### 7.0.5 Intent Classification Rules

Defines how the skill maps natural language requests to specific workflows. The conversation may be multi-turn to clarify the request, but the output is always invoking a single workflow.

**Classification Strategy:**
- Each request maps to exactly ONE workflow
- Ambiguous requests trigger clarification prompts
- Chained workflows require explicit user statements

**Intent Categories:**

| Intent | Workflow | Primary Keywords | Secondary Signals |
|--------|----------|------------------|-------------------|
| **EVALUATE** | Diagnose/Fix | fix, wrong, incorrect, not working, issue, debug, broken, error, problem | User mentions existing measure/visual not behaving correctly |
| **CREATE_ARTIFACT** | Create measure/column/table/visual | add, create, new, build + (measure, column, calculated, table, visual) | User describes something that doesn't exist yet |
| **CREATE_PAGE** | Create entire page | page, dashboard, screen, view, layout + create/new/build | User wants a new report page with multiple visuals |
| **IMPLEMENT** | Apply changes | apply, deploy, implement, execute, run, push | References to existing findings.md or previous analysis |
| **ANALYZE** | Document existing | explain, document, what does, understand, describe, analyze, summarize | User asking about existing dashboard, not changing it |
| **MERGE** | Compare/merge projects | merge, compare, diff, combine, sync, reconcile | User mentions two projects or versions |

**Intent Detection Flow:**

```
USER REQUEST
    │
    ▼
┌─────────────────────────────────────────┐
│  Step 1: Keyword Scan                    │
│  ─────────────────────────────────────── │
│  • Scan request for primary keywords     │
│  • Score each intent category            │
│  • If single intent scores >70% → use it │
└─────────────────────────────────────────┘
    │
    ▼ (if ambiguous or low confidence)
┌─────────────────────────────────────────┐
│  Step 2: Context Analysis                │
│  ─────────────────────────────────────── │
│  • Check if user referenced files        │
│  • Check for previous workflow in session│
│  • Analyze sentence structure            │
└─────────────────────────────────────────┘
    │
    ▼ (if still ambiguous)
┌─────────────────────────────────────────┐
│  Step 3: Ask for Clarification           │
│  ─────────────────────────────────────── │
│  Present options to user:                │
│  "I can help with that in a few ways:    │
│   [1] Diagnose why it's not working      │
│   [2] Create a new measure for this      │
│   [3] Analyze what currently exists      │
│   Which would you like?"                 │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  Step 4: Invoke Workflow                 │
│  ─────────────────────────────────────── │
│  • Selected workflow begins              │
│  • Workflow handles its own sub-steps    │
└─────────────────────────────────────────┘
```

**Ambiguity Clarification Template:**

```
🔍 CLARIFICATION NEEDED

Your request could be handled by different workflows:

   [E] EVALUATE - Diagnose and fix an issue with existing code
       "The YoY calculation is wrong"

   [C] CREATE - Build a new measure, column, or visual
       "Add a new margin percentage measure"

   [A] ANALYZE - Document and explain what exists
       "What does this dashboard do?"

Which approach fits your needs? [E/C/A]
```

**Chained Workflow Support:**

Workflows can chain, but only with explicit user statements:

```
✅ VALID (explicit):
User: "Create a YoY growth measure"
  → CREATE_ARTIFACT workflow runs, produces findings.md
User: "Now implement those changes"
  → IMPLEMENT workflow runs

✅ VALID (explicit):
User: "Create and deploy a new margin measure"
  → Skill asks: "I'll create the measure first. Would you like me to
    automatically proceed to implementation after, or pause for review?"

❌ INVALID (automatic):
User: "Create a YoY growth measure"
  → CREATE_ARTIFACT completes
  → Skill automatically starts IMPLEMENT without asking
```

**Post-Workflow Suggestions:**

After a workflow completes, the skill MAY suggest logical next steps:

```
✅ Workflow Complete: CREATE_ARTIFACT

📄 Findings saved to: agent_scratchpads/20251220-143000-yoy-growth/findings.md

NEXT STEPS (optional):
  [1] Review the specification before implementing
  [2] Implement now: "implement the changes"
  [3] Create more artifacts: "also add a prior year measure"

What would you like to do?
```

**Edge Cases:**

| Scenario | Handling |
|----------|----------|
| User says "help" or "what can you do" | Display workflow menu with descriptions |
| User provides only a file path | Ask what they want to do with that project |
| User request is completely unrelated to Power BI | Respond that skill is specialized for Power BI |
| User asks about Claude Code itself | Redirect to claude-code-guide agent |

#### 7.0.6 Workflow Execution Sections

Each workflow is a condensed version of the corresponding command, with MCP integration changes highlighted.

---

##### Workflow 1: EVALUATE (Diagnose/Fix)

**Corresponds to:** `/evaluate-pbi-project-file`

**Purpose:** Diagnose issues with existing Power BI code and propose fixes.

**Condensed Flow:**

```
1. VALIDATE PROJECT
   ├─ [MCP MODE] mcp.connection_operations.connect()
   │   └─ Validate connection, get model metadata
   └─ [FALLBACK] powerbi-verify-pbiproject-folder-setup agent
       └─ Parse TMDL files, validate structure

2. CLARIFY PROBLEM (unchanged)
   └─ Interactive Q&A to understand desired outcome
   └─ Human-in-the-loop confirmation

3. CREATE SCRATCHPAD
   └─ agent_scratchpads/<timestamp>-<problem-name>/findings.md

4. INVESTIGATE
   ├─ [MCP MODE] mcp.measure_operations.get() + mcp.dax_query_operations.execute()
   │   └─ Get measure definitions, query actual data
   └─ [FALLBACK] powerbi-code-locator + powerbi-data-context-agent
       └─ Grep TMDL files, XMLA queries

5. PLAN CHANGES
   └─ powerbi-dashboard-update-planner agent (unchanged - LLM reasoning)
   └─ Outputs Section 2 (Proposed Changes)

6. VERIFY
   └─ power-bi-verification agent (unchanged - LLM reasoning)
   └─ Outputs Section 3 (Test Cases)

7. COMPLETE
   └─ Display findings.md location
   └─ Suggest: "implement the changes" to proceed
```

**MCP-Specific Changes:**
- Step 1: Replace folder validation with MCP connection
- Step 4: Replace file grep with `measure_operations.get(name)`
- Step 4: Replace XMLA scripts with `dax_query_operations.execute(query)`

---

##### Workflow 2: CREATE_ARTIFACT (New Measure/Column/Table/Visual)

**Corresponds to:** `/create-pbi-artifact`

**Purpose:** Create new DAX measures, calculated columns, tables, or visuals through interactive specification.

**Condensed Flow:**

```
1. VALIDATE PROJECT
   ├─ [MCP MODE] mcp.connection_operations.connect()
   └─ [FALLBACK] powerbi-verify-pbiproject-folder-setup agent

2. ANALYZE SCHEMA
   ├─ [MCP MODE] mcp.table_operations.list() + mcp.column_operations.list()
   │   └─ Get complete model schema from live connection
   └─ [FALLBACK] powerbi-data-model-analyzer agent
       └─ Parse TMDL files

3. DECOMPOSE (if complex request)
   └─ powerbi-artifact-decomposer agent (unchanged)
   └─ Break into discrete artifacts with dependencies

4. SPECIFY EACH ARTIFACT
   └─ powerbi-data-understanding-agent (unchanged - LLM reasoning)
   └─ Interactive Q&A for business logic, edge cases, formatting

5. DISCOVER PATTERNS
   ├─ [MCP MODE] mcp.measure_operations.list() → LLM pattern analysis
   └─ [FALLBACK] powerbi-pattern-discovery agent
       └─ Grep existing TMDL for patterns

6. GENERATE CODE
   ├─ [MCP MODE] DAX Specialist agent → validates with mcp.dax_query_operations.validate()
   └─ [FALLBACK] powerbi-artifact-designer agent
       └─ Generate DAX, no live validation

7. COMPLETE
   └─ Section 2 in findings.md (Proposed Changes)
   └─ Suggest: "implement the changes" to proceed
```

**MCP-Specific Changes:**
- Step 2: Replace TMDL parsing with MCP schema operations
- Step 5: Replace file grep with MCP list + LLM analysis
- Step 6: Add live DAX validation via MCP

---

##### Workflow 3: CREATE_PAGE (New Dashboard Page)

**Corresponds to:** `/create-pbi-page-specs`

**Purpose:** Create complete specifications for a new Power BI report page including measures, visuals, layout, and interactions.

**Condensed Flow:**

```
1. VALIDATE PROJECT (must have .Report folder)
   ├─ [MCP MODE] mcp.connection_operations.connect() + check PBIR
   └─ [FALLBACK] powerbi-verify-pbiproject-folder-setup agent

2. ANALYZE QUESTION
   └─ powerbi-page-question-analyzer agent (unchanged)
   └─ Classify question type, identify metrics/dimensions

3. ANALYZE SCHEMA
   ├─ [MCP MODE] mcp.table_operations.list() + mcp.measure_operations.list()
   └─ [FALLBACK] powerbi-data-model-analyzer agent

4. DECOMPOSE PAGE
   └─ powerbi-artifact-decomposer agent (page mode, unchanged)
   └─ Identify all measures + visuals needed

5. SPECIFY MEASURES (parallel)
   └─ Same as CREATE_ARTIFACT Steps 4-6 for each measure

6. SPECIFY VISUALS (parallel)
   └─ powerbi-visual-type-recommender agent (unchanged)
   └─ powerbi-data-understanding-agent (visual mode, unchanged)

7. DESIGN LAYOUT
   └─ powerbi-page-layout-designer agent (unchanged - PBIR only)
   └─ Generate coordinates using 8px grid system

8. DESIGN INTERACTIONS
   └─ powerbi-interaction-designer agent (unchanged - PBIR only)
   └─ Cross-filtering matrix, drill-through targets

9. GENERATE PBIR FILES
   └─ powerbi-pbir-page-generator agent (unchanged - PBIR only)
   └─ Complete page.json, visual.json files

10. VALIDATE
    └─ power-bi-verification + powerbi-pbir-validator agents

11. COMPLETE
    └─ Section 2.A (Measures) + Section 2.B (Visuals) + Section 5 (PBIR)
    └─ Suggest: "implement the changes" to proceed
```

**MCP-Specific Changes:**
- Steps 1, 3: MCP for schema extraction
- Steps 5: MCP for DAX validation
- Steps 7-9: PBIR agents unchanged (MCP doesn't support reports)

---

##### Workflow 4: IMPLEMENT (Apply Changes)

**Corresponds to:** `/implement-deploy-test-pbi-project-file`

**Purpose:** Apply proposed changes from findings.md to the project, optionally deploy and test.

**Condensed Flow:**

```
1. VALIDATE FINDINGS
   └─ Read findings.md, extract project path
   └─ Verify Section 2 exists with proposed changes

2. APPLY CODE CHANGES
   ├─ [MCP MODE] mcp.transaction_operations.begin()
   │   └─ For each change in Section 2.A:
   │       └─ mcp.measure_operations.create/update()
   │   └─ mcp.transaction_operations.commit() or rollback()
   └─ [FALLBACK] powerbi-code-implementer-apply agent
       └─ Create versioned copy, write TMDL files

3. VALIDATE TMDL (fallback only)
   └─ [FALLBACK] powerbi-tmdl-syntax-validator agent
   └─ [MCP MODE] Implicit validation during operations

4. VALIDATE DAX
   ├─ [MCP MODE] mcp.dax_query_operations.validate() for each measure
   └─ [FALLBACK] powerbi-dax-review-agent

5. APPLY VISUAL CHANGES (if Section 2.B exists)
   └─ powerbi-visual-implementer-apply agent (unchanged - PBIR)
   └─ Modify visual.json files

6. VALIDATE PBIR
   └─ powerbi-pbir-validator agent (unchanged)

7. DEPLOY (optional, if --deploy)
   ├─ [MCP MODE] mcp.database_operations.deploy()
   └─ [FALLBACK] pbi-tools deploy CLI

8. TEST (optional, if URL available)
   └─ powerbi-playwright-tester agent (unchanged)

9. CONSOLIDATE
   └─ Update findings.md with Section 4 (Results)
```

**MCP-Specific Changes:**
- Step 2: Transaction-based changes instead of file writes
- Step 3: Eliminated (MCP validates implicitly)
- Step 4: MCP validation instead of LLM-only review
- Step 7: MCP deployment instead of pbi-tools CLI

---

##### Workflow 5: ANALYZE (Document Existing)

**Corresponds to:** `/analyze-pbi-dashboard`

**Purpose:** Create business-friendly documentation of an existing Power BI dashboard.

**Condensed Flow:**

```
1. VALIDATE PROJECT
   ├─ [MCP MODE] mcp.connection_operations.connect()
   └─ [FALLBACK] powerbi-verify-pbiproject-folder-setup agent

2. DISCOVER PAGES
   └─ Read .Report/definition/pages/ structure (PBIR only)
   └─ Catalog all pages and visuals

3. EXTRACT MEASURES
   ├─ [MCP MODE] mcp.measure_operations.list() + get() for each
   └─ [FALLBACK] Parse TMDL files

4. ANALYZE TECHNICAL
   └─ For each measure: document DAX, dependencies, usage
   └─ For each visual: document type, fields, filters
   └─ Document relationships and interactions

5. SYNTHESIZE BUSINESS
   └─ LLM translation of technical details to business language
   └─ Create metric definitions, user guides, FAQ

6. COMPLETE
   └─ Generate dashboard_analysis.md with sections:
       - Executive Summary
       - Pages (business-friendly)
       - Metrics Explained
       - Technical Appendix
```

**MCP-Specific Changes:**
- Steps 1, 3: MCP for measure extraction
- Steps 2, 4-5: PBIR/LLM unchanged

---

##### Workflow 6: MERGE (Compare/Merge Projects)

**Corresponds to:** `/merge-powerbi-projects`

**Purpose:** Compare two Power BI projects and merge changes.

**Condensed Flow:**

```
1. VALIDATE BOTH PROJECTS
   ├─ [MCP MODE] Connect to both models
   │   └─ mcp.connection_operations.connect(project_a)
   │   └─ mcp.connection_operations.connect(project_b)
   └─ [FALLBACK] Validate both folder structures

2. EXTRACT SCHEMAS
   ├─ [MCP MODE] mcp.table/column/measure_operations.list() for both
   └─ [FALLBACK] powerbi-data-model-analyzer for both

3. COMPARE
   └─ powerbi-compare-project-code agent (enhanced with MCP data)
   └─ Identify: added, removed, modified objects
   └─ Detect conflicts

4. UNDERSTAND DIFFERENCES
   └─ powerbi-code-understander agent (unchanged - LLM reasoning)
   └─ Explain semantic meaning of each difference

5. PRESENT DECISIONS
   └─ Human-in-the-loop for each conflict
   └─ User chooses: keep A, keep B, merge, skip

6. APPLY MERGE
   ├─ [MCP MODE] mcp.transaction_operations for atomic merge
   │   └─ Apply all decisions in single transaction
   └─ [FALLBACK] powerbi-code-merger agent
       └─ Write merged TMDL files

7. EXPORT (optional)
   └─ Export merged model to TMDL for version control

8. COMPLETE
   └─ Merge report with all decisions documented
```

**MCP-Specific Changes:**
- Steps 1-2: MCP for model extraction
- Step 6: Transactional merge instead of file manipulation
- Step 7: Optional TMDL export for git

---

**Workflow Summary Table:**

| Workflow | Key MCP Benefits | PBIR Required | Agents Replaced |
|----------|------------------|---------------|-----------------|
| EVALUATE | Live data queries, measure lookup | No | code-locator, data-context |
| CREATE_ARTIFACT | Schema extraction, DAX validation | No | data-model-analyzer, code-locator |
| CREATE_PAGE | Schema extraction, DAX validation | **Yes** | data-model-analyzer |
| IMPLEMENT | Transactional changes, deployment | Optional | code-implementer, tmdl-validator |
| ANALYZE | Measure extraction | **Yes** | data-model-analyzer |
| MERGE | Dual-model connect, atomic merge | No | compare, merger |

#### 7.0.7 Specialist Delegation Rules

Defines when the orchestrator delegates to specialized DAX or M-Code agents.

**Delegation Model:**
- Specialists are invoked **automatically** based on artifact type
- Specialists are **isolated** — no cross-invocation between specialists
- Orchestrator handles all coordination between specialists

**Artifact → Specialist Mapping:**

| Artifact Type | Specialist | Reasoning |
|---------------|------------|-----------|
| Measure | DAX Specialist | DAX expressions, filter context, time intelligence |
| Calculated Column | DAX Specialist | Row-context DAX, RELATED functions |
| Calculation Group | DAX Specialist | Format strings, SELECTEDMEASURE patterns |
| KPI | DAX Specialist | Goal measures, status expressions |
| Partition (M query) | M-Code Specialist | Power Query, ETL, query folding |
| Named Expression | M-Code Specialist | Shared expressions, parameters |
| Table (Import) | M-Code Specialist | Source queries, transformations |
| Table (Calculated) | DAX Specialist | DAX table expressions |
| Relationship | Orchestrator | Simple metadata, no code generation |
| Visual | Orchestrator | PBIR editing, no calculation logic |

**Delegation Flow:**

```
ORCHESTRATOR receives artifact request
    │
    ▼
┌─────────────────────────────────────────┐
│  Step 1: Classify Artifact Type          │
│  ─────────────────────────────────────── │
│  • Parse artifact description            │
│  • Match to type in mapping table        │
│  • Determine specialist or self-handle   │
└─────────────────────────────────────────┘
    │
    ├─ DAX Artifact ──────────────────────┐
    │                                      ▼
    │                        ┌─────────────────────────┐
    │                        │   DAX Specialist Agent   │
    │                        │   ───────────────────── │
    │                        │   Input:                 │
    │                        │   • Business requirement │
    │                        │   • Model schema         │
    │                        │   • Existing patterns    │
    │                        │   Output:                │
    │                        │   • Validated DAX        │
    │                        │   • Format string        │
    │                        │   • Display folder       │
    │                        └─────────────────────────┘
    │                                      │
    ├─ M-Code Artifact ───────────────────┤
    │                                      ▼
    │                        ┌─────────────────────────┐
    │                        │  M-Code Specialist Agent │
    │                        │   ───────────────────── │
    │                        │   Input:                 │
    │                        │   • Data source specs    │
    │                        │   • Transformation logic │
    │                        │   Output:                │
    │                        │   • M query              │
    │                        │   • Privacy level        │
    │                        │   • Query folding notes  │
    │                        └─────────────────────────┘
    │                                      │
    └─ Simple Artifact ───────────────────┤
                                           ▼
                             ┌─────────────────────────┐
                             │   Orchestrator Handles   │
                             │   ───────────────────── │
                             │   • Relationships        │
                             │   • Visual PBIR edits    │
                             │   • Metadata changes     │
                             └─────────────────────────┘
                                           │
                                           ▼
                             ┌─────────────────────────┐
                             │   Results → findings.md  │
                             └─────────────────────────┘
```

**Multi-Artifact Coordination:**

When a request requires BOTH DAX and M-Code artifacts (e.g., "create a table with calculated columns"):

```
ORCHESTRATOR
    │
    ├─ 1. Decompose into artifacts (powerbi-artifact-decomposer)
    │      └─ Partition → M-Code Specialist
    │      └─ Calculated Column → DAX Specialist (depends on table)
    │
    ├─ 2. Execute M-Code Specialist FIRST (table must exist)
    │      └─ Write M query to findings.md Section 2
    │
    ├─ 3. Execute DAX Specialist SECOND (table now exists)
    │      └─ Reference table from step 2
    │      └─ Write DAX to findings.md Section 2
    │
    └─ 4. Orchestrator assembles final Section 2
```

**Specialist Isolation Rules:**

- Specialists **CANNOT** invoke each other
- Specialists **CANNOT** invoke other agents
- Specialists read from findings.md (input)
- Specialists write to findings.md (output)
- Orchestrator controls execution order based on dependencies

**MCP Tool Access by Specialist:**

| Specialist | MCP Tools Available |
|------------|---------------------|
| DAX Specialist | `measure_operations.create/update`, `dax_query_operations.validate/execute`, `column_operations.create` (calculated) |
| M-Code Specialist | `partition_operations.create/update`, `table_operations.create`, `named_expression_operations` |
| Orchestrator | All MCP tools (orchestration) |

#### 7.0.8 State Management Patterns

Defines how the skill maintains session state via state.json and coordinates agent communication via the Task Blackboard pattern.

**Implementation Reference:**
> The state management implementation is defined in `state_manage.py` in this specification folder.
> The blackboard template is defined in `findings_template.md`.

---

##### 7.0.8.1 State File Locations

```
Project Root/
├── .claude/
│   ├── state.json              ← Global session state (singleton)
│   └── tasks/
│       └── <task-id>/
│           └── findings.md     ← Task-specific blackboard
```

**Migration Note:** Current workflows use `agent_scratchpads/<timestamp>-<problem>/`. The skill will use `.claude/tasks/<task-id>/` for consistency with state_manage.py. The `agent_scratchpads/` pattern is deprecated for new workflows.

---

##### 7.0.8.2 Complete State Schema

```json
{
  "session": {
    "started": "2025-12-20T10:30:00Z",
    "last_activity": "2025-12-20T14:45:00Z",
    "skill_version": "1.0.0",
    "mcp_available": true,
    "connection": {
      "type": "desktop|fabric|pbip|file_fallback",
      "status": "connected|disconnected|error",
      "details": {
        "desktop_port": 12345,
        "fabric_workspace": "workspace-guid",
        "fabric_dataset": "dataset-guid",
        "pbip_path": "C:/Projects/SalesReport"
      },
      "established_at": "2025-12-20T10:31:00Z"
    }
  },
  "model_schema": {
    "tables": [
      {
        "name": "Sales",
        "columns": ["Date", "Amount", "ProductID"],
        "measures": ["Total Sales", "YoY Growth"]
      }
    ],
    "relationships": [
      {"from": "Sales.ProductID", "to": "Products.ID", "cardinality": "many-to-one"}
    ],
    "last_synced": "2025-12-20T10:31:05Z",
    "sync_source": "mcp|tmdl_parse"
  },
  "active_tasks": {
    "fix-yoy-calc-1734700200": {
      "path": ".claude/tasks/fix-yoy-calc-1734700200",
      "status": "in_progress",
      "workflow_type": "evaluate",
      "created": "2025-12-20T10:30:00Z",
      "updated": "2025-12-20T10:45:00Z",
      "current_stage": "dax_specialist"
    }
  },
  "resource_locks": {
    "definition/tables/Sales.tmdl": "fix-yoy-calc-1734700200",
    "definition/pages/Overview/visuals/card1.json": "fix-yoy-calc-1734700200"
  },
  "validation_cache": {
    "last_dax_validation": {
      "task_id": "fix-yoy-calc-1734700200",
      "timestamp": "2025-12-20T10:42:00Z",
      "result": "passed",
      "measures_validated": ["YoY Growth"]
    }
  },
  "archived_tasks": [
    {
      "task_id": "add-margin-measure-1734690000",
      "completed": "2025-12-20T08:00:00Z",
      "summary": "Added Margin % measure with DIVIDE pattern"
    }
  ]
}
```

---

##### 7.0.8.3 Session Recovery Behavior

**Decision: Prompt User if Session Exists**

When skill initializes and finds existing state.json:

```
🔄 PREVIOUS SESSION DETECTED

Last activity: 2025-12-20 14:45:00 (2 hours ago)
Active tasks: 1 (fix-yoy-calc-1734700200)

Options:
  [R] Resume previous session
  [N] Start fresh (archives existing tasks)
  [V] View active task details

Choice: _
```

**Session Timeout Rules:**
| Time Since Last Activity | Behavior |
|--------------------------|----------|
| < 4 hours | Prompt to resume or start fresh |
| 4-24 hours | Warn about staleness, recommend fresh start |
| > 24 hours | Auto-archive, start fresh (with notification) |

**Recovery Logic:**
```python
def should_prompt_resume(state):
    last_activity = parse_iso(state["session"]["last_activity"])
    hours_elapsed = (now() - last_activity).total_seconds() / 3600

    if hours_elapsed > 24:
        return "auto_archive"
    elif hours_elapsed > 4:
        return "warn_stale"
    elif state["active_tasks"]:
        return "prompt_resume"
    else:
        return "fresh_start"
```

---

##### 7.0.8.4 Task Lifecycle

```
CREATE                  IN_PROGRESS              COMPLETE/FAIL           ARCHIVE
   │                        │                         │                     │
   ▼                        ▼                         ▼                     ▼
┌─────────┐  start    ┌───────────┐  finish    ┌───────────┐  archive ┌─────────┐
│ pending │ ────────► │in_progress│ ─────────► │ completed │ ───────► │archived │
└─────────┘           └───────────┘            │   failed  │          └─────────┘
                            │                  └───────────┘
                            │
                      ┌─────┴─────┐
                      ▼           ▼
               [DAX Specialist]  [M-Code Specialist]
               writes to         writes to
               findings.md       findings.md
```

**Lifecycle Commands:**

| Stage | Command | State Change |
|-------|---------|--------------|
| Create | `--create_task "name"` | `null → pending → in_progress` |
| Update Stage | `--update_stage <task_id> <stage>` | Updates `current_stage` |
| Complete | `--complete <task_id>` | `in_progress → completed` |
| Fail | `--fail <task_id> "reason"` | `in_progress → failed` |
| Archive | `--archive <task_id>` | Moves to `archived_tasks[]`, clears locks |

---

##### 7.0.8.5 Agent Communication Protocol (Task Blackboard Pattern)

Specialists communicate via the **Task Blackboard** (`findings.md`), not directly with each other.

**Blackboard Structure:**

```markdown
# Task Blackboard: [TASK_NAME]
**Status:** 🟡 In-Progress | 🟢 Complete | 🔴 Failed
**Task ID:** [TASK_ID]
**Workflow:** [evaluate|create|implement|analyze|merge]

---

## Section 1: Requirements (Orchestrator)
*Written by: powerbi-artifact-designer (Orchestrator)*
- **Goal:** [User intent in business terms]
- **Artifacts Needed:**
  - [ ] Measure: [Name] → DAX Specialist
  - [ ] Partition: [Name] → M-Code Specialist
  - [ ] Visual: [Type] → Orchestrator (PBIR)

---

## Section 2: DAX Logic (DAX Specialist)
*Written by: powerbi-dax-specialist*
- **Measures Created:**
  ```dax
  [Measure Name] = DIVIDE(SUM(Sales[Amount]), ...)
  ```
- **Validation:** ✅ Passed via MCP dax_query_operations.validate()
- **Dependencies:** [List of referenced measures/columns]

---

## Section 3: M-Code Logic (M-Code Specialist)
*Written by: powerbi-mcode-specialist*
- **Partitions Created:**
  ```m
  let Source = ... in FinalTable
  ```
- **Query Folding:** ✅ Folds to source
- **Privacy Level:** Organizational

---

## Section 4: Implementation (Orchestrator)
*Written by: powerbi-artifact-designer after specialist sections complete*
- **TMDL Changes:**
  - File: `definition/tables/Sales.tmdl`
  - Operation: CREATE measure [YoY Growth]
- **PBIR Changes:**
  - File: `definition/pages/Overview/visuals/card1.json`
  - Operation: UPDATE dataBindings

---

## Section 5: Validation Results
*Written by: Validation agents after implementation*
- **DAX Review:** ✅ Passed
- **PBIR Validation:** ✅ Passed
- **TMDL Syntax:** ✅ Passed

---

## Section 6: Final Manifest
*Moved to state.json archived_tasks on completion*
- **Summary:** Added YoY Growth measure using SAMEPERIODLASTYEAR pattern
```

**Communication Rules:**

| Agent | Reads | Writes |
|-------|-------|--------|
| Orchestrator | User request, state.json | Section 1, Section 4, Final Manifest |
| DAX Specialist | Section 1, state.json (model_schema) | Section 2 |
| M-Code Specialist | Section 1, state.json (model_schema) | Section 3 |
| Validators | Section 2-4 | Section 5 |

**Isolation Rules:**
- Specialists CANNOT read each other's sections until Orchestrator signals completion
- Specialists CANNOT invoke other agents
- Specialists CANNOT modify state.json (only Orchestrator can)
- All cross-agent data flows through findings.md

---

##### 7.0.8.6 Resource Locking Protocol

Locks prevent concurrent modification of the same file by multiple tasks.

**When to Lock:**

| Operation | Requires Lock |
|-----------|---------------|
| Read TMDL/PBIR | No |
| Write TMDL measure | Yes (table file) |
| Write PBIR visual | Yes (visual.json) |
| Write PBIR page | Yes (entire page folder) |
| MCP operations | No (MCP handles internally) |

**Lock Acquisition Flow:**

```
BEFORE FILE WRITE
    │
    ▼
┌─────────────────────────────────────────┐
│  python state_manage.py --lock          │
│    definition/tables/Sales.tmdl         │
│    --task_id fix-yoy-calc-1734700200    │
└─────────────────────────────────────────┘
    │
    ├─ Lock acquired ────────► Proceed with write
    │
    └─ Lock denied ──────────► STOP
                               │
                               ▼
                    ┌─────────────────────────┐
                    │ ⚠️ RESOURCE LOCKED        │
                    │                          │
                    │ File: Sales.tmdl         │
                    │ Locked by: task-abc-123  │
                    │                          │
                    │ Wait for other task to   │
                    │ complete, or force       │
                    │ release with --force     │
                    └─────────────────────────┘
```

**Lock Cleanup:**
- Locks are automatically released when task is archived
- Stale locks (task no longer in active_tasks) can be force-released
- Locks older than 24 hours are auto-released with warning

---

##### 7.0.8.7 Model Schema Caching Strategy

The `model_schema` in state.json caches table/column/measure/relationship metadata to avoid repeated MCP calls.

**Cache Invalidation Rules:**

| Event | Cache Action |
|-------|--------------|
| Session start | Refresh from MCP/TMDL |
| After IMPLEMENT workflow | Refresh affected tables |
| After MERGE workflow | Full refresh |
| MCP operation fails | Mark as stale, refresh on next read |
| Manual request | `--refresh_schema` |

**Staleness Detection:**
```python
def is_schema_stale(state):
    if not state["model_schema"]["last_synced"]:
        return True

    last_sync = parse_iso(state["model_schema"]["last_synced"])
    # Stale if older than 1 hour or different session
    return (now() - last_sync).total_seconds() > 3600
```

**Refresh Strategy:**
- **MCP Mode:** Call `table_operations.list()`, `measure_operations.list()`
- **Fallback Mode:** Parse TMDL files from `.SemanticModel/definition/`

---

##### 7.0.8.8 Specialist Naming Convention

**Canonical Agent Names:**

| Role | Agent File | findings.md Section |
|------|------------|---------------------|
| Orchestrator | `powerbi-artifact-designer.md` | Section 1, 4, 6 |
| DAX Specialist | `powerbi-dax-specialist.md` | Section 2 |
| M-Code Specialist | `powerbi-mcode-specialist.md` | Section 3 |
| Validators | Various (`powerbi-dax-review-agent.md`, etc.) | Section 5 |

**Deprecated Naming:**
The following names appear in older documents and are deprecated:
- `visual_analyst.md` → Use Orchestrator for analysis tasks
- `visual_specialist.md` → Use Orchestrator for PBIR tasks

---

##### 7.0.8.9 CLI Command Reference

Complete CLI interface for `state_manage.py`:

```bash
# Session Management
python state_manage.py --summary                    # Show state summary
python state_manage.py --refresh_schema             # Refresh model_schema from source
python state_manage.py --reset                      # Clear all state (dangerous)

# Task Management
python state_manage.py --create_task "task-name"    # Create new task, returns task_id
python state_manage.py --update_stage <id> <stage>  # Update current_stage
python state_manage.py --complete <id>              # Mark task completed
python state_manage.py --fail <id> "reason"         # Mark task failed
python state_manage.py --archive <id>               # Archive completed task
python state_manage.py --list_tasks                 # List active tasks

# Lock Management
python state_manage.py --lock <path> --task_id <id>     # Acquire lock
python state_manage.py --release <path> --task_id <id>  # Release lock
python state_manage.py --list_locks                     # List all locks
python state_manage.py --force_release <path>           # Force release (admin)

# Schema Cache
python state_manage.py --get_schema                 # Return cached model_schema
python state_manage.py --set_schema <json>          # Update model_schema (after MCP)
```

---

#### 7.0.9 Error Handling and Fallback Logic

Defines how the skill handles errors and falls back to file-based operations.

**Fallback Mode: Warn Per Operation**

When MCP is unavailable or fails, the skill warns for EACH degraded operation:

```
⚠️ MCP FALLBACK: measure_operations.get() unavailable
   └─ Using file-based search (grep TMDL files) instead
   └─ Capability impact: No live validation, slower search

[Operation proceeds with fallback method]
```

**Error Categories:**

| Category | Severity | Behavior |
|----------|----------|----------|
| MCP Connection Failed | Warning | Switch to fallback, warn once |
| MCP Operation Failed | Warning | Fallback for that operation, warn |
| MCP Timeout | Warning | Retry once, then fallback |
| File Not Found | Error | Abort operation, show fix guidance |
| Permission Denied | Error | Abort operation, show settings guidance |
| Validation Failed | Blocking | Halt workflow, require fix |
| Syntax Error in Code | Blocking | Halt workflow, show error details |

**Fallback Capability Matrix:**

| Operation | MCP Mode | Fallback Mode | Degradation |
|-----------|----------|---------------|-------------|
| Get measure definition | `measure_operations.get()` | Grep TMDL files | No validation |
| Validate DAX | `dax_query_operations.validate()` | LLM syntax check only | May miss runtime errors |
| Query data | `dax_query_operations.execute()` | XMLA via Python | Requires separate auth |
| Create measure | `measure_operations.create()` | Write TMDL file | No transaction support |
| Deploy | `database_operations.deploy()` | pbi-tools CLI | Different auth flow |
| Schema extraction | `table_operations.list()` | Parse TMDL files | May be stale |

**Fallback Warning Template:**

```
⚠️ DEGRADED CAPABILITY

Operation: [operation name]
MCP Status: [unavailable | failed | timeout]
Fallback: [fallback method]

Impact:
• [specific capability lost]
• [workaround or limitation]

Proceeding with fallback method...
```

---

#### 7.0.10 Validation Gate Integration

Defines validation checkpoints and their blocking behavior.

**Validation Strategy: Balanced**
- **Critical errors** → Block workflow, require fix
- **Minor warnings** → Allow continue with acknowledgment

**Validation Gates:**

| Gate | When | Critical (Blocks) | Warning (Continues) |
|------|------|-------------------|---------------------|
| TMDL Syntax | After code generation | Parse errors, invalid structure | Formatting inconsistencies |
| DAX Validation | After measure creation | Syntax errors, invalid references | Performance concerns, style |
| PBIR Validation | After visual edits | Invalid JSON, missing properties | Non-standard formatting |
| Dependency Check | Before implementation | Circular references, missing objects | Unused dependencies |
| Schema Validation | Before deployment | Type mismatches, broken relationships | Schema warnings |

**Validation Flow:**

```
VALIDATION GATE
    │
    ├─ No Issues ───────────────────────── ✅ Continue
    │
    ├─ Warnings Only ──────────────────────┐
    │                                       ▼
    │                         ┌─────────────────────────┐
    │                         │   ⚠️ WARNINGS DETECTED   │
    │                         │   ─────────────────────  │
    │                         │   1. [warning 1]         │
    │                         │   2. [warning 2]         │
    │                         │                          │
    │                         │   [C]ontinue with warnings│
    │                         │   [R]eview details        │
    │                         │   [F]ix before proceeding │
    │                         └─────────────────────────┘
    │                                       │
    │                                       ▼
    │                         (User chooses to continue)
    │                                       │
    └─ Critical Errors ────────────────────┤
                                            ▼
                              ┌─────────────────────────┐
                              │   ❌ VALIDATION FAILED   │
                              │   ─────────────────────  │
                              │   Critical issues found: │
                              │   1. [error 1]           │
                              │   2. [error 2]           │
                              │                          │
                              │   Workflow halted.       │
                              │   Fix issues and retry.  │
                              └─────────────────────────┘
```

**MCP vs Fallback Validation:**

| Validation | MCP Mode | Fallback Mode |
|------------|----------|---------------|
| DAX Syntax | `dax_query_operations.validate()` — authoritative | LLM check — best effort |
| TMDL Structure | Implicit during operations | `tmdl_format_validator.py` |
| Runtime Errors | Detected during validate | Not detectable |
| Schema Consistency | MCP enforces | Manual check |

---

#### 7.0.11 Human-in-the-Loop Patterns

Defines when the skill requires explicit user confirmation.

**Confirmation Strategy: Confirm Major Only**

Explicit confirmation required for:
- Implement (applying changes to project)
- Deploy (pushing to Power BI Service)
- Delete (removing objects)

Auto-proceed allowed for:
- Analyze (read-only)
- Create specs (writes to scratchpad only)
- Pattern discovery (read-only)

**Confirmation Categories:**

| Action | Confirmation Required | Reason |
|--------|----------------------|--------|
| Implement changes | **Yes** | Modifies project files |
| Deploy to service | **Yes** | Affects production |
| Delete measure/table | **Yes** | Destructive action |
| Overwrite findings.md | **Yes** | Loses previous work |
| Create scratchpad | No | Safe, timestamped |
| Read project files | No | Non-destructive |
| Query data via MCP | No | Read-only |
| Analyze dashboard | No | Read-only |
| Generate specs | No | Writes to scratchpad |

**Confirmation Templates:**

**Before Implementation:**
```
📋 IMPLEMENTATION CONFIRMATION

The following changes will be applied to your project:

PROJECT: C:\Projects\SalesReport
CHANGES:
  ✏️  MODIFY: [Total Sales] measure
  ➕  CREATE: [YoY Growth %] measure
  ➕  CREATE: [Prior Year Sales] measure

This will create a versioned copy at:
  C:\Projects\SalesReport_20251220_143000\

[Y] Proceed with implementation
[N] Cancel and review changes
[R] Review proposed changes in findings.md
```

**Before Deployment:**
```
🚀 DEPLOYMENT CONFIRMATION

You are about to deploy to Power BI Service:

ENVIRONMENT: DEV
WORKSPACE: Sales Analytics
DATASET: Sales Report Model

This will:
  • Upload the semantic model
  • Replace the existing dataset
  • Trigger a data refresh

[Y] Deploy now
[N] Cancel deployment
[S] Skip deployment, keep local changes only
```

**Before Destructive Action:**
```
⚠️ DESTRUCTIVE ACTION CONFIRMATION

You are about to DELETE:

  🗑️  Measure: [Obsolete Metric]
  📁  Location: Sales.tmdl line 145

This action cannot be undone automatically.
A backup will be created before deletion.

[Y] Delete and create backup
[N] Cancel
```

---

#### 7.0.12 Format-Specific Handling

Defines how the skill handles different Power BI project formats.

**Format Strategy: PBIP Preferred, Others with Guidance**

| Format | Support Level | MCP Compatible | Notes |
|--------|---------------|----------------|-------|
| .pbip (Power BI Project) | **Full** | Yes | Native format, all features |
| .pbix (Power BI Desktop) | Conversion | After extraction | Must extract first |
| pbi-tools extracted | Partial | Yes (semantic model) | No PBIR support |
| model.bim (SSAS) | Read-only | Via MCP | Analysis only |

**Format Detection Flow:**

```
USER PROVIDES PATH
    │
    ▼
┌─────────────────────────────────────────┐
│  Detect Format                           │
│  ─────────────────────────────────────── │
│  • .pbip file present → PBIP format      │
│  • .pbix file → PBIX (needs extraction)  │
│  • .SemanticModel/ only → pbi-tools      │
│  • model.bim → Legacy/SSAS               │
└─────────────────────────────────────────┘
    │
    ├─ PBIP ─────────────────── ✅ Full support, proceed
    │
    ├─ PBIX ─────────────────── ⚠️ Extraction required
    │                             │
    │                             ▼
    │                 ┌─────────────────────────┐
    │                 │  PBIX DETECTED           │
    │                 │  ─────────────────────── │
    │                 │  This file needs to be   │
    │                 │  converted to .pbip      │
    │                 │                          │
    │                 │  Options:                │
    │                 │  [1] Extract with pbi-tools│
    │                 │  [2] Convert in Desktop  │
    │                 │  [3] Show instructions   │
    │                 └─────────────────────────┘
    │
    ├─ pbi-tools ────────────── ⚠️ Partial support
    │                             │
    │                             ▼
    │                 ┌─────────────────────────┐
    │                 │  PBI-TOOLS FORMAT        │
    │                 │  ─────────────────────── │
    │                 │  Semantic model: ✅ Full │
    │                 │  Visual editing: ❌ None │
    │                 │                          │
    │                 │  For visual changes,     │
    │                 │  convert to .pbip format │
    │                 └─────────────────────────┘
    │
    └─ Unknown ──────────────── ❌ Error with guidance
```

**PBIP Format (Full Support):**

```
project/
├── project.pbip              ← Project file (detected)
├── project.SemanticModel/    ← Semantic model (TMDL)
│   └── definition/
│       ├── model.tmdl
│       └── tables/
└── project.Report/           ← Report definition (PBIR)
    └── definition/
        ├── definition.pbir
        └── pages/
```

Features available:
- All 6 workflows
- MCP integration
- PBIR visual editing
- Full deployment

**PBIX Conversion Guidance:**

```
📦 PBIX FILE DETECTED

To use this file with the Power BI Analyst skill, convert it to
Power BI Project format:

OPTION 1: Using Power BI Desktop (Recommended)
─────────────────────────────────────────────
1. Open Power BI Desktop
2. File → Open → Select your .pbix file
3. File → Save As → Power BI Project
4. Choose location and name
5. Re-run skill with the new .pbip folder

OPTION 2: Using pbi-tools CLI
─────────────────────────────────────────────
pbi-tools extract "C:\path\to\file.pbix"

Note: pbi-tools extraction creates a different folder structure
that has limited visual editing support.
```

**pbi-tools Format (Partial Support):**

```
project/                      ← Extracted folder
├── Model/                    ← Semantic model
│   └── database.json
└── Report/                   ← Report (limited structure)
    └── report.json
```

Limitations:
- No PBIR visual editing (different structure)
- CREATE_PAGE workflow unavailable
- Visual changes require manual Power BI Desktop work

**7.1 Create Skill Structure**
- [ ] Create `.claude/skills/powerbi-analyst/` folder
- [ ] Create `skill.md` with full skill definition (expand from placeholder)
- [ ] Move/reference agents into skill
- [ ] Define MCP dependency
- [ ] Add PBIR format validation (Enhanced vs Legacy detection)
- [ ] Add schema version checking logic

**7.2 Document Skill Usage**
- [ ] Create user guide
- [ ] Document prerequisites (MCP installation)
- [ ] Create quick start examples
- [ ] Add troubleshooting

**7.3 Test as Skill**
- [ ] Test skill invocation
- [ ] Verify MCP integration works via skill
- [ ] Test all commands
- [ ] Fix any skill-specific issues

**Estimated Effort:** 4-8 hours

---

### Phase 8: Cleanup

**8.1 Remove Deprecated Code**
- [ ] Delete replaced agent files
- [ ] Delete Python TMDL parsing scripts (if not needed for PBIR)
- [ ] Delete Python XMLA scripts
- [ ] Update tool documentation

**8.2 Final Documentation**
- [ ] Update README.md with new architecture
- [ ] Update CLAUDE.md
- [ ] Create architecture diagram
- [ ] Document breaking changes

**Estimated Effort:** 2-4 hours

---

## 5. Risk Assessment

### 5.1 High Risk

**MCP Availability:**
- MCP is closed-source, binary-only
- Microsoft controls updates and compatibility
- No fallback if MCP has bugs

**Mitigation:**
- Keep file-based agents as fallback (don't delete immediately)
- Document manual workarounds
- Monitor MCP issues on GitHub

**Authentication Complexity:**
- Fabric auth may not work in all tenants
- Desktop connection requires running instance
- Azure Identity SDK dependencies

**Mitigation:**
- Support all three connection types
- Provide clear auth troubleshooting
- Test in multiple environments

### 5.2 Medium Risk

**Breaking Changes:**
- Commands will behave differently
- Error messages will change
- Some edge cases may not be covered

**Mitigation:**
- Phased rollout
- Keep old agents during transition
- Comprehensive testing

**PBIR Agents Unchanged:**
- Still need file manipulation for reports
- Maintaining two paradigms (MCP + files)

**Mitigation:**
- Clear separation in architecture
- Document which agents use which approach

### 5.3 Low Risk

**Performance:**
- MCP may be slower/faster than file ops
- Transaction overhead

**Mitigation:**
- Benchmark key operations
- Optimize if needed

---

## 6. Success Criteria

### 6.1 Functional

- [ ] All 4 commands work with MCP backend
- [ ] Can connect to Power BI Desktop
- [ ] Can connect to Fabric workspace
- [ ] Can connect to PBIP folder
- [ ] Transactions rollback on failure
- [ ] Deployment works via MCP
- [ ] PBIR agents work unchanged

### 6.2 Quality

- [ ] Agent count reduced from 27 to ~18 (net reduction of 9, with 2 new specialists)
- [ ] No pbi-tools dependency for semantic model ops
- [ ] Python dependencies reduced
- [ ] Error messages are clear and actionable

### 6.3 Documentation

- [ ] README updated with MCP architecture
- [ ] Skill documentation complete
- [ ] Troubleshooting guide updated
- [ ] Breaking changes documented

---

## 7. Timeline Estimate

| Phase | Effort | Cumulative |
|-------|--------|------------|
| Phase 1: Cleanup | 2-4 hrs | 2-4 hrs |
| Phase 2: Core MCP | 8-16 hrs | 10-20 hrs |
| Phase 2.5: Specialists | 6-10 hrs | 16-30 hrs |
| Phase 3: Implementation | 8-16 hrs | 24-46 hrs |
| Phase 4: Merge | 4-8 hrs | 28-54 hrs |
| Phase 5: Patterns | 2-4 hrs | 30-58 hrs |
| Phase 6: Commands | 8-12 hrs | 38-70 hrs |
| Phase 7: Skill | 4-8 hrs | 42-78 hrs |
| Phase 8: Cleanup | 2-4 hrs | 44-82 hrs |

**Total Estimate:** 44-82 hours (~1.5-2 weeks full-time)

---

## 8. Open Questions

1. **Offline Support:** Should we keep file-based agents for offline use (no Desktop/Fabric)?

2. **PBIR via MCP:** Will Microsoft add report support to MCP? If so, when?

3. **Skill Distribution:** How will we distribute the skill with MCP dependency?

4. **Version Control:** MCP works on live models - how do we maintain TMDL for git?
   - Option A: Export TMDL after changes
   - Option B: Keep PBIP as source of truth, sync via MCP

5. **Transaction Scope:** Can we batch all changes in one transaction, or per-object?

6. **Error Recovery:** If MCP fails mid-operation, what's the recovery path?

---

## 9. Next Steps

1. **Immediate:** Delete deprecated agents (Phase 1.1)
2. **This Week:** Set up MCP and test connection types (Phase 2.1)
3. **Decide:** Offline support strategy (Question 1)
4. **Prioritize:** Start with /evaluate command (most used)

---

## Appendix A: MCP Tool Reference

See: https://github.com/microsoft/powerbi-modeling-mcp

Key operations:
- connection_operations
- database_operations
- table_operations
- column_operations
- measure_operations
- relationship_operations
- dax_query_operations
- transaction_operations
- partition_operations
- calculation_group_operations

---

## Appendix B: Agent Mapping Reference

| Current Agent | Target | MCP Tools |
|---------------|--------|-----------|
| powerbi-verify-pbiproject-folder-setup | REPLACE | connection_operations |
| powerbi-data-model-analyzer | REPLACE | table/column/measure_operations |
| powerbi-data-context-agent | REPLACE | dax_query_operations |
| powerbi-code-locator | REPLACE | measure_operations.get() |
| powerbi-code-implementer-apply | REPLACE | transaction + CRUD operations |
| powerbi-tmdl-syntax-validator | REMOVE | (implicit validation) |
| powerbi-dax-review-agent | ENHANCE | dax_query_operations.validate() |
| powerbi-pattern-discovery | ENHANCE | measure_operations.list() |
| powerbi-compare-project-code | ENHANCE | multi-model read |
| powerbi-code-merger | REPLACE | transaction + CRUD |
| powerbi-code-fix-identifier | DELETE | (deprecated) |
| pbir-visual-edit-planner | DELETE | (deprecated) |
| powerbi-visual-locator | KEEP | (PBIR) |
| powerbi-visual-implementer-apply | KEEP | (PBIR) |
| powerbi-pbir-validator | KEEP | (PBIR) |
| powerbi-page-* (5 agents) | KEEP | (PBIR) |
| powerbi-dashboard-update-planner | KEEP | (LLM reasoning) |
| powerbi-artifact-designer | REFACTOR | Becomes Orchestrator for specialists |
| powerbi-artifact-decomposer | KEEP | (LLM reasoning) |
| powerbi-data-understanding-agent | KEEP | (LLM reasoning) |
| power-bi-verification | KEEP | (LLM reasoning) |
| powerbi-code-understander | KEEP | (LLM reasoning) |
| powerbi-playwright-tester | KEEP | (testing) |
| **NEW: powerbi-dax-specialist** | CREATE | measure_operations, dax_query_operations |
| **NEW: powerbi-mcode-specialist** | CREATE | partition_operations, named_expressions |

---

## Appendix C: Findings Template (findings_template.md)

The `findings.md` file serves as the **Task Blackboard** where specialists write their outputs. Each task gets its own findings file in the task folder.

> **Full Template:** See `findings_template.md` in this specification folder for the complete template.
> **Detailed Protocol:** See Section 7.0.8.5 for the Agent Communication Protocol.

**Structure Summary:**

```markdown
# Task Blackboard: [TASK_NAME]
**Status:** 🟡 In-Progress | 🟢 Complete | 🔴 Failed
**Task ID:** [auto-generated]
**Workflow:** [evaluate|create|implement|analyze|merge]

## Section 1: Requirements (Orchestrator)
- Goal, project path, artifacts needed

## Section 2: DAX Logic (DAX Specialist)
- Measures created with DAX formulas, validation status

## Section 3: M-Code Logic (M-Code Specialist)
- Partitions created, query folding status, privacy levels

## Section 4: Implementation (Orchestrator)
- TMDL changes, PBIR changes, MCP operations

## Section 5: Validation Results
- DAX review, PBIR validation, TMDL syntax results

## Section 6: Final Manifest
- Summary moved to state.json archived_tasks upon archival
```

**Usage Pattern:**
1. Orchestrator creates task, writes Section 1
2. DAX Specialist reads Section 1 + state.json, writes Section 2
3. M-Code Specialist reads Section 1 + state.json, writes Section 3
4. Orchestrator reads Sections 2-3, writes Section 4 (implementation plan)
5. Validators read Sections 2-4, write Section 5
6. Orchestrator writes Section 6, archives task

---

## Appendix D: State Manager (state_manage.py)

The `PBIStateManager` class maintains session-level "Global Truth" in `.claude/state.json`.

> **Complete Specification:** See Section 7.0.8 for the full state management specification including:
> - Complete state schema (7.0.8.2)
> - Session recovery behavior (7.0.8.3)
> - Task lifecycle (7.0.8.4)
> - Agent communication protocol (7.0.8.5)
> - Resource locking protocol (7.0.8.6)
> - Model schema caching (7.0.8.7)
> - CLI command reference (7.0.8.9)

**Core Features:**

| Feature | Method | Purpose |
|---------|--------|---------|
| State Persistence | `_load()` / `save()` | JSON read/write to `.claude/state.json` |
| Task Creation | `create_task(name)` | Creates timestamped task folder in `.claude/tasks/` |
| Resource Locking | `acquire_lock(resource, task_id)` | Prevents concurrent edits to same file |
| Lock Release | `release_lock(resource, task_id)` | Frees resource after task completion |

**Current Implementation:**
The `state_manage.py` in this specification folder is a **skeleton** that demonstrates the pattern.
Implementation work is tracked in Phase 2 of the work breakdown.

**Key CLI Commands:**

```bash
# Session Management
python state_manage.py --summary              # Show state, detect session recovery

# Task Management
python state_manage.py --create_task "name"   # Create task workspace
python state_manage.py --archive <task_id>    # Archive completed task

# Lock Management
python state_manage.py --lock <path> --task_id <id>     # Acquire lock
python state_manage.py --release <path> --task_id <id>  # Release lock
```

**Integration with Skill:**
- Orchestrator calls `--summary` at session start (triggers recovery prompt if needed)
- Each sub-agent receives `TASK_PATH` and writes to `findings.md`
- Locks prevent race conditions when multiple agents work in parallel
- State is archived when task completes via `--archive`
- Archived task summaries persist in `archived_tasks[]` for project memory
