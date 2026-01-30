# QA Loop Prerequisites Setup Guide

**This is a Developer-only feature.**

This guide walks you through setting up all prerequisites for the `/qa-loop-pbi-dashboard` workflow. If you have a Power BI dashboard on your desktop (.pbix file) and want to use the automated QA loop, follow these steps in order.

---

## First: What Type of Power BI Account Do You Have?

**Is your Power BI workspace connected to GitHub (Fabric Git Integration)?**

| Your Answer | What This Means | Go To |
|-------------|-----------------|-------|
| **Yes** - My workspace has Git integration enabled | You have **Fabric** capacity | Step 3A (simple setup) |
| **No** - I don't see Git integration in my workspace | You have a **Standard** account | Step 3B (GitHub Actions setup) |
| **I don't know** | Check below | ↓ |

### How to Check

1. Go to https://app.powerbi.com → Open your workspace
2. Click **Workspace settings** (gear icon)
3. Look for **Git integration** in the left menu
   - **If you see it:** You have Fabric → Follow **Step 3A**
   - **If you don't see it:** Standard account → Follow **Step 3B**

### Setup Time by Account Type

| Account Type | Deployment Setup | Total Time |
|--------------|------------------|------------|
| **Fabric** | Connect to GitHub (one-time) | ~45 min |
| **Standard** | Azure AD app + GitHub Actions | ~1.5-2 hours |

---

## Overview: What You Need

The QA loop automates deployment verification for Power BI projects. It requires:

| Prerequisite | What It Does | Setup Time |
|--------------|--------------|------------|
| PBIP Format | Enables version control and automation | 5 min |
| GitHub Repository | Hosts your project for CI/CD | 10 min |
| Deployment Pipeline | Deploys changes to Power BI Service | **10 min (Fabric)** or **30-60 min (Standard)** |
| Playwright MCP | Inspects deployed reports for errors | 10 min |
| GitHub CLI | Monitors deployment status | 5 min |

**Total estimated setup time:**
- **Fabric accounts:** ~45 minutes (one-time)
- **Standard accounts:** ~1.5-2 hours (one-time)

---

## Step 1: Convert to PBIP Format

**Why:** The QA loop requires PBIP format for version control and automated deployment.

**If you have a .pbix file:**

1. Open Power BI Desktop
2. File → Open → Select your .pbix file
3. File → Save As → **Power BI Project (.pbip)**
4. Choose a location with a short path (e.g., `C:\PBI\MyProject`)
5. A folder is created with this structure:

```
MyProject/
├── MyProject.pbip
├── MyProject.SemanticModel/
│   └── definition/
│       ├── tables/
│       └── model.tmdl
└── MyProject.Report/
    └── definition/
        └── pages/
```

**Path length warning:** PBIP projects have deep folder structures. Keep your base path short:
- Good: `C:\PBI\Sales`
- Bad: `C:\Users\JohnSmith\Documents\PowerBI\Projects\2024\Q4\SalesAnalytics`

See `getting-started.md` for detailed conversion instructions.

---

## Step 2: Set Up GitHub Repository

**Why:** The QA loop monitors GitHub Actions for deployment status.

See `github-setup-for-powerbi.md` for complete instructions.

**Quick steps:**

1. **Install Git** (if not installed):
   - Download from https://git-scm.com/downloads
   - Run installer with default options

2. **Create GitHub account** (if needed):
   - Go to https://github.com/signup

3. **Initialize your project:**
   ```powershell
   cd "C:\PBI\MyProject"
   git init
   ```

4. **Create .gitignore:**
   ```
   # Power BI temporary files
   *.pbix.tmp
   .pbi/

   # Local settings
   .claude/tasks/
   ```

5. **Create GitHub repository:**
   - Go to https://github.com/new
   - Name: `my-powerbi-project`
   - Private or Public (your choice)
   - Don't initialize with README (you already have files)

6. **Connect and push:**
   ```powershell
   git remote add origin https://github.com/YOUR-USERNAME/my-powerbi-project.git
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git push -u origin main
   ```

---

## Step 3: Set Up Deployment Pipeline

**Why:** The QA loop needs a way to deploy your project to Power BI Service and monitor the deployment.

**Which section applies to you?** (Based on your answer in "First: What Type of Account")

