---
name: agentic-workflow-creator
description: Create high-quality agentic workflows (slash commands with multi-agent orchestration) following proven architectural principles. Use when users request "create a workflow", "build an agentic system", "design a multi-agent workflow", or "set up automation for [task]". This skill synthesizes user requests into structured workflows with proper prompt refinement, human feedback loops, validation loops, persistent documentation, and clear summaries with examples. It ensures workflows use coordination files for sub-agent communication and follow naming conventions.
---

# Agentic Workflow Creator

Create production-quality agentic workflows that implement the 5 core architectural principles for reliable, maintainable multi-agent systems.

## Overview

This skill guides you through creating complete agentic workflows that include:
- **Slash commands** that orchestrate workflow execution
- **Specialized agents** that perform discrete tasks
- **Coordination files** for persistent sub-agent communication
- **Proper architecture** following validation-proven principles

**Use this skill when:**
- User requests creation of a new workflow or automation
- User describes a multi-step process that needs agent orchestration
- User wants to improve an existing workflow with best practices
- User asks "how do I create a workflow for [task]"

## Workflow Creation Process

### Step 1: Synthesize User Request

Understand what the user wants to accomplish:

**Ask clarifying questions:**
- What is the primary goal of this workflow?
- What are the inputs and expected outputs?
- Are there multiple steps or phases?
- Should multiple agents work in parallel or sequentially?
- What decisions require human approval?

**Analyze existing workflows:**
Before creating new workflows, check `.claude/README.md` for existing agents and workflows that could be reused or composed.

Read `.claude/README.md` to understand:
- What agents already exist
- What workflows are already implemented
- Whether components can be reused

---

### Step 2: Design Workflow Architecture

Apply the 5 core architectural principles from `references/workflow-architecture-principles.md`:

#### 2.1: Load Architecture Principles

Read `references/workflow-architecture-principles.md` to understand:
1. **Prompt Refinement** - How to clarify goals, constraints, outputs
2. **Human Feedback Loop** - How to present recommendations
3. **Validation Loop** - How to implement quality checks with iteration
4. **Persistent Documentation** - How to structure coordination files
5. **Clear Summary** - How to show before/after with concrete examples

#### 2.2: Identify Agent Decomposition

Break down the workflow into specialized agents:

**Questions to answer:**
- What are the distinct responsibilities? (Each becomes an agent)
- Which tasks can run in parallel vs sequential?
- What information needs to be shared between agents?
- Where do validation loops belong?

**Pattern Recognition:**

