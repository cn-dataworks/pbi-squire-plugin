# Power BI Analyst Skill - Future Enhancements

This document tracks planned and proposed enhancements for the Power BI Analyst skill.

## Status Legend
- **Proposed** - Under consideration
- **Planned** - Approved for implementation
- **In Progress** - Currently being developed
- **Completed** - Implemented and released

---

## Enhancements

### High Priority

| ID | Enhancement | Description | Status | Notes |
|----|-------------|-------------|--------|-------|
| ENH-001 | GitHub CI/CD for PBIP | Git management and CI/CD pipeline for Power BI projects | Proposed | See detailed proposal below |
| ENH-002 | ANONYMIZE for Live Analysis | MCP Compliance Protocol + `/anonymize` workflow to enable safe live debugging | In Progress | SPEC.md 7.0.17 + workflow |

### Medium Priority

| ID | Enhancement | Description | Status | Notes |
|----|-------------|-------------|--------|-------|
| | | | | |

### Low Priority / Nice to Have

| ID | Enhancement | Description | Status | Notes |
|----|-------------|-------------|--------|-------|
| | | | | |

---

## Completed Enhancements

| ID | Enhancement | Completion Date | Notes |
|----|-------------|-----------------|-------|
| | | | |

---

## Enhancement Proposals

### Template

```
### ENH-XXX: [Enhancement Title]

**Priority:** High/Medium/Low
**Status:** Proposed
**Proposed Date:** YYYY-MM-DD

#### Problem Statement
[Describe the current limitation or pain point]

#### Proposed Solution
[Describe the enhancement]

#### Benefits
- [Benefit 1]
- [Benefit 2]

#### Implementation Notes
[Any technical considerations]

#### Dependencies
- [Dependency 1]
```

---

### ENH-001: GitHub Management & CI/CD Pipeline for PBIP

**Priority:** High
**Status:** Proposed
**Proposed Date:** 2025-12-23

#### Problem Statement
Power BI projects (.pbip folders) currently lack standardized version control and automated deployment workflows. Teams manually manage changes, leading to:
- No audit trail of who changed what and when
- Difficult collaboration between multiple developers
- Manual deployment processes prone to human error
- No automated validation before deployment
- Inconsistent environments (Dev/Test/Prod)

#### Proposed Solution
Implement GitHub-based source control and CI/CD pipeline integration for PBIP folders:

**1. Git Repository Management**
- Initialize/connect PBIP folders to Git repositories
- Standard `.gitignore` templates for Power BI projects
- Branch protection rules and policies
- Automated commit message formatting

**2. Branch Strategy**
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - Feature branches for new development
- `hotfix/*` - Emergency production fixes
- `release/*` - Release preparation branches

**3. CI Pipeline (Continuous Integration)**
- Automated TMDL syntax validation on PR
- DAX formula validation
- Schema change detection and reporting
- Automated code review checks
- Conflict detection for concurrent edits

**4. CD Pipeline (Continuous Deployment)**
- Environment-specific deployment (Dev → Test → Prod)
- pbi-tools integration for deployment
- Automated workspace deployment via Power BI REST API
- Rollback capabilities
- Deployment approval gates

**5. GitHub Actions Workflows**
- `validate-pr.yml` - Run on pull requests
- `deploy-dev.yml` - Auto-deploy to dev on merge to develop
- `deploy-prod.yml` - Deploy to production with approval
- `rollback.yml` - Emergency rollback workflow

#### Benefits
- Complete audit trail of all changes
- Collaborative development with proper branching
- Automated validation catches errors before deployment
- Consistent, repeatable deployments across environments
- Reduced deployment time and human error
- Easy rollback if issues are discovered
- Enables code review process for Power BI changes

#### Implementation Notes
- Leverage existing pbi-tools for deployment operations
- Use Power BI REST API for workspace management
- GitHub Actions for workflow orchestration
- Consider Azure DevOps as alternative pipeline option
- Service principal authentication for automated deployments
- Secrets management for credentials (GitHub Secrets / Azure Key Vault)

