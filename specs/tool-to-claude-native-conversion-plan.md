# Plan: Convert Python Tools to Claude-Native Reference Documents

## Objective

Apply the established pattern (used for `m_pattern_analyzer.py` → `m_pattern_discovery.md`) to all remaining convertible tools, enabling Analyst Edition to work without Python.

---

## Tool Conversion Matrix

| Tool | Current Fallback Status | Action Required | Priority |
|------|------------------------|-----------------|----------|
| `m_pattern_analyzer.py` | ✅ DONE | Already converted | Complete |
| `query_folding_validator.py` | ✅ Good reference exists | Add detection rules to `query_folding_guide.md` | P1 |
| `sensitive_column_detector.py` | ✅ Good reference exists | Add detection rules to `anonymization-patterns.md` | P1 |
| `tmdl_format_validator.py` | ✅ Good reference exists | Add validation rules to `tmdl_partition_structure.md` | P2 |
| `pbi_project_validator.py` | ⚠️ No reference doc | Create `project_structure_validation.md` | P2 |
| `pbi_merger_utils.py` | ⚠️ No reference doc | Create `project_comparison_guide.md` | P3 |
| `extract_visual_layout.py` | ⚠️ No reference doc | Create `pbir_visual_structure.md` | P3 |

### Pro-Only (No Conversion Needed)

| Tool | Reason |
|------|--------|
| `pbir_visual_editor.py` | User confirmed Developer-only |
| `agent_logger.py` | Analytics (Developer-only) |
| `analytics_merger.py` | Analytics (Developer-only) |
| `token_analyzer.py` | Analytics (Developer-only) |

### Already MCP-Preferred

| Tool | MCP Alternative | Fallback Doc |
|------|-----------------|--------------|
| `tmdl_measure_replacer.py` | `measure_operations.update()` | MCP first, Edit tool fallback |
| `m_partition_editor.py` | `partition_operations` | MCP first, Edit tool fallback |
| `anonymization_generator.py` | Manual M code generation | `anonymization-patterns.md` templates |

---

## Conversion Pattern (Template)

For each tool, follow this pattern established with `m_pattern_discovery.md`:

### 1. Read the Python Tool
- Extract detection/validation logic
- Identify regex patterns, classification rules, categorization logic

### 2. Enhance Reference Document
Structure the reference doc with:
```markdown
# [Topic] Guide

## Quick Reference
| Edition | Method |
|---------|--------|
| **Pro** | Run `tool_name.py` |
| **Core** | Follow detection rules below |

## Part 1: Detection Rules (Claude-Native)
[Step-by-step instructions extracted from Python tool]
- What to search for (Grep patterns)
- How to classify results
- How to generate report

## Part 2: Application Rules
[How to apply detected patterns]

## Part 3: Checklist
[Verification before completing]
```

### 3. Update Agent
- Add reference document link to Core fallback section
- Specify which Part to follow

### 4. Update tool-fallback-pattern.md
- Update the mapping row with specific reference doc part

---

## Priority 1: Enhance Existing References

### 1A. query_folding_guide.md Enhancement

**Python tool:** `query_folding_validator.py` (316 lines)

**Key logic to extract:**
```python
FOLDING_BREAKERS = {
    'Table.AddColumn': 'Adding custom columns breaks query folding',
    'Text.Start': 'Text operations break query folding',
    # ... 20+ patterns
}
FOLDING_PRESERVERS = {
    'Table.SelectRows': 'Row filtering preserves query folding',
    # ... 15+ patterns
}
FOLDING_MAYBE = {
    'Table.TransformColumns': 'May break folding depending on transform',
    # ...
}
```

**Changes to reference doc:**
1. Add "Part 1: Folding Analysis (Claude-Native)" section
2. Include complete operation categorization tables from Python
3. Add Grep patterns for scanning M code
4. Add percentage-based folding score calculation

**Agent to update:** `powerbi-mcode-specialist.md`

---

