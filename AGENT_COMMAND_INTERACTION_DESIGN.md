# Agent-Command Interaction Design
## powerbi-verify-pbiproject-folder-setup ↔ evaluate-pbi-project-file

**Created**: 2025-10-27
**Purpose**: Define the feedback loop between the verification agent and the evaluation command

---

## Design Principles

1. **Agent writes status, Command reads and acts**
2. **Agent NEVER prompts user directly** - it only documents what's needed
3. **Command handles all user interaction**
4. **Agent is idempotent** - can be re-invoked with updated parameters
5. **Findings file is the communication medium**

---

## Interaction Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ /evaluate-pbi-project-file Command                          │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ 1. Parse arguments
                          │    --project, --description
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │ Create scratchpad + findings.md    │
        └─────────────────────────────────────┘
                          │
                          │ 2. Invoke agent
                          │    (pass: project_path, findings_path)
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ powerbi-verify-pbiproject-folder-setup Agent                │
│                                                              │
│ • Detect format (.pbip, .pbix, pbi-tools)                  │
│ • Validate structure                                        │
│ • Write status to findings.md "Prerequisites" section      │
│ • Return (does NOT prompt user)                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ 3. Return with status
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │ Command reads Prerequisites section │
        └─────────────────────────────────────┘
                          │
                          │ 4. Check status field
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
        ▼                                   ▼
   status=validated              status=action_required
        │                                   │
        │                                   │
        ▼                                   ▼
   ┌─────────┐                    ┌──────────────────┐
   │Continue │                    │ Check action_type│
   │Analysis │                    └──────────────────┘
   └─────────┘                              │
                                            │
                    ┌───────────────────────┼───────────────────┐
                    ▼                       ▼                   ▼
             pbix_extraction       pbitools_install     invalid_format
                    │                       │                   │
                    ▼                       ▼                   ▼
            ┌──────────────┐      ┌───────────────┐   ┌──────────┐
            │ Prompt user: │      │Show install   │   │Show error│
            │ [Y/N/I]      │      │instructions   │   │Exit      │
            └──────────────┘      │Exit           │   └──────────┘
                    │              └───────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
      [Y]         [N]         [I]
        │           │           │
        ▼           ▼           ▼
   ┌────────┐  ┌────────┐  ┌────────┐
   │Check   │  │Show    │  │Show    │
   │pbi-    │  │manual  │  │install │
   │tools   │  │guide   │  │guide   │
   └────────┘  │Exit    │  │Exit    │
        │      └────────┘  └────────┘
        │
    ┌───┴────┐
    ▼        ▼
  Found   Not found
    │        │
    ▼        ▼
┌────────┐ ┌─────────┐
│Re-invoke│ │Show     │
│agent    │ │error    │
│with     │ │Re-prompt│
│extract  │ └─────────┘
│flag     │
└────────┘
    │
    │ 5. Re-invoke agent
    │    (pass: extract=true)
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Agent (2nd invocation)                                       │
│                                                              │
│ • Execute extraction                                         │
│ • Validate extracted folder                                 │
│ • Update Prerequisites section with success                 │
│ • Return                                                     │
└─────────────────────────────────────────────────────────────┘
    │
    │ 6. Return with status=validated
    │
    ▼
┌─────────────────────────────────────┐
│ Command reads updated Prerequisites │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────┐
│ Continue    │
│ Analysis    │
└─────────────┘
```

---

## Data Contract: Prerequisites Section Format

The agent writes this structure to findings.md, and the command reads it:

```yaml
## Prerequisites: Project Setup Validation

**Validation Date**: 2025-10-27 14:30:00
**Agent**: powerbi-verify-pbiproject-folder-setup
**Status**: [validated | action_required | error]
**Action Type**: [none | pbix_extraction | pbitools_install | invalid_format]

### Input Format Detection
**Format Detected**: [pbip | pbi-tools | pbix | unknown]
**Project Path**: <original-path>
**Original PBIX**: <pbix-path-if-applicable>

### Action Required Details
**Required Action**: [description of what user needs to do]
**User Choices Available**: [Y/N/I] or [manual instructions]
**Next Steps**: [what will happen after user responds]

