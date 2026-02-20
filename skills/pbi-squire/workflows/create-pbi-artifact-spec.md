---
name: create-pbi-artifact-spec
description: Create new Power BI code artifacts (measures, calculated columns, tables) through an interactive specification process that analyzes the data model, samples data, discovers patterns, and generates implementation-ready DAX/M code with styling
pattern: ^/create-pbi-artifact-spec\s+(.+)$
---

# Create Power BI Artifact Specification

> **MAIN THREAD EXECUTION**: This workflow executes in the MAIN THREAD, not a subagent.
> The main thread spawns leaf subagents via `Task()` and coordinates their work through findings.md.
> Subagents do NOT spawn other subagents.

This slash command creates comprehensive specifications for new Power BI **code artifacts** (measures, calculated columns, tables) through an interactive, human-in-the-loop process that:
1. Analyzes the existing data model structure
2. Iteratively clarifies requirements through intelligent Q&A with data sampling
3. Discovers existing patterns and conventions to follow
4. Designs complete DAX/M code with styling specifications
5. Outputs findings.md ready for `/implement-deploy-test-pbi-project-file`

> **NOTE:** This workflow handles **code-based artifacts** only. For visual creation (cards, charts, tables, slicers), use `/create-pbi-page-specs` which handles layout, field bindings, visual.json generation, and PBIR file creation.

## Tracing Output (Required)

**IMPORTANT:** This workflow MUST output trace markers for visibility. See `resources/tracing-conventions.md` for full format.

**On workflow start, output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 WORKFLOW: create-pbi-artifact-spec
   └─ Type: [artifact-type or auto-detect]
   └─ Description: [brief description]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Before each phase, output:**
```
📋 PHASE [N]: [Phase Name]
   └─ [What this phase does]
```

**When invoking agents, output:**
```
   └─ 🤖 [AGENT] [agent-name]
   └─    Starting: [brief description]
```

**When using MCP tools, output:**
```
   └─ 🔌 [MCP] [tool-name]
   └─    [context/parameters]
   └─    ✅ Success / ❌ Error: [result]
```

**On workflow complete, output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WORKFLOW COMPLETE: create-pbi-artifact-spec
   └─ Artifacts: [list of artifacts created]
   └─ Output: [findings file path]
   └─ Next: Run /implement-deploy-test-pbi-project-file
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Usage

### Standalone Mode (Default)

```bash
/create-pbi-artifact-spec --project <path-to-pbip-folder> --type <artifact-type> --description "<what to create>" [--workspace <workspace-name>] [--dataset <dataset-name>]
```

### Embedded Mode (Called by page-specs)

```bash
# Internal use only - called by /create-pbi-page-specs workflow
create-pbi-artifact-spec --embedded-mode \
  --parent-findings "<path-to-parent-findings.md>" \
  --section "<section-id>" \
  --schema-section "<schema-section-id>" \
  --type <artifact-type> \
  --description "<what to create>"
```

### Parameters

#### Standard Parameters

- `--project` (required in standalone mode): Path to the Power BI Project folder (the folder containing the .pbip file structure)
- `--type` (optional): Type of artifact to create - if omitted, agent will analyze description and detect all needed artifacts
  - `measure`: Single DAX measure
  - `calculated-column`: Single DAX calculated column
  - `table`: Single new table (with M query or DAX)
  - `auto`: Auto-detect artifacts from description (default if omitted)
  - `multi`: Explicitly request multi-artifact analysis
  - ~~`visual`~~: **Removed** - Use `/create-pbi-page-specs` for visual creation
- `--description` (required): Description of what to create (e.g., "Year-over-Year Revenue Growth percentage measure")
- `--workspace` (optional): Power BI workspace name for XMLA data sampling. If provided, enables data context retrieval for better recommendations
- `--dataset` (optional): Power BI dataset/semantic model name for XMLA data sampling. Required if `--workspace` is provided

#### Embedded Mode Parameters (Internal Use)

These parameters are used when `/create-pbi-page-specs` calls this workflow as a sub-workflow:

- `--embedded-mode` (boolean): Run as sub-workflow, skip setup phases
- `--parent-findings` (path): Path to parent workflow's findings.md
- `--section` (string): Section identifier to write output to (e.g., "2.A.1")
- `--schema-section` (string): Section in parent findings to read schema from (e.g., "1.1")

**Embedded Mode Behavior:**
- **Skip Phase 1-2:** Project already validated, scratchpad already created by parent
- **Phase 3:** Read schema from `--schema-section` in `--parent-findings` instead of extracting
- **Phases 4-6:** Execute normally (data understanding, pattern discovery, code generation)
- **Phase 7:** Skip completion messaging (parent handles workflow completion)
- **Output:** Write to `--section` in `--parent-findings` instead of own findings.md

### Examples

```bash
# Create a new measure (no data sampling)
/create-pbi-artifact-spec --project "C:\Projects\SalesReport" --type measure --description "Year-over-Year Revenue Growth percentage"

# Create a new measure with data sampling for better recommendations
/create-pbi-artifact-spec --project "./MyReport" --type measure --description "YoY Growth %" --workspace "Sales Analytics" --dataset "Sales Report Model"

# Create a new calculated column
/create-pbi-artifact-spec --project "C:\Reports\FinanceDashboard.Report" --type calculated-column --description "Customer full name combining first and last name"

# Create a new table
/create-pbi-artifact-spec --project "C:\Projects\Analysis" --type table --description "Date dimension table with fiscal calendar"

# Multi-artifact creation (auto-detect from description)
/create-pbi-artifact-spec --project "./Dashboard" --description "Create YoY growth measure with prior year helper"
# Agent will detect: YoY measure + PY helper measure

# Explicitly request multi-artifact analysis
/create-pbi-artifact-spec --project "C:\Reports\KPI" --type multi --description "Revenue, profit margin, and customer count measures"
# Agent will detect: 3 measures with any shared dependencies

# NOTE: For visuals, use /create-pbi-page-specs instead:
# /create-pbi-page-specs --project "./Dashboard" --question "Show sales performance card with YoY comparison"
```

## Workflow

### Phase 1: Validation & Setup

> **SKIP IF:** `--embedded-mode` is true (parent workflow already validated project)

1. Parse command arguments to extract project path, artifact type, and description
2. Validate that the Power BI project folder exists
3. Search for `.pbip` files and TMDL structure to confirm valid project
4. Exit with clear error message if project is invalid
5. Create scratchpad workspace for this creation session

### Phase 2: Scratchpad Creation

