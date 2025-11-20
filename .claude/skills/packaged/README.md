# Packaged Skills

This folder contains distributable `.skill` files - packaged versions of the skills in the parent directory.

## What Are .skill Files?

`.skill` files are ZIP archives containing all the files needed for a skill:
- SKILL.md (skill definition and instructions)
- Scripts (Python utilities)
- References (documentation)
- Assets (templates, examples)

## Purpose

These packaged files are for:
- **Distribution**: Share skills with colleagues or the community
- **Installation**: Import skills into other Claude Code projects
- **Releases**: Maintain stable versions separate from development

## Source vs Package

- **Source folders** (`../agentic-workflow-creator/`, etc.): Active development - edit these
- **Packaged files** (this folder): Built/compiled releases - distribute these

## Creating a Package

To create or update a `.skill` file:

1. Make changes in the source folder
2. Run the packaging script:
   ```bash
   python C:\Users\AndrewNorthrup\.claude\plugins\marketplaces\anthropic-agent-skills\skill-creator\scripts\package_skill.py <path-to-skill-folder> <output-directory>
   ```
3. Or manually create a ZIP and rename to `.skill`

## Contents

- `agentic-workflow-creator.skill` - Create multi-agent workflows
- `powerbi-dashboard-analyzer.skill` - Analyze Power BI dashboards with business-friendly summaries

## Note

If you're only developing locally, you don't need these packaged files - Claude Code can use the source folders directly. The `.skill` files are optional for distribution purposes only.