### Extraction Details (populated after successful extraction)
**Extraction Method**: [automatic-pbitools | manual-pending | none]
**Extraction Status**: [success | pending | n/a]
**Extracted Folder Path**: <path>
**pbi-tools Version**: <version>

### Project Structure (populated after validation)
**Semantic Model Path**: <path>
**TMDL Structure**: [validated | invalid]
**Compilation Required**: [true | false]

### Metadata
**format**: <pbip|pbi-tools|pbix-extracted-pbitools>
**requires_compilation**: <true|false>
**validated_project_path**: <path-to-use-for-analysis>
```

---

## Detailed Step-by-Step Flow

### Initial Invocation

**Command (evaluate-pbi-project-file):**
1. Parse `--project` argument
2. Create scratchpad folder
3. Create empty findings.md
4. Invoke agent with:
   ```
   project_path: <from --project>
   findings_file_path: <scratchpad-path>/findings.md
   user_action: none  # first invocation
   ```

**Agent (powerbi-verify-pbiproject-folder-setup):**
1. Detect format:
   - Check for .pbip file → Format: pbip
   - Check for .pbixproj.json → Format: pbi-tools
   - Check if .pbix file → Format: pbix
   - None found → Format: unknown

2. Based on format, write Prerequisites section:

   **If format = pbip:**
   ```yaml
   Status: validated
   Action Type: none
   Format Detected: pbip
   Project Path: <original-path>
   TMDL Structure: validated
   Compilation Required: false
   validated_project_path: <original-path>
   ```
   Return to command

   **If format = pbi-tools:**
   ```yaml
   Status: validated
   Action Type: none
   Format Detected: pbi-tools
   Project Path: <original-path>
   TMDL Structure: validated
   Compilation Required: true
   validated_project_path: <original-path>
   ```
   Return to command

   **If format = pbix:**
   ```yaml
   Status: action_required
   Action Type: pbix_extraction
   Format Detected: pbix
   Project Path: <pbix-file-path>
   Original PBIX: <pbix-file-path>

   Required Action: "PBIX file needs extraction to folder format"
   User Choices Available: "[Y] Extract with pbi-tools | [N] Manual extraction | [I] Install pbi-tools"
   Next Steps: "Command will prompt user for choice"
   ```
   Return to command

   **If format = unknown:**
   ```yaml
   Status: error
   Action Type: invalid_format
   Format Detected: unknown
   Project Path: <original-path>

   Error Message: "Path does not contain .pbip, .pbix, or pbi-tools structure"
   Files Found: [list of files in directory]
   ```
   Return to command

**Command reads Prerequisites:**
1. Parse YAML-style fields from Prerequisites section
2. Read `Status` field
3. Branch based on status:

   **If Status = validated:**
   - Extract `validated_project_path`
   - Display success message
   - Continue to Phase 2 (problem clarification)

   **If Status = action_required:**
   - Read `Action Type`
   - Read `User Choices Available`
   - Prompt user accordingly

   **If Status = error:**
   - Read `Error Message`
   - Display error to user
   - Exit workflow

---

### User Interaction for PBIX Extraction

**Command prompts user:**
```
ℹ️  PBIX File Detected

You've provided a .pbix file: <filename>

To analyze this file, it needs to be extracted to a folder structure.

Do you have pbi-tools CLI installed?

[Y] Yes - Extract automatically with pbi-tools
[N] No - Show me manual extraction instructions
[I] Help me install pbi-tools first