#### Key Commands to Add
- `/pbi-git-init` - Initialize Git repo for PBIP folder
- `/pbi-git-sync` - Sync changes and create commits
- `/pbi-create-pr` - Create pull request with validation
- `/pbi-deploy` - Trigger deployment to specified environment
- `/pbi-rollback` - Rollback to previous deployment

#### Dependencies
- pbi-tools CLI
- GitHub account / GitHub Actions
- Power BI Service Principal for API access
- Workspace access permissions

---

---

### ENH-002: ANONYMIZE for Live Analysis

**Priority:** High
**Status:** In Progress
**Proposed Date:** 2025-12-23

> **Reference:** Technical protocol implemented in **SPEC.md Section 7.0.17**

#### Problem Statement

Users who want to run **Live Mode** analysis (query execution, debugging, measure testing) with sensitive data need:
1. A protocol that enforces safe connection modes
2. Automated PII detection and anonymization setup
3. A toggle to switch between masked (dev) and real (prod) data
4. TMDL annotations to track what's masked

#### Solution Overview

| Component | Description | Status |
|-----------|-------------|--------|
| **MCP Compliance Protocol** | Technical spec for connection modes, PII scanning, `fxAnonymize` | ✅ SPEC.md 7.0.17 |
| **`/anonymize` Workflow** | User-facing automation to set up and unlock Live Mode | ⏳ Proposed |

---

#### Part 1: MCP Compliance Protocol (SPEC.md 7.0.17) ✅

| Section | Content |
|---------|---------|
| **7.0.17.1** | Connection Integrity Check (Schema Mode vs Live Mode) |
| **7.0.17.2** | PII Sensitivity Scanning (Identity, Contact, Financial patterns) |
| **7.0.17.3** | Anonymization Logic (`fxAnonymize` SHA256 hash function) |
| **7.0.17.4** | TMDL Annotation for Anonymization Status |
| **7.0.17.5** | PBIX File Warning (convert to PBIP guidance) |
| **7.0.17.6** | Connection Mode Decision Tree |

##### Two Connection Modes

| Mode | Use Case | Data Exposure |
|------|----------|---------------|
| **Schema Mode** | Create measures, organize tables, format DAX | None (metadata only) |
| **Live/Debug Mode** | Query execution, debugging, validation | Yes (requires anonymization first) |

##### `fxAnonymize` Function

```m
// Deterministic SHA256 Hash with Toggle
(InputString as any) as text =>
let
    RunAnonymization = ComplianceMode,
    SourceText = Text.From(InputString),
    HashText = Text.Start(Binary.ToText(Crypto.CreateHash(Algorithm.SHA256, Text.ToBinary(SourceText)), BinaryEncoding.Hex), 10),
    Result = if RunAnonymization = true then HashText else SourceText
in
    if InputString = null then null else Result
```

##### `ComplianceMode` Toggle

- `TRUE` = Anonymization active (safe for sharing, demos, debugging)
- `FALSE` = Real data (production only)

---

#### Part 2: `/anonymize` Workflow ⏳

**Intent Classification (add to SPEC.md 7.0.5):**

| Intent | Workflow | Primary Keywords | Secondary Signals |
|--------|----------|------------------|-------------------|
| **ANONYMIZE** | Set up anonymization | anonymize, mask, prepare for live, enable live mode, hide PII | User wants to debug/test but has sensitive data |

**Workflow Steps:**

