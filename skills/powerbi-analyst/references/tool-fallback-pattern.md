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

| Python Tool | Pro Behavior | Core Fallback |
|-------------|--------------|---------------|
| `tmdl_format_validator.py` | Run validator, get precise errors | Read TMDL, validate against `tmdl_partition_structure.md` rules |
| `pbir_visual_editor.py` | Execute XML edit plan | Parse XML, use Edit tool on visual.json |
| `m_partition_editor.py` | Edit M code with tab handling | Use Edit tool with careful indentation |
| `tmdl_measure_replacer.py` | Replace measure DAX | Use Edit tool or MCP measure_operations |
| `m_pattern_analyzer.py` | Scan for M patterns | Read TMDL files, analyze with Claude |
| `query_folding_validator.py` | Analyze folding | Use `query_folding_guide.md` reference |
| `pbi_project_validator.py` | Validate structure | Use Glob to check folder structure |
| `pbi_merger_utils.py` | Compare/merge projects | Read and compare files directly |
| `sensitive_column_detector.py` | Pattern match columns | Use `anonymization-patterns.md` reference |
| `anonymization_generator.py` | Generate M code | Use templates from `anonymization-patterns.md` |
| `extract_visual_layout.py` | Extract layout info | Read visual.json directly |

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

## See Also

- `SKILL.md` - Main skill documentation
- `tmdl_partition_structure.md` - TMDL format rules for fallback validation
- `anonymization-patterns.md` - Patterns for fallback anonymization
- `query_folding_guide.md` - Query folding rules for fallback analysis
