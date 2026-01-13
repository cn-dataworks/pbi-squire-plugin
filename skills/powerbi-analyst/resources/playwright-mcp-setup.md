# Playwright MCP Setup for QA Loop

**This is a Pro-only feature.**

This guide walks you through installing and configuring Playwright MCP, which enables Claude to inspect deployed Power BI reports for visual errors.

---

## What Playwright MCP Does

Playwright MCP allows Claude to:
- Navigate to Power BI Service URLs
- Capture accessibility snapshots (DOM structure)
- Take screenshots of reports
- Detect error indicators (grey boxes, crash messages)
- Interact with page elements

The QA loop uses this to verify deployments work correctly.

---

## Prerequisites

- Node.js 18+ (for npx)
- Claude Code installed
- A browser (Edge or Chrome) logged into Power BI Service

---

## Step 1: Install Node.js

### Windows

**Option A: Using winget (recommended):**
```powershell
winget install OpenJS.NodeJS.LTS
```

**Option B: Manual download:**
1. Go to https://nodejs.org/
2. Download the LTS version
3. Run the installer
4. Restart your terminal

### macOS

```bash
# Using Homebrew
brew install node@20

# Or download from nodejs.org
```

### Verify Installation

```powershell
node --version
# Should output: v18.x.x or higher

npm --version
# Should output: 9.x.x or higher
```

---

## Step 2: Configure MCP in Your Project

The Playwright MCP is configured per-project via a `.mcp.json` file.

### Create/Update .mcp.json

In your Power BI project folder, create or update `.mcp.json`:

```json
{
  "mcpServers": {
    "playwright-extension": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--extension"
      ]
    }
  }
}
```

**Note:** The `--extension` flag enables extended features like screenshots and DOM inspection.

### Alternative: Global Configuration

To enable Playwright MCP for all projects, add to your user MCP config:

**Windows:** `%USERPROFILE%\.claude\mcp.json`
**macOS:** `~/.claude/mcp.json`

```json
{
  "mcpServers": {
    "playwright-extension": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--extension"
      ]
    }
  }
}
```

---

## Step 3: Install Playwright Browsers

The first time Playwright runs, it may need to download browser binaries:

```powershell
npx playwright install chromium
```

This downloads Chromium for Playwright to use. You only need to do this once.

---

## Step 4: Restart Claude Code

After modifying `.mcp.json`, restart Claude Code to load the new MCP server:

1. Close Claude Code (Ctrl+C or close terminal)
2. Open a new terminal
3. Navigate to your project folder
4. Start Claude Code: `claude`

---

## Step 5: Verify MCP is Available

Ask Claude:

> "Can you check if Playwright MCP is available?"

Claude should be able to use browser tools like `browser_navigate` and `browser_snapshot`.

### Quick Test

Ask Claude:

> "Navigate to https://example.com and capture a snapshot"

If Playwright MCP is working, Claude will:
1. Open a browser
2. Navigate to the URL
3. Return an accessibility snapshot of the page

---

## Browser Session for Power BI

### Why Browser Session Matters

Power BI Service requires authentication. Playwright MCP reuses your existing browser session, so:

1. **Before running the QA loop:**
   - Open your regular browser (Edge or Chrome)
   - Go to https://app.powerbi.com
   - Sign in if prompted
   - Keep the browser open

2. **During QA inspection:**
   - Playwright opens a new browser window
   - It shares your authenticated session
   - No additional login required

### If Authentication Fails

If Playwright can't access Power BI:

1. **Refresh your Power BI session:**
   - Go to https://app.powerbi.com in your browser
   - Sign out and sign back in
   - Try the QA loop again

2. **Check browser profile:**
   - Playwright uses the default browser profile
   - Ensure you're signed into Power BI in that profile

3. **Try explicit browser:**
   ```json
   {
     "mcpServers": {
       "playwright-extension": {
         "command": "npx",
         "args": [
           "@playwright/mcp@latest",
           "--extension",
           "--browser", "msedge"
         ]
       }
     }
   }
   ```

