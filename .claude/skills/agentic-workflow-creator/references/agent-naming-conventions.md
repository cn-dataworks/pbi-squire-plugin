# Agent Naming Conventions

Guidelines for naming and organizing agents in agentic workflows.

## Naming Patterns

### Single-Agent Workflows

For workflows with a single autonomous agent:

**Pattern:** `[domain]-[function]-[role]`

**Examples:**
- `powerbi-code-locator` - Locates code in Power BI projects
- `powerbi-data-model-analyzer` - Analyzes data model schema
- `powerbi-tmdl-syntax-validator` - Validates TMDL formatting

**Characteristics:**
- Verb-based naming (locator, analyzer, validator)
- Domain prefix for clarity (`powerbi-`, `python-`, `web-`)
- Single responsibility principle

---

### Multi-Agent Workflows

For workflows orchestrating multiple specialized agents:

**Orchestrator Pattern:** `[workflow-name]` (slash command)
**Agent Pattern:** `[workflow-name]-[specialization]-[role]`

**Example: `/merge-powerbi-projects`**

Agents:
- `powerbi-compare-project-code` - Technical Auditor
- `powerbi-code-understander` - Business Analyst
- `powerbi-code-merger` - Merge Surgeon

**Coordination File:** `merge_context.md` or `coordination.md`

---

## Agent Role Archetypes

Use these role archetypes for consistency:

### Analysis Roles
- **Analyzer** - Examines structure/schema
- **Locator** - Finds specific components
- **Discoverer** - Identifies patterns
- **Auditor** - Compares and identifies differences

### Transformation Roles
- **Designer** - Creates specifications/plans
- **Planner** - Designs solutions
- **Implementer** - Applies changes
- **Merger** - Combines components

### Validation Roles
- **Validator** - Checks correctness
- **Reviewer** - Evaluates quality
- **Tester** - Executes test cases
- **Verifier** - Confirms expectations

### Understanding Roles
- **Understander** - Explains business impact
- **Interpreter** - Translates technical to business
- **Decomposer** - Breaks down complex requests

---

## File Naming Conventions

### Slash Commands
**Location:** `.claude/commands/[workflow-name].md`

**Pattern:** Kebab-case, descriptive verb phrase

**Examples:**
- `/evaluate-pbi-project-file` → `evaluate-pbi-project-file.md`
- `/create-pbi-artifact` → `create-pbi-artifact.md`
- `/merge-powerbi-projects` → `merge-powerbi-projects.md`

---

### Agent Definitions
**Location:** `.claude/agents/[agent-name].md`

**Pattern:** Kebab-case, matches agent invocation name

**Examples:**
- `powerbi-code-locator.md`
- `powerbi-data-understanding-agent.md`
- `powerbi-dashboard-update-planner.md`

---

### Coordination Files
**Location:** `agent_scratchpads/[timestamp]-[problem-name]/[file-name].md`

**Common Patterns:**
- `findings.md` - Main analysis and implementation document
- `coordination.md` - Sub-agent communication file
- `agent_context.md` - Alternative to coordination.md
- `merge_analysis.md` - Merge workflow specific

**Naming Principle:** Use descriptive names that indicate purpose

---

## Workflow Folder Structure

### Standard Pattern

```
.claude/
├── commands/
│   └── [workflow-name].md              # Slash command orchestrator
├── agents/
│   ├── [agent-1-name].md               # Specialized agent 1
│   ├── [agent-2-name].md               # Specialized agent 2
│   └── [agent-n-name].md               # Specialized agent N
└── tools/
    └── [utility-scripts].py            # Python utilities

agent_scratchpads/
└── [timestamp]-[problem-name]/
    ├── findings.md                     # Main coordination file
    └── [additional-outputs]/           # Test results, screenshots, etc.
```

---

### Multi-Agent Coordination Pattern

```
.claude/
├── commands/
│   └── complex-workflow.md             # Orchestrates multiple agents
├── agents/
│   ├── complex-workflow-analyzer.md    # Phase 1 agent
│   ├── complex-workflow-planner.md     # Phase 2 agent
│   └── complex-workflow-executor.md    # Phase 3 agent
└── tools/
    └── workflow_utils.py               # Shared utilities

agent_scratchpads/
└── [timestamp]-[workflow-execution]/
    ├── coordination.md                 # Sub-agent communication
    └── findings.md                     # Final results
```

---

## Agent Invocation Names

When invoking agents via the Task tool, use consistent naming:

**Pattern:** Match the agent filename (without `.md`)

**Example:**
```python
Task(
    subagent_type="powerbi-code-locator",
    prompt="Find the Total Revenue measure in the Sales table",
    description="Locate existing code"
)
```

---

## Naming Anti-Patterns

❌ **Avoid generic names:**
- `agent-1`, `helper-agent`, `utility`

❌ **Avoid ambiguous verbs:**
- `processor`, `handler`, `manager` (too vague)

❌ **Avoid redundant domain prefixes:**
- `powerbi-powerbi-validator` (redundant)
- `pbi-pb-analyzer` (unclear abbreviations)

❌ **Avoid overly long names:**
- `powerbi-comprehensive-data-model-schema-analysis-and-documentation-agent`

✅ **Prefer specific, verb-based names:**
- `powerbi-data-model-analyzer`
- `powerbi-code-locator`
- `powerbi-tmdl-syntax-validator`

---

## Coordination File Templates

### Standard Coordination File Structure

```markdown
# [Workflow Name] Coordination

**Workflow:** [Name]
**Started:** [Timestamp]
**Status:** [In Progress | Completed | Failed]

---

## 1. Request Summary
[User's request and refined specifications]

---

## 2. Main Agent Findings
[Analysis and delegation plan]

---

## 3. Sub-Agent Reports

### Agent: [Agent Name]
**Task:** [Assigned task]
**Status:** [Pending | In Progress | Completed]
**Findings:** [Results]

---

## 4. Integration & Synthesis
[Combined findings across agents]

---

## 5. User Feedback Loop
[Questions and decisions]

---

## 6. Implementation Plan
[Chosen approach and steps]

---

## 7. Validation Results
[Quality checks and iteration log]

---

## 8. Final Summary
[Before/after with impact]
```

---

## Best Practices

1. **Consistency:** Use the same naming pattern across related workflows
2. **Clarity:** Names should be self-documenting
3. **Brevity:** Keep names concise while maintaining clarity
4. **Domain Prefixes:** Use when working in specific domains (powerbi-, python-, web-)
5. **Verb-Based:** Agent names should indicate their action (analyze, locate, validate)
6. **Template Usage:** Reuse proven templates for coordination files
