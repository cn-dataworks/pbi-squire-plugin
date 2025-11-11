# Sub-Agent Communication Template

This template defines the structure for persistent markdown files used to coordinate between main agents and sub-agents in agentic workflows.

## Purpose

When workflows use sub-agents (via the Task tool or similar delegation mechanisms), they need a persistent communication channel. This markdown file serves as:

1. **Context Persistence:** Information survives across sub-agent invocations
2. **Bidirectional Communication:** Main agent → sub-agents AND sub-agents → main agent
3. **Sub-agent Collaboration:** Sub-agents can read each other's outputs and coordinate
4. **Decision History:** Track reasoning and decisions made during workflow execution

## File Location

Recommended: `.claude/workflows/<workflow-name>/agent_context.md`

Example: `.claude/workflows/yoy-revenue-measure/agent_context.md`

## Template Structure

```markdown
# Agent Context: [Workflow Name]

**Workflow:** [Name of the workflow being executed]
**Started:** [Timestamp]
**Status:** [In Progress | Completed | Failed]

---

## 1. Request Summary

**Original Request:**
[User's original request verbatim]

**Refined Specifications:**
- **Goals:** [Specific, measurable objectives]
- **Constraints:** [Limitations, requirements, boundaries]
- **Desired Outputs:** [Expected artifacts and formats]

---

## 2. Main Agent Findings

**Last Updated:** [Timestamp]

### Initial Analysis
[Main agent's analysis of the request, context, and requirements]

### Recommendations
[Main agent's recommendations for approach, with pros/cons of options]

### Sub-Agent Delegation Plan
- **Sub-Agent 1:** [Name/Purpose] - [Specific task assigned]
- **Sub-Agent 2:** [Name/Purpose] - [Specific task assigned]
- **Sub-Agent N:** [Name/Purpose] - [Specific task assigned]

---

## 3. Sub-Agent Reports

### Sub-Agent: [Name/ID]

**Task:** [Specific task assigned to this sub-agent]
**Status:** [Pending | In Progress | Completed | Failed]
**Last Updated:** [Timestamp]

#### Findings
[Sub-agent's findings, analysis, and results]

#### Data/Artifacts
[Any data, code snippets, or artifacts produced]

#### Issues/Blockers
[Any problems encountered or questions for main agent]

#### Recommendations
[Sub-agent's recommendations for next steps]

---

### Sub-Agent: [Name/ID]

**Task:** [Specific task assigned to this sub-agent]
**Status:** [Pending | In Progress | Completed | Failed]
**Last Updated:** [Timestamp]

#### Findings
[Sub-agent's findings, analysis, and results]

#### Data/Artifacts
[Any data, code snippets, or artifacts produced]

#### Issues/Blockers
[Any problems encountered or questions for main agent]

#### Recommendations
[Sub-agent's recommendations for next steps]

---

## 4. Integration & Synthesis

**Last Updated:** [Timestamp]

### Combined Findings
[Main agent synthesizes sub-agent findings into coherent understanding]

### Cross-Agent Dependencies
[How sub-agent findings relate to each other and affect overall approach]

### Conflicts/Inconsistencies
[Any contradictions between sub-agent findings that need resolution]

---

## 5. User Feedback Loop

### Questions for User
1. [Question 1 with context and recommendations]
2. [Question 2 with context and recommendations]

### User Responses
**Response to Q1:** [User's answer]
**Response to Q2:** [User's answer]

### Decisions Made
- [Decision 1 and rationale]
- [Decision 2 and rationale]

---

## 6. Implementation Plan

**Status:** [Draft | Approved | In Progress | Completed]

### Approach
[Chosen approach based on analysis and user feedback]

### Steps
1. [Step 1]
2. [Step 2]
3. [Step N]

### Success Criteria
- [Criterion 1]
- [Criterion 2]

---

## 7. Validation Results

### Syntax Validation
**Status:** [Pass | Fail]
**Details:** [Results and any issues found]

### Logic Validation
**Status:** [Pass | Fail]
**Details:** [Results and any issues found]

### Quality Checks
**Status:** [Pass | Fail]
**Details:** [Performance, accuracy, standards compliance results]

### Iteration Log
- **Iteration 1:** [What was fixed and why]
- **Iteration 2:** [What was fixed and why]

---

## 8. Final Summary

**Completion Date:** [Timestamp]

### What Was Done
[Clear description of work completed]

### Before State
[What existed before workflow execution]

### After State
[What exists after workflow execution]

### Impact
[Concrete examples showing the difference]

### Next Steps
[Usage instructions or follow-up actions]
```

