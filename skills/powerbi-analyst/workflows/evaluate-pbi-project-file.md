---
name: evaluate-pbi-project-file
description: Analyze and evaluate Power BI project changes by creating a comprehensive analyst findings report through interactive problem clarification and automated agent analysis
pattern: ^/evaluate-pbi-project-file\s+(.+)$
---

# Evaluate Power BI Project File

This slash command creates a comprehensive analyst findings report for Power BI project changes by:
1. Interactively clarifying the problem statement with the user
2. Creating a structured scratchpad workspace
3. Orchestrating specialized agents to locate, implement, and verify proposed changes

## Tracing Output (Required)

**IMPORTANT:** This workflow MUST output trace markers for visibility. See `resources/tracing-conventions.md` for full format.

**On workflow start, output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 WORKFLOW: evaluate-pbi-project-file
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
✅ WORKFLOW COMPLETE: evaluate-pbi-project-file
   └─ Output: [findings file path]
   └─ Next: [suggested next step]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Usage

```bash
/evaluate-pbi-project-file --project <path-to-pbip-folder> [--image <path-to-image>] --description "<problem description>" [--workspace <workspace-name>] [--dataset <dataset-name>]
```

### Parameters

- `--project` (required): Path to the Power BI Project folder (the folder containing the .pbip file structure)
- `--image` (optional): Path to an image file that provides visual context for the problem
- `--description` (required): Description of the issue or update needed
- `--workspace` (optional): Power BI workspace name for XMLA data retrieval. If provided, the data context agent will query actual data from the semantic model
- `--dataset` (optional): Power BI dataset/semantic model name for XMLA data retrieval. Required if `--workspace` is provided

### Examples

```bash
# Basic usage without data retrieval (code-only analysis)
/evaluate-pbi-project-file --project "C:\Projects\SalesReport" --description "Update the Total Sales measure to exclude returns and apply a 5% discount"

# With screenshot for visual context
/evaluate-pbi-project-file --project "./MyReport" --image "./screenshots/current-bug.png" --description "The Year-over-Year Growth measure is showing incorrect values in Q4"

# With data context retrieval (recommended for data issues)
/evaluate-pbi-project-file --project "C:\Reports\FinanceDashboard.Report" --workspace "Sales Analytics" --dataset "Sales Report Model" --description "Invoice P3495801 is not showing up for sales rep Loy Baldwin"
```

## Workflow

### Phase 1: Project Validation & Setup

This phase validates the Power BI project structure and handles format conversion if needed, using the `powerbi-verify-pbiproject-folder-setup` agent.

**Step 1: Parse Arguments and Create Workspace**

1. Parse command arguments:
   - `--project`: Project path (required)
   - `--description`: Problem description (required)
   - `--image`: Image path (optional)
   - `--workspace`: Power BI workspace name (optional)
   - `--dataset`: Dataset name (optional)

2. Generate timestamp: `YYYYMMDD-HHMMSS` format

3. Create distilled problem name from description (kebab-case, ~30-40 chars)

4. Create scratchpad folder: `agent_scratchpads/<timestamp>-<distilled-name>/`

5. Create empty findings.md file with Problem Statement header

**Step 1.5: Analyze Problem Description for Visual Changes**

Parse the `--description` parameter to detect if visual changes are expected:

1. **Define Visual Change Keywords**:
   - Layout keywords: "move", "resize", "reposition", "position", "coordinates", "x", "y", "width", "height"
   - Formatting keywords: "color", "font", "title", "label", "format", "style", "theme"
   - Visual type keywords: "chart", "visual", "graph", "table visual", "card", "slicer"
   - Property keywords: "axis", "legend", "data labels", "tooltip"

2. **Check for Visual Keywords**:
   ```python
   visual_keywords = ["move", "resize", "reposition", "position", "coordinates",
                      "color", "font", "title", "label", "axis", "legend",
                      "chart", "visual", "graph", "card", "layout"]

   description_lower = description.lower()
   visual_changes_expected = any(keyword in description_lower for keyword in visual_keywords)
   ```

3. **Set Flag**:
   - If any visual keywords found: `visual_changes_expected = true`
   - Otherwise: `visual_changes_expected = false`

4. **Context Note**: This flag will be passed to the verification agent to ensure PBIR structure validation

**Step 2: Invoke Verification Agent (Initial)**

Invoke the `powerbi-verify-pbiproject-folder-setup` agent:
```
project_path: <from --project argument>
findings_file_path: <scratchpad-path>/findings.md
user_action: none
visual_changes_expected: <true/false from Step 1.5>
```

**Step 3: Read Prerequisites Section**

