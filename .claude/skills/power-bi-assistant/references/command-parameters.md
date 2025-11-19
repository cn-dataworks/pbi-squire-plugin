# Command Parameters Reference

Detailed breakdown of parameters for each Power BI workflow command.

## `/evaluate-pbi-project-file`

### Required Parameters

**`--project <path>`**
- **Purpose:** Path to your Power BI Project folder or file
- **Formats accepted:**
  - `.pbip` folder (Power BI Project format) - PREFERRED
  - `.pbix` file (will be extracted using pbi-tools)
  - pbi-tools extracted folder
- **Examples:**
  - Windows: `C:\Users\YourName\Documents\Projects\SalesReport.pbip`
  - WSL: `/mnt/c/Users/YourName/Documents/Projects/SalesReport.pbip`
- **Tips:** Always use absolute paths, not relative

**`--description "<text>"`**
- **Purpose:** Describe the problem or change needed
- **Be specific:** Include what's wrong AND what you expect
- **Good examples:**
  - `"Total Sales measure shows $709 instead of expected $4,072"`
  - `"YoY Growth % measure returns blank for 2024 data"`
  - `"Chart title shows 'Visual Title' instead of 'Revenue by Region'"`
- **Bad examples:**
  - `"Fix the measure"` (too vague)
  - `"It's broken"` (no context)

### Optional Parameters

**`--image <path>`**
- **Purpose:** Provide screenshot showing the issue
- **When to use:** Visual problems, dashboard layout issues
- **Example:** `C:\Screenshots\dashboard_issue.png`

**`--workspace <name>`**
- **Purpose:** Power BI workspace name for data sampling
- **Benefits:** Enables actual data retrieval for root cause analysis
- **Example:** `"Sales Analytics Workspace"`
- **Note:** Requires `--dataset` parameter

**`--dataset <name>`**
- **Purpose:** Dataset/semantic model name in the workspace
- **Example:** `"Sales Data Model"`
- **Note:** Required if `--workspace` provided

### Full Example
```bash
/evaluate-pbi-project-file --project "/mnt/c/Projects/SalesReport.pbip" --description "Total Revenue measure shows incorrect totals when filtered by sales rep" --workspace "Analytics" --dataset "Sales Model"
```

---

## `/create-pbi-artifact`

### Required Parameters

**`--project <path>`**
- **Purpose:** Path to Power BI Project folder
- **Format:** Must be `.pbip` format (not `.pbix`)
- **Examples:**
  - Windows: `C:\Projects\SalesReport.pbip`
  - WSL: `/mnt/c/Projects/SalesReport.pbip`

**`--description "<text>"`**
- **Purpose:** Describe what you want to create
- **Be specific:** Include purpose, calculation method, desired format
- **Good examples:**
  - `"Create YoY Revenue Growth % measure comparing current year to prior year"`
  - `"Add calculated column for customer full name combining first and last name"`
  - `"Build KPI card showing Total Sales with target comparison"`
- **Bad examples:**
  - `"New measure"` (too vague)
  - `"Sales calc"` (unclear what to calculate)

### Optional Parameters

**`--type <artifact-type>`**
- **Purpose:** Specify what type of artifact to create
- **Options:**
  - `measure` - DAX measure
  - `calculated-column` - Calculated column in a table
  - `table` - Calculated table
  - `visual` - Report visual (card, chart, etc.)
  - `auto` - Let the system detect (default)
  - `multi` - Multiple related artifacts
- **Default:** `auto` (detects from description)
- **Example:** `--type measure`

**`--workspace <name>`** and **`--dataset <name>`**
- Same as `/evaluate-pbi-project-file`
- **Benefits:** Enables data sampling for intelligent recommendations

### Full Example
```bash
/create-pbi-artifact --project "/mnt/c/Projects/SalesReport.pbip" --type measure --description "YoY Revenue Growth % comparing current year to same period last year, formatted as percentage" --workspace "Analytics" --dataset "Sales Model"
```

---

## `/create-pbi-page-specs`

### Required Parameters

**`--project <path>`**
- **Purpose:** Path to Power BI Project folder
- **Format:** Must be `.pbip` format with `.Report` folder
- **Examples:**
  - Windows: `C:\Projects\SalesReport.pbip`
  - WSL: `/mnt/c/Projects/SalesReport.pbip`
- **Important:** This workflow requires .Report folder for page creation (native .pbip format)

**`--question "<text>"`**
- **Purpose:** Business question this page should answer
- **Be specific:** Include metrics, dimensions, and analytical intent
- **Good examples:**
  - `"Show Q4 sales performance by region and product category"`
  - `"Compare year-over-year revenue growth across sales territories"`
  - `"Display executive KPI summary with top 10 products"`
  - `"Analyze customer retention trends by segment"`
- **Bad examples:**
  - `"Sales page"` (too vague - what about sales?)
  - `"Dashboard"` (what question should it answer?)

### Optional Parameters