### 1B. anonymization-patterns.md Enhancement

**Python tool:** `sensitive_column_detector.py` (detailed pattern matching)

**Key logic to extract:**
- 100+ regex patterns for PII detection
- Column name patterns: names, emails, SSN, phones, addresses
- Data type associations
- Confidence scoring

**Changes to reference doc:**
1. Add "Part 1: Sensitive Column Detection (Claude-Native)" section
2. Include regex pattern table from Python
3. Add Grep commands for scanning TMDL
4. Add confidence scoring rules

**Agent to update:** `powerbi-anonymization-setup.md`

---

## Priority 2: Enhance + Create References

### 2A. tmdl_partition_structure.md Enhancement

**Python tool:** `tmdl_format_validator.py` (838 lines, 13 error codes)

**Key logic to extract:**
- TMDL001-TMDL013 error code definitions
- Indentation validation rules
- Property placement validation
- DAX block boundary detection

**Changes to reference doc:**
1. Add "Part 1: Format Validation (Claude-Native)" section
2. Include all 13 error codes with detection patterns
3. Add line-by-line validation procedure
4. Add auto-fix recommendations

**Agent to update:** `implement-deploy-test-pbi-project-file.md`

---

### 2B. CREATE: project_structure_validation.md

**Python tool:** `pbi_project_validator.py` (671 lines)

**New reference doc content:**
```markdown
# Project Structure Validation

## Part 1: Format Detection (Claude-Native)

### Step 1: Detect Project Format
Search for these indicators:
| File/Folder | Format |
|-------------|--------|
| `*.pbip` file | PBIP (Power BI Project) |
| `.pbi/` folder | pbi-tools format |
| `*.pbix` file only | PBIX (not supported) |

### Step 2: Validate Required Files
[Glob patterns for each format type]

### Step 3: Path Length Check
[Windows 260 char limit validation]

## Part 2: Validation Report Format
[Template for reporting issues]
```

**Agent to update:** `qa-loop-pbi-dashboard.md` (or create new validator agent)

---

## Priority 3: Create New References

### 3A. CREATE: project_comparison_guide.md

**Python tool:** `pbi_merger_utils.py`

**New reference doc content:**
- TMDL parsing instructions for Claude
- Measure/column extraction patterns
- Comparison logic (what constitutes same/different)
- Merge decision framework

**Agent to update:** `powerbi-compare-project-code.md`

---

### 3B. CREATE: pbir_visual_structure.md

**Python tool:** `extract_visual_layout.py`

**New reference doc content:**
- visual.json schema documentation
- Page structure hierarchy
- Property extraction patterns
- Layout coordinate system explanation

**Agent to update:** Various visual-related agents

---

## Files to Modify

### Reference Documents (in skills/pbi-squire/references/)

| File | Action |
|------|--------|
| `query_folding_guide.md` | Enhance: Add Part 1 detection rules |
| `anonymization-patterns.md` | Enhance: Add Part 1 detection rules |
| `tmdl_partition_structure.md` | Enhance: Add Part 1 validation rules |
| `project_structure_validation.md` | CREATE new |
| `project_comparison_guide.md` | CREATE new |
| `pbir_visual_structure.md` | CREATE new |
| `tool-fallback-pattern.md` | Update all mappings with specific parts |

### Agents (in skills/pbi-squire/agents/)

| File | Action |
|------|--------|
| `powerbi-mcode-specialist.md` | Update Core fallback to reference doc |
| `powerbi-anonymization-setup.md` | Update Core fallback to reference doc |
| `powerbi-compare-project-code.md` | Update Core fallback to reference doc |
| Workflow files using validators | Update Core fallback sections |

---

## Implementation Order