After agent returns, read the Prerequisites section from findings.md and parse these fields:
- `Status`: One of `validated`, `action_required`, `error`
- `Action Type`: Specific action type (e.g., `pbix_extraction`, `invalid_format`)
- `validated_project_path`: Path to use for analysis (if status=validated)
- `format`: Project format type (if status=validated)
- `requires_compilation`: Boolean (if status=validated)
- `Required Action`: Description (if status=action_required)
- `User Choices Available`: Options (if status=action_required)
- `Error Message`: Error description (if status=error)

**Step 4: Branch Based on Status**

**If Status = validated:**
- Extract `validated_project_path` from Prerequisites
- Display success message:
  ```
  ✅ Project validated successfully
  Format: <format>
  Path: <validated_project_path>
  ```
- Continue to Phase 2 (problem clarification)

**If Status = action_required:**
- Check `Action Type` field:

  **If Action Type = pbix_extraction:**
  Display prominent warning to user:
  ```
  ╔═══════════════════════════════════════════════════════════════════════════╗
  ║  ⚠️  PBIX FILE DETECTED - LIMITED ANALYSIS MODE                           ║
  ╠═══════════════════════════════════════════════════════════════════════════╣
  ║                                                                           ║
  ║  You've pointed to a .pbix file. This binary format significantly limits  ║
  ║  what can be analyzed:                                                    ║
  ║                                                                           ║
  ║    PBIX (your format)              PBIP (recommended)                     ║
  ║    ─────────────────────           ─────────────────────                  ║
  ║    [--] M code/Power Query         [OK] M code/Power Query                ║
  ║    [--] Data lineage               [OK] Data lineage                      ║
  ║    [--] Table schemas              [OK] Table schemas                     ║
  ║    [--] Visual editing (PBIR)      [OK] Visual editing (PBIR)             ║
  ║    [OK] DAX measures (after extraction)                                   ║
  ║                                                                           ║
  ║  STRONGLY RECOMMENDED: Convert to PBIP format for full analysis.         ║
  ║                                                                           ║
  ╚═══════════════════════════════════════════════════════════════════════════╝

  CONVERSION OPTION (Recommended):
  ────────────────────────────────
  1. Open this file in Power BI Desktop
  2. File → Save As → Power BI Project (.pbip)
  3. Re-run this command with the .pbip folder path

  EXTRACTION OPTION (DAX-only analysis):
  ──────────────────────────────────────
  If you must proceed with limited analysis:

  [Y] Extract with pbi-tools (DAX measures only)
  [N] Show me manual extraction instructions
  [I] Help me install pbi-tools first
  [C] I'll convert to PBIP and come back (recommended)

  Choose an option:
  ```

  **User selects [Y]:**
  1. Check if pbi-tools is available:
     ```bash
     where pbi-tools  # Windows
     which pbi-tools  # Linux/Mac
     ```

  2. **If pbi-tools found:**
     - Display: `✓ pbi-tools found at: <path>`
     - Display: `📦 Extracting PBIX file...`
     - Re-invoke verification agent:
       ```
       project_path: <pbix-file-path>
       findings_file_path: <scratchpad-path>/findings.md
       user_action: extract_with_pbitools
       visual_changes_expected: <true/false from Step 1.5>
       ```
     - After agent returns, go back to Step 3 (Read Prerequisites)

  3. **If pbi-tools NOT found:**
     - Display: `❌ pbi-tools not found in system PATH`
     - Re-display prompt with only [N] and [I] options

  **User selects [C]:**

  First, read the configured projects folder from `.claude/powerbi-analyst.json` → `projectPath`.
  Extract project name from the .pbix filename (without extension).

  Display folder creation offer:
  ```
  ✅ Great choice! Converting to PBIP unlocks full analysis capabilities.

  ⚠️  IMPORTANT: Each PBIP project needs its own folder!
  ─────────────────────────────────────────────────────
  When you save a PBIP, Power BI creates MULTIPLE files at the save location:
    - <project-name>.pbip
    - <project-name>.SemanticModel/
    - <project-name>.Report/

  Without a container folder, these mix with other projects.

  Would you like me to create the project folder?

    [Y] Yes, create: <configured-projects-folder>/<project-name>/
    [N] No, I'll create it myself
  ```

  **If user selects [Y]:**

  1. Create the folder:
     ```bash
     mkdir -p "<configured-projects-folder>/<project-name>"
     ```

  2. Display Save As instructions:
     ```
     ✅ Folder created: <configured-projects-folder>/<project-name>/

     Now complete the conversion:
     ────────────────────────────
     1. Open Power BI Desktop
     2. File → Open → Select: <pbix-file-path>
     3. File → Save As → Power BI Project (.pbip)
     4. Navigate to: <configured-projects-folder>/<project-name>/
     5. Click Save

     After conversion, re-run:
     ────────────────────────────
     /evaluate-pbi-project-file \
       --project "<configured-projects-folder>/<project-name>" \
       --description "<description>"
     ```

  **If user selects [N]:**
  - Remind them to create a containing folder first, then Save As inside it
  - Show the recommended path structure
  - Wait for them to provide the new path

  **Variable Substitutions:**
  - `<configured-projects-folder>`: From `.claude/powerbi-analyst.json` → `projectPath`
    - If null: Use "a short path like C:\PBI\ or D:\Projects\"
  - `<project-name>`: Extract from the .pbix filename (without extension)

  Update Prerequisites section with:
  ```markdown
  **Status**: action_required
  **Action Type**: user_converting_to_pbip
  **User Action**: User is converting to PBIP format (recommended path)
  ```

  Exit workflow gracefully (exit code 0)

  **User selects [N]:**
  Display manual extraction instructions (pbi-tools extraction path):
  ```
  📋 PBIX Extraction Instructions (DAX-only analysis)

  Note: This extracts DAX measures but M code will remain unreadable.
  For full analysis, consider converting to PBIP instead.

  ═══════════════════════════════════════════════════════════
  Using Power BI Desktop (for PBIP conversion - RECOMMENDED)
  ═══════════════════════════════════════════════════════════
  1. Open Power BI Desktop
  2. File → Open → Select: <pbix-file-path>
  3. File → Save As → Power BI Project
  4. Choose a location and name for the project
  5. A folder will be created with a .pbip file inside

  ═══════════════════════════════════════════════════════════
  Using pbi-tools (for DAX-only extraction)
  ═══════════════════════════════════════════════════════════
  pbi-tools extract "<pbix-file-path>"

  ═══════════════════════════════════════════════════════════
  After Conversion - Re-run this command:
  ═══════════════════════════════════════════════════════════
  /evaluate-pbi-project-file \
    --project "<converted-project-folder>" \
    --description "<description>"
  ```

  Update Prerequisites section with:
  ```markdown
  **Status**: action_required
  **Action Type**: manual_extraction_pending
  **User Action**: Manual conversion to .pbip format required
  ```

  Exit workflow gracefully (exit code 0)

  **User selects [I]:**
  Display installation guide:
  ```
  📦 pbi-tools Installation Guide

  pbi-tools is a command-line tool for extracting and compiling Power BI files.

  ═══════════════════════════════════════════════════════════
  Windows - Standalone Executable (Recommended)
  ═══════════════════════════════════════════════════════════
  1. Download latest release:
     https://github.com/pbi-tools/pbi-tools/releases

  2. Look for: pbi-tools.<version>.win-x64.zip

  3. Extract to a permanent location:
     Example: C:\tools\pbi-tools\

  4. Add to PATH (optional but recommended):
     - Windows Settings → System → About
     - Advanced system settings → Environment Variables
     - Edit "Path" variable
     - Add: C:\tools\pbi-tools\

  5. Verify installation:
     Open new terminal and run: pbi-tools --version

  ═══════════════════════════════════════════════════════════
  Windows - Chocolatey (if you use Chocolatey)
  ═══════════════════════════════════════════════════════════
  choco install pbi-tools

  ═══════════════════════════════════════════════════════════
  Cross-Platform - .NET Tool
  ═══════════════════════════════════════════════════════════
  Requirements: .NET 6.0+ SDK installed

  dotnet tool install -g pbi-tools

  ═══════════════════════════════════════════════════════════
  After Installation - Re-run this command:
  ═══════════════════════════════════════════════════════════
  /evaluate-pbi-project-file \
    --project "<pbix-file-path>" \
    --description "<description>"

  Then select [Y] when prompted to extract automatically.
  ```

  Update Prerequisites section with:
  ```markdown
  **Status**: action_required
  **Action Type**: pbitools_install_pending
  **User Action**: pbi-tools installation required
  ```

  Exit workflow gracefully (exit code 0)

