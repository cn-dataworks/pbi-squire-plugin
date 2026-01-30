# Redundant File Cleanup Plan

## Problem Statement

The plugin has significant file sprawl with duplicate and potentially obsolete files:

1. **Duplicate Agent Directories** - Agents exist in two places
2. **Duplicate Reference Files** - Same content with different filenames
3. **Obsolete Reference Files** - Replaced by newer documents

---

## Issue 1: Duplicate Agent Directories

### Current State
```
agents/analyst/           (23 files) ← AUTHORITATIVE (plugin.json uses this)
agents/developer/            (3 files)  ← AUTHORITATIVE (plugin.json uses this)
skills/pbi-squire/agents/  (22 .md files + 1 nul) ← STALE COPIES (not registered)
```

The `plugin.json` references `agents/analyst/` and `agents/developer/`, making `skills/pbi-squire/agents/` **orphaned/obsolete**.

### Analysis (2025-01-29)

Compared multiple agents in both locations:

#### Agent 1: `powerbi-dax-specialist.md`

| Aspect | `agents/analyst/` (7.2KB) | `skills/.../agents/` (10.6KB) |
|--------|------------------------|-------------------------------|
| Format | Clean YAML frontmatter with `tools:` and `skills:` | Verbose YAML with `thinking:` config |
| Structure | Step-based workflow (5 steps) | Same steps but more prose |
| Content | Lean, production-ready | Older, verbose drafts |

#### Agent 2: `powerbi-code-understander.md`

| Aspect | `agents/analyst/` (4.2KB) | `skills/.../agents/` (8.8KB) |
|--------|------------------------|-------------------------------|
| Purpose | Explain DAX/M code in business language | Same purpose but different scope |
| Format | Clean YAML with `tools:` list | No YAML frontmatter (markdown only) |
| Focus | General code explanation | Merge workflow business impact analysis |
| Output | Business explanation to findings.md | JSON with `business_impact` field |

**Note:** These agents have **diverged in purpose**. The `agents/analyst/` version is a general code explainer, while `skills/.../agents/` version is specialized for merge workflow business impact. The core version is the registered, authoritative one.

#### Agent 3: `powerbi-visual-locator.md`

| Aspect | `agents/analyst/` (8.1KB) | `skills/.../agents/` (8.5KB) |
|--------|------------------------|-------------------------------|
| Format | Clean YAML with `tools:` and `skills:` | Verbose YAML with `thinking:` and examples |
| Workflow | Mandatory 4-step workflow | Same 3-step workflow with more prose |
| Error handling | Detailed error templates | Same error templates |
| Tracing | Included | Not included |

#### Agent 4: `powerbi-pattern-discovery.md`

| Aspect | `agents/analyst/` (9.3KB) | `skills/.../agents/` (13.5KB) |
|--------|------------------------|-------------------------------|
| Format | Clean YAML with `tools:` and `skills:` | Verbose YAML with `thinking:` and examples |
| MCP support | Not mentioned | Detailed MCP mode instructions |
| Tool fallback | Not mentioned | Tool-first pattern with Claude-native fallback |
| Output section | Section 1.D | Section 1.3 (different numbering) |

**Note:** The `skills/.../agents/` version has more detailed MCP and tool-fallback patterns, but uses outdated section numbering. The core version is simpler but aligned with current workflow.

#### Summary Table

| Agent | `agents/analyst/` | `skills/.../agents/` | Verdict |
|-------|----------------|----------------------|---------|
| powerbi-dax-specialist | 7.2KB, lean | 10.6KB, verbose | Core is authoritative |
| powerbi-code-understander | 4.2KB, general | 8.8KB, merge-specific | Core is authoritative (different purpose) |
| powerbi-visual-locator | 8.1KB, with tracing | 8.5KB, no tracing | Core is authoritative |
| powerbi-pattern-discovery | 9.3KB, simple | 13.5KB, MCP details | Core is authoritative |

**Conclusion:** The `agents/analyst/` versions are consistently:
- Leaner and more focused
- Use clean YAML frontmatter with `tools:` and `skills:` arrays
- Include tracing output patterns
- Aligned with current workflow section numbering
- Registered in `plugin.json`

