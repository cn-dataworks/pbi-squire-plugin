# Best Practices for Power BI Workflows

Best practices extracted from project documentation and real-world usage.

## Command Selection Best Practices

### Start with the Right Workflow

✅ **Do:** Use `/evaluate-pbi-project-file` as your starting point for most tasks
- It can analyze and recommend whether you need to fix or create
- Provides comprehensive context about the problem
- Identifies dependencies and side effects

❌ **Don't:** Jump straight to `/create-pbi-artifact-spec` unless you're certain you need a new artifact
- Evaluation might reveal an existing artifact can be modified instead
- May identify dependencies you weren't aware of

### When to Use Each Command

**Use `/evaluate-pbi-project-file` when:**
- Something is broken or incorrect
- You need to understand existing code
- You want to modify calculations or visuals
- You're unsure whether to fix or create

**Use `/create-pbi-artifact-spec` when:**
- You're certain you need a single net-new artifact
- You have a clear specification of what to build
- You want guided specification building with recommendations

**Use `/create-pbi-page-specs` when:**
- You need to design a complete dashboard page
- You have a business question to answer with multiple visuals
- You want intelligent layout, interactions, and visual type recommendations
- You need measures AND visuals created together

**Use `/implement-deploy-test-pbi-project-file` when:**
- You have a completed findings.md file
- You've reviewed and approved the proposed changes
- You're ready to apply changes to your project

**Use `/merge-powerbi-projects` when:**
- Comparing two complete project versions
- Syncing development and production models
- Adopting selective changes from another project

---

## Path and File Management Best Practices

### Always Use Absolute Paths

✅ **Good:**
```bash
--project "/mnt/c/Users/YourName/Projects/SalesReport.pbip"
--project "C:\Users\YourName\Projects\SalesReport.pbip"
```

❌ **Bad:**
```bash
--project "./SalesReport.pbip"
--project "../Projects/SalesReport.pbip"
```

### Quote Paths with Spaces

✅ **Good:**
```bash
--project "C:\My Projects\Sales Report.pbip"
--project "/mnt/c/My Projects/Sales Report.pbip"
```

❌ **Bad:**
```bash
--project C:\My Projects\Sales Report.pbip
```

### Prefer .pbip Format Over .pbix

✅ **Prefer:** Power BI Project format (`.pbip`)
- Native support for all workflows
- Visual editing capabilities (Section 2.B)
- Better for source control
- Faster processing

⚠️ **Acceptable:** PBIX files (`.pbix`)
- Will be extracted using pbi-tools
- Adds extraction time
- No visual editing support in extracted format

### Understand WSL Path Translation

**Windows paths:**
```
C:\Users\YourName\Documents\Projects
```

**Equivalent WSL paths:**
```
/mnt/c/Users/YourName/Documents/Projects
```

**Tip:** Use `pwd` command in WSL to get current directory path

---

## Data Sampling Best Practices

### Always Provide Workspace/Dataset When Possible

✅ **Recommended:**
```bash
--workspace "Sales Analytics" --dataset "Sales Model v2"
```

**Benefits:**
- Enables actual data retrieval for root cause analysis
- Provides intelligent recommendations based on real data distribution
- Validates assumptions against actual data
- Improves specification quality for new artifacts

**When to skip:**
- Dataset not yet deployed
- No XMLA endpoint access
- Working offline
- Privacy/security constraints

### Authenticate Proactively

✅ **Do:** Complete authentication at the start of the workflow
- Prevents mid-workflow timeouts
- Allows agents to run without interruption

❌ **Don't:** Delay authentication
- May cause agent timeouts
- Requires re-running workflows

---

## Problem Description Best Practices

### Be Specific and Detailed

✅ **Good descriptions:**
```
"Total Revenue measure shows $709 instead of expected $4,072 when filtered by sales rep Loy Baldwin"

"YoY Growth % measure returns BLANK for all 2024 dates, but works for 2023"

"Chart title displays 'Visual Title' instead of 'Revenue by Region' on the Sales Overview page"
```

❌ **Bad descriptions:**
```
"Fix the measure"
"It's broken"
"Measure doesn't work"
"Update the dashboard"
```

### Include Expected vs. Actual Behavior

✅ **Template:**
```
"[Component] shows [actual behavior] but should show [expected behavior]"
```

**Example:**
```
"Total Sales measure shows sum of Amount column but should calculate Quantity × Price for accurate revenue"
```

### Mention Context and Filters

✅ **Include:**
- Which visual or page has the issue
- What filters are applied
- Which users/scenarios are affected

**Example:**
```
"Total Revenue on Sales by Rep visual shows incorrect values when filtered by specific sales reps, but works correctly with no filters"
```

---

## Workflow Execution Best Practices

### Review Before Proceeding

✅ **Critical checkpoints:**