**If Status = error:**
- Read `Error Message` and `Action Type` from Prerequisites
- **If Action Type = report_folder_missing or format_incompatible_with_visual_changes:**
  Display error specific to visual changes incompatibility:
  ```
  ❌ Visual Changes Not Supported

  <Error Message from Prerequisites>

  The workflow detected that your problem description includes visual property modifications
  (layout, colors, titles, formatting), but the project format does not support these changes.

  <Suggested Fixes from Prerequisites section>

  You can:
  1. Re-run with a .pbip project that includes a .Report folder
  2. Modify your problem description to focus only on calculation changes
  3. Handle visual changes manually in Power BI Desktop UI
  ```
  Exit workflow gracefully (exit code 0)

- **Otherwise (generic error):**
  Display error to user:
  ```
  ❌ Project Validation Failed

  <Error Message>

  Suggested Fix:
  <Suggested Fix>
  ```
  Exit workflow with error code 1

**Step 5: Validation Complete**

Once status=validated, Phase 1 is complete. The `validated_project_path` from Prerequisites should be used for all subsequent agent invocations.

Note: If the project `format` is `pbi-tools` or `pbix-extracted-pbitools`, remember that `requires_compilation: true` - this will be important in the implementation phase.

**Step 2.5: Storage Mode Detection & Format Recommendation**

