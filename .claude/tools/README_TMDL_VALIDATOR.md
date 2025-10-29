# TMDL Format Validator

A lightweight standalone Python tool for validating TMDL (Tabular Model Definition Language) file formatting and structure.

## Overview

The TMDL Format Validator catches formatting errors in TMDL files before they cause issues in Power BI Desktop. It validates:

- ✅ Indentation consistency (tabs vs spaces, proper levels)
- ✅ Property placement (formatString, displayFolder, etc.)
- ✅ Property context (ensures properties are outside DAX blocks)
- ✅ Measure/column/table structure
- ✅ TMDL syntax compliance

## Why This Tool Exists

Power BI Desktop requires TMDL files to follow strict formatting rules. Common issues include:

- **Indentation errors**: Properties must have exactly 2 tabs
- **Property placement**: Properties inside DAX expressions cause parsing errors
- **Inconsistent formatting**: Mixed tabs/spaces break the parser

These errors produce cryptic error messages like:
```
TMDL Format Error: Unsupported property - formatString is not a supported property in the current context!
```

The validator catches these issues early with clear, actionable error messages.

## Installation

**No installation required!** This is a standalone Python script with no external dependencies.

**Requirements:**
- Python 3.x

**Location:**
- `.claude/tools/tmdl_format_validator.py`

## Usage

### Basic Validation

```bash
python .claude/tools/tmdl_format_validator.py <tmdl_file_path>
```

**Example:**
```bash
python .claude/tools/tmdl_format_validator.py "C:\path\to\project\definition\tables\Commissions_Measures.tmdl"
```

### With Context

Provide context about what was changed for better reporting:

```bash
python .claude/tools/tmdl_format_validator.py <tmdl_file_path> --context "description"
```

**Example:**
```bash
python .claude/tools/tmdl_format_validator.py ".\tables\Measures.tmdl" --context "Updated PSSR Misc Commission formatString"
```

## Output

### Success Output

```
================================================================================
TMDL FORMAT VALIDATION REPORT
================================================================================
File: Commissions_Measures.tmdl
Context: Updated PSSR Misc Commission measure
Total Lines: 2006
Indentation: TABS
================================================================================

[SUCCESS] No formatting issues found!

The TMDL file is properly formatted and ready for use.
================================================================================
```

### Error Output

```
================================================================================
TMDL FORMAT VALIDATION REPORT
================================================================================
File: Commissions_Measures.tmdl
Context: Updated PSSR Misc Commission measure
Total Lines: 2006
Indentation: TABS
================================================================================

[SUMMARY]
  Errors:   2
  Warnings: 0
  Info:     0

[ERRORS] (Must Fix):
--------------------------------------------------------------------------------

Line 1628 [ERROR] TMDL001: Inconsistent property indentation. Expected 2 tabs/levels, got 1
  → 	formatString: \$#,0.00;(\$#,0.00);\$#,0.00

Line 1630 [ERROR] TMDL002: Property has insufficient indentation. Properties should have 2 tabs/levels, got 1
  → 	displayFolder: PSSR Comms

================================================================================

[VALIDATION FAILED]

The TMDL file has formatting errors that must be fixed before
it can be opened in Power BI Desktop.
================================================================================
```

## Exit Codes

- `0`: Validation passed (no errors)
- `1`: Validation failed (errors found)
- `2`: File not found or read error

Use exit codes in automated scripts:

```bash
python .claude/tools/tmdl_format_validator.py "file.tmdl"
if [ $? -eq 0 ]; then
    echo "Validation passed!"
else
    echo "Validation failed!"
fi
```

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| TMDL001 | ERROR | Inconsistent property indentation within a group |
| TMDL002 | ERROR | Property has insufficient indentation (needs more tabs) |
| TMDL003 | WARNING | DAX expression line indentation issue |
| TMDL004 | ERROR | Property appears inside DAX expression block |

## Common Issues and Fixes

### Issue 1: Property with Wrong Indentation

**Error:**
```
Line 1628 [ERROR] TMDL001: Expected 2 tabs, got 1
  → 	formatString: \$#,0.00
```

**Fix:**
Add one more tab at the beginning of the line.

**Before:**
```tmdl
measure 'Example' =
		RETURN
		_value
	formatString: "$#,0.00"    ← Only 1 tab (WRONG)
```

**After:**
```tmdl
measure 'Example' =
		RETURN
		_value
		formatString: "$#,0.00"  ← 2 tabs (CORRECT)
```

### Issue 2: Property Inside DAX Expression

**Error:**
```
Line 1625 [ERROR] TMDL004: Property inside DAX expression block
  → 		formatString: "$#,0.00"
```

**Fix:**
Move the property AFTER the RETURN statement's value, with 2 tabs.

**Before:**
```tmdl
measure 'Example' =
		VAR _x = 1
		formatString: "$#,0.00"  ← Inside expression (WRONG)
		RETURN
		_x
```

