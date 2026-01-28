# Workflow Decision Tree

This document helps map user intents to the appropriate Power BI workflow command.

## Pre-Check: Is this a PBIX file?

### 0. User references a .pbix file → CONVERSION REQUIRED

**Detection:** User provides a path ending in `.pbix` or mentions "my pbix file", "desktop file"

**STOP** - Do not proceed to any workflow until conversion is complete.

**What to do:**
1. Read `.claude/powerbi-analyst.json` → `projectPath` for the configured projects folder
2. Extract project name from the .pbix filename (without extension)
3. Explain that each PBIP needs its own container folder
4. **Offer to create the folder** for them
5. Guide user through Power BI Desktop Save As steps

**Message to display:**
```
📦 PBIX FILE DETECTED

You've pointed to a .pbix file. This binary format limits what can be analyzed.

⚠️  IMPORTANT: Each PBIP project needs its own folder!

When you save a PBIP, Power BI creates MULTIPLE files:
  - <project-name>.pbip
  - <project-name>.SemanticModel/
  - <project-name>.Report/

Without a container folder, these mix with other projects!

Would you like me to create the project folder?

  [Y] Yes, create: <projects-folder>/<project-name>/
  [N] No, I'll handle it myself
```

**If user selects [Y]:**
1. Create folder: `mkdir -p "<projects-folder>/<project-name>"`
2. Show Save As instructions pointing to that folder
3. Wait for user to complete conversion

**Why this is first:**
- PBIX files have severely limited analysis capability
- Converting unlocks M code, data lineage, and visual editing
- Users often have files on Desktop that need to be moved to the proper location
- Each PBIP creates multiple files that need to be contained

---

## Primary Decision: What do you need to do?

### 1. "I have a problem/issue/bug with existing code"

**Command:** `/evaluate-pbi-project-file`

**User statements that match:**
- "My measure shows wrong totals"
- "The calculation is incorrect"
- "I need to fix a broken measure"
- "Something is wrong with my DAX"
- "I need to debug this calculation"
- "The visual title needs to change"
- "I need to update the chart colors"
- "The dashboard layout needs adjustment"

**What it does:**
- Analyzes existing code/visuals
- Diagnoses problems
- Proposes fixes
- Creates findings report for implementation

**Next step:** Review findings.md, then use `/implement-deploy-test-pbi-project-file`

---

### 2. "I need to create something new"

**Decision:** Single artifact or complete page?

#### 2A. "Create a single artifact (measure, column, table, or visual)"

**Command:** `/create-pbi-artifact`

**User statements that match:**
- "Create a YoY growth measure"
- "Add a new calculated column"
- "Build a KPI card"
- "I want to add a new table"
- "Create a visual showing sales by region"
- "Add a measure for customer count"

**What it does:**
- Guides you through specification
- Analyzes data model
- Discovers existing patterns
- Generates implementation-ready code

**Next step:** Review findings.md, then use `/implement-deploy-test-pbi-project-file`

---

#### 2B. "Create a complete dashboard page"

**Command:** `/create-pbi-page-specs`

**User statements that match:**
- "Create a page showing Q4 sales by region"
- "Build a dashboard page for revenue analysis"
- "Design a page answering [business question]"
- "Add a new page with KPIs and charts"
- "Create a sales performance page"
- "I need a page to analyze customer trends"

**What it does:**
- Analyzes your business question
- Identifies needed measures AND visuals
- Designs optimal layout (research-based coordinates)
- Creates cross-filtering and interactions
- Generates complete PBIR page specifications
- Recommends helper pages for drill-through

**Key difference from /create-pbi-artifact:**
- Creates ENTIRE PAGE (measures + visuals + layout + interactions)
- Multiple artifacts in one workflow
- Layout and interaction design included
- Parallel measure + visual specification

**Next step:** Review findings.md, then use `/implement-deploy-test-pbi-project-file`

---

### 3. "I have a plan ready and need to apply it"

**Command:** `/implement-deploy-test-pbi-project-file`

**User statements that match:**
- "Apply these changes"
- "Implement the plan"
- "Deploy this to Power BI Service"
- "Execute the findings report"
- "I'm ready to make these changes"

**What it does:**
- Applies code/visual changes
- Validates TMDL format and DAX logic
- Optionally deploys to service
- Optionally runs automated tests

