# Workflow Examples

Complete examples of well-designed agentic workflows implementing all 5 core principles.

## Example 1: Single-Agent Workflow

### `/validate-code-quality`

Simple workflow with one autonomous agent performing multi-step validation.

```markdown
# Slash Command: validate-code-quality.md

**Purpose:** Validate code quality using linting, type checking, and security scanning.

**Parameters:**
- `--project` (required): Path to project folder
- `--language` (required): Programming language (python, javascript, typescript)

**Workflow:**

## Phase 1: Prompt Refinement

Clarify validation scope:

**Goals:**
- Run linting checks
- Perform type checking
- Execute security vulnerability scan

**Constraints:**
- Use language-specific tools (pylint for Python, eslint for JS)
- Report only errors and warnings, not info-level messages

**Desired Outputs:**
- validation_report.md with findings
- Pass/fail verdict

## Phase 2: Invoke Validator Agent

Uses `code-quality-validator` agent to:
- Run linting tools
- Execute type checkers
- Scan for security issues
- Generate structured report

## Phase 3: Present Results

Display validation report with:
- Summary of issues found
- Breakdown by category (linting, types, security)
- Recommendations for fixes
- Pass/fail verdict based on error count

**Agent Involved:**
- `code-quality-validator` - Executes all validation checks
```

**Agent File: code-quality-validator.md**

```markdown
# Code Quality Validator Agent

**Purpose:** Execute comprehensive code quality checks.

**Inputs:**
- Project path
- Language
- Validation report file path

**Process:**

## Step 1: Detect Language-Specific Tools

Based on language parameter:
- Python: pylint, mypy, bandit
- JavaScript: eslint, flow
- TypeScript: eslint, tsc

## Step 2: Run Validation Checks

Execute each tool and capture output:

1. **Linting:** Check code style and best practices
2. **Type Checking:** Verify type correctness
3. **Security:** Scan for vulnerabilities

## Step 3: Parse Results

Extract:
- Error count by category
- Warning count by category
- File-level breakdown

## Step 4: Generate Report

Document in validation_report.md:

### Validation Summary

**Status:** [PASS | FAIL]
**Total Errors:** [N]
**Total Warnings:** [M]

### Linting Results
- [Error/warning details]

### Type Checking Results
- [Error/warning details]

### Security Scan Results
- [Vulnerability details]

### Recommendations
1. [Fix priority 1]
2. [Fix priority 2]

## Step 5: Validation Loop

If errors found:
- Document in report
- Provide remediation guidance
- User can fix and re-run

**Output:** validation_report.md with all findings
```

---

## Example 2: Multi-Agent Sequential Workflow

### `/create-feature-documentation`

Workflow with multiple agents executing in sequence to create comprehensive documentation.

```markdown
# Slash Command: create-feature-documentation.md

**Purpose:** Generate comprehensive feature documentation by analyzing code, extracting patterns, and creating user guides.

**Parameters:**
- `--project` (required): Path to project folder
- `--feature` (required): Feature name or module to document

**Workflow:**

## Phase 1: Prompt Refinement

**Goals:**
- Analyze feature code and understand functionality
- Extract API contracts and usage patterns
- Generate user-facing documentation

**Constraints:**
- Documentation must be accurate to actual code behavior
- Include code examples from actual usage
- Follow project's documentation style guide

**Desired Outputs:**
- feature_documentation.md with complete user guide
- api_reference.md with API details
- examples/ folder with code samples

## Phase 2: Create Coordination File

Initialize `agent_scratchpads/[timestamp]-doc-[feature]/coordination.md`:

Serves as persistent communication channel between:
- Code analyzer agent
- Pattern extractor agent
- Documentation writer agent

## Phase 3: Invoke Code Analyzer Agent

Uses `feature-code-analyzer` to:
- Scan codebase for feature implementation
- Extract function signatures and parameters
- Identify public API surface
- Document in Section 1 of coordination.md

## Phase 4: Invoke Pattern Extractor Agent

Uses `feature-pattern-extractor` to:
- Find usage examples in tests and existing code
- Extract common patterns
- Identify edge cases and error handling
- Document in Section 2 of coordination.md

## Phase 5: Human Feedback Loop

Present findings from agents and ask:

**Recommended Documentation Structure:**
- **Getting Started** - Basic usage with simple example
- **API Reference** - Complete function/class documentation
- **Advanced Patterns** - Complex usage scenarios
- **Troubleshooting** - Common issues and solutions

Confirm structure or request modifications.

## Phase 6: Invoke Documentation Writer Agent

Uses `feature-documentation-writer` to:
- Read Sections 1 & 2 from coordination.md
- Generate documentation following approved structure
- Include code examples from pattern analysis
- Document in Section 3 of coordination.md

## Phase 7: Validation Loop

Review generated documentation for:
1. **Accuracy:** Matches actual code behavior
2. **Completeness:** Covers all public APIs
3. **Clarity:** Examples are understandable
4. **Style:** Follows project guidelines

If validation fails, iterate with documentation writer.

## Phase 8: Summary

**Before:**
- Feature existed but lacked documentation
- Developers had to read code to understand usage

**After:**
- Comprehensive user guide with examples
- API reference with all functions documented
- Common patterns and troubleshooting guide

**Files Created:**
- `docs/features/[feature].md` - User guide
- `docs/api/[feature].md` - API reference
- `docs/examples/[feature]/` - Code samples

**Agents Involved:**
1. `feature-code-analyzer` - Analyzes implementation
2. `feature-pattern-extractor` - Finds usage patterns
3. `feature-documentation-writer` - Generates documentation
```

**Coordination File Template:**

