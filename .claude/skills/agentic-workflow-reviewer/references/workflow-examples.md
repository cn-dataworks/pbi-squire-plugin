# Agentic Workflow Examples

This document provides concrete examples of good and bad agentic workflow implementations across all 5 core properties.

## Example 1: Complete Good Workflow

This example demonstrates a workflow that implements all 5 core properties correctly.

```markdown
# Create Power BI YoY Revenue Measure Workflow

## Prompt Refinement

Before proceeding with implementation, clarify the following specifications:

**Goals:**
1. Create a DAX measure calculating year-over-year revenue growth as a percentage
2. Measure must handle missing historical data gracefully (no #ERROR on visuals)
3. Results must be accurate for fiscal year analysis

**Constraints:**
- Must use existing Date and Sales tables without modifications
- Cannot alter existing table relationships
- Must follow project naming conventions (YoY_* prefix)
- Maximum query execution time: 2 seconds

**Desired Outputs:**
- DAX measure code in TMDL format at `.../measures/YoY_Revenue_Growth.tmdl`
- Complete documentation in `findings.md` with design rationale
- Test validation results demonstrating accuracy
- Usage examples showing before/after impact

---

## Data Model Analysis

**Sub-Agent Delegation:** Analyze data model structure
**Context File:** `.claude/workflows/yoy-measure/agent_context.md`

The Data Model Analyzer sub-agent will:
1. Scan TMDL files to identify Date and Sales table structures
2. Document column names, data types, and relationships
3. Verify date table continuity for time intelligence functions
4. Report findings in agent_context.md Section 3

---

## Pattern Discovery

**Sub-Agent Delegation:** Discover existing YoY patterns
**Context File:** `.claude/workflows/yoy-measure/agent_context.md`

The Pattern Discovery sub-agent will:
1. Search codebase for existing YoY measures
2. Extract calculation patterns and naming conventions
3. Identify formatting standards (percentage, decimal places)
4. Report findings in agent_context.md Section 3

---

## Human Feedback & Recommendations

**Context:** Sub-agents have completed analysis (see `agent_context.md` sections 3-4)

Based on analysis, I recommend:

**Option 1: SAMEPERIODLASTYEAR Pattern (Recommended)**
- **Pros:**
  - Handles fiscal calendars correctly
  - Matches 2 existing YoY measures in your project
  - Standard time intelligence pattern in Power BI
- **Cons:**
  - Requires continuous date table (✓ verified available)
  - More complex than simple date math

**Option 2: DATEADD(-365 days)**
- **Pros:**
  - Simpler logic
  - Works with gaps in date table
- **Cons:**
  - Inaccurate for leap years
  - Doesn't match existing project patterns
  - Not recommended for fiscal year analysis

**Option 3: Custom Date Math**
- **Pros:**
  - Maximum flexibility
- **Cons:**
  - Risk of errors
  - Breaks project consistency
  - Harder to maintain

**Recommendation:** Use Option 1 (SAMEPERIODLASTYEAR) to maintain consistency with existing project patterns and ensure fiscal year accuracy.

**Please confirm your preference or specify alternative approach.**

---

## Implementation

**Status:** Awaiting user approval (see Human Feedback section above)
**Context File:** `.claude/workflows/yoy-measure/agent_context.md`

Once approach is confirmed:
1. Create measure definition following approved pattern
2. Apply formatting (percentage, 1 decimal place based on project standards)
3. Document implementation in findings.md
4. Update agent_context.md with implementation details

---

## Validation Loop

After implementation, perform the following quality checks:

### 1. Syntax Validation
- Parse TMDL file to verify no syntax errors
- Confirm measure name follows YoY_* convention
- Validate formatting expression is correct

### 2. Logic Validation
- Execute test query with known data (Q2 2024 vs Q2 2023)
- Verify result matches manual calculation
- Test edge cases: no prior year data, zero revenue in prior year

### 3. Performance Check
- Measure query execution time
- Verify < 2 second constraint is met
- Document performance metrics in findings.md

### 4. Quality Standards
- Naming follows project conventions: ✓/✗
- Pattern matches existing measures: ✓/✗
- Documentation is complete: ✓/✗
- Test cases pass: ✓/✗

**If any validation fails:**
1. Document the failure in agent_context.md Section 7
2. Analyze root cause
3. Apply corrective fix
4. Re-run validation loop
5. Maximum 3 iterations before escalating to user

---

## Documentation

All workflow progress is documented in `findings.md` with the following structure:

### Structure
1. **Prerequisites:** Initial requirements and context
2. **Analysis:** Data model findings and pattern discovery results
3. **Design:** Specification and design decisions with rationale
4. **Implementation:** Code changes applied with file locations
5. **Validation:** Test results and quality check outcomes
6. **Summary:** Final outcomes, impact, and usage guidance

Documentation is updated incrementally after each phase, not just at the end.

---

## Summary

**Status:** [To be completed after workflow execution]

### What Was Done
[Clear description of work completed]

### Before State
- No year-over-year revenue calculation capability in Power BI
- Manual Excel-based YoY analysis required for stakeholder reports
- Inconsistent YoY calculations across different analysts

### After State
- Automated YoY revenue calculation available in Power BI
- Single source of truth for YoY metrics
- Follows established project patterns and conventions

### Example Impact

**Before:**
```
User Question: "What was revenue growth in Q2 2024?"
Process: Export data → Excel → Manual formula → Report
Time: 15 minutes per query
Accuracy: Varies by analyst
```

**After:**
```dax
// Add [YoY_Revenue_Growth] measure to any visual with time context
YoY_Revenue_Growth =
    VAR CurrentRevenue = [Total_Revenue]
    VAR PriorRevenue = CALCULATE([Total_Revenue], SAMEPERIODLASTYEAR('Date'[Date]))
    RETURN DIVIDE(CurrentRevenue - PriorRevenue, PriorRevenue, 0)

