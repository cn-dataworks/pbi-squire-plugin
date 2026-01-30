# GitHub Setup for Power BI Projects

**This is a Developer-only feature.**

This guide walks you through setting up Git and GitHub for your Power BI project. This is a prerequisite for the QA loop workflow.

---

## Prerequisites

- Power BI project in PBIP format (see `getting-started.md` for conversion)
- Windows 10/11 or macOS

---

## Step 1: Install Git

### Windows

**Option A: Using winget (recommended):**
```powershell
winget install Git.Git
```

**Option B: Manual download:**
1. Go to https://git-scm.com/download/win
2. Download the installer
3. Run installer with default options
4. Restart your terminal

### macOS

```bash
# Using Homebrew
brew install git

# Or it may already be installed with Xcode
git --version
```

### Verify Installation

```powershell
git --version
# Should output: git version 2.x.x
```

---

## Step 2: Configure Git Identity

Set your name and email (used for commit history):

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**Note:** Use the email associated with your GitHub account.

---

## Step 3: Create GitHub Account

If you don't have a GitHub account:

1. Go to https://github.com/signup
2. Enter your email address
3. Create a password
4. Choose a username
5. Complete verification
6. Select the free plan (sufficient for private repos)

---

## Step 4: Initialize Your Project

Navigate to your PBIP project folder and initialize Git:

```powershell
cd "C:\PBI\MyProject"
git init
```

This creates a hidden `.git` folder that tracks changes.

---

## Step 5: Create .gitignore

Create a `.gitignore` file to exclude files that shouldn't be tracked:

```powershell
# In your project folder, create .gitignore with this content:
```

**.gitignore contents:**
```
# Power BI temporary files
*.pbix.tmp
.pbi/
*.bim.lock

# Power BI Desktop cache
*.Report/.cache/
*.SemanticModel/.cache/

# Local Claude settings (optional - include if you want shared settings)
.claude/tasks/

# OS files
.DS_Store
Thumbs.db

# IDE files
.vscode/
.idea/
```

---

## Step 6: Create GitHub Repository

### Option A: Via GitHub Website

1. Go to https://github.com/new
2. **Repository name:** Use a descriptive name (e.g., `sales-dashboard`)
3. **Description:** Optional but helpful
4. **Visibility:**
   - **Private** - Only you and collaborators can see it
   - **Public** - Anyone can see it (choose carefully for business projects)
5. **Do NOT** check "Add a README file" (you already have files)
6. **Do NOT** add .gitignore (you already created one)
7. Click **Create repository**

### Option B: Via GitHub CLI

```powershell
# Make sure gh is installed and authenticated
gh auth login

# Create repository
gh repo create sales-dashboard --private --source=. --remote=origin
```

---

## Step 7: Connect Local Repository to GitHub

After creating the repository on GitHub, connect your local project:

```powershell
cd "C:\PBI\MyProject"

# Add the remote repository
git remote add origin https://github.com/YOUR-USERNAME/sales-dashboard.git
```

**Verify the remote:**
```powershell
git remote -v
# Should show:
# origin  https://github.com/YOUR-USERNAME/sales-dashboard.git (fetch)
# origin  https://github.com/YOUR-USERNAME/sales-dashboard.git (push)
```

---

## Step 8: Make Your First Commit

Stage all files and create your first commit:

```powershell
# Stage all files
git add .

# Check what will be committed
git status

# Create the commit
git commit -m "Initial commit: Power BI project"
```

---

## Step 9: Push to GitHub

Push your local commits to GitHub:

```powershell
# Rename default branch to 'main' (if not already)
git branch -M main

# Push and set upstream
git push -u origin main
```

**If prompted for credentials:**
- Enter your GitHub username
- For password, use a **Personal Access Token** (not your GitHub password)
  - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
  - Generate new token with `repo` scope
  - Use this token as your password

---

## Step 10: Verify on GitHub

1. Go to your repository: `https://github.com/YOUR-USERNAME/sales-dashboard`
2. You should see your project files
3. Verify the folder structure looks correct

---

## Daily Workflow

After initial setup, your daily workflow is:

### Making Changes

```powershell
# 1. Check current status
git status

# 2. Stage changes
git add .

# 3. Commit with descriptive message
git commit -m "Fix: Corrected YoY calculation in Sales measures"

# 4. Push to GitHub
git push
```

### Good Commit Messages

Use clear, descriptive messages:
- `Add: New customer retention measures`
- `Fix: Revenue calculation excluding returns`
- `Update: Dashboard page layout for mobile`
- `Refactor: Consolidated date table logic`

---

## Branch Strategy (Optional)

For more structured development:

```powershell
# Create a feature branch
git checkout -b feature/add-forecasting

# Make changes and commit
git add .
git commit -m "Add: Sales forecasting measures"

# Push the branch
git push -u origin feature/add-forecasting

# Create a pull request on GitHub, then merge
# After merging, switch back to main
git checkout main
git pull
```

---

## Troubleshooting

### "fatal: not a git repository"

You're not in a Git-initialized folder:
```powershell
cd "C:\PBI\MyProject"
git init
```

### "remote origin already exists"

Remove and re-add the remote:
```powershell
git remote remove origin
git remote add origin https://github.com/YOUR-USERNAME/repo-name.git
```

### "failed to push some refs"

Your local branch is behind the remote:
```powershell
git pull --rebase origin main
git push
```

### "Authentication failed"

Use a Personal Access Token instead of your password:
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic) with `repo` scope
3. Use the token when prompted for password

Or set up SSH keys:
```powershell
ssh-keygen -t ed25519 -C "your.email@example.com"
# Add the public key to GitHub → Settings → SSH Keys
```

### Path too long errors on Windows

PBIP projects have deep folder structures. Enable long paths:
```powershell
# Run as Administrator
git config --system core.longpaths true
```

---

## GitHub CLI (Recommended)

The GitHub CLI (`gh`) simplifies many operations:

### Install

```powershell
winget install GitHub.cli
```

### Authenticate

```powershell
gh auth login
# Select GitHub.com, HTTPS, and authenticate via browser
```

### Useful Commands

```powershell
# Check authentication status
gh auth status

# Create repository
gh repo create my-project --private

# View recent workflow runs
gh run list

# Watch a workflow run
gh run watch

# View workflow logs
gh run view --log
```

The QA loop uses `gh` to monitor deployment workflows.

---

## Next Steps

After setting up GitHub:

1. **Set up deployment pipeline** - See `fabric-deployment-setup.md`
2. **Install Playwright MCP** - See `playwright-mcp-setup.md`
3. **Run the QA loop** - See `workflows/qa-loop-pbi-dashboard.md`

---

## See Also

- `qa-loop-prerequisites.md` - Complete prerequisites checklist
- `fabric-deployment-setup.md` - Deployment pipeline configuration
- `getting-started.md` - PBIP format conversion
