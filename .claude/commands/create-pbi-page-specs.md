---
name: create-pbi-page-specs
description: Create comprehensive specifications for a Power BI dashboard page (measures, visuals, layout, interactions) through intelligent analysis and design—ready for implementation via /implement-deploy-test-pbi-project-file
pattern: ^/create-pbi-page-specs\s+(.+)$
---

# Create Power BI Page Specifications

This slash command creates comprehensive specifications for a complete Power BI dashboard page by:
1. Analyzing the business question to determine page requirements
2. Identifying measures and visuals needed with dependencies
3. Designing optimal layout using research-based positioning
4. Creating cross-filtering and interaction patterns
5. Generating complete PBIR page files ready for implementation

**CRITICAL:** This command creates SPECIFICATIONS only. It does NOT modify any project files. Use `/implement-deploy-test-pbi-project-file` to apply changes.

## Usage

```bash
/create-pbi-page-specs --project <path-to-pbip-folder> \
                       --question "<business question to answer>" \
                       [--workspace <workspace-name>] \
                       [--dataset <dataset-name>] \
                       [--page-name "<custom page name>"]
```

### Parameters

- `--project` (required): Path to the Power BI Project folder (the folder containing .pbip file structure with .Report folder)
- `--question` (required): Business question this page should answer
  - Example: "Show Q4 sales performance by region and product category"
  - Example: "Compare year-over-year revenue growth across sales territories"
- `--workspace` (optional): Power BI workspace name for XMLA data sampling. If provided, enables data context retrieval for better recommendations
- `--dataset` (optional): Power BI dataset/semantic model name for XMLA data sampling. Required if `--workspace` is provided
- `--page-name` (optional): Custom name for the page (auto-generated from question if omitted)

### Examples

```bash
# Basic usage without data sampling
/create-pbi-page-specs --project "C:\Projects\SalesReport" \
  --question "Show Q4 sales performance by region and product category"

# With data sampling for better recommendations
/create-pbi-page-specs --project "./MyReport" \
  --question "Compare YoY revenue growth across territories" \
  --workspace "Sales Analytics" \
  --dataset "Sales Report Model"

# With custom page name
/create-pbi-page-specs --project "C:\Reports\Dashboard" \
  --question "Executive KPI summary with top products" \
  --page-name "Executive Summary"
```

## Workflow Overview

### Agents Involved

1. `powerbi-verify-pbiproject-folder-setup` - Validate project format and .Report folder
2. `powerbi-page-question-analyzer` - Analyze business question for page requirements
3. `powerbi-data-model-analyzer` - Extract data model schema
4. `powerbi-artifact-decomposer` - Break down page into measures + visuals + interactions (page mode)
5. `powerbi-data-understanding-agent` - Specify measures (measure mode) and visuals (visual mode)
6. `powerbi-pattern-discovery` - Find existing patterns for measures
7. `powerbi-artifact-designer` - Generate DAX code for measures
8. `powerbi-visual-type-recommender` - Recommend visual types with pros/cons
9. `powerbi-page-layout-designer` - Generate optimal coordinates and layout
10. `powerbi-interaction-designer` - Design cross-filtering and drill-through
11. `powerbi-pbir-page-generator` - Generate complete PBIR page files
12. `power-bi-verification` - Validate DAX measures
13. `powerbi-pbir-validator` - Validate PBIR files

### Execution Pattern

**Hybrid:** Sequential phases with parallel measure + visual specification branches

```
Phases 1-4: Sequential (validation → question analysis → schema → decomposition)
   ↓
Phase 5: PARALLEL BRANCHES
   ├─ Branch A: Measure specifications (per measure)
   └─ Branch B: Visual specifications (per visual)
   ↓
Phases 6-11: Sequential (layout → interactions → PBIR generation → validation → summary)
```

### Coordination File

`agent_scratchpads/[timestamp]-[page-name]/findings.md`

---

## Phase 1: Prerequisites & Project Validation

**Purpose:** Validate that the project is in correct format (.pbip with .Report folder)

**Execute:** `powerbi-verify-pbiproject-folder-setup` agent

