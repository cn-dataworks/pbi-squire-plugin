# Power BI Skill Migration: Readiness Analysis

**Analysis Date:** 2025-12-20
**Spec Version:** Draft (from SPEC.md)
**Status:** NOT READY FOR IMPLEMENTATION
**Estimated Additional Spec Work:** 8-16 hours

---

## Summary

The SPEC.md provides excellent strategic direction for converting the Power BI Analyst Plugin to a skill with MCP integration. However, significant gaps exist that would cause implementation failures. This document itemizes all gaps as actionable tasks.

---

## Task Tracking

### Legend
- [ ] Not started
- [x] Complete
- [~] In progress

---

## Section 1: Critical Gaps (Must Fix Before Implementation)

### 1.1 Complete Skill Prompt
**Priority:** P0 (Blocker)
**Effort:** 4-6 hours
**Status:** [x] Complete (2025-12-20)

**Current State:**
The `skill.md` is a 20-line placeholder skeleton that references non-existent agents (`agents/visual_analyst.md`, `agents/dax_specialist.md`).

**Required Deliverable:**
A complete skill prompt (200-400 lines) containing:

- [x] **1.1.1** Skill metadata block (name, description, allowed-tools, dependencies) → SPEC.md Section 7.0.1-7.0.3
- [x] **1.1.2** Session initialization logic (MCP detection, connection, state.json init) → SPEC.md Section 7.0.4
- [x] **1.1.3** Intent classification rules (map natural language to workflow type) → SPEC.md Section 7.0.5
- [x] **1.1.4** Workflow execution sections for all 6 command equivalents → SPEC.md Section 7.0.6
  - [x] Evaluate workflow (diagnose/fix)
  - [x] Create artifact workflow (new measures/columns/visuals)
  - [x] Create page workflow (new dashboard pages)
  - [x] Implement workflow (apply changes)
  - [x] Analyze workflow (document existing)
  - [x] Merge workflow (compare/merge projects)
- [x] **1.1.5** Specialist delegation rules (when to invoke DAX vs M-Code specialists) → SPEC.md Section 7.0.7
- [x] **1.1.6** State management patterns (state.json updates, task lifecycle) → SPEC.md Section 7.0.8 (TODO: complete schema)
- [x] **1.1.7** Error handling and fallback logic (MCP failure recovery) → SPEC.md Section 7.0.9
- [x] **1.1.8** Validation gate integration (DAX review, PBIR validation, TMDL syntax) → SPEC.md Section 7.0.10
- [x] **1.1.9** Human-in-the-loop confirmation patterns → SPEC.md Section 7.0.11
- [x] **1.1.10** Format-specific handling (PBIP vs PBIX vs pbi-tools extracted) → SPEC.md Section 7.0.12

**Acceptance Criteria:**
- Skill can be invoked with natural language requests
- Skill correctly routes to appropriate workflow
- Skill handles MCP unavailability gracefully

---

### 1.2 Intent Router Design
**Priority:** P0 (Blocker)
**Effort:** 2-3 hours
**Status:** [ ] Not started

**Current State:**
No mechanism exists to map natural language requests to specific workflows.

**Required Deliverable:**
Intent classification logic that maps requests to workflows.

- [ ] **1.2.1** Define intent categories:
  ```
  EVALUATE   - diagnose, fix, debug, wrong, incorrect, not working, issue
  CREATE     - add, create, new, build (for artifacts)
  PAGE       - page, dashboard, screen, view (for full pages)
  IMPLEMENT  - apply, deploy, implement, execute, run changes
  ANALYZE    - explain, document, what does, understand, describe
  MERGE      - merge, compare, diff, combine, sync
  ```

- [ ] **1.2.2** Define keyword detection rules with priority ordering

- [ ] **1.2.3** Define ambiguity resolution prompts (when multiple intents detected)

- [ ] **1.2.4** Define explicit override patterns (user says "use evaluate workflow")

- [ ] **1.2.5** Create intent→workflow mapping table:
  | Intent | Primary Keywords | Workflow Section | Required Inputs |
  |--------|------------------|------------------|-----------------|
  | EVALUATE | fix, wrong, issue | 3.1 | project path, problem description |
  | CREATE | add measure, new column | 3.2 | project path, artifact type, description |
  | ... | ... | ... | ... |