Choose an option: _
```

**User selects [Y]:**

**Command:**
1. Check if pbi-tools exists:
   ```bash
   where pbi-tools  # Windows
   which pbi-tools  # Linux/Mac
   ```

2. **If pbi-tools found:**
   - Display: "✓ pbi-tools found at: <path>"
   - Re-invoke agent with:
     ```
     project_path: <pbix-file-path>
     findings_file_path: <scratchpad-path>/findings.md
     user_action: extract_with_pbitools
     ```

3. **If pbi-tools NOT found:**
   - Display: "❌ pbi-tools not found in PATH"
   - Re-prompt user with [N] or [I] options only

**Agent (2nd invocation with user_action=extract_with_pbitools):**
1. Execute extraction:
   ```bash
   pbi-tools extract "<pbix-file-path>"
   ```

2. **If extraction succeeds:**
   - Determine extracted folder path
   - Validate TMDL structure
   - Update Prerequisites section:
     ```yaml
     Status: validated
     Action Type: none
     Format Detected: pbix-extracted-pbitools
     Original PBIX: <pbix-file-path>
     Extraction Method: automatic-pbitools
     Extraction Status: success
     Extracted Folder Path: <extracted-path>
     pbi-tools Version: <version>
     TMDL Structure: validated
     Compilation Required: true
     validated_project_path: <extracted-path>
     ```
   - Return to command

3. **If extraction fails:**
   - Update Prerequisites section:
     ```yaml
     Status: error
     Action Type: extraction_failed
     Error Message: <pbi-tools error output>
     Suggested Fix: "Check PBIX file integrity, ensure it's not password protected"
     ```
   - Return to command

**Command reads updated Prerequisites:**
- If Status = validated → Continue to analysis
- If Status = error → Display error, exit

---

**User selects [N] (Manual extraction):**

**Command:**
1. Display manual instructions:
   ```
   📋 Manual PBIX Conversion Instructions

   To analyze this .pbix file, convert it to Power BI Project format:

   1. Open Power BI Desktop
   2. File → Open → Select: <pbix-file-path>
   3. File → Save As → Power BI Project
   4. Choose a location and name
   5. A folder with .pbip file will be created

   After conversion, re-run this command with the project folder:
   /evaluate-pbi-project-file \
     --project "<converted-project-folder>" \
     --description "<description>"
   ```

2. Update Prerequisites section (via direct write, not agent):
   ```yaml
   Status: action_required
   Action Type: manual_extraction_pending
   User Action: Manual conversion to .pbip format required
   ```

3. Exit workflow gracefully (exit code 0)

---

**User selects [I] (Install pbi-tools):**

**Command:**
1. Display installation guide:
   ```
   📦 pbi-tools Installation Guide

   Windows - Standalone:
   1. Download: https://github.com/pbi-tools/pbi-tools/releases
   2. Extract to: C:\tools\pbi-tools\
   3. Add to PATH (optional)
   4. Verify: pbi-tools --version

   Windows - Chocolatey:
   choco install pbi-tools

   Cross-platform - .NET:
   dotnet tool install -g pbi-tools

   After installation, re-run this command and select [Y].
   ```

2. Update Prerequisites section:
   ```yaml
   Status: action_required
   Action Type: pbitools_install_pending
   User Action: pbi-tools installation required
   ```

3. Exit workflow gracefully (exit code 0)

---

## Key Design Decisions

### 1. Agent is Stateless
- Each invocation is independent
- Agent doesn't remember previous calls
- All state is in findings.md Prerequisites section

### 2. Command is Stateful
- Command orchestrates the full workflow
- Command reads agent output and decides next steps
- Command handles ALL user interaction

### 3. Prerequisites Section is Single Source of Truth
- Command reads this to determine status
- Agent writes this to communicate results
- Section is updated progressively (not rewritten each time)

### 4. User Actions Never in Agent
- Agent documents what's needed
- Command prompts user
- Command passes user choice back to agent

### 5. Idempotent Agent
- Can be called multiple times with different parameters
- `user_action` parameter tells agent what to do:
  - `none`: Initial detection/validation
  - `extract_with_pbitools`: Perform extraction
  - Other actions as needed

---

## Example: Complete PBIX Workflow

**User runs:**
```bash
/evaluate-pbi-project-file --project "C:\Reports\Sales.pbix" --description "Fix total sales"
```

**Step 1: Command parses args, creates scratchpad**
- Creates: `agent_scratchpads/20251027-143000-fix-total-sales/findings.md`

**Step 2: Command invokes agent (1st time)**
```
project_path: C:\Reports\Sales.pbix
findings_file_path: agent_scratchpads/.../findings.md
user_action: none
```

**Step 3: Agent detects .pbix, writes Prerequisites**
```yaml
Status: action_required
Action Type: pbix_extraction
Format Detected: pbix
User Choices Available: [Y/N/I]
```

**Step 4: Command reads Prerequisites, sees action_required**

**Step 5: Command prompts user**
```
Do you have pbi-tools? [Y/N/I]
```

**Step 6: User selects [Y]**

**Step 7: Command checks for pbi-tools**
```bash
where pbi-tools  # Found: C:\tools\pbi-tools\pbi-tools.exe
```

**Step 8: Command re-invokes agent (2nd time)**
```
project_path: C:\Reports\Sales.pbix
findings_file_path: agent_scratchpads/.../findings.md
user_action: extract_with_pbitools
```

**Step 9: Agent extracts PBIX**
```bash
pbi-tools extract "C:\Reports\Sales.pbix"
# Creates: C:\Reports\Sales\ folder
```

**Step 10: Agent validates extraction, updates Prerequisites**
```yaml
Status: validated
Format Detected: pbix-extracted-pbitools
Extraction Status: success
Extracted Folder Path: C:\Reports\Sales\
validated_project_path: C:\Reports\Sales\
```

**Step 11: Command reads updated Prerequisites, sees validated**

**Step 12: Command continues to Phase 2 (problem clarification)**

---

## Implementation Checklist

### Agent Changes Needed:
- [ ] Remove all user prompting code (display messages)
- [ ] Accept `user_action` parameter
- [ ] Write structured Prerequisites section (YAML-like format)
- [ ] Return status via Prerequisites (not console output)
- [ ] Handle `user_action=extract_with_pbitools` to perform extraction
- [ ] Update Prerequisites section (not replace) on re-invocation

### Command Changes Needed:
- [ ] Invoke agent at start of Phase 1
- [ ] Read Prerequisites section from findings.md
- [ ] Parse status, action_type, and other fields
- [ ] Branch logic based on status
- [ ] Prompt user for PBIX extraction choice
- [ ] Check for pbi-tools if user selects [Y]
- [ ] Re-invoke agent with user_action parameter
- [ ] Display manual instructions if user selects [N]
- [ ] Display install guide if user selects [I]
- [ ] Extract validated_project_path and continue analysis

### Prerequisites Section Parser:
- [ ] Create helper function to parse Prerequisites YAML-like format
- [ ] Extract key fields: status, action_type, validated_project_path
- [ ] Handle missing fields gracefully

---

## Benefits of This Design

✅ **Clear separation of concerns**: Agent detects/acts, Command orchestrates
✅ **User interaction in one place**: All prompts in command, not scattered
✅ **Testable**: Can test agent independently by mocking findings file
✅ **Resumable**: User can exit and re-run command after manual actions
✅ **Auditable**: Prerequisites section documents full history
✅ **Flexible**: Easy to add new user_action types

---

## Questions to Confirm

1. **Should the Prerequisites section use strict YAML or markdown-formatted YAML?**
   - Option A: Strict YAML (parseable with YAML library)
   - Option B: Markdown with YAML-like format (human-readable, requires custom parser)

2. **Should the agent update the existing Prerequisites section or replace it entirely on re-invocation?**
   - Proposed: Update/append (preserves history)

3. **Should extraction failures allow retry or immediately exit?**
   - Proposed: Immediate exit with error (user can fix and re-run)

4. **Where should extracted folders be created?**
   - Proposed: Same directory as original PBIX (pbi-tools default behavior)

5. **Should the command store original command args in Prerequisites for re-run instructions?**
   - Proposed: Yes, useful for manual extraction instructions

---

## Next Steps After Design Approval

1. Update `powerbi-verify-pbiproject-folder-setup.md` agent
2. Update `evaluate-pbi-project-file.md` command (Phase 1)
3. Create Prerequisites parser helper
4. Test all paths (pbip, pbi-tools, pbix with [Y/N/I], invalid)
5. Update `implement-deploy-test-pbi-project-file.md` to read Prerequisites

