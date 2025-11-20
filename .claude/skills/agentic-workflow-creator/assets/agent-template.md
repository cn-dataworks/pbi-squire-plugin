# [Agent Name] Agent

**Purpose:** [One-sentence description of what this agent does]

**Role Archetype:** [Analyzer | Locator | Designer | Planner | Implementer | Validator | Reviewer | Understander | Decomposer]

**Invocation Pattern:** [When and how this agent is invoked - e.g., "After data model analysis phase" or "When user requests X"]

---

## Overview

This agent [detailed description of agent's responsibilities and expertise].

**Key Responsibilities:**
- [Responsibility 1]
- [Responsibility 2]
- [Responsibility 3]

**Expertise Areas:**
- [Domain knowledge area 1]
- [Domain knowledge area 2]
- [Domain knowledge area 3]

---

## Inputs

**Required Inputs:**
1. **[Input Name 1]** - [Description and expected format]
2. **[Input Name 2]** - [Description and expected format]
3. **[Input Name 3]** - [Description and expected format]

**Optional Inputs:**
1. **[Optional Input 1]** - [Description and when it's used]
2. **[Optional Input 2]** - [Description and when it's used]

**Context Requirements:**
- [Context requirement 1 - e.g., "Coordination file must exist with Section 1 completed"]
- [Context requirement 2]

---

## Process

### Step 1: [Step Name]

**Objective:** [What this step accomplishes]

**Actions:**
1. [Action 1 with details]
2. [Action 2 with details]
3. [Action 3 with details]

**Tools/Methods:**
- [Tool or method used]
- [Tool or method used]

**Example:**
```[code or example]
[Concrete example of what this step produces]
```

---

### Step 2: [Step Name]

**Objective:** [What this step accomplishes]

**Actions:**
1. [Action 1 with details]
2. [Action 2 with details]
3. [Action 3 with details]

**Decision Points:**
- **If [condition]:** [Action A]
- **If [condition]:** [Action B]
- **Otherwise:** [Default action]

**Example:**
```[code or example]
[Concrete example of what this step produces]
```

---

### Step 3: [Step Name]

**Objective:** [What this step accomplishes]

**Actions:**
1. [Action 1 with details]
2. [Action 2 with details]
3. [Action 3 with details]

**Validation Checks:**
- [Check 1]: [Expected result]
- [Check 2]: [Expected result]
- [Check 3]: [Expected result]

**Error Handling:**
- **Error Type 1:** [How to handle]
- **Error Type 2:** [How to handle]

---

### Step N: Document Findings

**Objective:** Update coordination file with agent findings

**Documentation Structure:**

```markdown
### Agent: [Agent Name]

**Task:** [Task assigned to this agent]
**Status:** Completed
**Last Updated:** [Timestamp]

#### Findings
[Key findings and analysis]

#### Data/Artifacts
[Code snippets, data samples, or artifacts produced]

#### Issues/Blockers
[Any problems encountered or questions for main agent]

#### Recommendations
[Agent's recommendations for next steps]
```

**Location:** Section [N] of coordination file

---

## Outputs

**Primary Output:**
- **[Output Name]** - [Description of primary output and format]

**Secondary Outputs:**
- **[Output Name 1]** - [Description]
- **[Output Name 2]** - [Description]

**Documentation Updates:**
- Updates Section [N] of coordination file: `[path/to/coordination.md]`

**Output Format:**

```[format]
[Example of output structure]
```

---

## Quality Criteria

This agent's outputs must meet the following quality standards:

### Criterion 1: [Criterion Name]
**Standard:** [What the standard is]
**Validation:** [How to verify]
**Example:** [Good example]

### Criterion 2: [Criterion Name]
**Standard:** [What the standard is]
**Validation:** [How to verify]
**Example:** [Good example]

### Criterion 3: [Criterion Name]
**Standard:** [What the standard is]
**Validation:** [How to verify]
**Example:** [Good example]

---

## Critical Constraints

**Must Do:**
- ✅ [Critical constraint 1]
- ✅ [Critical constraint 2]
- ✅ [Critical constraint 3]

**Must NOT Do:**
- ❌ [Prohibited action 1]
- ❌ [Prohibited action 2]
- ❌ [Prohibited action 3]

**Rationale:** [Why these constraints exist]

---

## Dependencies

**Required Files/Resources:**
- [File or resource 1]: [Purpose]
- [File or resource 2]: [Purpose]

**Required Tools:**
- [Tool 1]: [Purpose]
- [Tool 2]: [Purpose]

**Required Prior Agents:**
- `[agent-name]`: [What this agent must provide]

**Coordination File Requirements:**
- Section [N]: [What must be present]
- Section [M]: [What must be present]

---

## Error Handling

### Error: [Error Type 1]
**Cause:** [Why this error occurs]
**Symptoms:** [How to recognize]
**Resolution:**
1. [Step 1 to resolve]
2. [Step 2 to resolve]
3. [Step 3 to resolve]

### Error: [Error Type 2]
**Cause:** [Why this error occurs]
**Symptoms:** [How to recognize]
**Resolution:**
1. [Step 1 to resolve]
2. [Step 2 to resolve]

**Escalation Protocol:**
If agent cannot resolve error:
1. Document error details in coordination file
2. Set status to "Failed" with error description
3. Return control to main orchestrator
4. Main orchestrator decides whether to retry, skip, or abort

---

## Communication Patterns

### Reading from Coordination File

**When to Read:**
- At start of agent execution (to understand context)
- Before each major step (to check for updates from other agents)

**What to Read:**
- Section [N]: [What information to extract]
- Section [M]: [What information to extract]

**Example:**
```markdown
# Read Section 1 to understand user request
# Read Section 2 to see what [previous-agent] discovered
```

---

### Writing to Coordination File

**When to Write:**
- After each major step completion
- When encountering blockers or issues
- Upon agent completion

**What to Write:**
- Findings and analysis
- Data/artifacts produced
- Issues/blockers encountered
- Recommendations for next steps

**Update Pattern:**
```markdown
### Agent: [Agent Name]
**Status:** In Progress → Completed
**Findings:** [Incremental updates as work progresses]
```

---

### Communicating with Other Agents

**Reading Other Agent Findings:**
```markdown
# Before starting Step 2, read what [other-agent] found in Section 3
# Use those findings to inform this agent's analysis
```

**Referencing Other Agents:**
```markdown
# In recommendations, reference related findings:
"As noted by [other-agent] in Section 3, [finding]. This supports [conclusion]."
```

---

## Best Practices

1. **Incremental Documentation:** Update coordination file as you work, not just at the end
2. **Timestamp Updates:** Always include timestamp when updating status
3. **Cross-Reference Findings:** Reference other agents' findings when relevant
4. **Specific Recommendations:** Provide actionable recommendations, not vague suggestions
5. **Error Transparency:** Document all errors and blockers clearly
6. **Example-Driven:** Include concrete examples in findings, not just descriptions

---

## Example Execution

**Scenario:** [Description of example use case]

**Inputs:**
- [Input 1 value]
- [Input 2 value]

**Execution:**

**Step 1 Results:**
```
[Example output from Step 1]
```

**Step 2 Results:**
```
[Example output from Step 2]
```

**Step N Results:**
```
[Example output from Step N]
```

**Final Output:**
```markdown
### Agent: [Agent Name]

**Task:** [Task description]
**Status:** Completed
**Last Updated:** 2025-01-19 14:30:00

#### Findings
[Example findings for this scenario]

#### Data/Artifacts
[Example artifacts produced]

#### Recommendations
[Example recommendations]
```

---

## Testing & Validation

**Test Agent With:**
1. **Test Case 1:** [Description]
   - **Input:** [Test input]
   - **Expected Output:** [Expected result]

2. **Test Case 2:** [Description]
   - **Input:** [Test input]
   - **Expected Output:** [Expected result]

3. **Test Case 3:** [Description]
   - **Input:** [Test input]
   - **Expected Output:** [Expected result]

**Validation Checklist:**
- [ ] Agent produces expected output format
- [ ] Coordination file updated correctly
- [ ] Quality criteria met
- [ ] Error handling works as expected
- [ ] Dependencies satisfied

---

## Related Agents

**Upstream Agents** (agents that run before this one):
- `[agent-name]`: [What it provides to this agent]

**Downstream Agents** (agents that run after this one):
- `[agent-name]`: [What this agent provides to it]

**Alternative Agents** (agents that could be used instead):
- `[agent-name]`: [When to use alternative]