**Input:**
- Project path from --project parameter
- Visual changes expected: `true` (page creation requires .Report folder)

**Actions:**
1. Check project format (must be .pbip with .Report folder)
2. Reject pbi-tools or PBIX-only formats
3. Document validated project path

**Output:** Prerequisites section with validation status

**Error Handling:**
- **No .Report folder:** Display clear error message that page creation requires native .pbip format with .Report folder
- **PBIX file:** Prompt user to convert to .pbip format in Power BI Desktop (File → Save As → Power BI Project)

---

## Phase 2: Scratchpad Creation

**Purpose:** Create workspace for specifications

**Actions:**
1. Generate timestamp: `YYYYMMDD-HHMMSS` format
2. Create distilled page name from question:
   - Extract key terms from question
   - Convert to kebab-case
   - Limit to ~30-40 chars
   - Example: "q4-sales-by-region"
3. Create folder: `agent_scratchpads/[timestamp]-[distilled-name]/`
4. Create findings file: `agent_scratchpads/[timestamp]-[distilled-name]/findings.md`
5. Populate findings file with:
   - **Original Command** section with full command-line prompt
   - Business question
   - Power BI project path information
   - Empty sections 1.0-8 ready for agent population

---

## Phase 3: Question Analysis & Page Planning

**Purpose:** Understand what the page needs to accomplish

**Execute:** `powerbi-page-question-analyzer` agent

**Input:**
- Business question from --question parameter
- Findings file path

**Agent Actions:**
1. Classify question type (comparison, trend, composition, performance tracking, relationship)
2. Identify analytical components:
   - Metrics needed (what to measure)
   - Dimensions needed (how to slice)
   - Time context (fiscal periods, comparisons)
   - Analytical intent (identify winners, spot trends, find outliers)
3. Determine page structure:
   - Summary-level visuals (KPI cards)
   - Detail-level visuals (charts, tables, matrices)
   - Filtering needs (slicers, page-level filters)

**Output:** Populates Section 1.0 (Question Analysis & Page Planning)

**Success Criteria:**
- Question type clearly classified
- All analytical components identified
- Page structure defined

---

## Phase 4: Data Model Schema Analysis

**Purpose:** Extract existing data model structure

**Execute:** `powerbi-data-model-analyzer` agent

**Input:**
- Validated project path from Phase 1
- Findings file path

**Agent Actions:**
1. Scan `.SemanticModel/definition/tables/*.tmdl` files
2. Extract table definitions: names, columns, data types
3. Parse `model.tmdl` for relationships and cardinality
4. Identify fact vs dimension tables
5. Document existing measures

**Output:** Populates Section 1.1 (Data Model Schema)

**Success Criteria:**
- Complete schema documented
- Relationships mapped
- Existing measures cataloged

---

## Phase 5: Artifact Decomposition & User Confirmation

**Purpose:** Break down page requirements into discrete artifacts

**Execute:** `powerbi-artifact-decomposer` agent (in page mode)

**Input:**
- Findings file path (with Sections 1.0 and 1.1 completed)
- Mode: `page` (vs default `single-artifact`)

**Agent Actions:**
1. Identify ALL artifacts needed:
   - **Measures:** NEW measures to create vs EXISTING to reference
   - **Visuals:** Cards, charts, tables, slicers
   - **Page-level filters:** Date filters, dimension filters
   - **Interactions:** Cross-filtering candidates, drill-through targets

2. Build dependency graph showing relationships

3. Determine creation order (topological sort)

4. Present plan to user with:
   - Total artifact count
   - Complexity assessment
   - Dependency visualization
   - Confirmation options: ✓ Approve | ⚠️ Modify | ✗ Cancel

5. Handle user modifications if requested

**Output:** Populates Section 1.2 (Artifact Breakdown Plan)

**User Interaction:** REQUIRED - User must approve artifact plan before proceeding

**Success Criteria:**
- All necessary artifacts identified
- Dependencies correctly mapped
- User has confirmed plan

---

## Phase 6: PARALLEL WORKFLOWS - Measure & Visual Specification

**Purpose:** Specify measures and visuals in parallel for efficiency

