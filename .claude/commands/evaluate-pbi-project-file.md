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

### Phase 1: Validation & Setup
1. Parse command arguments to extract project path, image path (if provided), and description
2. Validate that the Power BI project folder exists
3. Search for `.pbip` files and TMDL structure to confirm valid project
4. Exit with clear error message if project is invalid

### Phase 2: Interactive Problem Clarification
1. Read the image file (if provided) to understand visual context
2. Analyze the problem description to identify:
   - Key Power BI objects mentioned (measures, tables, columns, relationships)
   - Ambiguous requirements or unclear specifications
   - Missing critical information (data types, business logic, filter contexts)
3. Present a structured problem analysis to the user with:
   - Understanding of the request
   - Identified ambiguities or unclear points
   - Specific clarifying questions
4. Wait for user responses and incorporate them into the problem statement
5. Repeat clarification if needed until the problem is well-defined

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

Execute agents conditionally in sequence:

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

#### Step 2: Code Location (powerbi-code-locator)
- **Purpose**: Find existing relevant code in the Power BI project
- **Input**: Problem statement, project path, findings file path (with data context if available)
- **Output**: Populates Section 1 (Current Implementation Investigation) with code snippets
- **Conditional**: Always runs
- **Note**: May return empty if this is a new feature with no existing code

#### Step 3: Code Fix Identification (powerbi-code-fix-identifier)
- **Purpose**: Diagnose issues and generate corrected code implementations
- **Input**: Problem statement, findings file path (with Section 1 completed, including data context)
- **Output**: Populates Section 2 (Proposed Changes)
- **Conditional**: Always runs (can handle both new and modified code)
- **Note**: Should use data context from Step 1 to inform diagnosis

#### Step 4: Verification & Testing (power-bi-verification)
- **Purpose**: Validate proposed changes and assess impact
- **Input**: Problem statement, findings file path (with Sections 1 & 2 completed)
- **Output**: Populates Section 3 (Test Cases and Impact Analysis)
- **Conditional**: Only runs if Section 2 has proposed changes
- **Result**: Provides Pass/Warning/Fail verdict

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