**Prerequisites:** Must have findings.md from evaluate or create workflow

---

### 4. "I need to merge/compare two projects"

**Command:** `/merge-powerbi-projects`

**User statements that match:**
- "Compare dev and prod models"
- "Merge these two projects"
- "What's different between these projects?"
- "Combine changes from both versions"
- "Sync development into production"

**What it does:**
- Compares two projects
- Explains business impact
- Lets you choose which version to keep
- Creates new merged project

**Result:** New timestamped merged project folder

---

## Secondary Decision: What information do I need?

### For `/evaluate-pbi-project-file`:
- ✅ **Required:** Project path (.pbip folder or .pbix file)
- ✅ **Required:** Problem description (what's wrong?)
- ⭐ **Recommended:** Workspace name + dataset name (for data sampling)
- 📷 **Optional:** Screenshot showing the issue

### For `/create-pbi-artifact`:
- ✅ **Required:** Project path (.pbip folder)
- ✅ **Required:** What to create (description)
- 📝 **Optional:** Artifact type (measure, calculated-column, table, visual, multi)
- ⭐ **Recommended:** Workspace name + dataset name (for data sampling)

### For `/implement-deploy-test-pbi-project-file`:
- ✅ **Required:** Path to findings.md file
- 🚀 **Optional:** Deploy environment name (DEV, TEST, PROD)
- 🧪 **Optional:** Dashboard URL (for automated testing)

### For `/merge-powerbi-projects`:
- ✅ **Required:** Main project path (baseline)
- ✅ **Required:** Comparison project path (source of changes)
- 🎯 **Optional:** Description (focus area to filter differences)

---

## Common Scenarios

### Scenario: "User points to a .pbix file on their Desktop"
```
1. User: "Analyze C:\Users\Me\Desktop\SalesReport.pbix"
2. STOP - Display conversion message explaining folder structure
3. Offer: "Would you like me to create the folder C:\PBI\SalesReport\ for you?"
4. User: "Yes"
5. Create folder: mkdir -p "C:\PBI\SalesReport"
6. Show Save As instructions: Open pbix, File → Save As → PBIP, navigate to C:\PBI\SalesReport\
7. User completes conversion in Power BI Desktop
8. User: "Done"
9. Now proceed with requested workflow using C:\PBI\SalesReport as the project path
```

### Scenario: "Fix a broken measure"
```
1. /evaluate-pbi-project-file --project "path" --description "Total Sales shows wrong value"
2. Review findings.md
3. /implement-deploy-test-pbi-project-file --findings "findings.md"
```

### Scenario: "Add a new measure"
```
1. /create-pbi-artifact --project "path" --type measure --description "YoY Revenue Growth %"
2. Review findings.md specification
3. /implement-deploy-test-pbi-project-file --findings "findings.md" --deploy DEV --dashboard-url "https://..."
```

### Scenario: "Create a complete dashboard page"
```
1. /create-pbi-page-specs --project "path" --question "Show Q4 sales by region with YoY growth" --workspace "Analytics" --dataset "Sales Model"
2. Review findings.md (all 8 sections - especially layout and interactions)
3. /implement-deploy-test-pbi-project-file --findings "findings.md" --deploy DEV
4. (Optional) Create helper pages identified in Section 6
```

### Scenario: "Merge development into production"
```
1. /merge-powerbi-projects --main "prod-path" --comparison "dev-path"
2. Review combined analysis
3. Respond with decisions: "diff_001: Comparison, diff_002: Main, ..."
4. Test merged project in Power BI Desktop
```

### Scenario: "Update visual and calculation together"
```
1. /evaluate-pbi-project-file --project "path" --description "Update Total Revenue calculation AND change chart title"
2. Review hybrid changes (Section 2.A for code, Section 2.B for visual)
3. /implement-deploy-test-pbi-project-file --findings "findings.md"
```

---

## When Uncertain

**If user request is vague:**
- Ask clarifying questions
- Is it about existing code (evaluate) or new artifact (create)?
- What specifically needs to change?

**If multiple workflows apply:**
- Start with `/evaluate-pbi-project-file` for analysis
- It can identify if creation is better suited

**If user just says "help with Power BI":**
- Ask: "What would you like to do?"
- Options: Fix something, Create something, Compare projects, or Learn about workflows