```
Phase 1 (P1) - Enhance existing well-documented references
├── 1A. query_folding_guide.md + agent update
└── 1B. anonymization-patterns.md + agent update

Phase 2 (P2) - Enhance + create validation references
├── 2A. tmdl_partition_structure.md + agent update
└── 2B. CREATE project_structure_validation.md + agent update

Phase 3 (P3) - Create remaining references
├── 3A. CREATE project_comparison_guide.md + agent update
└── 3B. CREATE pbir_visual_structure.md + agent update

Phase 4 - Final updates
├── Update tool-fallback-pattern.md with all mappings
├── Update SKILL.md if needed
└── Test Analyst Edition workflows
```

---

## Detailed Implementation Plan

### Phase 1A: Query Folding Guide Enhancement

**Goal:** Convert `query_folding_validator.py` logic to `query_folding_guide.md`

#### Step 1: Extract Python Logic
```
Read: tools/developer/query_folding_validator.py
Extract:
- FOLDING_BREAKERS dict (operations that break folding)
- FOLDING_PRESERVERS dict (operations that preserve folding)
- FOLDING_MAYBE dict (context-dependent operations)
- Score calculation logic
- Report generation format
```

#### Step 2: Enhance Reference Document
```
Edit: skills/pbi-squire/references/query_folding_guide.md

Add sections:
1. Quick Reference table (Pro vs Core methods)
2. Part 1: Folding Analysis (Claude-Native)
   - Step 1: Scan M code files (Glob pattern: **/definition.m)
   - Step 2: Identify operations (Grep patterns for each category)
   - Step 3: Classify each operation (tables from Python)
   - Step 4: Calculate folding score (formula)
   - Step 5: Generate report (template)
```

#### Step 3: Update Agent
```
Edit: skills/pbi-squire/agents/powerbi-mcode-specialist.md

Add to Core fallback section:
- Reference: query_folding_guide.md → Part 1
- When to use: Query folding analysis without Python
```

#### Step 4: Update Fallback Pattern
```
Edit: skills/pbi-squire/references/tool-fallback-pattern.md

Update row:
| query_folding_validator.py | query_folding_guide.md | Part 1: Folding Analysis |
```

---

### Phase 1B: Anonymization Patterns Enhancement

**Goal:** Convert `sensitive_column_detector.py` logic to `anonymization-patterns.md`

#### Step 1: Extract Python Logic
```
Read: tools/developer/sensitive_column_detector.py
Extract:
- PII_PATTERNS dict (regex patterns by category)
- Column name patterns (names, emails, SSN, phones, addresses)
- Data type associations
- Confidence scoring algorithm
- Report format
```

#### Step 2: Enhance Reference Document
```
Edit: skills/pbi-squire/references/anonymization-patterns.md

Add sections:
1. Quick Reference table (Pro vs Core methods)
2. Part 1: Sensitive Column Detection (Claude-Native)
   - Step 1: Scan TMDL files (Glob pattern: **/*.tmdl)
   - Step 2: Extract column definitions (Grep for "column")
   - Step 3: Match against PII patterns (pattern table)
   - Step 4: Assign confidence scores (scoring rules)
   - Step 5: Generate detection report (template)
```

#### Step 3: Update Agent
```
Edit: skills/pbi-squire/agents/powerbi-anonymization-setup.md

Add to Core fallback section:
- Reference: anonymization-patterns.md → Part 1
- When to use: Sensitive column detection without Python
```

#### Step 4: Update Fallback Pattern
```
Edit: skills/pbi-squire/references/tool-fallback-pattern.md

Update row:
| sensitive_column_detector.py | anonymization-patterns.md | Part 1: Detection |
```

---

### Phase 2A: TMDL Partition Structure Enhancement

**Goal:** Convert `tmdl_format_validator.py` logic to `tmdl_partition_structure.md`

#### Step 1: Extract Python Logic
```
Read: tools/developer/tmdl_format_validator.py
Extract:
- Error codes TMDL001-TMDL013 with descriptions
- Indentation rules (tabs vs spaces, nesting levels)
- Property placement rules
- DAX block boundary patterns (```)
- Auto-fix recommendations per error code
```

#### Step 2: Enhance Reference Document
```
Edit: skills/pbi-squire/references/tmdl_partition_structure.md