```
USER: "I want to run live analysis but this has customer data"
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: CONNECT (Schema Mode)                                  │
│  • Verify PBIP folder (warn if PBIX per 7.0.17.5)               │
│  • Connect via folder path only (no Desktop)                    │
│  • Confirm cache.abf deleted                                    │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: SCAN FOR PII (per 7.0.17.2)                            │
│  • Analyze all Table[Column] names                              │
│  • Flag: Identity, Contact, Financial patterns                  │
│  • Present "Recommended Columns for Masking" table              │
│  • User confirms/adjusts selection                              │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: CREATE INFRASTRUCTURE                                  │
│  • Create `ComplianceMode` parameter (default: TRUE)            │
│  • Create `fxAnonymize` function (per 7.0.17.3)                 │
│  • Add TMDL annotations to affected tables (per 7.0.17.4)       │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: INJECT ANONYMIZATION                                   │
│  • Modify partition M code for each selected column             │
│  • Wrap column: fxAnonymize([ColumnName])                       │
│  • Preserve query folding order                                 │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: PROMPT REFRESH                                         │
│  "Anonymization configured. To activate:                        │
│   1. Open project in Power BI Desktop                           │
│   2. Verify ComplianceMode = TRUE                               │
│   3. Refresh all tables                                         │
│   4. Return here and confirm refresh complete"                  │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 6: UNLOCK LIVE MODE                                       │
│  • User confirms refresh complete                               │
│  • Gate passed (per 7.0.17.1 Intent 2 protocol)                 │
│  • "✅ Live Mode unlocked. You can now run queries, debug       │
│     measures, and test calculations with anonymized data."      │
└─────────────────────────────────────────────────────────────────┘
```

##### Commands

| Command | Purpose |
|---------|---------|
| `/anonymize` | Full workflow: scan → configure → inject → prompt refresh |
| `/anonymize-scan` | PII scan only - preview what would be masked |
| `/anonymize-status` | Show current anonymization configuration |
| `/anonymize-toggle` | Switch `ComplianceMode` TRUE/FALSE |
| `/anonymize-remove` | Remove anonymization from specified table(s) |

##### Example Session

```
User: I need to debug the YoY Growth measure but this project has real customer data

Claude: I can help you set up anonymization so we can use Live Mode safely.
        First, let me scan your schema for sensitive columns...

        🔍 PII SCAN RESULTS

        | Table    | Column       | Category  | Confidence |
        |----------|--------------|-----------|------------|
        | Customer | CustomerName | Identity  | High       |
        | Customer | Email        | Identity  | High       |
        | Customer | Phone        | Contact   | High       |
        | Employee | SSN          | Identity  | High       |

        Would you like me to configure anonymization for these columns? [Y/N]

User: Yes

Claude: Creating anonymization infrastructure...
        ✓ Created ComplianceMode parameter (TRUE)
        ✓ Created fxAnonymize function
        ✓ Modified Customer partition
        ✓ Modified Employee partition
        ✓ Added TMDL annotations

        To activate: Open in Desktop, refresh, then tell me "refresh complete"

User: Refresh complete

Claude: ✅ LIVE MODE UNLOCKED
        What would you like to investigate with the YoY Growth measure?
```

---

#### Benefits

- **Deterministic:** Same input → same hash (enables joins, grouping)
- **Irreversible:** SHA256 cannot be reversed
- **Toggle-Controlled:** Switch modes via `ComplianceMode` parameter
- **Traceable:** TMDL annotation documents what's masked
- **One command** to prepare for live analysis
- **Safe by default** (`ComplianceMode = TRUE`)

---

#### Implementation Status

| Task | Status |
|------|--------|
| MCP Compliance Protocol (SPEC.md 7.0.17) | ✅ Complete |
| Add ANONYMIZE to Intent Classification (SPEC 7.0.5) | ⏳ Pending |
| Add Workflow 8: ANONYMIZE to SPEC 7.0.6 | ⏳ Pending |
| Update M-Code Specialist with `fxAnonymize` pattern | ⏳ Pending |
| Add `/anonymize` commands to SKILL.md | ⏳ Pending |
| Create agent or orchestrator logic | ⏳ Pending |
| Test end-to-end workflow | ⏳ Pending |

---

## Notes

- Enhancement IDs follow the format `ENH-XXX` where XXX is a sequential number
- Add new proposals to the Enhancement Proposals section using the template
- Move to appropriate priority table once approved
