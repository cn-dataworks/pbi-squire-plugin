# /merge-powerbi-projects

> **MAIN THREAD EXECUTION**: This workflow executes in the MAIN THREAD, not a subagent.
> The main thread spawns leaf subagents via `Task()` and coordinates their work.
> Subagents do NOT spawn other subagents.

**Role:** This workflow runs in the main thread and coordinates the Power BI project comparison and merge process.

## Invocation

```
/merge-powerbi-projects --main "<path_to_main_project>" --comparison "<path_to_comparison_project>" [--description "<focus_area>"]
```

## Parameters

- `--main`: Path to the main Power BI project folder (.pbip) - this is the base version
- `--comparison`: Path to the comparison Power BI project folder (.pbip) - contains changes to potentially merge
- `--description` (optional): Focus area to filter differences - only show changes related to this topic (e.g., "revenue calculations", "customer segmentation", "date tables")

## Workflow Overview

This command orchestrates a three-phase workflow with human-in-the-loop decision making:

1. **Technical Comparison** (via `powerbi-compare-project-code` agent)
2. **Business Impact Analysis** (via `powerbi-code-understander` agent)
3. **User Decision & Merge** (via `powerbi-code-merger` agent)

## Execution Instructions

This workflow runs in the main thread. Follow these steps precisely:

### Phase 1: Validate Input

1. Verify that both `--main` and `--comparison` paths are provided
2. Check that both paths exist and contain valid `.pbip` project structures
3. Look for the presence of:
   - `*.SemanticModel/` folder with either `model.bim` or TMDL structure
   - `*.Report/` folder with `report.json`
4. If validation fails, inform the user and stop

### Phase 2: Technical Comparison

**Note:** The `powerbi-compare-project-code` agent uses tool-first fallback pattern:
- **Developer Edition:** Uses `pbi_merger_utils.py` for fast, structured comparison
- **Analyst Edition:** Uses `references/project_comparison_guide.md` → Part 1 for Claude-native comparison

Main thread spawns the technical auditor agent:

```
Task(powerbi-compare-project-code):
Prompt: "Compare the two Power BI project folders:
- Main project: {main_path}
- Comparison project: {comparison_path}

{If --description parameter was provided:}
**FOCUS FILTER**: Only include differences related to: "{description}"

Use semantic relevance matching to filter differences:
- Check if component names contain relevant keywords
- Check if DAX/M code references relevant columns/tables
- Check if visual titles or data fields relate to the focus area
- Include dependencies (e.g., if a measure is relevant, include tables it references)

Examples of relevance matching:
- Description: "revenue calculations" → Include: measures with "Revenue", "Sales", "Income" in name or code
- Description: "customer segmentation" → Include: tables/columns with "Customer", "Segment", visuals showing customer data
- Description: "date tables" → Include: Date/Calendar tables, time intelligence measures, date relationships

**IMPORTANT**: If unsure about relevance, INCLUDE the diff (false positives better than false negatives).

Generate a structured JSON 'Diff Report' that identifies all semantic differences{if description: " related to the focus area"}:
- Tables, measures, calculated columns, relationships (from model.bim or TMDL)
- Report pages, visuals, filters (from report.json)
- Any added or deleted files

Each diff must have:
- diff_id: unique identifier
- component_type: type of object (Measure, Table, Visual, etc.)
- component_name: name of the object
- file_path: relative path within project
- status: Added, Modified, or Deleted
- main_version_code: code/JSON from main (if exists)
- comparison_version_code: code/JSON from comparison (if exists)
{If description provided:}
- relevance_reason: brief explanation of why this diff is relevant to '{description}'

{If description provided:}
Also include a 'filter_summary' field in the output:
```json
\"filter_summary\": {
  \"focus_area\": \"{description}\",
  \"total_diffs_found\": {count},
  \"total_diffs_included\": {count},
  \"total_diffs_filtered_out\": {count}
}
```

Return the complete structured JSON diff report."
```

Wait for the agent to complete. Store the result as `diff_report.json`.

### Phase 3: Business Impact Analysis

Main thread spawns the business analyst agent:

