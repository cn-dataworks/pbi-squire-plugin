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
- Package as a Claude Code skill with automated installer

**Distribution Philosophy: Driver/Installer Pattern**

The skill uses a **Driver/Installer Pattern** rather than a static skill package. This is necessary because:
1. The Microsoft Power BI Modeling MCP is an external binary dependency
2. MCP availability varies by user environment (installed vs. not installed)
3. Configuration must be dynamic based on detected capabilities

The skill includes installer scripts (`install.ps1` for Windows, `install.sh` for macOS/Linux) that:
- Auto-detect the user's environment (MCP available vs. file-based only)
- Configure `mcpServers` in Claude config if MCP binary is found
- Set up fallback mode if MCP is unavailable
- Initialize state management in `.claude/state.json`

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
> - See **Appendix D** for the state management scripts (`state_manage.ps1`/`state_manage.sh`)

```
┌─────────────────────────────────────────────────────────────┐
│                      Orchestrator                            │
│                     (skill.md)                               │
│           Main LLM thread manages state.json                 │
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

### 3.2 Target Agent Inventory (20 total)

> **Definitive Inventory** - Reconciled 2025-12-22, updated for Template Harvesting. This is the authoritative list.

#### 3.2.1 Summary Table

| Category | Count | Status |
|----------|-------|--------|
| Planning/Reasoning | 5 | KEEP |
| Specialists | 2 | NEW (created) |
| Investigation | 1 | KEEP |
| Implementation | 1 | KEEP |
| Validation | 2 | KEEP (1 enhance) |
| Page Design | 5 | KEEP |
| Merge Workflow | 1 | KEEP (enhance) |
| Pattern Discovery | 1 | KEEP (enhance) |
| Template Harvesting | 1 | NEW |
| Testing | 1 | KEEP |
| **Total** | **20** | |

#### 3.2.2 Complete Agent Manifest

| # | Agent File | Category | Action | Notes |
|---|------------|----------|--------|-------|
| 1 | `powerbi-dashboard-update-planner.md` | Planning | KEEP | LLM reasoning |
| 2 | `powerbi-artifact-decomposer.md` | Planning | KEEP | LLM reasoning |
| 3 | `powerbi-data-understanding-agent.md` | Planning | KEEP | LLM reasoning |
| 4 | `power-bi-verification.md` | Planning | KEEP | LLM reasoning |
| 5 | `powerbi-code-understander.md` | Planning | KEEP | LLM reasoning |
| 6 | `powerbi-dax-specialist.md` | Specialist | KEEP | NEW - DAX generation |
| 7 | `powerbi-mcode-specialist.md` | Specialist | KEEP | NEW - M code generation |
| 8 | `powerbi-visual-locator.md` | Investigation | KEEP | PBIR only |
| 9 | `powerbi-visual-implementer-apply.md` | Implementation | KEEP | PBIR only |
| 10 | `powerbi-dax-review-agent.md` | Validation | ENHANCE | Add MCP validation |
| 11 | `powerbi-pbir-validator.md` | Validation | KEEP | PBIR only |
| 12 | `powerbi-page-question-analyzer.md` | Page Design | KEEP | PBIR only |
| 13 | `powerbi-visual-type-recommender.md` | Page Design | KEEP | PBIR only |
| 14 | `powerbi-page-layout-designer.md` | Page Design | KEEP | PBIR only |
| 15 | `powerbi-interaction-designer.md` | Page Design | KEEP | PBIR only |
| 16 | `powerbi-pbir-page-generator.md` | Page Design | KEEP | PBIR only |
| 17 | `powerbi-compare-project-code.md` | Merge | ENHANCE | Add MCP model reads |
| 18 | `powerbi-pattern-discovery.md` | Discovery | ENHANCE | Use MCP for measure list |
| 19 | `powerbi-template-harvester.md` | Template Harvesting | NEW | PBIR visual template extraction |
| 20 | `powerbi-playwright-tester.md` | Testing | KEEP | Browser testing |

#### 3.2.3 Deleted Agents (10 total)

| Agent File | Replacement |
|------------|-------------|
| `powerbi-data-model-analyzer.md` | `mcp.table/column/measure_operations` |
| `powerbi-data-context-agent.md` | `mcp.dax_query_operations.execute()` |
| `powerbi-code-locator.md` | `mcp.measure_operations.get()` |
| `powerbi-code-implementer-apply.md` | MCP transactions |
| `powerbi-tmdl-syntax-validator.md` | MCP validates implicitly |
| `powerbi-verify-pbiproject-folder-setup.md` | `mcp.connection_operations` |
| `powerbi-code-merger.md` | MCP transactions |
| `powerbi-code-fix-identifier.md` | Deprecated (use dashboard-update-planner) |
| `power-bi-visual-edit-planner.md` | Deprecated (use visual agents) |
| `powerbi-artifact-designer.md` | Moved to skill.md orchestration |

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

**2.5.3 Remove powerbi-artifact-designer (Orchestration Moves to skill.md)**

> **Architecture Correction:** The main LLM thread (skill.md) is the orchestrator, not a subagent. Subagents cannot spawn other subagents.

- [ ] Delete `powerbi-artifact-designer.md` (or keep for fallback only)
- [ ] Move orchestration logic to skill.md:
  - state.json initialization and management
  - Artifact type detection and specialist delegation
  - MCP transaction coordination
  - Specialist output assembly
- [ ] Skill.md delegates to appropriate specialist based on artifact type:
  - Measures → DAX Specialist (via Task tool)
  - Calculated Columns → DAX Specialist (via Task tool)
  - Partitions/Tables → M-Code Specialist (via Task tool)
  - Calculation Groups → DAX Specialist (via Task tool)
- [ ] Specialists are pure workers - they receive input, generate code, return output

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

#### 7.0.0 Official Skill Folder Structure (Claude Code Standard)

> **Reference:** This structure is based on official Anthropic documentation:
> - [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
> - [Claude Code Skills](https://code.claude.com/docs/en/skills)
> - [Skills Cookbook](https://github.com/anthropics/claude-cookbooks/tree/main/skills)

**Key Principle:** Skills must be **self-contained**. All related components (workflows, agents, scripts, resources) live INSIDE the skill folder.

**Official Standard Structure:**

```
.claude/skills/
└── skill-name/
    ├── SKILL.md              # Required: Main entry point with YAML frontmatter
    ├── workflows/            # User-invocable commands (slash commands)
    │   ├── evaluate.md
    │   └── create.md
    ├── agents/               # Subagents invoked by the skill (not standalone)
    │   ├── specialist-a.md
    │   └── specialist-b.md
    ├── scripts/              # Executable code (Python, PowerShell, Bash)
    │   ├── install.ps1
    │   └── helper.py
    └── resources/            # Templates, reference docs, data files
        ├── template.md
        └── glossary.md
```

**Component Definitions:**

| Folder | Purpose | Invocation |
|--------|---------|------------|
| `workflows/` | User-facing slash commands (`/evaluate`, `/create`) | User types `/command` |
| `agents/` | Subagents that the skill delegates to via Task tool | Skill invokes internally |
| `scripts/` | Executable utilities (installers, validators, helpers) | Claude runs via Bash |
| `resources/` | Reference materials, templates, context documents | Claude reads as needed |

**Progressive Disclosure:**
- **Level 1 (Always loaded):** SKILL.md frontmatter (`name`, `description`) ~100 tokens
- **Level 2 (On trigger):** SKILL.md body instructions <5k tokens
- **Level 3 (As needed):** Files in subfolders (unlimited, loaded on demand)

**SKILL.md Frontmatter Requirements:**

```yaml
---
name: skill-name          # Max 64 chars, lowercase, letters/numbers/hyphens only
description: |            # Max 1024 chars, explains what AND when to use
  Brief description of what this skill does and when Claude should use it.
---
```

**What NOT to do:**
- ❌ Commands at repository root (`/commands/`) - should be `skill/workflows/`
- ❌ Agents at repository root (`/agents/`) - should be `skill/agents/`
- ❌ Scattered installation scripts - should be `skill/scripts/`

**This Skill's Target Structure:**

```
skills/powerbi-analyst/
├── SKILL.md                           # Main entry point
├── workflows/                         # 7 user-invocable commands
│   ├── evaluate-pbi-project-file.md
│   ├── create-pbi-artifact.md
│   ├── create-pbi-page-specs.md
│   ├── implement-deploy-test-pbi-project-file.md
│   ├── analyze-pbi-dashboard.md
│   ├── merge-powerbi-projects.md
│   └── harvest-templates.md
├── agents/                            # 20 subagents
│   ├── powerbi-dax-specialist.md
│   ├── powerbi-mcode-specialist.md
│   └── ... (18 more)
├── scripts/                           # Installer and state management
│   ├── install.ps1
│   ├── install.sh
│   ├── state_manage.ps1
│   └── state_manage.sh
└── resources/                         # Reference documentation
    ├── getting-started.md
    ├── glossary.md
    ├── troubleshooting-faq.md
    └── findings_template.md
```

---

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

**Soft Requirement: Preferred with Fallback (Install-Time Detection)**

The MCP dependency is a "soft requirement" — the skill works without it but with reduced capabilities. MCP availability is determined **at install time** by the installer scripts (`install.ps1` for Windows, `install.sh` for macOS/Linux).

**Install-Time Configuration:**

```
Installer script execution:
1. Scan for powerbi-modeling-mcp.exe:
   - VS Code extensions folder
   - Standard paths (Program Files, AppData, homebrew)
   - PATH environment variable
2. If found:
   - Register MCP server in claude_config (mcpServers section)
   - Set skill mode = "mcp" in state.json
3. If not found:
   - Omit MCP server from config
   - Set skill mode = "file_fallback" in state.json
   - Log warning (no installation failure)
```

**MCP Server Configuration (Generated by installer):**

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

**Generated mcpServers Entry (when MCP found):**

> **🖥️ Desktop Mode (Default)**
>
> The empty `env` block triggers **Windows Integrated Authentication**.
> No environment variables are needed for Power BI Desktop connections.
> This is the default and recommended configuration for v1.0.

```json
{
  "mcpServers": {
    "powerbi-modeling": {
      "command": "C:/path/to/powerbi-modeling-mcp.exe",
      "args": [],
      "env": {}
    }
  }
}
```

> **Note:** Fabric/Azure connections requiring service principal authentication
> are **out of scope** for v1.0. Future releases may add `env` configuration
> for `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET`.

**Runtime Detection (Fallback Verification):**
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
│    (see state_manage.ps1/sh for current  │
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
│  • state_manage.ps1 -Summary (or .sh)    │
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
> The state management scripts (`state_manage.ps1`/`state_manage.sh`) currently:
> - Load existing state.json if present
> - Create fresh state if no file exists
> - Do not implement session timeout or staleness detection
>
> **Options to implement:**
> 1. **Fresh start always** - Ignore existing state, start clean
> 2. **Resume if recent** - Check `last_updated` timestamp, resume if <24h
> 3. **Prompt user** - Ask user if they want to continue previous session
> 4. **Auto-resume silently** - Always resume (current behavior)
>
> **Recommendation:** Option 3 (Prompt user) provides transparency while allowing resumption.
>
> **Implementation location:** Update state management scripts with session timeout logic.

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
| **HARVEST** | Extract visual templates | harvest, extract, template, save visual, reuse visual, template library | User wants to capture visual formatting for reuse |

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
   └─ [FALLBACK] DAX Specialist agent (file-based mode)
       └─ Generate DAX, validation deferred to TMDL validator

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

##### Workflow 7: HARVEST_TEMPLATES (Extract Visual Templates)

**Corresponds to:** `/harvest-templates`, `/review-templates`, `/promote-templates`

**Purpose:** Extract reusable PBIR visual templates from existing dashboards, deduplicate, and optionally promote to a public template library via Pull Request.

**Public Template Repository:**

```
github.com/cn-dataworks/pbir-visuals (PUBLIC)
└── visual-templates/
    ├── card-single-measure.json
    ├── line-chart-with-series.json
    ├── bar-chart-category-y.json
    └── ... (community-contributed templates)
```

**Storage Architecture:**

```
┌─────────────────────────────────────────────────────────────────────┐
│  USER'S PROJECT (Local Staging)                                     │
│  ───────────────────────────────                                    │
│  MyProject/                                                         │
│  ├── .templates/                                                    │
│  │   └── harvested/              ← Extracted templates staged here  │
│  │       ├── bar-chart-xyz.json                                     │
│  │       └── manifest.json                                          │
│  └── .Report/definition/pages/   ← Source visuals scanned here      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │  /promote-templates (creates PR)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PUBLIC REPO: github.com/cn-dataworks/pbir-visuals                  │
│  ─────────────────────────────────────────────────                  │
│  • Anyone can fork and submit PRs                                   │
│  • Templates fetched via raw.githubusercontent.com                  │
│  • CONTRIBUTING.md guides contributors                              │
└─────────────────────────────────────────────────────────────────────┘
```

**Benefits of Public Repository:**
- **Community contributions** - Anyone can submit templates via PR
- **Discoverability** - Templates searchable on GitHub
- **Version control** - Track template changes and history
- **Independence** - Works without this private skill installed
- **Standard workflow** - Fork → Branch → PR (familiar to developers)

**Naming Convention:**
```
[visual-type]-[binding-pattern].json

Examples:
- bar-chart-category-y.json      (bar chart with category axis)
- line-chart-multi-measure.json  (line chart with multiple Y values)
- card-single-measure.json       (card showing one measure)
- matrix-rows-columns-values.json (matrix with all three roles)
- slicer-dropdown.json           (dropdown slicer)
```

**Naming Logic:**
1. `visualType` property → kebab-case base (`barChart` → `bar-chart`)
2. Data binding pattern → suffix based on query roles used
3. Collision handling → append `-v2`, `-v3` if structure differs but name matches

---

**Capability Tiers (Runtime Detection):**

Commands are available based on runtime capability checks. No configuration file required -
dependencies are checked when each command runs, with helpful feedback if requirements aren't met.

| Command | Tier | Requirements | Fallback |
|---------|------|--------------|----------|
| `/harvest-templates` | 1 - Always | PBIR .Report folder | Error with conversion guidance |
| `/review-templates` | 2 - Read-Only | Harvested templates + Internet | Offline: skip comparison |
| `/promote-templates` | 3 - Contributor | GitHub CLI + authenticated | Manual PR instructions |

---

**Preflight Checks:**

Each phase performs runtime checks before execution. Failed checks produce actionable error messages.

```
┌─────────────────────────────────────────────────────────────────────┐
│  PREFLIGHT: /harvest-templates                                      │
└─────────────────────────────────────────────────────────────────────┘