**After:**
```tmdl
measure 'Example' =
		VAR _x = 1
		RETURN
		_x
		formatString: "$#,0.00"  ← After expression (CORRECT)
		displayFolder: "Measures"
```

### Issue 3: Inconsistent Property Indentation

**Error:**
```
Line 1630 [ERROR] TMDL001: Inconsistent indentation
```

**Fix:**
Ensure ALL properties in a group have the SAME indentation (2 tabs).

**Before:**
```tmdl
measure 'Example' =
		RETURN _x
		formatString: "$#,0.00"    ← 2 tabs
	displayFolder: "Measures"  ← Only 1 tab (WRONG)
```

**After:**
```tmdl
measure 'Example' =
		RETURN _x
		formatString: "$#,0.00"    ← 2 tabs
		displayFolder: "Measures"  ← 2 tabs (CORRECT)
```

## TMDL Indentation Rules

### Rule 1: Use Tabs, Not Spaces

TMDL files MUST use tab characters (`\t`), not spaces.

### Rule 2: Measure Properties Need 2 Tabs

All measure properties must be indented with exactly **2 tabs**:

```tmdl
measure 'Name' =
		<DAX expression>           ← 2 tabs
		formatString: ...          ← 2 tabs
		displayFolder: ...         ← 2 tabs
		lineageTag: ...            ← 2 tabs
		annotation ...             ← 2 tabs
```

### Rule 3: Properties Come After DAX Expression

Properties must appear AFTER the entire DAX expression, not in the middle:

```tmdl
measure 'Name' =
		VAR _x = 1
		RETURN
		_x
		<-- Properties go here -->
	formatString: ...
	displayFolder: ...
```

### Rule 4: Consistent Indentation Within Groups

All consecutive properties must have the same indentation level:

```tmdl
		formatString: "$#,0.00"    ← Same indent
		displayFolder: "Folder"    ← Same indent
		lineageTag: abc-123        ← Same indent
```

## Integration with Agents

This validator is automatically called by:

- **powerbi-code-implementer-apply**: After applying code changes
- **powerbi-tmdl-syntax-validator**: As the primary validation agent

### Agent Usage Example

```python
# In powerbi-code-implementer-apply agent
result = subprocess.run([
    "python",
    ".claude/tools/tmdl_format_validator.py",
    tmdl_file_path,
    "--context",
    "Modified measure: Example"
], capture_output=True, text=True)

if result.returncode == 0:
    print("✅ TMDL format validation passed")
else:
    print(f"❌ TMDL format validation failed:\n{result.stdout}")
    # Halt workflow
```

## Workflow Position

The validator runs at Phase 2.5 of the implementation workflow:

```
Phase 2: Apply Code Changes (powerbi-code-implementer-apply)
         ↓
Phase 2.5: TMDL Format Validation ← THIS TOOL
         ↓
Phase 3: DAX Logic Validation (powerbi-dax-review-agent)
         ↓
Phase 4: Deployment
```

## Limitations

### What This Tool Does NOT Validate

- ❌ DAX formula correctness (syntax/semantics)
- ❌ Column references existence
- ❌ Business logic
- ❌ Function parameters
- ❌ Measure dependencies
- ❌ M code syntax
- ❌ Visual JSON structure

These are validated by other agents in the workflow.

### File Types Supported

- ✅ `.tmdl` files (TMDL format)
- ❌ `.bim` files (JSON format - not supported)
- ❌ `.pbix` files (binary format - not supported)

## Troubleshooting

### Python Not Found

```bash
python: command not found
```

**Solution:** Ensure Python 3.x is installed and in your PATH.

### File Not Found

```bash
ERROR: File not found: C:\path\to\file.tmdl
```

**Solution:** Check the file path is correct and the file exists.

### Permission Denied

```bash
ERROR: Failed to read file: PermissionError
```

**Solution:** Ensure you have read permissions for the file.

## Development

### Running Tests

Test the validator on sample files:

```bash
# Test a valid file
python .claude/tools/tmdl_format_validator.py "tests/valid_measure.tmdl"

# Test a file with errors
python .claude/tools/tmdl_format_validator.py "tests/invalid_indentation.tmdl"
```

### Adding New Validation Rules

To add new validation rules, edit `tmdl_format_validator.py`:

1. Add a new validation method to the `TmdlFormatValidator` class
2. Call it from the `validate()` method
3. Use the `ValidationIssue` dataclass to report errors
4. Document the new error code in this README

## Support

For issues or questions:
1. Check this README for common issues
2. Review the error messages and line numbers
3. Consult the TMDL indentation rules above
4. Open an issue in the project repository

## Version

**Version:** 1.0.0
**Last Updated:** 2025-10-27
**Python Version:** 3.x+
**Dependencies:** None (standalone)

---

**Remember:** This tool catches format errors BEFORE Power BI Desktop, saving you from cryptic error messages and debugging time!