- **Sequential Pattern:** Agent A → Agent B → Agent C (when B needs A's output)
- **Parallel Pattern:** Agent A + Agent B → Agent C (when A and B are independent)
- **Validation Pattern:** Implementation Agent → Validation Agent → (loop if fail)

#### 2.3: Define Coordination Strategy

For multi-agent workflows, define coordination file structure:

**Coordination File Template:** See `assets/coordination-file-template.md`

**Key sections:**
1. Request Summary - User's request and refined specs
2. Main Agent Findings - Analysis and delegation plan
3. Sub-Agent Reports - Each agent documents findings
4. Integration & Synthesis - Combined understanding
5. User Feedback Loop - Questions and decisions
6. Implementation Plan - Chosen approach
7. Validation Results - Quality checks and iterations
8. Final Summary - Before/after with examples

#### 2.4: Design Human-in-the-Loop Points

Identify where user input is needed:

**Common feedback points:**
- After analysis phase (approach confirmation)
- After planning phase (implementation approval)
- After validation failures (retry vs abort decision)

**Recommendation pattern:**
- Present 2-3 options with pros/cons
- Recommend one option with rationale
- Ask user to confirm or choose alternative

---

### Step 3: Apply Naming Conventions

Read `references/agent-naming-conventions.md` for guidance on:

**Slash Command Naming:**
- Pattern: `/[workflow-name]` (kebab-case, verb phrase)
- Examples: `/evaluate-pbi-project-file`, `/create-pbi-artifact`
- File: `.claude/commands/[workflow-name].md`

**Agent Naming:**
- Pattern: `[domain]-[function]-[role]`
- Role archetypes: analyzer, locator, designer, planner, implementer, validator, reviewer, understander, decomposer
- Examples: `powerbi-code-locator`, `powerbi-data-model-analyzer`
- File: `.claude/agents/[agent-name].md`

**Coordination File Naming:**
- Common names: `findings.md`, `coordination.md`, `agent_context.md`
- Location: `agent_scratchpads/[timestamp]-[problem-name]/[filename].md`

---

### Step 4: Create Workflow Plan Document

Present a structured plan to the user for approval:

```markdown
# Workflow Plan: [Workflow Name]

## Purpose
[One-sentence description]

## Parameters
- --param1 (required): [description]
- --param2 (optional): [description]

## Architecture

### Phases
1. **Prompt Refinement** - Clarify goals, constraints, outputs
2. **[Phase Name]** - [Description] (Agent: [agent-name])
3. **[Phase Name]** - [Description] (Agent: [agent-name])
4. **Human Feedback** - Present options and get user decision
5. **[Phase Name]** - [Description] (Agent: [agent-name])
6. **Validation** - Check quality, iterate if needed
7. **Summary** - Generate before/after examples

### Agents Required

1. **[agent-1-name]** - [Role] - [What it does]
   - Inputs: [What it needs]
   - Outputs: [What it produces]
   - Updates: Section [N] of coordination file

2. **[agent-2-name]** - [Role] - [What it does]
   - Inputs: [What it needs]
   - Outputs: [What it produces]
   - Updates: Section [M] of coordination file

### Coordination File
- Location: `agent_scratchpads/[timestamp]-[workflow-name]/[filename].md`
- Template: See coordination-file-template.md
- Sections: [List key sections]

### Execution Flow
```
User Request
   ↓
Prompt Refinement
   ↓
Initialize Coordination File
   ↓
[Agent 1] → Section 1 of coordination.md
   ↓
[Agent 2] → Section 2 of coordination.md (reads Section 1)
   ↓
Integration & Synthesis (Main Agent)
   ↓
Human Feedback Loop
   ↓
[Agent 3] → Section 3 of coordination.md (uses user decision)
   ↓
Validation Loop
   ↓
Final Summary
```

### Files to Create
1. `.claude/commands/[workflow-name].md` - Slash command
2. `.claude/agents/[agent-1-name].md` - Agent 1
3. `.claude/agents/[agent-2-name].md` - Agent 2
4. `.claude/agents/[agent-n-name].md` - Agent N

---

**User Approval Required:** Please confirm this plan or suggest modifications.
```

**Wait for user approval** before proceeding to implementation.

---

### Step 5: Implement Workflow Files

Once plan is approved, create the workflow files using templates:

#### 5.1: Create Slash Command File

Use `assets/slash-command-template.md` as base.

**Customize for workflow:**
- Fill in workflow name, purpose, parameters
- Define each phase with clear objectives
- Specify agent invocations with Task tool
- Include validation loops
- Document expected outputs

**File location:** `.claude/commands/[workflow-name].md`

**Key sections to customize:**
- Phase 1: Prompt Refinement (goals, constraints, outputs)
- Phase N: Agent invocations with coordination file updates
- Human Feedback Loop with recommendation-first approach
- Validation Loop with iteration capability
- Final Summary structure

#### 5.2: Create Agent Files

Use `assets/agent-template.md` as base for each agent.

**Customize for each agent:**
- Define agent's purpose and role archetype
- List inputs and outputs
- Document step-by-step process
- Specify coordination file sections to read/write
- Include error handling
- Provide example execution

**File location:** `.claude/agents/[agent-name].md`

**Critical elements:**
- Clear process steps with decision points
- Coordination file communication patterns
- Quality criteria for outputs
- Critical constraints (must do / must not do)

#### 5.3: Document in README.md

Add workflow to `.claude/README.md`:

**In Commands section:**
```markdown
### `/[workflow-name]`

**Purpose:** [Description]

**Usage:**
```bash
/[workflow-name] --param1 <value> --description "<description>"
```

**Parameters:**
- --param1 (required): [Description]

**Workflow:**
1. [Phase 1 description]
2. [Phase 2 description]
...

**Agents Involved:**
1. [agent-name] - [Description]
```

**In Agents section** (for each new agent):
```markdown
#### `[agent-name]`

**Purpose:** [One-line description]

**Invocation:** [When it's invoked]

**Inputs:**
- [Input 1]

**What It Does:**
- [Action 1]
- [Action 2]

**Output:** [What it produces]
```

---

### Step 6: Validate Workflow Design

Check the created workflow against the 5 core principles:

**Use agentic-workflow-reviewer skill** to validate:
```
Review the workflow I just created at .claude/commands/[workflow-name].md
```

The reviewer will check:
1. ✅ Prompt Refinement - Clear goals, constraints, outputs
2. ✅ Human Feedback Loop - Recommendations and coordination file
3. ✅ Validation Loop - Explicit checks with iteration
4. ✅ Persistent Documentation - Incremental updates
5. ✅ Clear Summary - Before/after examples

**If validation fails:**
- Review findings from agentic-workflow-reviewer
- Apply recommended improvements
- Re-validate

**If validation passes:**
- Workflow is ready for use
- User can test with real scenarios

---

## Reference Materials

This skill includes comprehensive references:

### `references/workflow-architecture-principles.md`

The 5 core principles that every workflow must implement:
1. Prompt Refinement
2. Human Feedback Loop
3. Validation Loop
4. Persistent Documentation
5. Clear Summary with Examples

**When to read:** During Step 2 (Design Workflow Architecture)

---

### `references/agent-naming-conventions.md`

Naming patterns for:
- Slash commands
- Agents
- Coordination files
- Agent role archetypes

**When to read:** During Step 3 (Apply Naming Conventions)

---

### `references/workflow-examples.md`

Complete examples of well-designed workflows:
- Example 1: Single-agent workflow
- Example 2: Multi-agent sequential workflow
- Example 3: Multi-agent parallel + sequential workflow

**When to read:** When learning patterns or need inspiration

---

## Template Assets

### `assets/slash-command-template.md`

Complete template for slash command files with:
- Frontmatter structure
- Phase-by-phase workflow definition
- Agent invocation patterns
- Validation loop structure
- Summary format

**When to use:** Step 5.1 (Create Slash Command File)

---

### `assets/agent-template.md`

Complete template for agent files with:
- Purpose and role definition
- Inputs/outputs specification
- Step-by-step process
- Coordination file patterns
- Error handling
- Example execution

**When to use:** Step 5.2 (Create Agent Files)

---

### `assets/coordination-file-template.md`

Complete template for coordination files with:
- 8-section structure
- Request summary format
- Sub-agent report structure
- Validation results format
- Final summary with before/after examples

**When to use:** Referenced by workflows; agents use this structure

---

## Best Practices

### 1. Reuse Before Creating

Always check `.claude/README.md` for existing agents that can be composed into new workflows.

**Example:** Don't create a new "code validator" if `powerbi-tmdl-syntax-validator` already exists.

---

### 2. Start with Simplest Pattern

Begin with simplest workflow that solves the problem:
- Single agent if possible
- Sequential agents if dependencies exist
- Parallel agents only when truly independent

**Complexity progression:**
- Single agent → Sequential agents → Parallel + sequential

---

### 3. Coordination Files are Mandatory for Multi-Agent Workflows

Never create a multi-agent workflow without a coordination file.

**Why:** Agents are stateless - they need persistent state to communicate.

---

### 4. Recommendation-First User Interaction

Never ask open-ended questions. Always:
1. Analyze the situation
2. Provide 2-3 options with pros/cons
3. Recommend one with rationale
4. Ask user to confirm or choose alternative

**Bad:** "How should we implement this?"
**Good:** "I recommend Option A (SAMEPERIODLASTYEAR) because [reasons]. Alternatively, Option B (DATEADD) could work if [conditions]. Which do you prefer?"

---

### 5. Validation Loops with Max Iterations

Always include validation with iteration limit:

```markdown
## Validation Loop

1. Check [criteria]
2. If fail: document, fix, re-run (max 3 iterations)
3. If still failing: escalate to user
```

---

### 6. Concrete Examples in Summaries

Final summaries must show before/after with actual code/examples:

```markdown
**Before:**
```dax
SUM(Sales[Amount])
```

**After:**
```dax
SUMX(Sales, Sales[Quantity] * Sales[Price])
```

**Result:** Calculation now uses transaction-level multiplication for accuracy.
```

---

## Common Workflow Patterns

### Pattern 1: Analyze → Plan → Implement → Validate

**Structure:**
1. Analysis agent examines context
2. Planning agent designs solution
3. Implementation agent applies changes
4. Validation agent checks quality

**When to use:** Most modification/update workflows

**Example:** `/evaluate-pbi-project-file`

---

### Pattern 2: Decompose → Specify → Discover → Design

**Structure:**
1. Decomposition agent breaks down request
2. Specification agent gathers requirements
3. Discovery agent finds patterns
4. Design agent generates solution

**When to use:** Creation workflows

**Example:** `/create-pbi-artifact`

---

### Pattern 3: Compare → Explain → Merge

**Structure:**
1. Comparison agent identifies differences
2. Explanation agent translates to business impact
3. Merge agent executes user decisions

**When to use:** Reconciliation/merging workflows

**Example:** `/merge-powerbi-projects`

---

## Quick Reference

### Workflow Creation Checklist

- [ ] Step 1: Understand user request with clarifying questions
- [ ] Step 2: Load architecture principles and design workflow
- [ ] Step 3: Apply naming conventions
- [ ] Step 4: Create workflow plan and get user approval
- [ ] Step 5: Implement files using templates
- [ ] Step 6: Validate with agentic-workflow-reviewer
- [ ] Update `.claude/README.md` with workflow documentation

---

### 5 Core Principles Quick Check

Every workflow MUST have:

1. ✅ **Prompt Refinement** - Goals, constraints, outputs at start
2. ✅ **Human Feedback** - Recommendations, coordination file for multi-agent
3. ✅ **Validation Loop** - Explicit checks with iteration capability
4. ✅ **Persistent Docs** - Incremental coordination file updates
5. ✅ **Clear Summary** - Before/after with concrete examples

---

### File Locations

```
.claude/
├── commands/[workflow-name].md         # Slash command
├── agents/[agent-name].md              # Individual agents
└── README.md                           # Update with new workflow

agent_scratchpads/
└── [timestamp]-[workflow-name]/
    └── [coordination-file].md          # Created at runtime
```

---

## Example Usage

**User:** "Create a workflow to analyze and optimize SQL queries"

**Skill Response:**

**Step 1: Synthesize Request**
- Primary goal: Analyze SQL queries and suggest optimizations
- Inputs: SQL query file or directory
- Outputs: Analysis report with optimization recommendations
- Multiple steps: Parse → Analyze → Recommend → Apply (optional)
- Human approval: After recommendations, before applying

**Step 2: Design Architecture**

Agents needed:
1. `sql-query-parser` - Extract queries and understand structure
2. `sql-performance-analyzer` - Identify performance issues
3. `sql-optimization-recommender` - Suggest improvements
4. `sql-query-implementer` - Apply approved optimizations (optional)

Execution: Sequential (each needs previous agent's output)

**Step 3: Naming**
- Command: `/optimize-sql-queries`
- Agents: Follow `[domain]-[function]-[role]` pattern
- Coordination: `sql_optimization_coordination.md`

**Step 4: Plan Document**
[Present workflow plan to user for approval]

**Step 5: Implementation**
[Create workflow files using templates]

**Step 6: Validation**
[Use agentic-workflow-reviewer to validate]

---

## Troubleshooting

### Issue: "Agents can't communicate with each other"
**Cause:** No coordination file defined
**Solution:** Add coordination file following `coordination-file-template.md`

### Issue: "Workflow doesn't have validation"
**Cause:** Missing validation loop phase
**Solution:** Add validation phase with explicit checks and iteration

### Issue: "Summary is too abstract"
**Cause:** Not using concrete before/after examples
**Solution:** Include actual code/data examples showing impact

### Issue: "User confused by workflow plan"
**Cause:** Too complex or missing human feedback points
**Solution:** Simplify phases, add human approval at key decision points