CHECK 1: Project path provided or detectable
├─ Pass: Continue
└─ Fail: "Please specify a Power BI project path, or run from within a project folder."

CHECK 2: .Report folder exists (PBIR format)
├─ Pass: Continue
└─ Fail:
   "❌ No .Report folder found in [project-path].

    Template harvesting requires PBIR format (Power BI Enhanced Report).

    To convert your project:
    1. Open your .pbix in Power BI Desktop
    2. File → Save As → Select 'Power BI Project (*.pbip)'
    3. Re-run /harvest-templates on the new .pbip project"

CHECK 3: .Report/definition/pages/ contains visuals
├─ Pass: Continue
└─ Fail:
   "⚠️ No visuals found in [project-path].Report/definition/pages/

    This report appears to be empty or uses a different structure.
    Ensure the report has at least one page with visuals."

┌─────────────────────────────────────────────────────────────────────┐
│  PREFLIGHT: /review-templates                                       │
└─────────────────────────────────────────────────────────────────────┘

CHECK 1: Harvested templates exist
├─ Pass: Continue
└─ Fail:
   "❌ No harvested templates found.

    Run /harvest-templates first to extract templates from your report."

CHECK 2: manifest.json is valid
├─ Pass: Continue
└─ Fail:
   "❌ Invalid or corrupted manifest.json in .templates/harvested/

    Delete the .templates/harvested/ folder and re-run /harvest-templates"

CHECK 3: GitHub API reachable (for comparison)
├─ Pass: Continue with full comparison
└─ Warn (non-blocking):
   "⚠️ Cannot reach GitHub API. Continuing in offline mode.

    Review will show harvested templates without library comparison.
    Promotion will not be available until connectivity is restored."

┌─────────────────────────────────────────────────────────────────────┐
│  PREFLIGHT: /promote-templates                                      │
└─────────────────────────────────────────────────────────────────────┘

CHECK 1: Templates marked for promotion
├─ Pass: Continue
└─ Fail:
   "❌ No templates marked for promotion.

    Run /review-templates first and mark templates with [P]romote."

CHECK 2: GitHub CLI installed
├─ Command: gh --version
├─ Pass: Continue
└─ Fail:
   "❌ GitHub CLI (gh) is not installed.

    Template promotion requires the GitHub CLI to create Pull Requests.

    To install:
    • Windows:  winget install GitHub.cli
    • macOS:    brew install gh
    • Linux:    See https://cli.github.com/

    After installing, run: gh auth login

    ─────────────────────────────────────────────
    ALTERNATIVE: Manual Pull Request
    ─────────────────────────────────────────────
    If you prefer not to install gh CLI:
    1. Go to https://github.com/cn-dataworks/pbir-visuals
    2. Click 'Fork' to create your copy
    3. Upload templates via 'Add file' → 'Upload files'
    4. Click 'Contribute' → 'Open pull request'"

CHECK 3: GitHub CLI authenticated
├─ Command: gh auth status
├─ Pass: Continue (show username)
└─ Fail:
   "❌ GitHub CLI is not authenticated.

    Run: gh auth login

    Follow the prompts to authenticate with your GitHub account.
    You'll need a GitHub account (free) to contribute templates."

CHECK 4: Can reach github.com
├─ Pass: Continue
└─ Fail:
   "❌ Cannot reach github.com

    Check your internet connection and try again.
    If you're behind a proxy, configure gh with:
    gh config set http_proxy <proxy-url>"
```

---

**Condensed Flow:**

```
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 1: HARVEST (/harvest-templates)                              │
└─────────────────────────────────────────────────────────────────────┘

1. VALIDATE PROJECT (must have .Report folder)
   └─ Check for .Report/definition/pages/ structure

2. SCAN VISUALS
   └─ Glob: .Report/definition/pages/*/visuals/*/visual.json
   └─ Read each visual.json

3. CLASSIFY EACH VISUAL
   └─ Extract: visualType, query.queryState roles, objects
   └─ Generate descriptive name based on pattern
   └─ Check for existing template with same name

4. DEDUPLICATE
   └─ Hash visual structure (excluding position, name, GUIDs)
   └─ Group by visual type + binding pattern
   └─ Keep unique structures only

5. SANITIZE (Create Template)
   └─ Replace specific values with {{PLACEHOLDER}} syntax:
       - name → {{VISUAL_NAME}}
       - position x/y/z/width/height → {{X}}, {{Y}}, etc.
       - table names → {{TABLE_NAME}}, {{CATEGORY_TABLE}}, etc.
       - column/measure names → {{COLUMN_NAME}}, {{MEASURE_NAME}}, etc.
       - filter GUIDs → {{FILTER_GUID}}
       - title text → {{TITLE}}
   └─ Preserve: $schema, visualType, formatting objects

6. SAVE TO LOCAL STAGING
   └─ Create .templates/harvested/ if not exists
   └─ Write: .templates/harvested/[descriptive-name].json
   └─ Generate harvest manifest: .templates/harvested/manifest.json

7. REPORT RESULTS
   └─ Summary: X visuals scanned, Y unique patterns, Z new templates
   └─ List templates created with naming rationale

┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 2: REVIEW (/review-templates)                                │
└─────────────────────────────────────────────────────────────────────┘

1. LOAD HARVESTED
   └─ Read .templates/harvested/manifest.json
   └─ List all harvested templates

2. FETCH EXISTING PUBLIC LIBRARY
   └─ WebFetch: https://api.github.com/repos/cn-dataworks/pbir-visuals/contents/visual-templates
   └─ Parse directory listing to get existing template names
   └─ Optionally fetch individual templates for structure comparison

3. COMPARE
   └─ For each harvested template:
       - Check if name exists in public library
       - If exists, fetch and compare structure hash
       - Flag: NEW, DUPLICATE, VARIANT, IMPROVED
   └─ Provide comparison summary

4. PRESENT FOR REVIEW
   └─ Show each template with status and diff (if variant)
   └─ Allow user to mark for promotion: [P]romote, [S]kip, [R]ename
   └─ Store decisions in manifest.json

┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 3: PROMOTE (/promote-templates) - PR Workflow                │
└─────────────────────────────────────────────────────────────────────┘

**Prerequisites:**
- User must have GitHub CLI (`gh`) installed and authenticated
- User must have permission to create forks (free for public repos)

**Workflow:**

1. CHECK GITHUB AUTHENTICATION
   └─ Run: gh auth status
   └─ If not authenticated, prompt user to run: gh auth login

2. SETUP FORK (First Time Only)
   └─ Check if user already has fork: gh repo view cn-dataworks/pbir-visuals --json isFork
   └─ If no fork exists:
       - Create fork: gh repo fork cn-dataworks/pbir-visuals --clone=false
       - Wait for fork creation to complete
   └─ Clone or update local copy:
       - If no local: gh repo clone [username]/pbir-visuals ~/pbir-visuals-fork
       - If exists: cd ~/pbir-visuals-fork && git pull origin main

3. CREATE FEATURE BRANCH
   └─ Branch name: templates/[project-name]-[timestamp]
   └─ Run: git checkout -b templates/sales-dashboard-20251223

4. COPY SELECTED TEMPLATES
   └─ Copy marked templates from .templates/harvested/ to fork
   └─ Use approved names (may have been renamed in review)
   └─ Destination: ~/pbir-visuals-fork/visual-templates/

