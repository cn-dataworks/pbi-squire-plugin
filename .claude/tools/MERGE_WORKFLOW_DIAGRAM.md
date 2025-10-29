# Power BI Project Merge Workflow - Visual Diagrams

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                  /merge-powerbi-projects                        │
│                   (Main Orchestrator)                           │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ Coordinates
             │
    ┌────────┴────────┬──────────────────┬───────────────────┐
    │                 │                  │                   │
    v                 v                  v                   v
┌─────────┐    ┌──────────┐    ┌──────────────┐    ┌───────────┐
│ Agent 1 │    │ Agent 2  │    │    HITL      │    │ Agent 3   │
│Technical│───>│Business  │───>│  (Human      │───>│Merge      │
│Auditor  │    │Analyst   │    │  Decision)   │    │Surgeon    │
└─────────┘    └──────────┘    └──────────────┘    └───────────┘
```

## Detailed Workflow Sequence

```
START: User runs command
│
├─> /merge-powerbi-projects --main "A" --comparison "B"
│
v
┌──────────────────────────────────────────────────────────────┐
│ PHASE 1: INPUT VALIDATION                                    │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ • Verify paths exist                                     │ │
│ │ • Check for .SemanticModel/ folder                       │ │
│ │ • Check for .Report/ folder                              │ │
│ │ • Detect TMDL vs BIM format                              │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
│
│ IF VALID
│
v
┌──────────────────────────────────────────────────────────────┐
│ PHASE 2: TECHNICAL COMPARISON                                │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ AGENT: powerbi-compare-project-code                      │ │
│ │                                                          │ │
│ │ Scans:                                                   │ │
│ │  ├─> File structure (additions/deletions)                │ │
│ │  ├─> Semantic Model                                      │ │
│ │  │    ├─> Tables (.tmdl files or model.bim)             │ │
│ │  │    ├─> Measures (DAX expressions)                    │ │
│ │  │    ├─> Columns (data types, calc columns)           │ │
│ │  │    └─> Relationships (cardinality, filters)         │ │
│ │  └─> Report                                              │ │
│ │       ├─> Pages (report.json)                           │ │
│ │       ├─> Visuals (types, data fields)                  │ │
│ │       └─> Filters (page & visual level)                 │ │
│ │                                                          │ │
│ │ Outputs: DiffReport.json                                 │ │
│ │ ┌──────────────────────────────────────────────────────┐ │ │
│ │ │ {                                                    │ │ │
│ │ │   "diffs": [                                         │ │ │
│ │ │     {                                                │ │ │
│ │ │       "diff_id": "diff_001",                         │ │ │
│ │ │       "component_type": "Measure",                   │ │ │
│ │ │       "component_name": "Total Revenue",             │ │ │
│ │ │       "status": "Modified",                          │ │ │
│ │ │       "main_version_code": "...",                    │ │ │
│ │ │       "comparison_version_code": "..."               │ │ │
│ │ │     }                                                │ │ │
│ │ │   ],                                                 │ │ │
│ │ │   "summary": {...}                                   │ │ │
│ │ │ }                                                    │ │ │
│ │ └──────────────────────────────────────────────────────┘ │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
│
v
┌──────────────────────────────────────────────────────────────┐
│ PHASE 3: BUSINESS IMPACT ANALYSIS                            │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ AGENT: powerbi-code-understander                         │ │
│ │                                                          │ │
│ │ For each diff:                                           │ │
│ │  ├─> Analyze calculation logic (DAX)                     │ │
│ │  ├─> Assess performance impact                           │ │
│ │  ├─> Identify business consequences                      │ │
│ │  ├─> Flag breaking changes                               │ │
│ │  └─> Provide decision guidance                           │ │
│ │                                                          │ │
│ │ Enriches: DiffReport with "business_impact" field        │ │
│ │ ┌──────────────────────────────────────────────────────┐ │ │
│ │ │ {                                                    │ │ │
│ │ │   "diff_id": "diff_001",                             │ │ │
│ │ │   ...                                                │ │ │
│ │ │   "business_impact": "This changes how Total         │ │ │
│ │ │   Revenue is calculated. MAIN uses pre-calculated    │ │ │
│ │ │   column, COMPARISON calculates dynamically..."      │ │ │
│ │ │ }                                                    │ │ │
│ │ └──────────────────────────────────────────────────────┘ │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
│
v
┌──────────────────────────────────────────────────────────────┐
│ PHASE 4: HUMAN DECISION (HITL)                               │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Orchestrator presents combined report to user:          │ │
│ │                                                          │ │
│ │ ╔════════════════════════════════════════════════════╗  │ │
│ │ ║ Diff diff_001: Measure - "Total Revenue"           ║  │ │
│ │ ║                                                    ║  │ │
│ │ ║ Technical Details:                                 ║  │ │
│ │ ║   Main: SUM(Sales[Amount])                         ║  │ │
│ │ ║   Comparison: SUMX(Sales, Qty * Price)             ║  │ │
│ │ ║                                                    ║  │ │
│ │ ║ Business Impact:                                   ║  │ │
│ │ ║   [Explanation of what changed and why it matters] ║  │ │
│ │ ║                                                    ║  │ │
│ │ ║ Your Choice: diff_001: [Main or Comparison]        ║  │ │
│ │ ╚════════════════════════════════════════════════════╝  │ │
│ │                                                          │ │
│ │ User responds:                                           │ │
│ │   diff_001: Comparison                                   │ │
│ │   diff_002: Main                                         │ │
│ │   diff_003: Comparison                                   │ │
│ │   ...                                                    │ │
│ │                                                          │ │
│ │ Orchestrator parses → MergeManifest.json                 │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
│
v
┌──────────────────────────────────────────────────────────────┐
│ PHASE 5: MERGE EXECUTION                                     │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ AGENT: powerbi-code-merger                               │ │
│ │                                                          │ │
│ │ Step 1: Create output folder                             │ │
│ │   └─> merged_20250128_143022.pbip/                       │ │
│ │                                                          │ │
│ │ Step 2: Copy main project                                │ │
│ │   └─> cp -r main.pbip/* output/                          │ │
│ │                                                          │ │
│ │ Step 3: Apply "Comparison" decisions                     │ │
│ │   For each diff where choice = "Comparison":             │ │
│ │     ├─> If Modified:                                     │ │
│ │     │    └─> Replace component in output                 │ │
│ │     ├─> If Added:                                        │ │
│ │     │    └─> Copy component to output                    │ │
│ │     └─> If Deleted:                                      │ │
│ │          └─> Remove component from output                │ │
│ │                                                          │ │
│ │ Step 4: Generate log                                     │ │
│ │   ├─> Timestamp each operation                           │ │
│ │   ├─> Record successes                                   │ │
│ │   ├─> Collect errors                                     │ │
│ │   └─> Calculate statistics                               │ │
│ │                                                          │ │
│ │ Outputs: MergeResult.json + merged project               │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
│
v
┌──────────────────────────────────────────────────────────────┐
│ PHASE 5.5: TMDL FORMAT VALIDATION (Quality Gate)            │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ AGENT: powerbi-tmdl-syntax-validator                     │ │
│ │                                                          │ │
│ │ For each modified TMDL file:                             │ │
│ │   ├─> Check indentation consistency                      │ │
│ │   ├─> Validate property placement                        │ │
│ │   ├─> Verify tab usage                                   │ │
│ │   └─> Check measure/column structure                     │ │
│ │                                                          │ │
│ │ Output: Validation report (PASS/WARNINGS/FAIL)           │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
│
v
┌──────────────────────────────────────────────────────────────┐
│ PHASE 5.6: DAX SYNTAX VALIDATION (Quality Gate)             │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ AGENT: powerbi-dax-review-agent                          │ │
│ │                                                          │ │
│ │ For each modified DAX object:                            │ │
│ │   ├─> Validate DAX syntax                                │ │
│ │   ├─> Check function signatures                          │ │
│ │   ├─> Verify references                                  │ │
│ │   ├─> Assess runtime risks                               │ │
│ │   └─> Check context usage                                │ │
│ │                                                          │ │
│ │ Output: Validation report (PASS/WARNINGS/FAIL)           │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
│
v
┌──────────────────────────────────────────────────────────────┐
│ PHASE 6: FINAL REPORT                                        │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Orchestrator presents:                                   │ │
│ │                                                          │ │
│ │ ╔════════════════════════════════════════════════════╗  │ │
│ │ ║ Power BI Project Merge Complete                   ║  │ │
│ │ ║                                                    ║  │ │
│ │ ║ Output: merged_20250128_143022.pbip                ║  │ │
│ │ ║ Decisions Applied: 25                              ║  │ │
│ │ ║ Changes Applied: 12 (7 Main, 5 Comparison)         ║  │ │
│ │ ║ Errors: 0                                          ║  │ │
│ │ ║                                                    ║  │ │
│ │ ║ Section 1: Technical Diffs [summary table]         ║  │ │
│ │ ║ Section 2: Business Impact [highlights]            ║  │ │
│ │ ║ Section 3: Merge Log [detailed operations]         ║  │ │
│ │ ╚════════════════════════════════════════════════════╝  │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
│
v
END: User has merged project ready for testing/deployment
```

## Data Flow Diagram

```
┌────────────┐                    ┌────────────┐
│ Main       │                    │ Comparison │
│ Project    │                    │ Project    │
│ (path A)   │                    │ (path B)   │
└──────┬─────┘                    └──────┬─────┘
       │                                 │
       └────────────┬────────────────────┘
                    │
                    v
          ┌─────────────────┐
          │  Agent 1 Scan   │
          │  (Comparer)     │
          └────────┬────────┘
                   │
                   v
          ┌─────────────────┐
          │ DiffReport.json │
          │                 │
          │ [diff_001]      │
          │ [diff_002]      │
          │ [diff_003]      │
          │ ...             │
          └────────┬────────┘
                   │
                   v
          ┌─────────────────┐
          │  Agent 2 LLM    │
          │  (Understander) │
          └────────┬────────┘
                   │
                   v
          ┌──────────────────────┐
          │ BusinessImpact.json  │
          │                      │
          │ [diff_001 + impact]  │
          │ [diff_002 + impact]  │
          │ ...                  │
          └────────┬─────────────┘
                   │
                   v
          ┌─────────────────┐
          │  User Reviews   │
          │  & Decides      │
          └────────┬────────┘
                   │
                   v
          ┌─────────────────┐
          │MergeManifest.json│
          │                 │
          │ decisions: [    │
          │   {diff_001: C} │
          │   {diff_002: M} │
          │ ]               │
          └────────┬────────┘
                   │
                   v
          ┌─────────────────┐
          │  Agent 3 Exec   │
          │  (Merger)       │
          └────────┬────────┘
                   │
                   v
          ┌──────────────────────┐
          │ TMDL Format Validator│
          │ (Quality Gate)       │
          └────────┬─────────────┘
                   │
                   v
          ┌──────────────────────┐
          │ DAX Syntax Validator │
          │ (Quality Gate)       │
          └────────┬─────────────┘
                   │
                   v
          ┌─────────────────┐
          │ Merged Project  │
          │ + MergeLog      │
          │ + Validation    │
          └─────────────────┘
```

## Component Interaction Model

```
┌─────────────────────────────────────────────────────────┐
│              Main Orchestrator                          │
│           (merge-powerbi-projects.md)                   │
│                                                         │
│  State Management:                                      │
│  ┌───────────────────────────────────────────────────┐ │
│  │ • main_path: string                               │ │
│  │ • comparison_path: string                         │ │
│  │ • diff_report: DiffReport                         │ │
│  │ • business_impact_report: BusinessImpactReport    │ │
│  │ • merge_manifest: MergeManifest                   │ │
│  │ • merge_result: MergeResult                       │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  Control Flow:                                          │
│  ┌───────────────────────────────────────────────────┐ │
│  │ 1. validate_input()                               │ │
│  │ 2. invoke_agent_1() → diff_report                 │ │
│  │ 3. invoke_agent_2(diff_report) → business_report  │ │
│  │ 4. present_to_user(business_report)               │ │
│  │ 5. wait_for_user_response()                       │ │
│  │ 6. parse_decisions() → merge_manifest             │ │
│  │ 7. invoke_agent_3(merge_manifest) → merge_result  │ │
│  │ 8. generate_final_report()                        │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
        │                    │                    │
        │ Task               │ Task               │ Task
        │ Invocation         │ Invocation         │ Invocation
        v                    v                    v
┌───────────────┐   ┌──────────────┐   ┌──────────────┐
│   Agent 1     │   │   Agent 2    │   │   Agent 3    │
│               │   │              │   │              │
│ Uses:         │   │ Uses:        │   │ Uses:        │
│ • Glob        │   │ • LLM        │   │ • Read       │
│ • Read        │   │ • Read       │   │ • Write      │
│ • Python util │   │ • JSON parse │   │ • Edit       │
│               │   │              │   │ • Bash       │
│ Returns:      │   │ Returns:     │   │ Returns:     │
│ DiffReport    │   │ BusinessRpt  │   │ MergeResult  │
└───────────────┘   └──────────────┘   └──────────────┘
```

## File System Operations

```
BEFORE MERGE:
─────────────

main.pbip/
├── Project.SemanticModel/
│   └── definition/
│       └── tables/
│           └── Sales.tmdl    [measure: SUM(Amount)]
└── Project.Report/
    └── report.json

comparison.pbip/
├── Project.SemanticModel/
│   └── definition/
│       └── tables/
│           └── Sales.tmdl    [measure: SUMX(Qty*Price)]
└── Project.Report/
    └── report.json


AFTER MERGE (if user chose "Comparison" for that measure):
────────────────────────────────────────────────────────────

merged_20250128_143022.pbip/
├── Project.SemanticModel/
│   └── definition/
│       └── tables/
│           └── Sales.tmdl    [measure: SUMX(Qty*Price)]  ← UPDATED
└── Project.Report/
    └── report.json

[Original main.pbip and comparison.pbip remain unchanged]
```

## Error Handling Flow

```
┌─────────────┐
│ Operation   │
└──────┬──────┘
       │
       v
   ┌───────┐
   │Try    │
   └───┬───┘
       │
       ├─> Success ──> Log & Continue
       │
       ├─> FileNotFound
       │   └─> Add to errors[], Log, Skip, Continue
       │
       ├─> ParseError
       │   └─> Add to errors[], Log, Skip, Continue
       │
       └─> CriticalError
           └─> Add to errors[], Log, ABORT
```

## Success Path Summary

```
User Command
    ↓
Validation ✓
    ↓
Technical Scan → 25 diffs found
    ↓
Business Analysis → Impact explained
    ↓
User Reviews → Makes 25 decisions
    ↓
Merge Execution → 12 changes applied
    ↓
Validation ✓
    ↓
Final Report + Merged Project
    ↓
User Tests in Power BI Desktop
    ↓
Deployment to Production
```

## Agent Autonomy Levels

```
Agent 1: FULLY AUTONOMOUS
├─ Scans files without user input
├─ Parses TMDL/BIM autonomously
└─ Returns complete report

Agent 2: FULLY AUTONOMOUS
├─ Analyzes each diff independently
├─ Generates business explanations
└─ No user interaction required

HITL: HUMAN REQUIRED
├─ Reviews all information
├─ Makes final decisions
└─ Cannot be skipped

Agent 3: FULLY AUTONOMOUS
├─ Executes decisions faithfully
├─ Handles errors gracefully
└─ Returns complete result
```

This visual representation shows how the three autonomous agents work together under orchestration, with human judgment at the critical decision point.