**Execution Pattern:** Two independent branches that write to different sections

### Branch A: Measure Specification (per NEW measure from Section 1.2)

**For each NEW measure identified:**

#### Step A1: Data Understanding & Specification

**Execute:** `powerbi-data-understanding-agent` (in measure mode)

**Input:**
- Measure name and purpose (from Section 1.2)
- Section 1.1 (schema)
- Workspace/dataset (if provided for data sampling)

**Agent Actions:**
- Interactive Q&A for measure specifications
- Recommend column selections, aggregations, filters
- Sample data if workspace/dataset available
- Handle time intelligence requirements

**Output:** Measure specification in Section 2.A subsection

#### Step A2: Pattern Discovery

**Execute:** `powerbi-pattern-discovery` agent

**Input:**
- Project path
- Measure specification from Step A1
- Findings file path

**Agent Actions:**
- Find similar measures in existing model
- Extract naming conventions, format strings, display folders
- Identify calculation patterns

**Output:** Appends patterns to Section 2.A subsection

#### Step A3: Code Generation

**Execute:** `powerbi-artifact-designer` agent

**Input:**
- Measure specification
- Discovered patterns
- Findings file path

**Agent Actions:**
- Generate complete DAX code
- Apply styling (format string, display folder, description)
- Include error handling

**Output:** Appends DAX code to Section 2.A subsection

**Final Section 2.A Structure:**
```markdown
## Section 2.A: Calculation Changes (Measures)

### Measure 1: Total Q4 Sales
**Change Type:** CREATE
**Proposed Code:** [DAX with formatString, displayFolder, description]
**Change Rationale:** [Details]

### Measure 2: Q4 QoQ Growth %
[Similar structure]
```

---

### Branch B: Visual Specification (per visual from Section 1.2)

**For each visual identified:**

#### Step B1: Visual Type Recommendation

**Execute:** `powerbi-visual-type-recommender` agent

**Input:**
- Visual purpose (from Section 1.2)
- Metric type (count, sum, percentage)
- Dimension cardinality (from Section 1.1)

**Agent Actions:**
- Analyze data characteristics
- Apply recommendation rules:
  - Single value → Card or KPI
  - 2-7 categories → Bar/Column chart
  - Time series → Line chart
  - High cardinality → Table or Matrix
- Present 2-3 options with pros/cons
- Get user selection

**Output:** Visual type recommendation in Section 2.B subsection

**User Interaction:** User chooses visual type from recommendations

#### Step B2: Visual Field Specification

**Execute:** `powerbi-data-understanding-agent` (in visual mode)

**Input:**
- Chosen visual type
- Available measures (from Section 1.1 + Section 2.A measure names)
- Available dimensions (from Section 1.1)

**Agent Actions:**
- Interactive Q&A for field mappings:
  - Which measure(s) for Values?
  - Which dimension for Axis/Legend/Rows/Columns?
  - Sorting preferences?
  - Filtering requirements?
- Formatting recommendations:
  - Data labels?
  - Title text?
  - Color scheme?
  - Conditional formatting?

**Output:** Appends complete visual specification to Section 2.B subsection

**Final Section 2.B Structure:**
```markdown
## Section 2.B: Visual Specifications

### Visual 1: Sales KPI Card
**Visual Type:** Card
**Data Mappings:** [Values, Axis, Legend, Tooltips]
**Formatting:** [Title, colors, labels]
**Filters:** [Visual-level filters]

### Visual 2: Regional Bar Chart
[Similar structure]
```

---

**Branch Coordination:**
- Both branches read Sections 1.0, 1.1, 1.2
- Branch A writes to Section 2.A
- Branch B writes to Section 2.B
- Branch B can reference measure NAMES from Section 1.2 (actual code generated in parallel)
- Next phase waits for BOTH branches to complete

---

## Phase 7: Page Layout Design

**Purpose:** Generate optimal coordinates and sizes for all visuals

**Execute:** `powerbi-page-layout-designer` agent

**Input:**
- Visual list from Section 2.B (with types and importance)
- Canvas size: 1600x900 (professional standard)
- Existing pages (to ensure filter pane consistency)
- Findings file path

