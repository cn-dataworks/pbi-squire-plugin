# Power BI Analyst Desktop App - Project Specification

**Version:** 1.0.0
**Date:** 2025-11-10
**Status:** Planning - Awaiting Decisions

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Pre-Development Setup](#pre-development-setup)
3. [Architecture Overview](#architecture-overview)
4. [Repository Structure](#repository-structure)
5. [Development Workflow](#development-workflow)
6. [Technical Stack](#technical-stack)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Open Decisions](#open-decisions)
9. [References](#references)

---

## 1. Executive Summary

### Purpose

Create a desktop application that provides a GUI interface for the Power BI Analyst plugin workflows, targeting non-technical Power BI users who are not comfortable with terminal/command-line interfaces.

### Key Goals

- **Single Source of Truth**: Maintain plugin as source, desktop app as translation
- **No Code Duplication**: Share Python execution engine, utilities, and workflow logic
- **Seamless Sync**: Automated synchronization from plugin to desktop app
- **Independent Distribution**: Plugin via Claude marketplace, Desktop via installers
- **Separate Repositories**: Plugin and desktop in different GitHub repos with submodule linking

### Target Users

- **Plugin Users**: Technical users comfortable with Claude Code terminal
- **Desktop Users**: Business analysts, Power BI developers who prefer GUI
- **Both**: Same workflows, different interfaces

---

## 2. Pre-Development Setup

### 2.1 GitHub Repository Setup

#### Step 1: Create Plugin Repository (Private)

**Repository Name:** `powerbi-analyst-plugin`
**Visibility:** Private
**Organization:** `[DECISION NEEDED]`

**Actions Required:**

```bash
# 1. Create repository on GitHub
gh repo create [org-name]/powerbi-analyst-plugin --private

# 2. Initialize repository structure
cd ~/code/power-bi-analyst

# 3. Restructure current repo for plugin distribution
mkdir -p .claude-plugin
cat > .claude-plugin/plugin.json << 'EOF'
{
  "name": "powerbi-analyst",
  "version": "1.0.0",
  "description": "Power BI project analysis, modification, and deployment workflows",
  "author": "Your Name",
  "repository": "https://github.com/[org-name]/powerbi-analyst-plugin",
  "commands": ".claude/commands",
  "agents": ".claude/agents",
  "skills": ".claude/skills"
}
EOF

# 4. Add plugin-specific README
cat > README.md << 'EOF'
# Power BI Analyst Plugin

Claude Code plugin for Power BI project analysis and workflow automation.

## Installation

\`\`\`bash
/plugin install powerbi-analyst@github/[org-name]/powerbi-analyst-plugin
\`\`\`

## Commands

- `/evaluate-pbi-project-file` - Analyze and diagnose issues
- `/create-pbi-artifact` - Create new measures, columns, tables, visuals
- `/implement-deploy-test-pbi-project-file` - Apply changes and deploy
- `/merge-powerbi-projects` - Compare and merge projects

See [.claude/README.md](.claude/README.md) for detailed documentation.
EOF

# 5. Commit and push
git add .
git commit -m "Convert to Claude Code plugin structure"
git remote add origin https://github.com/[org-name]/powerbi-analyst-plugin.git
git push -u origin main
```

**Questions to Answer:**

- **Q1:** What GitHub organization should host these repositories?
  - [ ] Personal account: `your-username/powerbi-analyst-plugin`
  - [ ] Organization account: `org-name/powerbi-analyst-plugin` (please specify org name)
  - [ ] Company account: `company-name/powerbi-analyst-plugin`

- **Q2:** Should the plugin repository remain on the current branch structure or start fresh?
  - [ ] Keep existing `main` branch and history
  - [ ] Create fresh repository with clean history
  - [ ] Archive current repo and start new

#### Step 2: Create Desktop App Repository (Private)

**Repository Name:** `powerbi-analyst-desktop`
**Visibility:** Private
**Organization:** [Same as plugin]

**Actions Required:**

```bash
# 1. Create new repository for desktop app
gh repo create [org-name]/powerbi-analyst-desktop --private

# 2. Clone locally
cd ~/code
git clone https://github.com/[org-name]/powerbi-analyst-desktop.git
cd powerbi-analyst-desktop

# 3. Create initial structure
mkdir -p frontend backend scripts docs

# 4. Add plugin as submodule
git submodule add https://github.com/[org-name]/powerbi-analyst-plugin.git backend/plugin

# 5. Create .gitmodules configuration
cat > .gitmodules << 'EOF'
[submodule "backend/plugin"]
    path = backend/plugin
    url = https://github.com/[org-name]/powerbi-analyst-plugin.git
    branch = main
EOF

# 6. Initialize basic structure
cat > README.md << 'EOF'
# Power BI Analyst Desktop App

Desktop application providing GUI interface for Power BI project analysis workflows.

## For Users

Download installers from [Releases](https://github.com/[org-name]/powerbi-analyst-desktop/releases).

## For Developers

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for setup instructions.
EOF

# 7. Commit initial structure
git add .
git commit -m "Initial desktop app repository structure with plugin submodule"
git push -u origin main
```

#### Step 3: Configure Access Control

**Plugin Repository Access:**

```yaml
# Settings → Collaborators and teams
Teams/Users with Access:
  - @core-team: Admin (you + core maintainers)
  - @plugin-contributors: Write (community contributors - optional)
  - @desktop-developers: Read (can view plugin for desktop integration)
```

**Desktop Repository Access:**

```yaml
# Settings → Collaborators and teams
Teams/Users with Access:
  - @core-team: Admin (you + core maintainers)
  - @desktop-developers: Write (frontend/backend developers)
```

**Questions to Answer:**

- **Q3:** Who needs access to each repository?
  - Plugin repository:
    - [ ] Just you (solo development)
    - [ ] You + team members (please specify team members)
    - [ ] Open to external contributors (public PRs)

  - Desktop repository:
    - [ ] Just you (solo development)
    - [ ] You + team members (please specify team members)
    - [ ] Private team only (no external access)

#### Step 4: Set Up GitHub Secrets

**For Desktop App CI/CD (if using automated builds):**

```yaml
# Repository Settings → Secrets and variables → Actions

Required Secrets:
  - ANTHROPIC_API_KEY: Claude API key for backend
  - CODESIGN_CERTIFICATE_WIN: Windows code signing certificate (optional)
  - CODESIGN_CERTIFICATE_MAC: macOS code signing certificate (optional)
  - CSC_LINK: macOS certificate link
  - CSC_KEY_PASSWORD: macOS certificate password
```

**Questions to Answer:**

- **Q4:** Will you use automated builds with GitHub Actions?
  - [ ] Yes, set up CI/CD from the start
  - [ ] No, manual builds initially
  - [ ] Maybe later (can add after initial development)

- **Q5:** Will you code sign the desktop application?
  - [ ] Yes, purchase certificates for Windows and macOS
  - [ ] No, unsigned builds initially
  - [ ] Windows only
  - [ ] macOS only

#### Step 5: Repository Settings Configuration

**Plugin Repository Settings:**

```yaml
Settings to Configure:
  - Default branch: main
  - Branch protection rules:
      - Require pull request reviews: [Yes/No - DECISION NEEDED]
      - Require status checks: [Yes/No - DECISION NEEDED]
  - Pages: Disabled
  - Wikis: [Enabled/Disabled - DECISION NEEDED]
  - Issues: [Enabled/Disabled - DECISION NEEDED]
  - Discussions: [Enabled/Disabled - DECISION NEEDED]
```

**Desktop Repository Settings:**

```yaml
Settings to Configure:
  - Default branch: main
  - Branch protection rules:
      - Require pull request reviews: [Yes/No - DECISION NEEDED]
      - Require status checks: [Yes/No - DECISION NEEDED]
  - Releases: Enabled (for installers)
  - Pages: [Enabled for documentation site - DECISION NEEDED]
  - Wikis: [Enabled/Disabled - DECISION NEEDED]
  - Issues: Enabled (for bug tracking)
  - Discussions: [Enabled for user support - DECISION NEEDED]
```

**Questions to Answer:**

- **Q6:** Development workflow preferences:
  - [ ] Strict: Require PR reviews, status checks, branch protection
  - [ ] Moderate: PR reviews optional, direct commits to main allowed
  - [ ] Flexible: No restrictions (solo development)

- **Q7:** Documentation and support:
  - [ ] Enable GitHub Pages for documentation website
  - [ ] Use GitHub Discussions for user support
  - [ ] Use GitHub Issues only
  - [ ] External documentation site (separate)

---

### 2.2 Development Environment Setup

#### Required Software

**For Plugin Development:**
- Git
- Claude Code (latest version)
- Python 3.10+
- Visual Studio Code or preferred editor

**For Desktop App Development:**
- All plugin requirements +
- Node.js 18+ and npm
- Electron development tools
- PyInstaller (for backend packaging)

**Platform-Specific:**
- **Windows**: Visual Studio Build Tools (for native modules)
- **macOS**: Xcode Command Line Tools
- **Linux**: Build essentials (`build-essential`, `libgtk-3-dev`)

#### Local Repository Setup

```bash
# 1. Clone both repositories
cd ~/code

# Plugin repository
git clone https://github.com/[org-name]/powerbi-analyst-plugin.git
cd powerbi-analyst-plugin
# Test plugin in Claude Code
# Should work as-is

# Desktop repository
cd ~/code
git clone --recurse-submodules https://github.com/[org-name]/powerbi-analyst-desktop.git
cd powerbi-analyst-desktop

# Verify submodule is initialized
ls backend/plugin/.claude/  # Should show commands, agents, tools, etc.
```

**Questions to Answer:**

- **Q8:** Development machine OS (affects tooling decisions):
  - [ ] Windows only
  - [ ] macOS only
  - [ ] Linux only
  - [ ] Multiple platforms (specify: _____________)

- **Q9:** Will you develop both plugin and desktop simultaneously?
  - [ ] Yes, keep both repos open in parallel
  - [ ] No, focus on one at a time
  - [ ] Plugin first, then desktop later

---

### 2.3 External Service Setup

#### Claude API Access

**Required for Desktop App:**
- Anthropic API account
- API key with sufficient credits
- Rate limits understanding

**Questions to Answer:**

- **Q10:** Claude API key management:
  - [ ] Users provide their own API keys (enter in desktop app)
  - [ ] You provide embedded API key (you pay for usage)
  - [ ] Hybrid: Free tier with your key, users can add their own for unlimited

- **Q11:** Expected usage volume:
  - [ ] Low (<100 requests/day)
  - [ ] Medium (100-1000 requests/day)
  - [ ] High (>1000 requests/day)
  - [ ] Unknown (need analytics first)

#### Optional Services

**Analytics (Optional):**
- Telemetry for desktop app usage
- Error reporting (Sentry, Rollbar, etc.)

**Questions to Answer:**

- **Q12:** Analytics and error tracking:
  - [ ] Yes, implement from the start (specify service: ___________)
  - [ ] No, privacy-first approach (no telemetry)
  - [ ] Add later based on need

**Auto-Update Server:**
- GitHub Releases (free)
- Custom server (paid hosting)

**Questions to Answer:**

- **Q13:** Desktop app updates:
  - [ ] GitHub Releases (users download manually or auto-update via electron-updater)
  - [ ] Custom update server
  - [ ] No auto-update (manual downloads only)

---

## 3. Architecture Overview

### 3.1 High-Level Architecture

```
┌────────────────────────────────────────────────────────────┐
│     Plugin Repository (Source of Truth)                    │
│     github.com/[org]/powerbi-analyst-plugin                │
│                                                            │
│  ├── .claude/                                              │
│  │   ├── commands/      (Workflow orchestration)          │
│  │   ├── agents/        (Specialized tasks)               │
│  │   ├── tools/         (Python utilities)                │
│  │   └── skills/        (Auto-invoke capabilities)        │
│  │                                                         │
│  └── .claude-plugin/    (Plugin metadata)                 │
│      └── plugin.json                                       │
└────────────────────┬───────────────────────────────────────┘
                     │
                     │ Git Submodule
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│     Desktop App Repository                                 │
│     github.com/[org]/powerbi-analyst-desktop               │
│                                                            │
│  ├── frontend/             (Electron + React)             │
│  │   ├── src/                                             │
│  │   │   ├── components/  (UI components)                 │
│  │   │   ├── forms/       (Auto-generated from specs)     │
│  │   │   ├── views/       (Main application views)        │
│  │   │   └── api/         (Backend API client)            │
│  │   └── package.json                                      │
│  │                                                         │
│  ├── backend/             (Python + FastAPI)              │
│  │   ├── plugin/          [GIT SUBMODULE → plugin repo]   │
│  │   │   └── .claude/    (Linked from plugin)            │
│  │   ├── executor.py     (Simulates Claude Code)          │
│  │   ├── api.py          (REST API endpoints)             │
│  │   └── requirements.txt                                 │
│  │                                                         │
│  └── scripts/            (Build & sync automation)        │
│      ├── sync-plugin.js  (Copy plugin → generate forms)   │
│      └── build.sh        (Package app for distribution)   │
└────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│  User Interaction (Desktop App GUI)                         │
│  • Select .pbip project via file picker                     │
│  • Enter problem description in text area                   │
│  • Click "Evaluate Project" button                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Frontend (React/Electron)                                  │
│  • Validates inputs                                         │
│  • Sends POST request to backend API                        │
│  • Displays progress & results                              │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/IPC
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend API (FastAPI)                                      │
│  • Receives request                                         │
│  • Calls PluginExecutor.execute_command()                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Plugin Executor (Python)                                   │
│  • Reads command spec from backend/plugin/.claude/commands/ │
│  • Loads agent tools from backend/plugin/.claude/agents/    │
│  • Calls Claude API with workflow prompt + tools            │
│  • Executes Python utilities from backend/plugin/.claude/tools/│
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Claude API (Anthropic)                                     │
│  • Orchestrates workflow                                    │
│  • Invokes agent tools as needed                            │
│  • Returns findings/results                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Response Flow                                              │
│  Backend → Frontend → User sees results in GUI              │
│  • findings.md rendered as rich text                        │
│  • Progress updates streamed in real-time                   │
│  • Option to export, view history, etc.                     │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Plugin-to-Desktop Synchronization

```
┌─────────────────────────────────────────────────────────┐
│  Developer Workflow                                      │
├─────────────────────────────────────────────────────────┤
│  1. Edit plugin (in plugin repo)                        │
│     • Modify .claude/commands/evaluate.md               │
│     • Test with /evaluate in Claude Code                │
│     • Commit & push to plugin repo                      │
│                                                          │
│  2. Update desktop app (in desktop repo)                │
│     cd desktop-app/backend/plugin                       │
│     git pull origin main                                │
│     cd ../..                                             │
│     git add backend/plugin                              │
│     git commit -m "Update plugin to v1.x.x"             │
│                                                          │
│  3. Sync plugin to desktop                              │
│     npm run sync-plugin                                 │
│     • Parses command specs                              │
│     • Generates React forms                             │
│     • Updates API routes                                │
│                                                          │
│  4. Test desktop app                                    │
│     npm run dev                                          │
│     • Verify new workflow appears in GUI                │
│     • Test end-to-end                                   │
│                                                          │
│  5. Build & release                                     │
│     npm run build                                        │
│     • Package for Windows/macOS/Linux                   │
│     • Create GitHub release                             │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Repository Structure

### 4.1 Plugin Repository Structure

```
powerbi-analyst-plugin/
├── .claude/
│   ├── commands/
│   │   ├── create-pbi-artifact.md
│   │   ├── evaluate-pbi-project-file.md
│   │   ├── implement-deploy-test-pbi-project-file.md
│   │   └── merge-powerbi-projects.md
│   │
│   ├── agents/
│   │   ├── powerbi-artifact-decomposer.md
│   │   ├── powerbi-code-locator.md
│   │   ├── powerbi-data-model-analyzer.md
│   │   └── ... (20+ agents)
│   │
│   ├── tools/
│   │   ├── tmdl_format_validator.py
│   │   ├── pbir_visual_editor.py
│   │   ├── pbi_merger_utils.py
│   │   └── ... (Python utilities)
│   │
│   ├── skills/
│   │   ├── power-bi-assistant/
│   │   │   ├── SKILL.md
│   │   │   └── references/
│   │   └── agentic-workflow-reviewer/
│   │       ├── SKILL.md
│   │       └── references/
│   │
│   ├── helpers/
│   │   └── pbi-url-filter-encoder.md
│   │
│   └── README.md
│
├── .claude-plugin/
│   └── plugin.json
│
├── specs/
│   ├── analyst_findings_template.md
│   ├── artifact_creation_template.md
│   └── power-bi-analyst-desktop-app.md (this file)
│
├── docs/
│   ├── PLUGIN_INSTALLATION.md
│   ├── WORKFLOW_GUIDE.md
│   └── CONTRIBUTING.md
│
├── README.md
├── CHANGELOG.md
├── LICENSE
└── .gitignore
```

### 4.2 Desktop App Repository Structure

```
powerbi-analyst-desktop/
├── frontend/
│   ├── src/
│   │   ├── main.ts                    # Electron main process
│   │   ├── preload.ts                 # Electron preload script
│   │   ├── renderer/
│   │   │   ├── App.tsx                # Main React app
│   │   │   ├── index.tsx              # Entry point
│   │   │   └── index.html             # HTML template
│   │   │
│   │   ├── components/                # Reusable UI components
│   │   │   ├── FilePathInput.tsx
│   │   │   ├── TextArea.tsx
│   │   │   ├── Button.tsx
│   │   │   ├── ProgressBar.tsx
│   │   │   └── FindingsViewer.tsx
│   │   │
│   │   ├── forms/                     # Auto-generated workflow forms
│   │   │   ├── EvaluateProjectForm.tsx
│   │   │   ├── CreateArtifactForm.tsx
│   │   │   ├── ImplementForm.tsx
│   │   │   └── MergeProjectsForm.tsx
│   │   │
│   │   ├── views/                     # Main application views
│   │   │   ├── HomeView.tsx
│   │   │   ├── WorkflowView.tsx
│   │   │   ├── HistoryView.tsx
│   │   │   └── SettingsView.tsx
│   │   │
│   │   ├── api/                       # Backend API client
│   │   │   ├── client.ts
│   │   │   └── types.ts
│   │   │
│   │   └── stores/                    # State management
│   │       ├── workflowStore.ts
│   │       └── settingsStore.ts
│   │
│   ├── assets/                        # Icons, images, fonts
│   │   ├── icon.png
│   │   └── fonts/
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── electron-builder.yml           # Electron packaging config
│   └── vite.config.ts                 # Vite bundler config
│
├── backend/
│   ├── plugin/                        # [GIT SUBMODULE]
│   │   └── .claude/                   # → powerbi-analyst-plugin
│   │
│   ├── executor.py                    # Plugin executor (simulates Claude Code)
│   ├── api.py                         # FastAPI REST API
│   ├── models.py                      # Data models
│   ├── config.py                      # Configuration
│   ├── main.py                        # Backend entry point
│   ├── requirements.txt               # Python dependencies
│   └── build.spec                     # PyInstaller build spec
│
├── scripts/
│   ├── sync-plugin.js                 # Sync plugin → desktop (auto-generate forms)
│   ├── build-backend.sh               # Package Python backend with PyInstaller
│   ├── build-frontend.sh              # Build Electron app
│   ├── build-all.sh                   # Build complete application
│   └── update-submodule.sh            # Update plugin submodule to latest
│
├── docs/
│   ├── DEVELOPMENT.md                 # Developer setup guide
│   ├── ARCHITECTURE.md                # Architecture overview
│   ├── BUILD.md                       # Build & packaging instructions
│   └── USER_GUIDE.md                  # End-user documentation
│
├── .github/
│   └── workflows/
│       ├── build.yml                  # CI/CD: Build on push
│       └── release.yml                # CI/CD: Create release on tag
│
├── .gitmodules                        # Submodule configuration
├── README.md
├── CHANGELOG.md
├── LICENSE
└── .gitignore
```

---

## 5. Development Workflow

### 5.1 Plugin Development Workflow

```bash
# 1. Work on plugin in Claude Code
cd ~/code/powerbi-analyst-plugin

# 2. Create feature branch
git checkout -b feature/new-workflow

# 3. Edit workflow
vim .claude/commands/new-workflow.md

# 4. Test in Claude Code
/new-workflow --test params

# 5. Commit and push
git add .
git commit -m "Add new workflow"
git push origin feature/new-workflow

# 6. Create PR, review, merge to main

# 7. Tag release
git tag v1.3.0
git push origin v1.3.0
```

### 5.2 Desktop App Development Workflow

```bash
# 1. Update plugin submodule to latest
cd ~/code/powerbi-analyst-desktop
cd backend/plugin
git pull origin main
git checkout v1.3.0  # Or specific version tag

cd ../..
git add backend/plugin
git commit -m "Update plugin to v1.3.0"

# 2. Sync plugin to desktop (auto-generate forms)
npm run sync-plugin

# 3. Develop frontend/backend
# Edit React components, add features, etc.

# 4. Test locally
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start frontend dev server
cd frontend
npm run dev

# 5. Test end-to-end
# Use desktop app GUI to execute workflows

# 6. Build for distribution
npm run build

# 7. Commit and push
git add .
git commit -m "Add desktop UI for new workflow"
git push origin main

# 8. Create release
git tag v1.1.0
git push origin v1.1.0
# GitHub Actions automatically builds installers
```

### 5.3 Sync Script (`scripts/sync-plugin.js`)

```javascript
// Pseudo-code for sync script
// This will be implemented in Phase 1

const fs = require('fs-extra');
const path = require('path');

async function syncPlugin() {
  // 1. Parse command specs from backend/plugin/.claude/commands/
  const commandSpecs = await parseCommandSpecs();

  // 2. Generate React forms for each command
  for (const spec of commandSpecs) {
    const formCode = generateReactForm(spec);
    await fs.writeFile(
      `frontend/src/forms/${spec.name}Form.tsx`,
      formCode
    );
  }

  // 3. Update API routes to match commands
  const apiCode = generateAPIRoutes(commandSpecs);
  await fs.writeFile('backend/api.py', apiCode);

  console.log('✅ Plugin synced successfully');
}
```

---

## 6. Technical Stack

### 6.1 Frontend Stack

```json
{
  "framework": "Electron 28+",
  "ui-library": "React 18 + TypeScript 5",
  "styling": "Tailwind CSS 3 + shadcn/ui",
  "state-management": "Zustand 4",
  "forms": "React Hook Form",
  "api-client": "Axios",
  "bundler": "Vite 5",
  "build": "electron-builder"
}
```

### 6.2 Backend Stack

```python
# requirements.txt
anthropic>=0.18.0           # Claude API client
fastapi>=0.110.0            # REST API framework
uvicorn>=0.27.0             # ASGI server
pydantic>=2.6.0             # Data validation
sqlalchemy>=2.0.0           # Database ORM (if needed)
aiofiles>=23.2.0            # Async file operations
python-multipart>=0.0.9     # File upload support

# Existing plugin dependencies
# (all existing Python utilities remain unchanged)
```

### 6.3 Development Tools

```yaml
Version Control: Git + Git Submodules
CI/CD: GitHub Actions
Code Signing:
  - Windows: SignTool (optional)
  - macOS: codesign + notarization (optional)
Package Management:
  - Frontend: npm
  - Backend: pip + venv
Testing:
  - Frontend: Vitest + React Testing Library
  - Backend: pytest
  - E2E: Playwright (optional)
```

---

## 7. Implementation Roadmap

### Phase 0: Pre-Development Setup (1-2 days)

**Goals:** Complete all manual setup and make decisions

**Tasks:**
- [ ] Answer all open questions in Section 8
- [ ] Create GitHub repositories (plugin + desktop)
- [ ] Configure access control
- [ ] Set up development environment
- [ ] Initialize repository structures
- [ ] Test submodule linking

**Deliverables:**
- Two GitHub repositories created and linked
- Development environment ready
- This specification finalized with decisions

---

### Phase 1: Proof of Concept (2-3 weeks)

**Goals:** Validate architecture with single workflow

**Tasks:**
- [ ] Implement `PluginExecutor` (Python backend)
- [ ] Create basic Electron + React shell
- [ ] Implement ONE workflow form (evaluate-pbi-project-file)
- [ ] Build `sync-plugin.js` script (basic version)
- [ ] Test end-to-end: Plugin spec → Desktop GUI → Claude API → Results

**Deliverables:**
- Working desktop app prototype
- One workflow functional (evaluate)
- Sync script operational
- Architecture validated

**Success Criteria:**
- Can execute evaluate workflow from desktop GUI
- Results match Claude Code plugin output
- Sync script successfully generates form from command spec

---

### Phase 2: Core Workflows (4-6 weeks)

**Goals:** Implement all four primary workflows

**Tasks:**
- [ ] Implement all workflow forms
  - [ ] EvaluateProjectForm
  - [ ] CreateArtifactForm
  - [ ] ImplementForm
  - [ ] MergeProjectsForm
- [ ] Build comprehensive UI
  - [ ] Project browser/file picker
  - [ ] Findings viewer with markdown rendering
  - [ ] Progress tracking with real-time updates
  - [ ] Workflow history
- [ ] Complete backend API
  - [ ] All workflow endpoints
  - [ ] WebSocket for progress streaming
  - [ ] File upload/download
- [ ] Error handling and validation
- [ ] State management (Zustand stores)

**Deliverables:**
- All four workflows functional in desktop app
- Complete UI for all workflows
- Comprehensive error handling
- Progress tracking system

---

### Phase 3: Polish & Features (3-4 weeks)

**Goals:** Production-ready features and UX polish

**Tasks:**
- [ ] Settings and preferences
  - [ ] API key management
  - [ ] Workspace/dataset credentials
  - [ ] Theme selection (light/dark)
- [ ] Project management
  - [ ] Recent projects list
  - [ ] Favorites/bookmarks
  - [ ] Version history browser
- [ ] Export features
  - [ ] Export findings to PDF
  - [ ] Export findings to Word
- [ ] UI/UX polish
  - [ ] Loading states
  - [ ] Empty states
  - [ ] Error states
  - [ ] Accessibility (keyboard nav, screen readers)
- [ ] Performance optimization
  - [ ] Lazy loading
  - [ ] Caching
  - [ ] Background processing

**Deliverables:**
- Polished, production-ready UI
- Settings/preferences system
- Export capabilities
- Performance optimizations

---

### Phase 4: Packaging & Distribution (2-3 weeks)

**Goals:** Package app for distribution on all platforms

**Tasks:**
- [ ] Configure electron-builder for all platforms
- [ ] Package Python backend with PyInstaller
- [ ] Create installers
  - [ ] Windows: NSIS installer + portable
  - [ ] macOS: DMG + ZIP
  - [ ] Linux: AppImage + DEB
- [ ] Code signing (optional but recommended)
  - [ ] Windows: Authenticode certificate
  - [ ] macOS: Developer ID + notarization
- [ ] Auto-update implementation
  - [ ] electron-updater configuration
  - [ ] Release metadata (latest.yml)
- [ ] Documentation
  - [ ] User guide
  - [ ] Installation instructions
  - [ ] Troubleshooting guide
- [ ] Set up distribution
  - [ ] GitHub Releases
  - [ ] Download page (optional)

**Deliverables:**
- Installers for Windows, macOS, Linux
- Auto-update functionality
- User documentation
- Distribution infrastructure

---

### Phase 5: Beta Testing & Iteration (2-4 weeks)

**Goals:** Beta test with real users, fix bugs, iterate

**Tasks:**
- [ ] Beta release to select users
- [ ] Gather feedback
- [ ] Bug fixes and improvements
- [ ] Performance tuning
- [ ] Documentation updates based on feedback

**Deliverables:**
- Beta-tested application
- Bug fixes applied
- User feedback incorporated
- Ready for v1.0 release

---

## 8. Open Decisions

### 8.1 GitHub Organization & Naming

**Q1: GitHub Organization**
- [ ] Personal account: `your-username/`
- [x] Organization account: `cn-dataworks`
- [ ] Company account: `_______________/` (specify)

**Decision:** Use existing `cn-dataworks` organization

---

**Q2: Repository History**
- [x] Keep existing history (current repo becomes plugin)
- [ ] Fresh start (archive current, create new)

**Decision:** Keep existing git history. Rename current `powerbi-analyst-agent` → `powerbi-analyst-plugin`. Clean up non-.claude files (move design docs to docs/, remove temp files).

---

### 8.2 Access Control & Collaboration

**Q3: Repository Access**

Plugin repository access:
- [x] Solo development (just you)
- [ ] Team development (specify team members: _______________)
- [ ] Open to contributors

Desktop repository access:
- [x] Solo development (just you)
- [ ] Team development (specify team members: _______________)

**Decision:** Solo development for both repositories initially. Can add collaborators later as needed.

---

**Q6: Development Workflow**
- [ ] Strict: PR reviews required, branch protection
- [ ] Moderate: PR reviews optional
- [x] Flexible: Direct commits allowed (solo dev)

**Decision:** Flexible workflow for solo development. Can add branch protection if team grows later.

---

**Q7: Documentation & Support**
- [ ] GitHub Pages for docs (add in Phase 4)
- [ ] GitHub Discussions for support
- [x] GitHub Issues only
- [ ] External site

**Decision:** GitHub Issues for v1.0. Can add GitHub Pages for documentation website in Phase 4 when ready for broader distribution.

---

### 8.3 Technical Decisions

**Q4: Automated Builds**
- [ ] Yes, CI/CD from start
- [ ] No, manual builds
- [x] Add later (Phase 4)

**Decision:** Manual builds during Phases 1-3 (development). Add GitHub Actions CI/CD in Phase 4 when packaging for distribution.

---

**Q5: Code Signing**
- [x] Windows only (investigate ISV Partner benefits)
- [ ] Yes, both Windows and macOS
- [ ] macOS only
- [ ] No signing initially

**Decision:** Investigate Microsoft ISV Partner benefits for free/discounted code signing certificates for Windows. Add code signing in Phase 4 before v1.0 release. macOS signing optional (requires Apple Developer Program $99/year).

**Action Items:**
- Check Microsoft Partner Center for certificate benefits
- Look for "Code Signing Certificate" or "EV Code Signing" offers
- If not available, budget $100-300/year for certificate purchase
- Windows is priority (primary target platform)

---

**Q8: Development Platform**
- [ ] Windows
- [ ] macOS
- [ ] Linux
- [x] Multiple: Windows + WSL2/Linux

**Decision:** Develop on Windows with WSL2 for cross-platform compatibility. Can test Windows and Linux builds natively. macOS builds via GitHub Actions or borrowed hardware.

---

**Q9: Development Approach**
- [ ] Parallel development (plugin + desktop simultaneously)
- [x] Sequential (plugin first, then desktop)

**Decision:** Sequential approach. First restructure current repo as stable plugin (weeks 1-2), then build desktop app wrapper (week 3+).

---

### 8.4 Claude API & Services

**Q10: API Key Management**
- [x] Users provide their own keys (v1.0 simplicity)
- [ ] You provide embedded key (you pay)
- [ ] Hybrid (free tier + user keys)

**Decision:** Users provide their own Anthropic API keys for v1.0 (simplest implementation). Subscription/proxy model can be added in v1.1+ if monetization desired (see Section 10: Monetization Architecture).

---

**Q11: Expected Usage**
- [x] Low (<100 requests/day) initially
- [ ] Medium (100-1000 requests/day)
- [ ] High (>1000 requests/day)
- [ ] Unknown

**Decision:** Low volume initially during beta/early adoption. Usage patterns will be monitored (without telemetry) based on subscription data if monetization implemented.

---

**Q12: Analytics & Telemetry**
- [ ] Yes (service: _______________)
- [x] No (privacy-first)
- [ ] Add later

**Decision:** No telemetry for v1.0 (privacy-first approach). Can add optional crash reporting in later versions with user opt-in.

---

**Q13: Auto-Updates**
- [x] GitHub Releases + electron-updater
- [ ] Custom update server
- [ ] Manual downloads only

**Decision:** Use GitHub Releases for hosting installers with electron-updater for automatic update notifications and downloads. Free, reliable, and standard Electron pattern.

---

### 8.5 Scope & Features

**Q14: Initial Scope** (for v1.0)
- [x] All four workflows + skills
- [ ] Just evaluate + implement (MVP)
- [ ] Custom scope (specify: _______________)

**Decision:** All four workflows (evaluate, create, implement, merge) plus the skills from main branch (power-bi-assistant, agentic-workflow-reviewer). Skills accessible via submodule in backend/plugin/.claude/skills/.

---

**Q15: Optional Features** (for v1.0)
- [ ] Include deployment to Power BI Service
- [ ] Include automated testing (Playwright)
- [x] Desktop editing only (no deploy/test)

**Decision:** Desktop editing only for v1.0. Remove deployment and automated testing features (too complex for initial release). Users can manually deploy via Power BI Desktop. Add deploy/test features in v1.1+ for advanced users.

---

**Q16: XMLA Integration** (for data sampling)
- [ ] Include from v1.0
- [x] Add in v1.1
- [ ] Not needed initially

**Decision:** No XMLA data sampling in v1.0 (complex authentication, not essential). Workflows still provide value without data sampling. Add in v1.1 for enhanced recommendations.

---

### 8.6 Distribution & Licensing

**Q17: Distribution Model**
- [ ] Free and open source (MIT/Apache)
- [x] Free but proprietary (closed source) for v1.0
- [ ] Commercial (paid licenses)
- [ ] Freemium (basic free, advanced paid)

**Decision:** Both plugin and desktop app will be private/closed source initially. No community contributions planned for v1.0. Allows flexibility for future monetization. Can open source later if desired.

---

**Q18: Target Audience Size**
- [ ] Personal use only
- [x] Small team (5-10 users) initially
- [ ] Department (10-50 users)
- [ ] Enterprise (50+ users)

**Decision:** Target 5-10 beta users for v1.0. Scale to 10-50 early adopters in v1.1+. This helps prioritize features appropriately (no enterprise SSO, complex admin features, etc.).

---

**Q19: Support Model**
- [x] Community support (GitHub Issues)
- [ ] Email support
- [ ] Paid support tiers
- [ ] No formal support

**Decision:** GitHub Issues for bug reports and feature requests. Simple, free, and sufficient for small user base. Can add email support or paid tiers if app becomes commercial product.

---

## 9. References

### Related Documents

- **[DESKTOP_APP_ANALYSIS.md](../DESKTOP_APP_ANALYSIS.md)** - Original desktop app analysis
- **[DESKTOP_APP_UPDATES.md](../DESKTOP_APP_UPDATES.md)** - Update and maintenance guide
- **[.claude/README.md](../.claude/README.md)** - Plugin documentation
- **[analyst_findings_template.md](./analyst_findings_template.md)** - Findings report template
- **[artifact_creation_template.md](./artifact_creation_template.md)** - Artifact creation template

### External Resources

- **Claude Code Plugin Docs:** https://code.claude.com/docs/en/plugins
- **Electron Documentation:** https://www.electronjs.org/docs/latest
- **electron-builder:** https://www.electron.build/
- **Claude Agent SDK:** https://docs.anthropic.com/en/api/agent-sdk
- **FastAPI:** https://fastapi.tiangolo.com/
- **Git Submodules:** https://git-scm.com/book/en/v2/Git-Tools-Submodules

---

## Next Steps

1. ✅ **Review this specification** - Complete (Section 8 decisions filled in)
2. **Execute Pre-Development Setup** (Section 2) - Ready to begin
3. **Begin Phase 1** (Proof of Concept) after setup is complete

---


## 10. Monetization Architecture

**Status:** Phased approach - Simple in v1.0, expand in v1.1+ based on demand

### 10.1 v1.0 Model: 30-Day Trial + Basic Subscription

**Goal:** Keep v1.0 simple while validating market demand

#### **User Experience**

```
Day 1-30: FREE TRIAL
├── Download app (free)
├── Enter Anthropic API key (user pays Anthropic ~$20/month)
├── Use all features (evaluate, create, implement, merge)
└── See banner: "Trial: 7 days remaining"

Day 31+: SUBSCRIPTION REQUIRED
├── Trial expired screen appears
├── Options:
│   ├── Subscribe to Basic ($9.99/month)
│   └── Or app becomes unusable
├── User subscribes via Stripe
├── Receives license key via email
├── Enters license key in app
└── App unlocked - continues working
```

#### **Pricing**

```yaml
Trial (30 days):
  Price: $0
  Features: All workflows
  Requirement: User's Anthropic API key

Basic Subscription:
  Price: $9.99/month or $99/year (save 17%)
  Features: All workflows, all skills, desktop GUI
  Requirement: User's Anthropic API key (they still pay Anthropic)
  Your Revenue: $9.99/month per user
  Your Costs: ~$2/month (Stripe fees: 2.9% + $0.30)
  Your Profit: ~$7.50/month per user
```

**Why this is simple for v1.0:**
- ✅ No backend server needed
- ✅ No API usage tracking
- ✅ No database needed
- ✅ Just Stripe + simple license check
- ✅ Focus on building great desktop app

#### **Revenue at Scale**

```
10 paying users: $100/month = $1,200/year
50 paying users: $500/month = $6,000/year  
100 paying users: $1,000/month = $12,000/year
```

After Stripe fees (~3%), you keep ~$970/month (100 users).

---

### 10.2 v1.0 Implementation

#### **Stripe Setup**

```bash
# 1. Create Stripe account at stripe.com
# 2. Create product in Stripe Dashboard

Product: Power BI Analyst Desktop
  Price: $9.99/month (recurring)
  Price ID: price_basic_monthly (copy this)
  
  Price: $99/year (recurring)
  Price ID: price_basic_yearly
```

#### **Desktop App License Validation**

```typescript
// frontend/src/services/licenseService.ts

export class LicenseService {
  async checkOnStartup(): Promise<boolean> {
    // Step 1: Check if in trial period
    const trial = await this.checkTrial();
    
    if (trial.active) {
      // Show trial banner
      if (trial.daysRemaining <= 7) {
        this.showTrialWarning(trial.daysRemaining);
      }
      return true; // Allow usage
    }
    
    // Step 2: Trial expired - need subscription
    const licenseKey = await keytar.getPassword('powerbi-analyst', 'subscription-id');
    
    if (!licenseKey) {
      // No subscription - block app
      this.showSubscriptionRequiredScreen();
      return false;
    }
    
    // Step 3: Validate subscription with Stripe
    const subscription = await this.validateStripeSubscription(licenseKey);
    
    if (subscription.status !== 'active') {
      this.showRenewSubscriptionScreen();
      return false;
    }
    
    // ✅ Valid subscription - allow usage
    return true;
  }
  
  private async checkTrial() {
    const firstLaunch = await storage.get('first_launch_date');
    
    if (!firstLaunch) {
      // First launch - start trial
      await storage.set('first_launch_date', Date.now());
      return { active: true, daysRemaining: 30 };
    }
    
    const daysSince = (Date.now() - firstLaunch) / (1000 * 60 * 60 * 24);
    const daysRemaining = Math.max(0, 30 - Math.floor(daysSince));
    
    return {
      active: daysRemaining > 0,
      daysRemaining
    };
  }
  
  private async validateStripeSubscription(subscriptionId: string) {
    // Call Stripe API to check subscription status
    const response = await fetch(`https://api.stripe.com/v1/subscriptions/${subscriptionId}`, {
      headers: {
        'Authorization': `Bearer ${STRIPE_SECRET_KEY}`
      }
    });
    
    return await response.json();
  }
}
```

#### **Purchase Flow**

```
1. Trial expires → User sees screen:
   ┌──────────────────────────────────────┐
   │  Trial Expired                       │
   │  Your 30-day trial has ended.        │
   │                                      │
   │  Subscribe to continue:              │
   │  • $9.99/month                       │
   │  • $99/year (save 17%)               │
   │                                      │
   │  [Subscribe Now]  [Exit]             │
   └──────────────────────────────────────┘

2. User clicks "Subscribe Now"
   → Opens browser to Stripe Checkout
   → https://buy.stripe.com/your-checkout-link

3. User completes payment in Stripe
   → Stripe sends webhook to your server (optional)
   → User receives email with subscription ID

4. User enters subscription ID in app
   ┌──────────────────────────────────────┐
   │  Activate Subscription               │
   │  Paste your subscription ID:         │
   │  [___________________________]       │
   │                                      │
   │  [Activate]                          │
   └──────────────────────────────────────┘

5. App validates with Stripe → ✅ Unlocked
```

**Simplified for v1.0:** No webhook needed - user just enters Stripe subscription ID from their email/dashboard.

---

### 10.3 Future Enhancements (v1.1+)

**Add ONLY if users request it:**

#### **Option C: Paid from Day 1 (No Trial)**

```
Download requires purchase first
├── User pays $9.99/month on website
├── Receives download link + license key
└── Installs app (pre-activated)
```

**When to use:** If trial users abuse/exploit the trial period.

#### **Option D: One-Time Purchase**

```
Desktop App: $199 one-time
├── Lifetime access
├── 1 year of updates
├── Still requires Anthropic API key
└── No recurring fees
```

**When to use:** If users resist subscriptions, want to "own" the software.

#### **Pro Tier: API Access Included ($29/month)**

**Requires backend infrastructure:**
- License server for validation
- API proxy server (you pay Anthropic)
- Database for usage tracking
- ~$30-50/month hosting costs

```yaml
Pro: $29/month
  - Desktop app access
  - No Anthropic API key needed
  - YOU provide API access
  - 100 workflows/month included
  - Your costs: ~$15-20/month (Anthropic)
  - Your profit: ~$9-14/month per user
```

**When to add:** If users say "I don't want to manage an API key."

#### **Enterprise Tier ($99/month)**

```yaml
Enterprise: $99/month
  - Everything in Pro
  - 500 workflows/month
  - XMLA data sampling
  - Deployment features
  - Priority support
  - Your costs: ~$85-110/month
  - Your profit: ~$0-14/month per user
```

**When to add:** If you get enterprise customers with higher volume needs.

---

### 10.4 Infrastructure Comparison

#### **v1.0 Infrastructure (Simple)**

```
What you need:
├── Stripe account (free, pay 2.9% + $0.30 per transaction)
├── Simple license validation (Stripe API calls from app)
└── That's it!

Monthly costs: ~$0 (no hosting)
Revenue per user: $9.99/month
Profit per user: ~$7.50/month (after Stripe fees)
```

#### **v1.1+ Infrastructure (If adding Pro tier)**

```
What you need:
├── Stripe account (payment processing)
├── Backend server (DigitalOcean, AWS, etc.) - $15-25/month
├── PostgreSQL database - $15-25/month
├── Domain: api.cn-dataworks.com - $0 (if you own domain)
└── SSL certificate - $0 (Let's Encrypt free)

Monthly costs: ~$30-50/month (hosting + database)
Break-even: 5-6 Basic subscribers OR 2-3 Pro subscribers
```

**Recommendation:** Start with v1.0 model. Only add backend infrastructure if demand justifies the complexity and cost.

---

### 10.5 Summary: Phased Monetization

```
v1.0 (Launch):
  └── 30-day trial → Basic ($9.99/month)
      • Users still need Anthropic API key
      • Simple Stripe integration
      • No backend server needed
      • Focus on great desktop UX

v1.1 (If successful):
  └── Add Option C: No trial, paid from day 1
      • If trial abuse becomes issue

v1.2 (If users request):
  └── Add Option D: One-time purchase ($199)
      • If subscription resistance

v1.3+ (If demand justifies):
  └── Add Pro tier ($29/month) - API included
      • Requires backend infrastructure
      • You manage API keys
      • Better UX for non-technical users
```

**Decision:** Build v1.0 first. Validate that people will pay $9.99/month. Then decide on Pro/Enterprise based on actual user feedback.

---

**End of Specification**

*This document will be updated as development progresses and decisions are made.*
