#!/usr/bin/env python3
"""
Robust TMDL File Editor for Power BI Projects
Handles tab-based indentation and measure replacement
"""

import re
import sys
from pathlib import Path

def read_file_with_tabs(filepath):
    """Read file preserving exact tab characters"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file_with_tabs(filepath, content):
    """Write file preserving exact tab characters"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def extract_measure(content, measure_name):
    """
    Extract a complete measure definition by name
    Returns (start_pos, end_pos, measure_text) or None if not found
    """
    # Escape special regex characters in measure name
    escaped_name = re.escape(measure_name)

    # Pattern to find the measure start
    # TMDL format: \tmeasure 'Name' =
    measure_start_pattern = rf"(\t+)measure '{escaped_name}' =\n"

    match = re.search(measure_start_pattern, content)
    if not match:
        print(f"ERROR: Measure '{measure_name}' not found")
        return None

    start_pos = match.start()
    indent_level = match.group(1)  # Capture the tab indentation

    # Find the end of the measure
    # A measure ends when we hit another top-level element at the same indent level
    # Look for: formatString:, displayFolder:, lineageTag:, or next measure/column/table

    # Start searching after the measure declaration
    search_start = match.end()

    # Pattern for end markers (properties at same indent level as measure)
    # These are measure properties that come after the DAX code
    end_pattern = rf"\n{indent_level}(formatString:|displayFolder:|lineageTag:|measure |column |table )"

    end_match = re.search(end_pattern, content[search_start:])
    if not end_match:
        # Measure goes to end of file
        end_pos = len(content)
    else:
        # End position is where the property/next element starts
        end_pos = search_start + end_match.start() + 1  # +1 to include the \n

    measure_text = content[start_pos:end_pos]
    return (start_pos, end_pos, measure_text, indent_level)

def replace_measure_dax(measure_text, new_dax_body, indent_level):
    """
    Replace just the DAX body of a measure, preserving properties

    measure_text: Full measure text including properties
    new_dax_body: Just the DAX code (VARs and RETURN)
    indent_level: The tab indentation level (e.g., '\t')
    """
    # Find where DAX body starts (after the = sign and newline)
    # Pattern: measure 'Name' =\n<DAX body>
    measure_header_pattern = r"(measure '[^']+' =)\n"

    match = re.search(measure_header_pattern, measure_text)
    if not match:
        print("ERROR: Could not find measure header")
        return None

    header_end = match.end()

    # Find where DAX body ends (before formatString/displayFolder/etc)
    # These properties are at the same indent level as 'measure'
    properties_pattern = rf"\n{indent_level}(formatString:|displayFolder:|lineageTag:|annotation )"

    prop_match = re.search(properties_pattern, measure_text)
    if prop_match:
        dax_end = prop_match.start() + 1  # +1 to include the \n before property
        properties = measure_text[dax_end:]
    else:
        # No properties found, DAX goes to end
        dax_end = len(measure_text)
        properties = ""

    # Construct new measure
    header = measure_text[:header_end]

    # Ensure new_dax_body has proper indentation (add one more tab level than measure)
    # The DAX body should be indented with indent_level + one more tab
    dax_indent = indent_level + '\t'

    # Process new_dax_body: ensure each line has proper indentation
    dax_lines = new_dax_body.strip().split('\n')
    indented_dax_lines = [dax_indent + line if line.strip() else line for line in dax_lines]
    formatted_dax = '\n'.join(indented_dax_lines) + '\n'

    new_measure = header + formatted_dax + properties
    return new_measure

def replace_measure_in_file(filepath, measure_name, new_dax_body):
    """
    Replace a specific measure's DAX body in a TMDL file

    Args:
        filepath: Path to the TMDL file
        measure_name: Exact name of the measure (without quotes)
        new_dax_body: New DAX code (VARs and RETURN statements)

    Returns:
        True if successful, False otherwise
    """
    # Read file
    content = read_file_with_tabs(filepath)

    # Extract measure
    result = extract_measure(content, measure_name)
    if not result:
        return False

    start_pos, end_pos, measure_text, indent_level = result

    # Replace DAX body
    new_measure_text = replace_measure_dax(measure_text, new_dax_body, indent_level)
    if not new_measure_text:
        return False

    # Build new file content
    new_content = content[:start_pos] + new_measure_text + content[end_pos:]

    # Create backup
    backup_path = str(filepath) + '.backup'
    write_file_with_tabs(backup_path, content)
    print(f"[OK] Backup created: {backup_path}")

    # Write new content
    write_file_with_tabs(filepath, new_content)
    print(f"[OK] Measure '{measure_name}' updated successfully")

    return True

