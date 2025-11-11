---
name: agentic-workflow-reviewer
description: This skill should be used when reviewing, auditing, or validating agentic workflow files (markdown-based) to ensure they follow best practices. Use when users request "review this workflow", "audit my agent", "check workflow quality", or "validate agent design". The skill evaluates workflows against 5 core properties (prompt refinement, human feedback loops, validation loops, persistent documentation, and clear summaries with examples) and provides detailed recommendations for improvement.
---

# Agentic Workflow Reviewer

## Overview

Review and validate agentic workflow designs against established best practices. This skill audits workflow files (typically markdown-based) to ensure they implement 5 core properties that distinguish high-quality agentic workflows from inadequate ones.

**Use this skill when:**
- User asks to "review this workflow" or "audit my workflow"
- User requests "check workflow quality" or "validate agent design"
- User wants to "ensure workflow follows best practices"
- User provides a workflow file path for evaluation

## Core Validation Framework

Every high-quality agentic workflow must implement these 5 core properties:

1. **Prompt Refinement** - Clear specifications with goals, constraints, and desired outputs
2. **Human Feedback Loop** - Dedicated section for clarification with recommendations and sub-agent coordination
3. **Validation Loop** - Quality checks with iteration capability
4. **Persistent Documentation** - Structured, incremental documentation throughout workflow
5. **Clear Summary** - Before/after examples showing concrete impact

For detailed criteria and examples, see `references/workflow-validation-checklist.md`.

## Workflow Review Process

### Step 1: Load the Workflow File

Read the workflow file provided by the user.

```bash
# User typically provides path like:
# "Review .claude/commands/create-pbi-artifact.md"
# "Audit this workflow: .claude/workflows/deploy-workflow.md"
```

Read the file and load it into context for analysis.

### Step 2: Load Validation Checklist

Read `references/workflow-validation-checklist.md` to understand the detailed validation criteria for each of the 5 core properties.

This reference file provides:
- Detailed requirements for each property
- Validation questions to assess compliance
- Good vs bad examples
- Scoring rubric

### Step 3: Evaluate Each Core Property

Systematically evaluate the workflow against each of the 5 core properties:

#### 3.1 Prompt Refinement Assessment

**Check for:**
- [ ] Does workflow start with specification/refinement phase?
- [ ] Are goals explicitly defined and measurable?
- [ ] Are constraints clearly stated?
- [ ] Are desired outputs specified with format details?

**Score:** ✅ Pass | ⚠️ Partial | ❌ Fail