```
Task(powerbi-code-understander):
Prompt: "Analyze this Power BI Diff Report and add business impact analysis:

{paste the diff_report.json here}

For each diff entry, add a new field 'business_impact' that explains:
- What changed in plain business terms
- Why this matters to report users
- Potential consequences of choosing one version over the other

Return the enriched JSON with business_impact added to each entry."
```

Wait for the agent to complete. Store the result as `business_impact_report.json`.

### Phase 4: Present Choices to User (HITL)

Format a user-friendly presentation combining technical and business information:

```markdown
# Power BI Project Merge Analysis

## Summary
- Main Project: {main_path}
- Comparison Project: {comparison_path}
{If description provided:}
- **Focus Area**: {description}
- **Filter Applied**: Showing only differences related to "{description}"
- **Total Differences Found**: {filter_summary.total_diffs_found}
- **Differences Included (Relevant)**: {filter_summary.total_diffs_included}
- **Differences Filtered Out**: {filter_summary.total_diffs_filtered_out}
{Else:}
- Total Differences Found: {count}

## Differences Requiring Your Decision

{For each diff in business_impact_report.json:}

---
### Diff {diff_id}: {component_type} - "{component_name}"

**Location:** {file_path}

**Status:** {status}

**Technical Details:**
- Main Version:
  ```
  {main_version_code or "Not present"}
  ```
- Comparison Version:
  ```
  {comparison_version_code or "Not present"}
  ```

**Business Impact:**
{business_impact}

{If description provided and relevance_reason exists:}
**Why This Is Relevant to "{description}":**
{relevance_reason}

**Your Choice:** [Respond with: "{diff_id}: Main" or "{diff_id}: Comparison"]

---

## Instructions

Please review each difference above and respond with your decisions in this format:
```
diff_001: Comparison
diff_002: Main
diff_003: Comparison
```

Or simply reply with "all Main" or "all Comparison" to choose one version for everything.
```

Present this to the user and WAIT for their response.

### Phase 5: Parse User Decisions

When the user responds:

1. Parse their response into a structured `merge_manifest.json`:
   ```json
   {
     "merge_decisions": [
       {"diff_id": "diff_001", "choice": "Comparison"},
       {"diff_id": "diff_002", "choice": "Main"}
     ],
     "main_project_path": "{main_path}",
     "comparison_project_path": "{comparison_path}",
     "output_project_path": "{generate timestamped path}"
   }
   ```

2. Handle special cases:
   - "all Main" → all choices are "Main"
   - "all Comparison" → all choices are "Comparison"
   - Individual decisions → parse each line

### Phase 6: Execute Merge

Main thread spawns the merge execution agent:

```
Task(powerbi-code-merger):
Prompt: "Execute this Power BI project merge based on user decisions:

{paste merge_manifest.json here}

Process:
1. Create a new timestamped project folder (non-destructive)
2. Copy the entire main project to the new folder
3. For each diff where choice is 'Comparison':
   - Parse the target file (model.bim, report.json, TMDL, etc.)
   - Locate the specific object by name/ID
   - Replace with the comparison version
   - Save the modified file
4. Generate a detailed merge log

Return:
- Path to the merged project
- Complete merge log showing all actions taken"
```

Wait for the agent to complete. Store the result as `merge_result`.

### Phase 6.5: TMDL Format Validation (Quality Gate)

**Note:** The `powerbi-tmdl-syntax-validator` agent uses tool-first fallback pattern:
- **Developer Edition:** Uses `tmdl_format_validator.py` for fast validation with auto-fix
- **Analyst Edition:** Uses `references/tmdl_partition_structure.md` → Part 1 for Claude-native validation

If any TMDL files were modified during the merge, validate their formatting:

```
Task(powerbi-tmdl-syntax-validator):
Prompt: "Validate TMDL file formatting for the merged Power BI project:

Project Path: {output_project_path from merge_result}

Context: Power BI project merge completed. {statistics.files_modified} files were modified during the merge operation. Need to validate TMDL formatting before presenting to user.

Modified Files: {list of .tmdl files that were modified, from merge log}

Please validate:
1. Indentation consistency (tabs vs spaces)
2. Property placement (formatString, displayFolder at correct indentation)
3. Measure/column structure syntax
4. Tab usage compliance

Return validation status for each modified TMDL file."
```

