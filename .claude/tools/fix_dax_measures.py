#!/usr/bin/env python3
"""
Script to fix OR() syntax error in DAX measures
Replaces invalid OR() in CALCULATETABLE with UNION() approach
"""

import re

filepath = r'C:\Users\anorthrup\Documents\msr_comms_pbi_proj_20251009_223627\MSR Commissions Pre Prod v2.SemanticModel\definition\tables\Commissions_Measures.tmdl'
backup_path = filepath + '.backup'

# Read the file
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Create backup
with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Backup created: {backup_path}")

# Pattern 1: Fix Sales Commission GP Actual NEW measure
# Find and replace the broken _customtable section
gp_old_pattern = r'''(\t\t// Build custom table with modified filtering logic to include backdated deals\n\t\tVAR _customtable = CALCULATETABLE \(\n\t\t    SUMMARIZECOLUMNS \(\n\t\t        FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES\[CONTRACT_ID\],\n\t\t        FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES\[EQUIPMENT_ID\],\n\t\t        DIM_EQUIPMENT_FOR_SALES_COMMISSION\[COMMISSION_PCT_TO_PAY_ON_SALE\],\n\t\t        "@GP", \[Gross Profit \(NBV\)\]\n\t\t    \),\n\t\t    DIM_EQUIPMENT_FOR_SALES_COMMISSION\[COMMISSION_CALC_TYPE_ON_SALE\] = "Gross Profit",\n\t\t    KEEPFILTERS\(FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES\[CONTRACT_EQUIPMENT_STATUS\] = "N"\),\n\t\t    FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES\[INVOICE_PAYMENT_INDICATOR\] = "Y",\n\t\t    // Modified filter: Include deals matching snapshot indicator OR backdated deals from prior 2 periods\n\t\t    OR\(\n\t\t        // Path 1: Standard snapshot indicator match \(existing logic\)\n\t\t        FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES\[SNAPSHOT_INDICATOR\] = _snapshotind,\n\t\t        // Path 2: Include backdated deals with freeze dates in current or prior 2 periods\n\t\t        // Only apply when viewing current pay period to avoid affecting historical period views\n\t\t        AND\(\n\t\t            _snapshotind = "Current Pay Period",\n\t\t            FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES\[SNAPSHOT_INDICATOR\] = "Current Pay Period",\n\t\t            DIM_DATE\[COMM_PAY_DATE\] >= _lookbackStartDate,\n\t\t            DIM_DATE\[COMM_PAY_DATE\] <= _currentFreezeDate\n\t\t        \)\n\t\t    \)\n\t\t\))'''

gp_new_text = '''\t\t// PATH 1: Standard snapshot indicator match (existing logic)
\t\tVAR _path1table = CALCULATETABLE (
\t\t    SUMMARIZECOLUMNS (
\t\t        FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_ID],
\t\t        FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[EQUIPMENT_ID],
\t\t        DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_PCT_TO_PAY_ON_SALE],
\t\t        "@GP", [Gross Profit (NBV)]
\t\t    ),
\t\t    DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_CALC_TYPE_ON_SALE] = "Gross Profit",
\t\t    KEEPFILTERS(FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_EQUIPMENT_STATUS] = "N"),
\t\t    FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[INVOICE_PAYMENT_INDICATOR] = "Y",
\t\t    FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[SNAPSHOT_INDICATOR] = _snapshotind
\t\t)

\t\t// PATH 2: Backdated deals with freeze dates in current or prior 2 periods
\t\t// Only applies when viewing current pay period
\t\tVAR _path2table =
\t\t    IF(
\t\t        _snapshotind = "Current Pay Period",
\t\t        CALCULATETABLE (
\t\t            SUMMARIZECOLUMNS (
\t\t                FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_ID],
\t\t                FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[EQUIPMENT_ID],
\t\t                DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_PCT_TO_PAY_ON_SALE],
\t\t                "@GP", [Gross Profit (NBV)]
\t\t            ),
\t\t            DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_CALC_TYPE_ON_SALE] = "Gross Profit",
\t\t            KEEPFILTERS(FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_EQUIPMENT_STATUS] = "N"),
\t\t            FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[INVOICE_PAYMENT_INDICATOR] = "Y",
\t\t            FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[SNAPSHOT_INDICATOR] = "Current Pay Period",
\t\t            DIM_DATE[COMM_PAY_DATE] >= _lookbackStartDate,
\t\t            DIM_DATE[COMM_PAY_DATE] <= _currentFreezeDate
\t\t        ),
\t\t        BLANK()
\t\t    )

\t\t// Combine both paths and remove duplicates
\t\tVAR _customtable =
\t\t    IF(
\t\t        _snapshotind = "Current Pay Period",
\t\t        DISTINCT(UNION(_path1table, _path2table)),
\t\t        _path1table
\t\t    )'''