| Your Account | Follow |
|--------------|--------|
| **Fabric** (Git integration available) | **Step 3A** below |
| **Standard** (No Git integration) | **Step 3B** below |

See `fabric-deployment-setup.md` for complete instructions on both paths.

---

### Step 3A: Fabric Git Integration (For Fabric Accounts)

**If you answered "Yes" to having Git integration in your workspace, follow this section.**

1. **In Power BI Service:**
   - Go to your workspace
   - Settings → Git integration
   - Connect to your GitHub repository
   - Select the branch to sync

2. **Create a notification workflow** (`.github/workflows/deploy.yml`):
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
     notify:
       runs-on: ubuntu-latest
       steps:
         - name: Deployment triggered
           run: |
             echo "Changes pushed to GitHub"
             echo "Fabric Git Integration will sync automatically"
             echo "Waiting for sync to complete..."

         - name: Wait for Fabric sync
           run: sleep 60  # Fabric typically syncs within 1 minute

         - name: Deployment complete
           run: echo "Deployment notification complete"
   ```

This workflow acts as a "deployment signal" that the QA loop monitors.

**Done with Step 3A?** Skip to [Step 4: Install Playwright MCP](#step-4-install-playwright-mcp).

---

### Step 3B: GitHub Actions Deployment (For Standard Accounts)

**If you answered "No" to having Git integration (Standard Power BI Pro account), follow this section.**

Standard accounts require GitHub Actions to deploy your project via the Power BI REST API. This involves:
1. Creating an Azure AD application (service principal)
2. Granting it access to your Power BI workspace
3. Configuring GitHub to use those credentials

**This is more complex than Fabric Git Integration, but works with any Power BI Pro or Premium account.**

#### Step 3B.1: Create Azure AD Application

1. Go to https://portal.azure.com
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. **Name:** `PowerBI-GitHub-Deployment`
5. **Supported account types:** Single tenant
6. Click **Register**
7. **Save these values:**
   - Application (client) ID
   - Directory (tenant) ID

#### Step 3B.2: Create Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
3. **Description:** `GitHub Actions`
4. Click **Add**
5. **Copy the secret value immediately** (you won't see it again)

#### Step 3B.3: Grant Power BI API Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission** → **Power BI Service**
3. Add: `Workspace.ReadWrite.All`, `Content.Create`
4. Click **Grant admin consent** (requires Azure AD admin)

#### Step 3B.4: Add Service Principal to Workspace

1. Go to https://app.powerbi.com → Your workspace
2. Click **Manage access** → **Add people or groups**
3. Search for `PowerBI-GitHub-Deployment`
4. Select **Contributor** role → **Add**

#### Step 3B.5: Add GitHub Secrets

In your GitHub repository → **Settings** → **Secrets and variables** → **Actions**:

| Secret Name | Value |
|-------------|-------|
| `AZURE_TENANT_ID` | Your tenant ID from Step 3B.1 |
| `AZURE_CLIENT_ID` | Your client ID from Step 3B.1 |
| `AZURE_CLIENT_SECRET` | Your secret from Step 3B.2 |
| `POWERBI_WORKSPACE_ID` | Your workspace ID* |

*Find workspace ID: In Power BI Service URL `.../groups/WORKSPACE-ID/...`

#### Step 3B.6: Create Deployment Workflow

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
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Get Azure AD Token
        id: token
        run: |
          TOKEN=$(curl -s -X POST \
            "https://login.microsoftonline.com/${{ secrets.AZURE_TENANT_ID }}/oauth2/v2.0/token" \
            -d "client_id=${{ secrets.AZURE_CLIENT_ID }}" \
            -d "client_secret=${{ secrets.AZURE_CLIENT_SECRET }}" \
            -d "scope=https://analysis.windows.net/powerbi/api/.default" \
            -d "grant_type=client_credentials" \
            | jq -r '.access_token')
          echo "::add-mask::$TOKEN"
          echo "token=$TOKEN" >> $GITHUB_OUTPUT

      - name: Deploy to Power BI
        run: |
          echo "Deploying to Power BI workspace..."
          # Note: Full REST API deployment requires additional scripting
          # See fabric-deployment-setup.md for complete implementation
          echo "Deployment triggered for commit ${{ github.sha }}"

      - name: Deployment complete
        run: echo "Deployment workflow complete"
```

