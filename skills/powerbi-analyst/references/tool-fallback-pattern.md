# Tool-First Fallback Pattern

This document describes the standard pattern for using Python tools when available, with Claude-native fallback when tools are not installed.

## Why This Pattern?

| Edition | Has Python Tools | Experience |
|---------|------------------|------------|
| **Pro** | Yes (via bootstrap) | Fast execution, lower token cost, precise validation |
| **Core** | No | Works without Python using Claude-native logic |

This enables the plugin to work for all users while giving Pro users better performance.

---

## The Pattern

Every agent that can use a Python tool should follow this pattern:

```markdown
**Tool Selection (Try Tool First, Fallback to Claude-Native):**

1. **Check for tool availability:**
   ```bash
   test -f ".claude/tools/<tool_name>.py" && echo "TOOL_AVAILABLE" || echo "TOOL_NOT_AVAILABLE"
   ```

2. **If tool available (Pro edition):**
   - Execute Python tool via Bash
   - Faster execution, deterministic results
   - Lower token usage

3. **If tool NOT available (Core edition):**
   - Use Claude-native approach (Read, Edit, Grep tools)
   - Load reference documents for patterns/rules
   - Apply logic directly in conversation
```

---

## Tool-to-Fallback Mapping

| Python Tool | Pro Behavior | Core Fallback | Reference Doc Part |
|-------------|--------------|---------------|-------------------|
| `m_pattern_analyzer.py` | Scan for M patterns, generate report | Follow detection rules | `m_pattern_discovery.md` → **Part 1** |
| `query_folding_validator.py` | Analyze folding, line-by-line | Scan for breaking operations | `query_folding_guide.md` → **Part 1** |
| `sensitive_column_detector.py` | Pattern match columns with confidence | Match against pattern tables | `anonymization-patterns.md` → **Part 1** |
| `tmdl_format_validator.py` | Validate with 13 error codes | Check indentation and structure | `tmdl_partition_structure.md` → **Part 1** |
| `pbi_project_validator.py` | Detect format, validate structure | Use Glob for format detection | `project_structure_validation.md` → **Part 1** |
| `pbi_merger_utils.py` | Compare/merge with diff IDs | Extract and compare measures | `project_comparison_guide.md` → **Part 1** |
| `extract_visual_layout.py` | Extract visual positions/fields | Read visual.json directly | `pbir_visual_structure.md` → **Part 1** |
| `pbir_visual_editor.py` | Execute visual edit plan | Parse JSON, use Edit tool | Pro-only (visual editing) |
| `m_partition_editor.py` | Edit M code with tab handling | Use Edit tool with indentation | `tmdl_partition_structure.md` |
| `tmdl_measure_replacer.py` | Replace measure DAX | Use Edit tool or MCP | Edit tool fallback |
| `anonymization_generator.py` | Generate M masking code | Use M code templates | `anonymization-patterns.md` → Templates |

---

## Performance Comparison

| Aspect | Python Tool | Claude-Native |
|--------|-------------|---------------|
| **Execution Speed** | Milliseconds | Seconds to minutes |
| **Token Cost** | Zero | Depends on file size |
| **Precision** | Deterministic, exact | May vary slightly |
| **Error Handling** | Structured exit codes | Natural language errors |
| **Availability** | Requires Python + bootstrap | Always available |

---

## Implementation Checklist

When adding tool-first fallback to an agent:

1. [ ] Add tool availability check at the start of the relevant step
2. [ ] Document the Pro (tool) behavior
3. [ ] Document the Core (Claude-native) fallback behavior
4. [ ] Reference the appropriate reference document for fallback logic
5. [ ] Ensure both paths produce equivalent results
6. [ ] Update Prerequisites section to mark Python as "Optional (Pro)"

---

## Example: TMDL Validation

**Pro (with tool):**
```bash
python .claude/tools/tmdl_format_validator.py "path/to/file.tmdl" --context "Modified Sales table"
```
- Returns structured errors with line numbers
- Auto-fixes TMDL012 warnings
- Exit code indicates pass/fail

**Core (Claude-native):**
1. Read the TMDL file
2. Check each line for indentation (count leading tabs)
3. Verify property placement using rules from `tmdl_partition_structure.md`
4. Report issues found in natural language

---

## Analytics Tools (Pro-Only)

Some tools are **Pro-only with no Core fallback** because they provide optional analytics:

| Tool | Purpose | Core Behavior |
|------|---------|---------------|
| `agent_logger.py` | Track agent execution | Analytics not available |
| `token_analyzer.py` | Parse token usage | Analytics not available |
| `analytics_merger.py` | Aggregate analytics | Analytics not available |
| `monitor_deployment_status.py` | QA Loop monitoring | QA Loop workflow not available |

These tools enhance the Pro experience but are not required for core functionality.

---

---

## Reference Document Structure

All Claude-native reference documents follow this structure:

```markdown
# [Topic] Guide

## Quick Reference
| Edition | Method |
|---------|--------|
| **Pro** | Run `tool_name.py` |
| **Core** | Follow detection rules below |

## Part 1: Detection/Validation (Claude-Native)
Step-by-step instructions for Claude to perform the same
analysis using Grep/Glob/Read tools.
- What to search for
- How to classify results
- How to generate report

## Part 2+: Application/Usage
How to apply detected patterns or fixes

## Checklist
Verification steps before completing
```

### Complete Reference Document List

| Reference Document | Purpose | Tool Equivalent |
|--------------------|---------|-----------------|
| `m_pattern_discovery.md` | M code pattern analysis | `m_pattern_analyzer.py` |
| `query_folding_guide.md` | Query folding analysis | `query_folding_validator.py` |
| `anonymization-patterns.md` | Sensitive column detection | `sensitive_column_detector.py` |
| `tmdl_partition_structure.md` | TMDL format validation | `tmdl_format_validator.py` |
| `project_structure_validation.md` | Project format detection | `pbi_project_validator.py` |
| `project_comparison_guide.md` | Project comparison/merge | `pbi_merger_utils.py` |
| `pbir_visual_structure.md` | Visual layout extraction | `extract_visual_layout.py` |

---

## See Also

- `SKILL.md` - Main skill documentation
- `m_pattern_discovery.md` - M code pattern detection
- `query_folding_guide.md` - Query folding analysis
- `anonymization-patterns.md` - Sensitive column detection
- `tmdl_partition_structure.md` - TMDL format validation
- `project_structure_validation.md` - Project format detection
- `project_comparison_guide.md` - Project comparison
- `pbir_visual_structure.md` - Visual layout extraction