## Usage Guidelines

### For Main Agents:
1. **Initialize** the file with sections 1-2 when workflow starts
2. **Update** section 2 with analysis and delegation plan
3. **Monitor** section 3 as sub-agents report findings
4. **Synthesize** findings in section 4
5. **Facilitate** user feedback in section 5
6. **Document** implementation and validation in sections 6-7
7. **Summarize** results in section 8

### For Sub-Agents:
1. **Read** sections 1-2 to understand context and task assignment
2. **Read** section 3 to see what other sub-agents have discovered
3. **Update** your assigned subsection in section 3 with findings
4. **Flag** issues or blockers that need main agent attention
5. **Provide** recommendations for next steps

### Communication Patterns:

**Main → Sub:** Use section 2 (delegation plan) to assign tasks and provide context

**Sub → Main:** Use section 3 (your subsection) to report findings and ask questions

**Sub → Sub:** Read other sub-agent subsections in section 3 to coordinate and avoid duplication

**Main → User:** Use section 5 to ask questions with recommendations

**User → Main:** Responses captured in section 5

## Example Workflow

```markdown
# Agent Context: YoY Revenue Growth Measure

**Workflow:** Create YoY Revenue Growth Measure
**Started:** 2024-10-30 09:00:00
**Status:** In Progress

---

## 1. Request Summary

**Original Request:**
"Create a year-over-year revenue growth measure"

**Refined Specifications:**
- **Goals:**
  - Create DAX measure calculating YoY revenue growth as percentage
  - Handle missing data gracefully (no errors on screen)
- **Constraints:**
  - Must use existing Date and Sales tables
  - Follow project naming convention (YoY_*)
- **Desired Outputs:**
  - DAX measure in TMDL format
  - Documentation in findings.md

---

## 2. Main Agent Findings

**Last Updated:** 2024-10-30 09:05:00

### Initial Analysis
Request requires understanding data model structure and existing measure patterns before implementation.

### Recommendations
Recommend pattern discovery to identify existing YoY measures and time intelligence patterns in project.

### Sub-Agent Delegation Plan
- **Sub-Agent 1 (Data Model Analyzer):** Analyze TMDL files to document Date and Sales table structure
- **Sub-Agent 2 (Pattern Discovery):** Search for existing YoY measures and extract calculation patterns

---

## 3. Sub-Agent Reports

### Sub-Agent: Data Model Analyzer

**Task:** Analyze TMDL files to document Date and Sales table structure
**Status:** Completed
**Last Updated:** 2024-10-30 09:10:00

#### Findings
- Date table: 'Date'[Date] column exists with continuous dates 2020-2024
- Sales table: 'Sales'[Revenue] column contains transaction-level revenue
- Existing relationship: Sales[Date] → Date[Date] (many-to-one)

#### Data/Artifacts
```
Date Table Columns:
- Date (DateTime, Primary Key)
- Year (Integer)
- Quarter (Integer)
- Month (Integer)