**Note:** Full REST API deployment is complex. See `fabric-deployment-setup.md` for the complete implementation with import/publish logic.

**Done with Step 3B?** Continue to Step 4 below.

---

## Step 4: Install Playwright MCP

**Why:** The QA loop uses Playwright to inspect deployed reports for visual errors.

See `playwright-mcp-setup.md` for complete instructions.

**Quick steps:**

1. **Install Node.js** (if not installed):
   - Download from https://nodejs.org/ (LTS version)

2. **Install Playwright MCP:**
   ```powershell
   npm install -g @anthropic/mcp-playwright
   ```

3. **Update Claude Code MCP config** (`~/.claude/mcp.json`):
   ```json
   {
     "mcpServers": {
       "playwright": {
         "command": "npx",
         "args": ["@anthropic/mcp-playwright"]
       }
     }
   }
   ```

4. **Restart Claude Code** to load the new MCP server.

5. **Verify:** Ask Claude "Can you check if Playwright MCP is available?"

---

## Step 5: Install and Authenticate GitHub CLI

**Why:** The QA loop uses `gh` to monitor GitHub Actions workflow runs.

**Install:**

```powershell
# Windows (via winget)
winget install GitHub.cli

# Or download from https://cli.github.com/
```

**Authenticate:**

```powershell
gh auth login
```

Follow the prompts:
- GitHub.com
- HTTPS
- Authenticate via browser

**Verify:**

```powershell
gh auth status
```

Should show: `Logged in to github.com as YOUR-USERNAME`

---

## Step 6: Publish Your Report (Get Report URL)

**Why:** The QA loop inspects the live report at a URL.

**If using Fabric Git Integration:**
- Your report is already published when you push to GitHub
- Find the URL in Power BI Service: Workspace → Your Report → Copy link

**If not using Fabric Git Integration:**
1. Open your project in Power BI Desktop
2. File → Publish → Select workspace
3. After publishing, click "Open in Power BI"
4. Copy the URL from your browser

**Report URL format:**
```
https://app.powerbi.com/groups/WORKSPACE-ID/reports/REPORT-ID
```

---

## Step 7: Ensure Browser Session

**Why:** Playwright reuses your browser session to access Power BI Service.

1. **Open your browser** (Edge or Chrome)
2. **Go to** https://app.powerbi.com
3. **Sign in** if prompted
4. **Keep the browser open** during QA loop runs

The QA loop will use this authenticated session to inspect your reports.

---

## Verification Checklist

Before running `/qa-loop-pbi-dashboard`, verify:

- [ ] Project is in PBIP format (folder with `.pbip` file)
- [ ] Project is in a GitHub repository
- [ ] `.github/workflows/deploy.yml` exists
- [ ] `gh auth status` shows authenticated
- [ ] Playwright MCP is configured in Claude Code
- [ ] You have a published report URL
- [ ] You're logged into Power BI Service in your browser

---

## Running the QA Loop

Once all prerequisites are met:

```bash
/qa-loop-pbi-dashboard --project "C:\PBI\MyProject" --repo "username/my-powerbi-project" --report-url "https://app.powerbi.com/groups/.../reports/..."
```

See `workflows/qa-loop-pbi-dashboard.md` for full workflow documentation.

---

## Troubleshooting

### "Playwright MCP not available"
- Check that `~/.claude/mcp.json` includes the playwright server
- Restart Claude Code after modifying MCP config
- Run `npm list -g @anthropic/mcp-playwright` to verify installation

### "GitHub CLI not authenticated"
- Run `gh auth login` and complete the authentication flow
- Run `gh auth status` to verify

### "Deployment workflow not found"
- Verify `.github/workflows/deploy.yml` exists in your repository
- Check the workflow name matches the `--workflow` parameter
- Ensure the file was committed and pushed

### "Report URL not accessible"
- Verify you're logged into Power BI Service in your browser
- Check that the report is published to a workspace you have access to
- Try opening the URL manually in your browser

---

## See Also

- `github-setup-for-powerbi.md` - Detailed GitHub setup guide
- `fabric-deployment-setup.md` - Deployment pipeline configuration
- `playwright-mcp-setup.md` - Playwright MCP installation
- `workflows/qa-loop-pbi-dashboard.md` - QA loop workflow documentation
- `getting-started.md` - PBIP format conversion