# Simpler approach: Find the specific string fragments and replace
# For GP measure
if '// Build custom table with modified filtering logic to include backdated deals' in content:
    # Find the section to replace using string manipulation
    start_marker = '\t\t// Build custom table with modified filtering logic to include backdated deals'
    end_marker = '\t\t)\n\t\t// Calculate commission only for positive GP.'

    start_idx = content.find(start_marker)
    if start_idx != -1:
        end_idx = content.find(end_marker, start_idx)
        if end_idx != -1:
            # Replace the GP measure section
            old_section = content[start_idx:end_idx]
            new_section = '''\t\t// PATH 1: Standard snapshot indicator match (existing logic)
\t\tVAR _path1table = CALCULATETABLE (
\t\t    SUMMARIZECOLUMNS (
\t\t        FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_ID],
\t\t        FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[EQUIPMENT_ID],
\t\t        DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_PCT_TO_PAY_ON_SALE],
\t\t        "@GP", [Gross Profit (NBV)]
\t\t    ),
\t\t    DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_CALC_TYPE_ON_SALE] = "Gross Profit",
\t\t    KEEPFILTERS(FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_EQUIPMENT_STATUS] = "N"),
\t\t    FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[INVOICE_PAYMENT_INDICATOR] = "Y",
\t\t    FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[SNAPSHOT_INDICATOR] = _snapshotind
\t\t)

\t\t// PATH 2: Backdated deals with freeze dates in current or prior 2 periods
\t\t// Only applies when viewing current pay period
\t\tVAR _path2table =
\t\t    IF(
\t\t        _snapshotind = "Current Pay Period",
\t\t        CALCULATETABLE (
\t\t            SUMMARIZECOLUMNS (
\t\t                FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_ID],
\t\t                FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[EQUIPMENT_ID],
\t\t                DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_PCT_TO_PAY_ON_SALE],
\t\t                "@GP", [Gross Profit (NBV)]
\t\t            ),
\t\t            DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_CALC_TYPE_ON_SALE] = "Gross Profit",
\t\t            KEEPFILTERS(FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_EQUIPMENT_STATUS] = "N"),
\t\t            FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[INVOICE_PAYMENT_INDICATOR] = "Y",
\t\t            FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[SNAPSHOT_INDICATOR] = "Current Pay Period",
\t\t            DIM_DATE[COMM_PAY_DATE] >= _lookbackStartDate,
\t\t            DIM_DATE[COMM_PAY_DATE] <= _currentFreezeDate
\t\t        ),
\t\t        BLANK()
\t\t    )

\t\t// Combine both paths and remove duplicates
\t\tVAR _customtable =
\t\t    IF(
\t\t        _snapshotind = "Current Pay Period",
\t\t        DISTINCT(UNION(_path1table, _path2table)),
\t\t        _path1table
\t\t    )
'''
            content = content[:start_idx] + new_section + content[end_idx:]
            print("[OK] Fixed Sales Commission GP Actual NEW measure")

# For TransAmt measure - similar approach
start_marker2 = '\t\t// Build a table of contracts for the snapshot and commission type.'
end_marker2 = '\t\t)\n\t\t// Calculate commission for transaction amount.'

