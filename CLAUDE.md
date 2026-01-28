# Power BI Analyst Plugin

Claude Code plugin for Power BI project analysis, modification, and deployment.

## What It Does

One comprehensive skill: **`powerbi-analyst`**

| Workflow | Purpose | Trigger Example |
|----------|---------|-----------------|
| EVALUATE | Diagnose and fix issues | "Fix this measure" |
| CREATE_ARTIFACT | Create new DAX measures/columns | "Create a YoY measure" |
| DATA_PREP | M code / Power Query transformations | "Filter this table" |
| ANALYZE | Document dashboards in business language | "Explain this dashboard" |
| IMPLEMENT | Apply planned changes | "Apply the changes" |
| MERGE | Compare and merge projects | "Merge these projects" |

The skill automatically routes requests to the appropriate workflow.

## Key Commands

| Command | Purpose |
|---------|---------|
| `/evaluate-pbi-project-file` | Analyze and diagnose issues |
| `/create-pbi-artifact` | Create measures, columns, tables, visuals |
| `/implement-deploy-test-pbi-project-file` | Deploy and test changes |
| `/merge-powerbi-projects` | Compare and merge projects |

Or just describe what you need - the skill will route appropriately.

## Development

When working on this plugin codebase, consult `CONTRIBUTING.md` for:

- **Git operations** - Which branch to use (`main` vs `pro`)
- **Committing changes** - Feature branches, commit workflow
- **Merging/pushing** - Cascading changes from `main` to `pro`
- **Adding features** - Core (both versions) vs Pro-only features
- **Hotfixes** - Critical bug fix workflow

**Key rule:** Changes flow `main` → `pro`, never the reverse.

### Before ANY Commit

**STOP and verify:**

1. **Is this a Core feature or Pro feature?**
   - Core = benefits all users → branch from `main`
   - Pro = paid/advanced only → branch from `pro`
   - See `CONTRIBUTING.md` → "Pro-Only Features" and "Core Features" sections for complete lists

2. **Am I on the correct branch?**
   ```bash
   git branch  # Check current branch
   ```

3. **Will this need to cascade?**
   - Core changes → YES, cascade `main` → `pro` after merge
   - Pro changes → NO, stays in `pro` only

4. **What type of version bump is needed?**

   | Change Type | Bump | Example | When to Use |
   |-------------|------|---------|-------------|
   | **MAJOR** | `X.0.0` | `1.2.0` → `2.0.0` | Breaking changes, removed features, major restructure |
   | **MINOR** | `0.X.0` | `1.2.0` → `1.3.0` | New features, new workflows, new commands |
   | **PATCH** | `0.0.X` | `1.2.0` → `1.2.1` | Bug fixes, typos, small tweaks, documentation |

   **Before pushing, run:**
   ```powershell
   .\tools\sync-version.ps1 -Version "X.Y.Z"
   git add tools/core/version.txt .claude-plugin/plugin.json
   ```

See `CONTRIBUTING.md` for detailed scenarios and commands.

### Release Workflow

After pushing a version bump, create a GitHub release with release notes:

```powershell
# 1. Bump version and commit
.\tools\sync-version.ps1 -Version "1.4.0"
git add tools/core/version.txt .claude-plugin/plugin.json
git commit -m "Bump version to 1.4.0"

# 2. Push and tag
git push origin main
git tag -a v1.4.0 -m "Release 1.4.0"
git push origin v1.4.0

# 3. Create GitHub release
gh release create v1.4.0 --title "v1.4.0" --notes "release notes here"

# 4. Cascade to pro and repeat for pro-origin
```

### Release Notes Template

```markdown
## What's New in X.Y.Z

### Features
- Added [feature] - [one-line description]

### Fixes
- Fixed [issue] - [what was wrong]

### Breaking Changes
- [Only if applicable - removal, API changes, etc.]

## Files Changed
- [List key files that changed]
```

**When to create releases:**

| Scenario | Create Release? |
|----------|-----------------|
| Version bump (MAJOR/MINOR/PATCH) | **Yes** |
| Internal refactor (no user impact) | Optional |
| Work-in-progress commits | No |

---

## Documentation Update Matrix

When modifying this plugin, **all affected documentation must be updated together**. Use these checklists to ensure consistency.

### Adding a New Workflow

| File | Action | Required |
|------|--------|----------|
| `skills/powerbi-analyst/workflows/<name>.md` | Create workflow documentation | Yes |
| `skills/powerbi-analyst/SKILL.md` | Add to "Trigger Actions" section | Yes |
| `skills/powerbi-analyst/SKILL.md` | Add to "Example Prompts" table | Yes |
| `agents/core/powerbi-orchestrator.md` | Add to routing decision tree | Yes |
| `skills/powerbi-analyst/pro-features.md` | Add trigger + workflow section | If Pro |
| `CONTRIBUTING.md` | Add to "Pro-Only Features" table | If Pro |
| `.gitignore` (on `main` branch) | Add workflow path | If Pro |

### Adding a New Agent