// Result: 12.5% growth in Q2 2024 (verified against manual calculation)
```

```
User Question: "What was revenue growth in Q2 2024?"
Process: View dashboard with YoY_Revenue_Growth measure
Time: Instant
Accuracy: Consistent across all users
```

### Usage Instructions
1. Add `YoY_Revenue_Growth` to any visual with time dimension
2. Measure automatically calculates YoY % based on date context
3. Returns 0 when no prior year data exists (no errors displayed)
4. Format is applied automatically (percentage, 1 decimal place)

### Next Steps
- Add measure to executive revenue dashboard
- Create documentation for business users
- Consider creating similar measures for other KPIs (units, customers, margin)
```

---

## Example 2: Bad Workflow (Missing Core Properties)

This example demonstrates a workflow that fails to implement the 5 core properties.

```markdown
# Create YoY Measure

## Step 1: Analysis
I'll analyze the data model to understand the structure.

[Analysis happens but no sub-agent coordination file exists]

## Step 2: Create Measure
I'll create a measure for year-over-year growth.

[No prompt refinement, no goals/constraints specified]

```dax
YoY_Revenue = [Revenue] - CALCULATE([Revenue], DATEADD('Date'[Date], -1, YEAR))
```

[No human feedback section, no recommendations provided]

## Step 3: Done
I've created the measure. It calculates year-over-year revenue growth.

[No validation loop, no quality checks performed]

[No persistent documentation file created]

[No before/after examples, no usage guidance]
```

**Problems with this workflow:**

1. ❌ **Prompt Refinement:** No goals, constraints, or desired outputs specified
2. ❌ **Human Feedback:** No recommendations, no feedback loop, no sub-agent coordination
3. ❌ **Validation Loop:** No syntax check, no logic validation, no quality checks
4. ❌ **Persistent Documentation:** No findings.md, no structured documentation
5. ❌ **Summary with Examples:** No before/after comparison, no impact examples, no usage guidance

---

## Example 3: Partial Implementation (Needs Improvement)

This workflow has some good elements but is missing key components.

```markdown
# Create YoY Revenue Measure

## Specifications

**Goals:**
- Create a YoY revenue measure

**Constraints:**
- Use existing tables

**Outputs:**
- DAX measure

[✓ Prompt refinement exists but is too vague - needs specific, measurable details]

---

## Analysis

I've analyzed the data model and found:
- Date table exists
- Sales table exists

[✓ Analysis performed but no sub-agent coordination]
[❌ No agent_context.md for persistence]

---

## Recommendation

I recommend using SAMEPERIODLASTYEAR for the calculation.

[⚠️ Recommendation exists but lacks detail - no pros/cons, no alternatives]
[❌ No explicit feedback loop or user confirmation step]

---

## Implementation

```dax
YoY_Revenue_Growth =
    DIVIDE(
        [Revenue] - CALCULATE([Revenue], SAMEPERIODLASTYEAR('Date'[Date])),
        CALCULATE([Revenue], SAMEPERIODLASTYEAR('Date'[Date])),
        0
    )
```

[✓ Implementation provided]
[❌ No validation loop to check syntax/logic/quality]

---

## Summary

Created a YoY measure using SAMEPERIODLASTYEAR pattern.

[⚠️ Summary exists but lacks depth]
[❌ No before/after comparison]
[❌ No concrete examples showing impact]
[❌ No usage instructions]
```

**Assessment:**

1. ⚠️ **Prompt Refinement:** Present but too vague (needs measurable goals, specific constraints)
2. ❌ **Human Feedback:** Recommendation exists but no proper feedback loop, no sub-agent coordination
3. ❌ **Validation Loop:** No validation performed
4. ❌ **Persistent Documentation:** No structured documentation file
5. ⚠️ **Summary with Examples:** Summary exists but lacks examples and impact analysis

**Score:** 0 Pass, 2 Partial, 3 Fail = **Needs Improvement**

---

## Key Takeaways

### Good Workflows Have:
✓ Specific, measurable goals and constraints upfront
✓ Sub-agent coordination via persistent markdown files
✓ Detailed recommendations with pros/cons
✓ Explicit user feedback loops with confirmation steps
✓ Multi-stage validation (syntax, logic, quality)
✓ Iteration capability when validation fails
✓ Incremental persistent documentation
✓ Before/after examples showing concrete impact
✓ Clear usage instructions and next steps

### Bad Workflows Have:
✗ Vague or missing specifications
✗ No sub-agent coordination mechanism
✗ No recommendations or feedback loops
✗ No validation or quality checks
✗ No persistent documentation
✗ No examples or impact analysis
✗ Abrupt ending without guidance

### The Difference:
Good workflows treat the user as a collaborator, providing transparency, options, validation, and clear outcomes. Bad workflows treat the user as passive, providing minimal context and rushing to completion without verification.
