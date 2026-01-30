# Power BI Analyst Tools

This directory contains specialized tools used by the Power BI analyst agent system. These tools provide core functionality for TMDL validation, visual editing, project merging, and data extraction.

## Table of Contents

- [Core Python Tools](#core-python-tools)
  - [Project Validation](#project-validation)
  - [TMDL Validation](#tmdl-validation)
  - [Visual Editing](#visual-editing)
  - [Project Merging](#project-merging)
  - [Data Extraction](#data-extraction)
- [C# Validator](#c-validator)
- [Build Utilities](#build-utilities)
- [Schema Definitions](#schema-definitions)
- [Documentation](#documentation)
- [Archive Policy](#archive-policy)

---

## Core Python Tools

### Project Validation

#### `pbi_project_validator.py`

Lightweight script to validate Power BI project folder structures and detect project format types.

**Purpose:**
- Detect project format (Power BI Project .pbip, pbi-tools, PBIX file)
- Validate folder structure and required files exist
- Check visual change compatibility (requires .Report folder)
- Return structured JSON for programmatic use
- Replaces multiple bash/find commands with single efficient execution

**Command-Line Usage:**
```bash
python pbi_project_validator.py <project_path> [--visual-changes] [--json]
```

**Examples:**
```bash
# Validate a Power BI Project (human-readable output)
python pbi_project_validator.py "C:\Projects\SalesReport"

# Validate with visual changes expected
python pbi_project_validator.py "C:\Projects\SalesReport" --visual-changes

# Get JSON output for programmatic use
python pbi_project_validator.py "C:\Projects\SalesReport" --json
```

**Options:**
- `--visual-changes` - Flag indicating visual property changes are expected (requires .Report folder)
- `--json` - Output results as JSON instead of human-readable format

**Exit Codes:**
- `0` - Validation passed (status: validated)
- `1` - Action required (status: action_required) - e.g., PBIX needs extraction
- `2` - Validation error (status: error)
- `3` - Script error (invalid arguments)

**JSON Output Structure:**
```json
{
  "status": "validated|action_required|error",
  "format": "pbip|pbi-tools|pbix|invalid",
  "action_type": "pbix_extraction|invalid_format|report_folder_missing|...",
  "validated_project_path": "...",
  "requires_compilation": true|false,
  "semantic_model_path": "...",
  "report_path": "...",
  "tmdl_files_found": ["model.tmdl", "tables/", ...],
  "report_files_found": ["report.json", "pages/", ...]
}
```

**Supported Formats:**
1. **Power BI Project (.pbip)**: Folder with `*.pbip` file and `*.SemanticModel/` folder
2. **pbi-tools Format**: Folder with `.pbixproj.json` and `Model/` folder
3. **PBIX File**: Compiled binary requiring extraction (returns action_required)

**Used By:**
- `powerbi-verify-pbiproject-folder-setup` agent
- `/evaluate-pbi-project-file` command
- `/create-pbi-artifact-spec` command
- `/summarize-pbi-dashboard` command

**Efficiency Note:**
This script reduces token usage by 75-80% compared to LLM-based file existence checks. A single Python execution replaces 5-8 sequential bash commands with LLM reasoning.

---

### TMDL Validation

#### `tmdl_format_validator.py`

Lightweight standalone validator for TMDL (Tabular Model Definition Language) file formatting and structure.

**Purpose:**
- Validates TMDL syntax, indentation, and property placement
- Detects 13 types of formatting errors (TMDL001-TMDL013)
- Auto-fixes ambiguous DAX blocks (TMDL012)
- Optionally runs authoritative C# TmdlSerializer validation
- No external dependencies required (Python-only mode)

**Command-Line Usage:**
```bash
python tmdl_format_validator.py <tmdl_file_path> [--context "description of changes"] [--authoritative]
```

**Examples:**
```bash
# Basic format validation
python tmdl_format_validator.py "C:\project\MyModel.SemanticModel\definition\tables\Sales.tmdl"

# With context description
python tmdl_format_validator.py "Sales.tmdl" --context "Added YoY growth measure"

# With authoritative C# validation
python tmdl_format_validator.py "Sales.tmdl" --authoritative
```

**Options:**
- `--context 'text'` - Add context description to report
- `--authoritative` - Run C# TmdlSerializer validation (requires .SemanticModel folder)

**Exit Codes:**
- `0` - All validations passed
- `1` - Validation errors found
- `2` - File not found or read error

**Validation Checks:**
- TMDL001-TMDL004: Property and DAX indentation issues
- TMDL005-TMDL008: Partition source formatting (tabs/spaces)
- TMDL009-TMDL010: Field parameter syntax
- TMDL011: Mixed tabs/spaces (disabled)
- TMDL012: DAX at same indentation as properties (auto-fixed with backticks)
- TMDL013: Duplicate property detection (blocks auto-fix)

**Used By:**
- `powerbi-tmdl-syntax-validator` agent
- `powerbi-code-implementer-apply` agent
- `/implement-deploy-test-pbi-project-file` command
- `/merge-powerbi-projects` command

**Documentation:** [docs/TMDL_DOCUMENTATION.md](docs/TMDL_DOCUMENTATION.md)

---

#### `tmdl_measure_replacer.py`

Robust, measure-level replacement tool for DAX code in TMDL files with proper tab indentation handling.

**Purpose:**
- Solves whitespace complexity when programmatically editing TMDL files
- Finds measures by name (not exact text matching)
- Preserves TMDL properties (formatString, displayFolder, lineageTag)
- Handles tab indentation correctly

**Command-Line Usage:**
```bash
python tmdl_measure_replacer.py <tmdl_file> <measure_name> <new_dax_file>
```

**Example:**
```bash
python tmdl_measure_replacer.py "Commissions_Measures.tmdl" "Total Sales" "new_dax.txt"
```

**Arguments:**
- `tmdl_file`: Path to the TMDL file containing the measure
- `measure_name`: Exact name of the measure (without quotes)
- `new_dax_file`: Path to file containing new DAX body code

**Key Features:**
- Regex-based measure extraction by name
- Preserves measure properties after DAX block
- Auto-indents new code to match TMDL structure
- Tab-aware processing (explicit `\t` handling)

**Used By:**
- Manual editing scenarios
- Custom automation scripts

**Documentation:** [docs/TMDL_DOCUMENTATION.md](docs/TMDL_DOCUMENTATION.md)

---

### Visual Editing

#### `pbir_visual_editor.py`

XML edit plan executor for Power BI Report (PBIR) visual.json files.

**Purpose:**
- Execute structured edit plans on visual.json files
- Modify visual properties (position, size, type)
- Edit stringified config properties (titles, formatting)
- Supports type-safe value parsing

**Command-Line Usage:**
```bash
python pbir_visual_editor.py <edit_plan.xml> <base_path>
```

**Example:**
```bash
python pbir_visual_editor.py "visual_changes.xml" "C:\MyProject.Report"
```

**XML Edit Plan Format:**
```xml
<edit_plan>
  <step
    file_path="definition/pages/Page1/visuals/Visual1/visual.json"
    operation="replace_property"
    json_path="width"
    new_value="500"
  />
  <step
    file_path="definition/pages/Page1/visuals/Visual1/visual.json"
    operation="config_edit"
    json_path="title.text"
    new_value="'Regional Performance'"
  />
</edit_plan>
```

**Operations:**
1. `replace_property`: Modify top-level visual.json properties (x, y, width, height, visualType)
2. `config_edit`: Modify properties inside the stringified config blob

**Value Parsing:**
- Numbers: `500` → 500 (int), `3.14` → 3.14 (float)
- Booleans: `true` → True, `false` → False
- Strings: `'text'` or `"text"` → "text"
- Null: `null` → None

**Used By:**
- `powerbi-visual-implementer-apply` agent
- `/implement-deploy-test-pbi-project-file` command (visual changes)

**Key Features:**
- Nested JSON path navigation with array indexing
- Stringified config blob parsing/re-stringification
- Type-safe value conversion
- UTF-8 encoding support for emoji characters

---

#### `extract_visual_layout.py`

Extracts and analyzes visual layout data from Power BI Report (.Report) pages.

**Purpose:**
- Read visual.json files from PBIR pages
- Generate detailed layout reports
- Show visual positions, sizes, types, and data fields
- List available pages in a report

**Command-Line Usage:**
```bash
# List available pages
python extract_visual_layout.py <report_path> --list-pages

# Analyze specific page
python extract_visual_layout.py <report_path> <page_id> [--output <file>] [--json]
```

**Examples:**
```bash
# List pages
python extract_visual_layout.py "PSSR Commissions.Report" --list-pages

# Analyze page and save to file
python extract_visual_layout.py "PSSR Commissions.Report" "feaad185bc0ca0d442fb" --output layout.txt

# Get JSON output
python extract_visual_layout.py "PSSR Commissions.Report" "feaad185bc0ca0d442fb" --json
```

**Output Information:**
- Visual container ID and name
- Position (x, y) and size (width, height)
- Z-order and tab order
- Visual type (e.g., card, clusteredBarChart)
- Data fields used by the visual
- Title and formatting properties

**Used By:**
- Manual analysis and documentation
- Visual discovery workflows

---

### Project Merging

#### `pbi_merger_utils.py`

Utility functions for comparing and merging Power BI projects (.pbip).

**Purpose:**
- Parse TMDL and model.bim files
- Extract measures, columns, tables, relationships
- Perform project-level comparisons
- Support selective merging operations

**Key Classes:**

**`TmdlParser`**
- `extract_measures(tmdl_content)`: Extract all measures from TMDL
- `extract_columns(tmdl_content)`: Extract all columns from TMDL
- `extract_table_name(tmdl_content)`: Get table name
- `replace_measure(tmdl_content, measure_name, new_definition)`: Replace measure
- `replace_column(tmdl_content, column_name, new_definition)`: Replace column

**`BimParser`**
- `load_bim(file_path)`: Load and parse model.bim JSON file
- Methods for extracting model objects from BIM format

**`ProjectComparer`**
- Compare two Power BI projects
- Identify differences in measures, columns, tables
- Generate detailed diff reports

**`ProjectMerger`**
- Merge changes from one project to another
- Selective merge based on user decisions
- Preserve formatting and structure

**Used By:**
- `powerbi-compare-project-code` agent
- `powerbi-code-understander` agent
- `powerbi-code-merger` agent
- `/merge-powerbi-projects` command

**Documentation:** [docs/MERGE_WORKFLOW.md](docs/MERGE_WORKFLOW.md)

---

### Data Extraction

(No standalone tools currently - data extraction is handled by agents using XMLA/Power BI APIs)

---

## C# Validator

### TmdlValidator

A C# command-line tool that validates TMDL projects using Microsoft's official `TmdlSerializer` parser.

**Location:** `TmdlValidator/` subdirectory with executable at root: `TmdlValidator.exe`

**Purpose:**
- 100% accurate validation identical to Power BI Desktop
- Catches ALL syntax and semantic errors
- Provides detailed error reporting with exact file path, line number, and line text
- No false positives or false negatives

**Building:**
```powershell
cd TmdlValidator
.\build.ps1
```

**Command-Line Usage:**
```bash
# Basic validation
TmdlValidator.exe "C:\path\to\MyProject.SemanticModel"

# JSON output (for programmatic use)
TmdlValidator.exe --path "C:\path\to\MyProject.SemanticModel" --json
```

**Exit Codes:**
- `0` - Validation successful (TMDL is valid)
- `1` - Validation failed (TMDL has errors)

**Error Types:**
- `FormatError`: TMDL syntax/format error (invalid keywords, indentation, structure)
- `SerializationError`: Valid TMDL syntax but invalid metadata logic
- `PathNotFound`: Specified path does not exist
- `InvalidStructure`: Path exists but is not a valid TMDL project
- `DirectoryNotFound`: Required directory not found
- `UnexpectedError`: Unexpected exception occurred

**Advantages Over Regex Validation:**

| Aspect | Regex Validator | TmdlValidator (C#) |
|--------|----------------|-------------------|
| Accuracy | Pattern matching - misses edge cases | 100% accurate - same parser as Power BI |
| Coverage | Limited to known patterns | Catches ALL syntax and semantic errors |
| Alignment | Guesses at TMDL rules | Identical to Power BI Desktop |
| Maintenance | Requires updating for new patterns | Auto-updated with library |
| False Positives | Possible | None - only real errors |
| False Negatives | Possible | None - catches everything |

**Technical Details:**
- Framework: .NET 8.0
- Parser: `Microsoft.AnalysisServices.Tabular.TmdlSerializer`
- Package: `Microsoft.AnalysisServices.NetCore.retail.amd64` v19.84.2
- Build Type: Self-contained single-file executable (~90MB)
- Platform: Windows x64

**Used By:**
- `powerbi-tmdl-syntax-validator` agent (authoritative validation step)
- `tmdl_format_validator.py` (when `--authoritative` flag is used)
- `/merge-powerbi-projects` command (quality gate)

**Documentation:** [TmdlValidator/README.md](TmdlValidator/README.md), [TmdlValidator/INSTALL.md](TmdlValidator/INSTALL.md)

---

## Build Utilities

.NET SDK installation scripts are located in the `TmdlValidator/` subdirectory:
- **TmdlValidator/install_dotnet.ps1** - Advanced installer with registry/PATH detection
- **TmdlValidator/install_dotnet_simple.ps1** - Simplified installer for most environments

These scripts are used one-time during initial setup to install .NET 8.0 SDK for building the C# validator.

**See:** [TmdlValidator/INSTALL.md](TmdlValidator/INSTALL.md) for complete setup instructions

---

## Schema Definitions

### `pbi_merger_schemas.json`

JSON schema definitions for merge workflow outputs.

**Schemas Defined:**
1. `DiffReport`: Technical comparison output from `powerbi-compare-project-code`
2. `BusinessImpactReport`: Business analysis output from `powerbi-code-understander`
3. `MergeManifest`: User decisions and merge instructions
4. `MergeResult`: Merge execution results from `powerbi-code-merger`

**Used By:**
- `/merge-powerbi-projects` command
- Merge workflow agents for structured data exchange

---

## Documentation

### Core Documentation Files

- **[docs/MERGE_WORKFLOW.md](docs/MERGE_WORKFLOW.md)** - Complete merge workflow documentation including quick start guide, technical architecture, and visual diagrams
- **[docs/TMDL_DOCUMENTATION.md](docs/TMDL_DOCUMENTATION.md)** - Complete TMDL tool documentation including validator usage, two-tier validation system, and measure replacer guide

### TmdlValidator Documentation

Located in `TmdlValidator/` subdirectory:
- **[TmdlValidator/README.md](TmdlValidator/README.md)** - Complete C# validator documentation
- **[TmdlValidator/INSTALL.md](TmdlValidator/INSTALL.md)** - Installation and build instructions

---

## Archive Policy

Per project guidelines in [../CLAUDE.md](../CLAUDE.md), tools should be evaluated for archival based on:

1. **Problem-Specific Tools**: Scripts created for specific dashboard problems should remain in scratchpad folders (`agent_scratchpads/<timestamp>-<problem-name>/`) rather than being promoted to `.claude/tools/`

2. **Superseded Tools**: Tools that have been replaced by better implementations should be moved to `archive/`

3. **Consolidation Principle**: Prefer consolidating related functionality into comprehensive tools rather than maintaining many specialized standalone files

### Files Recommended for Archive

The following files have been moved to `.claude/tools/archive/`:

**Problem-Specific Scripts (`archive/problem-specific/`):**
- `fix_dax_measures.py` - Hardcoded to fix specific OR() syntax error in specific measures
- `fix_misc_gp.py` - Hardcoded fixes for "Sales Commission GP Actual NEW" measure
- `temp_dax_update.py` - Temporary DAX update script

**Superseded Tools (`archive/superseded/`):**
- `robust_tmdl_editor.py` - Superseded by `tmdl_measure_replacer.py` (nearly identical functionality)

**Ad-Hoc Scripts (`archive/adhoc/`):**
- `document_all_visuals.py` - Ad-hoc visual documentation script (version 1)
- `document_all_visuals_v2.py` - Ad-hoc visual documentation script (version 2)

### Archive Structure

```
.claude/tools/archive/
├── problem-specific/
│   ├── fix_dax_measures.py
│   ├── fix_misc_gp.py
│   └── temp_dax_update.py
├── superseded/
│   └── robust_tmdl_editor.py
└── adhoc/
    ├── document_all_visuals.py
    └── document_all_visuals_v2.py
```

---

## Tool Consolidation Guidelines

Before creating new tools in this directory:

1. **Evaluate Integration**: Can the functionality be added to an existing tool?
2. **Assess Reusability**: Is this for a specific problem or broad use cases?
3. **Check Documentation**: Should this be documented in .claude/README.md or kept in scratchpad?
4. **Consider Consolidation**: Would this create overlapping functionality?

**Example of Good Consolidation:**
TMDL validation checks TMDL001-TMDL013 are all consolidated into `tmdl_format_validator.py` rather than 13 separate validator files.

**Example of Appropriate Separation:**
`pbir_visual_editor.py` and `extract_visual_layout.py` remain separate because they serve different purposes (editing vs analysis).

---

## Version History

**2025-12-16:** Added `pbi_project_validator.py` for efficient project folder structure validation

**2025-11-18:** Initial README.md created consolidating tool documentation; 6 files archived

**2025-11-10:** TMDL013 duplicate property detection added to `tmdl_format_validator.py`

**2025-11-06:** TmdlValidator C# tool built and integrated

**2025-11-05:** PBIR visual editor created for visual.json manipulation

**2025-10-28:** Merge workflow tools and documentation completed

**2025-10-10:** TMDL measure replacer and format validator created
