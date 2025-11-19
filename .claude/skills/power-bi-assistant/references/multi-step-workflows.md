# Multi-Step Workflows

Complete end-to-end workflow sequences for Power BI development.

## Workflow 1: Analyze → Implement → Deploy → Test

**Use when:** Fixing existing code, modifying calculations, updating visuals

### Step 1: Analyze the Problem

**Command:**
```bash
/evaluate-pbi-project-file --project "<path>" --description "<problem>" [--workspace "<name>"] [--dataset "<name>"]
```

**What happens:**
1. Project validation (format detection, structure check)
2. Optional: Data context retrieval (if workspace/dataset provided)
3. Problem classification (calculation, visual, or hybrid)
4. Investigation phase:
   - Locates relevant code (Section 1.A)
   - Locates visual state (Section 1.B, if visual changes)
5. Planning phase:
   - Designs fixes (Section 2.A for code, Section 2.B for visual)
   - Coordinates hybrid changes (both code and visual)
6. Verification: Validates proposed changes

**Output:**
- `agent_scratchpads/<timestamp>-<problem>/findings.md`
- Sections 1 (Investigation), 2 (Proposed Changes), 3 (Test Cases)

**Checkpoint:** Review findings.md before proceeding
- Check Section 2.A (code changes) - correct logic?
- Check Section 2.B (visual changes) - correct properties?
- Review Section 3 (test cases) - cover all scenarios?

---

### Step 2: Implement Changes

**Command:**
```bash
/implement-deploy-test-pbi-project-file --findings "<path-to-findings.md>" [--deploy "<env>"] [--dashboard-url "<url>"]
```

**What happens:**
1. Parses findings file
2. Creates timestamped project copy
3. Applies code changes (if Section 2.A exists):
   - Modifies DAX measures, M queries, or TMDL structures
   - Uses robust TMDL editor for proper formatting
4. Applies visual changes (if Section 2.B exists):
   - Executes XML edit plans on visual.json files
   - Modifies layout, formatting, titles, colors
5. Validation phase:
   - TMDL format validation (if code changes)
   - PBIR structure validation (if visual changes)
   - DAX syntax validation (if code changes)
6. Optional deployment (if --deploy provided)
7. Optional testing (if --dashboard-url provided)

**Output:**
- Versioned project: `<project>_YYYYMMDD_HHMMSS`
- Updated findings.md with Section 4 (Implementation Results)
- Test results in `test-results/` (if testing performed)

**Checkpoint:** Verify implementation success
- Check validation reports (Section 2.5, 2.6)
- Review deployment status (if deployed)
- Examine test results (if tested)

---

### Step 3: Manual Verification (Always Recommended)

**Open the versioned project in Power BI Desktop:**
1. Navigate to versioned folder: `<project>_YYYYMMDD_HHMMSS`
2. Open `.pbip` file in Power BI Desktop
3. Verify changes:
   - For code changes: Check measures/columns work correctly
   - For visual changes: Check visual appearance and behavior
4. Test with actual data and filters
5. Review performance (query execution time)

**If issues found:**
- Review validation reports in findings.md
- Fix issues in original findings.md (Section 2)
- Re-run implement command with updated findings

---

### Step 4: Deploy to Production (Optional)

**If not deployed in Step 2:**
```bash
/implement-deploy-test-pbi-project-file --findings "<path-to-findings.md>" --deploy PROD
```

**Manual deployment alternative:**
1. Open versioned project in Power BI Desktop
2. Publish to Power BI Service
3. Configure refresh schedule
4. Share with stakeholders

---

## Workflow 2A: Create Single Artifact → Implement → Deploy → Test

**Use when:** Building a new measure, column, table, or single visual

### Step 1: Create Artifact Specification

**Command:**
```bash
/create-pbi-artifact --project "<path>" --type <type> --description "<what-to-create>" [--workspace "<name>"] [--dataset "<name>"]
```

**What happens:**
1. Project validation
2. Data model analysis (Section 1.1 - schema extraction)
3. Artifact decomposition (Section 1.0 - breaks complex requests into parts)
4. Interactive data understanding:
   - Asks clarifying questions with recommendations
   - Samples actual data (if workspace/dataset provided)
   - Builds complete specification (Section 1.2)
5. Pattern discovery (Section 1.3 - finds similar existing artifacts)
6. Artifact design (Section 2 - generates implementation-ready code)

**Output:**
- `agent_scratchpads/<timestamp>-create-<name>/findings.md`
- Section 1.0 (Artifact Breakdown)
- Section 1.1 (Data Model Schema)
- Section 1.2 (Specification)
- Section 1.3 (Pattern Discovery)
- Section 2 (Proposed Code in CREATE format)

**Checkpoint:** Review specification thoroughly
- Section 1.2: Is the business logic correct?
- Section 1.3: Do the patterns make sense for your project?
- Section 2: Is the generated code what you expect?
  - Correct calculation method?
  - Proper formatting?
  - Handles edge cases?

---

### Step 2-4: Same as Workflow 1

