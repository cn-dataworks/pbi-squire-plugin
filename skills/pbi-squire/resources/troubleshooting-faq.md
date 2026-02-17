# Troubleshooting FAQ

Common issues and solutions when using the PBI Squire skill.

---

## Connection Issues

### "MCP not responding" or "Cannot connect to Power BI Desktop"

**Cause:** The MCP server process isn't running or Power BI Desktop isn't open.

**Solutions:**
1. Open Power BI Desktop and load your project
2. Wait 10-15 seconds for MCP to initialize
3. Try the operation again

If still not working:
- Close and reopen Power BI Desktop
- Check that you're using a PBIP project (not PBIX)
- Verify MCP is installed: Check for `powerbi-mcp` in your extensions

---

### "File-Only mode: MCP unavailable"

**Cause:** Working without Power BI Desktop connection.

**What this means:**
- Operations will read/write TMDL files directly
- DAX validation is syntax-only (no semantic checking)
- Data sampling is unavailable

**When this is fine:**
- Making simple changes you're confident about
- Power BI Desktop is unavailable
- Working on a machine without Desktop installed

**When you should fix it:**
- Complex DAX formulas that need validation
- Need to sample data to understand the model
- Want to verify changes before committing

---

### "Cannot find project at path..."

**Cause:** The specified project path doesn't exist or isn't a valid PBIP folder.

**Solutions:**
1. Verify the path exists
2. Check for the `.SemanticModel/` and `.Report/` subfolders
3. Ensure you're pointing to the folder, not a file
4. Check for typos in the path

**Expected structure:**
```
MyProject/
├── MyProject.pbip
├── MyProject.SemanticModel/
│   └── definition/
│       ├── tables/
│       └── relationships/
└── MyProject.Report/
    └── definition/
        └── pages/
```

---

## DAX Errors

### "Measure X contains a circular dependency"

**Cause:** Two or more measures reference each other, creating a loop.

**Example:**
- Measure A: `[Measure B] * 2`
- Measure B: `[Measure A] / 2`

**Solutions:**
1. Review the measure dependency chain
2. Refactor to break the cycle
3. Use a calculated column instead if appropriate

---

### "Column 'X' does not exist or is not accessible"

**Cause:** The DAX formula references a column that doesn't exist or uses wrong syntax.

**Common causes:**
- Typo in column name
- Using `Column` instead of `Table[Column]`
- Column was renamed or deleted
- Case sensitivity issue

**Solutions:**
1. Check exact column name in the table
2. Use full syntax: `'Table Name'[Column Name]`
3. Verify the table relationship exists

---

### "DIVIDE function: Division by zero"

**Cause:** A DIVIDE operation has a zero denominator.

**Note:** DIVIDE handles this automatically (returns BLANK), but you may get warnings.

**If you want a different result:**
```dax
DIVIDE([Numerator], [Denominator], 0)  -- Returns 0 instead of BLANK
```

---

## Validation Errors

### "TMDL syntax error at line X"

**Cause:** The TMDL file has incorrect formatting or indentation.

**Common causes:**
- Tab instead of spaces (or vice versa)
- Missing or extra line breaks
- Incorrect nesting of properties

**Solutions:**
1. Check the specific line number mentioned
2. Compare with a known-working TMDL file
3. Use the TMDL syntax validator
4. Open in Power BI Desktop to get detailed error

---

### "DAX validation failed: [error details]"

**Cause:** The DAX formula is syntactically valid but semantically incorrect.

**Solutions:**
1. Read the specific error message carefully
2. Check that all referenced objects exist
3. Verify data types are compatible
4. Test the formula in Power BI Desktop DAX query view

---

## Workflow Issues

### "Task not found: [task-id]"

**Cause:** Trying to operate on a task that doesn't exist or was archived.

**Solutions:**
1. List active tasks: `state_manage.ps1 -ListTasks`
2. Use the correct task ID
3. Create a new task if needed

---

### "Resource locked by another task"

**Cause:** Another task is currently editing the same file.

**What this means:**
- A previous task didn't complete or release its lock
- Two concurrent tasks are trying to edit the same file

**Solutions:**
1. Complete or archive the blocking task first
2. Force release the lock: `state_manage.ps1 -ForceRelease "path/to/file"`
3. Wait for the other task to complete

---

### "Changes not appearing in Power BI Desktop"

**Cause:** Power BI Desktop hasn't reloaded the changed files.

**Solutions:**
1. Save all files
2. In Power BI Desktop: Close and reopen the project
3. Or: Use "Refresh" if available
4. Check that you edited the correct project folder

---

## File Issues

### "Cannot write to file: Access denied"

**Cause:** The file is locked by another process or permissions issue.

**Solutions:**
1. Close Power BI Desktop (it may have the file open)
2. Close any text editors with the file open
3. Check file permissions
4. Verify you're not editing a read-only or system folder

---

### "Versioned copy already exists"

**Cause:** A backup with the same timestamp already exists.

**Solutions:**
1. Wait a second and try again (new timestamp)
2. Delete the existing versioned copy if not needed
3. Use a different naming convention

---

## Performance Issues

### "Operation taking too long"

**Causes:**
- Large project with many tables/measures
- Complex DAX formula validation
- MCP connection slow

**Solutions:**
1. Be patient - some operations take time
2. Use file-only mode for simple edits
3. Close other Power BI Desktop instances
4. Restart Power BI Desktop

---

## Agent Behavior Issues

### "I edited the file but the change isn't showing in Power BI"

**Cause:** The agent may have edited `TMDLScripts/` instead of the canonical `definition/` directory.

**How to check:**
1. Look at the file path in the implementation report (Section 4.A)
2. If the path contains `TMDLScripts/`, the edit went to the wrong location
3. Power BI Desktop overwrites `TMDLScripts/` on every save, discarding your changes

**Solutions:**
1. Re-run the workflow — PBI Squire v1.1.0+ enforces path validation to `definition/` only
2. Manually verify the target path contains `/definition/tables/`
3. If using an older version, update the plugin

---

### "Task was marked complete but the measure still shows wrong values"

**Cause:** The agent confirmed the file saved successfully but did not verify the DAX actually produces correct results.

**How to check:**
1. Open the TMDL file and verify the new DAX expression is present
2. Check that the OLD expression is completely removed (not duplicated)
3. Test the measure in Power BI Desktop DAX query view

**Solutions:**
1. PBI Squire v1.1.0+ includes Phase 3.5 (Outcome Verification) that verifies changes are effective, not just saved
2. In LIVE MODE: Run `EVALUATE ROW("Result", [Measure Name])` to test
3. In FILE MODE: Grep the TMDL file for both old and new expressions

---

### "Config was created with dataSensitiveMode: false but I have sensitive data"

**Cause:** During initial setup, the data sensitivity prompt was skipped or auto-defaulted without asking.

**Solutions:**
1. Edit `.claude/pbi-squire.json` and change `"dataSensitiveMode": false` to `"dataSensitiveMode": true`
2. PBI Squire v1.1.0+ makes this prompt BLOCKING — it will not proceed until you explicitly choose
3. After changing the setting, run `/setup-data-anonymization` to configure masking

---

## Getting More Help

If your issue isn't listed here:

1. **Describe the problem clearly**: What were you trying to do? What happened instead?
2. **Include error messages**: Copy the exact error text
3. **Show your context**: What project are you working with? What mode (Desktop/File-only)?

Ask: "I'm getting [error] when trying to [action]. Can you help?"

---

*Last updated: 2026-02-16*