The `skills/pbi-squire/agents/` folder contains older, verbose drafts that:
- Often include `thinking:` configuration (not used in production)
- Have outdated section numbering
- Are NOT registered in `plugin.json`
- In some cases have diverged in purpose

### Recommendation
**DELETE** the entire `skills/pbi-squire/agents/` directory.

**Files to delete:**
- `skills/pbi-squire/agents/*.md` (22 files)
- `skills/pbi-squire/agents/nul` (empty artifact file)

---

## Issue 2: Duplicate Reference Files

### Current State
```
references/anonymization_patterns.md  (16,600 bytes, older)
references/anonymization-patterns.md  (17,375 bytes, newer)
```

Two files with same purpose, different naming conventions.

### Recommendation
**DELETE** `anonymization_patterns.md` (underscore version, older).
**KEEP** `anonymization-patterns.md` (hyphen version, newer).

---

## Issue 3: Obsolete Reference Files

### Files Replaced by orchestration-pattern.md

| File | Status | Reason |
|------|--------|--------|
| `multi-step-workflows.md` | **DELETE** | Replaced by `orchestration-pattern.md` |
| `workflow-decision-tree.md` | **DELETE** | Replaced by `orchestration-pattern.md` |

These files documented the old orchestrator-based architecture which has been replaced by main-thread orchestration.

### Analysis (2025-01-29)

Compared content coverage:

| Feature | `multi-step-workflows.md` | `workflow-decision-tree.md` | `orchestration-pattern.md` |
|---------|---------------------------|----------------------------|---------------------------|
| Workflow sequences | ✅ Detailed (4 workflows) | ❌ No | ✅ Phase-based execution |
| Decision tree | ❌ No | ✅ Full tree | ✅ Full decision tree with triggers |
| User intents mapping | ❌ No | ✅ Detailed | ✅ Quick classification table |
| Subagent invocation | ❌ No | ❌ No | ✅ Full pattern with prompts |
| Quality gates | ❌ No | ❌ No | ✅ Detailed gate checks |
| Error handling | ⚠️ Troubleshooting section | ❌ No | ✅ Comprehensive |
| findings.md template | ❌ No | ❌ No | ✅ Full template |
| Tracing output | ❌ No | ❌ No | ✅ Full example |

**Conclusion:** `orchestration-pattern.md` consolidates BOTH old files into a single, more comprehensive document with significant new content (subagent invocation patterns, quality gates, error handling, tracing).

**Note:** `multi-step-workflows.md` contains "Workflow Execution Time Estimates" (lines 391-427) which are NOT in `orchestration-pattern.md`. Consider migrating this content to a user-facing doc like `getting-started.md` before deletion.

---

## Issue 4: Workflows Assessment

### Current State (10 workflows)

| Workflow | Size | Status |
|----------|------|--------|
| `evaluate-pbi-project-file.md` | 48KB | CORE - referenced in SKILL.md |
| `create-pbi-artifact-spec.md` | 26KB | CORE - referenced in SKILL.md |
| `implement-deploy-test-pbi-project-file.md` | 25KB | CORE - referenced in SKILL.md |
| `merge-powerbi-projects.md` | 14KB | CORE - referenced in SKILL.md |
| `setup-data-anonymization.md` | 20KB | CORE - referenced in SKILL.md |
| `summarize-pbi-dashboard.md` | 19KB | CORE - referenced in SKILL.md |
| `create-pbi-page-specs.md` | 27KB | CORE - referenced in SKILL.md |
| `harvest-templates.md` | 3KB | PRO - documented in developer-features.md |
| `qa-loop-pbi-dashboard.md` | 16KB | PRO - documented in developer-features.md |
| `review-ux-pbi-dashboard.md` | 16KB | PRO - documented in developer-features.md |

### Recommendation
**KEEP ALL 10 WORKFLOWS** - They all serve documented purposes (7 Core + 3 Pro).

---

## Issue 5: Reference Files Audit

### Summary