Follow Steps 2-4 from Workflow 1 (Implement → Verify → Deploy)

**Note for multi-artifact creation:**
- Implementation applies artifacts in dependency order
- Helper measures created before main measures
- Base calculations before dependent calculations

---

## Workflow 2B: Create Complete Page → Implement → Deploy → Test

**Use when:** Designing a complete dashboard page with multiple visuals, measures, layout, and interactions

### Step 1: Create Page Specifications

**Command:**
```bash
/create-pbi-page-specs --project "<path>" --question "<business-question>" [--workspace "<name>"] [--dataset "<name>"] [--page-name "<name>"]
```

**What happens:**
1. Project validation (requires .Report folder)
2. Question analysis (classifies question type, identifies requirements)
3. Data model analysis (Section 1.1 - schema extraction)
4. Artifact decomposition (Section 1.2 - separates measures vs visuals vs interactions)
5. **PARALLEL WORKFLOWS:**
   - **Branch A (Measures):** For each new measure:
     - Interactive Q&A for measure specification
     - Pattern discovery
     - DAX code generation
   - **Branch B (Visuals):** For each visual:
     - Visual type recommendation (2-3 options with pros/cons)
     - Field mapping Q&A (axis, values, legend)
     - Formatting recommendations
6. Page layout design (Section 3 - generates coordinates using research-based 1600×900 canvas)
7. Interaction design (Section 4 - cross-filtering matrix, drill-through targets)
8. PBIR page generation (Section 5 - complete page.json and visual.json files)
9. Helper page identification (Section 6 - recommends drill-through targets)
10. Validation (DAX + PBIR)

**Output:**
- `agent_scratchpads/<timestamp>-<page-name>/findings.md`
- Section 1.0 (Question Analysis & Page Planning)
- Section 1.1 (Data Model Schema)
- Section 1.2 (Artifact Breakdown - measures + visuals separated)
- Section 2.A (Calculation Changes - DAX measures)
- Section 2.B (Visual Specifications - field mappings, formatting)
- Section 3 (Page Layout Plan - coordinates table)
- Section 4 (Interaction Design - cross-filtering matrix)
- Section 5 (PBIR Page Files - complete JSON)
- Section 6 (Helper Page Recommendations)
- Section 7 (Validation Results)
- Section 8 (Final Summary)

**Checkpoint:** Review complete page design
- **Section 1.2:** Are all needed measures and visuals identified?
- **Section 2.A:** Is the DAX code correct for each measure?
- **Section 2.B:** Are visual types and field mappings appropriate?
- **Section 3:** Does the layout make analytical sense?
- **Section 4:** Are interactions logical (cross-filtering, drill-through)?
- **Section 5:** Review PBIR JSON for any issues
- **Section 6:** Should you create helper pages first or later?

---

### Step 2-4: Same as Workflow 1

Follow Steps 2-4 from Workflow 1 (Implement → Verify → Deploy)

**Note for page creation:**
- Implementation creates folder structure in .Report/definition/pages/
- All measures created first (Section 2.A)
- Then page and visual files created (Section 5)
- Validation includes both DAX and PBIR checks

---

## Workflow 3: Compare → Decide → Merge

**Use when:** Merging two Power BI projects, syncing dev/prod, adopting changes

### Step 1: Compare Projects

**Command:**
```bash
/merge-powerbi-projects --main "<baseline-path>" --comparison "<source-path>" [--description "<focus>"]
```

**What happens:**
1. Validates both project paths
2. Technical comparison (Agent 1: powerbi-compare-project-code):
   - Scans file structures
   - Identifies all differences (added/modified/deleted)
   - Generates DiffReport with unique IDs
3. Business impact analysis (Agent 2: powerbi-code-understander):
   - Explains what each change means
   - Assesses consequences of choosing each version
   - Provides decision guidance

**Output:**
- Combined analysis showing:
  - **Section 1:** Code-Level Differences (technical)
  - **Section 2:** Business Impact Analysis (plain English)
  - Diff IDs for each change (diff_001, diff_002, etc.)

**Checkpoint:** Review analysis carefully
- Understand each difference
- Consider business impact
- Identify critical vs. minor changes

---

### Step 2: Make Decisions

**Respond with your choices:**

**Individual decisions:**
```
diff_001: Comparison
diff_002: Main
diff_003: Comparison
diff_004: Main
```

**Bulk decisions (all at once):**
```
all Main
```
or
```
all Comparison
```

**Mixed approach:**
```
diff_001: Comparison
diff_002: Comparison
rest Main
```

**What each choice means:**
- **Main**: Keep the version from your baseline project (no change)
- **Comparison**: Adopt the version from the source project (apply change)

---

### Step 3: Execute Merge

**What happens automatically:**
1. Parses your decisions into MergeManifest
2. Merge execution (Agent 3: powerbi-code-merger):
   - Creates new timestamped output folder
   - Copies main project as base
   - Applies "Comparison" choices surgically
   - Preserves file formatting
3. Validation:
   - TMDL format validation
   - DAX syntax validation
4. Final report generation