# DAX code for both measures (without indentation - will be added automatically)
GP_MEASURE_DAX = """// Get the selected pay period.
VAR _payperiod = SELECTEDVALUE(DIM_DATE[COMM_FUNDED_PAID_SNAPSHOT_DISPLAY])
// Find the snapshot indicator for the pay period.
VAR _snapshotind = CALCULATE(
    MIN(DIM_DATE[SNAPSHOT_INDICATOR]),
    DIM_DATE[COMM_FUNDED_PAID_SNAPSHOT_DISPLAY] = _payperiod
)
// Calculate the lookback date range for backdated deals (2 months prior from first day of current month)
// This is only relevant when snapshot indicator is "Current Pay Period"
VAR _currentFreezeDate = CALCULATE(
    MIN(DIM_DATE[COMM_PAY_DATE]),
    DIM_DATE[COMM_FUNDED_PAID_SNAPSHOT_DISPLAY] = _payperiod
)
VAR _lookbackStartDate =
    IF(
        _snapshotind = "Current Pay Period",
        DATE(YEAR(_currentFreezeDate), MONTH(_currentFreezeDate) - 2, 1),
        BLANK()
    )

// PATH 1: Standard snapshot indicator match (existing logic)
VAR _path1table = CALCULATETABLE (
    SUMMARIZECOLUMNS (
        FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_ID],
        FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[EQUIPMENT_ID],
        DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_PCT_TO_PAY_ON_SALE],
        "@GP", [Gross Profit (NBV)]
    ),
    DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_CALC_TYPE_ON_SALE] = "Gross Profit",
    KEEPFILTERS(FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_EQUIPMENT_STATUS] = "N"),
    FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[INVOICE_PAYMENT_INDICATOR] = "Y",
    FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[SNAPSHOT_INDICATOR] = _snapshotind
)

// PATH 2: Backdated deals with freeze dates in current or prior 2 periods
// Only applies when viewing current pay period
VAR _path2table =
    IF(
        _snapshotind = "Current Pay Period",
        CALCULATETABLE (
            SUMMARIZECOLUMNS (
                FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_ID],
                FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[EQUIPMENT_ID],
                DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_PCT_TO_PAY_ON_SALE],
                "@GP", [Gross Profit (NBV)]
            ),
            DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_CALC_TYPE_ON_SALE] = "Gross Profit",
            KEEPFILTERS(FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_EQUIPMENT_STATUS] = "N"),
            FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[INVOICE_PAYMENT_INDICATOR] = "Y",
            FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[SNAPSHOT_INDICATOR] = "Current Pay Period",
            DIM_DATE[COMM_PAY_DATE] >= _lookbackStartDate,
            DIM_DATE[COMM_PAY_DATE] <= _currentFreezeDate
        ),
        BLANK()
    )

// Combine both paths and remove duplicates
VAR _customtable =
    IF(
        _snapshotind = "Current Pay Period",
        DISTINCT(UNION(_path1table, _path2table)),
        _path1table
    )

// Calculate commission only for positive GP.
VAR _comms =
    CALCULATE(
    SUMX(
        _customtable,
        //  only compute commissions for GP > 0 (don't penalize Sales Rep)
        IF(
            [@GP] > 0,
            [@GP] * [COMMISSION_PCT_TO_PAY_ON_SALE],
            0
        )
    )
)
// Get total RPO pay for new equipment.
VAR _rpopay = [Total RPO Pay NEW]
// Subtract RPO pay from commission.
VAR _result = _comms - _rpopay
// Return the result.
RETURN
    _result"""

