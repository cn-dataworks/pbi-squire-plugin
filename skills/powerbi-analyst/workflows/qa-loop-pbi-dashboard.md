---
name: qa-loop-pbi-dashboard
description: Automated QA loop for Power BI dashboard deployment with GitHub Actions monitoring and live report inspection for error detection
pattern: ^/qa-loop-pbi-dashboard\s+(.+)$
---

# QA Loop for Power BI Dashboard

**This is a Pro-only feature.**

This slash command orchestrates an automated quality assurance loop for Power BI dashboards that follows a "Deploy → Inspect → Fix" cycle. It monitors deployment via GitHub Actions and inspects the live report for runtime errors (grey boxes, crashes, broken visuals).

**Note:** This workflow assumes code has already been validated through the `/implement-deploy-test-pbi-project-file` workflow. It focuses on detecting **runtime/deployment errors**, not syntax errors.

## Usage

```bash
/qa-loop-pbi-dashboard --project "<path>" --repo "<owner/repo>" [options]
```

### Parameters

- `--project` (required): Path to PBIP project folder
- `--repo` (required): GitHub repository in `owner/repo` format
- `--report-url` (optional): Published Power BI report URL for DOM inspection
- `--workflow` (optional): GitHub Actions workflow file name (default: `deploy.yml`)
- `--max-retries` (optional): Maximum QA loop iterations (default: 3)
- `--timeout` (optional): Deployment monitoring timeout in seconds (default: 600)
- `--design-critique` (optional): Enable design standards critique during DOM inspection (default: false)

### Examples

```bash
# Basic usage with project and repo
/qa-loop-pbi-dashboard --project "C:\Projects\SalesReport.Report" --repo "myorg/sales-report"

# With specific report URL for inspection
/qa-loop-pbi-dashboard --project "C:\Projects\SalesReport.Report" --repo "myorg/sales-report" --report-url "https://app.powerbi.com/reports/abc123"

# With custom workflow and timeout
/qa-loop-pbi-dashboard --project "C:\Projects\SalesReport.Report" --repo "myorg/sales-report" --workflow "power-bi-deploy.yml" --timeout 900

# With design critique enabled (checks layout, colors, typography against standards)
/qa-loop-pbi-dashboard --project "C:\Projects\SalesReport.Report" --repo "myorg/sales-report" --report-url "https://app.powerbi.com/reports/abc123" --design-critique
```

## Prerequisites

Before running this workflow, ensure:

1. **PBIP Project**: Project must be in Power BI Project (`.pbip`) format with `.Report` and/or `.SemanticModel` folders
2. **GitHub Repository**: Project must be in a GitHub repository with a deployment workflow
3. **GitHub CLI**: `gh` must be installed and authenticated (`gh auth login`)
4. **Playwright MCP**: Playwright MCP server must be available for DOM inspection
5. **Power BI Session**: User must be logged into Power BI Service in their browser (for Playwright to reuse session)
6. **Code Already Validated**: Run `/implement-deploy-test-pbi-project-file` first to validate TMDL/PBIR syntax

**New to CI/CD?** If you're starting with just a dashboard on your desktop (.pbix file), see `resources/qa-loop-prerequisites.md` for complete step-by-step setup instructions.

### Setup Guides

| Prerequisite | Setup Guide | Time |
|--------------|-------------|------|
| Convert to PBIP | `resources/getting-started.md` | 5 min |
| Git & GitHub | `resources/github-setup-for-powerbi.md` | 10 min |
| Deployment Pipeline | `resources/fabric-deployment-setup.md` | 30-60 min |
| Playwright MCP | `resources/playwright-mcp-setup.md` | 10 min |
| GitHub CLI | Install via `winget install GitHub.cli`, then `gh auth login` | 5 min |

## Workflow

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 WORKFLOW: qa-loop-pbi-dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase 0: Prerequisites Check

**Before starting the QA loop, verify all prerequisites:**

1. **Check Playwright MCP Availability**
   ```
   📋 PHASE 0: Prerequisites Check
      └─ 🔌 [MCP] Playwright availability check
      └─    ✅ Playwright MCP available / ❌ Not available (abort)
   ```
   - If Playwright MCP is not available, abort workflow with helpful error message
   - Inform user how to enable Playwright MCP

2. **Check GitHub CLI Availability**
   ```
      └─ 🔧 [BASH] gh auth status
      └─    ✅ GitHub CLI authenticated / ❌ Not authenticated
   ```
   - If `gh` is not authenticated, provide instructions for `gh auth login`

