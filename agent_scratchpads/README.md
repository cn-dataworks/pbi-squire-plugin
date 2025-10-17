# Agent Scratchpads

This folder contains timestamped analysis workspaces created by the `/evaluate-pbi-project-file` and `/implement-deploy-test-pbi-project-file` slash commands.

## Folder Structure

Each scratchpad follows this naming convention and can be expanded with implementation artifacts:

### Initial Analysis (created by `/evaluate-pbi-project-file`)
```
YYYYMMDD-HHMMSS-descriptive-problem-name/
  └── findings.md                    # Sections 1-3: Analysis, Proposed Changes, Test Plan
```

### After Implementation (expanded by `/implement-deploy-test-pbi-project-file`)
```
YYYYMMDD-HHMMSS-descriptive-problem-name/
  ├── findings.md                    # Sections 1-4: Now includes Implementation Results
  └── test-results/                  # Testing artifacts
      ├── test_results.md            # Test execution summary
      └── screenshots/               # Visual evidence from Playwright tests
          ├── TestCase_Default_View.png
          ├── TestCase_Aggregation_Check.png
          └── TestCase_Filter_Validation.png
```

### Complete Example
```
20251003-071759-pssr-misc-commissions-aggregation-mismatch/
  ├── findings.md
  └── test-results/
      ├── test_results.md
      └── screenshots/
          ├── TestCase_Aggregation_Consistency.png
          ├── TestCase_Discount_Y_Logic.png
          ├── TestCase_Discount_N_Logic.png
          └── TestCase_Mixed_Indicators.png
```

## Purpose

Scratchpads preserve the complete lifecycle for Power BI project changes, including:
- **Problem Statement**: Original issue description and context
- **Current Implementation Investigation**: Existing code and root cause analysis
- **Proposed Changes**: Corrected code with detailed rationale
- **Test Cases and Impact Analysis**: Verification plan and dependency assessment
- **Implementation Results**: Versioned project path, deployment status, test outcomes
- **Visual Evidence**: Screenshots from automated testing

## Workflow

### Phase 1: Analyze Problem
```bash
/evaluate-pbi-project-file --project "C:\path\to\project" \
  --image "path/to/screenshot.png" \
  --description "The measure total doesn't match the sum of detail rows"
```

**Creates:**
- `agent_scratchpads/YYYYMMDD-HHMMSS-problem-name/findings.md`

**Populated Sections:**
- Section 1: Current Implementation Investigation (by powerbi-code-locator agent)
- Section 2: Proposed Changes (by powerbi-code-fix-identifier agent)
- Section 3: Test Cases and Impact Analysis (by power-bi-verification agent)

---

### Phase 2: Implement, Deploy, and Test

```bash
/implement-deploy-test-pbi-project-file \
  --findings "agent_scratchpads/YYYYMMDD-HHMMSS-problem-name/findings.md" \
  --deploy "DEV" \
  --dashboard-url "https://app.powerbi.com/reports/abc123"
```

**Workflow:**
1. **Apply Changes** (powerbi-code-implementer-apply agent)
   - Creates versioned copy: `C:\path\to\project_YYYYMMDD_HHMMSS`
   - Applies all changes from Section 2
   - Configures deployment profile if needed (interactive setup)

2. **Deploy to Power BI Service** (optional - if `--deploy` provided)
   - Uses pbi-tools CLI with service principal authentication
   - Publishes to specified environment (DEV, TEST, PROD)
   - Captures deployed dashboard URL

3. **Run Automated Tests** (powerbi-playwright-tester agent)
   - Executes test cases from Section 3 (or default visual test)
   - Captures screenshots to `test-results/screenshots/`
   - Generates `test-results/test_results.md`

4. **Update findings.md**
   - Adds Section 4: Implementation Results
   - Documents versioned project path
   - Reports deployment status and URL
   - Summarizes test results

**Updates:**
- `findings.md` → Section 4 appended
- `test-results/test_results.md` → Created
- `test-results/screenshots/` → Screenshot files

---

## Usage Examples

### Example 1: Analyze Only (No Implementation Yet)
```bash
/evaluate-pbi-project-file --project "C:\Reports\SalesReport" \
  --description "Update Total Sales measure to exclude returns"
```

**Result:** Analysis complete, findings.md ready for review

---

### Example 2: Analyze + Implement Locally (No Deployment)
```bash
# Step 1: Analyze
/evaluate-pbi-project-file --project "C:\Reports\SalesReport" \
  --description "Update Total Sales measure to exclude returns"

# Step 2: Implement changes locally
/implement-deploy-test-pbi-project-file \
  --findings "agent_scratchpads/20251003-143500-update-total-sales/findings.md"
```

**Result:** Versioned project created with changes applied, no deployment

---