Sales Table Columns:
- TransactionID (String, Primary Key)
- Date (DateTime, Foreign Key → Date[Date])
- Revenue (Decimal)
```

#### Issues/Blockers
None

#### Recommendations
Data model structure supports SAMEPERIODLASTYEAR time intelligence function.

---

### Sub-Agent: Pattern Discovery

**Task:** Search for existing YoY measures and extract calculation patterns
**Status:** Completed
**Last Updated:** 2024-10-30 09:15:00

#### Findings
Found 2 existing YoY measures in project:
1. `YoY_Units_Sold` - Uses SAMEPERIODLASTYEAR pattern
2. `YoY_Customer_Count` - Uses SAMEPERIODLASTYEAR pattern

Both use DIVIDE function to handle division by zero.

#### Data/Artifacts
```dax
// Pattern extracted from YoY_Units_Sold
YoY_Units_Sold =
    VAR CurrentValue = [Total_Units]
    VAR PriorValue = CALCULATE([Total_Units], SAMEPERIODLASTYEAR('Date'[Date]))
    RETURN DIVIDE(CurrentValue - PriorValue, PriorValue, 0)
```

#### Issues/Blockers
None

#### Recommendations
Follow established pattern: SAMEPERIODLASTYEAR + DIVIDE for consistency with project conventions.

---

## 4. Integration & Synthesis

**Last Updated:** 2024-10-30 09:20:00

### Combined Findings
- Data model supports SAMEPERIODLASTYEAR (continuous date table with proper relationships)
- Project convention established: VAR pattern with SAMEPERIODLASTYEAR and DIVIDE
- Naming convention confirmed: YoY_* prefix

### Cross-Agent Dependencies
Data model analysis (Sub-Agent 1) confirmed that pattern recommendation (Sub-Agent 2) is viable.

### Conflicts/Inconsistencies
None - findings are aligned and mutually supportive.

---

## 5. User Feedback Loop

### Questions for User
1. The project uses SAMEPERIODLASTYEAR pattern for YoY calculations. Should we follow this convention?
   - **Recommended:** Yes - maintains consistency with existing measures
   - **Alternative:** DATEADD(-365) for simpler logic

### User Responses
**Response to Q1:** Yes, use SAMEPERIODLASTYEAR

### Decisions Made
- Use SAMEPERIODLASTYEAR + DIVIDE pattern (matches project conventions)
- Name: YoY_Revenue_Growth
- Format as percentage with 1 decimal place

---

## 6. Implementation Plan

**Status:** Approved

### Approach
Create measure following established project pattern with SAMEPERIODLASTYEAR and DIVIDE.

### Steps
1. Create measure definition in appropriate TMDL file
2. Apply percentage formatting
3. Validate syntax and logic

### Success Criteria
- Measure calculates YoY growth correctly
- Handles missing data (returns 0 instead of error)
- Follows naming and pattern conventions

---

## 7. Validation Results

### Syntax Validation
**Status:** Pass
**Details:** TMDL file parsed successfully, no syntax errors

### Logic Validation
**Status:** Pass
**Details:** Test query returned expected 12.5% growth for Q2 2024

### Quality Checks
**Status:** Pass
**Details:**
- Performance: Query execution 0.3s (target: <2s)
- Accuracy: Results match manual calculation
- Standards: Naming follows YoY_* convention

### Iteration Log
None - passed on first attempt

---

## 8. Final Summary

**Completion Date:** 2024-10-30 09:45:00

### What Was Done
Created `YoY_Revenue_Growth` measure with fiscal year handling.

### Before State
- No YoY revenue calculation in Power BI
- Manual Excel-based analysis required

### After State
- Automated YoY revenue calculation available
- Handles missing data gracefully
- Follows project conventions

### Impact
Users can now add `YoY_Revenue_Growth` to any visual with time context to see year-over-year revenue growth percentage.

### Next Steps
Add measure to existing revenue dashboard for visibility.
```

## Best Practices

1. **Update Incrementally:** Don't wait until the end - update as workflow progresses
2. **Timestamp Updates:** Always include timestamps so it's clear when information was added
3. **Be Specific:** Provide concrete details, not vague summaries
4. **Cross-Reference:** Sub-agents should reference each other's findings to coordinate
5. **Preserve History:** Don't delete previous information - append new iterations
6. **Clear Status:** Always update status fields so everyone knows current state