If validation **FAILS**:
- Add validation errors to the final report
- Mark merge status as "completed with formatting warnings"
- Recommend user fix issues before deploying

If validation **PASSES**:
- Proceed to Phase 6.6

### Phase 6.6: DAX Validation (Quality Gate)

If any measures, calculated columns, or tables were modified, validate DAX syntax:

```
Task(powerbi-dax-review-agent):
Prompt: "Validate DAX syntax for modified objects in merged Power BI project:

Project Path: {output_project_path from merge_result}

Context: Power BI project merge completed. The following DAX objects were modified by merging from the comparison project:

{For each diff where choice='Comparison' and component_type in ['Measure', 'CalculatedColumn', 'CalculatedTable']:
  - Object: {component_name}
  - Type: {component_type}
  - File: {file_path}
  - Source: Merged from comparison project
}

Please validate ONLY these specific objects for:
1. DAX syntax errors
2. Function signature correctness
3. Reference validity
4. Runtime error risks (division by zero, null handling)
5. Context usage appropriateness

Return validation status for each modified DAX object."
```

**Note**: This is a lightweight validation focused only on the merged objects, NOT a full project scan.

If validation **FAILS**:
- Add DAX errors to the final report
- Mark merge status as "completed with DAX errors"
- Recommend user review and fix before deploying

If validation **PASSES**:
- Proceed to Phase 7

### Phase 7: Final Report to User

Present the final consolidated report:

```markdown
# Power BI Project Merge Complete

## Summary
- **Original Main:** {main_path}
- **Comparison Source:** {comparison_path}
- **Merged Output:** {output_path}
- **Decisions Applied:** {count} differences processed

## Section 1: Code-Level Differences
{Summary table from diff_report.json}

## Section 2: Business Impact Analysis
{Summary from business_impact_report.json}

## Section 3: Merge Execution Log
{merge_log from powerbi-code-merger}

## Section 4: Validation Results

### TMDL Format Validation
{If TMDL validation was performed:}
**Status**: ✅ PASSED | ⚠️ WARNINGS | ❌ FAILED
**Files Validated**: {count}
**Issues Found**: {count}

{If issues found, list them with file paths and line numbers}

### DAX Syntax Validation
{If DAX validation was performed:}
**Status**: ✅ PASSED | ⚠️ WARNINGS | ❌ FAILED
**Objects Validated**: {count}
**Syntax Errors**: {count}
**Semantic Warnings**: {count}

{If issues found, list them with object names and descriptions}

## Overall Merge Status

{If all validations passed:}
✅ **MERGE SUCCESSFUL** - Ready for deployment

{If warnings but no errors:}
⚠️ **MERGE COMPLETED WITH WARNINGS** - Review warnings before deployment

{If errors found:}
❌ **MERGE COMPLETED WITH ERRORS** - Fix validation errors before deployment

## Next Steps

{If all validations passed:}
Your merged project is ready at: {output_path}

You can now:
1. Open the merged .pbip in Power BI Desktop
2. Verify visuals and measures work correctly
3. Deploy to Power BI Service

{If warnings:}
Your merged project is at: {output_path}

Recommended actions:
1. Review the warnings in Section 4 above
2. Decide if fixes are needed
3. If acceptable, proceed to open in Power BI Desktop
4. Test thoroughly before deployment

{If errors:}
Your merged project is at: {output_path}

**CRITICAL**: The merged project has validation errors and may not open correctly in Power BI Desktop.

Required actions:
1. Review errors in Section 4 above
2. Manually fix the errors in the merged project files
3. Re-run validation (optional)
4. Then open in Power BI Desktop
```

## Error Handling

- If any agent fails, capture the error and present it to the user
- Always preserve the original projects (non-destructive workflow)
- If user cancels during decision phase, clean up any temp files

## State Management

Maintain these variables throughout the workflow:
- `main_path`: Path to main project
- `comparison_path`: Path to comparison project
- `diff_report`: Results from Phase 2
- `business_impact_report`: Results from Phase 3
- `merge_manifest`: User decisions from Phase 5
- `merge_result`: Results from Phase 6

## Success Criteria

The workflow is complete when:
1. All three agents have successfully executed
2. User has made decisions on all differences
3. Merged project has been created
4. Final report has been presented

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
