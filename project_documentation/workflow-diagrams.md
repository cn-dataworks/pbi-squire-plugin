# PBI Squire Plugin - Workflow Mermaid Diagram

**Target location:** `project_documentation/workflow-diagrams.md`

---

## Mermaid Flowchart

Copy this into FigJam (it supports Mermaid) or any Mermaid renderer:

```mermaid
flowchart TD
    subgraph PreChecks["Pre-Workflow Checks"]
        A[User Request] --> B{PBIX file?}
        B -->|Yes| B1[STOP: Convert to PBIP]
        B -->|No| C{Config exists?}
        C -->|No| C2{Developer Edition?}
        C2 -->|Yes| C1[Exit: Run bootstrap<br/>Python tools required]
        C2 -->|No| C3[Interactive Setup<br/>Create configs via Claude]
        C3 --> D
        C -->|Yes| D{MCP Available?}
        D -->|No + Write| D1[Warn: Limited validation]
        D -->|Yes or Read-only| E[Load Config]
        D1 --> E
        E --> F{Multiple projects?}
        F -->|Yes| F1[Ask user to select]
        F -->|No| G{Sensitive data mode?}
        F1 --> G
        G -->|Yes, no config| G1[Warn: Setup anonymization]
        G -->|No or configured| H[Route Request]
        G1 --> H
    end

    subgraph Routing["Workflow Routing"]
        H --> I{Classify Intent}

        I -->|fix, broken, debug, error| W1[EVALUATE]
        I -->|create measure, add column| W2[CREATE_ARTIFACT]
        I -->|visual, card, chart, page| W3{Developer Edition?}
        W3 -->|Yes| W3a[CREATE_PAGE]
        W3 -->|No| W2
        I -->|M code, transform, ETL| W4[DATA_PREP]
        I -->|explain, document, understand| W5[SUMMARIZE]
        I -->|apply, implement, deploy| W6[IMPLEMENT]
        I -->|compare, merge, diff| W7[MERGE]
        I -->|version, update| W8[VERSION_CHECK]
        I -->|anonymize, mask data| W9[SETUP_ANONYMIZATION]
        I -->|unclear| W10[Ask Clarifying Questions]
        W10 --> I
    end

    subgraph Execution["Phase Execution (Write Workflows)"]
        W1 & W2 & W3a & W4 --> P0

        P0[Phase 0: Setup<br/>Create scratchpad + findings.md] --> P1

        P1[Phase 1: Investigation<br/>PARALLEL subagents] --> QG1{Quality Gate 1}
        QG1 -->|Pass| P2
        QG1 -->|Fail| P1

        P2[Phase 2: Planning<br/>SEQUENTIAL agents] --> QG2{Quality Gate 2}
        QG2 -->|Pass| P3
        QG2 -->|Fail| P2

        P3[Phase 3: Validation<br/>PARALLEL validators] --> QG3{Quality Gate 3<br/>100% pass required}
        QG3 -->|Pass| P4[Phase 4: Present Findings]
        QG3 -->|Fail| P2

        P4 --> NEXT[Suggest: /implement]
    end

    subgraph ReadOnly["Read-Only Workflows"]
        W5 --> RO1[Read project files<br/>Generate documentation]
        W8 --> RO2[Check version.txt<br/>Report edition]
        W9 --> RO3[Run anonymization-setup agent]
    end

    subgraph Implement["IMPLEMENT Workflow"]
        W6 --> IMP1{findings.md exists?}
        IMP1 -->|No| IMP2[Error: Run evaluation first]
        IMP1 -->|Yes| IMP3[Apply changes to project]
        IMP3 --> IMP4{Developer Edition?}
        IMP4 -->|Yes| IMP5[Run Playwright tests]
        IMP4 -->|No| IMP6[Manual verification]
    end

    subgraph Merge["MERGE Workflow"]
        W7 --> M1[Phase 1: Compare projects]
        M1 --> M2[Phase 2: Analyze impact]
        M2 --> M3{User approves?}
        M3 -->|Yes| M4[Phase 3: Execute merge]
        M3 -->|No| M5[Abort]
    end
```

## Subagent Pool Diagram

```mermaid
flowchart LR
    subgraph Investigation["Phase 1: Investigation Agents"]
        direction TB
        INV1[powerbi-code-locator<br/>Find DAX/M/TMDL]
        INV2[powerbi-visual-locator<br/>Find PBIR visuals]
        INV3[powerbi-data-context-agent<br/>Query live data via MCP]
        INV4[powerbi-pattern-discovery<br/>Find similar patterns]
    end

    subgraph Planning["Phase 2: Planning Agents"]
        direction TB
        PLN1[powerbi-dashboard-update-planner<br/>Design changes]
        PLN2[powerbi-artifact-decomposer<br/>Break down requests]
        PLN3[powerbi-dax-specialist<br/>Generate DAX code]
        PLN4[powerbi-mcode-specialist<br/>Generate M code]
    end

    subgraph Validation["Phase 3: Validation Agents"]
        direction TB
        VAL1[powerbi-dax-review-agent<br/>DAX syntax check]
        VAL2[powerbi-pbir-validator<br/>PBIR JSON check]
        VAL3[TMDL validation<br/>MCP or Claude-native]
    end

    subgraph Execution["Phase 4: Execution Agents"]
        direction TB
        EXE1[powerbi-code-implementer-apply<br/>Apply TMDL]
        EXE2[powerbi-visual-implementer-apply<br/>Apply PBIR]
    end

    subgraph Pro["Pro-Only Agents"]
        direction TB
        PRO1[powerbi-playwright-tester<br/>Browser automation]
        PRO2[powerbi-ux-reviewer<br/>Design critique]
        PRO3[powerbi-qa-inspector<br/>DOM inspection]
    end
```

## Trigger Keywords Reference

| Workflow | Trigger Keywords |
|----------|------------------|
| EVALUATE | fix, broken, wrong, debug, issue, error, not working |
| CREATE_ARTIFACT | create measure, add measure, new column, new table |
| CREATE_PAGE (Developer) | visual, card, chart, page, dashboard page, build visual |
| DATA_PREP | M code, Power Query, transform, ETL, filter table, merge tables |
| SUMMARIZE | explain, understand, what does, document, tell me about |
| IMPLEMENT | apply, implement, deploy, execute, make the changes |
| MERGE | compare, merge, diff, sync projects, combine |
| VERSION_CHECK | version, update, edition |
| SETUP_ANONYMIZATION | anonymize, mask sensitive, data masking, hide PII |

## Usage

1. **In FigJam**: Paste the Mermaid code into a code block - FigJam renders Mermaid natively
2. **In VS Code**: Use Mermaid Preview extension
3. **Online**: Use [mermaid.live](https://mermaid.live) to render and export as SVG/PNG
4. **In GitHub**: Mermaid renders automatically in markdown files

## Next Steps

If you want me to:
- Export this as an SVG file
- Add more detail to specific sections
- Create separate diagrams for individual workflows

Just let me know!
