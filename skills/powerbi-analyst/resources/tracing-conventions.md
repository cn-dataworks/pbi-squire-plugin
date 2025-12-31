# Tracing Conventions

This document defines output conventions for workflow and agent traceability.

## Purpose

All workflows and agents MUST output trace markers to provide visibility into:
- Which workflow is running
- Which phase/step is active
- Which agent is executing
- When MCP tools are called
- Success/failure status

## Output Format

### Workflow Start

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 WORKFLOW: [workflow-name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Phase Markers

```
📋 PHASE [N]: [Phase Name]
   └─ [Description of what's happening]
```

### Agent Invocation

```
   └─ 🤖 [AGENT] [agent-name]
   └─    Starting: [brief description]
```

### MCP Tool Calls

```
   └─ 🔌 [MCP] [tool-name]
   └─    [parameters or context]
   └─    ✅ Success: [result summary]
   └─    ❌ Error: [error message]
```

### Sub-steps

```
   └─ 📂 [action]: [detail]
   └─ 🔍 [action]: [detail]
   └─ ✏️ [action]: [detail]
```

### Workflow Complete

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WORKFLOW COMPLETE: [workflow-name]
   └─ Duration: [if available]
   └─ Output: [file path or summary]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Workflow Failed

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ WORKFLOW FAILED: [workflow-name]
   └─ Phase: [where it failed]
   └─ Error: [error description]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Icons Reference

| Icon | Meaning |
|------|---------|
| 🚀 | Workflow start |
| 📋 | Phase/step |
| 🤖 | Agent invocation |
| 🔌 | MCP tool call |
| 📂 | File operation |
| 🔍 | Search/discovery |
| ✏️ | Edit/write |
| ✅ | Success |
| ❌ | Error/failure |
| ⚠️ | Warning |
| 💡 | Info/hint |

## Example Full Trace

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 WORKFLOW: evaluate-pbi-project-file
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 PHASE 1: Project Discovery
   └─ 🔍 Scanning for Power BI project files...
   └─ 📂 Found: C:\Projects\Sales\SalesReport.pbip
   └─ 📂 SemanticModel: .SemanticModel\
   └─ 📂 Report: .Report\

📋 PHASE 2: Connection & Schema
   └─ 🔌 [MCP] connection_operations.connect
   └─    Target: localhost:54321
   └─    ✅ Connected to Power BI Desktop
   └─ 🔌 [MCP] table_operations.list
   └─    ✅ Found 5 tables
   └─ 🔌 [MCP] measure_operations.list
   └─    ✅ Found 23 measures

📋 PHASE 3: Problem Analysis
   └─ 🤖 [AGENT] powerbi-dax-review-agent
   └─    Starting: Validate all DAX expressions
   └─ 🔌 [MCP] dax_query_operations.validate
   └─    Expression: [Total Sales]
   └─    ✅ Valid
   └─ 🔌 [MCP] dax_query_operations.validate
   └─    Expression: [YoY Growth %]
   └─    ❌ Error: Column 'Dates'[Year] not found
   └─ 💡 Found 1 issue requiring attention

📋 PHASE 4: Generate Findings
   └─ ✏️ Creating task directory: .claude/tasks/eval-1234/
   └─ ✏️ Writing: findings.md
   └─ ✅ Findings document complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WORKFLOW COMPLETE: evaluate-pbi-project-file
   └─ Output: .claude/tasks/eval-1234/findings.md
   └─ Issues found: 1
   └─ Next: Review findings and run /implement-deploy-test
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Agent Implementation

Every agent MUST:

1. **Announce on start:**
   ```
   └─ 🤖 [AGENT] [my-agent-name]
   └─    Starting: [what I'm about to do]
   ```

2. **Log MCP calls:**
   ```
   └─ 🔌 [MCP] [tool-name]
   └─    [context]
   └─    [result]
   ```

3. **Report completion:**
   ```
   └─ 🤖 [AGENT] [my-agent-name] complete
   └─    Result: [summary]
   ```

## Workflow Implementation

Every workflow MUST:

1. Output workflow start banner
2. Output phase markers before each major step
3. Output workflow complete/failed banner
4. Include output file paths in completion