**Findings:** [Document what exists and what's missing]

#### 3.2 Human Feedback Loop Assessment

**Check for:**
- [ ] Is there a dedicated feedback section?
- [ ] Does it provide recommendations (not just questions)?
- [ ] If sub-agents are used, is there a persistent coordination file?
- [ ] Does the coordination file follow the template structure?
- [ ] Can sub-agents read from and write to this file?

**Reference template:** `references/subagent-communication-template.md`

**Score:** ✅ Pass | ⚠️ Partial | ❌ Fail

**Findings:** [Document what exists and what's missing]

**Critical Issue:** If sub-agents are used but no persistent coordination file exists, flag this as a **non-passing critical issue** that prevents proper agent coordination.

#### 3.3 Validation Loop Assessment

**Check for:**
- [ ] Is there an explicit validation step?
- [ ] Are specific quality checks defined?
- [ ] Does workflow loop back if validation fails?
- [ ] Are validation criteria clearly defined?

**Score:** ✅ Pass | ⚠️ Partial | ❌ Fail

**Findings:** [Document what exists and what's missing]

#### 3.4 Persistent Documentation Assessment

**Check for:**
- [ ] Is there a persistent documentation file?
- [ ] Is documentation updated incrementally during execution?
- [ ] Does documentation follow consistent structure?
- [ ] Are key decisions and rationale captured?

**Score:** ✅ Pass | ⚠️ Partial | ❌ Fail

**Findings:** [Document what exists and what's missing]

#### 3.5 Clear Summary with Examples Assessment

**Check for:**
- [ ] Is there a dedicated summary section?
- [ ] Does it include before/after comparison?
- [ ] Are concrete examples provided?
- [ ] Is impact clearly explained?
- [ ] Are usage instructions provided?

**Score:** ✅ Pass | ⚠️ Partial | ❌ Fail

**Findings:** [Document what exists and what's missing]

### Step 4: Calculate Overall Score

Use the scoring rubric from `references/workflow-validation-checklist.md`:

- **Excellent:** 5/5 Pass
- **Good:** 4/5 Pass, 1/5 Partial
- **Needs Improvement:** 3/5 or fewer Pass
- **Inadequate:** 2/5 or more Fail

### Step 5: Generate Detailed Review Report

Create a comprehensive review report with the following structure:

```markdown
# Workflow Review Report: [Workflow Name]

**File Reviewed:** [Path to workflow file]
**Review Date:** [Timestamp]
**Overall Assessment:** [Excellent | Good | Needs Improvement | Inadequate]
**Pass Rate:** [X/5 Pass, Y/5 Partial, Z/5 Fail]

---

## Executive Summary

[2-3 sentence summary of overall quality and key findings]

---

## Detailed Assessment

### 1. Prompt Refinement
**Score:** [✅ Pass | ⚠️ Partial | ❌ Fail]

**Findings:**
[What exists in the workflow]

**Issues:**
[What's missing or inadequate]

**Recommendations:**
[Specific suggestions to improve this property]

---

### 2. Human Feedback Loop
**Score:** [✅ Pass | ⚠️ Partial | ❌ Fail]

**Findings:**
[What exists in the workflow]

**Issues:**
[What's missing or inadequate]

**Critical Issues:**
- [ ] Sub-agents used without persistent coordination file
- [ ] No agent_context.md or equivalent
- [ ] Sub-agents cannot communicate with each other

**Recommendations:**
[Specific suggestions to improve this property]
[Reference: See `references/subagent-communication-template.md` for proper structure]

---

### 3. Validation Loop
**Score:** [✅ Pass | ⚠️ Partial | ❌ Fail]

**Findings:**
[What exists in the workflow]

**Issues:**
[What's missing or inadequate]

**Recommendations:**
[Specific suggestions to improve this property]

---

### 4. Persistent Documentation
**Score:** [✅ Pass | ⚠️ Partial | ❌ Fail]

**Findings:**
[What exists in the workflow]

**Issues:**
[What's missing or inadequate]

**Recommendations:**
[Specific suggestions to improve this property]

---

### 5. Clear Summary with Examples
**Score:** [✅ Pass | ⚠️ Partial | ❌ Fail]

**Findings:**
[What exists in the workflow]

**Issues:**
[What's missing or inadequate]

**Recommendations:**
[Specific suggestions to improve this property]

---

## Priority Improvements

List the most critical improvements in priority order:

1. **[High Priority]** [Issue and recommended fix]
2. **[High Priority]** [Issue and recommended fix]
3. **[Medium Priority]** [Issue and recommended fix]
4. **[Medium Priority]** [Issue and recommended fix]
5. **[Low Priority]** [Issue and recommended fix]

---

## Comparison to Best Practices

Show side-by-side comparison of current workflow vs best practices:

### Example: Current Workflow
```markdown
[Excerpt from current workflow showing problematic section]
```

### Example: Recommended Improvement
```markdown
[Improved version following best practices from references/workflow-examples.md]
```

---

## Next Steps

1. [Concrete action item to improve workflow]
2. [Concrete action item to improve workflow]
3. [Concrete action item to improve workflow]

---

## Reference Materials

For detailed guidance on improving this workflow:
- **Validation Checklist:** See `references/workflow-validation-checklist.md`
- **Sub-agent Template:** See `references/subagent-communication-template.md`
- **Good Examples:** See `references/workflow-examples.md`
```

### Step 6: Highlight Critical Issues

If the workflow uses sub-agents but lacks proper coordination:

**Flag this prominently:**
```
🚨 CRITICAL ISSUE: Sub-Agent Coordination Missing

This workflow uses sub-agents but does not implement a persistent coordination file.

**Impact:**
- Sub-agents cannot share context or findings
- No mechanism for main agent to communicate with sub-agents
- Risk of duplicated work or contradictory results
- Loss of information between sub-agent invocations

**Required Fix:**
Implement agent_context.md following the template in `references/subagent-communication-template.md`

**Location:** `.claude/workflows/[workflow-name]/agent_context.md`

This is a NON-PASSING critical issue that prevents proper agent coordination.
```

### Step 7: Provide Actionable Examples

For each failing or partial property, provide:
1. **Current state** (excerpt from workflow)
2. **Recommended improvement** (concrete example of fix)
3. **Reference** (link to relevant section in reference files)

Use examples from `references/workflow-examples.md` to illustrate good patterns.

## Quick Reference Guide

### When to Use This Skill

**Trigger Phrases:**
- "Review this workflow"
- "Audit my agent design"
- "Check workflow quality"
- "Validate this workflow"
- "Does this workflow follow best practices?"
- "Review .claude/commands/[workflow-name].md"

### What This Skill Does NOT Do

- ❌ Does not execute or run workflows
- ❌ Does not fix workflows automatically (only provides recommendations)
- ❌ Does not review non-workflow files (code, data, etc.)
- ❌ Does not create new workflows from scratch

### Output Format

Always produce a structured review report with:
1. Executive summary
2. Detailed assessment (5 properties)
3. Priority improvements list
4. Comparison examples
5. Next steps

## Resources

This skill includes reference files with detailed guidance:

### references/workflow-validation-checklist.md
Detailed validation criteria for all 5 core properties with:
- Required elements for each property
- Validation questions
- Good vs bad examples
- Scoring rubric

Load this file when performing validation to ensure comprehensive coverage.

### references/subagent-communication-template.md
Template structure for persistent markdown files used to coordinate between main agents and sub-agents.

Reference this when:
- Evaluating workflows that use sub-agents
- Providing recommendations for missing coordination
- Showing examples of proper agent coordination

Key sections:
- Request summary with refined specifications
- Main agent findings and delegation plan
- Sub-agent reports (findings, data, blockers, recommendations)
- Integration and synthesis across sub-agents
- User feedback loop
- Implementation plan, validation results, final summary

### references/workflow-examples.md
Concrete examples of complete good workflows, bad workflows, and partial implementations.

Use these examples when:
- Illustrating what good looks like
- Showing before/after improvements
- Providing concrete recommendations

Examples include:
- Complete good workflow with all 5 properties
- Bad workflow missing all properties
- Partial workflow needing improvement

## Best Practices for Using This Skill

1. **Load all reference files** before starting evaluation to ensure comprehensive assessment
2. **Be specific in findings** - quote actual sections from workflow, don't generalize
3. **Provide actionable recommendations** - concrete fixes, not vague suggestions
4. **Use examples** - show current vs improved versions side-by-side
5. **Prioritize improvements** - help user focus on most critical issues first
6. **Flag critical issues prominently** - especially missing sub-agent coordination
7. **Reference templates** - point user to specific reference files for guidance

## Example Usage

**User Request:**
"Review my workflow at .claude/commands/create-measure.md"

**Skill Response:**
1. Read .claude/commands/create-measure.md
2. Load references/workflow-validation-checklist.md
3. Evaluate against 5 core properties
4. Generate detailed review report with scores
5. Provide specific recommendations with examples
6. Flag any critical issues (e.g., missing sub-agent coordination)
7. Output actionable next steps

**Expected Output:**
Structured review report following the template in Step 5, with specific findings, scores, and recommendations tailored to the reviewed workflow.
