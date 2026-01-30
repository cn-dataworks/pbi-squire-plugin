---
name: review-ux-pbi-dashboard
description: Analyze Power BI dashboard UX by capturing screenshots and generating improvement recommendations for chart types, layout, accessibility, labeling, and interactions
pattern: ^/review-ux-pbi-dashboard\s+(.+)$
---

# Review UX Power BI Dashboard

This slash command captures dashboard screenshots and analyzes them for UX improvements, generating implementation-ready recommendations compatible with `/implement-deploy-test-pbi-project-file`.

**This is a Developer-only feature.**

## Tracing Output (Required)

**IMPORTANT:** This workflow MUST output trace markers for visibility.

**On workflow start, output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 WORKFLOW: review-ux-pbi-dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Before each phase, output:**
```
📋 PHASE [N]: [Phase Name]
   └─ [What this phase does]
```

**On workflow complete, output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WORKFLOW COMPLETE: review-ux-pbi-dashboard
   └─ Output: [findings file path]
   └─ Next: /implement-deploy-test-pbi-project-file --findings "<path>"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Usage

```bash
# Analyze published dashboard via URL
/review-ux-pbi-dashboard --url <published-power-bi-url>

# Analyze local project (auto-publish, analyze, cleanup)
/review-ux-pbi-dashboard --project <path-to-pbip> [--cleanup]
```

### Parameters

- `--url` (option 1): Published Power BI Service URL to analyze
- `--project` (option 2): Path to local .pbip project folder (will auto-publish)
- `--cleanup` (optional): Auto-cleanup temporary publish without prompting (only with --project)

### Examples

```bash
# Analyze live dashboard
/review-ux-pbi-dashboard --url "https://app.powerbi.com/groups/abc123/reports/def456"

# Analyze local project with auto-cleanup
/review-ux-pbi-dashboard --project "C:\Reports\SalesDashboard" --cleanup

# Analyze local project with cleanup prompt
/review-ux-pbi-dashboard --project "./FinanceReport"
```

---

## Workflow Phases

### Phase 0: Prerequisites Check

**Objective:** Verify environment before starting

**Step 0.1: Check Playwright MCP Availability**

Attempt to call `browser_tabs(action: "list")` to verify Playwright MCP is responding.

**If MCP not available:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ WORKFLOW BLOCKED: review-ux-pbi-dashboard
   └─ Playwright MCP not available
   └─ Install: npx @playwright/mcp@latest --extension
   └─ Add to .mcp.json and restart Claude Code
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**If MCP available:** Continue to Phase 0.2

**Step 0.2: Check Temp Workspace Config (if --project provided)**

Read `.claude/pbi-squire.json` for `tempWorkspace` setting.

**If `tempWorkspace` not configured:**
```
⚠️  TEMP WORKSPACE NOT CONFIGURED

UX Review with --project requires publishing to Power BI Service.
Please specify a workspace for temporary publishing.

Options:
1. Add to .claude/pbi-squire.json: { "tempWorkspace": "Your_Workspace_Name" }
2. Provide workspace name now: _______________

This workspace should be a development/sandbox workspace.
```

Wait for user input, then save to config if provided.

---

### Phase 1: Input Validation & Setup

**Objective:** Parse arguments and create workspace

**Step 1.1: Parse Arguments**

Parse command arguments:
- `--url`: Power BI Service URL (entry point 1)
- `--project`: Local .pbip project path (entry point 2)
- `--cleanup`: Auto-cleanup flag

**Validation:**
- Exactly one of `--url` OR `--project` must be provided
- If `--project`: Path must exist and contain .pbip structure

**Step 1.2: Detect Entry Point**

```
IF --url provided:
    entry_point = "PUBLISHED_URL"
    Skip to Phase 1.5 (Anonymization Warning)

IF --project provided:
    entry_point = "LOCAL_PROJECT"
    Continue to Phase 1.3
```

**Step 1.3: Validate Project Structure (LOCAL_PROJECT only)**

Invoke `powerbi-verify-pbiproject-folder-setup` agent to validate project.

**Step 1.4: Create Scratchpad Workspace**

1. Generate timestamp: `YYYYMMDD-HHMMSS`
2. Create folder: `agent_scratchpads/<timestamp>-ux-review/`
3. Create `screenshots/` subfolder
4. Create empty `findings.md` with header:

```markdown
# UX Review: [Dashboard/Project Name]

**Created**: [Timestamp]
**Source**: [URL or Project Path]
**Entry Point**: [PUBLISHED_URL or LOCAL_PROJECT]

---

## Prerequisites

**Playwright MCP**: Available
**Data Mode**: [Pending user confirmation]

---
```

---

### Phase 1.5: Anonymization Warning

**Objective:** Warn user to verify data is anonymized before capturing screenshots

**Display Warning:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  DATA ANONYMIZATION REMINDER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Screenshots will be captured and may be shared.
Please verify before proceeding:

1. Check DataMode parameter is set to "Anonymized"
2. Refresh the data in Power BI Desktop (Close & Apply)
3. Confirm the dashboard shows anonymized data