Add sections:
1. Quick Reference table (Pro vs Core methods)
2. Part 1: Format Validation (Claude-Native)
   - Step 1: Read TMDL file
   - Step 2: Check indentation (rules table)
   - Step 3: Validate property placement (rules table)
   - Step 4: Check DAX block boundaries
   - Step 5: Report errors with codes (TMDL001-013 table)
   - Step 6: Suggest fixes (fix recommendations table)
```

#### Step 3: Update Agent/Workflow
```
Edit: skills/pbi-squire/workflows/implement-deploy-test-pbi-project-file.md

Add to Core fallback section:
- Reference: tmdl_partition_structure.md → Part 1
- When to use: TMDL validation without Python
```

#### Step 4: Update Fallback Pattern
```
Edit: skills/pbi-squire/references/tool-fallback-pattern.md

Update row:
| tmdl_format_validator.py | tmdl_partition_structure.md | Part 1: Validation |
```

---

### Phase 2B: Create Project Structure Validation

**Goal:** Create new `project_structure_validation.md` from `pbi_project_validator.py`

#### Step 1: Extract Python Logic
```
Read: tools/developer/pbi_project_validator.py
Extract:
- Format detection logic (PBIP vs pbi-tools vs PBIX)
- Required files per format
- Path length validation (260 char limit)
- Encoding checks
- Common error patterns
```

#### Step 2: Create New Reference Document
```
Create: skills/pbi-squire/references/project_structure_validation.md

Structure:
# Project Structure Validation

## Quick Reference
| Edition | Method |
|---------|--------|
| **Pro** | Run `pbi_project_validator.py` |
| **Core** | Follow detection rules below |

## Part 1: Format Detection (Claude-Native)
### Step 1: Detect Project Format
[Glob patterns and indicators]

### Step 2: Validate Required Files
[Checklist per format type]

### Step 3: Path Length Check
[260 char validation procedure]

### Step 4: Encoding Validation
[UTF-8 BOM checks]

## Part 2: Validation Report Format
[Template for reporting issues]

## Part 3: Common Issues Checklist
[Quick fixes for common problems]
```

#### Step 3: Update Agent/Workflow
```
Edit: skills/pbi-squire/workflows/qa-loop-pbi-dashboard.md (or relevant workflow)

Add Core fallback section:
- Reference: project_structure_validation.md → Part 1
```

#### Step 4: Update Fallback Pattern
```
Edit: skills/pbi-squire/references/tool-fallback-pattern.md

Add row:
| pbi_project_validator.py | project_structure_validation.md | Part 1: Detection |
```

---

### Phase 3A: Create Project Comparison Guide

**Goal:** Create new `project_comparison_guide.md` from `pbi_merger_utils.py`

#### Step 1: Extract Python Logic
```
Read: tools/developer/pbi_merger_utils.py
Extract:
- TMDL parsing patterns
- Measure extraction logic
- Column extraction logic
- Comparison algorithms (same/different/modified)
- Merge decision rules
```

#### Step 2: Create New Reference Document
```
Create: skills/pbi-squire/references/project_comparison_guide.md

Structure:
# Project Comparison Guide

## Quick Reference
| Edition | Method |
|---------|--------|
| **Pro** | Run `pbi_merger_utils.py` |
| **Core** | Follow comparison rules below |

## Part 1: Project Comparison (Claude-Native)
### Step 1: Enumerate Objects
[Glob patterns for measures, columns, tables]

### Step 2: Extract Definitions
[Read patterns for each object type]

### Step 3: Compare Objects
[Comparison logic: name match, definition match]

### Step 4: Classify Differences
[Categories: added, removed, modified, unchanged]

## Part 2: Merge Decision Framework
[When to accept source vs target]

## Part 3: Comparison Report Format
[Template for diff output]
```

#### Step 3: Update Agent
```
Edit: skills/pbi-squire/agents/powerbi-compare-project-code.md