**`--workspace <name>`** and **`--dataset <name>`**
- Same as `/create-pbi-artifact`
- **Benefits:** Enables data sampling for BOTH measure and visual recommendations
- **Highly recommended** for page design

**`--page-name "<name>"`**
- **Purpose:** Custom name for the dashboard page
- **Default:** Auto-generated from question (e.g., "Q4 Sales by Region")
- **Example:** `--page-name "Executive Summary"`
- **Note:** Page names should be descriptive and user-friendly

### Full Example
```bash
/create-pbi-page-specs --project "/mnt/c/Projects/SalesReport.pbip" --question "Show Q4 sales performance by region and product category with year-over-year growth comparison" --workspace "Analytics" --dataset "Sales Model" --page-name "Q4 Sales Performance"
```

---

## `/implement-deploy-test-pbi-project-file`

### Required Parameters

**`--findings "<path>"`**
- **Purpose:** Path to findings.md file from evaluate or create workflow
- **Location:** Usually in `agent_scratchpads/<timestamp>-<name>/findings.md`
- **Examples:**
  - Windows: `C:\Users\YourName\Documents\power_bi_analyst\agent_scratchpads\20250109-fix-sales\findings.md`
  - WSL: `/mnt/c/Users/YourName/Documents/power_bi_analyst/agent_scratchpads/20250109-fix-sales/findings.md`
- **Tip:** Use the full path shown after evaluate/create workflow completes

### Optional Parameters

**`--deploy "<environment>"`**
- **Purpose:** Deploy to Power BI Service after implementing changes
- **Format:** Environment name (any string)
- **Common values:** `DEV`, `TEST`, `PROD`, `UAT`
- **Example:** `--deploy PROD`
- **Prerequisites:**
  - Power BI PowerShell module installed
  - Active Power BI login
  - Contributor/Admin role on workspace

**`--dashboard-url "<url>"`**
- **Purpose:** URL of deployed dashboard for automated testing
- **When to use:** After deployment to validate changes
- **Example:** `--dashboard-url "https://app.powerbi.com/groups/abc123/reports/def456"`
- **Requires:** Playwright MCP available

### Full Example
```bash
/implement-deploy-test-pbi-project-file --findings "/mnt/c/Documents/agent_scratchpads/20250109-fix-sales/findings.md" --deploy PROD --dashboard-url "https://app.powerbi.com/groups/workspace-id/reports/report-id"
```

---

## `/merge-powerbi-projects`

### Required Parameters

**`--main "<path>"`**
- **Purpose:** Path to the main/baseline Power BI project (your target)
- **Format:** `.pbip` folder
- **Example:** `/mnt/c/Projects/SalesReport_PROD.pbip`
- **Role:** This is the project you're merging INTO

**`--comparison "<path>"`**
- **Purpose:** Path to the comparison project (source of changes)
- **Format:** `.pbip` folder
- **Example:** `/mnt/c/Projects/SalesReport_DEV.pbip`
- **Role:** This project contains changes you want to consider merging

### Optional Parameters

**`--description "<focus>"`**
- **Purpose:** Filter differences to specific topic/area
- **When to use:** Large projects where you only want specific changes
- **Examples:**
  - `"revenue calculations"` - Only show revenue-related changes
  - `"customer segmentation"` - Filter to customer measures/visuals
  - `"date tables"` - Show only date/time intelligence changes
- **Behavior:** Uses semantic matching (includes related terms and dependencies)

### Full Example
```bash
/merge-powerbi-projects --main "/mnt/c/Projects/Sales_PROD.pbip" --comparison "/mnt/c/Projects/Sales_DEV.pbip" --description "revenue calculations"
```

---

## Path Formatting Best Practices

### Windows Paths
```
C:\Users\YourName\Documents\Projects\Report.pbip
C:\Projects\SalesReport.pbip
```

### WSL Paths
```
/mnt/c/Users/YourName/Documents/Projects/Report.pbip
/mnt/c/Projects/SalesReport.pbip
```

### Common Mistakes
- ❌ Using relative paths: `./Projects/Report.pbip`
- ❌ Missing quotes for paths with spaces: `C:\My Projects\Report.pbip`
- ✅ Always use absolute paths: `"C:\My Projects\Report.pbip"`
- ✅ Quote paths with spaces: `"/mnt/c/My Projects/Report.pbip"`

---

## Authentication Parameters (Workspace + Dataset)

When providing `--workspace` and `--dataset`:

**Benefits:**
- Enables actual data sampling
- Provides intelligent recommendations based on real data
- Improves root cause analysis accuracy

**Requirements:**
- Active Power BI account
- Access to the workspace and dataset
- XMLA endpoint enabled (usually automatic)

**Authentication Flow:**
- First-time: Device code flow (browser authentication)
- Subsequent: Cached token (valid for period)

**Example:**
```bash
--workspace "Sales Analytics Workspace" --dataset "Sales Data Model v2"
```

**Tip:** Workspace and dataset names are case-sensitive and must match exactly
