# Power BI Analyst Agent System

This repository contains a comprehensive system of commands and agents designed to analyze, modify, and deploy Power BI projects with automated workflows.

## Table of Contents

- [Commands](#commands)
- [Agents](#agents)
- [Workflow Integration](#workflow-integration)

---

## Commands

Commands are invoked using slash notation (e.g., `/evaluate-pbi-project-file`) and orchestrate complex multi-agent workflows.

### `/evaluate-pbi-project-file`

**Purpose:** Analyze and evaluate Power BI project changes by creating a comprehensive analyst findings report through interactive problem clarification and automated agent analysis.

**Usage:**
```bash
/evaluate-pbi-project-file --project <path-to-pbip-folder> [--image <path-to-image>] --description "<problem description>" [--workspace <workspace-name>] [--dataset <dataset-name>]
```

**Parameters:**
- `--project` (required): Path to the Power BI Project folder
- `--image` (optional): Path to an image file providing visual context
- `--description` (required): Description of the issue or update needed
- `--workspace` (optional): Power BI workspace name for XMLA data retrieval
- `--dataset` (optional): Dataset/semantic model name (required if `--workspace` provided)

**Workflow:**
1. **Project Validation**: Uses `powerbi-verify-pbiproject-folder-setup` to validate project structure
2. **Interactive Problem Clarification**: Refines the problem statement with user input
3. **Scratchpad Creation**: Creates timestamped workspace folder with findings.md
4. **Agent Orchestration**:
   - Pre-flight authentication check (if workspace/dataset provided)
   - `powerbi-data-context-agent` - Retrieves actual data from semantic model (optional)
   - **Classification**: Determines change type (calculation, visual, or hybrid)
   - **Investigation Phase** (conditional parallel execution):
     - `powerbi-code-locator` - Finds relevant TMDL/DAX/M code → Section 1.A
     - `powerbi-visual-locator` - Finds relevant PBIR visual state → Section 1.B (if visual changes)
   - **Planning Phase**: `powerbi-dashboard-update-planner` - Designs coordinated changes:
     - Calculation-only: Section 2.A
     - Visual-only: Section 2.B
     - Hybrid: Coordination Summary + Section 2.A + Section 2.B
   - `power-bi-verification` - Validates proposed changes
5. **Completion**: Displays verification verdict and suggests next steps

**Supported Change Types:**
- **Calculation Changes**: DAX measures, M queries, TMDL model definitions
- **Visual Changes**: PBIR visual properties (layout, formatting, titles, colors) - requires .pbip format
- **Hybrid Changes**: Both calculation and visual changes with automatic coordination

**Output:** Creates `agent_scratchpads/<timestamp>-<problem-name>/findings.md` with comprehensive analysis.

---

### `/create-pbi-artifact`

**Purpose:** Create new Power BI artifacts (measures, calculated columns, tables, visuals) through an interactive specification process that analyzes the data model, samples data, discovers patterns, and generates implementation-ready code with styling.

**Usage:**
```bash
/create-pbi-artifact --project <path-to-pbip-folder> --type <artifact-type> --description "<what to create>" [--workspace <workspace-name>] [--dataset <dataset-name>]
```

**Parameters:**
- `--project` (required): Path to the Power BI Project folder
- `--type` (optional): Type of artifact - `measure`, `calculated-column`, `table`, `visual`, `auto`, `multi`
- `--description` (required): Description of what to create
- `--workspace` (optional): Power BI workspace name for data sampling
- `--dataset` (optional): Dataset name (required if `--workspace` provided)

**Workflow:**
1. **Validation & Setup**: Validates project and creates scratchpad
2. **Data Model Analysis**: Uses `powerbi-data-model-analyzer` to extract schema
3. **Artifact Decomposition** ⭐: Uses `powerbi-artifact-decomposer` to identify all needed artifacts and dependencies
4. **Interactive Data Understanding** ⭐: Uses `powerbi-data-understanding-agent` to build complete specification through intelligent Q&A
5. **Pattern Discovery**: Uses `powerbi-pattern-discovery` to find existing similar artifacts
6. **Artifact Design**: Uses `powerbi-artifact-designer` to generate final code and styling
7. **Completion**: Outputs findings.md ready for implementation

**Output:** Creates `agent_scratchpads/<timestamp>-create-<name>/findings.md` with Section 2 (Proposed Changes) in CREATE format.

---

### `/implement-deploy-test-pbi-project-file`

**Purpose:** Implement Power BI code and/or visual changes from an analyst findings report by applying changes to a versioned project, optionally deploying to Power BI Service, and running automated tests.

**Usage:**
```bash
/implement-deploy-test-pbi-project-file --findings "<path-to-findings.md>" [--deploy "<environment>"] [--dashboard-url "<url>"]
```

**Parameters:**
- `--findings` (required): Path to findings.md file
- `--deploy` (optional): Environment name for deployment (e.g., "DEV", "TEST", "PROD")
- `--dashboard-url` (optional): URL of deployed dashboard for testing

**Workflow:**
1. **Validation & Setup**: Parses findings file and validates project
2. **Apply Changes** (conditional):
   - **Code Changes** (Section 2.A): Uses `powerbi-code-implementer-apply` to apply DAX/M/TMDL changes
   - **Visual Changes** (Section 2.B): Uses `powerbi-visual-implementer-apply` 🆕 to execute XML edit plans on visual.json files
3. **Validation** (conditional quality gates):
   - **TMDL Format** ⭐: Uses `powerbi-tmdl-syntax-validator` to validate file formatting (if code changes)
   - **PBIR Structure** ⭐: Uses `powerbi-pbir-validator` 🆕 to validate visual.json files (if visual changes)
   - **DAX Logic** ⭐: Uses `powerbi-dax-review-agent` to validate DAX syntax and semantics (if code changes)
4. **Deployment** (optional): Deploys to Power BI Service using PowerShell or pbi-tools
5. **Testing** (optional): Uses `powerbi-playwright-tester` to run automated tests
6. **Consolidate Results**: Updates findings.md with Section 4 (Implementation Results)

**Authentication Methods:**
- **User Authentication** (Recommended): Uses your Power BI login via PowerShell cmdlets
- **Service Principal** (CI/CD): Uses Azure service principal via pbi-tools

**Output:**
- Timestamped project copy with applied changes
- Updated findings.md with implementation results
- Test results in `test-results/` folder (if testing performed)

---

### `/merge-powerbi-projects`

**Purpose:** Compare two Power BI project folders, identify technical and business-level differences, and selectively merge changes from a comparison project into a main project with human-in-the-loop decision making.

**Usage:**
```bash
/merge-powerbi-projects --main "<path-to-main-project>" --comparison "<path-to-comparison-project>" [--description "<focus_area>"]
```

**Parameters:**
- `--main` (required): Path to the main/baseline Power BI project folder (.pbip)
- `--comparison` (required): Path to the comparison project folder containing changes to potentially merge
- `--description` (optional): Focus area to filter differences - only show changes related to this topic
  - Examples: "revenue calculations", "customer segmentation", "date tables", "YoY measures"
  - Filters based on component names, code content, visual data fields, and dependencies
  - Uses semantic matching (includes related terms and dependencies)

**Workflow:**
1. **Input Validation**: Validates both project paths and detects TMDL vs BIM format
2. **Technical Comparison**: Uses `powerbi-compare-project-code` to identify all technical differences
3. **Business Impact Analysis**: Uses `powerbi-code-understander` to explain business implications
4. **User Decision (HITL)**: Presents combined analysis and waits for user to choose Main or Comparison for each diff
5. **Parse Decisions**: Converts user responses into structured merge manifest
6. **Execute Merge**: Uses `powerbi-code-merger` to create new merged project
7. **TMDL Validation** ⭐: Uses `powerbi-tmdl-syntax-validator` to validate formatting
8. **DAX Validation** ⭐: Uses `powerbi-dax-review-agent` to validate DAX syntax
9. **Final Report**: Presents comprehensive report with merge log, validation results, and statistics

**Agents Involved:**
1. `powerbi-compare-project-code` - Technical Auditor (finds WHAT changed)
2. `powerbi-code-understander` - Business Analyst (explains WHY it matters)
3. `powerbi-code-merger` - Merge Surgeon (executes decisions)
4. `powerbi-tmdl-syntax-validator` - Format Validator (quality gate)
5. `powerbi-dax-review-agent` - DAX Validator (quality gate)

**User Response Format:**
```
# Individual decisions
diff_001: Comparison
diff_002: Main
diff_003: Comparison

# Or bulk decisions
all Main
all Comparison
```

**Output:**
- New timestamped merged project folder (e.g., `merged_20250128_143022.pbip`)
- Comprehensive merge report with:
  - Section 1: Code-Level Differences
  - Section 2: Business Impact Analysis
  - Section 3: Merge Execution Log
- Original projects remain unchanged (non-destructive)

**Supported Components:**
- Measures, calculated columns, calculated tables
- Tables, columns, relationships
- Report pages, visuals, filters
- Parameters, roles, expressions
- File additions/deletions

**Documentation:**
- Technical: [.claude/tools/README_MERGE_WORKFLOW.md](.claude/tools/README_MERGE_WORKFLOW.md)
- User Guide: [.claude/tools/MERGE_QUICK_START.md](.claude/tools/MERGE_QUICK_START.md)
- Diagrams: [.claude/tools/MERGE_WORKFLOW_DIAGRAM.md](.claude/tools/MERGE_WORKFLOW_DIAGRAM.md)

---

## Agents

Agents are specialized autonomous components invoked by commands to perform specific tasks. Each agent has expertise in a particular domain.

### Project Validation Agents

#### `powerbi-verify-pbiproject-folder-setup`

**Purpose:** Validates and prepares Power BI project folders at the start of evaluation workflows.

**Invocation:** Automatically invoked by commands; not called directly by users.

**Inputs:**
- `project_path`: Path to project folder, PBIX file, or pbi-tools folder
- `findings_file_path`: Path to findings.md
- `user_action`: Action to perform (`none`, `extract_with_pbitools`)

**What It Does:**
- Detects input format (Power BI Project .pbip, PBIX file, or pbi-tools format)
- Validates TMDL structure
- Handles PBIX extraction if needed using pbi-tools
- Writes structured status to Prerequisites section of findings.md

**Critical Constraint:** NEVER prompts users directly - only writes status for command to read.

**Output:** Prerequisites section in findings.md with validation status and project metadata.

---

### Data Analysis Agents

#### `powerbi-data-model-analyzer`

**Purpose:** Analyzes and documents Power BI data model schema by extracting table structures, column definitions, data types, and relationships from TMDL files.

**Invocation:** First step in artifact creation workflows.

**Inputs:**
- Creation request (artifact type and description)
- Findings file path
- Power BI project path

**What It Does:**
- Scans `.SemanticModel/definition/` folder for TMDL files
- Extracts table schemas, columns, data types
- Parses relationships from `model.tmdl`
- Identifies fact vs dimension tables
- Documents existing measures and their organization

**Requirements:**
- Valid Power BI project with TMDL format
- Read access to definition files

**Output:** Populates Section 1.1 (Data Model Schema) in findings.md with structured documentation.

---

#### `powerbi-data-context-agent`

**Purpose:** Retrieves actual data from Power BI semantic model via XMLA endpoints to provide factual context for problem diagnosis.

**Invocation:** Invoked BEFORE code analysis agents when investigating data-related issues.

**Inputs:**
- Problem statement
- Findings file path
- Workspace and dataset names
- Semantic model project path

**What It Does:**
- Extracts identifiers from problem statement (invoice numbers, names, dates)
- Constructs DAX queries to retrieve specific records or samples
- Connects to semantic model via XMLA
- Handles authentication (device code flow)
- Documents actual data values in findings file

**Authentication:** Requires Power BI authentication via device code flow.

**Critical Constraint:** Returns `status='auth_required'` if authentication needed - NEVER falls back to assumptions.

**Output:** Populates Data Context subsection in Section 1 with actual data from semantic model.

---

### Code Analysis Agents

#### `powerbi-code-locator`

**Purpose:** Identifies specific calculation code locations in Power BI projects before making modifications.

**Invocation:** Invoked during investigation phase when calculation changes are needed.

**Inputs:**
- User's change request (calculation portion)
- Findings file path
- Power BI project structure context
- Optional: image paths for visual analysis

**What It Does:**
- Interprets natural language requests to identify objects (measures, tables, columns)
- Analyzes dashboard screenshots if provided
- Scans TMDL files to locate object definitions
- Extracts complete code snippets (DAX expressions, M code, TMDL structures)
- Records exact file paths

**Critical Constraint:** Purely identification and extraction - NEVER modifies code or suggests improvements.

**Output:** Populates Section 1.A (Calculation Code Investigation) with code snippets and locations.

---

#### `powerbi-visual-locator` 🆕

**Purpose:** Identifies and documents current state of PBIR visuals before planning visual modifications.

**Invocation:** Invoked during investigation phase when visual changes are needed.

**Inputs:**
- Visual change request (extracted from problem statement)
- Power BI Project .Report folder path
- Findings file path
- Context about which visuals to locate

**What It Does:**
- Reads PBIR file structure (report.json, page.json, visual.json)
- Locates specific visuals by name, page, or description
- Extracts current visual properties (layout, type, configuration)
- Parses stringified config blob for formatting details
- Documents data bindings (measures/columns used by visual)
- Analyzes dashboard screenshots to identify visuals

**Requirements:**
- Power BI Project (.pbip) format with .Report folder
- Not applicable for pbi-tools format

**Output:** Populates Section 1.B (Visual Current State Investigation) with visual state documentation.

---

#### `powerbi-dashboard-update-planner` 🆕

**Purpose:** Dashboard update planning agent that designs calculation changes, visual changes, or both with automatic coordination.

**Invocation:** After investigation phase completes (replaces separate code-fix and visual-edit agents).

**Inputs:**
- Problem statement
- Findings file path
- Section 1.A (if exists - calculation code context)
- Section 1.B (if exists - visual state context)

**What It Does:**
- **Self-detects scenario** by reading Section 1.A and 1.B:
  - Calculation-only: Designs DAX/M/TMDL fixes
  - Visual-only: Generates XML edit plans for PBIR changes
  - Hybrid: Coordinates both (code changes inform visual changes)
- **For calculation changes**: Diagnoses root causes, generates corrected code
- **For visual changes**: Creates machine-executable XML edit plans
- **For hybrid changes**:
  - Designs calculation changes FIRST (determines measure names, formats)
  - Designs visual changes SECOND (references exact names from calculations)
  - Documents dependencies and execution order
- **Web Research Capability**: Can search Power BI forums, expert blogs, and documentation when:
  - Problem involves advanced/non-standard DAX patterns
  - Complex M code transformations requiring specialized techniques
  - Obscure TMDL syntax or recent Power BI feature updates
  - Specialized community knowledge needed for complex scenarios
  - Documents research sources in Change Rationale section

**Expertise:**
- DAX: Context transition, filter context, iterator optimization, best practices
- M Code: Query folding preservation, performance optimization
- TMDL: Syntax correctness, relationship definitions
- PBIR: Visual.json schema, XML edit plan generation, config blob editing
- Research: **dax.guide** (authoritative DAX reference), **powerquery.how** (M code patterns), Power BI forums, SQLBI resources, Microsoft docs, expert blogs

**Critical Feature:** Single agent ensures naming consistency in hybrid scenarios (measure names in Section 2.A exactly match visual references in Section 2.B).

**Output:**
- **Calculation-only**: Section 2.A (Calculation Changes)
- **Visual-only**: Section 2.B (Visual Changes) with XML edit plans
- **Hybrid**: Coordination Summary + Section 2.A + Section 2.B

**Replaces:** `powerbi-code-fix-identifier` and `pbir-visual-edit-planner` (now deprecated).

---

### Validation Agents

#### `power-bi-verification`

**Purpose:** Validates proposed changes before implementation to ensure safety and correctness.

**Invocation:** After code fix identification phase.

**Inputs:**
- Problem statement
- Findings file path (with Sections 1 & 2 completed)
- Power BI project context

**What It Does:**
- Reviews proposed code changes for semantic correctness
- Designs DAX unit test queries
- Performs dependency analysis (data lineage)
- Assesses performance impact
- Identifies breaking changes
- Discovers data model structure for filter metadata

**Output:** Populates Section 3 (Test Cases and Impact Analysis) with:
- Test cases with filter metadata (YAML format for URL filtering)
- Verification verdict (Pass/Warning/Fail)
- Impact analysis
- Recommendations

**Critical Feature:** Includes filter metadata for automated browser-based testing.

---

#### `powerbi-tmdl-syntax-validator`

**Purpose:** Validates TMDL file formatting and structure after code changes are applied.

**Invocation:** After code implementation, BEFORE DAX validation.

**Inputs:**
- TMDL file path
- Context description (what was changed)
- Optional: specific objects modified

**What It Does:**
- Executes Python validator script (`.claude/tools/tmdl_format_validator.py`)
- Checks indentation consistency (tabs vs spaces)
- Validates property placement (formatString, displayFolder, etc.)
- Ensures properties are outside DAX expression blocks
- **Detects duplicate properties (TMDL013)** ⭐ NEW: Catches duplicate lineageTag/formatString/etc that cause Power BI Desktop loading failures
- Verifies TMDL structure and syntax

**Requirements:**
- Python 3.x installed
- No external dependencies

**Output:** Validation report with:
- Pass/fail verdict
- Line numbers for issues
- Remediation guidance
- Error codes (TMDL001-TMDL013)

**Critical Constraint:** Validates format only, NOT DAX logic.

**Error Codes:**
- TMDL001-TMDL004: Property and DAX indentation issues
- TMDL005-TMDL008: Partition source formatting (tabs/spaces)
- TMDL009-TMDL010: Field parameter syntax
- TMDL011: Mixed tabs/spaces (disabled)
- TMDL012: DAX at same indentation as properties
- **TMDL013: Duplicate property detected** ⭐ NEW: Catches duplicate lineageTag, formatString, displayFolder, annotation, etc. that cause Power BI Desktop to misinterpret properties as DAX code

**Validation Consolidation:**
All TMDL validation checks are consolidated into a single tool (`tmdl_format_validator.py`) for simplicity. Previous standalone validators (`tmdl_duplicate_property_validator.py`, `tmdl_measure_backticks_validator.py`) have been integrated or removed.

**Important Validation Lessons:**

⚠️ **TmdlSerializer vs Power BI Desktop Gap**: TmdlSerializer (Microsoft's authoritative parser) accepts multiple formatting styles as "valid TMDL," but Power BI Desktop has stricter loading requirements. A file that passes TmdlSerializer validation may still fail to load in Desktop. This is why TMDL013 duplicate property check and TMDL012 auto-fix were added.

⚠️ **TMDL012 Auto-Fix**: When TMDL012 warnings are detected (DAX at same indentation as properties), the validator automatically adds triple backticks to remove structural ambiguity. This follows Power BI best practices and prevents Desktop loading issues. Auto-fix is safe because it preserves DAX logic exactly while clarifying structure.

⚠️ **TMDL013 Blocks Auto-Fix**: If duplicate properties (TMDL013) are detected alongside TMDL012, auto-fix is blocked and reported as ERROR. Duplicate properties indicate deeper issues (merge conflicts, code generation errors) that require manual resolution.

⚠️ **Why No Backticks-Only Validator**: An earlier attempt to validate triple backticks usage was removed due to 86 false positives on a working project. Power BI Desktop accepts many indentation patterns. The real issue is **duplicate properties** (TMDL013), not missing backticks. TMDL012 warnings are now auto-fixed with backticks when safe to do so.

---

#### `powerbi-dax-review-agent`

**Purpose:** Validates DAX syntax and detects runtime errors after changes are applied but before deployment.

**Invocation:** After TMDL format validation, before deployment.

**Inputs:**
- Findings file path (with Section 2)
- Versioned project path

**What It Does:**
- Parses Section 2 to identify modified objects
- Extracts DAX code for ONLY modified objects
- Performs syntax validation (balanced parentheses, valid functions)
- Checks semantic issues (invalid references, circular dependencies)
- Analyzes runtime risks (division by zero, type mismatches)
- Verifies specification compliance

**Critical Constraint:** Reviews ONLY objects listed in Section 2 - does not scan entire project.

**Output:** Appends Section 2.5 (DAX Validation Report) with:
- Validation status (Pass/Warnings/Fail)
- Detailed findings for each modified object
- Critical issues requiring fixes
- Next steps based on verdict

---

### Creation Workflow Agents

#### `powerbi-artifact-decomposer`

**Purpose:** Analyzes complex creation requests and breaks them down into discrete artifacts with dependency relationships.

**Invocation:** After data model analysis, before data understanding phase.

**Inputs:**
- Findings file path (with Section 1.1 completed)
- Original creation request
- Artifact type parameter

**What It Does:**
- Parses natural language to identify primary artifact and dependencies
- Detects explicit references (mentions of specific measures, columns)
- Detects implicit dependencies (visual needs measures, YoY needs PY helper)
- Checks schema to determine which artifacts exist vs need creation
- Builds dependency graph
- Determines creation order (topological sort)
- Presents plan to user for confirmation

**Pattern Recognition:**
- KPI Card Pattern: Card visual + measures + optional targets
- YoY Growth Pattern: Main measure + helper measure + base measure
- Dashboard Pattern: Multiple visuals + supporting measures
- Trend Visual Pattern: Chart + measure + date validation

**Output:** Populates Section 1.0 (Artifact Breakdown Plan) with:
- List of artifacts to create
- Dependency graph
- Creation order with reasoning
- User confirmation status

---

#### `powerbi-data-understanding-agent`

**Purpose:** Builds complete artifact specifications through interactive Q&A with intelligent recommendations and data sampling.

**Invocation:** After artifact decomposition (or data model analysis for single artifacts).

**Inputs:**
- Findings file path (with Section 1.1 and optionally 1.0)
- Artifact type and description
- Workspace and dataset names (for data sampling)
- User responses to Q&A

**What It Does:**
- Makes intelligent recommendations based on schema and data analysis
- Samples actual data (if workspace/dataset provided) to validate assumptions
- Presents options with evidence and confidence levels (🟢 High, 🟡 Medium, 🔴 Low)
- Guides user through confirmations rather than open-ended questions
- Iterates until every specification aspect is confirmed
- Documents complete specification including styling decisions

**Recommendation Categories:**
- Data Source Selection (column selection, aggregation methods)
- Filtering Logic (categorical detection, value distribution)
- Date/Time Context (time intelligence approaches)
- Business Logic (calculation methods, edge cases)
- Styling & Formatting (format strings, display folders, descriptions)

**Requirements:**
- Valid Section 1.1 (Data Model Schema)
- Optional: Workspace/dataset for data sampling
- Optional: Authentication for XMLA queries

**Output:** Populates Section 1.2 (Data Understanding & Artifact Specification) with:
- Complete business requirement statement
- Data sources with treatment decisions
- Data validation results (if sampling performed)
- Complete business logic specification
- Styling & formatting decisions
- Confirmation trail

---

#### `powerbi-pattern-discovery`

**Purpose:** Finds existing similar artifacts and extracts patterns, naming conventions, and styling standards.

**Invocation:** After data understanding phase.

**Inputs:**
- Findings file path (with Sections 1.1 and 1.2)
- Project path
- Artifact type

**What It Does:**
- Analyzes Section 1.2 to understand what patterns to search for
- Searches TMDL files for similar artifacts
- Extracts naming conventions (prefixes, suffixes, casing)
- Identifies calculation patterns (time intelligence, variables, DIVIDE usage)
- Extracts styling patterns (format strings, display folders, descriptions)
- Documents design system patterns (for visuals)

**Pattern Types:**
- Time Intelligence: SAMEPERIODLASTYEAR, helper measure approaches
- Aggregation: Variable usage, error handling
- Division: DIVIDE vs IF patterns
- Styling: Currency/percentage formats, folder organization

**Output:** Populates Section 1.3 (Pattern Discovery) with:
- Similar artifacts found with code examples
- Naming conventions observed
- Calculation patterns documented
- Styling standards
- Recommendation summary

---

#### `powerbi-artifact-designer`

**Purpose:** Generates final DAX/M code and complete styling specifications based on validated specification and discovered patterns.

**Invocation:** After pattern discovery phase.

**Inputs:**
- Findings file path (with Sections 1.1-1.3 completed)
- Artifact type

**What It Does:**
- Reviews complete context from all specification phases
- Confirms final specification with user
- Finalizes styling decisions with recommendation-first approach
- Generates syntactically correct, optimized DAX/M code
- Follows discovered patterns for consistency
- Documents complete rationale and dependencies
- Outputs Section 2 in CREATE format

**Code Generation Principles:**
- Use variables for clarity and performance
- Apply discovered patterns from Section 1.3
- Handle edge cases (DIVIDE, ISBLANK, IFERROR)
- Optimize for performance
- Include inline comments for complex logic

**Output:** Populates Section 2 (Proposed Changes) with:
- Change Type: CREATE
- Target Location: Specific .tmdl file path
- Proposed Code: Complete DAX/M implementation
- Styling & Metadata: Format string, display folder, description
- Visual Formatting (if visual artifact)
- Change Rationale: Detailed explanation
- Dependencies: Required artifacts and relationships
- Validation Notes: Edge cases and performance considerations

---

### Implementation Agents

#### `powerbi-code-implementer-apply`

**Purpose:** Applies pre-defined code changes to Power BI projects with proper versioning and optional deployment.

**Invocation:** When user has an existing implementation plan and wants to apply changes.

**Inputs:**
- Findings file path
- Project path
- Optional: deployment environment
- Optional: user_action parameter

**What It Does:**
- Creates timestamped versioned copy of project
- Parses Section 2 for change items (CREATE or MODIFY)
- Handles multi-artifact creation with dependency validation
- Applies code changes using appropriate method:
  - **Creation Workflow**: Inserts new measures, columns, tables, visuals
  - **Modification Workflow**: Uses robust TMDL editor for DAX measures
- Validates TMDL indentation (2 tabs for properties)
- Optionally deploys to Power BI Service
- Supports both user authentication and service principal

**TMDL Indentation Requirements (CRITICAL):**
- TMDL uses TABS (`\t`), not spaces
- Measure properties must use EXACTLY 2 TABS
- Inconsistent indentation causes parsing errors

**Deployment Methods:**
- **User Authentication**: PowerShell cmdlets with Power BI login
- **Service Principal**: pbi-tools with Azure app registration

**Requirements:**
- Python 3.x (for robust TMDL editing)
- PowerShell + MicrosoftPowerBIMgmt module (for user auth deployment)
- pbi-tools CLI (for compilation and service principal deployment)

**Output:**
- Timestamped project copy: `<project>_YYYYMMDD_HHMMSS`
- Summary log of applied changes
- Deployment URL (if deployed)

---

#### `powerbi-visual-implementer-apply` 🆕

**Purpose:** Applies PBIR visual changes from Section 2.B by executing XML edit plans to modify visual.json files.

**Invocation:** After code changes are applied (if any), when Section 2.B contains visual modifications.

**Inputs:**
- Findings file path (with Section 2.B)
- Versioned project path (from code implementer or newly created)

**What It Does:**
- Parses XML edit plan from Section 2.B
- Executes operations using `pbir_visual_editor.py` Python utility
- Modifies visual.json files in .Report folder
- Supports two operation types:
  - **replace_property**: Modify top-level properties (x, y, width, height, visualType)
  - **config_edit**: Modify properties inside stringified config blob (title.text, colors, fonts)
- Validates JSON structure after modifications
- Logs all visual modifications

**Operation Types:**
```xml
<step file_path="..." operation="replace_property" json_path="width" new_value="500" />
<step file_path="..." operation="config_edit" json_path="title.text" new_value="'New Title'" />
```

**Requirements:**
- Python 3.x
- Power BI Project in .pbip format with .Report folder
- `pbir_visual_editor.py` utility in `.claude/tools/`

**Critical:** Runs AFTER code implementer in hybrid scenarios to ensure measures/columns exist before visual changes reference them.

**Output:**
- List of modified visuals with operation counts
- Validation status for each visual
- Error details (if any)

---

#### `powerbi-pbir-validator` 🆕

**Purpose:** Validates PBIR visual.json files after modifications but before deployment (parallel to `powerbi-dax-review-agent`).

**Invocation:** After visual implementer applies changes, as a quality gate before deployment.

**Inputs:**
- Findings file path (for Section 2.B)
- Versioned project path

**What It Does:**
- Parses Section 2.B to identify modified visuals
- For each modified visual.json:
  - Validates JSON structure
  - Verifies config string is valid JSON
  - Checks property types match schema
  - Validates position object (x, y, z, width, height, tabOrder)
  - Confirms modified properties have expected values
- Cross-references measure dependencies with Section 2.A (if applicable)
- Generates Section 2.6: PBIR Validation Report

**Validation Checks:**
- ✅ JSON syntax valid
- ✅ Config string parseable
- ✅ Required properties present
- ✅ Property data types correct
- ✅ Measure references valid
- ✅ Modified operations successful

**Outcomes:**
- **✅ PASS**: Ready for deployment
- **⚠️ WARNINGS**: Non-critical issues, user decides
- **❌ FAIL**: Critical errors, must fix before deployment

**Output:** Section 2.6 appended to findings.md with detailed validation report.

**Critical Constraint:** Validates ONLY modified visuals (from Section 2.B), not entire report.

---

### Merge Workflow Agents

#### `powerbi-compare-project-code`

**Purpose:** Technical Auditor - Identifies all technical differences between two Power BI projects.

**Invocation:** Automatically invoked by `/merge-powerbi-projects` command in Phase 2.

**Inputs:**
- `main_project_path`: Path to baseline project
- `comparison_project_path`: Path to project with changes

**What It Does:**
- Scans file structures for additions/deletions/modifications
- Parses TMDL format (`.tmdl` files in `definition/` folder)
- Parses BIM format (`model.bim` JSON)
- Parses `report.json` for visuals and pages
- Compares semantically (not just text diff):
  - Tables, measures, calculated columns, relationships
  - Report pages, visuals, filters
  - Data types, expressions, properties
- Generates unique diff ID for each atomic change

**Output Format:** JSON `DiffReport` with:
```json
{
  "diffs": [
    {
      "diff_id": "diff_001",
      "component_type": "Measure",
      "component_name": "Total Revenue",
      "file_path": "Project.SemanticModel/definition/tables/Sales.tmdl",
      "status": "Modified",
      "main_version_code": "SUM(Sales[Amount])",
      "comparison_version_code": "SUMX(Sales, Sales[Quantity] * Sales[Price])",
      "metadata": { "parent_table": "Sales" }
    }
  ],
  "summary": {
    "total_diffs": 1,
    "added": 0,
    "modified": 1,
    "deleted": 0,
    "breakdown": { "Measure": 1 }
  }
}
```

**Critical Constraint:** Reports facts only, no business interpretation.

---

#### `powerbi-code-understander`

**Purpose:** Business Analyst - Translates technical differences into business impact explanations.

**Invocation:** Automatically invoked by `/merge-powerbi-projects` command in Phase 3.

**Inputs:**
- `DiffReport` JSON from `powerbi-compare-project-code`

**What It Does:**
- Analyzes each technical diff using LLM reasoning
- Explains WHAT changed in plain English
- Explains WHY it matters to business users
- Assesses consequences of choosing each version:
  - Calculation accuracy
  - Performance impact
  - Breaking changes
  - Dependency effects
- Provides decision guidance
- Flags critical issues with ⚠️

**Output Format:** Enriched JSON `BusinessImpactReport`:
```json
{
  "diff_id": "diff_001",
  "component_type": "Measure",
  ...
  "business_impact": "This changes how Total Revenue is calculated.
  MAIN uses pre-calculated column (simple SUM), COMPARISON calculates
  dynamically (SUMX). Choose MAIN if Amount is official figure;
  choose COMPARISON for real-time calculation."
}
```

**Expertise Areas:**
- DAX context transition and filter context
- Time intelligence patterns
- Aggregation methods
- Visual configuration impact
- Model relationship implications

**Critical Constraint:** Provides analysis but never makes the decision for the user.

---

#### `powerbi-code-merger`

**Purpose:** Merge Surgeon - Executes user-approved merge decisions with precision.

**Invocation:** Automatically invoked by `/merge-powerbi-projects` command in Phase 6.

**Inputs:**
- `MergeManifest` JSON with user decisions
- `DiffReport` for reference
- Main and comparison project paths

**What It Does:**
- Creates new timestamped output folder
- Copies entire main project as base
- Iterates through user decisions:
  - **If "Main"**: Skip (already in base copy)
  - **If "Comparison"**: Apply change based on status:
    - **Modified**: Replace component in output
    - **Added**: Copy component to output
    - **Deleted**: Remove component from output
- Handles both TMDL and BIM formats
- Uses regex/JSON parsing for surgical edits
- Validates modified files
- Generates detailed log with timestamps

**File Operation Methods:**
- **TMDL**: Text-based regex replacement of component definitions
- **BIM**: JSON parsing and object replacement
- **Report JSON**: JSON parsing for visual/page updates
- **Files**: Direct file copy/delete

**Output Format:** JSON `MergeResult`:
```json
{
  "status": "success",
  "output_path": "C:/merged_20250128_143022.pbip",
  "merge_log": "[2025-01-28 14:30:22] MERGE INITIATED\n...",
  "statistics": {
    "total_decisions": 25,
    "main_chosen": 13,
    "comparison_chosen": 12,
    "files_modified": 8,
    "components_added": 2,
    "components_modified": 9,
    "components_deleted": 1,
    "errors": 0
  },
  "errors": []
}
```

**Error Handling:**
- **FileNotFound**: Log and skip
- **ParseError**: Log and skip
- **ComponentNotFound**: Attempt to add as new
- **CriticalError**: Abort merge

**Critical Constraints:**
- NEVER modifies original projects
- Atomic operations (all or nothing per component)
- Comprehensive logging of every action
- Preserves file formatting

---

### Testing Agents

#### `powerbi-playwright-tester`

**Purpose:** Performs automated quality assurance testing on deployed Power BI dashboards.

**Invocation:** After report deployment is complete and testing is required.

**Inputs:**
- Findings file path (or dedicated test document)
- Dashboard URL
- Optional: test plan location

**What It Does:**
- Reads encoding reference (`.claude/helpers/pbi-url-filter-encoder.md`)
- Parses test cases from findings.md Section 3 or dedicated test document
- Constructs filtered URLs using filter metadata (preferred method)
- Navigates to dashboard via Playwright MCP
- Executes test steps (URL filtering or DOM interaction fallback)
- Captures screenshots as evidence
- Visually verifies expected results using multimodal capabilities
- Generates comprehensive test results report

**Filtering Methods:**
- **URL-based filtering** (PRIMARY): Constructs Power BI filter URLs from YAML metadata
- **DOM interaction** (FALLBACK): Interacts with slicers when metadata unavailable

**Requirements:**
- Playwright MCP available
- Dashboard URL accessible
- Optional: Power BI credentials for authentication

**Output:** Creates `test-results/` folder with:
- `test_results.md`: Comprehensive test report
- `screenshots/`: Visual evidence for each test case

**Test Strategies:**
- Strategy A: findings.md with Section 3 (structured test cases)
- Strategy B: Dedicated test document (level-2 headings)
- Strategy C: Fallback (default visual verification)

---

## Workflow Integration

### Complete End-to-End Workflow

This system supports three primary workflows:

#### Workflow 1: Analyze → Implement → Deploy → Test (Existing Code Changes)

```
1. /evaluate-pbi-project-file
   ↓ Creates findings.md with Sections 1-3

2. User reviews findings.md
   ↓

3. /implement-deploy-test-pbi-project-file --findings <path> --deploy DEV
   ↓ Applies changes, validates, deploys, tests

4. Review test results in test-results/
```

**Agents Involved:**
1. `powerbi-verify-pbiproject-folder-setup` - Validates project
2. `powerbi-data-context-agent` - Retrieves actual data (optional)
3. **Classification** (orchestrator logic) - Determines change type (calc/visual/hybrid)
4. **Investigation Phase** (conditional parallel):
   - `powerbi-code-locator` - Finds existing code (Section 1.A)
   - `powerbi-visual-locator` - Finds visual state (Section 1.B, if visual changes)
5. `powerbi-dashboard-update-planner` - Designs coordinated changes (Section 2.A/2.B)
6. `power-bi-verification` - Validates proposed changes
7. **Implementation Phase** (conditional sequential):
   - `powerbi-code-implementer-apply` - Applies code changes (Section 2.A, if exists)
   - `powerbi-visual-implementer-apply` 🆕 - Applies visual changes (Section 2.B, if exists)
8. **Validation Phase** (conditional):
   - `powerbi-tmdl-syntax-validator` - Validates TMDL format (if code changes)
   - `powerbi-pbir-validator` 🆕 - Validates PBIR visual.json (if visual changes)
   - `powerbi-dax-review-agent` - Validates DAX logic (if code changes)
9. **Deployment & Testing** (optional):
   - Deployment to Power BI Service (PowerShell or pbi-tools)
   - `powerbi-playwright-tester` - Runs automated tests

**Key Enhancements:**
- Unified planner ensures calculation and visual changes are coordinated in hybrid scenarios
- Visual implementer applies PBIR changes via XML edit plans
- PBIR validator ensures visual.json integrity before deployment
- Conditional execution based on what's in Section 2 (code, visual, or both)

---

#### Workflow 2: Create → Implement → Deploy → Test (New Artifacts)

```
1. /create-pbi-artifact --project <path> --type measure --description "YoY Revenue Growth"
   ↓ Creates findings.md with Sections 1.0-1.3 and Section 2 (CREATE format)

2. User reviews specification in findings.md
   ↓

3. /implement-deploy-test-pbi-project-file --findings <path> --deploy DEV
   ↓ Creates artifacts, validates, deploys, tests

4. Review test results in test-results/
```

**Agents Involved:**
1. `powerbi-verify-pbiproject-folder-setup` - Validates project
2. `powerbi-data-model-analyzer` - Extracts schema
3. `powerbi-artifact-decomposer` - Breaks down complex requests
4. `powerbi-data-understanding-agent` - Builds specification
5. `powerbi-pattern-discovery` - Finds existing patterns
6. `powerbi-artifact-designer` - Generates code
7. `powerbi-code-implementer-apply` - Applies changes
8. `powerbi-tmdl-syntax-validator` - Validates format
9. `powerbi-dax-review-agent` - Validates DAX
10. `powerbi-playwright-tester` - Tests deployment

---

#### Workflow 3: Compare → Decide → Merge (Project Merging)

```
1. /merge-powerbi-projects --main <path-A> --comparison <path-B>
   ↓ Compares projects and identifies differences

2. Agent 1: Technical Comparison
   ↓ Creates DiffReport.json with all technical differences

3. Agent 2: Business Impact Analysis
   ↓ Enriches report with business explanations

4. User reviews combined analysis and makes decisions
   ↓ Responds with: "diff_001: Comparison, diff_002: Main, ..."

5. Agent 3: Execute Merge
   ↓ Creates new merged project based on user decisions

6. Review merge log and test merged project in Power BI Desktop
```

**Agents Involved:**
1. `powerbi-compare-project-code` - Technical Auditor (finds differences)
2. `powerbi-code-understander` - Business Analyst (explains impact)
3. `powerbi-code-merger` - Merge Surgeon (executes merge)

**Key Characteristics:**
- **Non-destructive**: Original projects never modified
- **Human-in-the-loop**: User makes all final decisions
- **Format agnostic**: Supports TMDL and BIM formats
- **Comprehensive**: Compares measures, tables, visuals, relationships, etc.
- **Timestamped output**: Easy to track and rollback

**Use Cases:**
- Merging development and production versions
- Adopting selective changes from a colleague's project
- Consolidating multiple project branches
- Reviewing and integrating external changes
- **Focused merges with `--description`**:
  - "Only merge revenue calculation changes" → Filters to revenue-related measures
  - "Update date table logic only" → Shows only date/time intelligence changes
  - "Customer analysis updates" → Filters to customer-related tables, measures, visuals

**Documentation:**
- [Technical Reference](.claude/tools/README_MERGE_WORKFLOW.md)
- [User Quick Start](.claude/tools/MERGE_QUICK_START.md)
- [Workflow Diagrams](.claude/tools/MERGE_WORKFLOW_DIAGRAM.md)
- [Implementation Details](../AGENT_MERGE_WORKFLOW_IMPLEMENTATION.md)

---

### Agent Orchestration Principles

1. **Sequential Execution**: Agents run in a specific order with clear dependencies
2. **Findings File as State**: All agents read/write to findings.md for coordination
3. **Stateless Agents**: Each agent is autonomous and can be re-run independently
4. **Quality Gates**: Validation agents act as gates before proceeding to next phase
5. **User Interaction**: Commands handle all user prompts; agents only document status
6. **Authentication Handling**: Pre-flight checks prevent mid-workflow auth failures

---

### Key Files and Directories

```
.claude/
├── commands/                        # Slash command definitions
│   ├── create-pbi-artifact.md
│   ├── evaluate-pbi-project-file.md
│   ├── implement-deploy-test-pbi-project-file.md
│   └── merge-powerbi-projects.md
├── agents/                          # Agent definitions
│   ├── powerbi-verify-pbiproject-folder-setup.md
│   ├── powerbi-data-model-analyzer.md
│   ├── powerbi-artifact-decomposer.md
│   ├── powerbi-data-understanding-agent.md
│   ├── powerbi-pattern-discovery.md
│   ├── powerbi-artifact-designer.md
│   ├── powerbi-data-context-agent.md
│   ├── powerbi-code-locator.md
│   ├── powerbi-code-fix-identifier.md
│   ├── power-bi-verification.md
│   ├── powerbi-code-implementer-apply.md
│   ├── powerbi-tmdl-syntax-validator.md
│   ├── powerbi-dax-review-agent.md
│   ├── powerbi-playwright-tester.md
│   ├── powerbi-compare-project-code.md
│   ├── powerbi-code-understander.md
│   └── powerbi-code-merger.md
├── tools/                           # Utility scripts
│   ├── tmdl_format_validator.py
│   ├── README_TMDL_VALIDATOR.md
│   ├── pbi_merger_utils.py
│   ├── pbi_merger_schemas.json
│   ├── README_MERGE_WORKFLOW.md
│   ├── MERGE_QUICK_START.md
│   └── MERGE_WORKFLOW_DIAGRAM.md
└── helpers/                         # Reference documentation
    └── pbi-url-filter-encoder.md

agent_scratchpads/                   # Created by commands
└── <timestamp>-<problem-name>/
    ├── findings.md                  # Main analysis document
    └── test-results/                # Created by testing agent
        ├── test_results.md
        └── screenshots/
```

---

## Authentication and Prerequisites

### For Data Sampling (Optional)
- Power BI workspace and dataset names
- Authentication via device code flow
- XMLA endpoint access

### For Code Implementation (Always Required)
- Python 3.x installed
- Robust TMDL editor scripts
- Write access to project folder

### For Deployment (Optional)

**User Authentication (Recommended):**
- Power BI PowerShell module (`MicrosoftPowerBIMgmt`)
- pbi-tools CLI (for compilation)
- Active Power BI login
- Contributor/Admin role on target workspace

**Service Principal (CI/CD):**
- pbi-tools CLI
- Azure Service Principal configured
- `PBI_CLIENT_SECRET` environment variable
- Service principal authorized in tenant
- Service principal added to workspace

### For Testing (Optional)
- Playwright MCP available
- Dashboard URL accessible
- Power BI credentials (if required)

---

## Error Handling and Quality Gates

### Quality Gates in Implementation Workflow

1. **TMDL Format Validation** (Phase 2.5)
   - Checks indentation, property placement
   - Must PASS before DAX validation
   - Quick validation (seconds)

2. **DAX Validation** (Phase 3)
   - Validates syntax and semantics
   - Possible outcomes: PASS, WARNINGS, FAIL
   - If FAIL: Must fix and re-run from Phase 2

3. **Deployment** (Phase 4)
   - Only runs if validation passed
   - Supports rollback if needed

4. **Testing** (Phase 5)
   - Only runs if deployment succeeded
   - Non-critical failures documented

### Error Recovery

- **Original project never modified**: All work done on versioned copies
- **Timestamped folders**: Easy to identify and rollback
- **Iterative refinement**: Fix → Re-validate → Deploy cycle
- **Comprehensive logging**: Every step documented

---

## Best Practices

1. **Always provide workspace/dataset** for data sampling when possible - improves recommendation quality
2. **Review Section 1.2 carefully** - this is your specification before code generation
3. **Leverage existing patterns** from Section 1.3 for consistency
4. **Document styling decisions** early in the process
5. **Use URL filtering** in test cases via filter metadata (not DOM interaction)
6. **Validate early and often** - format validation before DAX validation
7. **Preserve versioned copies** for audit trails and debugging
8. **Authenticate upfront** - handle auth before agent execution to avoid timeouts

---

## Troubleshooting

### Common Issues

**Issue: "TMDL file cannot be opened in Power BI Desktop"**
- Run TMDL format validator
- Check property indentation (must be 2 tabs)
- Verify properties are outside DAX expressions

**Issue: "Data context agent returns auth_required"**
- Run pre-flight authentication check
- Complete device code flow
- Verify token validity

**Issue: "pbi-tools not found"**
- Install pbi-tools CLI
- Add to system PATH
- Verify with `pbi-tools --version`

**Issue: "Deployment fails with insufficient permissions"**
- Verify Contributor/Admin role on workspace
- Check service principal authorization (if using SP)
- Confirm PBI_CLIENT_SECRET is set (if using SP)

**Issue: "Test cases cannot apply filters"**
- Add filter metadata YAML blocks to test cases
- Use URL filtering instead of DOM interaction
- Verify table/column names match TMDL definitions

---

## Contributing

When adding new agents or commands:
1. Follow existing naming conventions
2. Document inputs, outputs, and requirements
3. Specify invocation patterns and dependencies
4. Include error handling guidelines
5. Update this README with integration points

---

## Version History

- **Initial Release**: Core evaluation and implementation workflows
- **Create Workflow**: Added artifact creation with multi-artifact support
- **Testing Enhancement**: URL-based filtering for reliable automated testing
- **Validation Gates**: TMDL format and DAX validation as quality gates

---

## Support and Documentation

For detailed documentation on specific agents or commands, see the individual markdown files in [.claude/commands/](.claude/commands/) and [.claude/agents/](.claude/agents/).

For issues or questions, refer to the Power BI Analyst Agent project documentation.