Add Core fallback section:
- Reference: project_comparison_guide.md → Part 1
```

#### Step 4: Update Fallback Pattern
```
Edit: skills/pbi-squire/references/tool-fallback-pattern.md

Add row:
| pbi_merger_utils.py | project_comparison_guide.md | Part 1: Comparison |
```

---

### Phase 3B: Create PBIR Visual Structure

**Goal:** Create new `pbir_visual_structure.md` from `extract_visual_layout.py`

#### Step 1: Extract Python Logic
```
Read: tools/developer/extract_visual_layout.py
Extract:
- visual.json schema
- Page hierarchy structure
- Property extraction patterns
- Coordinate system (x, y, width, height)
- Visual type mappings
```

#### Step 2: Create New Reference Document
```
Create: skills/pbi-squire/references/pbir_visual_structure.md

Structure:
# PBIR Visual Structure

## Quick Reference
| Edition | Method |
|---------|--------|
| **Pro** | Run `extract_visual_layout.py` |
| **Core** | Follow extraction rules below |

## Part 1: Visual Layout Extraction (Claude-Native)
### Step 1: Locate Visual Files
[Glob pattern: **/definition/pages/*/visuals/*/visual.json]

### Step 2: Parse Visual JSON
[Key properties to extract]

### Step 3: Extract Layout Coordinates
[x, y, width, height interpretation]

### Step 4: Map Visual Types
[Visual type code → human name]

## Part 2: Page Structure
[How pages and visuals are organized]

## Part 3: Layout Report Format
[Template for visual inventory]
```

#### Step 3: Update Agents
```
Edit: Relevant visual-related agents

Add Core fallback section:
- Reference: pbir_visual_structure.md → Part 1
```

#### Step 4: Update Fallback Pattern
```
Edit: skills/pbi-squire/references/tool-fallback-pattern.md

Add row:
| extract_visual_layout.py | pbir_visual_structure.md | Part 1: Extraction |
```

---

### Phase 4: Final Updates

#### Step 1: Consolidate tool-fallback-pattern.md
```
Edit: skills/pbi-squire/references/tool-fallback-pattern.md

Verify all mappings are complete:
| Tool | Reference Doc | Part |
|------|---------------|------|
| m_pattern_analyzer.py | m_pattern_discovery.md | Part 1 |
| query_folding_validator.py | query_folding_guide.md | Part 1 |
| sensitive_column_detector.py | anonymization-patterns.md | Part 1 |
| tmdl_format_validator.py | tmdl_partition_structure.md | Part 1 |
| pbi_project_validator.py | project_structure_validation.md | Part 1 |
| pbi_merger_utils.py | project_comparison_guide.md | Part 1 |
| extract_visual_layout.py | pbir_visual_structure.md | Part 1 |
```

#### Step 2: Update SKILL.md (if needed)
```
Edit: skills/pbi-squire/SKILL.md

If any new references are user-facing, add to References section
```

#### Step 3: Test Analyst Edition Workflows
```
Test procedure:
1. Remove .claude/tools/ folder (simulate Analyst Edition)
2. Run each workflow that uses converted tools
3. Verify Claude follows reference doc Part 1
4. Compare output quality to Developer Edition
```

---

## Implementation Prompts

Use these prompts to execute each phase:

### Phase 1A Prompt
```
Read tools/developer/query_folding_validator.py and extract:
1. All FOLDING_BREAKERS patterns with descriptions
2. All FOLDING_PRESERVERS patterns with descriptions
3. All FOLDING_MAYBE patterns with descriptions
4. The score calculation logic
5. The report format

Then enhance skills/pbi-squire/references/query_folding_guide.md by adding
a "Part 1: Folding Analysis (Claude-Native)" section with step-by-step
instructions for Claude to perform the same analysis using Grep/Read tools.
```

### Phase 1B Prompt
```
Read tools/developer/sensitive_column_detector.py and extract all PII detection
patterns, confidence scoring rules, and report format.

