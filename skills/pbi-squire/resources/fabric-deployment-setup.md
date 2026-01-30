# Fabric Deployment Setup for QA Loop

**This is a Developer-only feature.**

This guide walks you through setting up automated deployment from GitHub to Power BI Service. The QA loop monitors these deployments to verify your changes work correctly.

---

## First: What Type of Account Do You Have?

**Does your Power BI workspace have Git integration?**

| Your Answer | Account Type | Follow Section |
|-------------|--------------|----------------|
| **Yes** - I see "Git integration" in workspace settings | **Fabric** | [Option A](#option-a-fabric-git-integration-recommended) |
| **No** - I don't see Git integration | **Standard** | [Option C](#option-c-github-actions-with-rest-api) |
| **Yes, and I want more CI/CD control** | **Fabric** (advanced) | [Option B](#option-b-github-actions-with-fabric-cicd) |

### How to Check

1. Go to https://app.powerbi.com → Open your workspace
2. Click **Workspace settings** (gear icon)
3. Look for **Git integration** in the left menu

---

## Deployment Options Summary

| Option | Account Type | Complexity | Best For |
|--------|--------------|------------|----------|
| **A: Fabric Git Integration** | Fabric | Easy (10 min) | Most Fabric users |
| **B: GitHub Actions + fabric-cicd** | Fabric | Medium (30 min) | CI/CD pipelines, validation steps |
| **C: GitHub Actions + REST API** | Standard (Developer) | Medium (45 min) | No Fabric access |

---

## Option A: Fabric Git Integration (Recommended)

**For: Fabric accounts (you answered "Yes" to Git integration)**

### What It Does

Fabric Git Integration connects a workspace directly to your GitHub repository. When you push changes:
1. Fabric automatically detects the push
2. Fabric syncs the changes to your workspace
3. Your report/model is updated in Power BI Service

### Requirements

- Microsoft Fabric workspace or Power BI Premium capacity
- GitHub repository (set up in `github-setup-for-powerbi.md`)
- Workspace Admin or Member role

### Step 1: Prepare Your Workspace

1. Go to https://app.powerbi.com
2. Navigate to your workspace (or create one)
3. Ensure the workspace is on Fabric/Premium capacity:
   - Workspace settings → License → Should show "Fabric" or "Premium"
   - If on Pro, you'll need to upgrade or use Option B/C

### Step 2: Connect to GitHub

1. In your workspace, click **Workspace settings** (gear icon)
2. Select **Git integration**
3. Click **Connect to a Git repository**
4. **Git provider:** GitHub
5. **Authenticate** with your GitHub account if prompted
6. **Repository:** Select your Power BI project repository
7. **Branch:** Select `main` (or your default branch)
8. **Git folder:** Usually root (`/`) or the folder containing your .pbip file
9. Click **Connect and sync**

### Step 3: Initial Sync

After connecting:
1. Fabric will import your project from GitHub
2. Wait for the sync to complete (1-2 minutes)
3. Your report and semantic model should appear in the workspace

### Step 4: Create Notification Workflow

The QA loop monitors GitHub Actions, so create a simple workflow that signals when changes are pushed:

Create `.github/workflows/deploy.yml`:

```yaml
name: Power BI Deployment

on:
  push:
    branches: [main]
    paths:
      - '**.tmdl'
      - '**.pbir'
      - '**.json'

jobs:
  deployment-notification:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Log deployment trigger
        run: |
          echo "========================================"
          echo "Power BI Deployment Triggered"
          echo "========================================"
          echo "Commit: ${{ github.sha }}"
          echo "Branch: ${{ github.ref_name }}"
          echo "Pusher: ${{ github.actor }}"
          echo ""
          echo "Fabric Git Integration will automatically"
          echo "sync these changes to Power BI Service."

      - name: Wait for Fabric sync
        run: |
          echo "Waiting for Fabric to sync changes..."
          sleep 90  # Fabric typically syncs within 60-90 seconds
          echo "Sync window complete."

      - name: Deployment complete
        run: |
          echo "========================================"
          echo "Deployment notification complete"
          echo "========================================"
          echo ""
          echo "If sync was successful, changes are now"
          echo "live in Power BI Service."
```

### Step 5: Commit and Push the Workflow

```powershell
git add .github/workflows/deploy.yml
git commit -m "Add: Deployment notification workflow for QA loop"
git push
```

### Step 6: Verify

1. Go to your GitHub repository
2. Click **Actions** tab
3. You should see the "Power BI Deployment" workflow running
4. After it completes, check your Power BI workspace - changes should be synced

### How It Works with QA Loop

```
You: git push
  │
  ├──► GitHub Actions: "Power BI Deployment" workflow starts
  │                    └── Waits 90 seconds for Fabric sync
  │
  └──► Fabric: Detects push, syncs to workspace
              └── Report/model updated in Power BI Service

QA Loop: Monitors GitHub Actions workflow
         └── When workflow succeeds, inspects live report
```

---

## Option B: GitHub Actions with fabric-cicd

**For: Fabric accounts that want CI/CD control (you answered "Yes, and I want more control")**

Use this option if you want more control over deployments or need to run validation steps.

### Requirements

- Fabric workspace (you must have Git integration available)
- Azure AD application (service principal)
- Service principal added to workspace with Contributor role

### Step 1: Create Azure AD Application

1. Go to https://portal.azure.com
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. **Name:** `PowerBI-GitHub-Deployment`
5. **Supported account types:** Single tenant
6. Click **Register**
7. Note the **Application (client) ID** and **Directory (tenant) ID**

### Step 2: Create Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
3. **Description:** `GitHub Actions`
4. **Expires:** Choose appropriate duration
5. Click **Add**
6. **Copy the secret value immediately** - you won't see it again!

### Step 3: Grant Power BI Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission**
3. Select **Power BI Service**
4. Select **Delegated permissions** (or Application permissions for service principal)
5. Add these permissions:
   - `Workspace.ReadWrite.All`
   - `Content.Create`
6. Click **Grant admin consent** (requires admin)

### Step 4: Add Service Principal to Workspace

1. Go to https://app.powerbi.com
2. Navigate to your workspace
3. Click **Manage access**
4. Click **Add people or groups**
5. Search for your app name (`PowerBI-GitHub-Deployment`)
6. Select **Contributor** role
7. Click **Add**

### Step 5: Add GitHub Secrets

In your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `FABRIC_TENANT_ID` | Your Azure AD tenant ID |
| `FABRIC_CLIENT_ID` | Your app's client ID |
| `FABRIC_CLIENT_SECRET` | Your app's client secret |
| `FABRIC_WORKSPACE_ID` | Your Power BI workspace ID* |

*Find workspace ID: In Power BI Service, go to workspace → the URL contains `.../groups/WORKSPACE-ID/...`

### Step 6: Create Deployment Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Power BI Deployment

on:
  push:
    branches: [main]
    paths:
      - '**.tmdl'
      - '**.pbir'
      - '**.json'

env:
  FABRIC_TENANT_ID: ${{ secrets.FABRIC_TENANT_ID }}
  FABRIC_CLIENT_ID: ${{ secrets.FABRIC_CLIENT_ID }}
  FABRIC_CLIENT_SECRET: ${{ secrets.FABRIC_CLIENT_SECRET }}

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install fabric-cicd
        run: pip install fabric-cicd

      - name: Deploy to Fabric
        run: |
          echo "Deploying to Power BI workspace..."
          fabric-cicd deploy \
            --workspace-id ${{ secrets.FABRIC_WORKSPACE_ID }} \
            --source-path . \
            --verbose

      - name: Deployment complete
        run: |
          echo "========================================"
          echo "Deployment successful!"
          echo "========================================"
          echo "Workspace: ${{ secrets.FABRIC_WORKSPACE_ID }}"
          echo "Commit: ${{ github.sha }}"
```

### Step 7: Commit and Test

```powershell
git add .github/workflows/deploy.yml
git commit -m "Add: fabric-cicd deployment workflow"
git push
```

Monitor the workflow in GitHub Actions.

---

## Option C: GitHub Actions with REST API

**For: Standard accounts without Fabric (you answered "No" to Git integration)**

Use this option if you have a Power BI Pro or Premium account without Fabric Git Integration.

### Overview

This option uses the Power BI REST API with a service principal to deploy your project. It requires:
1. Azure AD application registration
2. Service principal with Power BI permissions
3. GitHub Actions workflow with credentials

**Note:** This approach is more complex than Fabric Git Integration but works with any Power BI account.

### Workflow Template

```yaml
name: Power BI Deployment

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Get access token
        id: token
        run: |
          TOKEN=$(curl -X POST \
            "https://login.microsoftonline.com/${{ secrets.TENANT_ID }}/oauth2/v2.0/token" \
            -d "client_id=${{ secrets.CLIENT_ID }}" \
            -d "client_secret=${{ secrets.CLIENT_SECRET }}" \
            -d "scope=https://analysis.windows.net/powerbi/api/.default" \
            -d "grant_type=client_credentials" \
            | jq -r '.access_token')
          echo "token=$TOKEN" >> $GITHUB_OUTPUT

      - name: Deploy report
        run: |
          # Custom deployment logic using Power BI REST API
          # This requires packaging your PBIP as a .pbix first
          echo "Deploying via REST API..."
          # Implementation depends on your specific needs
```

**Recommendation:** Use Option A or B instead - they're more straightforward.

---

## Verifying Your Setup

### Check Workflow Runs

```powershell
# Using GitHub CLI
gh run list --workflow=deploy.yml

# Watch the latest run
gh run watch
```

### Check Power BI Service

1. Go to your workspace in Power BI Service
2. Verify the report/model shows recent modification time
3. Open the report to confirm changes are reflected

### Test the Full Flow

1. Make a small change to your project (e.g., edit a measure)
2. Commit and push:
   ```powershell
   git add .
   git commit -m "Test: Verify deployment pipeline"
   git push
   ```
3. Watch GitHub Actions: `gh run watch`
4. After success, refresh Power BI Service
5. Verify your change is live

---

## Troubleshooting

### Fabric Git sync not working

- Check workspace is on Fabric/Premium capacity
- Verify Git integration is connected (Workspace settings → Git integration)
- Check the branch name matches
- Try manual sync: Workspace settings → Git integration → Sync now

### GitHub Actions workflow failing

- Check workflow syntax: Go to Actions tab → Click failed run → View logs
- Verify secrets are set correctly
- Ensure service principal has workspace access

### fabric-cicd deployment errors

- Verify all secrets are correct
- Check service principal has Contributor role on workspace
- Ensure fabric-cicd version is current: `pip install --upgrade fabric-cicd`

### Authentication errors

- Regenerate client secret if expired
- Verify tenant ID is correct
- Ensure API permissions have admin consent

---

## Security Best Practices

1. **Use secrets** - Never commit credentials to your repository
2. **Minimal permissions** - Only grant necessary API permissions
3. **Rotate secrets** - Update client secrets periodically
4. **Private repos** - Keep Power BI projects in private repositories
5. **Review workflows** - Audit workflow files for security issues

---

## Next Steps

After setting up deployment:

1. **Install Playwright MCP** - See `playwright-mcp-setup.md`
2. **Get your report URL** - Copy from Power BI Service after deployment
3. **Run the QA loop** - `/qa-loop-pbi-dashboard --project ... --repo ... --report-url ...`

---

## See Also

- `qa-loop-prerequisites.md` - Complete prerequisites checklist
- `github-setup-for-powerbi.md` - GitHub repository setup
- `playwright-mcp-setup.md` - Browser automation setup
- `workflows/qa-loop-pbi-dashboard.md` - QA loop workflow documentation
