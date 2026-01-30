# HARVEST_TEMPLATES Workflow (Pro Feature)

Extract reusable visual templates from existing dashboards.

---

## Commands

| Command | Purpose |
|---------|---------|
| `/harvest-templates` | Extract templates from your report |
| `/review-templates` | Compare against existing library |
| `/promote-templates` | Submit PR to public repository |

---

## Public Template Repository

https://github.com/cn-dataworks/pbir-visuals

---

## Capability Tiers (Runtime Detection)

| Command | Requirements | If Missing |
|---------|--------------|------------|
| `/harvest-templates` | PBIR .Report folder | Guide to convert PBIX → PBIP |
| `/review-templates` | Harvested templates | Prompt to harvest first |
| `/promote-templates` | GitHub CLI (`gh`) + authenticated | Manual PR instructions |

Each command checks requirements at runtime and provides helpful error messages with next steps.

---

## Process

### 1. Harvest (`/harvest-templates`)

*Always available with PBIR project*

1. Preflight: Verify .Report folder exists
2. Scan .Report folder for all visuals
3. Classify visuals by type and binding pattern
4. Deduplicate (keep unique structures only)
5. Sanitize (replace specifics with `{{PLACEHOLDER}}` syntax)
6. Save to local staging: `.templates/harvested/`

### 2. Review (`/review-templates`)

*Requires harvested templates*

1. Preflight: Verify harvested templates exist
2. Fetch existing templates from public repository
3. Compare harvested against public library
4. Flag as: NEW, DUPLICATE, VARIANT, IMPROVED
5. Mark templates for promotion

### 3. Promote (`/promote-templates`)

*Requires GitHub CLI*

1. Preflight: Check `gh --version` and `gh auth status`
2. If gh not installed → show install instructions + manual PR alternative
3. If not authenticated → prompt `gh auth login`
4. Fork public repo (if not already forked)
5. Create feature branch, copy templates, create PR

---

## Naming Convention

```
[visual-type]-[binding-pattern].json

Examples:
- bar-chart-category-y.json
- line-chart-multi-measure.json
- card-single-measure.json
- slicer-dropdown.json
```

---

## Storage

| Location | Purpose |
|----------|---------|
| `[project]/.templates/harvested/` | Local staging |
| `github.com/cn-dataworks/pbir-visuals/visual-templates/` | Public library (via PR) |

---

## Output

- Template files (JSON with `{{PLACEHOLDER}}` syntax)
- Harvest manifest
- PR URL (on promotion)
