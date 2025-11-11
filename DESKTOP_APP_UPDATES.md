# Desktop App Updates & Maintenance Guide

This guide explains how to update your Power BI Analyst desktop app after initial deployment, including development workflow, version management, and distribution strategies.

---

## Table of Contents

1. [Development Workflow](#development-workflow)
2. [Version Management](#version-management)
3. [Building Updated Versions](#building-updated-versions)
4. [Distribution Strategies](#distribution-strategies)
5. [Auto-Update Implementation](#auto-update-implementation)
6. [Testing Updates](#testing-updates)
7. [Rollback Strategy](#rollback-strategy)
8. [Best Practices](#best-practices)

---

## 1. Development Workflow

### Local Development Environment

Your development setup stays the same as when building the initial version:

```bash
# Project structure
power-bi-analyst-desktop/
├── frontend/           # Electron + React
├── backend/           # Python + Agent SDK
└── .git/              # Version control
```

### Making Changes

**Step 1: Create a feature branch**
```bash
git checkout -b feature/add-export-to-pdf
```

**Step 2: Make your changes**

Example - Adding a new feature:
```typescript
// frontend/src/components/ExportButton.tsx
export const ExportToPDF = () => {
  const handleExport = async () => {
    await api.exportFindingsToPDF(workflowId);
  };

  return <button onClick={handleExport}>Export to PDF</button>;
};
```

```python
# backend/api/export.py
@app.post("/api/workflows/{workflow_id}/export-pdf")
async def export_to_pdf(workflow_id: str):
    state = load_workflow_state(workflow_id)
    pdf_path = generate_pdf_report(state)
    return {"pdf_path": pdf_path}
```

**Step 3: Test locally**
```bash
# Start backend (terminal 1)
cd backend
python main.py

# Start frontend in dev mode (terminal 2)
cd frontend
npm start
```

**Step 4: Commit changes**
```bash
git add .
git commit -m "Add PDF export feature"
git push origin feature/add-export-to-pdf
```

**Step 5: Merge to main**
```bash
git checkout main
git merge feature/add-export-to-pdf
```

---

## 2. Version Management

### Semantic Versioning (SemVer)

Use semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (1.0.0 → 2.0.0)
- **MINOR**: New features, backwards compatible (1.0.0 → 1.1.0)
- **PATCH**: Bug fixes (1.0.0 → 1.0.1)

### Where to Update Version Numbers

**Frontend (package.json):**
```json
{
  "name": "power-bi-analyst-desktop",
  "version": "1.2.0",  // ← Update this
  "description": "Desktop app for Power BI project analysis",
  "main": "main.js"
}
```

**Backend (version.py or __init__.py):**
```python
# backend/__init__.py
__version__ = "1.2.0"  # ← Update this
```

**Keep versions in sync** between frontend and backend for consistency.

### Version Update Checklist

When releasing a new version:
- [ ] Update `frontend/package.json` version
- [ ] Update `backend/__init__.py` version
- [ ] Update `CHANGELOG.md` with changes
- [ ] Create git tag: `git tag v1.2.0`
- [ ] Push tag: `git push origin v1.2.0`

---

## 3. Building Updated Versions

### Building Frontend (Electron App)

**Update build configuration:**
```json
// frontend/package.json
{
  "build": {
    "appId": "com.yourcompany.powerbi-analyst",
    "productName": "Power BI Analyst",
    "files": [
      "dist/**/*",
      "node_modules/**/*",
      "package.json"
    ],
    "directories": {
      "buildResources": "assets",
      "output": "release"
    },
    "win": {
      "target": ["nsis", "portable"],
      "icon": "assets/icon.ico"
    },
    "mac": {
      "target": ["dmg", "zip"],
      "icon": "assets/icon.icns",
      "category": "public.app-category.developer-tools"
    },
    "linux": {
      "target": ["AppImage", "deb"],
      "icon": "assets/icon.png",
      "category": "Development"
    }
  }
}
```

**Build command:**
```bash
cd frontend

# Build for current platform
npm run build

# Build for specific platforms
npm run build -- --win       # Windows
npm run build -- --mac       # macOS
npm run build -- --linux     # Linux

# Build for all platforms (requires platform-specific tools)
npm run build -- --win --mac --linux
```

**Output:**
```
frontend/release/
├── Power BI Analyst Setup 1.2.0.exe       # Windows installer
├── Power BI Analyst-1.2.0.dmg              # macOS installer
├── power-bi-analyst-1.2.0.AppImage         # Linux AppImage
└── latest.yml                               # Update metadata
```

### Packaging Backend (Python)

**Option 1: PyInstaller (Standalone Executable)**

Create `backend/build.spec`:
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('utils/*.py', 'utils'),
        ('tools/*.py', 'tools'),
    ],
    hiddenimports=[
        'claude_agent_sdk',
        'fastapi',
        'uvicorn',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pbi-analyst-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

**Build backend:**
```bash
cd backend
pip install pyinstaller
pyinstaller build.spec

# Output: backend/dist/pbi-analyst-backend.exe (or binary for your OS)
```

**Option 2: Bundle Python with App**

Include Python runtime with your app (simpler, larger file size):
```
frontend/resources/
├── python/                    # Python runtime
│   ├── python.exe            # Windows
│   ├── python3               # Linux/macOS
│   └── lib/                  # Python libraries
└── backend/                  # Your Python code
    ├── main.py
    └── ...
```

Your Electron main process starts the backend:
```typescript
// frontend/main.ts
import { spawn } from 'child_process';
import path from 'path';

let pythonProcess;

app.on('ready', () => {
  // Start Python backend
  const pythonPath = path.join(
    process.resourcesPath,
    'python',
    process.platform === 'win32' ? 'python.exe' : 'python3'
  );

  const backendScript = path.join(
    process.resourcesPath,
    'backend',
    'main.py'
  );

  pythonProcess = spawn(pythonPath, [backendScript]);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Backend: ${data}`);
  });

  // Wait for backend to start
  setTimeout(() => createWindow(), 2000);
});

app.on('will-quit', () => {
  if (pythonProcess) {
    pythonProcess.kill();
  }
});
```

---

## 4. Distribution Strategies

### Option 1: GitHub Releases (Recommended for Open Source)

**Advantages:**
- ✅ Free hosting
- ✅ Built-in version tracking
- ✅ Easy to automate with GitHub Actions
- ✅ Users can download directly

**Setup:**

1. Create a release on GitHub:
```bash
git tag v1.2.0
git push origin v1.2.0
```

2. Upload build artifacts:
```bash
# Using GitHub CLI
gh release create v1.2.0 \
  frontend/release/Power-BI-Analyst-Setup-1.2.0.exe \
  frontend/release/Power-BI-Analyst-1.2.0.dmg \
  frontend/release/power-bi-analyst-1.2.0.AppImage \
  --title "Version 1.2.0" \
  --notes "See CHANGELOG.md for details"
```

3. Users download from: `https://github.com/your-org/powerbi-analyst-desktop/releases`

### Option 2: Self-Hosted Distribution

**Advantages:**
- ✅ Full control
- ✅ Private distribution
- ✅ Custom branding

**Setup:**

1. Create a static file server:
```
https://yourcompany.com/downloads/
├── latest.json                           # Version metadata
├── windows/
│   └── Power-BI-Analyst-Setup-1.2.0.exe
├── macos/
│   └── Power-BI-Analyst-1.2.0.dmg
└── linux/
    └── power-bi-analyst-1.2.0.AppImage
```

2. Create version metadata (`latest.json`):
```json
{
  "version": "1.2.0",
  "releaseDate": "2025-11-08",
  "releaseNotes": "https://yourcompany.com/releases/1.2.0",
  "downloads": {
    "windows": {
      "url": "https://yourcompany.com/downloads/windows/Power-BI-Analyst-Setup-1.2.0.exe",
      "sha256": "abc123..."
    },
    "macos": {
      "url": "https://yourcompany.com/downloads/macos/Power-BI-Analyst-1.2.0.dmg",
      "sha256": "def456..."
    },
    "linux": {
      "url": "https://yourcompany.com/downloads/linux/power-bi-analyst-1.2.0.AppImage",
      "sha256": "ghi789..."
    }
  }
}
```

### Option 3: Microsoft Store / Mac App Store

**Advantages:**
- ✅ Automatic updates
- ✅ User trust
- ✅ Built-in payment (if paid app)

**Disadvantages:**
- ❌ Review process required
- ❌ Annual fees ($99 for Apple, $19 one-time for Microsoft)
- ❌ Strict guidelines

**When to use:** For wider commercial distribution.

---

## 5. Auto-Update Implementation

### Electron Builder Auto-Updater

**Install dependencies:**
```bash
npm install electron-updater
```

**Configure auto-update:**
```typescript
// frontend/main.ts
import { autoUpdater } from 'electron-updater';
import { BrowserWindow, ipcMain } from 'electron';

let mainWindow: BrowserWindow;

// Configure update server
autoUpdater.setFeedURL({
  provider: 'github',
  owner: 'your-org',
  repo: 'powerbi-analyst-desktop'
});

// OR for self-hosted:
autoUpdater.setFeedURL({
  provider: 'generic',
  url: 'https://yourcompany.com/downloads'
});

// Auto-update logic
app.on('ready', () => {
  createWindow();

  // Check for updates on startup
  autoUpdater.checkForUpdatesAndNotify();

  // Check for updates every 4 hours
  setInterval(() => {
    autoUpdater.checkForUpdates();
  }, 4 * 60 * 60 * 1000);
});

// Update events
autoUpdater.on('checking-for-update', () => {
  console.log('Checking for updates...');
});

autoUpdater.on('update-available', (info) => {
  console.log('Update available:', info.version);

  // Notify user
  mainWindow.webContents.send('update-available', info);
});

autoUpdater.on('update-not-available', () => {
  console.log('App is up to date');
});

autoUpdater.on('download-progress', (progressObj) => {
  console.log(`Download progress: ${progressObj.percent}%`);

  // Send progress to renderer
  mainWindow.webContents.send('download-progress', progressObj);
});

autoUpdater.on('update-downloaded', (info) => {
  console.log('Update downloaded:', info.version);

  // Prompt user to restart
  mainWindow.webContents.send('update-downloaded', info);
});

// IPC handlers for update actions
ipcMain.on('install-update', () => {
  autoUpdater.quitAndInstall();
});
```

**Frontend UI for updates:**
```typescript
// frontend/src/components/UpdateNotification.tsx
import React, { useEffect, useState } from 'react';

export const UpdateNotification = () => {
  const [updateInfo, setUpdateInfo] = useState(null);
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [status, setStatus] = useState(''); // 'available', 'downloading', 'ready'

  useEffect(() => {
    // Listen for update events from main process
    window.electron.on('update-available', (info) => {
      setUpdateInfo(info);
      setStatus('available');
    });

    window.electron.on('download-progress', (progress) => {
      setDownloadProgress(progress.percent);
      setStatus('downloading');
    });

    window.electron.on('update-downloaded', (info) => {
      setStatus('ready');
    });
  }, []);

  if (status === 'available') {
    return (
      <div className="update-notification">
        <p>Version {updateInfo.version} is available!</p>
        <button onClick={() => window.electron.send('start-download')}>
          Download Update
        </button>
      </div>
    );
  }

  if (status === 'downloading') {
    return (
      <div className="update-notification">
        <p>Downloading update... {Math.round(downloadProgress)}%</p>
        <progress value={downloadProgress} max="100" />
      </div>
    );
  }

  if (status === 'ready') {
    return (
      <div className="update-notification">
        <p>Update ready to install!</p>
        <button onClick={() => window.electron.send('install-update')}>
          Restart & Install
        </button>
        <button onClick={() => setStatus('')}>
          Install Later
        </button>
      </div>
    );
  }

  return null;
};
```

### Update Flow Diagram

```
User Opens App
      ↓
Check for Updates (Background)
      ↓
  ┌───────────────────┐
  │ Update Available? │
  └───────┬───────────┘
          │
    Yes   │   No
    ↓     │     ↓
[Notify User]  [Continue Normally]
    ↓
User Clicks "Download"
    ↓
Download in Background
    ↓
Show Progress Bar
    ↓
Download Complete
    ↓
[Notify User: "Ready to Install"]
    ↓
User Clicks "Restart & Install"
    ↓
App Closes → Installer Runs → App Reopens with New Version
```

---

## 6. Testing Updates

### Pre-Release Testing Checklist

Before releasing an update:

**1. Local Testing**
```bash
# Test in development mode
npm start

# Test production build locally
npm run build
# Install and test the built installer
```

**2. Beta Testing**

Create a beta channel for early testing:

```json
// package.json - Beta version
{
  "version": "1.2.0-beta.1"
}
```

Distribute to beta testers via separate release:
```bash
gh release create v1.2.0-beta.1 \
  --prerelease \
  --title "Beta: Version 1.2.0" \
  frontend/release/Power-BI-Analyst-Setup-1.2.0-beta.1.exe
```

**3. Update Testing**

Test the update mechanism:
```bash
# 1. Install previous version (e.g., 1.1.0)
# 2. Publish new version (1.2.0) to update server
# 3. Open app, verify update notification appears
# 4. Download update, verify progress bar works
# 5. Install update, verify app restarts with new version
# 6. Verify all features work after update
```

**4. Automated Testing**

Create update tests:
```typescript
// tests/update.spec.ts
import { test, expect } from '@playwright/test';

test('Update notification appears', async ({ page }) => {
  // Mock update server response
  await page.route('**/latest.json', (route) =>
    route.fulfill({
      json: { version: '1.2.0', ... }
    })
  );

  await page.goto('/');

  // Verify update notification
  await expect(page.locator('.update-notification')).toBeVisible();
});
```

---

## 7. Rollback Strategy

### What if an update breaks something?

**Option 1: Publish a Fixed Version**

Fastest solution - release a patch version:
```bash
# Fix the bug
git checkout -b hotfix/critical-bug
# Make fix
git commit -m "Fix critical bug in update 1.2.0"

# Release as 1.2.1
# Update version numbers
git tag v1.2.1
npm run build
gh release create v1.2.1 ...
```

**Option 2: Rollback to Previous Version**

Update your `latest.json` to point to previous version:
```json
{
  "version": "1.1.0",  // ← Point back to stable version
  "downloads": {
    "windows": {
      "url": "https://yourcompany.com/downloads/windows/Power-BI-Analyst-Setup-1.1.0.exe"
    }
  }
}
```

Users will see: "Version 1.1.0 is available" and can "downgrade" to stable version.

**Option 3: User-Initiated Rollback**

Allow users to manually download previous versions:
```
https://yourcompany.com/downloads/archive/
├── v1.0.0/
├── v1.1.0/
└── v1.2.0/
```

---

## 8. Best Practices

### Version Release Cadence

**Recommended Schedule:**
- **Patch releases** (bug fixes): As needed
- **Minor releases** (new features): Monthly or bi-monthly
- **Major releases** (breaking changes): Quarterly or annually

### Changelog Management

Keep a `CHANGELOG.md`:
```markdown
# Changelog

All notable changes to Power BI Analyst Desktop will be documented in this file.

## [1.2.0] - 2025-11-08

### Added
- PDF export feature for findings reports
- Dark mode theme option
- Project history browser

### Changed
- Improved XMLA authentication flow
- Updated Agent SDK to v0.2.0

### Fixed
- Fixed crash when analyzing large TMDL files
- Fixed memory leak in findings viewer

## [1.1.0] - 2025-10-15

### Added
- PBIR visual editing support
- Merge workflow for comparing projects

...
```

### Communication with Users

**1. In-App Notifications**
Show what's new after an update:
```typescript
// Show release notes on first launch after update
if (previousVersion !== currentVersion) {
  showReleaseNotesDialog(currentVersion);
}
```

**2. Email Notifications (Optional)**
For enterprise users, email update notifications:
```
Subject: Power BI Analyst Desktop v1.2.0 Available

Hi [User],

Version 1.2.0 is now available with new features:
- PDF export
- Dark mode
- Performance improvements

Download: https://yourcompany.com/downloads

Changelog: https://yourcompany.com/releases/1.2.0
```

**3. Website/Blog**
Publish release notes on your website for transparency.

### Breaking Changes

If you must make breaking changes:
1. **Communicate clearly** - Give users advance notice
2. **Provide migration guide** - Document how to adapt
3. **Offer support** - Help users transition
4. **Consider compatibility mode** - Support old behavior temporarily

Example:
```
# Version 2.0.0 Breaking Changes

## Changed: Findings File Format

The findings file format has changed from markdown to JSON.

### Migration:
Run this command to convert old findings files:
```bash
pbi-analyst migrate-findings --input findings.md --output findings.json
```

### Compatibility:
Version 2.0.0 can still read v1.x findings files for 6 months.
Support will be removed in v2.6.0 (June 2026).
```

### Monitoring & Analytics

Track update adoption:
```typescript
// Optional: Send anonymous usage statistics
import analytics from './analytics';

autoUpdater.on('update-downloaded', (info) => {
  analytics.track('update_downloaded', {
    from_version: app.getVersion(),
    to_version: info.version,
    platform: process.platform
  });
});
```

This helps you understand:
- How quickly users update
- Which platforms need attention
- If updates are causing issues

---

## 9. Continuous Integration/Deployment (CI/CD)

### Automate the Build Process

**GitHub Actions Example:**

Create `.github/workflows/release.yml`:
```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'  # Trigger on version tags (e.g., v1.2.0)

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install frontend dependencies
        run: |
          cd frontend
          npm install

      - name: Install backend dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pyinstaller

      - name: Build backend
        run: |
          cd backend
          pyinstaller build.spec

      - name: Build frontend
        run: |
          cd frontend
          npm run build
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.os }}-build
          path: frontend/release/*

  release:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v3

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            windows-latest-build/*
            macos-latest-build/*
            ubuntu-latest-build/*
          generate_release_notes: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Usage:**
```bash
# Create a release by pushing a version tag
git tag v1.2.0
git push origin v1.2.0

# GitHub Actions will automatically:
# 1. Build for Windows, macOS, and Linux
# 2. Create a GitHub Release
# 3. Upload installers as release assets
```

---

## 10. Quick Reference: Update Workflow

### Full Update Workflow Checklist

- [ ] **1. Make Changes**
  - Create feature branch
  - Implement changes
  - Test locally
  - Commit and push

- [ ] **2. Update Version**
  - Bump version in `frontend/package.json`
  - Bump version in `backend/__init__.py`
  - Update `CHANGELOG.md`
  - Create git tag: `git tag v1.2.0`

- [ ] **3. Build**
  - Build backend: `cd backend && pyinstaller build.spec`
  - Build frontend: `cd frontend && npm run build`
  - Test installers on all platforms

- [ ] **4. Test**
  - Install on clean machine
  - Test all features
  - Test update mechanism (if applicable)

- [ ] **5. Release**
  - Push tag: `git push origin v1.2.0`
  - Create GitHub release (or upload to your server)
  - Update `latest.json` metadata

- [ ] **6. Announce**
  - Post release notes on website/blog
  - Notify users (email, in-app, social media)
  - Monitor for issues

- [ ] **7. Monitor**
  - Check error reports
  - Monitor update adoption
  - Respond to user feedback

---

## Summary

**For beginners, I recommend:**

1. **Start Simple**: Use GitHub Releases for distribution
2. **Add Auto-Update**: Implement electron-updater early
3. **Automate Builds**: Set up GitHub Actions CI/CD
4. **Test Thoroughly**: Always test on clean machines
5. **Communicate**: Keep users informed of changes

**Typical Timeline:**
- Small bug fix: 1-2 days (code → test → release)
- New feature: 1-2 weeks (develop → test → release)
- Major version: 1-3 months (plan → develop → beta → release)

**Remember:**
- Version numbers communicate change impact
- Auto-updates make distribution easy
- Always test before releasing
- Keep old versions available for rollback
- Communicate changes clearly to users

You're building a desktop app, but the update process is similar to maintaining any software - iterate, test, release, repeat! 🚀