After validating the project structure, detect the storage mode to determine analysis capabilities. See `resources/project-format-detection.md` for full detection logic.

**Detection Steps:**

1. **For PBIP projects:**
   - Read 2-3 table TMDL files from `.SemanticModel/definition/tables/`
   - Look for `partition 'name' = m` blocks with `mode: import` or `mode: directQuery`
   - No partition blocks = Live Connection or calculated table

2. **For extracted PBIX (pbi-tools format):**
   - Check DataModel file size
   - > 1 MB = Import Mode (M code in binary, recommend PBIP conversion)
   - < 100 KB = Likely Live Connection

3. **Classify and set capabilities:**
   ```yaml
   storage_mode: import | direct_query | live_connection
   m_code_accessible: true | false
   recommendation: none | convert_to_pbip | get_source_dataset
   ```

**If Import Mode PBIX or pbi-tools format detected (limited M code access):**

Display recommendation in findings file and to user:
```
╔═══════════════════════════════════════════════════════════════════════════╗
║  NOTE: Limited Analysis Mode                                              ║
╚═══════════════════════════════════════════════════════════════════════════╝

Project format: <format>
Storage mode: Import Mode

Current capabilities:
  [OK] DAX measures - Full access
  [--] M code / Power Query - NOT READABLE (embedded in binary)
  [--] Data lineage tracing - NOT AVAILABLE

This means:
- I can analyze and fix DAX measure logic
- I CANNOT see or analyze Power Query transformations
- I CANNOT trace data lineage from source to table

If your issue involves M code, ETL, or data transformations:
  → Convert to PBIP format for full visibility
  → See: resources/project-format-detection.md
```

Add to findings file Prerequisites section:
```markdown
**Analysis Mode**: Limited (DAX-only)
**M Code Accessible**: No
**Recommendation**: Convert to PBIP for full analysis
```

**If Live Connection detected:**

Display and add to findings:
```
╔═══════════════════════════════════════════════════════════════════════════╗
║  LIVE CONNECTION REPORT DETECTED                                          ║
╚═══════════════════════════════════════════════════════════════════════════╝

This report connects to a remote dataset. The data model is not in this file.

Current capabilities:
  [OK] Report visuals - Can analyze layout and configuration
  [--] DAX measures - Remote (not in this file)
  [--] M code - Remote (not in this file)
  [--] Data model - Remote (not in this file)

To analyze the data model:
  1. Go to Power BI Service
  2. Find and download the source dataset
  3. Convert to PBIP format
  4. Re-run with the dataset's .pbip folder

Would you like to:
  [A] Continue with visual-only analysis
  [B] Exit and get the source dataset
```

**If user selects [B]:** Exit gracefully with instructions
**If user selects [A]:** Continue to Phase 2 with limited scope

---

### Phase 2: Interactive Problem Clarification (Outcome-Focused)

**Purpose**: Clarify the DESIRED OUTCOME and business intent, not implementation details.

1. Read the image file (if provided) to understand visual context

2. Analyze the problem description to identify:
   - **Ambiguities in the desired outcome or behavior** - what should the end result look like?
   - **Unclear scope** - does this apply to everything or specific scenarios?
   - **Expected vs. current behavior** - what should change in the user's experience?
   - **Business logic intent** - the conceptual logic (e.g., "exclude returns", "apply discount"), not specific columns

3. Present a structured problem analysis to the user with:
   - Your understanding of what they want to achieve (outcome-focused)
   - Questions about expected behavior and user-visible results
   - Questions about scope and applicability
   - **Meta-questions**: "Do you know if similar patterns exist in this project?" "Do you have a preferred approach?"

4. **DO NOT ask about** (these come later in Step 2.5 after code scan):
   - Specific column names, table names, or measure names
   - Implementation details or technical approach
   - Which specific objects to modify

5. **Example Good Questions** (outcome-focused):
   - "When you say 'exclude returns', should the visual show lower totals, or should returns appear separately?"
   - "Should this apply to all commission types or only specific scenarios?"
   - "Do you expect this to affect historical data or only future calculations?"
   - "Are there other similar exclusions in this report that we should match the pattern of?"

6. Wait for user responses and incorporate them into the problem statement

7. Repeat clarification if needed until the DESIRED OUTCOME is well-defined (not the implementation)