> **SKIP IF:** `--embedded-mode` is true (use parent's scratchpad and findings.md)

1. Generate timestamp: `YYYYMMDD-HHMMSS` format
2. Create distilled artifact name:
   - Extract key terms from description
   - Convert to kebab-case
   - Prefix with "create-"
   - Limit to reasonable length (~30-40 chars)
   - Example: "create-yoy-revenue-growth"
3. Create folder: `agent_scratchpads/<timestamp>-<distilled-name>/`
4. Create findings file: `agent_scratchpads/<timestamp>-<distilled-name>/findings.md`
5. Populate findings file with:
   - **Original Command** section at the very top with the full command-line prompt used
   - Problem Statement section (creation request)
   - Power BI project path information
   - Empty sections 1.0-1.3 and Section 2 ready for agent population

### Phase 3: Data Model Analysis

> **IF `--embedded-mode` is true:** Read schema from `--schema-section` in `--parent-findings` file instead of extracting. Skip to Phase 4.

**Main thread spawns:** `Task(powerbi-data-model-analyzer)`

**Purpose:** Extract and document the existing data model schema

**Standalone Mode Input:**
- Project path
- Findings file path
- Artifact type and description (for context)

**Standalone Mode Actions:**
1. Scan `.SemanticModel/definition/tables/*.tmdl` files
2. Extract table definitions: names, columns, data types
3. Parse `model.tmdl` for relationships and cardinality
4. Identify fact vs dimension tables (naming patterns, relationships)
5. Document table structures relevant to the creation request

**Schema Extraction Pattern (for reference):**
```
# Main thread can extract schema using:
1. Glob for TMDL files: **/*.SemanticModel/definition/tables/*.tmdl
2. For each .tmdl file, extract:
   - Table name (from file or content)
   - Columns (names, data types)
   - Measures (names, expressions)
3. Read model.tmdl for relationships: **/*.SemanticModel/definition/model.tmdl
4. Build schema documentation
# Reference: TmdlParser in tools/developer/pbi_merger_utils.py (Developer Edition)
```

**Output:** Populates **Section 1.1: Data Model Schema** with:
- List of relevant tables
- Column names and data types for each table
- Relationships between tables
- Approximate row counts (if available in metadata)
- Fact vs dimension classification

**Success Criteria:**
- Complete schema documented
- Relevant tables identified based on artifact description
- Relationships mapped

### Phase 3.5: Artifact Decomposition ⭐ NEW PHASE

**Main thread spawns:** `Task(powerbi-artifact-decomposer)`

**Purpose:** Analyze the creation request and break it down into discrete artifacts with dependency relationships

**When to execute:**
- Always execute if `--type` is omitted, `auto`, or `multi`
- Skip if `--type` is specific (measure, calculated-column, table, visual) AND description suggests single artifact
- Execute if description suggests complexity even with specific type

**Input:**
- Findings file path (with Section 1.1 completed)
- Original creation request
- Artifact type parameter

**Agent Actions:**
1. Parse description for artifact keywords (visual, measure, YoY, KPI, etc.)
2. Identify primary artifact (what user primarily wants)
3. Detect explicit references (mentions of specific measures/columns)
4. Detect implicit dependencies:
   - Visual needs measures
   - YoY needs PY helper
   - Complex calculations need intermediate measures
5. Check Section 1.1 to determine which artifacts exist vs need creation
6. Build dependency graph showing relationships
7. Determine creation order (topological sort)
8. Present plan to user for confirmation
9. Handle user modifications (add/remove/rename artifacts)

**Output:** Populates **Section 1.0: Artifact Breakdown Plan** with:
- List of all artifacts (primary + dependencies)
- For each artifact:
  - Type (measure, column, table, visual)
  - Purpose (why needed)
  - Status (CREATE vs existing/reference)
  - Priority/order
  - Dependencies (what it needs)
  - Used by (what needs it)
- Dependency graph (ASCII art)
- Creation order with reasoning
- User confirmation status
- Any modifications made

**User Interaction Example:**
```
📊 ARTIFACT DECOMPOSITION

Analyzing: "sales performance card with YoY growth"

I've identified 3 artifacts needed:

PRIMARY ARTIFACT:
1. 📊 Card Visual - Sales Performance Card
   Dependencies: [Total Revenue], [YoY Revenue Growth %]

REQUIRED MEASURES:
2. 📈 Measure - YoY Revenue Growth %
   Status: ❌ Does not exist (will create)
   Dependencies: [Total Revenue], [Total Revenue PY]

3. 📈 Measure - Total Revenue PY (Helper)
   Status: ❌ Does not exist (will create)

CREATION ORDER:
1. Total Revenue PY
2. YoY Revenue Growth %
3. Sales Performance Card

✓ Create all 3 artifacts
⚠️ Modify list
✗ Cancel
```

**Success Criteria:**
- All necessary artifacts identified
- Dependencies correctly mapped
- Creation order validated (no circular dependencies)
- User has confirmed or modified the plan

**Skip Conditions:**
- Single-artifact request with no dependencies
- User explicitly specified `--type measure` AND description is simple ("calculate total revenue")

### Phase 4: Interactive Data Understanding (CRITICAL PHASE)

**UPDATED:** Now iterates over each artifact from Section 1.0

**Main thread spawns:** `Task(powerbi-data-understanding-agent)`

**Purpose:** Build complete artifact specification through iterative Q&A with intelligent recommendations and data sampling

**Input:**
- Findings file path (with Section 1.1 completed)
- Artifact type and description
- Workspace and dataset names (if provided for data sampling)
- User responses to Q&A

**Agent Workflow:**

#### Step 4.1: Initial Analysis
- Read Section 1.1 (data model schema)
- Analyze artifact description to identify likely data sources
- Identify relevant tables and columns based on naming and types

#### Step 4.2: Make Intelligent Recommendations
For each specification aspect:
- **Analyze schema** to determine best options
- **Sample data** (if workspace/dataset provided) to validate assumptions
- **Make recommendation** with evidence and confidence level
- **Show alternatives** when applicable
- **Present to user** in structured format with ✓/✗ confirmation options

Recommendation Categories:
1. **Data Source Selection**
   - Which tables and columns to use
   - Aggregation methods (SUM, AVERAGE, COUNT, etc.)
   - Grain/level of calculation

2. **Filtering Logic**
   - Detect categorical columns (low cardinality)
   - Sample value distributions
   - Recommend filters based on patterns

3. **Date/Time Context**
   - Identify date columns with relationships to date dimension
   - Recommend time intelligence approaches
   - Handle fiscal vs calendar considerations

4. **Business Logic**
   - Calculation methods based on similar patterns
   - Edge case handling (division by zero, NULLs, blanks)
   - Performance considerations

5. **Styling & Formatting**
   - Format string patterns from similar artifacts
   - Display folder organization
   - Description/tooltip best practices
   - Conditional formatting recommendations

#### Step 4.3: Data Sampling (Conditional)

**When to sample:**
- Workspace and dataset parameters provided AND
- User approves data sampling AND
- Any of these conditions met:
  - Column usage is ambiguous
  - Data grain needs verification
  - Value distributions matter (e.g., status codes)
  - NULL handling needs validation

**Sampling Queries:**
```dax
-- Sample 1: Understand table grain and structure
EVALUATE TOPN(100, [Table], [Date Column], DESC)

-- Sample 2: Check column distributions
EVALUATE
SUMMARIZE(
    [Table],
    [Column],
    "Count", COUNTROWS([Table])
)

-- Sample 3: Data quality checks
EVALUATE {
    ("Total Rows", COUNTROWS([Table])),
    ("NULL Values", COUNTROWS(FILTER([Table], ISBLANK([Column])))),
    ("Distinct Values", DISTINCTCOUNT([Table][Column]))
}
```

**Present findings to user with visual formatting**

#### Step 4.4: Iterative Refinement
- User confirms (✓) or corrects (✗) each recommendation
- For corrections, update specification and potentially re-sample data
- Iterate until all specification aspects are confirmed
- Maintain audit trail of recommendations vs corrections

**Output:** Populates **Section 1.2: Data Understanding & Artifact Specification** with:
- Business requirement statement
- Data sources identified with treatment decisions
- Data validation results (if sampling performed)
- Complete business logic specification
- Column treatment table
- **Styling & formatting decisions**
- Confirmation trail (what was recommended, what was accepted/corrected)

**Success Criteria:**
- All specification aspects confirmed by user
- Styling decisions documented
- Edge cases addressed
- Specification marked as COMPLETE

### Phase 5: Pattern Discovery

**Main thread spawns:** `Task(powerbi-pattern-discovery)`

**Purpose:** Find existing similar artifacts and extract patterns to follow

**Input:**
- Project path
- Findings file path (with Sections 1.1 and 1.2 completed)
- Artifact type

**Agent Actions:**
1. Read Section 1.2 to understand what patterns to search for
2. Search existing TMDL files for similar artifacts (measures, columns, tables)
3. Extract naming conventions:
   - Prefixes and suffixes
   - Casing patterns (CamelCase, spaces, underscores)
   - Special characters
4. Identify calculation patterns:
   - Time intelligence functions used
   - DIVIDE() vs manual division
   - Helper measure patterns
   - Filter patterns
5. Extract styling patterns:
   - Format string conventions
   - Display folder organization
   - Description styles
6. For visuals: Extract design system patterns (colors, fonts, layouts)

**Output:** Populates **Section 1.3: Pattern Discovery** with:
- Similar artifacts found with code examples
- Naming conventions observed
- Calculation patterns documented
- Styling patterns extracted
- Design system patterns (if visual)

**Success Criteria:**
- At least one similar pattern found (or documented that this is truly novel)
- Naming conventions clear
- Styling patterns documented

### Phase 6: Artifact Design & Code Generation

**Main thread spawns:** `Task(powerbi-artifact-designer)`

**Purpose:** Generate final DAX/M code and complete styling specifications

**Input:**
- Findings file path (with Sections 1.1, 1.2, 1.3 completed)
- Artifact type

**Agent Workflow:**

#### Step 6.1: Review Complete Specification
- Read all context from Sections 1.1-1.3
- Confirm final specification summary with user
- Ask any final clarifying questions

#### Step 6.2: Styling Finalization
Present styling recommendations based on Section 1.3 patterns:

```
📊 STYLING & FORMATTING CONFIRMATION

Based on existing patterns in your project, here are the styling recommendations:

1. FORMAT STRING
   ✓ RECOMMENDATION: "0.0%" (matches existing YoY measures)
   Evidence: [Similar measures use this format]
   ✓ Confirm / ✗ Change to: ____________

2. DISPLAY FOLDER
   ✓ RECOMMENDATION: "Growth Metrics"
   Evidence: [Existing YoY measures are in this folder]
   ✓ Confirm / ✗ Change to: ____________

3. DESCRIPTION
   ✓ RECOMMENDATION: "Year-over-year revenue growth percentage..."
   ✓ Confirm / ✗ Change to: ____________
```

#### Step 6.3: Code Generation
1. Generate DAX/M code following patterns from Section 1.3
2. Apply naming conventions discovered
3. Include error handling for edge cases from Section 1.2
4. Apply performance optimizations (variables, DIVIDE, etc.)
5. Include inline comments for complex logic

#### Step 6.4: Dependencies Check
- Identify required existing measures/columns/tables
- Verify required relationships exist
- Document any prerequisites

**Output:** Populates **Section 2: Proposed Changes** with:
- **Change Type:** CREATE
- **Target Location:** Specific .tmdl file path
- **Proposed Code:** Complete DAX/M implementation
- **Styling & Metadata:**
  - Format String with explanation
  - Display Folder with organizational purpose
  - Description/tooltip text
  - Data Category (if applicable)
- **Visual Formatting:** (if visual artifact)
  - Font specifications
  - Color scheme
  - Conditional formatting rules
  - Layout details
- **Change Rationale:** Detailed explanation of all decisions
- **Dependencies:** Required existing artifacts and relationships
- **Validation Notes:** Edge case handling and performance considerations

**Success Criteria:**
- Complete, syntactically valid code generated
- All styling specifications documented
- Dependencies identified
- Change rationale comprehensive

### Phase 6.5: Senior Review (pbi-squire-senior-reviewer) ⭐ Developer Edition

> **SKIP IF:** `--embedded-mode` is true (parent workflow handles review)
> **SKIP IF:** Developer Edition not detected (Analyst Edition skips this phase silently)

**Purpose**: Holistic review of the entire artifact specification — traces proposed artifacts through
the codebase and validates no unintended consequences (naming collisions, dependency conflicts, filter context issues).

**Conditional**: Only runs if Developer Edition is detected (check if `pbi-squire-senior-reviewer` agent is available). Skip silently on Analyst Edition.

**Input**: Entire findings.md (all sections), plus direct access to PBIP codebase
**Output**: Section 2.9 (Senior Review) — only populated if concerns exist

**Invocation**: Always runs after artifact design is complete (Section 2 populated)

**Main thread spawns**: `Task(pbi-squire-senior-reviewer)`

```
project_path: <project-path>
findings_file_path: <scratchpad-path>/findings.md

Read: ALL sections of findings.md (Sections 1.1-1.3 and Section 2)
Read: Actual PBIP codebase files to check for naming collisions and dependency conflicts
Write: Section 2.9 (Senior Review)
```

**Quality Gate**:
- If APPROVED → proceed to Phase 7 (Completion)
- If CORRECTIONS RECOMMENDED → present corrections to user, offer to revise artifact design
- If CHANGES REQUIRED → present required changes, return to Phase 6 (redesign)

### Phase 7: Completion

> **SKIP IF:** `--embedded-mode` is true (parent workflow handles completion messaging)

**Standalone Mode Only:**

1. Display summary of findings location
2. Show specification completion status
3. Show senior review status (if senior review ran)
4. Provide clickable link to findings file
5. **Suggest next steps:**
   ```
   ✅ Artifact specification complete!

   📄 Findings: agent_scratchpads/20251020-163045-create-yoy-growth/findings.md

   Next steps:
   1. Review the complete specification in findings.md
   2. Make any final edits to Section 2 if needed
   3. Run implementation command:
      /implement-deploy-test-pbi-project-file --findings "agent_scratchpads/20251020-163045-create-yoy-growth/findings.md"
   ```

**Embedded Mode:**
- Output is written to `--section` in `--parent-findings`
- No completion message displayed
- Return control to parent workflow

## Error Handling

- **Project not found**: "Error: Power BI project folder not found at '<path>'. Please verify the path points to a valid .pbip project directory."
- **Invalid project structure**: "Error: The specified folder does not appear to be a valid Power BI project (missing .SemanticModel or definition folders)."
- **Invalid artifact type**: "Error: Unsupported artifact type '<type>'. Supported types: measure, calculated-column, table. For visuals, use /create-pbi-page-specs."
- **Visual type requested**: "Note: Visual creation requires /create-pbi-page-specs which handles layout, field bindings, and PBIR file generation."
- **Agent failure**: Report which agent failed and why, preserve partial findings file
- **Data sampling unavailable**: Warn user but continue with schema-only recommendations
- **Embedded mode missing parameters**: "Error: Embedded mode requires --parent-findings, --section, and --schema-section parameters."
- **Authentication Required** (data sampling):
  - Use same pre-flight authentication check as evaluate-pbi-project-file
  - Prompt user for device code authentication
  - Allow user to skip data sampling and proceed with schema-only mode

### Handling Authentication for Data Sampling

**Pre-Flight Authentication Check:**

Before invoking `powerbi-data-understanding-agent` with data sampling:

1. **Check Token Validity** (if workspace/dataset provided):
   ```python
   import sys
   sys.path.insert(0, 'xmla_agent')
   from get_token import check_token_validity

   token_status = check_token_validity()
   ```

2. **Interpret Results:**
   - If `token_status['valid'] == True`: Proceed with data sampling
   - If `token_status['requires_auth'] == True`: Prompt user for authentication

3. **Prompt User for Authentication** (if required):
   ```
   ⚠️  AUTHENTICATION REQUIRED FOR DATA SAMPLING

   The data understanding agent can provide better recommendations if it can sample
   actual data from your Power BI semantic model.

   To enable data sampling, you need to authenticate to Power BI:
     1. Open the URL provided in your browser
     2. Enter the device code shown
     3. Sign in with your Power BI credentials

   Would you like to authenticate now?
     [Y] Yes - start authentication and enable data sampling
     [N] No - skip data sampling and use schema-only recommendations
   ```

4. **Execute Authentication** (if user confirms):
   ```python
   from get_token import get_access_token
   token = get_access_token()

   if token:
       print("✓ Authentication successful! Data sampling enabled.")
   else:
       print("⚠️  Authentication failed. Continuing with schema-only mode.")
   ```

5. **Handle User Decline:**
   - Continue to data understanding agent with `--no-data-sampling` flag
   - Agent operates in schema-only mode with reduced confidence levels
   - Note in findings.md: "Data sampling skipped - recommendations based on schema only"

## Output Structure

The generated findings file follows this structure:

```markdown
# Analysis: Create [Artifact Name]

**Created**: <Timestamp>
**Project**: <Project Path>
**Artifact Type**: [measure | calculated-column | table | visual]
**Status**: [In Progress / Specification Complete / Ready for Implementation]

---

## Original Command

```bash
/create-pbi-artifact-spec --project "<project-path>" --type <type> --description "<description>" [--workspace "<workspace>"] [--dataset "<dataset>"]
```

This command can be modified and re-run for subsequent iterations.

---

## Problem Statement

<Description of the artifact to be created>

**Artifact Type**: [Measure | Calculated Column | Table | Visual]
**Business Purpose**: <Why this artifact is needed>

**Project File Locations**:
- Semantic Model: `<path>/.SemanticModel/`
- TMDL Definitions: `<path>/.SemanticModel/definition/`
- Report: `<path>/.Report/` (if applicable)

---

## Section 1: Current Implementation Investigation

### 1.1 Data Model Schema
[Populated by powerbi-data-model-analyzer]

### 1.2 Data Understanding & Artifact Specification
[Populated by powerbi-data-understanding-agent through iterative Q&A]

### 1.3 Pattern Discovery
[Populated by powerbi-pattern-discovery]

---

## Section 2: Proposed Changes

### [Artifact Name] - [Artifact Type]
**Change Type:** CREATE
**Target Location:** [filename.tmdl](path/to/file.tmdl)

**Proposed Code:**
```dax
[Complete DAX or M code]
```

**Styling & Metadata:**
- Format String: `"pattern"`
- Display Folder: `"folder/path"`
- Description: `"tooltip text"`
- Data Category: [None | Email | WebURL | etc.]

**Visual Formatting:** (if visual)
[Detailed visual styling specifications]

**Change Rationale:**
[Complete explanation of all decisions]

**Dependencies:**
- [Required artifacts and relationships]

**Validation Notes:**
- [Edge case handling]
- [Performance considerations]

---

## Section 3: Test Cases and Impact Analysis
[To be populated during implementation phase]
```

## Integration with implement-deploy-test-pbi-project-file

This command is designed as the first step in a two-phase workflow:

**Phase 1: Specification (this command)**
```bash
/create-pbi-artifact-spec --project "C:\path\to\project" --type measure \
  --description "YoY Revenue Growth %"
```
→ Creates findings.md with Section 2 (Proposed Changes) in CREATE format

**Phase 2: Implementation**
```bash
/implement-deploy-test-pbi-project-file \
  --findings "agent_scratchpads/YYYYMMDD-HHMMSS-create-artifact/findings.md" \
  --deploy "DEV"
```
→ Applies changes from Section 2, validates, deploys, tests

## Notes

- This command is designed for creating **new** artifacts, not modifying existing ones (use `/evaluate-pbi-project-file` for modifications)
- Data sampling via XMLA is **optional but recommended** - provides evidence-based recommendations
- The recommendation-first Q&A approach minimizes user effort (confirm vs typing full answers)
- All findings are preserved in timestamped scratchpad folders for historical reference
- Agents can be re-run individually if needed by invoking them directly with the findings file path
- Styling is integrated throughout the workflow, not an afterthought
- Output is compatible with the unified implementation command

## Best Practices

1. **Provide workspace and dataset** when possible for data sampling - significantly improves recommendation quality
2. **Review Section 1.2 carefully** - this is your specification, ensure it's complete before proceeding
3. **Leverage existing patterns** from Section 1.3 - consistency is valuable
4. **Document styling decisions** - future maintainers will thank you
5. **Test edge cases** - the specification should address NULL handling, division by zero, etc.

---

## Final Phase: Agent Usage Analytics

After the workflow completes, run token analysis and generate aggregated metrics:

```bash
python .claude/tools/token_analyzer.py --full
python .claude/tools/analytics_merger.py
```

This step:
1. Parses Claude Code JSONL logs for token usage data
2. Correlates with runtime events captured by hooks
3. Updates `agent_scratchpads/_analytics/agent_analytics.json` with aggregated metrics

**Note**: Runtime events are captured automatically via hooks. Token analysis requires parsing Claude Code's session logs.
