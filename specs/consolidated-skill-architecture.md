# Consolidated Skill Architecture

## Overview

This document describes the consolidation of four skills into one unified `powerbi-analyst` skill:

| Absorbed Skill | What It Becomes |
|----------------|-----------------|
| `powerbi-dashboard-analyzer` | **SUMMARIZE workflow** (enhanced) |
| `powerbi-data-prep` | **DATA_PREP workflow** (new) + enhanced mcode-specialist agent |
| `power-bi-assistant` | **Orchestrator behavior** + trigger patterns |

## Rationale

1. **User simplicity** - One skill to learn, one entry point
2. **Natural routing** - Claude + orchestrator handle clarification naturally
3. **Content preservation** - Specialized knowledge becomes references/agent enhancements
4. **Reduced confusion** - No "which skill do I use?" decisions

---

## New Skill Structure

```
skills/
└── powerbi-analyst/
    ├── SKILL.md                    # Unified skill definition
    │
    ├── agents/                     # (moved from agents/core/)
    │   ├── powerbi-orchestrator.md      # Enhanced: routing + clarification
    │   ├── powerbi-mcode-specialist.md  # Enhanced: data-prep workflow
    │   ├── powerbi-dax-specialist.md
    │   ├── powerbi-dashboard-documenter.md  # NEW: from dashboard-analyzer
    │   └── ... (other agents)
    │
    ├── workflows/                  # Workflow detail files (optional)
    │   ├── evaluate.md
    │   ├── create-artifact.md
    │   ├── data-prep.md           # NEW: M code workflow
    │   ├── analyze.md             # Enhanced: dashboard analysis
    │   ├── implement.md
    │   └── merge.md
    │
    ├── references/                 # Consolidated references
    │   ├── # From assistant
    │   ├── workflow-decision-tree.md
    │   ├── command-parameters.md
    │   ├── best-practices.md
    │   │
    │   ├── # From dashboard-analyzer
    │   ├── visual-types.md
    │   ├── dax-common-patterns.md
    │   ├── interaction-patterns.md
    │   ├── translation-guidelines.md
    │   │
    │   ├── # From data-prep
    │   ├── m-best-practices.md
    │   ├── query-folding-guide.md
    │   ├── common-transformations.md
    │   ├── tmdl-partition-structure.md
    │   ├── anonymization-patterns.md
    │   │
    │   └── # Existing
    │   └── ... (current references)
    │
    ├── assets/
    │   ├── findings_template.md
    │   ├── analysis_report_template.md  # From dashboard-analyzer
    │   └── visual-templates/
    │
    └── resources/
        ├── getting-started.md
        ├── glossary.md
        └── troubleshooting-faq.md
```

---

## SKILL.md Structure (Revised)

### 1. Header & Description

```yaml
---
name: powerbi-analyst
description: >
  Complete Power BI development assistant. Diagnose issues, create measures/visuals,
  edit M code transformations, analyze dashboards, and deploy changes. Uses Power BI
  Modeling MCP when available for live validation.
---
```

### 2. Quick Start (Replaces Assistant's Routing)

```markdown
## Quick Start

Tell me what you need help with:

| You say... | I'll do... |
|------------|-----------|
| "Fix this measure" / "Something is broken" | **EVALUATE** - diagnose and plan fixes |
| "Create a YoY growth measure" | **CREATE_ARTIFACT** - design new artifacts |
| "Filter this table in Power Query" | **DATA_PREP** - M code transformations |
| "Explain what this dashboard does" | **ANALYZE** - document in business language |
| "Apply the changes" | **IMPLEMENT** - execute the plan |
| "Compare these two projects" | **MERGE** - diff and merge |
| "Help me with Power BI" | I'll ask clarifying questions first |

**Not sure what you need?** Just describe your situation and I'll help figure it out.
```

### 3. Trigger Patterns (Comprehensive)