---

## How the QA Loop Uses Playwright

```
QA Loop Phase 3: DOM Inspection
        │
        ├── browser_navigate → Report URL
        │   └── Opens Power BI report page
        │
        ├── browser_wait_for → Page load
        │   └── Waits for visuals to render
        │
        ├── browser_snapshot → DOM structure
        │   └── Captures accessibility tree
        │   └── Searches for error patterns
        │
        └── browser_take_screenshot → Evidence
            └── Captures visual state
            └── Saved to qa-results/
```

### Error Detection

The QA inspector searches for:
- **Text patterns:** "Something went wrong", "Unable to load", etc.
- **DOM elements:** Error containers, alert dialogs
- **Visual indicators:** Grey boxes, missing content

---

## Troubleshooting

### "MCP server not found" or "Playwright MCP not available"

1. **Check .mcp.json exists** in your project folder
2. **Verify JSON syntax** is valid (no trailing commas)
3. **Restart Claude Code** after modifying .mcp.json
4. **Check Node.js version:** `node --version` (need 18+)

### "Browser not installed"

Run Playwright browser installation:
```powershell
npx playwright install chromium
```

### "Navigation failed" or "Timeout"

1. **Check the URL** is accessible in your regular browser
2. **Power BI may be slow** - the report might need time to load
3. **Try increasing timeout** in the workflow parameters

### "Authentication required" when accessing Power BI

1. Open your regular browser
2. Go to https://app.powerbi.com
3. Sign in
4. Keep browser open
5. Retry the QA loop

### Playwright opens wrong browser

Specify the browser explicitly in `.mcp.json`:
```json
{
  "mcpServers": {
    "playwright-extension": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--extension",
        "--browser", "chromium"
      ]
    }
  }
}
```

Options: `chromium`, `firefox`, `webkit`, `msedge`

### Screenshots not saving

1. Check the `qa-results/` folder exists or can be created
2. Verify write permissions in your project folder
3. Screenshots may be in a different location - check Claude's output

---

## Advanced Configuration

### Custom Browser Path

If you have a specific browser installation:

```json
{
  "mcpServers": {
    "playwright-extension": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--extension"
      ],
      "env": {
        "PLAYWRIGHT_BROWSERS_PATH": "C:\\path\\to\\browsers"
      }
    }
  }
}
```

### Headless Mode

By default, Playwright shows the browser. For headless operation:

```json
{
  "mcpServers": {
    "playwright-extension": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--extension",
        "--headless"
      ]
    }
  }
}
```

**Note:** Headless mode may have issues with Power BI authentication.

### Viewport Size

Set a specific viewport for consistent screenshots:

```json
{
  "mcpServers": {
    "playwright-extension": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--extension",
        "--viewport", "1920x1080"
      ]
    }
  }
}
```

---

## Security Considerations

1. **Session reuse:** Playwright can access any site you're logged into
2. **Screenshots:** May capture sensitive data - use anonymized data
3. **Local only:** Playwright runs locally, doesn't send data externally
4. **Close browser:** After QA loop, Playwright browser closes automatically

---

## Next Steps

After setting up Playwright MCP:

1. **Verify GitHub setup** - See `github-setup-for-powerbi.md`
2. **Configure deployment** - See `fabric-deployment-setup.md`
3. **Run the QA loop** - `/qa-loop-pbi-dashboard --project ... --repo ... --report-url ...`

---

## See Also

- `qa-loop-prerequisites.md` - Complete prerequisites checklist
- `github-setup-for-powerbi.md` - GitHub repository setup
- `fabric-deployment-setup.md` - Deployment pipeline setup
- `workflows/qa-loop-pbi-dashboard.md` - QA loop workflow documentation
- `agents/powerbi-qa-inspector.md` - QA inspector agent details
