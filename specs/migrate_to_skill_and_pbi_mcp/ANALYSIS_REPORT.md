# Skill Migration Spec - Gap Analysis Report

**Date:** 2025-12-22
**Reviewer:** Claude Code Analysis
**Spec Version:** SPEC.md (skill-migration branch)

---

## Executive Summary

The specification is **well-engineered** with thoughtful architecture decisions. However, several gaps exist that could impact **non-programmer usability**, **portability**, and **alignment with Anthropic's standard skill patterns**. This report identifies 23 issues across 6 categories with prioritized recommendations.

**Overall Assessment:** 7.5/10 - Strong technical foundation, needs UX polish for non-programmers

---

## 1. Critical Gaps (Must Fix Before Release)

### 1.1 Missing: Skill Frontmatter Metadata

**Issue:** The `specs/migrate_to_skill_and_pbi_mcp/skill.md` file lacks the standard Anthropic skill frontmatter.

**Anthropic Standard Pattern:**
```yaml
---
name: power-bi-analyst
description: [Brief description used in /help and skill discovery]
---
```

**Current State:** The skill.md in the spec folder is a design document, not a deployable skill file. The actual skill needs to be created at `.claude/skills/powerbi-analyst/SKILL.md`.

**Impact:** Users won't be able to discover the skill via `/help` or understand when to invoke it.

**Recommendation:** Create the actual SKILL.md file with proper frontmatter matching the existing skills in the repo.

---

### 1.2 Missing: Explicit "What Gets Installed Where" Section

**Issue:** The spec describes installation conceptually but lacks a concrete file manifest for non-programmers.

**Current State:** Section 7.0.14 discusses authentication, Phase 8 mentions files to create, but there's no simple "here's exactly what ends up on your machine" table.

**Missing Information:**
- Where does the MCP binary go? (System path, local folder, or bundled?)
- Where do skill files go? (`.claude/` in project vs. `~/.claude/` global?)
- What config files are modified? (Full paths for Windows/Mac/Linux)

**Recommendation:** Add an "Installation Manifest" section:

```markdown
## Installation Manifest

### Files Added to Your Project
| File | Purpose |
|------|---------|
| `.claude/skills/powerbi-analyst/SKILL.md` | Main skill entry point |
| `.claude/agents/powerbi-dax-specialist.md` | DAX code generation |
| `.claude/agents/powerbi-mcode-specialist.md` | M code generation |
| ... | ... |

### Files Modified on Your System
| File | Location | Purpose |
|------|----------|---------|
| `claude_desktop_config.json` | `%APPDATA%\Claude\` (Windows) | MCP server registration |
| `settings.json` | `.claude/settings.json` (project) | Permission allowlist |
```

---

### 1.3 Missing: Pre-Installation Validation Script

**Issue:** The spec mentions `setup.py` will diagnose issues, but non-programmers need a **pre-flight check** before committing to installation.

**Gap:** No way to answer "Will this work on my machine?" before starting.

**Recommendation:** Add a `check-requirements.bat` (or PowerShell script) that:
1. Checks for Python 3.9+
2. Checks for Claude Code CLI
3. Checks for Power BI Desktop installation
4. Checks for existing `.claude/` folder
5. Reports green/red status for each
6. Does NOT modify anything - just reports

**User Experience:**
```
> check-requirements.bat

Checking prerequisites...
  [✓] Python 3.11.4 found
  [✓] Claude Code CLI installed
  [✓] Power BI Desktop detected
  [✓] .claude/ folder does not exist (will be created)
  [✓] MCP server not yet configured (will be added)

All prerequisites met! Run install.bat to proceed.
```

---

### 1.4 Ambiguous: "Desktop Mode" vs "Full Mode" Naming

**Issue:** The spec uses "Desktop Mode" to mean "Power BI Desktop connection" but non-programmers might interpret it as "Claude Desktop app mode."

**Confusing Terminology:**
- "Desktop Mode" (Power BI Desktop)
- "Desktop connection" (Power BI Desktop)
- "Claude Desktop" (the application)
- "Fabric Mode" (cloud)
- "Fallback Mode" (no MCP)

**Recommendation:** Use more explicit naming:
- "Power BI Desktop Mode" (local development)
- "Fabric Cloud Mode" (cloud connection)
- "File-Only Mode" (no live connection, fallback)

---

## 2. UX Gaps for Non-Programmers

### 2.1 Missing: Guided First-Run Experience

**Issue:** After installation, users are dropped into the skill with no onboarding.

**Current State:** Section 7.0.16 shows a menu with options [1]-[5], but no guidance on which to pick first.

**Recommendation:** Add a "First-Time Setup" flow:

```markdown
🎉 Welcome to Power BI Analyst!

This appears to be your first time using this skill.
Let me help you get started.

Do you have a Power BI project to work with?
  [Y] Yes, I have a .pbip folder ready
  [N] No, I want to learn about the skill first
  [C] I have a .pbix file (needs conversion)
```

---

### 2.2 Missing: Glossary of Terms

**Issue:** The spec uses technical terms without defining them for non-programmers.

**Undefined Terms:**
- TMDL (Tabular Model Definition Language)
- PBIP (Power BI Project)
- PBIR (Power BI Report)
- Semantic Model
- MCP (Model Context Protocol)
- XMLA (XML for Analysis)
- Query Folding
- Partition

**Recommendation:** Add a Glossary section to the skill's help menu:

```markdown
## Glossary

**TMDL** - Tabular Model Definition Language. The text-based format Power BI
uses to store measures, tables, and relationships in .pbip projects.

**PBIP** - Power BI Project. A folder-based format that stores your report
as editable text files (vs. the compressed .pbix format).
```

---

### 2.3 Overly Technical: Error Messages

**Issue:** While the spec includes "Aggressive Help" for permission errors (good!), other error messages are still technical.

**Example from spec:**
```
❌ CONNECTION FAILED: Power BI Desktop not detected
```

**Better for non-programmers:**
```
❌ Power BI Desktop isn't running

This skill needs Power BI Desktop to test your changes.

📋 Quick Fix:
   1. Open Power BI Desktop from your Start menu
   2. Open your .pbip file (File → Open)
   3. Wait for the model to finish loading
   4. Come back here and try again

💡 Tip: Look for "Ready" in the bottom-left corner of
   Power BI Desktop to confirm it's fully loaded.
```

---

### 2.4 Missing: "What Should I Do Next?" Prompts

**Issue:** After completing a workflow (e.g., EVALUATE), users may not know the next step.

**Current State:** Workflows complete and show a summary, but don't explicitly guide to the next action.

**Recommendation:** Add contextual next-step prompts:

```markdown
✅ EVALUATION COMPLETE

I found 2 issues and proposed fixes in findings.md.

📋 What's Next?
   [1] Review the findings (opens findings.md)
   [2] Apply the changes (runs IMPLEMENT workflow)
   [3] Ask questions about the findings
   [4] Start over with a different problem

Select an option: _
```

---

## 3. Anthropic Skill Architecture Alignment

### 3.1 Gap: Missing `references/` and `assets/` Structure

**Issue:** The existing skills in the repo (`agentic-workflow-creator`, `power-bi-assistant`) use a standardized structure with `references/` and `assets/` subfolders. The spec doesn't define this structure for the new skill.

**Standard Pattern:**
```
.claude/skills/powerbi-analyst/
├── SKILL.md              # Main skill definition
├── README.md             # Optional user guide
├── references/           # Reference documentation
│   ├── dax-patterns.md
│   ├── m-patterns.md
│   └── visual-templates.md
└── assets/               # Templates and examples
    └── findings-template.md
```

**Current Spec:** The `findings_template.md` is in the spec folder, not defined as part of the skill structure.

**Recommendation:** Add explicit skill folder structure to Phase 7 (Create Skill Structure).

---

### 3.2 Gap: Skill Description Too Long

**Issue:** Anthropic's skill pattern uses a brief `description` in frontmatter for discovery. The current spec describes a very complex system.

**Current `power-bi-assistant` skill:**
```yaml
description: This skill should be used when users need guidance navigating
Power BI workflows and commands...
```
(One paragraph)

**Needed for new skill:**
```yaml
description: Analyze, create, and modify Power BI projects with intelligent
assistance. Diagnose calculation issues, create new measures, and deploy
changes with validation. Supports PBIP projects and Power BI Desktop.
```

---

### 3.3 Gap: Internal Agents Not Hidden from Task Tool Registration

**Issue:** The spec says internal agents should be hidden from `/help`, but they're currently registered in the Task tool's agent list (in the system prompt).

**Current State:** All `powerbi-*` agents are listed as Task tool subagent types.

**Anthropic Pattern:** Internal agents should be invocable via Task tool but not shown in user-facing help unless explicitly user-invocable.

**Recommendation:** Clarify in the spec that:
1. Internal agents remain in Task tool registry (for orchestration)
2. Only `/power-bi-assistant` appears in `/help` output
3. Users can still invoke internal agents directly if they know the name (power-user feature)

---

## 4. Portability and Configuration Issues

### 4.1 Windows-Centric Paths

