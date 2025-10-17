# TMDL Measure Replacer - Agent Usage Guide

## Purpose

The `tmdl_measure_replacer.py` tool solves the **whitespace complexity problem** when programmatically editing Power BI TMDL files. Traditional string matching fails because TMDL files use tab characters for indentation, making exact text replacement unreliable.

## The Problem This Solves

**Traditional Approach (FAILS):**
```python
# This fails due to whitespace/tab mismatches
content = file.read()
content = content.replace(original_code, new_code)  # ❌ Never finds exact match
file.write(content)
```

**Robust Approach (WORKS):**
```python
# This works by finding measures by name, not exact text
replace_measure_in_file(filepath, "Measure Name", new_dax_body)  # ✅ Success
```

## How It Works

1. **Finds measure by name** using regex: `measure 'Name' =`
2. **Extracts entire measure** from declaration to next top-level element
3. **Replaces DAX body** while preserving properties (formatString, displayFolder, etc.)
4. **Handles tabs correctly** using explicit `\t` characters
5. **Auto-indents new code** to match TMDL structure

## Command-Line Usage

### Basic Syntax
```bash
python tmdl_measure_replacer.py <tmdl_file> <measure_name> <new_dax_file>
```

### Example
```bash
python tmdl_measure_replacer.py \
  "C:\project\Commissions_Measures.tmdl" \
  "Sales Commission GP Actual NEW" \
  "new_dax.txt"
```

### Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `tmdl_file` | Path to TMDL file | `Commissions_Measures.tmdl` |
| `measure_name` | Exact measure name (no quotes) | `Sales Commission GP Actual NEW` |
| `new_dax_file` | Path to file with new DAX code | `new_dax.txt` |

## For Agents: Integration Guide

### Step 1: Detect Measure Changes

```python
# Check if this is a measure change in a TMDL file
is_measure = "measure" in section_title.lower()
is_tmdl = target_file.endswith('.tmdl')

if is_measure and is_tmdl:
    use_robust_editor = True
```

### Step 2: Extract Measure Name

```python
# From section header like: "### Sales Commission GP Actual NEW - Measure"
import re
match = re.search(r'###\s+(.+?)\s+-\s+Measure', section_title)
measure_name = match.group(1) if match else None
```

### Step 3: Prepare New DAX Code

```python
# Extract the Proposed Code from the markdown section
# Remove any leading/trailing whitespace but preserve structure
proposed_dax = extract_code_block(section, "Proposed Code")
proposed_dax = proposed_dax.strip()

# Save to temporary file
import tempfile
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
    f.write(proposed_dax)
    temp_dax_file = f.name
```

### Step 4: Execute Replacement

```python
import subprocess

cmd = [
    'python',
    '.claude/tools/tmdl_measure_replacer.py',
    target_tmdl_file,
    measure_name,
    temp_dax_file
]

result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode == 0:
    print(f"✅ {measure_name} updated successfully")
    print(result.stdout)
else:
    print(f"❌ Failed to update {measure_name}")
    print(result.stderr)
```

### Step 5: Verify Success

```python
# Check that measure still exists in file
with open(target_tmdl_file, 'r', encoding='utf-8') as f:
    content = f.read()

if f"measure '{measure_name}' =" in content:
    print(f"✅ Verification: Measure '{measure_name}' found in file")
else:
    print(f"⚠️ Warning: Measure '{measure_name}' not found after replacement")
```

## Example: Full Agent Workflow

```python
# Agent code for applying measure changes

def apply_measure_change(section, target_file, project_dir):
    """Apply a measure change using robust TMDL editor"""

    # 1. Extract information
    measure_name = extract_measure_name(section['title'])
    proposed_dax = extract_code_block(section, 'Proposed Code')

    # 2. Save DAX to temp file
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8')
    temp_file.write(proposed_dax.strip())
    temp_file.close()

    # 3. Construct full path
    full_target = os.path.join(project_dir, target_file)

    # 4. Execute replacement
    import subprocess
    result = subprocess.run([
        'python',
        '.claude/tools/tmdl_measure_replacer.py',
        full_target,
        measure_name,
        temp_file.name
    ], capture_output=True, text=True)

    # 5. Clean up temp file
    os.unlink(temp_file.name)

    # 6. Check result
    if result.returncode == 0:
        return {
            'success': True,
            'message': f"Measure '{measure_name}' updated",
            'method': 'Robust TMDL Editor'
        }
    else:
        return {
            'success': False,
            'message': result.stderr,
            'method': 'Robust TMDL Editor (failed)'
        }
```

## Output Messages

### Success
```
[BACKUP] Created: Commissions_Measures.tmdl.backup
[SUCCESS] Measure 'Sales Commission GP Actual NEW' updated successfully
[COMPLETE] Measure replacement successful
```

### Error Examples
```
ERROR: Measure 'Invalid Name' not found in file
ERROR: TMDL file not found: missing_file.tmdl
ERROR: DAX file not found: missing_dax.txt
ERROR: Could not find measure header
```

## Backup Strategy

The tool **automatically creates backups**:
- Backup file: `<original_file>.backup`
- Location: Same directory as the target file
- Content: Complete original file before modification

Example:
```
Commissions_Measures.tmdl         ← Modified file
Commissions_Measures.tmdl.backup  ← Original content (auto-created)
```

## Advantages Over Traditional String Replacement

| Feature | Traditional | Robust Editor |
|---------|------------|---------------|
| Handles tabs | ❌ Fails | ✅ Works |
| Whitespace insensitive | ❌ No | ✅ Yes |
| Finds by name | ❌ No | ✅ Yes |
| Preserves properties | ❌ Risky | ✅ Guaranteed |
| Auto-indentation | ❌ No | ✅ Yes |
| Error messages | ❌ Cryptic | ✅ Clear |
| Automatic backups | ❌ No | ✅ Yes |

## When NOT to Use This Tool

**Use traditional string replacement for:**
- M code (Power Query) changes
- Calculated column definitions
- Table definitions
- Non-measure TMDL elements
- Files other than TMDL (e.g., .json, .md)

**Use this tool for:**
- ✅ DAX measures in TMDL files
- ✅ Any `measure 'Name' =` definitions
- ✅ When Original Code whitespace doesn't match

## Troubleshooting

### "Measure not found"
- Check measure name is **exact** (case-sensitive)
- Ensure measure exists in the file
- Verify file path is correct

### "Could not find measure header"
- File may be corrupted
- TMDL structure may be invalid
- Try opening file in text editor to verify format

### Python not found
- Install Python 3.x
- Add Python to system PATH
- Use full path: `C:\Python\python.exe tmdl_measure_replacer.py ...`

## Version History

- **v1.0** (2025-10-10): Initial release
  - Measure-level replacement
  - Tab-aware indentation
  - Automatic backup creation
  - Command-line interface

## License

MIT License - Free to use and modify for Power BI automation projects.