If you haven't set up anonymization yet, run:
/setup-data-anonymization --project "<path>"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Have you verified the data is anonymized?

[Continue] - Yes, data is anonymized and refreshed
[Cancel] - No, I need to set up anonymization first
```

**If Cancel:** Exit workflow with message about running /setup-data-anonymization

**If Continue:** Update findings.md with:
```markdown
**Data Mode**: User confirmed anonymized
```

---

### Phase 2: Dashboard Access

**Objective:** Navigate to live dashboard that can be screenshotted

**Entry Point A: Published URL**

1. Navigate to URL using Playwright:
   ```
   └─ 🔌 [MCP] browser_navigate
   └─    URL: [provided URL]
   ```

2. Wait for page load:
   ```
   └─ 🔌 [MCP] browser_wait_for
   └─    Waiting for Power BI report content to load
   ```

3. If authentication required, prompt user to complete sign-in in browser

**Entry Point B: Local Project (Auto-Publish)**

1. Read `tempWorkspace` from config

2. Invoke pbi-tools deploy:
   ```bash
   pbi-tools deploy . [tempWorkspace]
   ```

   ```
   └─ 🔌 [BASH] pbi-tools deploy
   └─    Workspace: [tempWorkspace]
   └─    ✅ Published successfully
   ```

3. Capture published URL from deployment output

4. Store cleanup info in `cleanup_info.json`:
   ```json
   {
     "workspace": "[tempWorkspace]",
     "reportName": "[Report Name]",
     "publishedUrl": "[URL]",
     "cleanup_required": true
   }
   ```

5. Navigate to published report using Playwright

---

### Phase 3: Screenshot Capture

**Objective:** Capture screenshots of every dashboard page

**Step 3.1: Discover Pages**

Use `browser_snapshot` to get accessibility tree and parse for page navigation elements.

```
└─ 🔌 [MCP] browser_snapshot
└─    Discovering dashboard pages...
└─    📄 Found [N] pages: [Page 1], [Page 2], ...
```

**Step 3.2: Capture Each Page**

For each page:

```
📋 PAGE [N]: [Page Name]
   └─ 🔌 [MCP] browser_click
   └─    Navigating to page: [Page Name]
   └─ 🔌 [MCP] browser_wait_for
   └─    Waiting for visuals to load (2 seconds)
   └─ 🔌 [MCP] browser_take_screenshot
   └─    Filename: screenshots/page-[N]-[kebab-name].png
   └─    ✅ Screenshot captured
```

**Step 3.3: Update Findings with Screenshot Inventory**

```markdown
## Section 1: Investigation

### 1.1 Screenshots Captured

| Page # | Page Name | Screenshot |
|--------|-----------|------------|
| 1 | Sales Overview | [page-1-sales-overview.png](screenshots/page-1-sales-overview.png) |
| 2 | Regional Performance | [page-2-regional-performance.png](screenshots/page-2-regional-performance.png) |
```

---

### Phase 4: Visual UX Analysis

**Objective:** Analyze screenshots for chart type, hierarchy, accessibility, and labeling issues

**Invoke Agent:**

For each page screenshot, invoke `powerbi-ux-reviewer` agent:

```
└─ 🤖 [AGENT] powerbi-ux-reviewer
└─    Analyzing: [Page Name] (screenshots/page-N.png)
└─    📊 Visual Inventory: [N] visuals identified
└─    🔍 Evaluating chart types...
└─    🔍 Evaluating visual hierarchy...
└─    🔍 Evaluating color/accessibility...
└─    🔍 Evaluating labeling...
└─ 🤖 [AGENT] powerbi-ux-reviewer complete
└─    Findings: [N] issues ([N] CRITICAL, [N] MAJOR, [N] MINOR)
```

Agent writes findings to Section 1.4 in findings.md.

---

### Phase 4.5: Interaction Analysis

**Objective:** Review cross-filtering and visual coordination based on finalized visual recommendations

**Prerequisites:** Visual analysis from Phase 4 must be complete

**Invoke Agent (Interaction Mode):**

```
└─ 🤖 [AGENT] powerbi-ux-reviewer (Interaction Analysis)
└─    Context: Visual recommendations from Phase 4
└─    🔍 Analyzing cross-filtering relationships...
└─    🔍 Identifying drill-through opportunities...
└─    🔍 Evaluating slicer coordination...
└─ 🤖 [AGENT] powerbi-ux-reviewer complete
└─    Interaction Findings: [N] issues
```

Agent writes findings to Section 1.5 in findings.md.

---

### Phase 5: Implementation Plan Generation

**Objective:** Convert UX recommendations into actionable edit plans

**Step 5.1: Generate Section 2 Structure**

For each finding from Phases 4 and 4.5:

**VISUAL_CHANGE findings:**
```markdown
## Section 2: Proposed Changes

### 2.B Visual Changes

#### F-[N]: [Finding Title]

**Change Type**: VISUAL_TYPE_CHANGE