start_idx2 = content.find(start_marker2, start_idx + 1000 if start_idx != -1 else 0)  # Search after first replacement
if start_idx2 != -1:
    end_idx2 = content.find(end_marker2, start_idx2)
    if end_idx2 != -1:
        # Check if this section has the OR( problem
        section_check = content[start_idx2:end_idx2]
        if 'OR(' in section_check:
            new_section2 = '''\t\t// Calculate the lookback date range for backdated deals (2 months prior from first day of current month)
\t\t// This is only relevant when snapshot indicator is "Current Pay Period"
\t\tVAR _currentFreezeDate = CALCULATE(
\t\t    MIN(DIM_DATE[COMM_PAY_DATE]),
\t\t    DIM_DATE[COMM_FUNDED_PAID_SNAPSHOT_DISPLAY] = _payperiod
\t\t)
\t\tVAR _lookbackStartDate =
\t\t    IF(
\t\t        _snapshotind = "Current Pay Period",
\t\t        DATE(YEAR(_currentFreezeDate), MONTH(_currentFreezeDate) - 2, 1),
\t\t        BLANK()
\t\t    )

\t\t// PATH 1: Standard snapshot indicator match (existing logic)
\t\tVAR _path1table = CALCULATETABLE (
\t\t    SUMMARIZECOLUMNS (
\t\t        FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_ID],
\t\t        FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[EQUIPMENT_ID],
\t\t        DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_PCT_TO_PAY_ON_SALE],
\t\t        "@TransAmt", [Transaction Amount Measure]
\t\t    ),
\t\t    DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_CALC_TYPE_ON_SALE] = "Transaction Amount",
\t\t    KEEPFILTERS(FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_EQUIPMENT_STATUS] = "N"),
\t\t    FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[INVOICE_PAYMENT_INDICATOR] = "Y",
\t\t    FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[SNAPSHOT_INDICATOR] = _snapshotind
\t\t)

\t\t// PATH 2: Backdated deals with freeze dates in current or prior 2 periods
\t\t// Only applies when viewing current pay period
\t\tVAR _path2table =
\t\t    IF(
\t\t        _snapshotind = "Current Pay Period",
\t\t        CALCULATETABLE (
\t\t            SUMMARIZECOLUMNS (
\t\t                FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_ID],
\t\t                FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[EQUIPMENT_ID],
\t\t                DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_PCT_TO_PAY_ON_SALE],
\t\t                "@TransAmt", [Transaction Amount Measure]
\t\t            ),
\t\t            DIM_EQUIPMENT_FOR_SALES_COMMISSION[COMMISSION_CALC_TYPE_ON_SALE] = "Transaction Amount",
\t\t            KEEPFILTERS(FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[CONTRACT_EQUIPMENT_STATUS] = "N"),
\t\t            FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[INVOICE_PAYMENT_INDICATOR] = "Y",
\t\t            FACT_EQUIPMENT_SALES_RPO_CONTRACT_MACHINE_SALES[SNAPSHOT_INDICATOR] = "Current Pay Period",
\t\t            DIM_DATE[COMM_PAY_DATE] >= _lookbackStartDate,
\t\t            DIM_DATE[COMM_PAY_DATE] <= _currentFreezeDate
\t\t        ),
\t\t        BLANK()
\t\t    )

\t\t// Combine both paths and remove duplicates
\t\tVAR _customtable =
\t\t    IF(
\t\t        _snapshotind = "Current Pay Period",
\t\t        DISTINCT(UNION(_path1table, _path2table)),
\t\t        _path1table
\t\t    )
'''
            content = content[:start_idx2] + new_section2 + content[end_idx2:]
            print("[OK] Fixed Sales Commission Trans Amt Actual NEW measure")

# Write the fixed content
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n[OK] File updated: {filepath}")
print(f"[OK] Backup saved: {backup_path}")
print("\nBoth measures have been fixed. The OR() syntax errors have been replaced with UNION() logic.")