3. **Validate Project Path**
   ```
      └─ 🔍 [VALIDATE] Project structure
      └─    ✅ Valid PBIP project / ❌ Invalid project
   ```
   - Use `pbi_project_validator.py` to confirm valid PBIP structure
   - Detect project format (PBIP, pbi-tools, etc.)

---

### Phase 1: Deploy via Git Commit

**Purpose:** User triggers deployment by committing changes

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 PHASE 1: Deploy via Git Commit
   └─ Ready to deploy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

1. **Prompt User to Deploy**
   ```
   Please commit and push your changes:

     git add .
     git commit -m "Your commit message"
     git push

   After push completes, reply with "deployed" to continue monitoring.
   ```

2. **Wait for User Confirmation**
   - User responds with "deployed" or similar
   - Capture the latest commit SHA for monitoring

3. **Get Commit SHA**
   ```
      └─ 🔧 [BASH] git rev-parse HEAD
      └─    Commit SHA: [sha]
   ```

---

### Phase 2: Monitor GitHub Actions

**Purpose:** Poll deployment workflow until completion

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 PHASE 2: Monitor GitHub Actions
   └─ Monitoring deployment...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

1. **Start Monitoring**
   ```
      └─ 🔧 [BASH] python tools/advanced/monitor_deployment_status.py --repo "<repo>" --commit "<sha>" --workflow "<workflow>" --timeout <seconds>
   ```

2. **Display Progress**
   ```
      └─ Repository: [owner/repo]
      └─ Workflow: [workflow name]
      └─ Commit: [sha (short)]
      └─ ⏳ Status: pending (0s)
      └─ ⏳ Status: in_progress (30s)
      └─ ⏳ Status: in_progress (60s)
      └─ ✅ Deployment completed successfully
      └─ Duration: [N]s
   ```

3. **Handle Results**

**Success:**
```
   └─ ✅ Deployment SUCCEEDED
   └─    Duration: [N] seconds
   └─    Logs: [GitHub Actions URL]
   └─ Proceeding to DOM inspection...
```

**Failure:**
```
   └─ ❌ Deployment FAILED
   └─    Error: [error message]
   └─    Logs: [GitHub Actions URL]
   └─
   └─ Deployment failed. Options:
   └─   [R] Retry after fixing issues
   └─   [V] View deployment logs
   └─   [A] Abort workflow
```

**Timeout:**
```
   └─ ⏱️ Deployment TIMED OUT
   └─    Waited: [timeout]s
   └─
   └─ Options:
   └─   [C] Continue to inspection anyway
   └─   [W] Wait longer (extend timeout)
   └─   [A] Abort workflow
```

---

### Phase 3: Inspect Live Report DOM

**Purpose:** Detect visual errors in the deployed report

**Condition:** Only runs if `--report-url` was provided

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 PHASE 3: Inspect Live Report DOM
   └─ Launching powerbi-qa-inspector agent...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

1. **Invoke QA Inspector Agent**
   - Use Task tool to launch `powerbi-qa-inspector` agent
   - Pass the report URL
   - Pass `--design-critique` flag if enabled

2. **Agent Workflow** (see `agents/powerbi-qa-inspector.md`):
   - Navigate to Power BI report
   - Wait for full page render
   - Capture accessibility snapshot
   - Search for error patterns:
     - Error containers (grey boxes)
     - Modal error dialogs
     - Crash messages
   - Capture screenshot evidence
   - Classify result (PASS / FAIL with type)
   - **If `--design-critique` enabled:**
     - Load design standards (`.claude/powerbi-design-standards.md` or plugin default)
     - Execute glitch scan (truncation, scrollbars)
     - Score design against standards (1-5 scale)
     - Identify specific issues with fixes

3. **Report DOM Inspection Results**

**No Issues:**
```
   └─ 🤖 [AGENT] powerbi-qa-inspector complete
   └─    Result: ✅ No issues found
   └─    Screenshot: qa-results/inspection-001.png
```

**Issues Found:**
```
   └─ 🤖 [AGENT] powerbi-qa-inspector complete
   └─    Result: ❌ [N] issues detected
   └─    Type: VISUAL_ERROR
   └─
   └─    Issues:
   └─    1. Sales Chart - Error container (data binding issue)
   └─    2. Revenue Card - Grey box (column not found)
   └─
   └─    Screenshot: qa-results/inspection-001.png
```

---

### Phase 4: Report Results / Iterate

**Purpose:** Consolidate findings and decide on next action

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 QA LOOP RESULTS (Iteration [N] of [max])
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

1. **Generate Summary**
   ```
   QA Loop Summary:
   ─────────────────
   Deployment:     ✅ SUCCESS (45s)
   DOM Inspection: ❌ 2 ISSUES FOUND

   Overall Status: ❌ ISSUES REQUIRE ATTENTION
   ```