| Status | Count | Files |
|--------|-------|-------|
| DELETE | 3 | `anonymization_patterns.md`, `multi-step-workflows.md`, `workflow-decision-tree.md` |
| KEEP | 2 | `best-practices.md`, `command-parameters.md` |
| KEEP | 19 | All others |

### Files Reviewed (2025-01-29)

#### `best-practices.md` (581 lines) - **KEEP**

**Content:**
- Command selection guidance
- Path and file management
- Data sampling best practices
- Problem description guidance
- Workflow execution checkpoints
- Testing and deployment best practices
- Page design best practices
- Performance and collaboration tips

**Verdict:** Valuable operational reference that consolidates best practices across all workflows. Minor overlap with other docs but provides unique "dos and don'ts" guidance.

#### `command-parameters.md` (264 lines) - **KEEP**

**Content:**
- Detailed parameter documentation for each command
- Required vs optional parameters
- Example values and full command examples
- Path formatting tips

**Verdict:** Authoritative parameter reference. `SKILL.md` has command triggers but not parameter semantics. This is the only place with detailed parameter documentation.

---

## Cleanup Actions

### Phase 1: Delete Obsolete Agents Folder
```bash
rm -rf skills/pbi-squire/agents/
```
**Impact**: Removes 22 obsolete agent files + 1 empty `nul` file (stale copies)

### Phase 2: Delete Duplicate/Obsolete References
```bash
rm skills/pbi-squire/references/anonymization_patterns.md
rm skills/pbi-squire/references/multi-step-workflows.md
rm skills/pbi-squire/references/workflow-decision-tree.md
```
**Impact**: Removes 3 obsolete reference files

### Phase 3: ~~Review Questionable References~~ COMPLETED

**Review completed 2025-01-29:**
- `best-practices.md` - **KEEP** - Valuable operational reference
- `command-parameters.md` - **KEEP** - Authoritative parameter documentation

### Optional: Migrate Time Estimates

Before deleting `multi-step-workflows.md`, consider migrating "Workflow Execution Time Estimates" (lines 391-427) to `resources/getting-started.md` or similar user-facing doc.

---

## Before/After Comparison

### Before
```
skills/pbi-squire/
├── agents/          (23 files - OBSOLETE)
├── references/      (24 files - some duplicates)
├── resources/       (12 files)
├── workflows/       (10 files)
└── assets/          (1 file)
```

### After
```
skills/pbi-squire/
├── references/      (21 files - no duplicates, best-practices + command-parameters KEPT)
├── resources/       (12 files - unchanged)
├── workflows/       (10 files - unchanged)
└── assets/          (1 file - unchanged)
```

**Removed**: 26 obsolete files (23 agents + 3 references)

---

## Verification

After cleanup:
1. Run `/plugin list` - verify plugin still loads
2. Search for broken references to deleted files
3. Run a test workflow to verify nothing broke

---

## Appendix: Full Agent Comparison Analysis

**Analysis performed:** 2025-01-29

This appendix contains the detailed file-by-file comparison of agents in `agents/analyst/` vs `skills/pbi-squire/agents/`.

### Methodology

For each agent, compared:
- File size (KB)
- YAML frontmatter format
- Workflow structure
- Content focus and purpose
- Tracing output inclusion
- Section numbering alignment

### Detailed Comparisons

#### `powerbi-dax-specialist.md`

**`agents/analyst/` version (7.2KB):**
```yaml
---
name: powerbi-dax-specialist
description: Generate validated, production-ready DAX code...
model: sonnet
tools: [Read, Write, Edit, Glob, Grep]
skills: [pbi-squire]
color: cyan
---
```
- Clean 5-step mandatory workflow
- Writes to Section 2.A
- Includes tracing output template
- Quality checklist at end

**`skills/.../agents/` version (10.6KB):**
```yaml
---
name: powerbi-dax-specialist
description: [Long description with examples...]
model: sonnet
thinking:
  budget_tokens: 16000
color: cyan
---
```
- Verbose description with inline examples
- Uses `thinking:` config (not used in production)
- Missing `tools:` and `skills:` arrays
- Same workflow but more prose

**Verdict:** Core version is authoritative. Skills version is an older draft.

---

#### `powerbi-code-understander.md`