```markdown
## When to Use This Skill

**File Patterns:**
- `*.pbip`, `*.pbix`, `*.tmdl`, `*.bim`
- `*/.SemanticModel/**`, `*/.Report/**`

**Keyword Triggers:**
- Power BI, PBIX, PBIP, DAX, M code, Power Query
- Semantic model, measure, calculated column, TMDL, PBIR
- Dashboard, report, visual, chart, graph
- ETL, transformation, filter, merge tables
- Query folding, partition, data source
```

### 4. Workflows (8 Total)

| Workflow | Purpose | Primary Agent |
|----------|---------|---------------|
| **EVALUATE** | Fix existing problems | orchestrator → specialists |
| **CREATE_ARTIFACT** | New measures/columns/tables | orchestrator → dax/mcode-specialist |
| **CREATE_PAGE** | New report pages with visuals | orchestrator → page-designer |
| **DATA_PREP** | M code / Power Query transformations | orchestrator → mcode-specialist |
| **ANALYZE** | Document dashboard in business language | orchestrator → dashboard-documenter |
| **IMPLEMENT** | Apply changes from findings.md | orchestrator → implementers |
| **MERGE** | Compare and merge two projects | orchestrator → compare-agent |
| **VERSION_CHECK** | Plugin status and updates | (direct) |

### 5. Orchestrator Behavior (Absorbs Assistant Logic)

```markdown
## Orchestrator: Handling Unclear Requests

When user intent is unclear, the orchestrator MUST ask clarifying questions
before selecting a workflow.

### Clarification Flow

1. **Detect vagueness**: "help with Power BI", "I need assistance", no specific action
2. **Ask targeted questions**:
   - "Are you trying to **fix** something, **create** something new, or **understand** something?"
   - "Is this about **calculations** (DAX/measures) or **data loading** (M code/Power Query)?"
3. **Gather required info**:
   - Project path (if not obvious from context)
   - Specific problem or goal
4. **Confirm before proceeding**:
   - "I'll use the EVALUATE workflow to diagnose this. Sound good?"

### Decision Tree (Internal)

```
User Request
    │
    ├─ Contains "fix", "broken", "wrong", "debug", "issue"
    │  └─► EVALUATE
    │
    ├─ Contains "create", "add", "new measure/column/table/visual"
    │  └─► CREATE_ARTIFACT
    │
    ├─ Contains "M code", "Power Query", "transform", "ETL", "filter table"
    │  └─► DATA_PREP
    │
    ├─ Contains "explain", "understand", "what does this do", "document"
    │  └─► ANALYZE
    │
    ├─ Contains "apply", "implement", "deploy", "execute"
    │  └─► IMPLEMENT
    │
    ├─ Contains "compare", "merge", "diff", "sync projects"
    │  └─► MERGE
    │
    ├─ Contains "version", "update", "edition"
    │  └─► VERSION_CHECK
    │
    └─ Unclear
       └─► ASK CLARIFYING QUESTIONS
```
```

---

## Workflow Details

### DATA_PREP Workflow (New - from powerbi-data-prep)

```markdown
### DATA_PREP (M Code / Power Query)

**Use when:** User wants to modify data transformations, Power Query logic,
table filtering, column operations, or any ETL changes.

**Trigger phrases:**
- "Filter this table to only include..."
- "Add a column that calculates..."
- "Merge these two tables"
- "Change the data source"
- "Optimize this Power Query"

**Process:**
1. **Analyze patterns** - Discover naming conventions, existing transformation styles
2. **Design transformation** - Present simplest approach, alternatives if relevant
3. **Validate query folding** - Warn about performance impacts
4. **Apply M code changes** - Safe TMDL partition editing
5. **Validate syntax** - TMDL format check

**Invokes:** powerbi-mcode-specialist (enhanced)

**Output:** Updated TMDL files + validation results

**Key considerations:**
- Always check query folding before applying
- Follow project naming patterns
- Create backups before editing
```

### ANALYZE Workflow (Enhanced - from powerbi-dashboard-analyzer)

```markdown
### ANALYZE (Document Dashboard)

**Use when:** User wants to understand an existing dashboard, explain metrics
to stakeholders, or create documentation.

**Trigger phrases:**
- "Tell me what this dashboard is doing"
- "Explain how this metric is calculated"
- "Document this report for the business team"
- "What does this page show?"

**Process:**
1. **Validate project** - Ensure .Report folder exists for visual analysis
2. **Extract structure** - Pages, visuals, filters, interactions
3. **Extract measures** - DAX definitions and dependencies
4. **Translate to business language** - Apply translation guidelines
5. **Generate report** - Structured markdown documentation

**Invokes:** powerbi-dashboard-documenter (new agent)

**Output:** `dashboard_analysis.md` with:
- Executive summary
- Page-by-page breakdown
- Metrics glossary (business-friendly)
- Filter & interaction guide

**Translation principles:**
- Focus on "what" and "why", not "how"
- Use business terminology
- Describe visual purpose, not just type
- Include just enough technical detail for credibility
```

---

## Agent Changes

### powerbi-orchestrator.md (Enhanced)

Add to the orchestrator's responsibilities:

```markdown
## Routing & Clarification (from Assistant)

Before spawning workflow-specific agents, the orchestrator MUST:

1. **Classify the request** using the decision tree
2. **If unclear**, ask clarifying questions (max 2-3 questions)
3. **Confirm the selected workflow** with the user
4. **Gather missing parameters** (project path, problem description)

### Clarification Templates

**Intent unclear:**
> I want to help you with your Power BI project. Could you tell me:
> - Are you trying to **fix** something that's not working?
> - Do you want to **create** something new?
> - Do you need to **understand** what a dashboard does?

**Domain unclear:**
> Is this about:
> - **DAX calculations** (measures, calculated columns)?
> - **Power Query / M code** (data transformations, filtering)?
> - **Visuals** (charts, layouts, formatting)?

**Project path missing:**
> What's the path to your Power BI project?
> (Look for a folder containing a `.pbip` file)
```

### powerbi-mcode-specialist.md (Enhanced)

Absorb the detailed workflow from data-prep:

```markdown
## Enhanced M Code Workflow

### Before Writing M Code

1. **Analyze project patterns**
   - Run pattern discovery on existing M code
   - Note naming conventions (PascalCase, snake_case)
   - Identify common transformation styles

2. **Check query folding impact**
   - Will this transformation fold to the source?
   - If not, warn the user about performance implications

3. **Present options**
   - Simplest approach first
   - Alternatives with pros/cons if relevant

### Query Folding Rules

**Preserves folding:** SelectRows, SelectColumns, RenameColumns, Sort, Group, Joins (indexed)

**Breaks folding:** Custom columns with M functions, Text operations, Complex conditionals,
Pivot/unpivot, Merging with non-database sources

### After Writing M Code

1. Validate TMDL syntax
2. Document what changed
3. Suggest testing approach
```

### powerbi-dashboard-documenter.md (New Agent)

Create from dashboard-analyzer content:

```markdown
---
name: powerbi-dashboard-documenter
description: Generate business-friendly documentation for Power BI dashboards.
  Translates technical DAX/TMDL into clear explanations for non-technical stakeholders.
model: sonnet
tools:
  - Read
  - Write
  - Glob
  - Grep
skills:
  - powerbi-analyst
---

## Purpose

Transform technical Power BI content into business-friendly documentation.

## Translation Guidelines

1. **Focus on "what" and "why", not "how"**
   - Good: "Total Sales excluding returns and discounts"
   - Avoid: "SUMX function iterating over filtered table context"

2. **Explain dependencies without overwhelming detail**
   - Good: "Depends on: Total Sales, Prior Year Sales"
   - Avoid: Full nested DAX code blocks

3. **Use business terminology**
   - Good: "Year-over-year comparison"
   - Avoid: "SAMEPERIODLASTYEAR time intelligence function"

4. **Describe visual purpose, not just type**
   - Good: "Line chart tracking monthly revenue trends over time"
   - Avoid: "Line chart with Date on X-axis and Revenue on Y-axis"

## Output Template

See `assets/analysis_report_template.md` for the full structure.
```

---

## Reference Consolidation

### From power-bi-assistant → references/

| File | Content |
|------|---------|
| `workflow-decision-tree.md` | Routing logic (now in orchestrator) |
| `command-parameters.md` | Parameter docs for each workflow |
| `best-practices.md` | General best practices |

### From powerbi-dashboard-analyzer → references/

| File | Content |
|------|---------|
| `visual-types.md` | How to describe each visual type |
| `dax-common-patterns.md` | Business translations of DAX patterns |
| `interaction-patterns.md` | Cross-filtering, drillthrough explanations |
| `translation-guidelines.md` | Technical → business language rules |

### From powerbi-data-prep → references/

| File | Content |
|------|---------|
| `m-best-practices.md` | M code style guide |
| `query-folding-guide.md` | What preserves/breaks folding |
| `common-transformations.md` | M code pattern library |
| `tmdl-partition-structure.md` | Partition formatting rules |
| `anonymization-patterns.md` | Data masking templates |

---

## Plugin.json Update

```json
{
    "name": "powerbi-analyst",
    "version": "1.5.0",
    "description": "Complete Power BI development assistant - diagnose, create, transform, analyze, and deploy",
    "agents": [
        "./skills/powerbi-analyst/agents/powerbi-orchestrator.md",
        "./skills/powerbi-analyst/agents/powerbi-dashboard-documenter.md",
        "./skills/powerbi-analyst/agents/powerbi-mcode-specialist.md",
        // ... all other agents
    ],
    "skills": [
        "./skills/powerbi-analyst"
    ]
}
```

**Note:** Only ONE skill listed now.

---

## Migration Checklist

### Phase 1: Consolidate References
- [ ] Copy references from dashboard-analyzer to powerbi-analyst/references/
- [ ] Copy references from data-prep to powerbi-analyst/references/
- [ ] Copy references from assistant to powerbi-analyst/references/
- [ ] Update any internal links

### Phase 2: Create/Enhance Agents
- [ ] Create `powerbi-dashboard-documenter.md` agent
- [ ] Enhance `powerbi-orchestrator.md` with routing logic
- [ ] Enhance `powerbi-mcode-specialist.md` with data-prep workflow

### Phase 3: Update SKILL.md
- [ ] Add DATA_PREP workflow section
- [ ] Enhance SUMMARIZE workflow section
- [ ] Add Quick Start section (routing)
- [ ] Add orchestrator behavior section
- [ ] Update trigger patterns

### Phase 4: Update Plugin Manifest
- [ ] Remove other skills from plugin.json
- [ ] Update description
- [ ] Bump version to 1.5.0

### Phase 5: Deprecate Old Skills
- [ ] Add deprecation notice to old skill folders
- [ ] Update .gitignore to exclude old skills
- [ ] Update documentation (README, INSTALL)

### Phase 6: Test
- [ ] Test EVALUATE workflow
- [ ] Test CREATE_ARTIFACT workflow
- [ ] Test DATA_PREP workflow (new)
- [ ] Test SUMMARIZE workflow (enhanced)
- [ ] Test unclear request → clarification flow
- [ ] Test PBIX detection still works

---

## User Experience Comparison

### Before (4 Skills)

```
User: "Help me with Power BI"
Claude: Which skill? powerbi-analyst? power-bi-assistant? powerbi-dashboard-analyzer?

User: "I want to filter a table"
Claude: Is this powerbi-data-prep or powerbi-analyst?

User: "Explain this dashboard"
Claude: Should I use powerbi-analyst ANALYZE or powerbi-dashboard-analyzer?
```

### After (1 Skill)

```
User: "Help me with Power BI"
Claude (orchestrator): "I can help! Are you trying to fix something, create something,
                        or understand something?"

User: "I want to filter a table"
Claude: → DATA_PREP workflow (automatic routing)

User: "Explain this dashboard"
Claude: → SUMMARIZE workflow (automatic routing)
```

---

## Benefits Summary

| Aspect | Before | After |
|--------|--------|-------|
| Skills to learn | 4 | 1 |
| Routing decisions | User must choose | Automatic + clarification |
| M code workflow | Separate skill | Integrated workflow |
| Dashboard analysis | Separate skill | Integrated workflow |
| Reference location | Scattered | Consolidated |
| Plugin.json | 4 skills | 1 skill |
| Trigger confusion | High | None |

---

## Open Questions

1. **Agent location:** Should agents move to `skills/powerbi-analyst/agents/` or stay in `agents/core/`?
   - Recommendation: Keep in `agents/core/` for now, reference from skill

2. **Workflow files:** Should each workflow have its own file in `workflows/`?
   - Recommendation: Keep workflow details in SKILL.md for simplicity, extract to files if SKILL.md gets too long

3. **Deprecation period:** How long to keep old skill folders before deletion?
   - Recommendation: Mark deprecated immediately, delete in next major version