**Acceptance Criteria:**
- Natural language requests are correctly classified
- Ambiguous requests prompt for clarification
- User can override classification

---

### 1.3 MCP Connection Bootstrap Flow
**Priority:** P0 (Blocker)
**Effort:** 3-4 hours
**Status:** [ ] Not started

**Current State:**
SPEC.md references MCP operations but provides no connection initialization flow.

**Required Deliverable:**
Complete MCP connection bootstrapping specification.

- [ ] **1.3.1** MCP availability detection:
  ```
  Check if mcp_pbi_tool is available in tool list
  If not available → fallback to file-based mode
  ```

- [ ] **1.3.2** Connection type selection flow:
  ```
  Prompt user:
  [1] Power BI Desktop (requires running instance)
  [2] Fabric Workspace (cloud connection)
  [3] PBIP Folder (file-based with MCP validation)
  ```

- [ ] **1.3.3** Per-connection-type initialization:
  - Desktop: `mcp.connection_operations.connect_desktop(port?)`
  - Fabric: `mcp.connection_operations.connect_fabric(workspace_id, dataset_id)`
  - PBIP: `mcp.connection_operations.connect_pbip(folder_path)`

- [ ] **1.3.4** Connection validation and retry logic

- [ ] **1.3.5** Session persistence (connection caching within session)