**Agent Actions:**
1. Categorize visuals by importance and type
2. Apply research-based layout hierarchy:
   - Top-left (0-800x, 0-300y): Key KPIs
   - Top-right (800-1600x, 0-300y): Complementary metrics
   - Middle-left (0-800x, 300-700y): Primary analysis
   - Middle-right (800-1600x, 300-700y): Supporting analytics
   - Bottom (0-1600x, 700-900y): Filters/slicers
3. Use 8-pixel grid system for alignment
4. Calculate coordinates (x, y, width, height) for each visual
5. Validate no overlaps
6. Generate layout visualization (table + ASCII art)

**Output:** Populates Section 3 (Page Layout Plan)

```markdown
## Section 3: Page Layout Plan

**Canvas Size:** 1600 x 900 pixels

| Visual Name          | Type      | Position (x,y) | Size (w×h) | Zone         |
|----------------------|-----------|----------------|------------|--------------|
| Sales KPI Card       | Card      | (24, 24)       | 360×240    | Top-left     |
| Regional Bar Chart   | Bar Chart | (24, 288)      | 760×376    | Middle-left  |
| Quarter Slicer       | Slicer    | (24, 688)      | 200×168    | Bottom       |

[Layout visualization ASCII art]
[Layout rationale]
```

**Success Criteria:**
- All visuals positioned
- No overlaps detected
- Grid alignment verified
- Layout follows hierarchy principles

---

## Phase 8: Interaction Design

**Purpose:** Design cross-filtering and drill-through relationships

**Execute:** `powerbi-interaction-designer` agent

**Input:**
- Visual list from Section 2.B (with dimensions and measures)
- Layout from Section 3
- Page intent from Section 1.0
- Findings file path

**Agent Actions:**
1. Analyze common dimensions across visuals
2. Design cross-filtering matrix:
   - Visuals with shared dimensions → enable cross-filtering
   - Slicers → filter all visuals
   - Detail visuals (tables/matrices) → receive filters, don't send
3. Identify drill-through opportunities:
   - Summary visuals → detail pages (if applicable)
4. Bookmark navigation (only if requested or problem-suited)

**Output:** Populates Section 4 (Interaction Design)

```markdown
## Section 4: Interaction Design

### Cross-Filtering Matrix
[Table showing which visuals filter which]

### Drill-Through Targets
**From:** Regional Bar Chart
**To:** Regional Detail Page (helper page - recommended)
**Context:** Region[Region Name]
```

**Success Criteria:**
- Interaction matrix complete
- Drill-through targets identified
- Logic documented

---

## Phase 9: PBIR Page File Generation

**Purpose:** Generate complete PBIR files ready for implementation

**Execute:** `powerbi-pbir-page-generator` agent

**Input:**
- Visual specifications (Section 2.B)
- Layout coordinates (Section 3)
- Interactions (Section 4)
- Measure references (Section 2.A measure names)
- Findings file path

**Agent Actions:**
1. Generate page folder structure plan:
   ```
   .Report/definition/pages/[PageGUID]/
   ├── page.json
   └── visuals/
       ├── [VisualGUID1]/visual.json
       ├── [VisualGUID2]/visual.json
       ...
   ```

2. Create complete page.json content

3. For each visual, generate complete visual.json:
   - visualType
   - x, y, width, height (from Section 3)
   - config blob (stringified JSON with formatting)
   - query transforms (measure bindings)
   - filters (from Section 2.B)
   - interactions (from Section 4)

4. Generate pages.json update

**Output:** Populates Section 5 (PBIR Page Files)

```markdown
## Section 5: PBIR Page Files

**Page Folder:** `.Report/definition/pages/ReportSection12345678/`

### page.json
**Complete File Contents:**
```json
{...}
```

### Visual Files
#### Visual 1: Sales KPI Card
**File:** `visuals/VisualContainer1/visual.json`
**Complete File Contents:**
```json
{...}
```

[Repeat for all visuals]

### pages.json Update
**Action:** Add new page entry
```json
{...}
```
```