**After `/evaluate-pbi-project-file`:**
1. Read Section 1 (Investigation) - Does it correctly identify the problem?
2. Review Section 2.A (Code Changes) - Is the proposed fix correct?
3. Review Section 2.B (Visual Changes) - Are visual modifications appropriate?
4. Check Section 3 (Test Cases) - Do they cover all scenarios?

**After `/create-pbi-artifact-spec`:**
1. Read Section 1.2 (Specification) - Is this what you want?
2. Review Section 1.3 (Patterns) - Are the discovered patterns appropriate?
3. Check Section 2 (Proposed Code) - Is the implementation correct?
   - Calculation logic sound?
   - Format string appropriate?
   - Edge cases handled?

**After `/implement-deploy-test-pbi-project-file`:**
1. Check Section 2.5 (TMDL Validation) - Any format errors?
2. Check Section 2.6 (PBIR Validation) - Any visual errors?
3. Review Section 3 (DAX Validation) - Any logic issues?
4. Examine Section 4 (Implementation Results) - Did everything succeed?

### Use Validation Gates Properly

**Quality gates are mandatory:**

1. **TMDL Format Validation** (if code changes)
   - ✅ PASS → Proceed to DAX validation
   - ❌ FAIL → Fix formatting issues, re-run

2. **PBIR Structure Validation** (if visual changes)
   - ✅ PASS → Proceed to deployment
   - ⚠️ WARNINGS → Review and decide
   - ❌ FAIL → Fix issues, re-run

3. **DAX Validation** (if code changes)
   - ✅ PASS → Proceed to deployment
   - ⚠️ WARNINGS → Review warnings, may proceed
   - ❌ FAIL → Fix DAX errors, update Section 2, re-run

**Never skip validation:**
- Catching errors before deployment saves time
- Validation reports provide specific fix guidance
- Re-running is faster than debugging in production

---

## Testing Best Practices

### Use URL-Based Filtering (Preferred)

✅ **Include filter metadata in test cases:**

```yaml
filters:
  - table: Sales
    column: SalesRepID
    value: 12345
```

**Benefits:**
- More reliable than DOM interaction
- Faster test execution
- Works even if slicer UI changes

❌ **Avoid:** Relying solely on DOM interaction
- Brittle (breaks when UI changes)
- Slower execution
- Harder to maintain

### Test Incrementally

✅ **Recommended sequence:**
1. Test in development environment first
2. Validate core functionality
3. Test edge cases
4. Deploy to production
5. Monitor for unexpected issues

❌ **Don't:** Deploy directly to production without testing

---

## Deployment Best Practices

### Understand Authentication Methods

**User Authentication (Recommended for manual workflows):**
- Uses your Power BI login
- Interactive authentication via PowerShell
- Suitable for development and manual deployments

**Service Principal (Recommended for CI/CD):**
- Uses Azure app registration
- Non-interactive authentication
- Suitable for automated pipelines

### Verify Prerequisites Before Deployment

✅ **Checklist:**
- [ ] Validation gates passed
- [ ] Tested in Power BI Desktop
- [ ] Workspace access confirmed
- [ ] Authentication configured
- [ ] Backup of current production version exists

### Use Environment-Specific Deployments

```bash
--deploy DEV    # Development environment
--deploy TEST   # Testing/UAT environment
--deploy PROD   # Production environment
```

**Benefits:**
- Clear environment tracking
- Supports phased rollouts
- Easier troubleshooting

---

## Project Organization Best Practices

### Preserve Versioned Folders

✅ **Keep timestamped copies:**
```
MyProject_20250109_143022/
MyProject_20250109_151545/
MyProject_20250110_092314/
```

**Benefits:**
- Audit trail of all changes
- Easy rollback if needed
- Compare versions to understand evolution

**Storage tip:** Archive old versions after successful deployment

### Maintain Findings Files

✅ **Organize scratchpads:**
```
agent_scratchpads/
├── 20250109-fix-total-sales/
│   └── findings.md
├── 20250109-create-yoy-growth/
│   └── findings.md
└── 20250110-merge-dev-prod/
    └── findings.md
```

**Benefits:**
- Documentation of all changes
- Reasoning and decisions preserved
- Easy reference for future work

---

## Common Mistakes to Avoid

### ❌ Skipping Data Context

**Mistake:** Not providing workspace/dataset parameters

**Impact:**
- Less accurate recommendations
- No data validation
- May miss data-specific issues

**Fix:** Always provide workspace/dataset when available

### ❌ Ignoring Validation Warnings

**Mistake:** Proceeding despite validation warnings

**Impact:**
- Potential runtime errors
- Poor performance
- Unexpected behavior

**Fix:** Review all warnings, understand implications before proceeding

### ❌ Not Testing Before Production

**Mistake:** Deploying directly to production without testing

**Impact:**
- Broken reports for end users
- Emergency rollbacks
- Loss of trust

**Fix:** Always test in development environment first

### ❌ Vague Problem Descriptions