- [ ] **1.3.6** Timeout handling (what happens if MCP doesn't respond in 30s?)

- [ ] **1.3.7** Credential requirements per connection type

- [ ] **1.3.8** Document MCP tool signatures (from MCP GitHub repo)

**Acceptance Criteria:**
- Skill can establish MCP connection for all 3 connection types
- Connection failures are handled gracefully with user feedback
- Sessions persist connections appropriately

---

### 1.4 Specialist Agent Prompts
**Priority:** P0 (Blocker)
**Effort:** 3-4 hours
**Status:** [ ] Not started

**Current State:**
Section 2.5 describes two specialists but no `.md` files exist.

**Required Deliverable:**
Complete agent prompt files for both specialists.

#### 1.4.1 DAX Specialist Agent
- [ ] Create `.claude/agents/powerbi-dax-specialist.md`
- [ ] Define focus areas:
  - Time Intelligence patterns (SAMEPERIODLASTYEAR, DATEADD, PARALLELPERIOD)
  - Filter Context awareness (CALCULATE, FILTER, ALL, ALLEXCEPT, KEEPFILTERS)
  - Performance patterns (DIVIDE vs `/`, SUMX vs SUM, iterator vs aggregator)
  - Relationship-aware calculations (RELATED, RELATEDTABLE, USERELATIONSHIP)
- [ ] Define input schema (business logic + state.json model schema)
- [ ] Define output schema (validated DAX expression → findings.md)
- [ ] Define MCP tools available: `measure_operations.create/update`, `dax_query_operations.validate`
- [ ] Include 3-5 example invocations with expected outputs
- [ ] Define validation checkpoint (uses MCP validate before returning)

#### 1.4.2 M-Code Specialist Agent
- [ ] Create `.claude/agents/powerbi-mcode-specialist.md`
- [ ] Define focus areas:
  - ETL patterns (Table.TransformColumns, Table.AddColumn, Table.SelectRows)
  - Query folding optimization (keep operations foldable)
  - Privacy levels (Organizational, Private, Public)
  - Data type enforcement (type text, type number, type date)
  - Error handling (try/otherwise patterns)
- [ ] Define input schema (data source requirements + transformation logic)
- [ ] Define output schema (validated M script → findings.md)
- [ ] Define MCP tools available: `partition_operations`, `named_expression_operations`
- [ ] Include 3-5 example invocations with expected outputs

**Acceptance Criteria:**
- Specialist agents can be invoked by orchestrator
- Specialists produce validated code
- Specialists use MCP for validation

---

### 1.5 State Schema Definition
**Priority:** P1 (High)
**Effort:** 2-3 hours
**Status:** [x] Complete (2025-12-20)

**Current State:**
Complete state schema now documented in SPEC.md Section 7.0.8.2.

**Completed Deliverables:**

- [x] **1.5.1** Define complete schema:
  ```json
  {
    "session": {
      "started": "ISO8601 timestamp",
      "skill_version": "1.0.0",
      "mcp_available": true,
      "connection_type": "desktop|fabric|pbip|file_fallback",
      "connection_status": "connected|disconnected|error",
      "connection_details": {
        "desktop_port": 12345,
        "fabric_workspace": "workspace-id",
        "fabric_dataset": "dataset-id",
        "pbip_path": "/path/to/project"
      }
    },
    "model_schema": {
      "tables": [...],
      "relationships": [...],
      "measures": [...],
      "last_synced": "ISO8601 timestamp"
    },
    "active_tasks": {
      "task-id-123": {
        "path": ".claude/tasks/task-id-123",
        "status": "in_progress|completed|failed",
        "workflow_type": "evaluate|create|implement|analyze|merge",
        "created": "ISO8601 timestamp",
        "updated": "ISO8601 timestamp"
      }
    },
    "resource_locks": {
      "definition/pages/Page1/visual.json": "task-id-123"
    },
    "validation_status": {
      "last_dax_validation": {...},
      "last_pbir_validation": {...},
      "last_tmdl_validation": {...}
    }
  }
  ```

- [x] **1.5.2** Define sync behavior (when does model_schema refresh from MCP?)
  → Documented in SPEC.md Section 7.0.8.7 (Model Schema Caching Strategy)

- [x] **1.5.3** Define lock acquisition/release patterns
  → Documented in SPEC.md Section 7.0.8.6 (Resource Locking Protocol)

- [x] **1.5.4** Define task lifecycle (create → in_progress → completed/failed → archived)
  → Documented in SPEC.md Section 7.0.8.4 (Task Lifecycle)

- [ ] **1.5.5** Update `state_manage.py` to implement full schema
  → TODO: Implementation work, spec complete

**Acceptance Criteria:**
- [x] state.json schema accurately defined
- [x] Model schema sync strategy documented
- [x] Concurrent task handling via locking documented
- [ ] `state_manage.py` implementation (Phase 2 work)

---

### 1.6 PBIR Format Handling
**Priority:** P1 (High)
**Effort:** 2-3 hours
**Status:** [ ] Not started

**Current State:**
SPEC.md acknowledges PBIR gaps but provides no resolution:
- Schema version detection missing
- Enhanced vs Legacy format detection missing
- January 2026 format migration not addressed

**Required Deliverable:**
PBIR handling specification.

- [ ] **1.6.1** Schema version detection logic:
  ```
  Parse visual.json $schema URL
  Extract version (1.0.0, 1.1.0, 1.2.0)
  Map version to feature availability
  ```

- [ ] **1.6.2** Enhanced vs Legacy format detection:
  ```
  Check for .Report/definition/ structure (Enhanced PBIR)
  vs .Report/report.json flat structure (Legacy)
  ```

- [ ] **1.6.3** Version-specific handling rules:
  | Version | Config Blob Format | Interaction Model | Notes |
  |---------|-------------------|-------------------|-------|
  | 1.0.0 | Stringified JSON | Limited | Legacy |
  | 1.1.0 | Stringified JSON | Full | Current |
  | 1.2.0 | TBD | TBD | Jan 2026 |

- [ ] **1.6.4** Migration guidance (how to handle mixed-version projects)

- [ ] **1.6.5** Update visual templates in `.claude/visual-templates/` for all versions

**Acceptance Criteria:**
- Skill correctly detects PBIR format version
- Skill handles all supported versions
- User is warned about unsupported versions

---

### 1.7 Command→Workflow Mapping
**Priority:** P1 (High)
**Effort:** 2-3 hours
**Status:** [ ] Not started

**Current State:**
No explicit mapping from current commands to skill workflows.

**Required Deliverable:**
Complete mapping document.

- [ ] **1.7.1** `/evaluate-pbi-project-file` → Evaluate Workflow
  | Command Phase | Skill Equivalent | Agent Changes |
  |---------------|------------------|---------------|
  | Phase 1: Validation | MCP connection + validation | Replace verify agent with MCP |
  | Phase 2: Clarification | Same (LLM reasoning) | Keep |
  | Phase 3: Scratchpad | Same | Keep |
  | Phase 4: Agent Orchestration | MCP-based + specialists | Major changes |
  | Phase 5: Completion | Same | Keep |

- [ ] **1.7.2** `/create-pbi-artifact` → Create Artifact Workflow
  | Command Phase | Skill Equivalent | Agent Changes |
  |---------------|------------------|---------------|
  | ... | ... | ... |

- [ ] **1.7.3** `/create-pbi-page-specs` → Create Page Workflow

- [ ] **1.7.4** `/implement-deploy-test-pbi-project-file` → Implement Workflow

- [ ] **1.7.5** `/analyze-pbi-dashboard` → Analyze Workflow

- [ ] **1.7.6** `/merge-powerbi-projects` → Merge Workflow

**Acceptance Criteria:**
- Every command phase has a skill equivalent
- Agent changes are documented
- No functionality is lost in migration

---

## Section 2: Structural Improvements

### 2.1 Fallback Mode Specification
**Priority:** P1 (High)
**Effort:** 2-3 hours
**Status:** [ ] Not started

**Current State:**
SPEC.md mentions keeping file-based agents as fallback but provides no specification.

**Required Deliverable:**

- [ ] **2.1.1** Define MCP unavailability detection:
  - MCP tool not in available tools list
  - MCP connection timeout (>30s)
  - MCP returns error response

- [ ] **2.1.2** Define automatic fallback trigger conditions

- [ ] **2.1.3** Define manual fallback override (`--file-mode` equivalent)

- [ ] **2.1.4** Define feature parity table:
  | Feature | MCP Mode | File Fallback Mode |
  |---------|----------|-------------------|
  | Read model schema | Full | Partial (parse TMDL) |
  | Create measure | Live + validated | Write TMDL file |
  | Query data | Full | Requires XMLA separately |
  | Transactions | Full | None |
  | Deploy | Full | pbi-tools CLI |

- [ ] **2.1.5** Define degraded mode UX (what warnings to show user)

- [ ] **2.1.6** Document which agents are used in fallback mode

**Acceptance Criteria:**
- Skill functions (with reduced features) when MCP unavailable
- User is informed of degraded capabilities
- Fallback is seamless (no crashes)

---

### 2.2 Transaction Scope Resolution
**Priority:** P1 (High)
**Effort:** 1-2 hours
**Status:** [ ] Not started

**Current State:**
SPEC.md Question 5 is unresolved:
> Can we batch all changes in one transaction, or per-object?

**Required Deliverable:**

- [ ] **2.2.1** Research MCP transaction_operations capabilities

- [ ] **2.2.2** Define transaction strategy:
  - Option A: Single transaction for all changes in a workflow run
  - Option B: Per-object transactions with manual rollback tracking
  - Option C: Hybrid (group related changes, separate unrelated)

- [ ] **2.2.3** Document decision and rationale

- [ ] **2.2.4** Define rollback behavior on partial failure

- [ ] **2.2.5** Define user confirmation before commit

**Acceptance Criteria:**
- Transaction strategy is decided
- Rollback behavior is defined
- Error recovery path is clear

---

### 2.3 Version Control Integration
**Priority:** P1 (High)
**Effort:** 1-2 hours
**Status:** [ ] Not started

**Current State:**
SPEC.md Question 4 is unresolved:
> Option A: Export TMDL after changes
> Option B: Keep PBIP as source of truth, sync via MCP

**Required Deliverable:**

- [ ] **2.3.1** Evaluate pros/cons of each option

- [ ] **2.3.2** Document decision and rationale

- [ ] **2.3.3** Define TMDL export workflow (if Option A):
  - When to export (after every change? on demand?)
  - Export format (full model? incremental?)
  - Git integration (auto-commit?)

- [ ] **2.3.4** Define sync workflow (if Option B):
  - Conflict detection
  - Merge resolution

- [ ] **2.3.5** Update current "versioned copy" pattern for MCP mode

**Acceptance Criteria:**
- Version control strategy is decided
- Git-friendly workflow is defined
- No data loss scenarios

---

### 2.4 Analytics/Testing Integration
**Priority:** P2 (Medium)
**Effort:** 1-2 hours
**Status:** [ ] Not started

**Current State:**
Current commands end with analytics scripts. Migration path unclear.

**Required Deliverable:**

- [ ] **2.4.1** Define analytics hook integration with skill

- [ ] **2.4.2** Define Playwright testing integration (keep `powerbi-playwright-tester`)

- [ ] **2.4.3** Document token_analyzer.py usage in skill context

- [ ] **2.4.4** Define test result storage (findings.md? separate?)

**Acceptance Criteria:**
- Analytics collection continues to work
- Playwright testing continues to work

---

### 2.5 Authentication Consolidation
**Priority:** P1 (High)
**Effort:** 2-3 hours
**Status:** [ ] Not started

**Current State:**
Current commands have multiple auth paths:
- Device code flow (get_token.py)
- Service principal (pbi-tools)
- PowerShell cmdlets (MicrosoftPowerBIMgmt)

MCP has its own auth model.

**Required Deliverable:**

- [ ] **2.5.1** Document MCP authentication model

- [ ] **2.5.2** Map current auth flows to MCP equivalent:
  | Current | MCP Equivalent | Notes |
  |---------|----------------|-------|
  | Device code | ? | |
  | Service principal | ? | |
  | PowerShell | ? | |

- [ ] **2.5.3** Define unified auth flow for skill

- [ ] **2.5.4** Define credential storage/caching

- [ ] **2.5.5** Define auth error handling

**Acceptance Criteria:**
- Single auth flow for skill
- All current auth scenarios supported
- Auth errors handled gracefully

---

## Section 3: Open Questions Resolution

### 3.1 Question 1: Offline Support
**Priority:** P2 (Medium)
**Status:** [ ] Not decided

> Should we keep file-based agents for offline use (no Desktop/Fabric)?

- [ ] **3.1.1** Document decision (Yes/No)
- [ ] **3.1.2** If Yes, define offline mode trigger
- [ ] **3.1.3** If No, document deprecation plan for file-based agents

---

### 3.2 Question 2: PBIR via MCP
**Priority:** P3 (Low)
**Status:** [ ] Not decided

> Will Microsoft add report support to MCP? If so, when?

- [ ] **3.2.1** Research Microsoft roadmap
- [ ] **3.2.2** Document current limitation
- [ ] **3.2.3** Plan for future PBIR MCP support (when available)

---

### 3.3 Question 3: Skill Distribution
**Priority:** P2 (Medium)
**Status:** [ ] Not decided

> How will we distribute the skill with MCP dependency?

- [ ] **3.3.1** Define distribution mechanism (plugin registry? manual install?)
- [ ] **3.3.2** Define MCP installation prerequisite documentation
- [ ] **3.3.3** Define version compatibility matrix

---

### 3.4 Question 6: Error Recovery
**Priority:** P1 (High)
**Status:** [ ] Not decided

> If MCP fails mid-operation, what's the recovery path?

- [ ] **3.4.1** Define failure detection
- [ ] **3.4.2** Define automatic retry policy
- [ ] **3.4.3** Define manual recovery guidance
- [ ] **3.4.4** Define state cleanup on failure

---

## Section 4: Implementation Checklist

Once all gaps are addressed, use this checklist for implementation:

### Phase 1: Cleanup & Preparation
- [ ] Delete `.claude/agents/powerbi-code-fix-identifier.md`
- [ ] Delete `.claude/agents/power-bi-visual-edit-planner.md` (if exists with hyphen variant)
- [ ] Update README.md to remove references
- [ ] Verify no commands reference deprecated agents

### Phase 2: Core MCP Integration
- [ ] Create `.claude/helpers/mcp-connection.md`
- [ ] Create MCP-based verification (replace powerbi-verify-pbiproject-folder-setup)
- [ ] Create MCP-based schema extraction (replace powerbi-data-model-analyzer)
- [ ] Create MCP-based data context (replace powerbi-data-context-agent)
- [ ] Create MCP-based code locator (replace powerbi-code-locator)

### Phase 2.5: Specialist Agents
- [ ] Create `.claude/agents/powerbi-dax-specialist.md`
- [ ] Create `.claude/agents/powerbi-mcode-specialist.md`
- [ ] Refactor `.claude/agents/powerbi-artifact-designer.md` as Orchestrator

### Phase 3: Implementation Layer
- [ ] Create transaction-based implementation pattern
- [ ] Remove powerbi-tmdl-syntax-validator (MCP validates implicitly)
- [ ] Enhance powerbi-dax-review-agent with MCP validation

### Phase 4: Merge Workflow
- [ ] Enhance powerbi-compare-project-code with MCP
- [ ] Replace powerbi-code-merger with MCP transactions

### Phase 5: Pattern Discovery
- [ ] Enhance powerbi-pattern-discovery with MCP

### Phase 6: Skill Assembly
- [ ] Write complete skill.md
- [ ] Test skill invocation
- [ ] Verify all workflows work

### Phase 7: Command Migration
- [ ] Update /evaluate-pbi-project-file to use skill
- [ ] Update /create-pbi-artifact to use skill
- [ ] Update /create-pbi-page-specs to use skill
- [ ] Update /implement-deploy-test-pbi-project-file to use skill
- [ ] Update /analyze-pbi-dashboard to use skill
- [ ] Update /merge-powerbi-projects to use skill

### Phase 8: Cleanup
- [ ] Delete replaced agent files
- [ ] Delete Python TMDL parsing scripts (if not needed for PBIR)
- [ ] Delete Python XMLA scripts
- [ ] Update documentation

---

## Appendix A: File Inventory

### Files to Create
| File | Purpose | Spec Section |
|------|---------|--------------|
| `.claude/skills/powerbi-analyst/skill.md` | Main skill prompt | 1.1 |
| `.claude/agents/powerbi-dax-specialist.md` | DAX specialist agent | 1.4.1 |
| `.claude/agents/powerbi-mcode-specialist.md` | M-Code specialist agent | 1.4.2 |
| `.claude/helpers/mcp-connection.md` | MCP connection patterns | 1.3 |

### Files to Update
| File | Changes | Spec Section |
|------|---------|--------------|
| `specs/migrate_to_skill_and_pbi_mcp/skill.md` | Complete rewrite | 1.1 |
| `specs/migrate_to_skill_and_pbi_mcp/state_manage.py` | Implement full schema | 1.5.5 |
| `.claude/agents/powerbi-artifact-designer.md` | Refactor as Orchestrator | SPEC 2.5.3 |

### Files to Delete
| File | Reason | Spec Section |
|------|--------|--------------|
| `.claude/agents/powerbi-code-fix-identifier.md` | Deprecated | SPEC 1.1 |
| `.claude/agents/power-bi-visual-edit-planner.md` | Deprecated | SPEC 1.1 |

---

## Appendix B: Dependencies

### External Dependencies
| Dependency | Required For | Installation |
|------------|--------------|--------------|
| Power BI Modeling MCP | Core functionality | [GitHub](https://github.com/microsoft/powerbi-modeling-mcp) |
| Playwright MCP | Testing | Already configured |
| Python 3.x | PBIR editing, utilities | Already installed |

### Removed Dependencies (After Migration)
| Dependency | Replaced By |
|------------|-------------|
| pbi-tools CLI | MCP database_operations |
| Python XMLA scripts | MCP dax_query_operations |
| Python TMDL parsers | MCP table/column/measure_operations |

---

## Appendix C: Success Criteria

### Functional
- [ ] All 6 command workflows work with skill
- [ ] Can connect to Power BI Desktop
- [ ] Can connect to Fabric workspace
- [ ] Can connect to PBIP folder
- [ ] Transactions rollback on failure
- [ ] Deployment works via MCP
- [ ] PBIR agents work unchanged
- [ ] Fallback mode works when MCP unavailable

### Quality
- [ ] Agent count reduced from 27 to ~18
- [ ] No pbi-tools dependency for semantic model ops
- [ ] Python dependencies reduced
- [ ] Error messages are clear and actionable

### Documentation
- [ ] README updated with skill architecture
- [ ] Skill documentation complete
- [ ] Troubleshooting guide updated
- [ ] Breaking changes documented

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2025-12-20 | Claude (analysis) | Initial readiness analysis |