### Phase 3: Scratchpad Creation
1. Generate timestamp: `YYYYMMDD-HHMMSS` format
2. Create distilled problem name:
   - Extract key terms from problem description
   - Convert to kebab-case
   - Limit to reasonable length (~30-40 chars)
   - Example: "update-total-sales-exclude-returns"
3. Create folder: `agent_scratchpads/<timestamp>-<distilled-name>/`
4. Create findings file: `agent_scratchpads/<timestamp>-<distilled-name>/findings.md`
5. Populate findings file with:
   - **Original Command** section at the very top with the full command-line prompt used to invoke this evaluation
   - Problem Statement section (including refined description from clarification)
   - Image reference (if provided)
   - Power BI project path information
   - Empty sections 1-3 ready for agent population

### Phase 4: Agent Orchestration

Execute agents conditionally in sequence with iterative refinement:

#### Pre-Flight Step: Authentication Token Check 🆕

**Before invoking the data context agent**, verify that authentication token exists:

1. **Check Token Validity**: Use Python to check if a valid cached token exists:
   ```python
   import sys
   sys.path.insert(0, 'xmla_agent')
   from get_token import check_token_validity

   token_status = check_token_validity()
   ```

2. **Interpret Results**:
   - If `token_status['valid'] == True`: Proceed to Step 1 (Data Context Agent)
   - If `token_status['requires_auth'] == True`: Prompt user for authentication

3. **Prompt User for Authentication** (if required):
   ```
   ⚠️  AUTHENTICATION REQUIRED

   The Power BI data context agent needs authentication to retrieve data from the semantic model.

   To authenticate, I'll run the authentication flow now. You will need to:
     1. Open the URL provided in your browser
     2. Enter the device code shown
     3. Sign in with your Power BI credentials

   Would you like me to start the authentication process now? [Y/N]
   ```

4. **Execute Authentication** (if user confirms):
   ```python
   from get_token import get_access_token
   token = get_access_token()

   if token:
       print("✓ Authentication successful! Proceeding with data retrieval...")
   else:
       print("❌ Authentication failed. Continuing with code-only analysis.")
   ```

5. **Handle User Decline**:
   - If user declines authentication, skip to Step 2 (Code Locator)
   - Add note to findings file: "Data context skipped - authentication not provided"

**Why This Matters**: Pre-flight authentication prevents the agent from starting its analysis, discovering it needs auth, timing out, and returning auth_required. Instead, we handle authentication upfront when workspace/dataset parameters are provided.

#### Step 1: Data Context Retrieval (powerbi-data-context-agent) 🆕
- **Purpose**: Query actual data from the semantic model to provide factual context
- **Input**: Problem statement, findings file path, workspace name, dataset name
- **Output**: Populates "Data Context" subsection in Section 1 with actual data values
- **Conditional**: Runs when:
  - Workspace and dataset parameters are provided AND
  - Pre-flight authentication check succeeded (or user authenticated) AND
  - Identifiers (invoice numbers, IDs, names) are mentioned in the problem OR problem involves data issues
- **Skip Conditions**:
  - No workspace/dataset parameters provided
  - User declined authentication in pre-flight step
  - Problem is code-only (syntax, formatting, relationships without data)
- **Why This Step Is Critical**: Prevents incorrect root cause diagnosis based on assumptions. For example, if the problem states "invoice P3495801 is missing," this agent queries the actual SALES_REP_ID values for that invoice rather than assuming they are -1.

**Note**: The pre-flight authentication check (above) eliminates the need for mid-agent authentication blocking. The agent should now only be invoked when authentication is already confirmed.

#### Step 2.7: Change Type Classification

**Purpose**: Determine what type of changes are needed (calculation, visual, or both)

**Orchestrator Logic** (NOT an agent - this is command logic):

1. Parse clarified problem statement for keywords:
   - **Calculation keywords**: "measure", "column", "DAX", "M code", "query", "relationship", "table", "calculated column", "fix formula"
   - **Visual keywords**: "move", "resize", "position", "title", "color", "font", "chart", "visual", "layout", "dashboard title", "axis label"

2. Check project format from Prerequisites:
   - Read `format` field and check for .Report folder existence

3. Classify request and determine investigation needs

**Classification Result**: `calc_only` | `visual_only` | `hybrid`

#### Step 2: Investigation Phase (Conditional Parallel Execution)

**Purpose**: Document current state before planning changes

**Based on classification from Step 2.7**:

**A. CALC_ONLY**: Invoke `powerbi-code-locator` → Section 1.A only

**B. VISUAL_ONLY** (with .Report): Invoke `powerbi-visual-locator` → Section 1.B only

**C. VISUAL_ONLY** (no .Report - pbi-tools): Prompt user for manual action

