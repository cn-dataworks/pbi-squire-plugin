# Workflow Architecture Principles

These are the 5 core architectural principles that EVERY agentic workflow must implement for quality and effectiveness.

## 1. Prompt Refinement (Specification Phase)

**Requirement:** At the beginning of the workflow, the prompt must be refined with clear specifications.

**Must Include:**
- **Goals:** Clear, measurable objectives
- **Constraints:** Boundaries, limitations, requirements
- **Desired Outputs:** Specific artifacts and formats

**Implementation Pattern:**
```markdown
## Phase 1: Prompt Refinement

Clarify the following specifications before proceeding:

**Goals:**
- [Specific, measurable objective 1]
- [Specific, measurable objective 2]

**Constraints:**
- [Limitation or requirement 1]
- [Limitation or requirement 2]

**Desired Outputs:**
- [Artifact 1 with format details]
- [Artifact 2 with format details]
```

---

## 2. Human-in-the-Loop Feedback Section

**Requirement:** A dedicated section to clarify requirements and get human feedback with intelligent recommendations.

**Must Include:**
- **Feedback Loop Structure:** Clear mechanism for user input/approval
- **Recommendations:** Intelligent suggestions based on analysis (not just questions)
- **Sub-agent Coordination:** If sub-agents are used, a persistent markdown file for coordination

**Sub-agent Communication Requirements:**
- **Persistence:** Markdown file survives across sub-agent calls
- **Bidirectional:** Sub-agents read context AND communicate with each other
- **Structured Template:** Use standardized template structure

**Implementation Pattern:**
```markdown
## Phase 2: Human Feedback & Recommendations

Based on analysis, I recommend:

**Option 1: [Approach Name] (Recommended)**
- Pros: [Advantage 1], [Advantage 2]
- Cons: [Limitation 1]

**Option 2: [Alternative Approach]**
- Pros: [Advantage 1]
- Cons: [Limitation 1], [Limitation 2]

Please confirm your preference.

**Sub-agent Context:** See `[workflow-folder]/coordination.md` for:
- [Agent 1] findings
- [Agent 2] analysis
- Integration summary
```

---

## 3. Validation Loop with Quality Checks

**Requirement:** The workflow must include explicit validation with iteration capability.

**Must Include:**
- **Validation Step:** Explicit validation phase
- **Quality Checks:** Specific checks (syntax, logic, performance)
- **Iteration Capability:** Loop back and fix if validation fails

**Implementation Pattern:**
```markdown
## Phase N: Validation Loop

Perform the following checks:

1. **[Check Type 1]:** [What to validate]
2. **[Check Type 2]:** [What to validate]
3. **Quality Criteria:**
   - [Criterion 1]: [Threshold or standard]
   - [Criterion 2]: [Threshold or standard]

**If any validation fails:**
- Document failure in coordination.md
- Analyze root cause
- Apply fix
- Re-run validation (max 3 iterations)
```

---

## 4. Persistent Documentation

**Requirement:** Document outputs persistently throughout the workflow.

**Must Include:**
- **Findings File:** Markdown file persisting findings, decisions, results
- **Incremental Updates:** Documentation updated as workflow progresses
- **Structured Format:** Consistent structure across executions

**Implementation Pattern:**
```markdown
## Documentation Structure

All workflow progress documented in `[workflow-folder]/findings.md`:

**Structure:**
- Prerequisites: Initial context and requirements
- Phase 1: [Phase name and outcomes]
- Phase 2: [Phase name and outcomes]
- ...
- Summary: Final outcomes and impact

Documentation updated after each major phase.
```

---

## 5. Clear Summary with Before/After Examples

**Requirement:** Output clear summary with examples showing before/after impact.

**Must Include:**
- **Summary Section:** Clear description of work completed
- **Before State:** What existed before
- **After State:** What exists after
- **Impact Examples:** Concrete examples showing difference
- **Usage Guidance:** How to use or verify changes

**Implementation Pattern:**
```markdown
## Summary

[Clear description of what was accomplished]

**Before:**
- [State 1 before workflow]
- [State 2 before workflow]

**After:**
- [State 1 after workflow]
- [State 2 after workflow]

**Example Impact:**
```[code/example]
// Before: [description]
// After: [description]
// Result: [concrete outcome]
```

**Usage:**
[Instructions for using or verifying the changes]
```

---

## Design Principles for Implementation

### Principle 1: Sequential Clarity
Structure workflows as numbered phases that execute sequentially. Each phase should have clear inputs, outputs, and success criteria.

### Principle 2: Coordination Files Over Memory
For multi-agent workflows, ALWAYS use a persistent markdown coordination file. Never rely on agent memory or context passing alone.

### Principle 3: Recommendation-First Interaction
When asking users for input, provide intelligent recommendations based on analysis. Present options with pros/cons rather than open-ended questions.

### Principle 4: Incremental Documentation
Update persistent documentation after EACH phase, not just at the end. This creates an audit trail and enables recovery from failures.

### Principle 5: Concrete Examples Over Abstract Descriptions
In summaries and documentation, show actual code/examples rather than describing what changed in prose.

---

## Critical Success Factors

✅ **Every workflow MUST implement all 5 principles**
✅ **Multi-agent workflows MUST use coordination files**
✅ **Validation MUST be explicit with iteration capability**
✅ **Documentation MUST be incremental, not just final**
✅ **Summaries MUST include concrete before/after examples**