TRANS_AMT_MEASURE_DAX = """// Get the selected pay period.
VAR _payperiod = SELECTEDVALUE(DIM_DATE[COMM_FUNDED_PAID_SNAPSHOT_DISPLAY])
// Find the snapshot indicator for the pay period.
VAR _snapshotind = CALCULATE(
    MIN(DIM_DATE[SNAPSHOT_INDICATOR]),
    DIM_DATE[COMM_FUNDED_PAID_SNAPSHOT_DISPLAY] = _payperiod
)
// Calculate the lookback date range for backdated deals (2 months prior from first day of current month)
// This is only relevant when snapshot indicator is "Current Pay Period"
VAR _currentFreezeDate = CALCULATE(
    MIN(DIM_DATE[COMM_PAY_DATE]),
    DIM_DATE[COMM_FUNDED_PAID_SNAPSHOT_DISPLAY] = _payperiod
)
VAR _lookbackStartDate =
    IF(
        _snapshotind = "Current Pay Period",
        DATE(YEAR(_currentFreezeDate), MONTH(_currentFreezeDate) - 2, 1),
        BLANK()
    )

// PATH 1: Standard snapshot indicator match (existing logic)
VAR _path1table = CALCULATETABLE (
    SUMMARIZECOLUMNS (
        FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_ID],
        FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[EQUIPMENT_ID],
        DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_PCT_TO_PAY_ON_SALE],
        "@TransAmt", [Transaction Amount Measure]
    ),
    DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_CALC_TYPE_ON_SALE] = "Transaction Amount",
    KEEPFILTERS(FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_EQUIPMENT_STATUS] = "N"),
    FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[INVOICE_PAYMENT_INDICATOR] = "Y",
    FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[SNAPSHOT_INDICATOR] = _snapshotind
)

// PATH 2: Backdated deals with freeze dates in current or prior 2 periods
// Only applies when viewing current pay period
VAR _path2table =
    IF(
        _snapshotind = "Current Pay Period",
        CALCULATETABLE (
            SUMMARIZECOLUMNS (
                FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_ID],
                FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[EQUIPMENT_ID],
                DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_PCT_TO_PAY_ON_SALE],
                "@TransAmt", [Transaction Amount Measure]
            ),
            DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_CALC_TYPE_ON_SALE] = "Transaction Amount",
            KEEPFILTERS(FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_EQUIPMENT_STATUS] = "N"),
            FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[INVOICE_PAYMENT_INDICATOR] = "Y",
            FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[SNAPSHOT_INDICATOR] = "Current Pay Period",
            DIM_DATE[COMM_PAY_DATE] >= _lookbackStartDate,
            DIM_DATE[COMM_PAY_DATE] <= _currentFreezeDate
        ),
        BLANK()
    )

// Combine both paths and remove duplicates
VAR _customtable =
    IF(
        _snapshotind = "Current Pay Period",
        DISTINCT(UNION(_path1table, _path2table)),
        _path1table
    )

// Calculate commission for transaction amount.
VAR _comms = CALCULATE(
    SUMX(
        _customtable,
        [@TransAmt] * [COMMISSION_PCT_TO_PAY_ON_SALE]
    )
)
// Get total RPO pay for new equipment.
VAR _rpopay = [Total RPO Pay NEW]
// Subtract RPO pay from commission.
VAR _result = _comms - _rpopay
// Return the result.
RETURN
    _result"""

if __name__ == "__main__":
    filepath = r'C:\Users\anorthrup\Documents\msr_comms_pbi_proj_20251009_223627\MSR Commissions Pre Prod v2.SemanticModel\definition\tables\Commissions_Measures.tmdl'

    print("=== Robust TMDL Editor ===")
    print(f"Target file: {filepath}\n")

    # Replace Measure 1
    print("Step 1: Replacing 'Sales Commission GP Actual NEW' measure...")
    success1 = replace_measure_in_file(filepath, "Sales Commission GP Actual NEW", GP_MEASURE_DAX)

    if success1:
        print("[OK] Measure 1 replaced successfully\n")
    else:
        print("[ERROR] Failed to replace Measure 1\n")
        sys.exit(1)

    # Replace Measure 2
    print("Step 2: Replacing 'Sales Commission Trans Amt Actual NEW' measure...")
    success2 = replace_measure_in_file(filepath, "Sales Commission Trans Amt Actual NEW", TRANS_AMT_MEASURE_DAX)

    if success2:
        print("[OK] Measure 2 replaced successfully\n")
    else:
        print("[ERROR] Failed to replace Measure 2\n")
        sys.exit(1)

    print("=== All measures updated successfully ===")
    print("\nNext steps:")
    print("1. Verify the changes")
    print("2. Run DAX validation agent")
    print("3. Test in Power BI Desktop")
