---
name: power-bi-assistant
description: This skill should be used when users need guidance navigating Power BI workflows and commands. Use when users ask for help with Power BI, need to choose the right workflow, want to understand command parameters, need step-by-step guidance for evaluate/create/implement/merge workflows, or ask about plugin version/updates/edition. Helps users prepare command inputs, understand multi-step sequences, check for updates, and follow best practices.
---

# Power BI Assistant

## Overview

Interactive guide and helper for Power BI development workflows. Assists users in selecting the appropriate workflow command, preparing command parameters, understanding multi-step sequences, and following best practices from the Power BI Analyst Agent system.

## When to Use This Skill

Invoke this skill when users:
- Ask general questions about Power BI workflows ("How do I fix a measure?", "Help with Power BI")
- Need guidance choosing between evaluate/create/implement/merge commands
- Want to understand what parameters to provide for commands
- Need help preparing command inputs (project paths, problem descriptions)
- Ask about multi-step workflow sequences
- Request best practices for Power BI development
- Express uncertainty about next steps ("What should I do now?")
- Ask about plugin version, updates, or edition ("What version?", "Check for updates", "Am I on Pro?")

## Core Capabilities

### 1. Workflow Navigation & Command Selection

Guide users to the correct command based on their stated intent.

**Decision Framework:**

**User has a problem with existing code** → `/evaluate-pbi-project-file`
- Symptoms: "broken", "incorrect", "wrong", "fix", "debug", "issue"
- Applies to: Calculation problems, visual issues, hybrid changes

**User wants to create something new** → `/create-pbi-artifact`
- Symptoms: "create", "add", "build", "new measure/column/table/visual"
- Applies to: Net-new artifacts with specification guidance

**User has a plan and wants to apply it** → `/implement-deploy-test-pbi-project-file`
- Symptoms: "apply changes", "implement", "deploy", "execute findings"
- Prerequisites: Must have findings.md from previous workflow

**User wants to compare/merge projects** → `/merge-powerbi-projects`
- Symptoms: "compare", "merge", "sync", "combine", "differences"
- Applies to: Merging dev/prod, adopting selective changes

**User asks about plugin version/updates** → VERSION_CHECK workflow
- Symptoms: "version", "update", "latest", "check for updates", "am I on Pro", "what edition"
- Applies to: Plugin itself, not Power BI projects
- Reports: Plugin version, edition (Pro/Core), project version, update instructions

**Process:**
1. Analyze user's statement for intent keywords
2. Match to workflow decision tree (see `references/workflow-decision-tree.md`)
3. Present recommended command with rationale
4. Offer to help prepare parameters

**For vague requests:**
- Ask clarifying questions: "Are you trying to fix something or create something new?"
- Present options: "I can help you with [A], [B], or [C]. Which applies?"
- Default to `/evaluate-pbi-project-file` for investigation

---

### 2. Command Parameter Preparation

Help users gather and format all required parameters for their chosen command.

**Interactive Preparation Process:**

**Step 1: Identify required parameters**
- Load parameter requirements from `references/command-parameters.md`
- Present checklist of required vs. optional parameters

**Step 2: Gather information**
- Ask for each required parameter systematically
- Provide examples and format guidance
- Validate user responses

**Step 3: Build command**
- Construct complete command with proper syntax
- Show final command for user confirmation
- Explain what each parameter does

**Example for `/evaluate-pbi-project-file`:**

Guide through parameter collection:
1. Project path → validate absolute path format
2. Problem description → ensure specificity
3. Optional workspace/dataset → explain benefits
4. Build and present final command

Refer to `references/command-parameters.md` for detailed parameter guidance for all commands.

---

### 3. Multi-Step Workflow Guidance

Walk users through complete end-to-end workflows with clear checkpoints.

Load detailed workflow documentation from `references/multi-step-workflows.md` and guide users through:

1. **Analyze → Implement → Deploy → Test** (for fixes)
2. **Create → Implement → Deploy → Test** (for new artifacts)
3. **Compare → Decide → Merge** (for project merging)

**Guidance Approach:**

Before starting: Explain complete sequence, identify checkpoints, set expectations.

During execution: Announce steps, explain actions, indicate when user input needed.

At checkpoints: Prompt review, highlight what to look for, explain implications.

---

### 4. Best Practices Integration

Provide context-aware best practices from `references/best-practices.md`.

**When to apply:**
- After command selection: Recommend workspace/dataset parameters
- During path gathering: Validate absolute paths, proper quoting
- Before execution: Remind about validation gates, testing importance
- At checkpoints: Highlight what to review in findings files

**Key best practices to emphasize:**
- Always provide workspace/dataset for better recommendations
- Use absolute paths with proper quoting for spaces
- Review findings files before proceeding to implementation
- Never skip validation gates (TMDL, PBIR, DAX)
- Test in development before production deployment

---

## How to Use This Skill

### For General "Help with Power BI" Requests

1. Determine user's goal through clarifying questions
2. Match to appropriate workflow using decision tree
3. Explain what the workflow does and expected output
4. Offer to guide through parameter preparation
5. Present complete command ready to execute
6. Explain next steps after command completes

### For Workflow Navigation Questions

1. Load `references/workflow-decision-tree.md`
2. Present decision framework based on user's scenario
3. Explain rationale for recommendation
4. Show example command for chosen workflow
5. Offer to help with parameter preparation

### For Parameter Help

1. Load `references/command-parameters.md`
2. Present checklist of required/optional parameters
3. Gather information systematically
4. Validate inputs (paths, format, completeness)
5. Build complete command
6. Confirm with user before execution

### For Multi-Step Guidance

1. Load `references/multi-step-workflows.md`
2. Explain complete workflow sequence upfront
3. Guide through each step with clear announcements
4. Pause at checkpoints for user review
5. Explain what to look for at each checkpoint
6. Provide next-step recommendations

---

## References

This skill includes reference documentation for comprehensive guidance:

### `references/workflow-decision-tree.md`
Decision framework mapping user intents to commands, common scenarios, and when to use each workflow.

### `references/command-parameters.md`
Detailed parameter reference for all commands including required/optional parameters, format examples, and validation guidance.

### `references/multi-step-workflows.md`
Complete end-to-end workflow sequences with checkpoints, timing estimates, and troubleshooting guidance.

### `references/best-practices.md`
Best practices for command selection, parameter preparation, workflow execution, testing, and deployment extracted from project documentation.