**D. HYBRID** (with .Report): Invoke BOTH agents in PARALLEL:
  - `powerbi-code-locator` → Section 1.A
  - `powerbi-visual-locator` → Section 1.B

**E. HYBRID** (no .Report): Invoke `powerbi-code-locator` → Section 1.A + add manual note

**Important**: Use `validated_project_path` from Prerequisites

#### Step 2.5: Code-Context Validation & Iterative Refinement (Human-in-the-Loop) 🆕

**Purpose**: Ensure clarified requirements align with found code, gather missing information, and re-search code if new objects are discovered.

**Workflow**:

**1. Analyze Code-Requirements Alignment**
- Read Section 1 (populated by powerbi-code-locator)
- Read Problem Statement (from Phase 2 clarification)
- Identify gaps, ambiguities, or unconfirmed assumptions
- Check for: multiple candidates, naming mismatches, missing expected objects, scope ambiguity

**2. Present Structured Questions to User**
- Show what was found vs. what was expected
- Highlight ambiguities revealed by code context
- **CRITICAL**: NEVER assume - always ask user to confirm uncertain details
- Request missing information (column names, filter criteria, etc.)

**Example Question Format**:
```
⚠️ CODE-CONTEXT CLARIFICATION NEEDED

After analyzing the code, I need clarification:

**Issue 1: Multiple Candidate Measures**
Section 1 shows 3 commission measures:
  • "PSSR Labor Commission" (Line 1907)
  • "PSSR Parts Commission" (Line 1590)
  • "PSSR Misc Commission" (Line 1951)

Your request: "update commission to exclude returns"

❓ Which measure(s) should be modified?
  [A] All three measures
  [B] Only Labor Commission
  [C] Only Parts and Misc
  [D] Other (specify)

**Issue 2: Return Identification Logic Missing**
None of the commission measures currently filter returns.

❓ How should returns be identified?
  [A] A column exists (please provide name)
  [B] Negative QUANTITY_SOLD values
  [C] Specific LINE_ITEM_TYPE value
  [D] Other criteria (describe)
```

**3. User Provides Clarifications**
- User answers all questions
- User may reveal NEW information:
  - New column names (e.g., "RETURN_INDICATOR")
  - New table names
  - New measure names
  - Specific filter patterns

**4. Update Problem Statement**
- Add new subsection: "### Code-Context Clarifications"
- Document all newly discovered requirements
- Include specific object names, columns, filter criteria
- Mark scope decisions clearly

**Example Updated Problem Statement**:
```markdown
### Code-Context Clarifications

**Scope Confirmed**:
- All three commission measures (Labor, Parts, Misc) should exclude returns
- Target measures: Lines 1590, 1907, 1951 in Commissions_Measures.tmdl

**Return Identification Logic** (newly discovered):
- Column: `RETURN_INDICATOR` in FACT_PS_INVOICE_DETAILS_COMMISSIONS
- Filter condition: `RETURN_INDICATOR <> "Y"`
- Apply to all SUMX calculations in commission measures
```

**5. Decision Point: Re-run Code Locator?**

**✅ RE-RUN code-locator IF user revealed**:
- New column names → search for existing usage patterns
- New table names → find table definitions
- New measure names → locate related measures
- Related objects → find dependencies

**❌ SKIP re-run IF clarification only included**:
- Scope selection (which existing objects to modify)
- Business logic details (percentages, thresholds)
- Confirmation of obvious choices

**Re-Run Prompt Enhancement**:
If re-running, enhance the code-locator prompt with:
```
ADDITIONAL SEARCH TARGETS (from user clarification):
- Column: RETURN_INDICATOR (find existing usage patterns)
- Look for measures that already handle returns
- Find any return-filtering logic patterns
```

**6. Execute Re-Run (if needed)**
- Invoke powerbi-code-locator with enhanced prompt
- Agent APPENDS new findings to Section 1 (preserves original findings)
- Section 1 header updated: "Updated: [timestamp] - Added return handling patterns"

**7. Present Updated Section 1**
- Show complete Section 1 with all findings
- Summarize what was added from re-run
- Check if any NEW ambiguities emerged

**8. Final Confirmation Loop**
- Ask user: "Is Section 1 complete? Ready to proceed to fix identification?"
- If user identifies MORE missing info → return to step 1
- If user confirms → proceed to Step 3 (powerbi-code-fix-identifier)

**Loop Condition**: Steps 1-8 repeat until user confirms complete alignment

**Exit Criteria**: User explicitly confirms:
- All relevant code has been found
- All ambiguities are resolved
- Requirements are clear and aligned with code

**Ambiguity Categories to Check**:

