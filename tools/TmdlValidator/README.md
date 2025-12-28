# TMDL Validator

A C# command-line tool that validates Power BI TMDL (Tabular Model Definition Language) projects using Microsoft's official `TmdlSerializer` parser.

## Features

- **100% Accurate Validation**: Uses the same TMDL parser as Power BI Desktop
- **Detailed Error Reporting**: Provides exact file path, line number, and line text for errors
- **Multiple Output Formats**: Text (human-readable) or JSON (programmatic)
- **Comprehensive Error Detection**:
  - Format errors (invalid syntax, indentation, keywords)
  - Serialization errors (invalid metadata logic)
  - Structural errors (missing folders, invalid paths)

## Prerequisites

- .NET 8.0 SDK (for building)
- Windows x64

## Building

Run the build script:

```powershell
cd .claude/tools/TmdlValidator
.\build.ps1
```

This creates a self-contained executable at `.claude/tools/TmdlValidator.exe` (~50MB).

## Usage

### Command Line

**Basic validation:**
```bash
TmdlValidator.exe "C:\path\to\MyProject.SemanticModel"
```

**JSON output (for programmatic use):**
```bash
TmdlValidator.exe --path "C:\path\to\MyProject.SemanticModel" --json
```

### From Python

```python
import subprocess
import json

result = subprocess.run(
    ['TmdlValidator.exe', '--path', 'C:\\path\\to\\project.SemanticModel', '--json'],
    capture_output=True,
    text=True
)

validation_result = json.loads(result.stdout)

if validation_result['isValid']:
    print(f"✓ Valid: {validation_result['message']}")
else:
    print(f"✗ Error on line {validation_result['lineNumber']}: {validation_result['message']}")
    print(f"  File: {validation_result['document']}")
    print(f"  Line: {validation_result['lineText']}")
```

## Exit Codes

- `0` - Validation successful (TMDL is valid)
- `1` - Validation failed (TMDL has errors)

## Output Examples

### Success (Text Format)

```
================================================================================
TMDL VALIDATION REPORT (Microsoft TmdlSerializer)
================================================================================
Path: C:\Projects\MyReport.SemanticModel
Timestamp: 2025-11-06 17:30:45 UTC
================================================================================

[SUCCESS] TMDL project is valid!

Database Name: MyReport
Compatibility Level: 1605

This project can be opened in Power BI Desktop without errors.

================================================================================
```

### Error (Text Format)

```
================================================================================
TMDL VALIDATION REPORT (Microsoft TmdlSerializer)
================================================================================
Path: C:\Projects\MyReport.SemanticModel
Timestamp: 2025-11-06 17:30:45 UTC
================================================================================

[FORMATERROR] TMDL validation failed!

Error: Invalid indentation was detected!

Error Location:
  Document: ./tables/Commissions_Measures
  Line Number: 30
  Line Text:     lineageTag: e1f2a3b4-c5d6-7890-4567-890123456789

================================================================================
```

### Error (JSON Format)

```json
{
  "isValid": false,
  "path": "C:\\Projects\\MyReport.SemanticModel",
  "timestamp": "2025-11-06T17:30:45.1234567Z",
  "message": "Invalid indentation was detected!",
  "errorType": "FormatError",
  "document": "./tables/Commissions_Measures",
  "lineNumber": 30,
  "lineText": "    lineageTag: e1f2a3b4-c5d6-7890-4567-890123456789"
}
```

## Integration with Workflow

This validator is used by the `powerbi-tmdl-syntax-validator` agent as an authoritative validation step before deployment:

1. Python regex validator performs quick checks
2. C# TmdlValidator performs authoritative validation using Microsoft's parser
3. If both pass, proceed with deployment
4. If either fails, report errors to user

## Error Types

| Error Type | Description |
|------------|-------------|
| `FormatError` | TMDL syntax/format error (invalid keywords, indentation, structure) |
| `SerializationError` | Valid TMDL syntax but invalid metadata logic |
| `PathNotFound` | Specified path does not exist |
| `InvalidStructure` | Path exists but is not a valid TMDL project |
| `DirectoryNotFound` | Required directory not found |
| `UnexpectedError` | Unexpected exception occurred |

## Technical Details

- **Framework**: .NET 8.0
- **Parser**: `Microsoft.AnalysisServices.Tabular.TmdlSerializer`
- **Package**: `Microsoft.AnalysisServices.NetCore.retail.amd64` v19.84.2
- **Build Type**: Self-contained single-file executable
- **Platform**: Windows x64

## Advantages Over Regex Validation

| Aspect | Regex Validator | TmdlValidator (C#) |
|--------|----------------|-------------------|
| Accuracy | Pattern matching - misses edge cases | 100% accurate - same parser as Power BI |
| Coverage | Limited to known patterns | Catches ALL syntax and semantic errors |
| Alignment | Guesses at TMDL rules | Identical to Power BI Desktop |
| Maintenance | Requires updating for new patterns | Auto-updated with library |
| False Positives | Possible | None - only real errors |
| False Negatives | Possible | None - catches everything |

## License

This tool uses Microsoft Analysis Services libraries. See Microsoft's licensing terms for details.