**Success Criteria:**
- All JSON valid
- Measure bindings reference measures from Section 2.A or existing model
- Layout coordinates match Section 3
- Interactions match Section 4

---

## Phase 10: Helper Page Identification

**Purpose:** Identify additional pages that would enhance this page

**Executed by:** Main orchestrator (not separate agent)

**Actions:**
1. Review drill-through targets from Section 4
2. Analyze detail visuals that might need dedicated pages
3. Identify complementary analytical views

**Output:** Populates Section 6 (Helper Page Recommendations)

```markdown
## Section 6: Helper Page Recommendations

**Recommended Pages to Create (in future workflows):**

### 1. Regional Detail Page (HIGH PRIORITY)
**Purpose:** Drill-through target
**Triggered by:** Right-click region in bar chart
**Command:**
```bash
/create-pbi-page-specs --project "<path>" \
  --question "Show detailed product breakdown for a specific region"
```
```

---

## Phase 11: Validation

**Purpose:** Validate specifications before marking complete

**Execute:** Two validation agents in sequence

### Validation 1: DAX Measures

**Agent:** `power-bi-verification`

**Input:** Findings file path (Sections 2.A, 5)

**Checks:**
- DAX syntax correctness
- Measure references valid
- No circular dependencies
- Performance considerations

### Validation 2: PBIR Files

**Agent:** `powerbi-pbir-validator`

**Input:** Findings file path (Section 5)

**Checks:**
- JSON structure valid
- Config blob parseable
- Measure bindings reference valid measures
- Coordinates within canvas bounds
- No visual overlaps
- Interaction references valid

**Iteration:**
- If validation fails: Document error, attempt fix, re-validate (max 3 iterations)
- If still failing after 3 iterations: Escalate to user with error details

**Output:** Populates Section 7 (Validation Results)

**Success Criteria:**
- All validation checks pass OR
- User has been informed of validation warnings/errors

---

## Phase 12: Final Summary with Before/After

**Purpose:** Generate clear summary showing page creation impact

**Executed by:** Main orchestrator

**Actions:**
1. Summarize what was created
2. Show before/after state comparison
3. Provide concrete example user flow
4. List next steps clearly

**Output:** Populates Section 8 (Final Summary)

```markdown
## Section 8: Final Summary

### What Was Created
**Specifications for:**
- Page: [Page Name]
- [N] new measures
- [M] visuals
- [K] cross-filtering interactions
- [P] drill-through targets

### Before
- No dedicated page for [question]
- [Current user experience pain points]

### After
- Single page answers [question]
- [Improved user experience]

### Example User Flow
[Concrete step-by-step scenario]

### Next Steps

1. **Review specifications:**
   `agent_scratchpads/[timestamp]-[page-name]/findings.md`

2. **Implement page** (creates versioned copy + applies changes):
   ```bash
   /implement-deploy-test-pbi-project-file \
     --findings "agent_scratchpads/[timestamp]-[page-name]/findings.md"
   ```

3. **Create helper pages** (if recommended):
   ```bash
   /create-pbi-page-specs --project "<path>" --question "[helper page question]"
   ```

⚠️ **IMPORTANT:** This command only created specifications. No files were modified.
Run `/implement-deploy-test-pbi-project-file` to apply changes.
```

---

## Output Structure

The generated findings file follows this structure:

```markdown
# Page Specifications: [Page Name]

**Created**: [Timestamp]
**Project**: [Project Path]
**Status**: [In Progress / Specifications Complete]

---

## Original Command

```bash
/create-pbi-page-specs --project "<path>" --question "<question>" [options]
```

---

## Prerequisites

[Validation results from powerbi-verify-pbiproject-folder-setup]

---

## Section 1.0: Question Analysis & Page Planning
[powerbi-page-question-analyzer output]

## Section 1.1: Data Model Schema
[powerbi-data-model-analyzer output]

## Section 1.2: Artifact Breakdown Plan
[powerbi-artifact-decomposer output]

---

## Section 2: Proposed Changes

### A. Calculation Changes (Measures)
[Per-measure specifications with DAX code]

### B. Visual Specifications
[Per-visual specifications with field mappings and formatting]

---

## Section 3: Page Layout Plan
[powerbi-page-layout-designer output]

## Section 4: Interaction Design
[powerbi-interaction-designer output]

## Section 5: PBIR Page Files
[powerbi-pbir-page-generator output - complete JSON files]

## Section 6: Helper Page Recommendations
[Main orchestrator output]

## Section 7: Validation Results
[power-bi-verification + powerbi-pbir-validator output]

## Section 8: Final Summary
[Main orchestrator output with before/after]
```