**`agents/analyst/` version (4.2KB):**
```yaml
---
name: powerbi-code-understander
description: Explain DAX measures and M code in plain business language...
model: sonnet
tools: [Read, Write, Edit, Glob, Grep]
skills: [pbi-squire]
color: teal
---
```
- Purpose: General code explanation
- Output: Business explanation to findings.md
- Includes tracing output
- 3-step workflow (Identify → Parse → Generate)

**`skills/.../agents/` version (8.8KB):**
```
# powerbi-code-understander

**Role:** Business Analyst - LLM specialist...
```
- No YAML frontmatter (markdown only)
- Purpose: Merge workflow business impact analysis
- Output: JSON with `business_impact` field
- Receives JSON from `powerbi-compare-project-code`
- Specialized for `/merge-powerbi-projects` command

**Verdict:** These agents have **diverged in purpose**. Core is general; skills version is merge-specific. Core is registered and authoritative.

---

#### `powerbi-visual-locator.md`

**`agents/analyst/` version (8.1KB):**
```yaml
---
name: powerbi-visual-locator
description: Locate and document PBIR visuals...
model: sonnet
tools: [Read, Glob, Grep, Write, Edit]
skills: [pbi-squire]
color: purple
---
```
- 4-step mandatory workflow
- Writes to Section 1.B
- Detailed error handling templates
- Includes tracing output
- Search strategies documented

**`skills/.../agents/` version (8.5KB):**
```yaml
---
name: powerbi-visual-locator
description: [Long description with examples...]
model: sonnet
thinking:
  budget_tokens: 16000
color: purple
---
```
- 3-step workflow (same content, different organization)
- Uses `thinking:` config
- Includes example scenarios in description
- No tracing output section

**Verdict:** Core version is authoritative. Has tracing, cleaner structure.

---

#### `powerbi-pattern-discovery.md`

**`agents/analyst/` version (9.3KB):**
```yaml
---
name: powerbi-pattern-discovery
description: Find existing similar artifacts and extract patterns...
model: sonnet
tools: [Read, Glob, Grep, Write, Edit]
skills: [pbi-squire]
color: yellow
---
```
- 6-step workflow
- Writes to Section 1.D
- Focused on pattern extraction
- Includes tracing output

**`skills/.../agents/` version (13.5KB):**
```yaml
---
name: powerbi-pattern-discovery
description: [Long description with examples...]
model: sonnet
thinking:
  budget_tokens: 12000
color: yellow
---
```
- 6-step workflow with MCP mode details
- Writes to Section 1.3 (outdated numbering)
- Detailed MCP vs fallback mode instructions
- Tool-first pattern with Claude-native fallback
- More comprehensive but uses outdated section references

**Verdict:** Core version is authoritative. Skills version has useful MCP details but outdated section numbering.

---

### Files Only in `skills/pbi-squire/agents/`

These files exist in the skills folder but have no counterpart in `agents/analyst/`:

| File | Size | Notes |
|------|------|-------|
| `powerbi-page-question-analyzer.md` | 22KB | May be obsolete or merged into another agent |
| `nul` | 0 bytes | Empty artifact file (Windows `nul` device) |

### Files Only in `agents/analyst/`

These files exist in `agents/analyst/` but have no counterpart in skills folder:

| File | Notes |
|------|-------|
| `powerbi-code-implementer-apply.md` | New agent for code implementation |
| `powerbi-code-locator.md` | New agent for code location |
| `powerbi-dashboard-documenter.md` | New agent for dashboard documentation |
| `powerbi-data-context-agent.md` | New agent for data context |
| `powerbi-anonymization-setup.md` | New agent for anonymization |

### Conclusion

The `agents/analyst/` directory contains the **authoritative, production-ready** versions of all agents. The `skills/pbi-squire/agents/` directory contains:

1. **Older drafts** - More verbose, using deprecated `thinking:` config
2. **Diverged versions** - Some agents evolved in different directions
3. **Outdated references** - Using old section numbering (1.3 vs 1.D)
4. **Orphaned files** - Not registered in `plugin.json`

**Recommendation confirmed:** DELETE the entire `skills/pbi-squire/agents/` directory.