Then enhance skills/pbi-squire/references/anonymization-patterns.md by
adding a "Part 1: Sensitive Column Detection (Claude-Native)" section.
```

### Phase 2A Prompt
```
Read tools/developer/tmdl_format_validator.py and extract all error codes
(TMDL001-TMDL013), validation rules, and auto-fix recommendations.

Then enhance skills/pbi-squire/references/tmdl_partition_structure.md by
adding a "Part 1: Format Validation (Claude-Native)" section.
```

### Phase 2B Prompt
```
Read tools/developer/pbi_project_validator.py and extract format detection logic,
required files per format, and validation rules.

Then create skills/pbi-squire/references/project_structure_validation.md
following the template in the conversion plan spec.
```

### Phase 3A Prompt
```
Read tools/developer/pbi_merger_utils.py and extract TMDL parsing patterns,
comparison algorithms, and merge decision rules.

Then create skills/pbi-squire/references/project_comparison_guide.md
following the template in the conversion plan spec.
```

### Phase 3B Prompt
```
Read tools/developer/extract_visual_layout.py and extract visual.json schema,
coordinate system, and visual type mappings.

Then create skills/pbi-squire/references/pbir_visual_structure.md
following the template in the conversion plan spec.
```

---

## Verification

### For Each Converted Tool:

1. **Reference doc check:**
   - Part 1 contains step-by-step Claude-native detection/validation
   - Grep/Glob patterns are specified
   - Report format is documented

2. **Agent check:**
   - Core fallback section references the doc
   - Specific Part is mentioned
   - Tool availability check remains for Pro

3. **Functional test:**
   - Run workflow without Python installed
   - Verify Claude-native analysis produces similar results
   - Check that tool-first-fallback pattern works

### End-to-End Test:

1. Fresh project without `.claude/tools/` folder
2. Run each workflow that uses a converted tool
3. Verify Claude loads reference doc and follows detection rules
4. Compare output quality to Python tool output

---

## Success Criteria

- [x] All P1 and P2 tools have Claude-native fallback documented
- [x] Each reference doc has "Part 1: Detection/Validation (Claude-Native)" section
- [x] Each agent using these tools has updated Core fallback section
- [x] `tool-fallback-pattern.md` mappings point to specific reference doc parts
- [ ] Analyst Edition workflows function without Python (requires testing)

### Implementation Status

| Phase | Status | Files Modified/Created |
|-------|--------|------------------------|
| 1A | ✅ Complete | `query_folding_guide.md` enhanced |
| 1B | ✅ Complete | `anonymization-patterns.md` enhanced |
| 2A | ✅ Complete | `tmdl_partition_structure.md` enhanced |
| 2B | ✅ Complete | `project_structure_validation.md` **created** |
| 3A | ✅ Complete | `project_comparison_guide.md` **created** |
| 3B | ✅ Complete | `pbir_visual_structure.md` **created** |
| 4 | ✅ Complete | `tool-fallback-pattern.md` updated |

### Remaining Work

- End-to-end testing with Analyst Edition (no Python)

### Agent Updates Completed

The following agents/workflows were updated with Core fallback sections:

| File | Tool | Reference Added |
|------|------|-----------------|
| `powerbi-compare-project-code.md` | `pbi_merger_utils.py` | `project_comparison_guide.md` → Part 1 |
| `setup-data-anonymization.md` | `sensitive_column_detector.py` | `anonymization-patterns.md` → Part 1 |
| `implement-deploy-test-pbi-project-file.md` | `tmdl_format_validator.py` | `tmdl_partition_structure.md` → Part 1 |
| `evaluate-pbi-project-file.md` | `pbi_project_validator.py` | `project_structure_validation.md` → Part 1 |
| `merge-powerbi-projects.md` | Multiple tools | Added notes for comparison and TMDL validation |
| `powerbi-pattern-discovery.md` | `m_pattern_analyzer.py` | `m_pattern_discovery.md` → Part 1 (already had fallback)