**Issue:** Many examples use Windows paths (`C:\`, `%APPDATA%`) without Mac/Linux equivalents.

**Examples:**
- `C:\Program Files\PowerBI Modeling MCP\powerbi-modeling-mcp.exe`
- `%APPDATA%\Claude\claude_desktop_config.json`

**Recommendation:** Add cross-platform paths:

```markdown
| OS | Config Location |
|----|-----------------|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/claude/claude_desktop_config.json` |
```

**Note:** Power BI Desktop is Windows-only, but Claude Code runs on Mac. The skill should work in "File-Only Mode" on Mac for semantic model editing.

---

### 4.2 Missing: MCP Binary Distribution Strategy

**Issue:** The spec assumes the MCP binary exists but doesn't explain where users get it.

**Current State:** Section mentions "https://github.com/microsoft/powerbi-modeling-mcp" but:
- Is it a direct download?
- Is it on npm/pip?
- Does the installer bundle it?
- What's the versioning strategy?

**Recommendation:** Add explicit MCP acquisition section:

```markdown
## MCP Installation

The Power BI Modeling MCP is distributed by Microsoft as a standalone binary.

### Obtaining the MCP

**Option A: GitHub Release (Recommended)**
1. Go to https://github.com/microsoft/powerbi-modeling-mcp/releases
2. Download the latest release for your platform
3. Extract to a known location (e.g., `C:\Tools\pbi-mcp\`)
4. The installer will ask for this path

**Option B: npm Install**
```bash
npm install -g @microsoft/powerbi-modeling-mcp
```

**Version Compatibility:**
| Skill Version | MCP Version | Notes |
|---------------|-------------|-------|
| 1.0.x | 1.0.x | Initial release |
```

---

### 4.3 Gap: No Uninstall/Rollback Documentation

**Issue:** Users need a way to undo the installation if something goes wrong.

**Missing:**
- How to uninstall the skill
- How to remove MCP configuration
- How to restore original `.claude/` state
- What to do if installation corrupted existing files

**Recommendation:** Add "Uninstallation" section:

```markdown
## Uninstallation

### Remove Skill Files
Delete the following folders from your project:
- `.claude/skills/powerbi-analyst/`
- `.claude/agents/powerbi-*.md` (all Power BI agents)

### Remove MCP Configuration
Edit `%APPDATA%\Claude\claude_desktop_config.json`:
- Remove the "powerbi-modeling" entry from "mcpServers"

### Restore Backup (if created)
If install.bat created a backup, restore from:
- `%USERPROFILE%\.claude-backup-[timestamp]/`
```

---

## 5. Specification Inconsistencies

### 5.1 Conflicting Agent Counts

**Issue:** Different sections report different agent counts.

**Section 6.2 Architecture:** "Agent count reduced: From 27 to ~18"
**Section 7 (Tables):** Lists many agents but doesn't reconcile to 18

**Recommendation:** Add a definitive agent list:

```markdown
## Final Agent Inventory

### Kept (File-Based)
1. powerbi-visual-locator
2. powerbi-visual-type-recommender
3. powerbi-page-layout-designer
4. powerbi-interaction-designer
5. powerbi-pbir-page-generator
6. powerbi-pbir-validator
7. powerbi-visual-implementer-apply
8. powerbi-playwright-tester
9. powerbi-tmdl-syntax-validator
10. powerbi-pattern-discovery

### New (MCP-Enabled)
11. powerbi-dax-specialist
12. powerbi-mcode-specialist

### Replaced by MCP (Deleted)
- powerbi-verify-pbiproject-folder-setup → mcp.connection_operations.connect()
- powerbi-data-context-agent → mcp.dax_query_operations.execute()
- powerbi-code-locator → mcp.measure_operations.get()
- ... (complete list)
```

---

### 5.2 Findings Template Sections Don't Match Spec

**Issue:** The `findings_template.md` has 6 sections, but the spec references different section numbers in various places.

**Template Sections:**
1. Requirements
2. DAX Logic
3. M-Code Logic
4. PBIR Logic
5. Implementation Plan
6. Test Results

**Spec References:**
- "Section 2.B" for visual changes (not defined in template)
- "Section 3" for test cases (template has M-Code Logic in Section 3)

**Recommendation:** Reconcile the template with all spec references. Consider:
- Section 2.A: DAX Logic
- Section 2.B: PBIR Visual Logic
- Section 3: M-Code Logic
- Section 4: Implementation Plan
- Section 5: Test Cases
- Section 6: Test Results

---

### 5.3 State.json Schema Not Fully Defined

**Issue:** The spec shows fragments of state.json in different sections but never provides a complete schema.

**Fragments Found:**
- Section 7.0.7: `session`, `active_tasks`, `resource_locks`
- Section 7.0.13.1: `pbir_info`
- Section 7.0.11: `model_schema`, `mcp_available`

**Recommendation:** Add complete state.json JSON Schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "session": {
      "type": "object",
      "properties": {
        "workflow_id": { "type": "string" },
        "workflow_type": { "type": "string" },
        "started_at": { "type": "string", "format": "date-time" },
        "mcp_mode": { "enum": ["full", "fallback"] }
      }
    },
    "model_schema": { ... },
    "pbir_info": { ... },
    "active_tasks": { ... },
    "resource_locks": { ... }
  }
}
```

---

## 6. Missing Considerations

### 6.1 No Mention of Claude Code Version Compatibility

**Issue:** The skill may rely on Claude Code features that weren't available in older versions.

**Risk:** Users with older Claude Code versions may experience unexpected behavior.

**Recommendation:** Add version requirement:

```markdown
## Requirements