2. **If Issues Found - Prompt User**
   ```
   Issues Detected:
   ────────────────
   1. Visual "Sales Chart" shows error container
      Likely cause: Invalid measure reference

   2. Visual "Revenue Card" displays grey box
      Likely cause: Column binding not found

   ─────────────────────────────────────────────

   Options:
   [R] Retry QA loop after fixing issues
   [S] Skip DOM issues and mark complete
   [A] Abort workflow

   Iterations remaining: [N-1]
   ```

3. **If No Issues - Complete Successfully**
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ✅ QA LOOP COMPLETE
      └─ Report deployed and verified
      └─ No visual errors detected
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```

4. **Handle User Choice**

**Retry:**
- Return to Phase 1 (Deploy via Git Commit)
- Increment iteration counter
- Check if max retries exceeded

**Skip:**
- Mark workflow as complete with warnings
- Log skipped issues for reference

**Abort:**
- Terminate workflow
- Summarize what was completed

---

## Findings Output

If a scratchpad folder exists (from previous `/evaluate-pbi-project-file` run), append results to findings.md as **Section 5: QA Loop Results**.

```markdown
## Section 5: QA Loop Results

**QA Run**: 2025-01-10T15:30:00
**Iteration**: 1 of 3
**Overall Status**: ✅ PASSED / ❌ ISSUES FOUND

### 5.1 Deployment Status
- Repository: myorg/sales-report
- Workflow: deploy.yml
- Commit: abc123def
- Duration: 45s
- Status: ✅ SUCCESS

### 5.2 DOM Inspection
**Report URL**: https://app.powerbi.com/reports/xyz
**Screenshot**: [qa-results/inspection-001.png](./qa-results/inspection-001.png)

**Issues Found**:
| # | Visual | Issue Type | Details |
|---|--------|------------|---------|
| 1 | Sales Chart | Error Container | "Unable to load" message |
| 2 | Revenue Card | Grey Box | Visual failed to render |

### 5.3 Recommendations
1. Check measure references in "Sales Chart"
2. Verify column bindings for "Revenue Card"
3. Re-deploy after fixing issues
```

---

## Error Handling

### Deployment Failures
- Display GitHub Actions error logs
- Provide link to full logs
- Offer retry or abort options

### DOM Inspection Errors
- Classify error type (FATAL vs VISUAL vs WARNING)
- Capture screenshot evidence
- Provide actionable recommendations

### Max Retries Exceeded
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ MAX RETRIES EXCEEDED
   └─ Iterations: [max] of [max]
   └─ Issues persist after [max] attempts
   └─
   └─ Manual investigation recommended.
   └─ Check the issues listed above and fix manually.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Protocol: The QA Loop

**You are strictly forbidden from marking a task as "Complete" until you have verified it in the Power BI Service.**

For every design iteration, you must execute:

1. **Deployment & Wait**
   - Prompt user to commit changes
   - Run `monitor_deployment_status.py`
   - Wait for `SUCCEEDED` signal

2. **Visual Inspection**
   - Run `powerbi-qa-inspector` agent on the report URL
   - **Scenario A (FATAL_CRASH)**: Report failed to load. Revert last change.
   - **Scenario B (VISUAL_ERROR)**: Specific visuals broken. Fix data bindings.
   - **Scenario C (PASS)**: Success. Complete the task.

---

## Integration Points

This workflow integrates with:

- **monitor_deployment_status.py**: GitHub Actions monitoring tool
- **powerbi-qa-inspector**: DOM inspection agent (with optional design critique)
- **pbi_project_validator.py**: Project structure validation
- **Playwright MCP**: Browser automation for DOM inspection
- **powerbi-design-standards.md**: Design rules for critique loop (when `--design-critique` enabled)

## See Also

### Setup Guides (Start Here if New)
- `resources/qa-loop-prerequisites.md` - Complete prerequisites checklist and setup walkthrough
- `resources/github-setup-for-powerbi.md` - Git and GitHub setup for Power BI projects
- `resources/fabric-deployment-setup.md` - Deployment pipeline configuration
- `resources/playwright-mcp-setup.md` - Playwright MCP installation
- `resources/getting-started.md` - PBIP format conversion

### Technical References
- `agents/powerbi-qa-inspector.md` - DOM inspection agent documentation
- `references/powerbi-design-standards.md` - Dashboard design standards & AI critique rubric
- `tools/advanced/monitor_deployment_status.py` - Deployment monitor
- `workflows/implement-deploy-test-pbi-project-file.md` - Related implementation workflow (run this first for validation)
