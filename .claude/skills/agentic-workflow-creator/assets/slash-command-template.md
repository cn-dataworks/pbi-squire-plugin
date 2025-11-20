# [Workflow Name] Command

**Purpose:** [One-sentence description of what this workflow accomplishes]

**Usage:**
```bash
/[command-name] --param1 <value> [--param2 <value>] --description "<description>"
```

**Parameters:**
- `--param1` (required): [Description of required parameter]
- `--param2` (optional): [Description of optional parameter]
- `--description` (required): [Description of the problem/request]

---

## Workflow Overview

**Agents Involved:**
1. `[agent-1-name]` - [Brief description of agent's role]
2. `[agent-2-name]` - [Brief description of agent's role]
3. `[agent-n-name]` - [Brief description of agent's role]

**Execution Pattern:** [Sequential | Parallel | Hybrid]

**Coordination File:** `agent_scratchpads/[timestamp]-[workflow-name]/[coordination-file].md`

---

## Phase 1: Prompt Refinement

Clarify specifications before proceeding:

**Goals:**
- [Specific, measurable objective 1]
- [Specific, measurable objective 2]
- [Specific, measurable objective 3]

**Constraints:**
- [Limitation or requirement 1]
- [Limitation or requirement 2]
- [Limitation or requirement 3]

**Desired Outputs:**
- [Artifact 1 with format details]
- [Artifact 2 with format details]
- [Artifact 3 with format details]

**User Confirmation Required:** YES/NO

---

## Phase 2: Initialize Coordination File

Create persistent coordination file at:
`agent_scratchpads/[timestamp]-[workflow-name]/[coordination-file].md`

**Purpose:** Enables communication between:
- Main orchestrator and sub-agents
- Sub-agents with each other
- Persistent state across workflow execution

**Template:** Use coordination file template from assets.

---

## Phase 3: [Agent 1 Execution]

**Agent:** `[agent-1-name]`

**Task:** [What this agent accomplishes]

**Inputs:**
- [Input 1 from user or previous phase]
- [Input 2 from user or previous phase]

**Outputs:**
- Updates Section [N] of coordination file
- [Other outputs]

**Invocation:**
```
Invoke Task tool with:
- subagent_type: "[agent-1-name]"
- prompt: "[Detailed task description]"
- description: "[Short 3-5 word description]"
```

---

## Phase 4: [Agent 2 Execution]

**Agent:** `[agent-2-name]`

**Task:** [What this agent accomplishes]

**Inputs:**
- Section [N] from coordination file (Agent 1 findings)
- [Other inputs]

**Outputs:**
- Updates Section [M] of coordination file
- [Other outputs]

**Dependencies:** Requires Phase 3 completion

**Invocation:**
```
Invoke Task tool with:
- subagent_type: "[agent-2-name]"
- prompt: "[Detailed task description including reference to coordination file]"
- description: "[Short 3-5 word description]"
```

---

## Phase 5: Human Feedback Loop

Present findings and recommendations from agents:

**Analysis Summary:**
[Summary of what agents discovered]

**Recommendations:**

**Option 1: [Approach Name] (Recommended)**
- **Pros:** [Advantage 1], [Advantage 2]
- **Cons:** [Limitation 1]
- **Impact:** [What happens if user chooses this]

**Option 2: [Alternative Approach]**
- **Pros:** [Advantage 1]
- **Cons:** [Limitation 1], [Limitation 2]
- **Impact:** [What happens if user chooses this]

**Question:** Which approach should we proceed with?

**User Response Handling:**
- Capture user decision
- Document in Section [N] of coordination file
- Proceed to implementation phase

---

## Phase 6: [Implementation/Action Phase]

**Agent:** `[agent-n-name]`

**Task:** Execute user-approved approach

**Inputs:**
- Sections [N], [M] from coordination file
- User decision from Phase 5

**Outputs:**
- [Concrete artifact/change produced]
- Updates Section [P] of coordination file

**Invocation:**
```
Invoke Task tool with:
- subagent_type: "[agent-n-name]"
- prompt: "[Detailed implementation instructions]"
- description: "[Short 3-5 word description]"
```

---

## Phase 7: Validation Loop

Perform quality checks on implementation:

### Validation Check 1: [Check Name]
**Criteria:** [What to validate]
**Method:** [How to validate]
**Pass Criteria:** [Threshold or standard]

### Validation Check 2: [Check Name]
**Criteria:** [What to validate]
**Method:** [How to validate]
**Pass Criteria:** [Threshold or standard]

### Validation Check 3: [Check Name]
**Criteria:** [What to validate]
**Method:** [How to validate]
**Pass Criteria:** [Threshold or standard]

**If Any Validation Fails:**
1. Document failure details in coordination file
2. Analyze root cause
3. Apply fix (manual or via agent)
4. Re-run validation (max 3 iterations)
5. If still failing after 3 iterations, escalate to user

**Validation Agent:** `[validation-agent-name]` (if applicable)

---

## Phase 8: Final Summary

Generate comprehensive summary in coordination file Section [FINAL]:

**What Was Done:**
[Clear description of work completed]

**Before State:**
- [State 1 before workflow]
- [State 2 before workflow]
- [State 3 before workflow]

**After State:**
- [State 1 after workflow]
- [State 2 after workflow]
- [State 3 after workflow]

**Concrete Impact Example:**
```[code/example]
// Before: [description of before state]
[before code/example]

// After: [description of after state]
[after code/example]

// Result: [concrete outcome]
```

**Files Created/Modified:**
- `[path/to/file1]` - [Description]
- `[path/to/file2]` - [Description]

**Usage Instructions:**
[How to use or verify the changes]

**Next Steps:**
1. [Recommended next action 1]
2. [Recommended next action 2]

---

## Output Structure

**Primary Output:** `agent_scratchpads/[timestamp]-[workflow-name]/[coordination-file].md`

**Sections:**
1. Request Summary & Refined Specifications
2. Agent 1 Findings
3. Agent 2 Findings
4. Integration & Synthesis
5. User Feedback Loop & Decisions
6. Implementation Results
7. Validation Results
8. Final Summary with Before/After Examples

**Additional Outputs:** (if applicable)
- `[output-folder]/[files]`

---

## Error Handling

### Error: [Common Error Type 1]
**Symptoms:** [How to recognize this error]
**Cause:** [Why this error occurs]
**Resolution:** [How to fix]

### Error: [Common Error Type 2]
**Symptoms:** [How to recognize this error]
**Cause:** [Why this error occurs]
**Resolution:** [How to fix]

**General Error Protocol:**
1. Document error in coordination file
2. Attempt automated recovery (if applicable)
3. If recovery fails, provide user with:
   - Error description
   - Suggested resolution steps
   - Option to retry or abort

---

## Best Practices

1. **Incremental Documentation:** Update coordination file after EACH phase
2. **Recommendation-First:** Provide intelligent recommendations, not just questions
3. **Validation Before Finalization:** Always validate before marking workflow complete
4. **Concrete Examples:** Show actual code/examples in summary, not descriptions
5. **State Preservation:** Use coordination file to preserve state across agent invocations

---

## Dependencies

**Required Tools:**
- [Tool 1]: [Purpose]
- [Tool 2]: [Purpose]

**Required Agents:**
- `[agent-1-name]`: [File location]
- `[agent-2-name]`: [File location]

**Required Scripts/Utilities:** (if applicable)
- `[script-name]`: [Purpose and location]

---

## Testing & Validation

**Test Workflow With:**
1. [Test case 1 description]
2. [Test case 2 description]
3. [Test case 3 description]

**Expected Outcomes:**
- [Outcome 1]
- [Outcome 2]
- [Outcome 3]