**Target**: Visual #[N] on Page "[Page Name]"

**Current**: [Current Visual Type]
**Recommended**: [New Visual Type]

**Rationale**: [From agent finding]

**Implementation Note**: Visual type changes may require Power BI Desktop.
Mark as manual action if PBIR editing not supported.
```

**SETTINGS_CHANGE findings:**
```markdown
#### F-[N]: [Finding Title]

**Change Type**: SETTINGS_CHANGE

**Target**: Visual #[N] on Page "[Page Name]"

**Property**: [Property path]
**Current Value**: [If known]
**New Value**: "[Recommended value]"

**Rationale**: [From agent finding]
```

**INTERACTION_CHANGE findings:**
```markdown
### 2.C Interaction Changes

#### F-[N]: [Finding Title]

**Change Type**: INTERACTION_CHANGE

**Source Visual**: Visual #[N]
**Target Visual(s)**: Visual #[M], #[O]

**Current Behavior**: [Description]
**Recommended Behavior**: [Description]

**Rationale**: [From agent finding]

**Implementation Note**: Interaction changes require Power BI Desktop.
```

---

### Phase 6: Findings Consolidation

**Objective:** Compile complete findings.md ready for `/implement-deploy-test`

**Final Structure:**

```markdown
# UX Review: [Dashboard Name]

**Created**: [Timestamp]
**Source**: [URL or Project Path]
**Pages Analyzed**: [N]
**Issues Found**: [Total]
**By Type**: [N] VISUAL_CHANGE | [N] SETTINGS_CHANGE | [N] INTERACTION_CHANGE

---

## Prerequisites

**Playwright MCP**: Available
**Data Mode**: User confirmed anonymized

---

## Section 1: Investigation

### 1.1 Screenshots Captured
[Screenshot inventory table]

### 1.4 UX Review (Screenshot Analysis)
[Visual inventory and findings per page]

### 1.5 Interaction Review
[Interaction analysis findings]

---

## Section 2: Proposed Changes

### 2.B Visual Changes
[VISUAL_CHANGE and SETTINGS_CHANGE findings]

### 2.C Interaction Changes
[INTERACTION_CHANGE findings]

---

## Recommendations Summary

| # | Finding | Page | Visual(s) | Category | Severity | Type |
|---|---------|------|-----------|----------|----------|------|
[Summary table]

**Priority Order for Implementation:**
1. [CRITICAL findings first]
2. [MAJOR findings]
3. [MINOR findings]

---

## Next Steps

1. Review findings above
2. Run: `/implement-deploy-test-pbi-project-file --findings "[path]/findings.md"`
3. Complete any manual actions noted (Power BI Desktop required)
4. Re-run UX review to verify improvements
```

---

### Phase 7: Cleanup (LOCAL_PROJECT only)

**Objective:** Remove temporarily published report from Power BI Service

**If --cleanup flag provided:** Skip prompt, delete automatically

**If no --cleanup flag:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 CLEANUP: Temporary Published Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The following was published temporarily for UX review:
  Workspace: [tempWorkspace]
  Report: [Report Name]

Options:
  [D] Delete now (recommended)
  [K] Keep for manual inspection

Your choice: ___
```

**If Delete:**
```
└─ 🔌 [BASH] Removing temporary publish
└─    ✅ Temporary report deleted from Power BI Service
```

**If Keep:**
```
⚠️ Remember to manually delete the temporary report from:
   Workspace: [tempWorkspace]
   Report: [Report Name]
```

---

## Workflow Complete

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WORKFLOW COMPLETE: review-ux-pbi-dashboard
   └─ Output: agent_scratchpads/[timestamp]-ux-review/findings.md
   └─ Screenshots: agent_scratchpads/[timestamp]-ux-review/screenshots/
   └─ Issues Found: [N] ([N] CRITICAL, [N] MAJOR, [N] MINOR)
   └─ Next: /implement-deploy-test-pbi-project-file --findings "<path>/findings.md"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Error Handling

**Error: Playwright MCP not available**
- Block workflow
- Provide installation instructions
- Do not attempt screenshot capture

**Error: Power BI authentication required**
- Pause workflow
- Prompt user to complete sign-in in browser
- Resume when authenticated

**Error: pbi-tools deploy fails**
- Display error message
- Suggest checking workspace permissions
- Suggest using --url mode instead

**Error: Screenshot capture fails**
- Retry once with longer wait
- If still fails, note which page failed
- Continue with other pages

**Error: No pages found in dashboard**
- Check if URL is correct
- Check if authentication completed
- Suggest manual navigation and retry

---

## Integration

### Input From:
- Published Power BI dashboard URL
- Local .pbip project with anonymized data

### Output To:
- `/implement-deploy-test-pbi-project-file --findings "<path>"`
- Manual Power BI Desktop actions (for unsupported changes)

### Config File:
`.claude/pbi-squire.json`:
```json
{
  "projectPath": "...",
  "dataSensitiveMode": true,
  "tempWorkspace": "Dev_Sandbox"
}
```