```markdown
# Feature Documentation Coordination

**Feature:** [Feature Name]
**Started:** [Timestamp]
**Status:** In Progress

---

## 1. Request Summary

**Original Request:** Generate documentation for [feature]

**Refined Specifications:**
- Goals: Comprehensive user guide and API reference
- Constraints: Must reflect actual code behavior
- Desired Outputs: feature_documentation.md, api_reference.md, examples/

---

## 2. Main Agent Delegation Plan

- Agent 1 (Code Analyzer): Extract API surface and signatures
- Agent 2 (Pattern Extractor): Find usage examples
- Agent 3 (Documentation Writer): Generate final documentation

---

## 3. Sub-Agent Reports

### Agent: Code Analyzer
**Status:** Completed
**Findings:**
- Public Functions: [list with signatures]
- Classes: [list with methods]
- Configuration Options: [list]

### Agent: Pattern Extractor
**Status:** Completed
**Findings:**
- Usage Example 1: [code snippet]
- Usage Example 2: [code snippet]
- Common Error Handling: [pattern]

### Agent: Documentation Writer
**Status:** In Progress
**Output:** Generating documentation from Sections 1 & 2

---

## 4. Integration & Synthesis

Combined code analysis + patterns to create:
- Getting started guide with simple example
- Comprehensive API reference
- Advanced usage section with complex patterns

---

## 5. User Feedback Loop

**Question:** Approve documentation structure?
- Getting Started / API Reference / Advanced Patterns / Troubleshooting

**Response:** Approved

---

## 6. Validation Results

**Accuracy Check:** PASS - Verified against code
**Completeness Check:** PASS - All public APIs covered
**Style Check:** PASS - Follows project guidelines

---

## 7. Final Summary

**What Was Done:**
Created comprehensive documentation for [feature] including user guide, API reference, and examples.

**Before:**
- No documentation
- Developers reading source code

**After:**
- Complete user guide with examples
- API reference for all functions
- Troubleshooting guide

**Files Created:**
- docs/features/[feature].md
- docs/api/[feature].md
- docs/examples/[feature]/example1.py
```

---

## Example 3: Multi-Agent Parallel + Sequential Workflow

### `/deploy-and-test-application`

Complex workflow with parallel agent execution followed by sequential validation.

```markdown
# Slash Command: deploy-and-test-application.md

**Purpose:** Deploy application to target environment and run comprehensive test suite.

**Parameters:**
- `--project` (required): Path to project folder
- `--environment` (required): Target environment (dev, staging, prod)
- `--run-tests` (optional): Whether to run tests after deployment

**Workflow:**

## Phase 1: Prompt Refinement

**Goals:**
- Build and package application
- Deploy to target environment
- Run test suite and validate deployment

**Constraints:**
- Must pass build checks before deployment
- Must validate configuration for target environment
- Tests must pass before marking deployment successful

**Desired Outputs:**
- Deployed application URL
- Test results report
- Deployment status (success/failure)

## Phase 2: Create Coordination File

Initialize `agent_scratchpads/[timestamp]-deploy-[env]/deployment_coordination.md`

## Phase 3: Parallel Pre-Deployment Checks

Invoke TWO agents in PARALLEL:

**Agent 1: Build Validator**
- Verify dependencies are installed
- Run build process
- Validate build artifacts

**Agent 2: Configuration Validator**
- Check environment-specific config
- Validate secrets and credentials
- Verify target environment availability

Both agents write findings to Sections 1 & 2 of coordination.md

## Phase 4: Human Feedback Loop

If validation warnings found, present to user:

**Build Validation Warnings:**
- [Any warnings from build process]

**Configuration Issues:**
- [Any configuration warnings]

**Recommendation:** Proceed with deployment?
- Yes (warnings acceptable)
- No (fix issues first)

## Phase 5: Deploy Application

Uses `application-deployer` agent to:
- Package build artifacts
- Deploy to target environment
- Verify deployment health
- Capture deployment URL

Document in Section 3 of coordination.md

## Phase 6: Validation Loop - Deployment Health

Check deployment health:
1. **Service Availability:** Application responding
2. **Health Endpoints:** /health returns 200
3. **Database Connectivity:** Can connect to database

If any check fails:
- Document failure
- Rollback deployment
- Report error to user

## Phase 7: Run Test Suite (Optional)

If `--run-tests` specified, use `test-runner` agent to:
- Execute integration tests against deployed app
- Execute smoke tests
- Validate critical user flows

Document results in Section 4 of coordination.md

## Phase 8: Summary

**Before:**
- Application version [X] in [environment]

**After:**
- Application version [Y] deployed to [environment]
- Deployment URL: [URL]
- Health checks: PASS
- Test results: [N passed, M failed]

**Outcome:**
[SUCCESS | FAILED] - [Summary of deployment status]

**Agents Involved:**
1. `build-validator` (parallel) - Validates build
2. `configuration-validator` (parallel) - Validates config
3. `application-deployer` (sequential) - Executes deployment
4. `test-runner` (sequential, optional) - Runs tests

**Human-in-the-Loop Decisions:**
- Approval to proceed with deployment despite warnings
- Decision to rollback if tests fail
```

---

## Key Patterns Demonstrated

### Pattern 1: Progressive Refinement
All workflows start with prompt refinement phase to clarify goals, constraints, and outputs.

### Pattern 2: Persistent Coordination
Multi-agent workflows use coordination files as single source of truth.

### Pattern 3: Parallel + Sequential Orchestration
Complex workflows run independent agents in parallel, then sequence dependent agents.

### Pattern 4: Explicit Validation Loops
Every workflow includes validation with iteration capability.

### Pattern 5: Incremental Documentation
Agents update coordination file after each phase, creating audit trail.

### Pattern 6: Concrete Summaries
Final summaries show before/after state with concrete examples, not abstract descriptions.