**Output:**
- New merged project: `merged_YYYYMMDD_HHMMSS.pbip`
- Comprehensive merge report with:
  - Section 3: Merge Execution Log
  - Validation results
  - Statistics (how many changes applied)
- Original projects unchanged (non-destructive)

**Checkpoint:** Test merged project
- Open in Power BI Desktop
- Verify all changes applied correctly
- Test calculations and visuals
- Check for unexpected side effects

---

### Step 4: Deploy Merged Project (Manual)

1. Open merged project in Power BI Desktop
2. Test thoroughly with real data
3. Publish to appropriate workspace
4. Monitor for issues

---

## Cross-Workflow Integration

### Scenario: Evaluate → Discover Need to Create → Implement Both

**Situation:** During evaluation, you realize a helper measure is needed

**Approach:**
1. Complete evaluate workflow (creates findings with fix)
2. Run create workflow for helper measure
3. Manually combine Section 2 from both findings files
4. Run implement command with combined findings

**Alternative:**
1. Let evaluate workflow identify the need
2. It will document "requires new helper measure" in Section 2
3. Create helper measure first, then fix main measure

---

### Scenario: Merge → Evaluate Conflicts → Implement Fixes

**Situation:** After merge, some calculations don't work as expected

**Approach:**
1. Complete merge workflow
2. Open merged project, identify issues
3. Run evaluate workflow on merged project
4. Implement fixes

---

## General Workflow Best Practices

### Before Starting Any Workflow

1. **Backup your project** (or verify it's in source control)
2. **Know your paths** (absolute paths, proper quoting)
3. **Check prerequisites:**
   - For data sampling: workspace/dataset names ready
   - For deployment: authentication configured
   - For testing: dashboard URL accessible

### During Workflow Execution

1. **Review each output carefully** before proceeding
2. **Use workspace/dataset parameters** when possible (better recommendations)
3. **Read validation reports** - they catch issues early
4. **Don't skip checkpoints** - cheaper to fix before deployment

### After Workflow Completion

1. **Always test in Power BI Desktop** before production deployment
2. **Keep versioned folders** for audit trail and rollback
3. **Document changes** in your project's change log
4. **Monitor deployed changes** for unexpected issues

---

## Workflow Execution Time Estimates

### Workflow 1: Analyze → Implement → Deploy → Test
- **Evaluation:** 2-5 minutes (with data context: 5-10 minutes)
- **Implementation:** 1-3 minutes
- **Validation:** 30 seconds - 2 minutes
- **Deployment:** 2-5 minutes (depends on model size)
- **Testing:** 3-10 minutes (depends on test cases)
- **Total:** ~15-30 minutes

### Workflow 2A: Create Single Artifact → Implement → Deploy → Test
- **Creation:** 5-15 minutes (interactive Q&A, data sampling)
- **Implementation:** 1-3 minutes
- **Rest:** Same as Workflow 1
- **Total:** ~20-40 minutes

### Workflow 2B: Create Complete Page → Implement → Deploy → Test
- **Question Analysis:** 1-2 minutes
- **Artifact Decomposition:** 2-5 minutes (user confirmation)
- **Parallel Specification:** 10-30 minutes (depends on measure count + visual count)
  - Per measure: 3-5 minutes (Q&A, patterns, code gen)
  - Per visual: 2-4 minutes (type recommendation, field mapping)
- **Layout & Interaction Design:** 3-5 minutes
- **PBIR Generation:** 2-3 minutes
- **Validation:** 1-3 minutes
- **Implementation:** 2-5 minutes (creates page structure + measures)
- **Rest:** Same as Workflow 1
- **Total:** ~30-70 minutes (varies significantly with page complexity)

### Workflow 3: Compare → Decide → Merge
- **Comparison:** 3-10 minutes (depends on project size)
- **User Decision Time:** Variable (5-60 minutes)
- **Merge Execution:** 2-5 minutes
- **Validation:** 1-3 minutes
- **Total:** ~15-90 minutes (mostly user decision time)

---

## Troubleshooting Workflow Issues

### Issue: Evaluation fails at data context step

**Cause:** Authentication timeout or missing permissions

**Solution:**
- Verify workspace/dataset names are correct
- Ensure you have Read access to dataset
- Complete authentication flow promptly
- Alternative: Skip workspace/dataset parameters (proceed without data sampling)

### Issue: Implementation validation fails

**Cause:** TMDL formatting or DAX syntax errors

**Solution:**
- Review Section 2.5 (TMDL Validation) or Section 3 (DAX Validation)
- Fix issues in original findings.md Section 2
- Re-run implement command

### Issue: Merge creates unexpected results

**Cause:** Complex dependencies not captured in diff analysis

**Solution:**
- Open merged project in Power BI Desktop
- Identify specific issues
- Run evaluate workflow on merged project
- Apply targeted fixes

### Issue: Testing fails to apply filters

**Cause:** Missing filter metadata in test cases

**Solution:**
- Review Section 3 in findings.md
- Ensure filter metadata YAML blocks present
- Verify table/column names match TMDL definitions
- Alternative: Add filter metadata manually
