# Recommended Workflow Enhancement for Power BI Project Evaluation

## Problem Statement

During implementation on 2025-10-27, we encountered an issue where:
1. User provided a pbi-tools extracted folder (not a valid .pbip project)
2. The versioned output was also in pbi-tools format
3. User could not open the output in Power BI Desktop (no .pbip file)
4. pbi-tools compilation failed due to version mismatch

## Root Cause

The slash commands did not:
- Validate input format (missing .pbip file check)
- Handle different Power BI project formats gracefully
- Create a reviewable output format (.pbip or compiled .pbix/.pbit)

## Solution: Support Multiple Input Formats

Based on research:
- **Power BI Project (.pbip)**: Microsoft's native format, directly openable in PBI Desktop
- **PBIX file**: Compiled binary, needs extraction before editing
- **pbi-tools format**: Extracted folder structure, needs compilation to review

### pbi-tools Round-Trip Workflow

**Extract (PBIX → folder):**
```bash
pbi-tools extract "file.pbix"
# Creates: file/ folder with TMDL files
```

**Compile (folder → PBIT):**
```bash
pbi-tools compile "folder" "output.pbit" PBIT -overwrite
# Creates: output.pbit (can open in PBI Desktop)
# Note: PBIX output only works for "thin reports" (no model)
# Files with models MUST use PBIT format
```

**Limitation**: pbi-tools compiles folders with models to PBIT, not PBIX.
User must open PBIT, refresh data, save as PBIX.

---

## Recommended Changes to `/evaluate-pbi-project-file`

### Phase 1: Validation & Setup (ENHANCED)

Replace lines 43-47 with:

```markdown
### Phase 1: Validation & Setup
1. Parse command arguments to extract project path, image path (if provided), and description

2. **Detect and Validate Input Format**:

   **Format Detection Logic:**

   a) **Power BI Project (.pbip) - Preferred Format**
      - Check: Does folder contain a `*.pbip` file?
      - Check: Does folder contain `*.SemanticModel/` subfolder?
      - Check: Does folder contain `*.Report/` subfolder?
      - If all present → Valid .pbip project
      - **Action**: Proceed with standard workflow
      - **Mark format**: `format: "pbip"` in findings metadata

   b) **PBIX File Input**
      - Check: Is `--project` path pointing to a `.pbix` file?
      - If yes → Extract with pbi-tools
      - **Action**:
        ```bash
        pbi-tools extract "<pbix-path>"
        ```
      - Creates: `<pbix-name>/` folder with pbi-tools format
      - Update project path to extracted folder
      - **Mark format**: `format: "pbix-extracted", original_pbix: "<path>"` in findings metadata
      - Display message: "Extracted PBIX to temporary folder for analysis"

   c) **pbi-tools Extracted Format**
      - Check: Does folder contain `.pbixproj.json`?
      - Check: Does folder contain `Model/` subfolder? (not `*.SemanticModel/`)
      - If yes → Valid pbi-tools extraction
      - **Action**: Proceed with analysis (TMDL files are compatible)
      - **Mark format**: `format: "pbi-tools"` in findings metadata
      - Display message: "Detected pbi-tools format, will compile to PBIT for review"

   d) **Invalid Input**
      - If none of the above match
      - **Error Message**:
        ```
        ❌ Invalid Power BI project format

        Expected one of:
        1. Power BI Project folder with .pbip file
        2. PBIX file (will be extracted automatically)
        3. pbi-tools extracted folder (has .pbixproj.json)

        Provided: <path>
        Found: <describe what was found>

        To create a valid Power BI Project:
        - Open your .pbix in Power BI Desktop
        - File → Save As → Power BI Project
        ```
      - **Action**: Exit workflow with error code

3. **Validate TMDL Structure**:
   - For .pbip: Check `*.SemanticModel/definition/` folder
   - For pbi-tools: Check `Model/` folder
   - Confirm TMDL files exist (tables/, relationships.tmdl, etc.)

4. **Store Format Metadata** in findings file:
   Add to Problem Statement section:
   ```markdown
   **Project Format**: [pbip | pbix-extracted | pbi-tools]
   **Original PBIX Path**: <if extracted from pbix>
   **Requires Compilation**: [Yes (pbi-tools) | No (pbip)]
   ```
```

---

## Recommended Changes to `/implement-deploy-test-pbi-project-file`

### Phase 2: Apply Changes (ENHANCED)

Replace Phase 2 section with:

```markdown
### Phase 2: Apply Changes (ENHANCED)

**Invoke:** `powerbi-code-implementer-apply` agent

**Inputs:**
- Findings file path
- Project path (from findings.md metadata)
- **Project format** (read from findings metadata: pbip, pbix-extracted, or pbi-tools)

**Agent Actions:**

1. **Read format metadata from findings file**

2. **Create timestamped versioned copy** maintaining same format:
   - Timestamp: `YYYYMMDD_HHMMSS`
   - Copy all project files to `<original-name>_<timestamp>/`
   - Preserve folder structure exactly

3. **Apply all changes from Section 2**:
   - Edit TMDL files in versioned copy
   - Fix indentation issues (ensure proper tabs)
   - Log each file modification

4. **Create Reviewable Output** based on format:

   **If format = "pbip":**
   - Versioned folder IS the reviewable output
   - User can open `*.pbip` file directly in Power BI Desktop
   - No compilation needed

   **If format = "pbi-tools" OR "pbix-extracted":**
   - Attempt to compile to PBIT using pbi-tools:
     ```bash
     cd "<versioned-folder>"
     pbi-tools compile . "<name>_UPDATED.pbit" PBIT -overwrite
     ```
   - **If compilation succeeds**:
     - Creates `<name>_UPDATED.pbit` in same directory
     - User can open PBIT in Power BI Desktop
     - User must refresh data when opening
     - User saves as .pbix after reviewing/testing

   - **If compilation fails** (version mismatch, schema errors, etc.):
     - Log error details
     - Provide fallback instructions:
       ```
       ⚠️ pbi-tools compilation failed

       Error: <compilation error message>

       To review changes manually:

       Option 1: Direct TMDL Review
       - Changes are in: <versioned-folder>/Model/tables/
       - View modified TMDL files in text editor
       - Compare with original using diff tool

       Option 2: Manual Application to Original PBIX
       - Open original: <original-pbix-path>
       - Apply changes from Section 2 manually
       - DAX code to copy: [show formatted DAX]
       - Format string to apply: [show format]

       Option 3: Try Different pbi-tools Version
       - Update pbi-tools: https://pbi.tools/
       - Retry compilation with updated version
       ```

**Success Criteria:**
- Versioned project created successfully
- All code changes applied without errors
- **AND ONE OF**:
  - .pbip file ready to open (pbip format)
  - .pbit file compiled successfully (pbi-tools format)
  - Fallback instructions provided (if compilation fails)

**Outputs:**
- Path to versioned project folder
- Path to compiled .pbit file (if applicable and successful)
- Status: success | success-with-warnings | failed-compilation
- Instructions for manual review (if needed)
```

---

## Benefits of This Approach

### For Users:
✅ Can provide .pbix files directly (automatic extraction)
✅ Can provide pbi-tools folders (automatically detected)
✅ Can provide .pbip projects (optimal path)
✅ Always get a reviewable output (either .pbip or .pbit)
✅ Clear error messages if format is invalid

### For Workflow:
✅ Handles all three Power BI project formats
✅ Automatic format detection and handling
✅ Graceful fallback if compilation fails
✅ Clear documentation of format in findings.md
✅ No manual format conversion required

### For Implementation:
✅ Versioned output matches input format
✅ pbi-tools round-trip: extract → edit → compile
✅ PBIT compilation for models (correct format)
✅ Manual review instructions if automation fails

---

## Testing Scenarios

### Scenario 1: User provides .pbip project
- Input: `ProjectName.pbip` + folders
- Detection: .pbip file found → format = "pbip"
- Workflow: Standard (no extraction/compilation)
- Output: Versioned .pbip project (directly openable)

### Scenario 2: User provides .pbix file
- Input: `Report.pbix`
- Detection: .pbix file → format = "pbix-extracted"
- Workflow: Extract → Analyze → Apply → Compile
- Output: Versioned folder + `Report_UPDATED.pbit`

### Scenario 3: User provides pbi-tools folder
- Input: Folder with `.pbixproj.json` and `Model/`
- Detection: pbi-tools format → format = "pbi-tools"
- Workflow: Analyze → Apply → Compile
- Output: Versioned folder + `Project_UPDATED.pbit`

### Scenario 4: Compilation fails (like our case)
- Input: Any format requiring compilation
- Workflow: Extract/detect → Apply changes
- Compilation: FAILS with version mismatch
- Output: Versioned folder + manual instructions + formatted DAX

### Scenario 5: Invalid input
- Input: Random folder with no valid structure
- Detection: No .pbip, no .pbix, no .pbixproj.json
- Workflow: ERROR immediately with clear message
- Output: None (exit with helpful error)

---

## Implementation Priority

**HIGH PRIORITY** - This issue will recur for any user providing non-.pbip inputs.

**Recommended Implementation Order:**
1. Add format detection to `/evaluate-pbi-project-file` (Phase 1)
2. Store format metadata in findings.md
3. Update `/implement-deploy-test-pbi-project-file` to read format and compile
4. Add fallback instructions for compilation failures
5. Test all five scenarios above

---

## Files to Modify

1. **`.claude/commands/evaluate-pbi-project-file.md`**
   - Enhance Phase 1: Validation & Setup
   - Add format detection logic
   - Add format metadata to findings template

2. **`.claude/commands/implement-deploy-test-pbi-project-file.md`**
   - Enhance Phase 2: Apply Changes
   - Add format-specific compilation logic
   - Add fallback instructions section

3. **Agent prompts** (if agents are template-based):
   - `powerbi-code-implementer-apply`: Add format parameter
   - Update to handle compilation step

---

## Conclusion

This enhancement allows the workflow to:
- ✅ Accept any Power BI project format (.pbip, .pbix, pbi-tools)
- ✅ Automatically extract/convert as needed
- ✅ Always provide a reviewable output
- ✅ Handle errors gracefully with manual fallback

The key insight: **pbi-tools CAN round-trip** (extract → edit → compile), we just need to orchestrate it properly and handle the PBIT format requirement for models.