### Example 3: Full Workflow - Analyze, Implement, Deploy, Test
```bash
# Step 1: Analyze
/evaluate-pbi-project-file --project "C:\Reports\SalesReport" \
  --image "screenshots/sales-bug.png" \
  --description "Total Sales showing wrong value in Q4"

# Step 2: Implement, deploy to DEV, and test
/implement-deploy-test-pbi-project-file \
  --findings "agent_scratchpads/20251003-143500-sales-q4-bug/findings.md" \
  --deploy "DEV" \
  --dashboard-url "https://app.powerbi.com/reports/abc123"
```

**Result:** Complete end-to-end workflow with test results

---

### Example 4: Deploy to Production After DEV Testing
```bash
# Assuming DEV deployment was successful, now deploy to PROD
/implement-deploy-test-pbi-project-file \
  --findings "agent_scratchpads/20251003-143500-sales-q4-bug/findings.md" \
  --deploy "PROD" \
  --dashboard-url "https://app.powerbi.com/reports/xyz789"
```

**Result:** Same changes deployed to PROD environment with new test run

---

## Deployment Configuration

### Authentication Methods

The deployment system supports **two authentication methods**:

#### Option 1: User Authentication (Recommended for You!)

**This is the easiest method for interactive deployments.**

**Prerequisites:**
```powershell
# Install Power BI PowerShell module (one-time setup)
Install-Module -Name MicrosoftPowerBIMgmt -Scope CurrentUser

# Login to Power BI (when needed)
Connect-PowerBIServiceAccount
```

**How it works:**
1. Agent detects if you're already logged in
2. If yes → Uses your login automatically
3. If no → Prompts you to login interactively
4. Asks for workspace name and report name
5. Compiles PBIP → PBIX (using pbi-tools)
6. Deploys using PowerShell cmdlets
7. Returns deployed report URL

**Advantages:**
- ✅ No Azure service principal needed
- ✅ No complex configuration files
- ✅ Uses your existing Power BI permissions
- ✅ Quick and simple for manual deployments

**Example:**
```bash
# First deployment ever
/implement-deploy-test-pbi-project-file \
  --findings "agent_scratchpads/20251003.../findings.md" \
  --deploy "MyWorkspace"

# Agent will prompt:
# ✅ Power BI session detected. Using your login for deployment.
# Please provide deployment details:
# 1. Power BI Workspace Name: MyWorkspace
# 2. Report/Dataset Display Name (optional): PSSR Commissions Fix
# 3. Overwrite if exists? (yes/no): yes
```

---

#### Option 2: Service Principal (For CI/CD Automation)

**Use this method for:**
- Automated deployments in pipelines
- Unattended scheduled deployments
- CI/CD workflows (GitHub Actions, Azure DevOps, etc.)

**First-Time Setup:**

When you choose service principal, the agent guides you through:

1. **Deployment Profile Configuration**
   - Azure Tenant ID
   - Power BI Workspace Name
   - Environment Name (DEV, TEST, PROD)
   - Dataset Display Name
   - Auto-refresh settings

2. **Service Principal Setup**
   - Creating Azure App Registration
   - Generating client secret
   - Setting `PBI_CLIENT_SECRET` environment variable
   - Enabling service principal in Power BI Admin Portal
   - Granting workspace access

3. **Manifest Generation**
   - Creates `.pbixproj.json` in versioned project
   - Stores deployment configuration
   - Reusable for future deployments

**Subsequent Deployments:**

After initial setup, deployment is streamlined:
```bash
/implement-deploy-test-pbi-project-file \
  --findings "path/to/findings.md" \
  --deploy "DEV"
```

The existing `.pbixproj.json` configuration is reused automatically.

---

### Which Method Should You Use?

| Scenario | Recommended Method |
|----------|-------------------|
| Manual deployment from your machine | **User Authentication** ✅ |
| Testing changes before production | **User Authentication** ✅ |
| One-off deployments | **User Authentication** ✅ |
| GitHub Actions pipeline | Service Principal |
| Azure DevOps pipeline | Service Principal |
| Scheduled automated deployments | Service Principal |

**For most users: Start with User Authentication.** It's faster and easier!

---

## Retention

These folders are working directories and can be:
- **Archived** after implementation is complete
- **Deleted** once changes are verified in production
- **Kept** for historical reference and audit trails
- **Moved** to a separate documentation repository

Recommended retention:
- Active projects: Keep in `agent_scratchpads/`
- Completed projects: Archive to `agent_scratchpads/archive/YYYY-MM/`
- Deprecated projects: Delete after 90 days

---

## File Organization Best Practices

1. **One scratchpad per issue**: Don't reuse folders for multiple problems
2. **Descriptive names**: Use clear, concise problem names in folder titles
3. **Preserve artifacts**: Keep test screenshots and results for troubleshooting
4. **Version control**: Consider committing findings.md to git for team collaboration
5. **Clean up**: Periodically archive or delete old scratchpads

---

## Notes

- Scratchpads are created automatically - do not manually create folders
- The `/implement-deploy-test-pbi-project-file` command never modifies your original project
- All changes are applied to timestamped copies for safety
- Test results include visual evidence (screenshots) for verification
- Deployment uses pbi-tools CLI with service principal authentication
- Multiple environments (DEV, TEST, PROD) can be configured in a single project
