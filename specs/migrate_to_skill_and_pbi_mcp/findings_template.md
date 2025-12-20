# Task Blackboard: [TASK_NAME]
**Status:** 🟡 In-Progress | 🟢 Complete | 🔴 Failed
**Task ID:** [TASK_ID]
**Workflow:** [evaluate|create|implement|analyze|merge]

---

## Section 1: Requirements (Orchestrator)
*Written by: powerbi-artifact-designer (Orchestrator)*

- **Goal:** [User intent in business terms]
- **Project Path:** [Full path to .pbip or .SemanticModel folder]
- **Artifacts Needed:**
  - [ ] Measure: [Name] → DAX Specialist
  - [ ] Partition: [Name] → M-Code Specialist
  - [ ] Visual: [Type/Location] → Orchestrator (PBIR)

---

## Section 2: DAX Logic (DAX Specialist)
*Written by: powerbi-dax-specialist*

- **Measures Created:**
  | Measure Name | DAX Formula | Table | Format |
  |--------------|-------------|-------|--------|
  | [Name] | `DIVIDE(SUM(...), ...)` | [Table] | [0.0%] |

- **Calculated Columns Created:**
  | Column Name | DAX Formula | Table |
  |-------------|-------------|-------|
  | [Name] | `RELATED(...)` | [Table] |

- **Validation:** ✅ Passed via MCP `dax_query_operations.validate()` | ⚠️ LLM-only (fallback)
- **Dependencies:** [List of referenced measures/columns]
- **Notes:** [Time intelligence patterns used, filter context considerations, etc.]

---

## Section 3: M-Code Logic (M-Code Specialist)
*Written by: powerbi-mcode-specialist*

- **Partitions Created/Modified:**
  | Table | Partition | M Expression |
  |-------|-----------|--------------|
  | [Table] | [Partition] | `let Source = ... in FinalTable` |

- **Named Expressions:**
  | Name | M Expression | Purpose |
  |------|--------------|---------|
  | [Name] | `...` | [Shared parameter, etc.] |

- **Query Folding:** ✅ Folds to source | ⚠️ Breaks at step [X]
- **Privacy Level:** Organizational | Private | Public
- **Notes:** [ETL considerations, data type enforcement, etc.]

---

## Section 4: Implementation (Orchestrator)
*Written by: powerbi-artifact-designer after specialist sections complete*

### 4.A TMDL Changes (Semantic Model)
| File | Operation | Object | Details |
|------|-----------|--------|---------|
| `definition/tables/Sales.tmdl` | CREATE | measure [YoY Growth] | Line XX |
| `definition/tables/Sales.tmdl` | MODIFY | measure [Total Sales] | Line XX |

### 4.B PBIR Changes (Report)
| File | Operation | Details |
|------|-----------|---------|
| `definition/pages/Overview/visuals/card1.json` | UPDATE | dataBindings |
| `definition/pages/Overview/page.json` | UPDATE | layout coordinates |

### 4.C MCP Operations (if MCP mode)
| Operation | Target | Status |
|-----------|--------|--------|
| `measure_operations.create()` | [YoY Growth] | ⏳ Pending |
| `measure_operations.update()` | [Total Sales] | ⏳ Pending |

---

## Section 5: Validation Results
*Written by: Validation agents after implementation*

| Validator | Result | Details |
|-----------|--------|---------|
| DAX Review (`powerbi-dax-review-agent`) | ✅ Passed | [notes] |
| PBIR Validation (`powerbi-pbir-validator`) | ✅ Passed | [notes] |
| TMDL Syntax (`powerbi-tmdl-syntax-validator`) | ✅ Passed | [notes] |

**Blocking Issues:** None | [List critical errors]

**Warnings (non-blocking):**
- [Warning 1]
- [Warning 2]

---

## Section 6: Final Manifest
*Moved to state.json `archived_tasks` on completion*

- **Summary:** [2-sentence summary of what changed and why]
- **Artifacts Created:** [List of new measures/columns/visuals]
- **Artifacts Modified:** [List of changed objects]
- **Test Results:** [If Playwright testing was run]

---

## Appendix: Session Context
*Reference information for specialists*

- **MCP Mode:** ✅ Connected | ❌ Fallback (file-based)
- **Connection Type:** Desktop | Fabric | PBIP
- **Model Schema Synced:** [timestamp]
- **Resource Locks Held:**
  - `definition/tables/Sales.tmdl` (this task)