- Claude Code CLI: 1.x or later
- (Specific features used: Task tool, hooks, skill loading)
```

---

### 6.2 No Telemetry Opt-In Language

**Issue:** Section 7.0.15.5 describes OTEL telemetry but doesn't provide user-facing consent language.

**Concern:** Non-programmers may be sensitive to data collection.

**Recommendation:** Add explicit opt-in language:

```markdown
[3/4] Telemetry configuration

Would you like to enable anonymous usage analytics?

This helps improve the skill by tracking:
  • Which workflows are used most
  • Common error patterns
  • Performance metrics

No personal data, project names, or code is collected.

Enable telemetry? [y/N]: _
```

---

### 6.3 No Conflict Resolution for Existing Skills

**Issue:** What happens if the user already has a `.claude/skills/powerbi-analyst/` folder?

**Missing Scenarios:**
- Upgrading from an older version
- User manually created conflicting files
- Partial previous installation

**Recommendation:** Add upgrade/conflict handling:

```markdown
## Upgrade Handling

If an existing installation is detected:

1. **Version Check:** Compare installed vs. new version
2. **Backup:** Create backup of existing files
3. **Merge Strategy:**
   - SKILL.md: Replace with new version
   - references/: Merge (keep user additions)
   - agents/: Replace with new versions
4. **User Confirmation:** Show diff and confirm before overwrite
```

---

### 6.4 Missing: Troubleshooting FAQ

**Issue:** The spec has error messages but no FAQ section for common issues.

**Recommendation:** Add troubleshooting section:

```markdown
## Troubleshooting FAQ

### "MCP not responding"
**Cause:** The MCP server process isn't running
**Fix:** Restart Claude Desktop (the MCP auto-starts)

### "Power BI Desktop not detected"
**Cause:** Desktop isn't running or file isn't open
**Fix:** Open Power BI Desktop and load your .pbip file

### "Permission denied: agent_scratchpads/"
**Cause:** Folder permissions or antivirus block
**Fix:** Add folder to antivirus exceptions

### "TMDL validation failed"
**Cause:** Syntax error in generated code
**Fix:** Review error details in findings.md, manually correct if needed
```

---

## 7. Recommendations Summary

### Priority 1: Must Fix (Blocks Release)
1. [ ] Create actual SKILL.md with proper frontmatter
2. [ ] Add Installation Manifest with exact file locations
3. [ ] Add pre-installation requirements checker script
4. [ ] Clarify "Desktop Mode" terminology

### Priority 2: Should Fix (Impacts Non-Programmer UX)
5. [ ] Add guided first-run experience
6. [ ] Add glossary of technical terms
7. [ ] Improve error messages for non-technical users
8. [ ] Add "What's Next?" prompts after workflows

### Priority 3: Nice to Have (Polish)
9. [ ] Add cross-platform path documentation
10. [ ] Add MCP acquisition instructions
11. [ ] Add uninstallation documentation
12. [x] Reconcile agent counts *(Completed 2025-12-22: SPEC Section 3.2 updated with definitive 19-agent inventory)*
13. [ ] Reconcile findings template sections
14. [ ] Add complete state.json schema
15. [ ] Add Claude Code version requirements
16. [ ] Add telemetry opt-in language
17. [ ] Add upgrade/conflict handling
18. [ ] Add troubleshooting FAQ

---

## 8. Conclusion

The specification demonstrates strong technical thinking with:
- Clear hybrid architecture (MCP + file-based)
- Thoughtful error handling patterns
- Good human-in-the-loop design
- Comprehensive workflow coverage

The main gaps are in **non-programmer accessibility**:
- Installation is technically documented but not user-friendly
- Error messages are developer-oriented
- Missing onboarding and glossary
- No troubleshooting FAQ

With the Priority 1 and 2 fixes, this skill would be ready for non-programmer adoption. The architecture itself is solid and aligns well with Anthropic's skill patterns.

---

*Report generated by Claude Code gap analysis*