| Category | Example | Resolution |
|----------|---------|------------|
| Multiple Candidates | User said "Total Sales" but 3 measures have "Sales" | Ask which one(s) |
| Naming Mismatch | User said "Revenue" but code has "Net Revenue", "Gross Revenue" | Confirm mapping |
| Scope Ambiguity | User wants "update discount" but discount in 5 measures | Ask which measures |
| Missing Objects | User mentioned object not found in Section 1 | Ask for details, re-search |
| Column Name Unknown | User said "exclude returns" but no column identified | Ask how to identify |
| Similar Not Identical | User said "YoY Growth" but code has "YoY Growth %" and "YoY Growth Value" | Clarify which one |
| Unexpected Complexity | Simple request but code shows 8-variable calculation | Confirm full scope |
| Filter Context Needed | User wants to "add filter" but multiple filter contexts exist | Clarify exact context |

#### Step 3: Dashboard Update Planning (powerbi-dashboard-update-planner)

**Purpose**: Design calculation and/or visual changes based on investigation findings

**Agent**: `powerbi-dashboard-update-planner`

**Input**:
- Problem statement
- Findings file path
- Section 1.A (if exists - from code-locator)
- Section 1.B (if exists - from visual-locator)

**Agent Self-Detection**:
The agent reads Section 1.A and 1.B to determine scenario:
- Section 1.A only → CALCULATION_ONLY workflow
- Section 1.B only → VISUAL_ONLY workflow
- Both sections → HYBRID workflow (with coordination)

**Output** (scenario-dependent):
- **CALC_ONLY**: Section 2.A (Calculation Changes)
- **VISUAL_ONLY**: Section 2.B (Visual Changes)
- **HYBRID**: Coordination Summary + Section 2.A + Section 2.B

**Key Feature for HYBRID**:
- Agent designs calculation changes FIRST (determines measure names, formats)
- Agent designs visual changes SECOND (references exact names from calculations)
- Agent documents dependencies and execution order

**Note**: This single agent replaces the former `powerbi-code-fix-identifier` and `pbir-visual-edit-planner` agents with unified expertise

#### Step 4: Verification & Testing (power-bi-verification)

**Purpose**: Validate proposed changes and assess impact

**Input**: Problem statement, findings file path (with Sections 1 & 2 completed)

**Output**: Populates Section 3 (Test Cases and Impact Analysis)

**Conditional**: Only runs if Section 2 has proposed changes (either 2.A or 2.B or both)

**Validation Scope**:

**For Calculation Changes (Section 2.A)**:
- DAX syntax correctness
- Measure dependencies and references
- Filter context appropriateness
- Performance considerations
- Breaking change detection

**For Visual Changes (Section 2.B)**: 🆕
- XML syntax validation
- Target file path existence in .Report folder
- JSON path validity (property paths exist in visual.json schema)
- new_value data type compatibility
- Operation type appropriateness (replace_property vs config_edit)

**For Hybrid Changes (Both 2.A and 2.B)**:
- Compatibility between calculation and visual changes
- Example: If visual references a new measure, verify measure exists in Section 2.A
- Dependency ordering (calculations should be applied before visual changes)

**Result**: Provides Pass/Warning/Fail verdict based on comprehensive validation

### Phase 5: Completion
1. Display summary of findings location
2. Show verification verdict (if verification ran)
3. Provide clickable link to findings file
4. Suggest next steps based on verdict:
   - **Pass**: Ready to implement changes
   - **Warning**: Review recommendations before implementing
   - **Fail**: Address issues before proceeding

## Error Handling

- **Project not found**: "Error: Power BI project folder not found at '<path>'. Please verify the path points to a valid .pbip project directory."
- **Invalid project structure**: "Error: The specified folder does not appear to be a valid Power BI project (missing .SemanticModel or definition folders)."
- **Image not found**: "Warning: Image file '<path>' not found. Proceeding without visual context."
- **Agent failure**: Report which agent failed and why, preserve partial findings file
- **Authentication Required** (powerbi-data-context-agent):
  - **Primary Mechanism**: Use pre-flight authentication check (Phase 4, Pre-Flight Step) to handle auth before invoking agent
  - **Fallback**: If the agent still returns `status='auth_required'` (rare edge case), handle as follows:

### Handling Authentication Required Status (Fallback)

**Note**: This should rarely occur with pre-flight authentication check in place.

When the powerbi-data-context-agent returns `status='auth_required'` (fallback scenario), the orchestrator MUST:

1. **Parse the agent output** to extract the auth_info block from the final report
2. **Display authentication instructions** to the user in a clear, structured format:

```
⚠️  AUTHENTICATION REQUIRED

The data context agent needs you to authenticate to Power BI to retrieve actual data.

To authenticate:
  1. Open: https://microsoft.com/devicelogin
  2. Enter code: ABC123XYZ
  3. Sign in with your Power BI credentials
  4. The code expires in 15 minutes

What would you like to do?
  [A] I've completed authentication - retry the agent now
  [B] Skip data retrieval and continue with code-only analysis
  [C] Cancel the evaluation workflow
```

