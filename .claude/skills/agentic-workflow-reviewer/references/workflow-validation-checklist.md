# Agentic Workflow Validation Checklist

This checklist defines the 5 core properties that every high-quality agentic workflow must have.

## 1. Prompt Refinement (Specification Phase)

**Requirement:** At the beginning of the workflow, the prompt must be refined and made specific with clear specifications.

**Must Include:**
- **Goals:** Clear, measurable objectives the workflow aims to achieve
- **Constraints:** Boundaries, limitations, or requirements that must be respected
- **Desired Outputs:** Specific artifacts, files, or results expected at completion

**Validation Questions:**
- [ ] Does the workflow start with a prompt refinement phase?
- [ ] Are goals explicitly defined and measurable?
- [ ] Are constraints clearly stated?
- [ ] Are desired outputs specified with format/structure details?

**Example (Good):**
```markdown
## Prompt Refinement

Before proceeding, clarify the following specifications:

**Goals:**
- Create a Power BI measure for Year-over-Year revenue growth
- Ensure calculation handles missing data gracefully

**Constraints:**
- Must use existing Date and Sales tables
- Cannot modify existing relationships
- Must follow project naming conventions (YoY_*)

**Desired Outputs:**
- DAX measure code in TMDL format
- Documentation in findings.md
- Test validation results
```

**Example (Bad):**
```markdown
## Step 1: Create the measure
Create a measure for revenue growth.
```

---

## 2. Human-in-the-Loop Feedback Section

**Requirement:** A dedicated section to clarify requirements and get human feedback with recommendations.

**Must Include:**
- **Feedback Loop Structure:** Clear mechanism for user input/approval
- **Recommendations:** Intelligent suggestions based on analysis
- **Sub-agent Coordination:** If sub-agents are used, feedback loop must exist between main agent and sub-agents via persistent markdown file

**Sub-agent Communication Requirements:**
- **Persistence:** Markdown file that persists information between sub-agent calls
- **Bidirectional:** Sub-agents can read context from main agent AND communicate with each other
- **Structured Template:** Use standardized template structure (see `subagent-communication-template.md`)

**Validation Questions:**
- [ ] Is there a dedicated feedback section?
- [ ] Does it provide recommendations, not just ask questions?
- [ ] If sub-agents are used, is there a persistent markdown file for coordination?
- [ ] Does the coordination file follow the template structure?
- [ ] Can sub-agents read from and write to this file?

**Example (Good):**
```markdown
## Human Feedback & Recommendations

Based on analysis of your data model, I recommend:

**Option 1: SAMEPERIODLASTYEAR (Recommended)**
- Pros: Handles fiscal calendars, standard pattern in your project
- Cons: Requires contiguous date table

**Option 2: DATEADD with -365 days**
- Pros: Simple, works with gaps in data
- Cons: Not accurate for leap years

Please confirm your preference or provide alternative approach.

**Sub-agent Context:** See `.claude/workflows/yoy-measure/agent_context.md` for:
- Data model analysis results
- Pattern discovery findings
- Design specifications
```

**Example (Bad):**
```markdown
## Step 2: Implement
I'll now create the measure.
```

---

## 3. Validation Loop with Quality Checks

**Requirement:** The workflow must include a looping feature to validate solutions or check syntax/quality.

**Must Include:**
- **Validation Step:** Explicit validation phase after implementation
- **Quality Checks:** Syntax validation, logical validation, or quality assessment
- **Iteration Capability:** Ability to loop back and fix issues if validation fails

**Validation Questions:**
- [ ] Is there an explicit validation step?
- [ ] Are specific quality checks defined (syntax, logic, performance, etc.)?
- [ ] Does the workflow loop back if validation fails?
- [ ] Are validation criteria clearly defined?

**Example (Good):**
```markdown
## Validation Loop

After implementation, perform the following checks:

1. **Syntax Validation:** Parse TMDL file and check for syntax errors
2. **Logic Validation:** Test measure with sample data
3. **Quality Checks:**
   - Performance: Query execution time < 2s
   - Accuracy: Results match expected values in test cases
   - Standards: Naming follows project conventions

**If any validation fails:**
- Document the failure in agent_context.md
- Analyze root cause
- Apply fix
- Re-run validation loop (max 3 iterations)
```

**Example (Bad):**
```markdown
## Step 4: Done
The measure is created.
```

---

## 4. Persistent Documentation

**Requirement:** Document outputs in a persistent manner throughout the workflow.

**Must Include:**
- **Findings File:** Markdown file that persists findings, decisions, and results
- **Incremental Updates:** Documentation updated as workflow progresses, not just at the end
- **Structured Format:** Consistent structure across workflow executions

**Validation Questions:**
- [ ] Is there a persistent documentation file (e.g., findings.md, results.md)?
- [ ] Is documentation updated incrementally during workflow execution?
- [ ] Does documentation follow a consistent structure?
- [ ] Are key decisions and rationale captured?

**Example (Good):**
```markdown
## Documentation Structure

All workflow progress is documented in `.claude/workflows/yoy-measure/findings.md`:

**Structure:**
- Prerequisites: Initial context and requirements
- Analysis: Data model findings and patterns discovered
- Design: Specification and design decisions
- Implementation: Code changes applied
- Validation: Test results and quality checks
- Summary: Final outcomes and impact

Documentation is updated after each major phase.
```

**Example (Bad):**
```markdown
## Step 5: Summary
I created a measure.
```

---

## 5. Clear Summary with Before/After Examples

**Requirement:** Output a clear summary of what was done with examples showing before/after impact.

**Must Include:**
- **Summary Section:** Clear description of work completed
- **Before State:** What existed before the workflow
- **After State:** What exists after the workflow
- **Impact Examples:** Concrete examples showing the difference
- **Usage Guidance:** How to use or verify the changes

**Validation Questions:**
- [ ] Is there a dedicated summary section?
- [ ] Does it include before/after comparison?
- [ ] Are concrete examples provided?
- [ ] Is impact clearly explained?
- [ ] Are next steps or usage instructions provided?

**Example (Good):**
```markdown
## Summary

Created `YoY_Revenue_Growth` measure with fiscal year handling.

**Before:**
- No year-over-year calculation capability
- Manual Excel-based YoY analysis required

**After:**
- Automated YoY calculation in Power BI
- Handles missing data with DIVIDE pattern
- Follows project naming conventions

**Example Impact:**
```dax
// Query: What was revenue growth in Q2 2024?
// Before: Not possible in Power BI
// After:
[YoY_Revenue_Growth] =
    VAR CurrentRevenue = [Total_Revenue]
    VAR PriorRevenue = CALCULATE([Total_Revenue], SAMEPERIODLASTYEAR('Date'[Date]))
    RETURN DIVIDE(CurrentRevenue - PriorRevenue, PriorRevenue, 0)
// Result: Shows 12.5% growth in Q2 2024
```

**Usage:**
Add `YoY_Revenue_Growth` measure to any visual with time context.
```

**Example (Bad):**
```markdown
## Done
Created the measure. It calculates year-over-year growth.
```

---

## Scoring Rubric

For each of the 5 core properties:
- **✅ Pass:** Property is fully implemented with all required elements
- **⚠️ Partial:** Property exists but missing key elements
- **❌ Fail:** Property is missing or inadequate

**Overall Assessment:**
- **Excellent:** 5/5 Pass
- **Good:** 4/5 Pass, 1/5 Partial
- **Needs Improvement:** 3/5 or fewer Pass
- **Inadequate:** 2/5 or more Fail