**Mistake:** "Fix the measure" without context

**Impact:**
- Incorrect diagnosis
- Wrong fixes proposed
- Wasted time iterating

**Fix:** Provide specific, detailed problem descriptions

### ❌ Modifying Original Projects

**Mistake:** Making changes directly without versioned copies

**Impact:**
- No audit trail
- Hard to rollback
- Lost change history

**Fix:** All workflows create versioned copies automatically - use them

---

## Advanced Best Practices

### Hybrid Changes Coordination

**For changes involving both code and visuals:**

✅ **Let the system coordinate:**
- Evaluation workflow detects hybrid scenarios
- Single planner ensures consistency
- Code changes inform visual changes
- Measure names in Section 2.A match references in Section 2.B

✅ **Implementation order matters:**
- Code changes applied first (creates measures/columns)
- Visual changes applied second (references measures/columns)
- Never reverse this order

### Multi-Artifact Creation

**When creating complex features:**

✅ **Use artifact decomposition:**
- System identifies all needed artifacts
- Determines dependency order
- Creates helper measures before main measures

✅ **Review artifact breakdown:**
- Section 1.0 shows what will be created
- Confirm all artifacts are needed
- Verify creation order is correct

### Focused Merging

**For large projects with many differences:**

✅ **Use --description to filter:**
```bash
--description "revenue calculations"
```

**Benefits:**
- Focus on specific area
- Reduce decision fatigue
- Faster merge process
- Less risk of unintended changes

---

## Page Design Best Practices (for `/create-pbi-page-specs`)

### Frame Questions as Business Problems

✅ **Good question framing:**
```
"Show Q4 sales performance by region and product category"
"Compare year-over-year revenue growth across sales territories"
"Identify top-performing products with trend analysis"
```

**Why:** Questions should describe WHAT to analyze, not HOW to visualize

❌ **Bad question framing:**
```
"Create a bar chart and a table"
"Add 3 KPI cards"
```

**Why:** These describe implementation, not business intent

### Trust the Visual Type Recommendations

✅ **Review pros/cons carefully:**
- Recommendations are data-driven (based on cardinality, metric type)
- Pros/cons are specific to your data
- Choose based on your analytical priorities

⚠️ **When to override:**
- User audience preference (executives prefer cards over tables)
- Organizational standards (always use specific visual types)
- Specific feature requirements (need drill-through, custom visual)

### Review Layout for Analytical Flow

✅ **Check Section 3 (Layout Plan):**
- Do KPIs appear first (top-left)?
- Is primary analysis in middle zones?
- Are filters in consistent location (bottom)?
- Does layout support user's analytical workflow?

⚠️ **Red flags:**
- Filters in top zone (disrupts visual hierarchy)
- Primary analysis at bottom (buried)
- Overlapping visuals (validation should catch this)

### Validate Interaction Logic

✅ **Check Section 4 (Interaction Design):**
- Do cross-filtering interactions make analytical sense?
- Are bi-directional filters appropriate (or should be one-way)?
- Do drill-through targets address user's detail needs?
- Are slicers configured to filter all visuals?

⚠️ **Common issues:**
- KPI cards sending filters (should receive only)
- Detail tables filtering summary visuals (reverse flow)
- Missing drill-through for high-cardinality dimensions

### Plan Helper Pages Early

✅ **Review Section 6 (Helper Page Recommendations):**
- Identify drill-through targets BEFORE implementing
- Consider creating helper pages first if they're dependencies
- Plan multi-page workflows for complex dashboards

**Approach:**
1. Create main page first (with drill-through identified in Section 6)
2. Review in Power BI Desktop
3. Create helper pages using findings from Section 6
4. Link via drill-through in Desktop UI

### Use Data Sampling for Better Results

✅ **Highly recommended for page design:**
```bash
--workspace "Analytics" --dataset "Sales Model"
```

**Benefits for page workflow:**
- Better measure recommendations (column selection, filtering)
- Visual type recommendations based on actual cardinality
- Sorting recommendations based on data distribution
- Formatting recommendations based on value ranges

**Impact:** 2-3x better recommendation quality with data sampling

---

## Performance Best Practices

### For Large Projects

✅ **Optimize workflow execution:**
- Use focused descriptions (merge workflow)
- Limit scope to specific components
- Run validation only on changed objects

### For Complex Calculations

✅ **During creation:**
- Provide detailed specification upfront
- Leverage pattern discovery
- Review generated code for optimization opportunities

---

## Collaboration Best Practices

### When Working in Teams

✅ **Recommended practices:**
- Use merge workflow to integrate team changes
- Document decisions in findings files
- Maintain consistent naming conventions (discovered via pattern analysis)
- Share scratchpad folders for knowledge transfer

### Source Control Integration

✅ **Git-friendly workflows:**
- .pbip format works well with Git
- Commit versioned folders as milestones
- Tag releases after successful deployments
- Include findings.md files in commits for context