3. **Wait for user choice**:
   - **Option A**: Re-invoke the powerbi-data-context-agent with the same parameters
   - **Option B**: Continue to powerbi-code-locator (skip data context)
   - **Option C**: Exit the workflow gracefully

4. **On retry (Option A)**:
   - Re-run the Task tool with the powerbi-data-context-agent
   - If it succeeds, continue to next agent
   - If it fails again, offer Option B or C only

5. **On skip (Option B)**:
   - Add a note to the findings file indicating data context was skipped
   - Continue to powerbi-code-locator agent
   - Warn user that root cause diagnosis may be based on assumptions

6. **NEVER**:
   - Assume the agent completed successfully when status='auth_required'
   - Continue to the next agent without user confirmation
   - Silently skip data retrieval without informing the user

## Output Structure

The generated findings file follows this structure:

```markdown
# Analysis: <Distilled Problem Name>

**Created**: <Timestamp>
**Project**: <Project Path>
**Status**: [In Progress / Completed]

---

## Original Command

```bash
/evaluate-pbi-project-file --project "<project-path>" --description "<description>" [--image "<image-path>"] [--workspace "<workspace>"] [--dataset "<dataset>"]
```

This command can be modified and re-run for subsequent analysis iterations.

---

## Problem Statement

<Refined problem description from interactive clarification>

[Image: <path-to-image>] (if provided)

**Key Objects Identified**:
- Measure: "Total Sales"
- Table: "Sales"
- etc.

**Project File Locations**:
- Semantic Model: `<path>/.SemanticModel/`
- TMDL Definitions: `<path>/.SemanticModel/definition/`
- Report: `<path>/.Report/` (if applicable)

---

## Section 1: Current Implementation Investigation

### Data Context: Actual Values from Semantic Model
[Populated by powerbi-data-context-agent - only if workspace/dataset provided]

**Query Strategy**: [specific_records | sample_data | measure_calculation]

**Identifiers Extracted**: [list of IDs, names, dates found in problem statement]

**DAX Query Executed**:
```dax
[DAX query that was run]
```

**Results Retrieved**: [actual data from semantic model]

**Key Observations**: [factual observations about the data]

---

### Code Investigation
[Populated by powerbi-code-locator agent]

[Code snippets, file locations, DAX/M expressions]

---

## Section 2: Proposed Changes
[Populated by powerbi-code-fix-identifier agent - should reference data context if available]

## Section 3: Test Cases and Impact Analysis
[Populated by power-bi-verification agent]
```

## Notes

- This command is designed for focused, single-issue analysis
- For multiple unrelated changes, run the command separately for each
- The scratchpad folder preserves full analysis history with timestamps
- Agents can be re-run individually if needed by invoking them directly with the findings file path

### Unified Planning Architecture 🆕

**Supported Change Types**:
1. **Calculation Changes**: DAX measures, M queries, TMDL model definitions (all project formats)
2. **Visual Changes**: PBIR visual properties - layout, formatting, visual types, data bindings (Power BI Project .pbip format only)
3. **Hybrid Changes**: Both calculation and visual changes in a single request with automatic coordination

**Single Agent Approach**:
- The `powerbi-dashboard-update-planner` agent handles ALL three scenarios
- Agent automatically detects scenario by reading Section 1.A and 1.B
- For hybrid requests, agent coordinates changes (code decisions inform visual changes)

**Visual Editing Requirements**:
- Project must be in Power BI Project (.pbip) format
- .Report folder must exist in the project structure
- Not supported for pbi-tools or pbix-extracted-pbitools formats (manual actions required)

**Change Examples**:
- **Calculation**: "Update Total Sales to exclude returns" → Section 2.A only
- **Visual**: "Move Sales chart to top-right, resize to 600px" → Section 2.B only
- **Hybrid**: "Add YoY Growth measure and update dashboard title" → Coordination Summary + 2.A + 2.B

**What's NOT a Visual Change**:
- Field parameters (data model objects, not visual properties)
- New visuals (must be created in Power BI Desktop UI)
- Slicers, bookmarks (UI-only operations)

**Hybrid Coordination**:
- Calculation changes designed FIRST (determines names, formats)
- Visual changes designed SECOND (references exact names from calculations)
- Dependencies and execution order explicitly documented
- Example: Measure "YoY Growth %" created in 2.A, referenced by title in 2.B

**Output Formats**:
- Section 2.A: DAX/M/TMDL code (for calculations)
- Section 2.B: XML edit plans (for visuals)
- Coordination Summary: Dependencies and execution order (for hybrid)

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