| File | Action | Required |
|------|--------|----------|
| `skills/powerbi-analyst/agents/<name>.md` | Create agent documentation | Yes |
| `skills/powerbi-analyst/SKILL.md` | Add to "Specialist Agents" section | If orchestrated |
| `skills/powerbi-analyst/pro-features.md` | Add to "Pro Specialist Agents" | If Pro |
| Workflow that invokes it | Reference the agent | Yes |
| `CONTRIBUTING.md` | Add to "Pro-Only Features" table | If Pro |
| `.gitignore` (on `main` branch) | Add agent path | If Pro |

### Adding a New Tool (Python)

| File | Action | Required |
|------|--------|----------|
| `tools/core/<name>.py` | Create tool | If Core |
| `tools/advanced/<name>.py` | Create tool | If Pro |
| `tools/bootstrap.ps1` | Add to `$CoreToolFiles` or `$AdvancedToolFiles` | Yes |
| `tools/bootstrap.sh` | Add to copy list | Yes |
| `CONTRIBUTING.md` | Add to "Pro-Only Features" table | If Pro |
| `.gitignore` (on `main` branch) | Add tool path | If Pro |

### Adding a New Reference Document

| File | Action | Required |
|------|--------|----------|
| `skills/powerbi-analyst/references/<name>.md` | Create reference | Yes |
| `skills/powerbi-analyst/SKILL.md` | Add to "References" section | If user-facing |
| `skills/powerbi-analyst/pro-features.md` | Add to "Pro References" | If Pro |
| Agents/workflows that use it | Add "See Also" or load instructions | Yes |
| `CONTRIBUTING.md` | Add to "Pro-Only Features" table | If Pro |
| `.gitignore` (on `main` branch) | Add reference path | If Pro |

### Adding a New Template (Bootstrap)

| File | Action | Required |
|------|--------|----------|
| `tools/templates/<name>` | Create template file | Yes |
| `tools/bootstrap.ps1` | Add copy logic | Yes |
| `tools/bootstrap.sh` | Add copy logic | Yes |
| `skills/powerbi-analyst/pro-features.md` | Document if Pro bootstrap feature | If Pro |

### Adding/Modifying Trigger Patterns

| File | Action | Required |
|------|--------|----------|
| `skills/powerbi-analyst/SKILL.md` | Update "Trigger Actions" | Yes |
| `agents/core/powerbi-orchestrator.md` | Update routing decision tree | Yes |
| `skills/powerbi-analyst/pro-features.md` | Update "Pro Trigger Actions" | If Pro |

### Modifying a Skill's Capabilities

| File | Action | Required |
|------|--------|----------|
| `skills/<skill>/SKILL.md` | Update capability description | Yes |
| `CLAUDE.md` | Update "What It Does" table | If major change |
| `README.md` | Update feature list | If user-visible |
| `skills/powerbi-analyst/resources/getting-started.md` | Update if affects onboarding | If applicable |

---

## Documentation File Inventory

### Root Level
| File | Purpose | Update When |
|------|---------|-------------|
| `CLAUDE.md` | Plugin overview for Claude/developers | Skills or commands change |
| `CONTRIBUTING.md` | Git workflow, branch strategy, Pro features list | Adding Pro features, changing workflow |
| `README.md` | User installation guide | Installation process changes |
| `INSTALL.md` | Detailed installation steps | Installation process changes |

### Skill Documentation (`skills/powerbi-analyst/`)
| File | Purpose | Update When |
|------|---------|-------------|
| `SKILL.md` | Main skill definition, triggers, workflows | Any capability change |
| `pro-features.md` | Pro-only features index | Adding Pro features |

### Resources (`skills/powerbi-analyst/resources/`)
| File | Purpose | Update When |
|------|---------|-------------|
| `getting-started.md` | User onboarding guide | Workflow or setup changes |
| `glossary.md` | Term definitions | New concepts introduced |
| `troubleshooting-faq.md` | Common issues | New error patterns discovered |
| `tracing-conventions.md` | Agent output formatting | Tracing format changes |

### References (`skills/powerbi-analyst/references/`)
| File | Purpose | Update When |
|------|---------|-------------|
| `ux-review-guidelines.md` | UX evaluation criteria | UX review process changes |
| `powerbi-design-standards.md` | Design constitution & critique rubric | Design standards change |
| `translation-guidelines.md` | Technical to business language | ANALYZE workflow changes |
| `query_folding_guide.md` | M code query folding rules | DATA_PREP workflow changes |
| `workflow-decision-tree.md` | Routing logic | New workflows added |
| `command-parameters.md` | Parameter documentation | Command signatures change |

---

## Quick Validation Checklist

Before committing, verify:

- [ ] Trigger patterns in `SKILL.md` match routing in `powerbi-orchestrator.md`
- [ ] New Pro files are listed in `CONTRIBUTING.md` Pro features table
- [ ] New Pro files are added to `.gitignore` on `main` branch
- [ ] Bootstrap scripts updated if new tools/templates added
- [ ] "See Also" sections reference related documentation
- [ ] Examples in "Example Prompts" table are current
- [ ] New agents added to `plugin.json` agents list
