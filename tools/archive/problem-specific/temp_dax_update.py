#!/usr/bin/env python3
"""Apply DAX changes to PSSR Misc Commission and PSSR Misc GP measures"""

file_path = r"C:\Users\anorthrup\Desktop\Power BI Projects\PSSR Comms UC Issue_20251110_135641\PSSR Commissions Pre Prod v3.SemanticModel\definition\tables\Commissions_Measures.tmdl"

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Update PSSR Misc Commission (around line 1957-1964)
# Find the SUMX section and replace it
in_misc_comm = False
in_sumx = False
new_lines = []
i = 0

while i < len(lines):
    line = lines[i]

    # Detect PSSR Misc Commission measure
    if "'PSSR Misc Commission'" in line:
        in_misc_comm = True

    # Detect end of measure
    if in_misc_comm and line.strip().startswith('formatString:'):
        in_misc_comm = False
        in_sumx = False

    # Detect SUMX start in Misc Commission
    if in_misc_comm and 'SUMX(' in line:
        in_sumx = True
        new_lines.append(line)
        i += 1
        # Skip table name line
        new_lines.append(lines[i])
        i += 1

        # Now replace the calculation expression (lines with UNIT_SELL_PRICE through PCT_INVOICED_TO_CUST)
        # Skip old lines until we hit the closing ),
        start_calc = i
        while i < len(lines) and '),\n' not in lines[i] and '),' not in lines[i]:
            i += 1

        # Insert new code
        indent = '\t\t        '
        new_lines.append(indent + 'VAR _line_gp =\n')
        new_lines.append(indent + '    (FACT_PS_INVOICE_DETAILS_COMMISSIONS[UNIT_SELL_PRICE] +\n')
        new_lines.append(indent + '    (FACT_PS_INVOICE_DETAILS_COMMISSIONS[UNIT_SELL_PRICE_ADJUSTMENT] * _discountfactor) -\n')
        new_lines.append(indent + '    (FACT_PS_INVOICE_DETAILS_COMMISSIONS[UNIT_COST] * FACT_PS_INVOICE_DETAILS_COMMISSIONS[LINE_ITEM_DISCOUNT_INDICATOR])) *\n')
        new_lines.append(indent + '    FACT_PS_INVOICE_DETAILS_COMMISSIONS[QUANTITY_SOLD] *\n')
        new_lines.append(indent + '    FACT_PS_INVOICE_DETAILS_COMMISSIONS[PCT_INVOICED_TO_CUST]\n')
        new_lines.append(indent + 'VAR _adjusted_line_gp =\n')
        new_lines.append(indent + '    IF(\n')
        new_lines.append(indent + '        FACT_PS_INVOICE_DETAILS_COMMISSIONS[LINE_ITEM_DISCOUNT_INDICATOR] = 0,\n')
        new_lines.append(indent + '        _line_gp * _discountfactor,\n')
        new_lines.append(indent + '        _line_gp\n')
        new_lines.append(indent + '    )\n')
        new_lines.append(indent + 'RETURN _adjusted_line_gp\n')
        new_lines.append('\t\t    ),\n')

        i += 1
        in_sumx = False
        continue

    new_lines.append(line)
    i += 1

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Successfully updated PSSR Misc Commission measure")
print(f"Updated {len(new_lines)} lines total")