---

## Error Handling

- **Project not found**: "Error: Power BI project folder not found at '<path>'. Please verify the path points to a valid .pbip project directory."
- **No .Report folder**: "Error: Page creation requires a Power BI Project (.pbip) format with .Report folder. The specified project does not have a .Report folder. Please convert your project in Power BI Desktop (File → Save As → Power BI Project)."
- **Invalid question format**: "Error: Business question parameter is required. Please provide a clear business question this page should answer."
- **Agent failure**: Report which agent failed and at which phase, preserve partial findings file, offer retry or abort
- **Validation failure after 3 iterations**: Report validation errors to user with detailed diagnostic information
- **Authentication Required** (data sampling):
  - Use pre-flight authentication check (same as evaluate-pbi-project-file)
  - Prompt user for device code authentication
  - Allow user to skip data sampling and proceed with schema-only mode

---

## Best Practices

1. **Provide workspace and dataset** when possible for data sampling - significantly improves recommendation quality for both measures and visuals
2. **Review Section 1.2 carefully** - artifact decomposition is your blueprint, ensure it's complete before proceeding
3. **Leverage visual type recommendations** from Section 2.B - data-driven suggestions optimize analytical effectiveness
4. **Review layout in Section 3** - ensure visual positioning makes analytical sense for your users' workflow
5. **Validate drill-through targets** in Section 6 - plan helper pages early for cohesive dashboard design
6. **Review findings.md thoroughly** before running implementation - all specifications can be manually adjusted if needed

---

## Integration with /implement-deploy-test-pbi-project-file

This command is designed as the first step in a two-phase workflow:

**Phase 1: Specification (this command)**
```bash
/create-pbi-page-specs --project "C:\path\to\project" \
  --question "Show Q4 sales by region with YoY growth"
```
→ Creates findings.md with Sections 2.A (measures), 2.B (visuals), 5 (PBIR files)

**Phase 2: Implementation**
```bash
/implement-deploy-test-pbi-project-file \
  --findings "agent_scratchpads/YYYYMMDD-HHMMSS-page-name/findings.md" \
  [--deploy "DEV"] \
  [--test]
```
→ Applies measures, creates page files, validates, deploys, tests

---

## Notes

- This command creates **new pages**, not modifying existing ones (use `/evaluate-pbi-project-file` for modifications)
- Data sampling via XMLA is **optional but recommended** - provides evidence-based recommendations for both measures and visuals
- Parallel measure + visual specification minimizes user wait time
- All findings are preserved in timestamped scratchpad folders for historical reference
- Agents can be re-run individually if needed by invoking them directly with the findings file path
- Layout design uses research-based best practices (1600x900 canvas, 8-pixel grid, F-pattern reading hierarchy)
- Output is compatible with the unified implementation command

---

## Testing Strategy

**Test Case 1: Simple Page**
```bash
/create-pbi-page-specs --project "./test-project" \
  --question "Show total Q4 sales"
```
Expected: 1 card visual, 1 simple measure, minimal interactions

**Test Case 2: Complex Page**
```bash
/create-pbi-page-specs --project "./test-project" \
  --question "Compare regional sales performance with category breakdown and YoY trends" \
  --workspace "Test Workspace" \
  --dataset "Test Model"
```
Expected: 7+ visuals, 5+ measures (including time intelligence), rich cross-filtering, drill-through targets

**Test Case 3: Reference-Only Page**
```bash
/create-pbi-page-specs --project "./test-project" \
  --question "Create regional dashboard using existing sales measures"
```
Expected: Multiple visuals, no new measures (all existing), layout and interaction focus