5. COMMIT AND PUSH
   └─ git add visual-templates/*.json
   └─ git commit -m "Add [N] templates from [project-name]"
   └─ git push origin [branch-name]

6. CREATE PULL REQUEST
   └─ Run: gh pr create --repo cn-dataworks/pbir-visuals \
           --title "Add templates: [list]" \
           --body "[generated description with template details]"
   └─ Display PR URL to user

7. CLEANUP LOCAL STAGING
   └─ Remove promoted templates from .templates/harvested/
   └─ Update manifest.json with PR reference
   └─ Optionally delete local fork clone

**Example PR Body (Auto-Generated):**
```markdown
## New Templates

This PR adds the following visual templates extracted from [Project Name]:

| Template | Type | Description |
|----------|------|-------------|
| bar-chart-category-y.json | Bar Chart | Category axis with single Y value |
| card-single-measure.json | Card | Single KPI display |

## Source
- Extracted via `/harvest-templates` command
- Project: [anonymized or user-provided name]

## Checklist
- [ ] Templates use {{PLACEHOLDER}} syntax correctly
- [ ] Naming follows convention: [visual-type]-[binding-pattern].json
- [ ] No project-specific data or formatting leaked
```

**Alternative: Manual PR (No gh CLI)**

If user doesn't have gh CLI, provide manual instructions:
1. Fork https://github.com/cn-dataworks/pbir-visuals
2. Upload templates via GitHub web UI
3. Create PR from your fork to cn-dataworks/pbir-visuals
```

**Template Sanitization Rules:**

| Original Value | Placeholder | Notes |
|----------------|-------------|-------|
| Visual name (GUID) | `{{VISUAL_NAME}}` | Always replace |
| Position x | `{{X}}` | Always replace |
| Position y | `{{Y}}` | Always replace |
| Position z | `{{Z}}` | Always replace |
| Width | `{{WIDTH}}` | Always replace |
| Height | `{{HEIGHT}}` | Always replace |
| Tab order | `{{TAB_ORDER}}` | Always replace |
| Title text | `{{TITLE}}` | Always replace |
| Filter GUIDs | `{{FILTER_GUID}}` | Always replace |
| Primary table | `{{TABLE_NAME}}` | For single-table visuals |
| Primary measure | `{{MEASURE_NAME}}` | For single-measure visuals |
| Category table | `{{CATEGORY_TABLE}}` | For visuals with Category role |
| Category column | `{{CATEGORY_COLUMN}}` | For visuals with Category role |
| Series table | `{{SERIES_TABLE}}` | For visuals with Series/Legend role |
| Series column | `{{SERIES_COLUMN}}` | For visuals with Series/Legend role |
| Multiple measures | `{{MEASURE_1_NAME}}`, etc. | Numbered for multi-measure |

**Preserved Values (Not Replaced):**
- `$schema` URL
- `visualType`
- Formatting objects (colors, fonts, axis settings)
- Default boolean flags
- Static configuration

**Agent:**
- `powerbi-template-harvester.md` - Handles scan, classify, deduplicate, sanitize

**MCP-Specific Changes:**
- None (PBIR-only workflow, no semantic model operations)

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
| HARVEST_TEMPLATES | None (PBIR-only) | **Yes** | None (new workflow) |

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

#### 7.0.8 State Management Patterns (Zero-Dependency Architecture)

Defines how the skill maintains session state and coordinates agent communication using a **capability-based fallback strategy** that requires no Python runtime.

**Architecture Philosophy:**
- **Claude-Native First:** Use Claude's Read/Write/Edit tools for JSON state
- **Graceful Degradation:** Fall back to PowerShell → CMD → Bash if needed
- **Zero Core Dependencies:** No Python required for basic functionality
- **Optional Addons:** Python-based telemetry available as opt-in

---

##### 7.0.8.1 Revised Dependency Model

**Core Dependencies (Required):**

| Dependency | Version | Purpose | Built-In |
|------------|---------|---------|----------|
| **Claude Code** | 1.0+ | Skill execution, file operations | Yes |
| **PowerShell** | 5.1+ | Fallback state management | Yes (Windows 10+) |
| **Power BI Modeling MCP** | Latest | Semantic model operations | No (download) |

**Optional Dependencies (Addons):**

| Dependency | Version | Purpose | Addon |
|------------|---------|---------|-------|
| **Python** | 3.10+ | Telemetry, advanced validation | `telemetry.md` |
| **jq** | 1.6+ | Bash JSON processing (macOS/Linux) | `state_manage.sh` |
| **opentelemetry-sdk** | 1.20+ | Trace export | `telemetry.md` |
| **pydantic** | 2.0+ | Schema validation | `validation.md` |

**Removed from Core:**

| Previously Required | Replacement |
|---------------------|-------------|
| Python 3.10+ | PowerShell (Windows) / Bash (macOS/Linux) |
| pathlib | Claude Read/Write tools |
| pydantic | Optional addon |
| Python scripts | state_manage.ps1 / state_manage.sh |

---

##### 7.0.8.2 Capability Detection Protocol

The skill detects available capabilities **once per session** and stores the result.

```
SESSION START
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  CAPABILITY PROBE (Run Once)                                     │
│  ─────────────────────────────                                   │
│  Goal: Determine best available state management backend         │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Test 1: Claude-Native JSON Capability                           │
│  ─────────────────────────────────────                           │
│  1. Create test file: .claude/capability_probe.json              │
│     Content: {"probe": "test", "timestamp": 0}                   │
│  2. Read the file back                                           │
│  3. Parse JSON, update timestamp to current time                 │
│  4. Write updated JSON                                           │
│  5. Read again, verify timestamp changed                         │
│                                                                  │
│  SUCCESS → state_backend = "claude_native"                       │
│  FAILURE → Continue to Test 2                                    │
└─────────────────────────────────────────────────────────────────┘
    │ (if failed)
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Test 2: PowerShell Capability                                   │
│  ─────────────────────────────                                   │
│  Execute: powershell -Command "Write-Output 'PROBE_OK'"          │
│                                                                  │
│  If output contains "PROBE_OK":                                  │
│      → state_backend = "powershell"                              │
│  Else:                                                           │
│      → Continue to Test 3                                        │
└─────────────────────────────────────────────────────────────────┘
    │ (if failed)
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Test 3: CMD Capability (Windows)                                │
│  ─────────────────────────────────                               │
│  Execute: cmd /c "echo PROBE_OK"                                 │
│                                                                  │
│  If output contains "PROBE_OK":                                  │
│      → state_backend = "cmd"                                     │
│  Else:                                                           │
│      → Continue to Test 4                                        │
└─────────────────────────────────────────────────────────────────┘
    │ (if failed)
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Test 4: Bash + jq Capability (macOS/Linux)                      │
│  ─────────────────────────────────────────                       │
│  Execute: bash -c "command -v jq && echo PROBE_OK"               │
│                                                                  │
│  If output contains "PROBE_OK":                                  │
│      → state_backend = "bash"                                    │
│  Else:                                                           │
│      → state_backend = "none" (ERROR STATE - warn user)          │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Store Result in Session State                                   │
│  ─────────────────────────────                                   │
│  Write to .claude/state.json:                                    │
│  {                                                               │
│    "session": {                                                  │
│      "state_backend": "claude_native|powershell|cmd|bash",       │
│      "capability_probe": {                                       │
│        "tested_at": "2025-12-22T10:00:00Z",                      │
│        "claude_native": true|false,                              │
│        "powershell": true|false,                                 │
│        "cmd": true|false,                                        │
│        "bash": true|false                                        │
│      }                                                           │
│    }                                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

##### 7.0.8.3 State File Locations

```
Project Root/
├── .claude/
│   ├── state.json              ← Global session state (singleton)
│   ├── capability_probe.json   ← Capability test artifact
│   └── tasks/
│       └── <task-id>/
│           └── findings.md     ← Task-specific blackboard
```

**Migration Note:** Current workflows use `agent_scratchpads/<timestamp>-<problem>/`. The skill uses `.claude/tasks/<task-id>/` for consistency with the new state management architecture. The `agent_scratchpads/` pattern is deprecated for new workflows.

---

##### 7.0.8.4 Complete State Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Power BI Analyst Skill State",
  "type": "object",
  "properties": {
    "session": {
      "type": "object",
      "properties": {
        "started": { "type": "string", "format": "date-time" },
        "last_activity": { "type": "string", "format": "date-time" },
        "skill_version": { "type": "string" },
        "state_backend": {
          "type": "string",
          "enum": ["claude_native", "powershell", "cmd", "bash", "none"]
        },
        "capability_probe": {
          "type": "object",
          "properties": {
            "tested_at": { "type": "string", "format": "date-time" },
            "claude_native": { "type": "boolean" },
            "powershell": { "type": "boolean" },
            "cmd": { "type": "boolean" },
            "bash": { "type": "boolean" }
          }
        },
        "mcp_available": { "type": "boolean" },
        "connection": {
          "type": "object",
          "properties": {
            "type": { "type": "string", "enum": ["desktop", "fabric", "pbip", "file_fallback"] },
            "status": { "type": "string", "enum": ["connected", "disconnected", "error"] },
            "established_at": { "type": "string", "format": "date-time" }
          }
        }
      },
      "required": ["started", "state_backend"]
    },
    "model_schema": {
      "type": "object",
      "properties": {
        "tables": { "type": "array" },
        "relationships": { "type": "array" },
        "last_synced": { "type": "string", "format": "date-time" },
        "sync_source": { "type": "string", "enum": ["mcp", "tmdl_parse"] }
      }
    },
    "active_tasks": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "path": { "type": "string" },
          "status": { "type": "string", "enum": ["pending", "in_progress", "completed", "failed"] },
          "workflow_type": { "type": "string" },
          "created": { "type": "string", "format": "date-time" },
          "updated": { "type": "string", "format": "date-time" },
          "current_stage": { "type": "string" }
        },
        "required": ["path", "status", "workflow_type", "created"]
      }
    },
    "resource_locks": {
      "type": "object",
      "additionalProperties": { "type": "string" }
    },
    "archived_tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "task_id": { "type": "string" },
          "workflow_type": { "type": "string" },
          "completed_at": { "type": "string", "format": "date-time" },
          "summary": { "type": "string" }
        }
      }
    }
  },
  "required": ["session", "active_tasks", "resource_locks"]
}
```

---

##### 7.0.8.5 Backend-Specific Operations

Each state operation has multiple implementations. The skill uses the detected backend.

**Create Task:**

| Backend | Implementation |
|---------|----------------|
| Claude-Native | Generate ID, mkdir, Read/Write state.json, Write findings.md |
| PowerShell | `state_manage.ps1 -CreateTask "name" -Workflow "type"` |
| CMD | `state_manage.cmd create_task "name" "type"` |
| Bash | `state_manage.sh create_task "name" "type"` |

**Acquire Lock:**

| Backend | Implementation |
|---------|----------------|
| Claude-Native | Read state.json, check locks, update, Write state.json |
| PowerShell | `state_manage.ps1 -Lock "path" -TaskId "id"` |
| CMD | N/A (manual) |
| Bash | `state_manage.sh lock "path" "id"` |

**Complete Task:**

| Backend | Implementation |
|---------|----------------|
| Claude-Native | Read state.json, update status, release locks, Write |
| PowerShell | `state_manage.ps1 -Complete "task_id"` |
| CMD | N/A (manual) |
| Bash | `state_manage.sh complete "task_id"` |

---

##### 7.0.8.6 Session Recovery Behavior

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

---

##### 7.0.8.7 Task Lifecycle

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

---

##### 7.0.8.8 Agent Communication Protocol (Task Blackboard Pattern)

Specialists communicate via the **Task Blackboard** (`findings.md`), not directly with each other.

**Blackboard Structure:**

```markdown
# Task Blackboard: [TASK_NAME]

**Status:** in_progress
**Task ID:** [TASK_ID]
**Workflow:** [evaluate|create|implement|analyze|merge]
**Created:** [ISO_TIMESTAMP]
**Backend:** [claude_native|powershell|cmd|bash]

---

## Section 1: Requirements (Orchestrator)
- **Goal:** [User intent in business terms]
- **Artifacts Needed:**
  - [ ] Measure: [Name] → DAX Specialist
  - [ ] Partition: [Name] → M-Code Specialist

---

## Section 2: DAX Logic (DAX Specialist)
- **Measures Created:**
  [DAX code block]
- **Validation:** Passed/Failed

---

## Section 3: M-Code Logic (M-Code Specialist)
- **Partitions Created:**
  [M code block]
- **Query Folding:** Folds to source / Breaks folding

---

## Section 4: Implementation (Orchestrator)
- **TMDL Changes:** [List]
- **PBIR Changes:** [List]

---

## Section 5: Validation Results
- **DAX Review:** Passed/Failed
- **TMDL Syntax:** Passed/Failed

---

## Section 6: Final Manifest
- **Summary:** [Brief description]
```

**Communication Rules:**

| Agent | Reads | Writes |
|-------|-------|--------|
| Orchestrator | User request, state.json | Section 1, 4, 6 |
| DAX Specialist | Section 1, model_schema | Section 2 |
| M-Code Specialist | Section 1, model_schema | Section 3 |
| Validators | Section 2-4 | Section 5 |

---

##### 7.0.8.9 Resource Locking Protocol

Locks prevent concurrent modification of the same file by multiple tasks.

**When to Lock:**

| Operation | Requires Lock |
|-----------|---------------|
| Read TMDL/PBIR | No |
| Write TMDL measure | Yes (table file) |
| Write PBIR visual | Yes (visual.json) |
| MCP operations | No (MCP handles internally) |

**Lock Cleanup:**
- Locks are automatically released when task is archived
- Stale locks (task no longer in active_tasks) can be force-released
- Locks older than 24 hours are auto-released with warning

---

##### 7.0.8.10 Fallback Script Reference

Scripts are provided for fallback state management when Claude-native JSON operations are unavailable.

**PowerShell (Windows - Primary Fallback):**

Location: `.claude/tools/state_manage.ps1`

```bash
# Session
state_manage.ps1 -Summary
state_manage.ps1 -Reset

# Tasks
state_manage.ps1 -CreateTask "name" -Workflow "type"
state_manage.ps1 -Complete "task_id"
state_manage.ps1 -Archive "task_id"

# Locks
state_manage.ps1 -Lock "path" -TaskId "id"
state_manage.ps1 -Release "path" -TaskId "id"
```

**CMD (Windows - Minimal Fallback):**

Location: `.claude/tools/state_manage.cmd`

```bash
state_manage.cmd create_task "name" "workflow"
state_manage.cmd summary
```

**Bash + jq (macOS/Linux):**

Location: `.claude/tools/state_manage.sh`

```bash
state_manage.sh summary
state_manage.sh create_task "name" "workflow"
state_manage.sh complete "task_id"
state_manage.sh lock "path" "task_id"
state_manage.sh release "path" "task_id"
```

---

#### 7.0.9 Distribution Strategy (Zero-Dependency)

**Distribution Philosophy: Desktop First with Dual Installation Paths**

The skill is distributed as a zip file with **two installation paths**:

| Path | Entry Point | Target User | Philosophy |
|------|-------------|-------------|------------|
| **Quick Install** | `install.bat` / `install.sh` | Non-technical | Convenience |
| **Manual Setup** | `MANUAL_SETUP.md` | Technical/Auditors | Transparency |

> **SCOPE: Desktop Mode Only** - Fabric/Azure connections are out of scope for v1.0.

---

##### 7.0.9.1 Runtime Dependencies (No Python Required)

| Dependency | Version | Purpose | Required |
|------------|---------|---------|----------|
| **Claude Code** | 1.0+ | Skill execution | Yes |
| **PowerShell** | 5.1+ | State management fallback | Yes (Windows) |
| **Power BI Modeling MCP** | Latest | Semantic model operations | Yes |

**Note:** Python is NOT required for core functionality. Python is only needed for optional telemetry addon.

---

##### 7.0.9.2 Distribution Artifact Structure

```
powerbi-analyst-skill-v1.0.0.zip
├── install.bat                    # Windows installer (no Python)
├── install.sh                     # macOS/Linux installer
├── MANUAL_SETUP.md                # Step-by-step manual guide
├── README.txt
├── payload/
│   └── .claude/
│       ├── skills/powerbi-analyst/
│       │   ├── SKILL.md
│       │   └── addons/
│       ├── agents/
│       └── tools/
│           ├── state_manage.ps1   # PowerShell
│           ├── state_manage.cmd   # CMD minimal
│           ├── state_manage.sh    # Bash + jq
│           └── telemetry/         # Optional Python
└── optional/
    └── telemetry-setup.bat        # Separate telemetry installer
```

---

##### 7.0.9.3 Quick Install Path (No Python)

The `install.bat` script:
1. Verifies PowerShell is available
2. Detects Power BI Modeling MCP (prompts to download if missing)
3. Copies skill files to `.claude/`
4. Configures Claude Desktop for MCP
5. No Python installation required

---

##### 7.0.9.4 Desktop Mode Configuration

```json
{
  "mcpServers": {
    "powerbi-modeling": {
      "command": "C:\\Program Files\\PowerBI Modeling MCP\\powerbi-modeling-mcp.exe",
      "args": [],
      "env": {}
    }
  }
}
```

Empty `env` block ensures Windows Integrated Authentication.

---

##### 7.0.9.5 Telemetry Addon (Optional)

Telemetry requires separate installation:

1. Install Python 3.10+
2. `pip install opentelemetry-sdk opentelemetry-exporter-otlp arize-phoenix`
3. Copy `addons/telemetry.md` to skill root
4. Start Phoenix: `python -m phoenix.server.main serve`

**Telemetry is NOT installed by default.**

---

##### 7.0.9.6 Compatibility Header

SKILL.md includes compatibility header for future tools:

```yaml
compatibility:
  claude_code: ">=1.0.0"
  copilot: "experimental"

state_management:
  preferred: claude_native
  fallbacks:
    - backend: powershell
    - backend: cmd
    - backend: bash
```

---

#### 7.0.10 Error Handling and Fallback Logic

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

#### 7.0.11 Validation Gate Integration

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

#### 7.0.11.1 Measure Verification Protocol

After a DAX Specialist creates or modifies a measure, the Orchestrator enforces live validation against a running model.

**Why Live Testing is Required:**
- You cannot "test" a text file — TMDL is just code on disk
- DAX syntax validation catches errors, but not logic bugs
- Only a live engine can evaluate the measure against actual data

**Verification Sequence:**

```
DAX SPECIALIST COMPLETES MEASURE
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Define the Test Query                                  │
│  ─────────────────────────────                                  │
│  Create a DAX query that evaluates the new measure alongside    │
│  a 'Control' (e.g., a simple SUM of the same column).           │
│                                                                 │
│  Example for YoY Growth measure:                                │
│  EVALUATE                                                       │
│  SUMMARIZECOLUMNS(                                              │
│    'Date'[Year],                                                │
│    "New Measure", [YoY Growth %],                               │
│    "Control", DIVIDE(SUM(Sales[Amount]), SUM(Sales[PY Amount])) │
│  )                                                              │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Connect to Live Model                                  │
│  ─────────────────────────────                                  │
│  Priority:                                                      │
│  1. Desktop connection (if PBI Desktop is running)              │
│  2. Fabric dev workspace (if configured)                        │
│  3. Skip live test (warn user, mark as "Unverified")            │
│                                                                 │
│  MCP: mcp.connection_operations.connect()                       │
│  MCP: mcp.database_operations.refresh() ← picks up TMDL changes │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Execute Query                                          │
│  ─────────────────────                                          │
│  MCP: mcp.dax_query_operations.execute(test_query)              │
│                                                                 │
│  Capture results for analysis.                                  │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: Automated Assertions                                   │
│  ────────────────────────────                                   │
│                                                                 │
│  CHECK 1: Flatline Detection                                    │
│  ─────────────────────────────                                  │
│  If measure returns SAME value for every row:                   │
│  → Likely missing relationship or incorrect filter context      │
│  → Flag as ERROR, suggest fix before proceeding                 │
│                                                                 │
│  CHECK 2: NULL/Blank Detection                                  │
│  ─────────────────────────────                                  │
│  If measure returns NULL/BLANK for all rows:                    │
│  → Likely referencing wrong column or missing data              │
│  → Flag as WARNING, prompt user to verify                       │
│                                                                 │
│  CHECK 3: Logic Verification                                    │
│  ─────────────────────────────                                  │
│  For time intelligence (YoY, QoQ, etc.):                        │
│  → Query two separate periods                                   │
│  → Manually calculate expected result                           │
│  → Compare to measure result                                    │
│  → If mismatch > 1%, flag as ERROR                              │
│                                                                 │
│  CHECK 4: Control Comparison                                    │
│  ─────────────────────────────                                  │
│  Compare new measure to control measure:                        │
│  → Results should be logically consistent                       │
│  → Flag unexpected deviations                                   │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: Update Findings                                        │
│  ───────────────────────                                        │
│                                                                 │
│  In findings.md Section 2 (DAX Logic):                          │
│                                                                 │
│  **Verification Status:** ✅ PASSED                              │
│  - Flatline check: Passed (values vary by dimension)            │
│  - Logic check: YoY for 2024 = 12.3% (expected: 12.3%)          │
│  - Control comparison: Within tolerance                         │
│  - Live model: Power BI Desktop (localhost:54321)               │
│                                                                 │
│  OR                                                             │
│                                                                 │
│  **Verification Status:** ⚠️ UNVERIFIED                          │
│  - No live model available                                      │
│  - Recommend: Open Power BI Desktop before implementation       │
└─────────────────────────────────────────────────────────────────┘
```

**Truth File Testing (Advanced):**

For critical measures, store expected results in `.claude/tasks/<task-id>/truth.csv`:

```csv
Year,Expected_YoY_Growth
2022,0.00
2023,0.15
2024,0.12
```

The verification step compares actual query results against truth file:
- Match within tolerance (default 0.1%) → PASS
- Mismatch → FAIL with detailed comparison

**Skip Conditions:**

Live verification can be skipped when:
- User explicitly requests `--skip-verify`
- No live model is available (with warning)
- Measure is a formatting-only change (display, folder)

---

#### 7.0.12 Human-in-the-Loop Patterns

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

#### 7.0.13 Format-Specific Handling

Defines how the skill handles different Power BI project formats.

> **⚠️ CRITICAL: Hybrid Architecture Limit**
>
> The Microsoft Power BI Modeling MCP **cannot handle PBIR (Report/Visual) operations**.
> The MCP is strictly limited to **Semantic Model** operations:
> - ✅ Measures, Calculated Columns, Tables, Relationships (MCP)
> - ❌ Pages, Visuals, Layouts, Interactions (File-based only)
>
> **The skill MUST retain file-based agents for all operations inside the `.Report` folder:**
> - `powerbi-visual-locator` - Find visuals in PBIR structure
> - `powerbi-visual-type-recommender` - Suggest visual types
> - `powerbi-page-layout-designer` - Generate layout coordinates
> - `powerbi-interaction-designer` - Design cross-filtering
> - `powerbi-pbir-page-generator` - Generate page JSON files
> - `powerbi-pbir-validator` - Validate PBIR JSON structure
> - `powerbi-visual-implementer-apply` - Apply visual changes
>
> **This is a permanent architectural constraint**, not a temporary limitation.
> Monitor Microsoft's MCP repository for future `report_operations` support (Q8 decision).

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

---

#### 7.0.13.1 PBIR Schema Version Detection

PBIR files contain `$schema` URLs that specify the JSON schema version. The skill must detect and handle different schema versions to ensure compatibility.

**Schema URL Structure:**

```
https://developer.microsoft.com/json-schemas/fabric/item/report/definition/<component>/<version>/schema.json
```

**Key Schema Components and Versions:**

| Component | Schema Path | Known Versions | Notes |
|-----------|-------------|----------------|-------|
| definition.pbir | `definitionProperties` | 1.0.0, 2.0.0 | Report-level config |
| visual.json | `visualContainer` | 2.0.0, 2.2.0, 2.4.0 | Individual visuals |
| page.json | `page` | 1.0.0+ | Page definitions |
| report.json | `report` | 1.0.0+ | Report metadata |

**Detection Flow:**

```
PBIP PROJECT DETECTED
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Read definition.pbir                                    │
│  ───────────────────────────────────                             │
│  Extract:                                                        │
│  • "$schema" URL → definitionProperties version (1.0.0 or 2.0.0) │
│  • "version" property → report format version (1.0 or 4.0+)      │
└─────────────────────────────────────────────────────────────────┘
    │
    ├─ version = "1.0" ──────────────────────────────────────────┐
    │                                                             │
    │                                  ┌─────────────────────────┐
    │                                  │  PBIR-LEGACY ONLY       │
    │                                  │  ───────────────────    │
    │                                  │  • Uses report.json     │
    │                                  │  • No /definition folder│
    │                                  │  • Limited editability  │
    │                                  │  • Upgrade recommended  │
    │                                  └─────────────────────────┘
    │
    └─ version = "4.0"+ ─────────────────────────────────────────┐
                                                                  │
                               ┌─────────────────────────────────┐
                               │  PBIR ENHANCED (Full Support)   │
                               │  ───────────────────────────    │
                               │  • Uses /definition folder      │
                               │  • Individual visual.json files │
                               │  • Public JSON schemas          │
                               │  • Full skill support           │
                               └─────────────────────────────────┘
                                                                  │
                                                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Sample Visual Schema Version                            │
│  ────────────────────────────────────                            │
│  Read first visual.json in pages/*/visuals/*/visual.json         │
│  Extract "$schema" URL → visualContainer version                 │
│  Store in state.json for template matching                       │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Version Compatibility Check                             │
│  ───────────────────────────────────                             │
│  Compare detected version against skill's template versions      │
│  • Templates at: .claude/visual-templates/*.json                 │
│  • Current template version: 2.4.0                               │
└─────────────────────────────────────────────────────────────────┘
    │
    ├─ Exact Match ────────────── ✅ Full compatibility
    │
    ├─ Minor Version Diff ─────── ⚠️ Warning, likely compatible
    │   (e.g., templates 2.4.0, project 2.2.0)
    │
    └─ Major Version Diff ─────── ❌ Error with guidance
        (e.g., templates 2.x, project 3.x)
```

**Version Compatibility Matrix:**

| Project Schema | Template Schema | Status | Action |
|----------------|-----------------|--------|--------|
| 2.4.0 | 2.4.0 | ✅ Full | Proceed |
| 2.2.0 | 2.4.0 | ⚠️ Compatible | Warn, proceed (templates may have extra properties) |
| 2.0.0 | 2.4.0 | ⚠️ Compatible | Warn, proceed (older project, newer templates) |
| 3.0.0+ | 2.4.0 | ❌ Unknown | Halt, recommend updating skill |

**PBIR-Legacy Detection and Upgrade Guidance:**

```
⚠️ PBIR-LEGACY FORMAT DETECTED

Your report uses PBIR-Legacy format (version 1.0).
Visual editing features are limited in this format.

To unlock full PBIR editing capabilities:

UPGRADE IN POWER BI DESKTOP
──────────────────────────────
1. Open the report in Power BI Desktop
2. Go to File → Options and settings → Options
3. Under Preview features, enable "Store reports using
   enhanced metadata format (PBIR)"
4. Save As → Power BI Project (.pbip)

NOTE: This upgrade is one-way. A 30-day backup is created
automatically, but rollback via UI is not possible.

[C]ontinue with limited editing (semantic model only)
[A]bort and upgrade first
```

**Schema Version Extraction Code Pattern:**

```python
import json
import re
from pathlib import Path

def detect_pbir_versions(pbip_path: Path) -> dict:
    """Extract schema versions from a PBIP project."""
    result = {
        "definition_schema": None,
        "definition_version": None,
        "visual_schema": None,
        "is_pbir_enhanced": False
    }

    # Read definition.pbir
    definition_path = pbip_path / ".Report" / "definition.pbir"
    if definition_path.exists():
        with open(definition_path) as f:
            definition = json.load(f)

        # Extract schema version from URL
        schema_url = definition.get("$schema", "")
        match = re.search(r"/(\d+\.\d+\.\d+)/schema\.json", schema_url)
        if match:
            result["definition_schema"] = match.group(1)

        # Extract report format version
        result["definition_version"] = definition.get("version", "1.0")
        result["is_pbir_enhanced"] = float(result["definition_version"]) >= 4.0

    # Sample first visual.json for visualContainer schema
    if result["is_pbir_enhanced"]:
        pages_path = pbip_path / ".Report" / "definition" / "pages"
        if pages_path.exists():
            for visual_json in pages_path.glob("*/visuals/*/visual.json"):
                with open(visual_json) as f:
                    visual = json.load(f)
                schema_url = visual.get("$schema", "")
                match = re.search(r"visualContainer/(\d+\.\d+\.\d+)/", schema_url)
                if match:
                    result["visual_schema"] = match.group(1)
                break  # Only need first visual

    return result
```

**State.json Schema Version Storage:**

```json
{
  "session": { ... },
  "model_schema": { ... },
  "pbir_info": {
    "format": "pbir_enhanced",
    "definition_schema_version": "2.0.0",
    "definition_version": "4.0",
    "visual_schema_version": "2.4.0",
    "template_compatibility": "full",
    "detected_at": "2025-12-21T10:30:00Z"
  }
}
```

---

#### 7.0.13.2 Future Schema Version Handling

Microsoft periodically releases new PBIR schema versions. The skill should handle unknown future versions gracefully.

**Unknown Version Strategy:**

```
🆕 NEW SCHEMA VERSION DETECTED

Your project uses visualContainer schema version 3.0.0,
but this skill was built for version 2.4.0.

This may indicate:
• A newer Power BI Desktop version was used
• New visual features that require updated templates

OPTIONS:
[P] Proceed anyway (may work, may fail on new properties)
[S] Skip visual editing (semantic model changes only)
[U] Check for skill updates

Detected schema: https://developer.microsoft.com/json-schemas/
    fabric/item/report/definition/visualContainer/3.0.0/schema.json
Expected schema: visualContainer/2.4.0
```

**Template Version Update Process:**

When Microsoft releases a new schema version:

1. **Detection:** Skill encounters unknown schema in user's project
2. **Logging:** Record schema URL in analytics for tracking
3. **Manual Update:** Plugin maintainer:
   - Fetches new schema from Microsoft
   - Updates templates in `.claude/visual-templates/`
   - Tests against sample projects
   - Releases updated skill version
4. **Compatibility:** Old projects continue to work (templates are forward-compatible)

---

#### 7.0.14 Authentication Consolidation

The migration from file-based operations to MCP requires consolidating multiple authentication paths into a unified model.

**7.0.14.1 Current Authentication Landscape**

| Current Method | Tool/Script | Use Case |
|----------------|-------------|----------|
| Device Code Flow (MSAL) | `xmla_agent/get_token.py` | XMLA queries to Fabric |
| Service Principal | pbi-tools CLI | CI/CD deployment |
| PowerShell Cmdlets | MicrosoftPowerBIMgmt | Interactive deployment |
| Windows Integrated | Power BI Desktop | Local Analysis Services |

**7.0.14.2 MCP Authentication Model**

The MCP uses **Azure Identity SDK** for all credential handling:

> "Your credentials are always handled securely through the official Azure Identity SDK - we never store or manage tokens directly."

**Authentication by Connection Type:**

| Connection Type | Authentication | User Action Required |
|-----------------|---------------|---------------------|
| **PBIP (File)** | None | No auth (local files) |
| **Power BI Desktop** | Windows Integrated | None (uses logged-in user) |
| **Fabric Workspace** | Azure Identity SDK | Browser sign-in (first time) |

**Azure Identity SDK Credential Chain:**

The MCP follows Azure's `DefaultAzureCredential` pattern, attempting credentials in order:

```
1. EnvironmentCredential → Service principal from env vars
2. ManagedIdentityCredential → Azure managed identity
3. AzureCliCredential → `az login` session
4. AzureDeveloperCliCredential → `azd login` session
5. InteractiveBrowserCredential → Browser-based sign-in
```

**7.0.14.3 Migration Mapping**

| Current Auth | MCP Equivalent | Notes |
|--------------|----------------|-------|
| Device Code (MSAL) | InteractiveBrowserCredential | Azure Identity handles flow |
| Service Principal | EnvironmentCredential | Set `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID` |
| PowerShell | Not needed | MCP handles internally |
| Windows Integrated | Auto-detected | MCP uses for Desktop connection |

**7.0.14.4 Unified Authentication Flow**

```
USER INVOKES SKILL
    │
    ├─ Connection Type: PBIP
    │   └─ No authentication required
    │   └─ Read/write TMDL files directly
    │
    ├─ Connection Type: Desktop
    │   └─ Connect to local Analysis Services
    │   └─ Windows Integrated Auth (automatic)
    │
    └─ Connection Type: Fabric
        │
        ├─ Check Azure CLI session (`az account show`)
        │   └─ If valid → Use AzureCliCredential
        │
        ├─ Check environment variables
        │   └─ If set → Use EnvironmentCredential (service principal)
        │
        └─ Fall back to interactive browser
            └─ User signs in once
            └─ Token cached by Azure Identity SDK
```

**7.0.14.5 Credential Storage and Caching**

**MCP Approach (recommended):**
- Azure Identity SDK manages token caching
- Tokens stored in OS credential store (Windows Credential Manager, macOS Keychain)
- Automatic token refresh
- No custom cache files needed

**Deprecated Approach (remove):**
- `xmla_agent/.msal_token_cache.bin` - MSAL cache file
- Custom token serialization in get_token.py

**Migration Action:**
- [ ] Remove `xmla_agent/get_token.py` dependency
- [ ] Remove `.msal_token_cache.bin` from project
- [ ] Update XMLA query agents to use MCP's `dax_query_operations.execute()`
- [ ] Document Azure CLI setup for Fabric access

**7.0.14.6 Authentication Error Handling**

| Error | Cause | User Message | Recovery |
|-------|-------|--------------|----------|
| `AuthenticationError` | No valid credentials | "Please sign in to Azure: Run `az login` or set service principal environment variables" | Guide to Azure CLI |
| `ClientAuthenticationError` | Invalid credentials | "Authentication failed. Check your Azure credentials." | Re-authenticate |
| `CredentialUnavailableError` | No credential source | "No Azure credentials found. For Fabric connection, run `az login` first." | Azure CLI setup |
| `TokenExpiredError` | Cached token expired | (Silent refresh attempted first) | Auto-retry with refresh |

**Error Handling Template:**

```
❌ AUTHENTICATION REQUIRED

This workflow requires access to your Fabric workspace,
but no valid Azure credentials were found.

To authenticate, you have several options:

1. AZURE CLI (Recommended for interactive use):
   Run: az login
   Then: az account set --subscription <your-subscription-id>

2. SERVICE PRINCIPAL (Recommended for automation):
   Set environment variables:
   - AZURE_CLIENT_ID=<your-client-id>
   - AZURE_CLIENT_SECRET=<your-client-secret>
   - AZURE_TENANT_ID=<your-tenant-id>

3. SWITCH TO PBIP MODE:
   If you don't need live query execution, you can work
   with PBIP files directly (no authentication required).

[R] Retry after signing in
[P] Switch to PBIP mode
[H] Help with Azure setup
```

**7.0.14.7 Fabric Tenant Compatibility**

> "Connecting to a Semantic Model in a Fabric workspace may not work in your tenant due to the ongoing rollout of the client ID used for authentication."

**Tenant Compatibility Check:**

```python
# Before attempting Fabric connection
try:
    result = mcp.connection_operations.connect(
        connection_type="fabric",
        workspace_id=workspace_id,
        dataset_id=dataset_id
    )
except AuthenticationError as e:
    if "client_id" in str(e) or "not authorized" in str(e):
        # Known tenant rollout issue
        display_fabric_compatibility_warning()
```

**Fallback Message:**

```
⚠️ FABRIC CONNECTION NOT AVAILABLE

Your tenant may not yet support the MCP client ID for Fabric connections.
This is a known issue during Microsoft's rollout phase.

ALTERNATIVES:
1. Use PBIP mode for semantic model editing (file-based, no auth)
2. Use Power BI Desktop for live query testing (local connection)
3. Check with your tenant admin about MCP client ID authorization
4. Monitor: https://github.com/microsoft/powerbi-modeling-mcp/issues

[P] Proceed with PBIP mode
[D] Try Desktop connection instead
```

---

#### 7.0.15 Analytics and Testing Integration

The skill maintains existing analytics collection and testing capabilities from the command-based architecture.

**7.0.15.1 Analytics Continuation**

Current commands end with an analytics phase that runs:
```bash
python .claude/tools/token_analyzer.py --full
python .claude/tools/analytics_merger.py
```

**Skill Integration Approach:**

Analytics are triggered via Claude Code hooks, not embedded in the skill prompt:

```
Pre-command Hook: Record workflow_start event
Post-command Hook: Run analytics scripts
```

**Hook Configuration (.claude/hooks.json):**

```json
{
  "skill_complete": {
    "command": "python .claude/tools/token_analyzer.py --full && python .claude/tools/analytics_merger.py",
    "trigger": "on_skill_exit"
  }
}
```

**Analytics Data Flow:**

```
SKILL EXECUTION
    │
    ├─ state.json records:
    │   └─ workflow_type, start_time, mcp_available, artifacts_created
    │
    ├─ findings.md records:
    │   └─ Agent invocations, validation results, user decisions
    │
    └─ WORKFLOW COMPLETE
        │
        └─ Post-hook triggers:
            ├─ token_analyzer.py → Parse Claude logs for token usage
            └─ analytics_merger.py → Aggregate into agent_analytics.json
```

**Key Files:**
| File | Purpose | Location |
|------|---------|----------|
| `token_analyzer.py` | Parse Claude Code JSONL logs | `.claude/tools/` |
| `analytics_merger.py` | Aggregate metrics | `.claude/tools/` |
| `agent_analytics.json` | Aggregated results | `agent_scratchpads/_analytics/` |

**No Changes Required:**
- Analytics scripts continue to work unchanged
- Hook-based triggering replaces explicit command calls
- Same output format and storage location

**7.0.15.2 Playwright Testing Integration**

The `powerbi-playwright-tester` agent is **KEPT unchanged** for browser-based dashboard testing.

**Testing Architecture:**

```
IMPLEMENT WORKFLOW
    │
    ├─ Apply code changes (MCP or file-based)
    │
    ├─ Deploy to Power BI Service (MCP or pbi-tools)
    │
    └─ Phase: TESTING
        │
        ├─ Check for test plan (findings.md Section 3)
        │   └─ If no tests defined → Skip
        │
        └─ Invoke powerbi-playwright-tester
            │
            ├─ Uses Playwright MCP
            │   └─ browser_navigate, browser_click, browser_snapshot
            │
            ├─ Executes test cases from Section 3
            │
            └─ Records results to findings.md Section 6
```

**Test Result Storage:**

Results are stored in the findings.md file:

```markdown
## Section 6: Test Results

### Test Execution Summary
- **Date:** 2025-12-21 14:30:00
- **Dashboard URL:** https://app.powerbi.com/reports/abc123
- **Tests Executed:** 5
- **Passed:** 4
- **Failed:** 1

### Test Case Results

#### TC-001: Verify Total Revenue displays correctly ✅
**Status:** PASSED
**Evidence:** Screenshot saved to `test-evidence/tc-001.png`
**Actual Value:** $1,234,567.89
**Expected:** Matches source data

#### TC-002: Verify YoY Growth calculation ❌
**Status:** FAILED
**Evidence:** Screenshot saved to `test-evidence/tc-002.png`
**Actual Value:** 15.5%
**Expected:** 18.2%
**Notes:** Discrepancy due to missing Q4 data in filter
```

**Testing in MCP Mode vs Fallback Mode:**

| Aspect | MCP Mode | Fallback Mode |
|--------|----------|---------------|
| Deployment | `mcp.database_operations.deploy()` | pbi-tools CLI |
| Wait for ready | MCP provides status | Poll refresh status |
| Testing | Same (Playwright MCP) | Same (Playwright MCP) |
| Evidence capture | Same (screenshots) | Same (screenshots) |

**Test Evidence Storage:**

```
agent_scratchpads/
└── <timestamp>-<problem>/
    ├── findings.md         # Contains Section 6 test results
    └── test-evidence/      # Screenshots and logs
        ├── tc-001.png
        ├── tc-002.png
        └── browser-console.log
```

**7.0.15.3 Test Plan Generation**

Test cases are generated during the planning phase (EVALUATE/CREATE workflows) and stored in findings.md Section 3:

```markdown
## Section 3: Test Cases

### TC-001: Verify measure displays correctly
**Type:** Visual verification
**Steps:**
1. Navigate to Sales Overview page
2. Locate "Total Revenue" card
3. Verify format matches "$#,###.##"
**Expected:** Value displays in currency format with 2 decimals

### TC-002: Verify filter interaction
**Type:** Interactive test
**Steps:**
1. Select "2024" in Year slicer
2. Observe Total Revenue card update
**Expected:** Value changes to show 2024 data only
```

**7.0.15.4 Integration Points**

| Integration | Before (Commands) | After (Skill) |
|-------------|-------------------|---------------|
| Analytics trigger | Explicit bash in command | Hook-based (post-skill) |
| Test storage | findings.md Section 6 | findings.md Section 6 (unchanged) |
| Evidence location | test-evidence/ | test-evidence/ (unchanged) |
| Playwright usage | Same agent | Same agent (KEEP) |
| Token analysis | token_analyzer.py | token_analyzer.py (unchanged) |

---

**7.0.15.5 OTEL Strategy: Real-Time Telemetry**

The skill upgrades from "Post-Mortem Logs" (Level 1) to **Level 3: Real-Time Telemetry** using OpenTelemetry (OTEL).

**Telemetry Levels:**

| Level | Description | Current State |
|-------|-------------|---------------|
| Level 1 | Post-mortem logs (JSONL parsing) | ✅ Current (token_analyzer.py) |
| Level 2 | Structured events (custom format) | Not implemented |
| **Level 3** | **Real-time OTEL traces** | **NEW - Optional** |

**Benefits of OTEL:**
- Industry-standard tracing format
- Real-time visibility into agent execution
- Span hierarchy shows agent → MCP call relationships
- Compatible with many observability platforms (Jaeger, Zipkin, Arize Phoenix)

**OTEL Architecture:**

```
SKILL EXECUTION
    │
    ├─ Create root span: "powerbi-analyst.workflow"
    │   ├─ Attribute: workflow_type = "evaluate"
    │   ├─ Attribute: mcp_mode = "full" | "fallback"
    │   └─ Attribute: project_path = "..."
    │
    ├─ Child span: "dax_specialist.invoke"
    │   ├─ Duration: 2.5s
    │   ├─ Attribute: measures_generated = 2
    │   └─ Child span: "mcp.measure_operations.create"
    │       └─ Duration: 150ms
    │
    └─ Export to OTEL endpoint → Arize Phoenix dashboard
```

**Trace Propagation:**
- Root span created by skill.md (orchestrator)
- Child spans created by each specialist agent
- MCP operations create leaf spans
- Trace context propagated via state.json

---

**7.0.15.6 Prerequisites for Telemetry**

**Required:**
- Python 3.9+
- OpenTelemetry SDK (`opentelemetry-sdk`)
- OTEL OTLP Exporter (`opentelemetry-exporter-otlp`)

**Optional (Recommended for Visualization):**
- **Arize Phoenix** - Open-source LLM observability dashboard
  - Installation: `pip install arize-phoenix`
  - GitHub: https://github.com/Arize-ai/phoenix

**requirements.txt Update:**

```txt
# Core dependencies
# ... existing deps ...

# Telemetry (optional - uncomment to enable)
# opentelemetry-sdk>=1.20.0
# opentelemetry-exporter-otlp>=1.20.0
# arize-phoenix>=4.0.0  # For local dashboard
```

**Starting Arize Phoenix Locally:**

```bash
# Start Phoenix server (default port 6006)
python -m phoenix.server.main serve

# Or with Docker
docker run -p 6006:6006 arizephoenix/phoenix:latest
```

---

**7.0.15.7 Telemetry Configuration**

The installer scripts can optionally configure telemetry:

```
[3/4] Telemetry configuration
      Enable OpenTelemetry tracing? (requires arize-phoenix) [y/N]: y

      Configuring telemetry...
      ✅ OTEL endpoint: http://localhost:6006/v1/traces
      ✅ Service name: powerbi-analyst-skill

      Note: Start Arize Phoenix before using the skill:
            python -m phoenix.server.main serve
```

**Configuration Generated (if enabled):**

The installer sets environment variables in the MCP server configuration:

```json
{
  "mcpServers": {
    "powerbi-modeling": {
      "command": "C:/path/to/powerbi-modeling-mcp.exe",
      "args": [],
      "env": {
        "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
        "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:6006/v1/traces",
        "OTEL_SERVICE_NAME": "powerbi-analyst-skill"
      }
    }
  }
}
```

**Runtime Behavior:**

```
IF CLAUDE_CODE_ENABLE_TELEMETRY == "1":
    1. Initialize OTEL TracerProvider
    2. Create BatchSpanProcessor with OTLP exporter
    3. Wrap agent invocations in spans
    4. Export traces to configured endpoint
ELSE:
    1. Skip OTEL initialization
    2. Use existing post-mortem analytics (token_analyzer.py)
```

**Telemetry Disabled Warning (if endpoint unavailable):**

```
⚠️ TELEMETRY UNAVAILABLE

OpenTelemetry is enabled but the endpoint is not responding:
  http://localhost:6006/v1/traces

Options:
  [1] Start Arize Phoenix: python -m phoenix.server.main serve
  [2] Continue without telemetry
  [3] Disable telemetry permanently (re-run installer)
```

---

#### 7.0.16 UX Requirements

**Single Entry Point: `/power-bi-assistant`**

Users interact with the skill through a single command. Internal agents are not exposed as separate invocable commands.

```
USER INTERFACE

/power-bi-assistant  ← Single entry point (user-invocable)
        │
        └─ Internal agents (hidden from help menu):
            ├─ powerbi-dax-specialist
            ├─ powerbi-mcode-specialist
            ├─ powerbi-visual-locator
            ├─ powerbi-page-layout-designer
            ├─ powerbi-pbir-validator
            └─ ... (other specialist agents)
```

**User Experience Flow:**

```
USER: /power-bi-assistant

SKILL: Welcome to the Power BI Analyst. What would you like to do?

  [1] Evaluate - Diagnose issues in a Power BI project
  [2] Create   - Create new measures, columns, tables, or visuals
  [3] Implement - Apply planned changes and deploy
  [4] Merge    - Compare and merge two Power BI projects
  [5] Help     - Learn about capabilities and troubleshooting

USER: 1

SKILL: Please provide the path to your Power BI project (.pbip folder or .pbix file).
```

**"Aggressive Help" for Permission Errors:**

When users encounter permission issues (e.g., missing MCP tools, folder access), the skill provides exact JSON configuration snippets rather than generic instructions.

**Example - MCP Not Configured:**

```
❌ CONFIGURATION REQUIRED

The Power BI Modeling MCP is not configured in your Claude Desktop settings.

📋 Copy this exact JSON into your claude_desktop_config.json:

{
  "mcpServers": {
    "powerbi-modeling": {
      "command": "C:\\Program Files\\PowerBI Modeling MCP\\powerbi-modeling-mcp.exe",
      "args": [],
      "env": {}
    }
  }
}

📂 Config file location:
   %APPDATA%\Claude\claude_desktop_config.json

After adding this, restart Claude Desktop.
```

**Example - Folder Permission Error:**

```
❌ FOLDER ACCESS DENIED

Claude Code cannot access: C:\Users\John\Documents\PowerBI Projects

📋 Add this folder to your allowed list in .claude/settings.json:

{
  "permissions": {
    "allow": [
      "C:/Users/John/Documents/PowerBI Projects/**"
    ]
  }
}

📂 Settings file location:
   C:\Users\John\code\.claude\settings.json
```

**Example - Desktop Not Running:**

```
❌ CONNECTION FAILED: Power BI Desktop not detected

The MCP requires Power BI Desktop to be running with a file open.

📋 Steps to fix:
   1. Open Power BI Desktop
   2. Open your .pbix or .pbip file
   3. Wait for the model to fully load
   4. Try your command again

💡 The skill will auto-detect the open file once Desktop is running.
```

**Help Menu Visibility:**

| Element | Visibility | Reason |
|---------|------------|--------|
| `/power-bi-assistant` | ✅ Visible in `/help` | Single user entry point |
| `powerbi-dax-specialist` | ❌ Hidden | Internal agent |
| `powerbi-mcode-specialist` | ❌ Hidden | Internal agent |
| `powerbi-visual-locator` | ❌ Hidden | Internal agent |
| Other specialist agents | ❌ Hidden | Internal agents |

**Authentication Guidance:**

For Desktop Mode (v1.0 scope), the only auth message needed is:

```
🖥️ DESKTOP MODE

This skill connects to Power BI Desktop using Windows Integrated Authentication.

Prerequisites:
  ✓ Power BI Desktop installed and running
  ✓ A .pbix or .pbip file open in Desktop

No Azure login or service principal configuration required.
```

---

#### 7.0.17 MCP Compliance Protocol

**Context:** Use this protocol whenever the user invokes powerbi-modeling-mcp or requests Power BI data modeling tasks. This protocol ensures safe handling of potentially sensitive data.

---

##### 7.0.17.1 Connection Integrity Check

Before initializing any MCP tool use, the AI must classify the session intent and enforce the corresponding connection method.

**Intent 1: Schema Management (Safe Mode)**

| Attribute | Description |
|-----------|-------------|
| **Description** | Tasks involving creating measures, organizing tables, bulk renaming, or formatting DAX |
| **Data Exposure** | None - metadata only |
| **Use Cases** | Code review, measure creation, schema changes |

**Protocol:**
1. Instruct user to close Power BI Desktop
2. Instruct user to delete `cache.abf` from the project's `.pbi` folder
   - Path: `[ProjectName].Dataset\.pbi\cache.abf`
3. **Mandatory Connection:** Connect ONLY via the PBIP Folder path
4. **Verification:** Confirm `dax_query_operations` are unavailable

```
✅ SCHEMA MODE ACTIVE

Connected via: PBIP Folder (C:\Projects\SalesAnalytics\)
Desktop: Closed (verified)
Cache: Deleted (cache.abf removed)

Available Operations:
• measure_operations.create/update/delete
• table_operations.create/rename
• column_operations.create/rename
• relationship_operations.*

Restricted Operations:
• dax_query_operations.execute() ← BLOCKED
• Data sampling ← BLOCKED
```

---

**Intent 2: Data Validation (Live/Debug Mode)**

| Attribute | Description |
|-----------|-------------|
| **Description** | Tasks requiring query execution, debugging circular dependencies, or performance testing |
| **Data Exposure** | Yes - actual data values visible |
| **Use Cases** | Debugging measures, testing calculations, data validation |

**Protocol:**
1. **Stop Condition:** Halt and request confirmation of data anonymization
2. **Query:** "Have you applied `fxAnonymize` and refreshed with `ComplianceMode = TRUE`?"
3. **If Unconfirmed:** Deny live connection. Provide the M-Code Anonymization Pattern (see 7.0.17.3)
4. **If Confirmed:** Allow connection via Running Power BI Desktop

```
⚠️ LIVE MODE REQUESTED

This mode allows query execution against actual data.

Before proceeding, confirm:
  □ fxAnonymize function exists in the model
  □ ComplianceMode parameter = TRUE
  □ Data has been refreshed with anonymization active

Have you completed these steps? [Y/N]

If NO: I'll provide the anonymization setup instructions.
If YES: Proceeding with live connection.
```

---

##### 7.0.17.2 PII Sensitivity Scanning (Metadata Only)

The AI must perform a heuristic scan of the schema before recommending anonymization targets.

**Trigger:** Upon initial connection to a PBIP folder (Schema Mode)

**Action:** Analyze all `Table[Column]` names against standard PII patterns

**Patterns to Flag:**

| Category | Column Name Patterns |
|----------|---------------------|
| **Identity** | `Name`, `First`, `Last`, `Email`, `SSN`, `Social`, `ID` (if not FK), `User`, `Login` |
| **Contact** | `Phone`, `Mobile`, `Fax`, `Address`, `Street`, `City`, `Zip`, `Postal` |
| **Financial** | `Salary`, `Wage`, `Bonus`, `Commission`, `CreditCard`, `IBAN`, `Account` |

**Output:** Present a markdown list of "Recommended Columns for Masking" to the user for review.

```markdown
🔍 PII SCAN RESULTS

Scanning schema for potentially sensitive columns...

**Recommended for Anonymization:**

| Table | Column | Category | Confidence |
|-------|--------|----------|------------|
| Customer | CustomerName | Identity | High |
| Customer | Email | Identity | High |
| Customer | Phone | Contact | High |
| Customer | Address | Contact | High |
| Employee | SSN | Identity | High |
| Employee | Salary | Financial | High |
| Employee | BankAccount | Financial | Medium |

**Not Flagged (Review Manually):**
- Customer[CustomerID] - Appears to be FK, not PII
- Sales[TransactionID] - System identifier

Would you like me to generate the fxAnonymize function for these columns?
```

---

##### 7.0.17.3 Anonymization Logic Injection (M-Code)

When the user requests masking support or confirmation is needed for Live Mode, provide the standard deterministic hash pattern.

**Standard M-Code Pattern: `fxAnonymize`**

```m
// Specification: Deterministic SHA256 Hash with Toggle
// Usage: Create as 'fxAnonymize' and wrap sensitive columns
// Dependencies: Requires 'ComplianceMode' parameter (type: logical)

(InputString as any) as text =>
let
    RunAnonymization = ComplianceMode, // Must reference 'ComplianceMode' (type: logical) parameter
    SourceText = Text.From(InputString),
    HashText = Text.Start(Binary.ToText(Crypto.CreateHash(Algorithm.SHA256, Text.ToBinary(SourceText)), BinaryEncoding.Hex), 10),
    Result = if RunAnonymization = true then HashText else SourceText
in
    if InputString = null then null else Result
```

**Required Parameter: `ComplianceMode`**

```m
// Create as Named Expression in Power Query
true meta [IsParameterQuery=true, Type="Logical", IsParameterQueryRequired=true]
```

**Implementation in Table Partition:**

```m
let
    Source = Sql.Database("server", "database"),
    Customers = Source{[Schema="dbo", Item="Customers"]}[Data],

    // Apply anonymization to sensitive columns
    AnonymizedData = Table.TransformColumns(Customers, {
        {"CustomerName", each fxAnonymize(_)},
        {"Email", each fxAnonymize(_)},
        {"Phone", each fxAnonymize(_)},
        {"SSN", each fxAnonymize(_)}
    })
in
    AnonymizedData
```

**Key Properties:**
- **Deterministic:** Same input always produces same hash (enables joins, grouping)
- **Irreversible:** SHA256 hash cannot be reversed to original value
- **Toggle-Controlled:** `ComplianceMode = FALSE` bypasses anonymization for production
- **Null-Safe:** Handles null values gracefully

---

##### 7.0.17.4 TMDL Annotation for Anonymization Status

Add a comment block to the table's `.tmdl` file documenting anonymization configuration:

```tmdl
table Customer
    lineageTag: abc-123-def

    /// ╔════════════════════════════════════════════════════════════════╗
    /// ║ ANONYMIZATION CONFIGURATION                                    ║
    /// ╠════════════════════════════════════════════════════════════════╣
    /// ║ Status: ENABLED                                                ║
    /// ║ Function: fxAnonymize (SHA256 hash)                            ║
    /// ║ Toggle: ComplianceMode parameter                               ║
    /// ║                                                                ║
    /// ║ Masked Columns:                                                ║
    /// ║   • CustomerName (Identity)                                    ║
    /// ║   • Email (Identity)                                           ║
    /// ║   • Phone (Contact)                                            ║
    /// ║   • SSN (Identity)                                             ║
    /// ║                                                                ║
    /// ║ Last Modified: 2025-12-23T10:00:00Z                            ║
    /// ║ Modified By: powerbi-analyst skill                             ║
    /// ╚════════════════════════════════════════════════════════════════╝

    partition 'Customer-Partition' = m
        mode: import
        source = ...
```

---

##### 7.0.17.5 PBIX File Warning

When the user is working with a `.pbix` file (not `.pbip` folder), issue a warning:

```
⚠️ PBIX FORMAT DETECTED

Warning: PBIX files contain compressed binary data.
For strict compliance, please convert to PBIP format:

1. Open the .pbix file in Power BI Desktop
2. File → Save As → Select "Power BI Project (*.pbip)"
3. Delete the original .pbix file
4. Re-run this command on the new .pbip folder

Benefits of PBIP:
• Human-readable TMDL files (auditable)
• Git-friendly (proper version control)
• No cache.abf with pre-loaded data
• Explicit data source connections

Would you like instructions for conversion?
```

---

##### 7.0.17.6 Connection Mode Decision Tree

```
USER REQUEST RECEIVED
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Does request require data access?                              │
│  (query execution, debugging, validation with data)             │
└─────────────────────────────────────────────────────────────────┘
    │                           │
    │ NO                        │ YES
    ▼                           ▼
┌─────────────┐     ┌─────────────────────────────────────────────┐
│ SCHEMA MODE │     │  LIVE MODE GATE                             │
│             │     │  ─────────────────                          │
│ • Close     │     │  Ask: "Have you applied fxAnonymize         │
│   Desktop   │     │        and refreshed with                   │
│ • Delete    │     │        ComplianceMode = TRUE?"              │
│   cache.abf │     │                                             │
│ • Connect   │     │  ┌─────────┬─────────────┐                  │
│   via PBIP  │     │  │ YES     │ NO/UNSURE   │                  │
└─────────────┘     │  ▼         ▼             │                  │
                    │ ALLOW     PROVIDE        │                  │
                    │ LIVE      ANONYMIZATION  │                  │
                    │ MODE      INSTRUCTIONS   │                  │
                    └─────────────────────────────────────────────┘
```

---

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

**8.1 Files CREATED** *(Implemented)*

| File | Location | Purpose |
|------|----------|---------|
| `install.ps1` | `skills/powerbi-analyst/` | Windows PowerShell installer |
| `install.sh` | `skills/powerbi-analyst/` | macOS/Linux Bash installer |
| `state_manage.ps1` | `.claude/tools/` | Windows state management CLI |
| `state_manage.sh` | `.claude/tools/` | macOS/Linux state management CLI |
| `SKILL.md` | `skills/powerbi-analyst/` | Main skill entry point |
| `INSTALL.md` | Repository root | Plugin installation guide |

**8.2 Files to DELETE**

| File/Folder | Reason |
|-------------|--------|
| `xmla_agent/` | Replaced by MCP - no custom XMLA scripts needed |
| Deprecated agents | Any agents replaced by MCP operations |
| Python XMLA scripts | Authentication handled by MCP's Azure Identity SDK |
| Custom MSAL/token scripts | Eliminated - MCP handles auth internally |

**8.3 Files to UPDATE**

| File | Changes |
|------|---------|
| `README.md` | New architecture, single entry point (`/power-bi-assistant`) |
| `CLAUDE.md` | Updated workflow references |
| `.claude/README.md` | Remove references to deleted agents |
| `.claude/settings.json` | Add skill allowlist configuration |

**8.4 Final Documentation**
- [ ] Create architecture diagram showing MCP + File-based hybrid
- [ ] Document Desktop Mode configuration
- [ ] Document "Aggressive Help" error messages
- [ ] Update troubleshooting guide

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

**Authentication Complexity:** ✅ RISK REDUCED

By using the Microsoft Power BI Modeling MCP, authentication is **offloaded to the Azure Identity SDK** (built into the MCP binary). This **reduces our risk** significantly:

| Previous Risk | MCP Mitigation |
|---------------|----------------|
| Custom MSAL token scripts | ❌ Eliminated - Azure Identity handles token acquisition |
| Token cache management | ❌ Eliminated - OS credential store used |
| Device code flow implementation | ❌ Eliminated - MCP handles internally |
| Service principal configuration | ✅ Simplified - just set 3 env vars |

**Remaining Risk: User Environment Configuration**

The risk shifts from "auth implementation" to "user environment readiness":
- Is `az login` active? (for Fabric connections)
- Is Desktop running? (for Desktop connections)
- Are service principal env vars set? (for CI/CD)

**Mitigation:**
- Installer scripts diagnose environment issues:
  - Check for `az` CLI installation
  - Verify `az account show` returns valid session
  - Test MCP connectivity before completing install
- Support all three connection types (Desktop, Fabric, PBIP)
- Provide clear auth troubleshooting in error messages (see 7.0.14.6)
- Document Azure CLI setup for Fabric access

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

## 6. Success Criteria (Definition of Done)

### 6.1 Functional (Desktop Mode)

- [ ] All 4 workflows work with MCP backend (Evaluate, Create, Implement, Merge)
- [ ] Can connect to Power BI Desktop via Windows Integrated Auth
- [ ] PBIR agents work unchanged for Report/Visual operations
- [ ] Single entry point `/power-bi-assistant` surfaces all workflows
- [ ] "Aggressive Help" provides copy-paste JSON for configuration errors

### 6.2 Architecture

- [ ] **Hybrid Architecture documented**: MCP for Semantic Model + File-based for PBIR
- [ ] **Agent count reduced**: From 27 to ~18 (net reduction of 9, with 2 new specialists)
- [ ] **No pbi-tools dependency** for semantic model operations
- [ ] **Empty `env` block** as default Desktop Mode configuration

### 6.3 Distribution & Packaging

- [ ] **Dual installation paths** documented and functional:
  - Quick Install: `install.bat` for non-technical users
  - Manual Setup: `MANUAL_SETUP.md` for transparency/auditability
- [ ] **Desktop Mode defaults** in all generated configurations
- [ ] **Telemetry disabled by default** (no user prompts in installer)
- [ ] **Explicit runtime dependencies** listed in MANUAL_SETUP.md

### 6.4 Documentation

- [ ] README updated with new architecture and single entry point
- [ ] MANUAL_SETUP.md provides full transparency for manual installation
- [ ] Troubleshooting guide includes "Aggressive Help" examples
- [ ] Breaking changes documented (commands → single skill)

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

### Resolved Questions

#### Q4: Version Control Strategy ✅ RESOLVED (2025-12-21)

**Decision: Option B - PBIP as Source of Truth with Live Model Testing**

The MCP supports two complementary connection modes:
- **PBIP Folder Connection**: Reads/writes TMDL files directly (headless, Git-friendly)
- **Live Model Connection**: Desktop or Fabric for query execution and testing

**Hybrid Workflow Architecture:**

```
┌─────────────────────────────────────────────────────────────────┐
│  EDIT PHASE (Headless - PBIP as Source of Truth)                │
│  ───────────────────────────────────────────────                │
│  • Agent writes DAX/M code to TMDL files in PBIP folder         │
│  • MCP uses PBIP folder connection for schema operations        │
│  • Git always has the current state                             │
│  • No live model required for code generation                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  TEST PHASE (Live Model as Test Bench)                          │
│  ─────────────────────────────────────                          │
│  • MCP connects to live session (Desktop OR Fabric dev)         │
│  • MCP refreshes/reconnects to pick up TMDL changes             │
│  • Agent runs execute_query to validate DAX                     │
│  • Unit tests compare results against truth files               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  VERIFICATION (Automated Assertions)                            │
│  ───────────────────────────────────                            │
│  • Check for "flatline" (same value every row = missing rel)    │
│  • Logic check (manual calculation verification)                │
│  • Compare against control measures                             │
│  • Mark findings.md as "Verified" if passed                     │
└─────────────────────────────────────────────────────────────────┘
```

**Why this approach:**
- If you only edit the Live Model, you risk changes not being saved to Git
- PBIP files are the primary target; Live Session is only a Test Bench
- Repository is always the "Source of Truth"
- Tests are performed against the actual code that will be deployed

**Connection Priority for Testing:**
1. If Power BI Desktop is open → use Desktop connection
2. If Fabric dev workspace configured → use Fabric connection
3. If neither available → skip live testing, warn user

---

#### Q5: Transaction Scope ✅ RESOLVED (2025-12-21)

**Decision: Per-Workflow Transaction with Checkpoint Commits**

The MCP's `transaction_operations` supports begin/commit/rollback. Strategy:

```
WORKFLOW START
    │
    ▼
transaction_operations.begin()
    │
    ├── Operation 1: Create helper measure
    ├── Operation 2: Create main measure
    ├── Operation 3: Update visual bindings
    │
    ▼
[All operations succeed?]
    │
    ├── YES → transaction_operations.commit()
    │         └── Changes persisted to TMDL files
    │
    └── NO  → transaction_operations.rollback()
              └── All changes reverted, TMDL unchanged
```

**Transaction Boundaries:**
- One transaction per workflow invocation (EVALUATE, CREATE, IMPLEMENT, etc.)
- Related changes grouped together (e.g., measure + its dependencies)
- PBIR visual changes are NOT part of MCP transactions (file-based)

**Checkpoint Pattern for Long Workflows:**
```
CREATE_PAGE workflow (many artifacts):
  ├── Transaction 1: Create all measures (atomic)
  │   └── Commit if all measures succeed
  ├── Transaction 2: Create calculated columns (atomic)
  │   └── Commit if all columns succeed
  └── File operations: Create PBIR visuals (no transaction)
      └── Versioned copy provides rollback
```

---

#### Q6: Error Recovery ✅ RESOLVED (2025-12-21)

**Decision: Automatic Rollback + State Preservation + User Guidance**

**Error Detection:**
| Error Type | Detection | Recovery |
|------------|-----------|----------|
| MCP connection lost | Connection timeout | Retry once, then prompt user |
| DAX syntax error | MCP validation response | Show error, suggest fix |
| Transaction failure | MCP rollback triggered | Auto-rollback, preserve findings.md |
| PBIR file error | JSON parse failure | Restore from versioned copy |
| Partial completion | Task marked failed | Resume from last checkpoint |

**Recovery Flow:**
```
ERROR OCCURS
    │
    ▼
┌─────────────────────────────────────────┐
│  Step 1: Automatic Rollback             │
│  • MCP: transaction_operations.rollback()│
│  • PBIR: Restore from versioned copy    │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  Step 2: Preserve State                 │
│  • findings.md: Mark task as FAILED     │
│  • state.json: Record failure details   │
│  • Keep all diagnostic information      │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  Step 3: User Guidance                  │
│  ❌ OPERATION FAILED                    │
│                                         │
│  Error: [specific error message]        │
│  Changes have been rolled back.         │
│                                         │
│  To retry:                              │
│    • Fix: [suggested fix]               │
│    • Run: "retry the last operation"    │
│                                         │
│  Diagnostic info saved to:              │
│    .claude/tasks/<task-id>/findings.md  │
└─────────────────────────────────────────┘
```

**State Cleanup:**
- Failed tasks remain in `active_tasks` until explicitly archived
- Resource locks are released on failure
- User can resume or start fresh

---

#### Q7: Offline Support ✅ RESOLVED (2025-12-22)

**Decision: Option A - Keep File-Based Agents as Fallback**

> Should we keep file-based agents for offline use when MCP is unavailable?

**Decision:** Yes - maintain file-based agents as graceful fallback.

**Rationale:**
- File-based agents already exist and work (current implementation)
- Provides fallback when MCP is unavailable (not installed, broken, incompatible)
- Minimal maintenance burden (already built)
- Users without MCP can still use the skill in degraded mode

**Clarification on "Offline":**

The term "offline" was clarified during design discussion:
- **NOT about Desktop running:** PBIP folder connection via MCP is already headless
- **IS about MCP availability:** What happens when MCP itself is unavailable

**MCP Connection Modes (from Q4):**
| Mode | Requirement | Capability |
|------|-------------|------------|
| PBIP Folder | Just the folder | Headless - read/write TMDL, schema ops |
| Desktop | Desktop open | Live testing - execute DAX queries |
| Fabric | Cloud access | Live testing - execute DAX queries |

**Fallback Behavior:**

```
USER INVOKES SKILL
    │
    ├─ MCP Available?
    │   │
    │   ├─ YES → Use MCP (preferred)
    │   │        • Live validation
    │   │        • Schema operations via API
    │   │        • Data queries for context
    │   │
    │   └─ NO → Use File-Based Fallback (Section 7.0.9)
    │            • Parse TMDL files directly
    │            • LLM-based validation (best effort)
    │            • No live data queries
    │            • Clear warning to user about degraded mode
```

**File-Based Agents Retained:**
- `powerbi-verify-pbiproject-folder-setup` - TMDL parsing
- `powerbi-code-locator` - Grep-based code search
- `powerbi-data-context-agent` - XMLA queries (separate from MCP)
- `powerbi-pattern-discovery` - File-based pattern extraction

**User Experience in Fallback Mode:**
```
⚠️ MCP NOT AVAILABLE

The Power BI Modeling MCP is not available. Operating in fallback mode.

Limitations:
• No live DAX validation (syntax check only)
• No data sampling for context
• Schema read from TMDL files (may be stale)

To enable full functionality, install the Power BI Modeling MCP:
https://github.com/microsoft/powerbi-modeling-mcp

[C] Continue in fallback mode
[H] Help with MCP installation
```

---

#### Q8: PBIR via MCP ✅ RESOLVED (2025-12-22)

**Decision: Option B - Monitor and Adapt**

> Will Microsoft add report support to MCP? If so, when?

**Current State:**
- Power BI Modeling MCP supports **semantic model only** (measures, tables, columns, relationships)
- **Report/visual editing (PBIR) is NOT supported** by MCP
- All PBIR agents work with files directly (JSON editing)

**Decision:** Keep file-based PBIR agents now, monitor Microsoft roadmap, adapt if/when support is added.

**Current Architecture (Unchanged):**
```
SEMANTIC MODEL OPERATIONS          REPORT OPERATIONS
        │                                 │
        ▼                                 ▼
┌─────────────────┐              ┌─────────────────┐
│  Power BI MCP   │              │  File-Based     │
│  ─────────────  │              │  ─────────────  │
│  • Measures     │              │  • page.json    │
│  • Tables       │              │  • visual.json  │
│  • Columns      │              │  • config blobs │
│  • Relationships│              │  • layout       │
└─────────────────┘              └─────────────────┘
```

**PBIR Agents Retained (File-Based):**
- `powerbi-visual-locator` - Find visuals in PBIR structure
- `powerbi-visual-type-recommender` - Suggest visual types
- `powerbi-page-layout-designer` - Generate layout coordinates
- `powerbi-interaction-designer` - Design cross-filtering
- `powerbi-pbir-page-generator` - Generate page JSON files
- `powerbi-pbir-validator` - Validate PBIR JSON structure
- `powerbi-visual-implementer-apply` - Apply visual changes

**Monitoring Plan:**
- Check Microsoft's MCP repository quarterly: https://github.com/microsoft/powerbi-modeling-mcp
- Watch for `report_operations` or `visual_operations` in MCP changelog
- If added: Evaluate migration of PBIR agents to MCP

**Future Migration (If PBIR MCP Support Added):**
```
IF Microsoft adds report_operations to MCP:
    │
    ├─ Evaluate API capabilities vs current file-based
    │
    ├─ If MCP provides equivalent functionality:
    │   └─ Migrate PBIR agents to use MCP
    │   └─ Keep file-based as fallback (per Q7 decision)
    │
    └─ If MCP is limited:
        └─ Keep file-based for complex operations
        └─ Use MCP for simple operations
```

---

#### Q9: Skill Distribution ✅ RESOLVED (2025-12-22)

**Decision: Option A (Manual) Now, Option D (Install Script) Later**

> How will we distribute the skill with MCP dependency?

**Phase 1 (Current): Manual Installation**
- Users clone the repository or copy `.claude/` folder
- MCP documented as prerequisite in README
- Setup steps documented

**Installation Documentation:**
```markdown
## Prerequisites

1. Claude Code CLI installed
2. Power BI Modeling MCP installed:
   - Download from: https://github.com/microsoft/powerbi-modeling-mcp
   - Follow Microsoft's installation instructions

## Installation

1. Clone this repository:
   git clone https://github.com/<org>/powerbi-analyst-plugin.git

2. Copy the skill to your project:
   cp -r powerbi-analyst-plugin/.claude/ your-project/.claude/

3. Verify installation:
   - Open Claude Code in your project
   - Type: /power-bi-assistant
   - Should see skill options
```

**Phase 2 (Future): GitHub Release + Install Script**
- Create versioned GitHub releases
- Provide install script that:
  - Copies files to `.claude/`
  - Checks for MCP installation
  - Validates prerequisites
  - Provides clear error messages

**Future Install Script Concept:**
```bash
#!/bin/bash
# install-powerbi-skill.sh

# Check prerequisites
if ! command -v claude &> /dev/null; then
    echo "❌ Claude Code CLI not found. Install from: https://claude.ai/code"
    exit 1
fi

# Check for MCP (platform-specific)
# ... MCP detection logic ...

# Copy skill files
cp -r .claude/ ~/.claude/skills/powerbi-analyst/

echo "✅ Power BI Analyst skill installed"
echo "Run '/power-bi-assistant' to get started"
```

**Version Compatibility Matrix (Future):**
| Skill Version | MCP Version | Claude Code Version |
|---------------|-------------|---------------------|
| 1.0.x | 1.x | 1.x |
| (to be defined as versions are released) |

**Rationale:**
- Focus on making skill work first
- Distribution polish can come later
- Manual installation is sufficient for initial users
- Install script is a nice-to-have enhancement

---

## 9. Next Steps

1. **Immediate:** Delete deprecated agents (Phase 1.1)
2. **This Week:** Set up MCP and test connection types (Phase 2.1)
3. **Decide:** Offline support strategy (Question 1)
4. **Prioritize:** Start with /evaluate command (most used)

---

## Appendix C: Command → Workflow Phase Mapping

This appendix provides detailed phase-by-phase mapping from current slash commands to skill workflows, documenting which agents are replaced by MCP, which are kept, and which are enhanced.

---

### C.1 `/evaluate-pbi-project-file` → EVALUATE Workflow

**Purpose:** Diagnose issues with existing Power BI code and propose fixes.

| Current Phase | Skill Equivalent | Agent Changes |
|---------------|------------------|---------------|
| **Phase 1: Validation & Setup** | Same | REPLACE `powerbi-verify-pbiproject-folder-setup` → `mcp.connection_operations.connect()` |
| **Phase 2: Scratchpad** | Same | KEEP (file-based, no MCP needed) |
| **Phase 3: Clarification** | Same | KEEP (LLM reasoning, human-in-the-loop) |
| **Phase 4: Data Context** | MCP-enhanced | REPLACE `powerbi-data-context-agent` (Python XMLA) → `mcp.dax_query_operations.execute()` |
| **Phase 5: Code Location** | MCP-enhanced | REPLACE `powerbi-code-locator` (grep TMDL) → `mcp.measure_operations.get()` |
| **Phase 6: Planning** | Same | KEEP `powerbi-dashboard-update-planner` (LLM reasoning) |
| **Phase 7: Verification** | Same | KEEP `power-bi-verification` (LLM semantic review) |
| **Phase 8: Completion** | Same | KEEP (file-based summary) |

**Net Agent Changes:**
- Removed: 2 (`powerbi-verify-pbiproject-folder-setup`, `powerbi-code-locator`)
- Replaced: 1 (`powerbi-data-context-agent` → MCP)
- Kept: 3 (`powerbi-dashboard-update-planner`, `power-bi-verification`, scratchpad ops)

---

### C.2 `/create-pbi-artifact` → CREATE_ARTIFACT Workflow

**Purpose:** Create new measures, calculated columns, tables, or visuals through interactive specification.

| Current Phase | Skill Equivalent | Agent Changes |
|---------------|------------------|---------------|
| **Phase 1: Validation & Setup** | Same | REPLACE `powerbi-verify-pbiproject-folder-setup` → `mcp.connection_operations.connect()` |
| **Phase 2: Scratchpad** | Same | KEEP |
| **Phase 3: Data Model Analysis** | MCP-enhanced | REPLACE `powerbi-data-model-analyzer` → `mcp.table_operations.list()` + `mcp.column_operations.list()` |
| **Phase 3.5: Decomposition** | Same | KEEP `powerbi-artifact-decomposer` (LLM reasoning) |
| **Phase 4: Data Understanding** | Enhanced | KEEP `powerbi-data-understanding-agent` + ADD data sampling via `mcp.dax_query_operations.execute()` |
| **Phase 5: Pattern Discovery** | MCP-enhanced | ENHANCE `powerbi-pattern-discovery` + use `mcp.measure_operations.list()` |
| **Phase 6: Code Generation** | Specialist | REMOVE `powerbi-artifact-designer` → skill.md (main LLM thread) delegates to DAX Specialist or M-Code Specialist |
| **Phase 7: Completion** | Same | KEEP |

**Specialist Delegation (Phase 6):**
- Measure, Calculated Column, KPI → **DAX Specialist** with `mcp.dax_query_operations.validate()`
- Partition, Named Expression, Table (Import) → **M-Code Specialist** with `mcp.partition_operations`
- Visual → skill.md (main LLM thread) handles directly (PBIR, not MCP)

**Net Agent Changes:**
- Removed: 3 (`powerbi-verify-pbiproject-folder-setup`, `powerbi-data-model-analyzer`, `powerbi-artifact-designer`)
- Added: 2 (DAX Specialist, M-Code Specialist)
- Kept: 3 (`powerbi-artifact-decomposer`, `powerbi-data-understanding-agent`, `powerbi-pattern-discovery`)

---

### C.3 `/create-pbi-page-specs` → CREATE_PAGE Workflow

**Purpose:** Create complete specifications for a new Power BI report page.

| Current Phase | Skill Equivalent | Agent Changes |
|---------------|------------------|---------------|
| **Phase 1: Prerequisites** | Same | REPLACE → `mcp.connection_operations.connect()` + PBIR detection (Section 7.0.12.1) |
| **Phase 2: Scratchpad** | Same | KEEP |
| **Phase 3: Question Analysis** | Same | KEEP `powerbi-page-question-analyzer` (LLM reasoning) |
| **Phase 4: Schema Analysis** | MCP-enhanced | REPLACE `powerbi-data-model-analyzer` → MCP schema ops |
| **Phase 5: Decomposition** | Same | KEEP `powerbi-artifact-decomposer` (page mode) |
| **Phase 6A: Measure Specs** | Specialist | Same as CREATE_ARTIFACT Phase 6 (DAX Specialist) |
| **Phase 6B: Visual Specs** | Same | KEEP `powerbi-visual-type-recommender`, `powerbi-data-understanding-agent` (visual mode) |
| **Phase 7: Layout Design** | Same | KEEP `powerbi-page-layout-designer` (PBIR only) |
| **Phase 8: Interaction Design** | Same | KEEP `powerbi-interaction-designer` (PBIR only) |
| **Phase 9: PBIR Generation** | Same | KEEP `powerbi-pbir-page-generator` (PBIR only) |
| **Phase 10: Helper Pages** | Same | KEEP (orchestrator logic) |
| **Phase 11: Validation** | Enhanced | KEEP `power-bi-verification` + ADD `mcp.dax_query_operations.validate()` |
| **Phase 12: Summary** | Same | KEEP |

**Net Agent Changes:**
- Removed: 2 (`powerbi-verify-pbiproject-folder-setup`, `powerbi-data-model-analyzer`)
- Enhanced: 1 (`power-bi-verification` with MCP validation)
- Kept: 7 (all PBIR agents, question analyzer, decomposer, visual recommender)

---

### C.4 `/implement-deploy-test-pbi-project-file` → IMPLEMENT Workflow

**Purpose:** Apply proposed changes from findings.md to the project, deploy, and test.

| Current Phase | Skill Equivalent | Agent Changes |
|---------------|------------------|---------------|
| **Phase 1: Validation** | Same | KEEP (read findings.md, extract metadata) |
| **Phase 2a: Apply Code** | MCP transactional | REPLACE `powerbi-code-implementer-apply` → `mcp.transaction_operations.begin()` + `mcp.measure_operations.create/update()` + `mcp.transaction_operations.commit()` |
| **Phase 2b: Apply Visuals** | Same | KEEP `powerbi-visual-implementer-apply` (PBIR only) |
| **Phase 2.5: TMDL Validation** | MCP implicit | REMOVE `powerbi-tmdl-syntax-validator` (MCP validates on operation) |
| **Phase 2.6: PBIR Validation** | Same | KEEP `powerbi-pbir-validator` (PBIR only) |
| **Phase 3: DAX Validation** | MCP-enhanced | ENHANCE `powerbi-dax-review-agent` + `mcp.dax_query_operations.validate()` |
| **Phase 4: Deployment** | MCP | REPLACE pbi-tools CLI → `mcp.database_operations.deploy()` |
| **Phase 5: Testing** | Same | KEEP `powerbi-playwright-tester` |
| **Phase 6: Consolidation** | Same | KEEP (update findings.md) |
| **Phase 7: Summary** | Same | KEEP |

**Transaction Pattern:**
```
mcp.transaction_operations.begin()
  ├── For each measure in Section 2.A:
  │     mcp.measure_operations.create/update()
  ├── Validation: mcp.dax_query_operations.validate()
  └── mcp.transaction_operations.commit() OR rollback()

Then: PBIR changes (file-based, versioned copy provides rollback)
```

**Net Agent Changes:**
- Removed: 2 (`powerbi-code-implementer-apply`, `powerbi-tmdl-syntax-validator`)
- Enhanced: 1 (`powerbi-dax-review-agent` with MCP)
- Kept: 3 (`powerbi-visual-implementer-apply`, `powerbi-pbir-validator`, `powerbi-playwright-tester`)

---

### C.5 `/analyze-pbi-dashboard` → ANALYZE Workflow

**Purpose:** Create business-friendly documentation of an existing Power BI dashboard.

| Current Phase | Skill Equivalent | Agent Changes |
|---------------|------------------|---------------|
| **Phase 1: Validation** | Same | REPLACE → `mcp.connection_operations.connect()` |
| **Phase 2: Page Discovery** | Same | KEEP (PBIR file reading) |
| **Phase 3: Measure Analysis** | MCP-enhanced | ENHANCE: use `mcp.measure_operations.list()` + `mcp.measure_operations.get()` |
| **Phase 4: Business Synthesis** | Same | KEEP (LLM translation) |
| **Phase 5: Output** | Same | KEEP (markdown generation) |

**Net Agent Changes:**
- Removed: 1 (`powerbi-verify-pbiproject-folder-setup`)
- Enhanced: 1 (measure extraction via MCP)
- Kept: All PBIR analysis, LLM synthesis

---

### C.6 `/merge-powerbi-projects` → MERGE Workflow

**Purpose:** Compare two Power BI projects and merge changes.

| Current Phase | Skill Equivalent | Agent Changes |
|---------------|------------------|---------------|
| **Phase 1: Validate Input** | Dual connection | ENHANCE: `mcp.connection_operations.connect(project_a)` + `mcp.connection_operations.connect(project_b)` |
| **Phase 2: Comparison** | MCP-enhanced | ENHANCE `powerbi-compare-project-code` + use MCP to extract both model schemas |
| **Phase 3: Business Analysis** | Same | KEEP `powerbi-code-understander` (LLM reasoning) |
| **Phase 4: User Decisions** | Same | KEEP (human-in-the-loop) |
| **Phase 5: Parse Decisions** | Same | KEEP (orchestrator logic) |
| **Phase 6: Execute Merge** | MCP transactional | REPLACE `powerbi-code-merger` → `mcp.transaction_operations` for atomic merge |
| **Phase 6.5: TMDL Validation** | MCP implicit | REMOVE (MCP validates on operation) |
| **Phase 6.6: DAX Validation** | MCP-enhanced | ENHANCE with `mcp.dax_query_operations.validate()` |
| **Phase 7: Final Report** | Same | KEEP |

**Dual Connection Pattern:**
```
connection_a = mcp.connection_operations.connect(project_a_path)
connection_b = mcp.connection_operations.connect(project_b_path)

# Extract schemas from both
schema_a = mcp.table_operations.list(connection=connection_a)
schema_b = mcp.table_operations.list(connection=connection_b)

# Compare using LLM
differences = powerbi-compare-project-code(schema_a, schema_b)

# Apply merge decisions with transaction
mcp.transaction_operations.begin(connection=connection_a)
  for decision in user_decisions:
    if decision.choice == "comparison":
      mcp.measure_operations.update(definition_from_b)
mcp.transaction_operations.commit()
```

**Net Agent Changes:**
- Removed: 2 (`powerbi-code-merger`, `powerbi-tmdl-syntax-validator`)
- Enhanced: 2 (`powerbi-compare-project-code`, DAX validation)
- Kept: 1 (`powerbi-code-understander`)

---

### C.7 Summary: Agent Migration Matrix

| Agent | Current Role | Migration Status | Replacement |
|-------|--------------|------------------|-------------|
| `powerbi-verify-pbiproject-folder-setup` | Validate project | REMOVE | `mcp.connection_operations.connect()` |
| `powerbi-data-model-analyzer` | Extract schema | REMOVE | `mcp.table/column/measure_operations.list()` |
| `powerbi-data-context-agent` | Query data (XMLA) | REMOVE | `mcp.dax_query_operations.execute()` |
| `powerbi-code-locator` | Find measures | REMOVE | `mcp.measure_operations.get()` |
| `powerbi-code-implementer-apply` | Apply TMDL changes | REMOVE | `mcp.transaction_operations` + ops |
| `powerbi-code-merger` | Apply merge | REMOVE | `mcp.transaction_operations` |
| `powerbi-tmdl-syntax-validator` | Validate TMDL | REMOVE | MCP validates implicitly |
| `powerbi-artifact-designer` | Generate code | REMOVE | Orchestration → skill.md; Code → Specialists |
| `powerbi-pattern-discovery` | Find patterns | ENHANCE | + MCP measure listing |
| `powerbi-dax-review-agent` | DAX validation | ENHANCE | + `mcp.dax_query_operations.validate()` |
| `powerbi-compare-project-code` | Compare models | ENHANCE | + MCP schema extraction |
| `powerbi-dashboard-update-planner` | Plan changes | KEEP | LLM reasoning |
| `power-bi-verification` | Semantic review | KEEP | LLM reasoning |
| `powerbi-artifact-decomposer` | Break down artifacts | KEEP | LLM reasoning |
| `powerbi-data-understanding-agent` | Interactive Q&A | KEEP | LLM reasoning |
| `powerbi-code-understander` | Explain differences | KEEP | LLM reasoning |
| All PBIR agents (6) | Visual/page editing | KEEP | MCP doesn't support reports |
| `powerbi-playwright-tester` | Browser testing | KEEP | Playwright MCP |
| NEW: `powerbi-dax-specialist` | DAX code generation | ADD | With MCP validation |
| NEW: `powerbi-mcode-specialist` | M code generation | ADD | With MCP ops |

**Summary:**
- REMOVED: 8 agents (replaced by MCP operations or skill.md)
- ENHANCED: 3 agents (augmented with MCP)
- KEPT: 14 agents (LLM reasoning, PBIR, testing)
- ADDED: 2 specialists (DAX, M-Code)
- **NET: 27 → 18 agents** (9 reduction)

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
| powerbi-artifact-designer | REMOVE | Orchestration → skill.md; Code → Specialists |
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

## Appendix D: State Manager (state_manage.ps1 / state_manage.sh)

The state management scripts maintain session-level "Global Truth" in `.claude/state.json`.

> **Complete Specification:** See Section 7.0.8 for the full state management specification including:
> - Complete state schema (7.0.8.2)
> - Session recovery behavior (7.0.8.3)
> - Task lifecycle (7.0.8.4)
> - Agent communication protocol (7.0.8.5)
> - Resource locking protocol (7.0.8.6)
> - Model schema caching (7.0.8.7)
> - CLI command reference (7.0.8.9)

**Core Features:**

| Feature | Command | Purpose |
|---------|---------|---------|
| State Persistence | Load/Save | JSON read/write to `.claude/state.json` |
| Task Creation | `-CreateTask` / `create-task` | Creates timestamped task folder in `.claude/tasks/` |
| Resource Locking | `-Lock` / `lock` | Prevents concurrent edits to same file |
| Lock Release | `-Release` / `release` | Frees resource after task completion |

**Implementation Status:** ✅ Complete

Scripts are located in `.claude/tools/`:
- `state_manage.ps1` - Windows PowerShell (full-featured, ~475 lines)
- `state_manage.sh` - macOS/Linux Bash + jq (full-featured, ~350 lines)
- `state_manage.cmd` - Windows CMD fallback (delegates to PowerShell)

**Key CLI Commands:**

```powershell
# Windows PowerShell
.\state_manage.ps1 -Summary                           # Show state, detect session recovery
.\state_manage.ps1 -CreateTask "name" -WorkflowType evaluate  # Create task workspace
.\state_manage.ps1 -Archive -TaskId <id>              # Archive completed task
.\state_manage.ps1 -Lock -Resource <path> -TaskId <id>        # Acquire lock
.\state_manage.ps1 -Release -Resource <path> -TaskId <id>     # Release lock
```

```bash
# macOS/Linux Bash
./state_manage.sh summary                             # Show state, detect session recovery
./state_manage.sh create-task "name" evaluate         # Create task workspace
./state_manage.sh archive <task_id>                   # Archive completed task
./state_manage.sh lock <path> <task_id>               # Acquire lock
./state_manage.sh release <path> <task_id>            # Release lock
```

**Integration with Skill:**
- Orchestrator calls `summary` at session start (triggers recovery prompt if needed)
- Each sub-agent receives `TASK_PATH` and writes to `findings.md`
- Locks prevent race conditions when multiple agents work in parallel
- State is archived when task completes via `archive`
- Archived task summaries persist in `archived_tasks[]` for project memory
