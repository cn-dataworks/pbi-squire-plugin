#!/usr/bin/env python3
"""Fix PSSR Misc GP measure by adding triple backticks"""

file_path = r"C:\Users\anorthrup\Desktop\Power BI Projects\PSSR Comms UC Issue_20251110_151020\PSSR Commissions Pre Prod v3.SemanticModel\definition\tables\Commissions_Measures.tmdl"

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and fix the PSSR Misc GP measure
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]

    # Find the PSSR Misc GP measure definition
    if "'PSSR Misc GP'" in line and "measure" in line:
        # Add the line with triple backticks
        new_lines.append(line.rstrip() + " ```\n")
        i += 1

        # Copy all lines until we hit the first lineageTag (the incorrect one)
        while i < len(lines):
            if 'lineageTag: c3d4e5f6' in lines[i]:
                # Skip the duplicate lineageTag and annotation that are incorrectly in the DAX
                i += 1  # Skip lineageTag line
                if i < len(lines) and lines[i].strip() == '':
                    i += 1  # Skip empty line
                if i < len(lines) and 'annotation PBI_FormatHint' in lines[i]:
                    i += 1  # Skip annotation line

                # Add closing triple backticks and proper properties
                new_lines.append('\t\t```\n')
                new_lines.append('\t\tformatString: \\$#,0.00;(\\$#,0.00);\\$#,0.00\n')

                # Now add the real lineageTag (next one)
                if i < len(lines) and 'lineageTag:' in lines[i]:
                    new_lines.append(lines[i])
                    i += 1

                # Add empty line if present
                if i < len(lines) and lines[i].strip() == '':
                    new_lines.append(lines[i])
                    i += 1

                # Add annotation if present
                if i < len(lines) and 'annotation PBI_FormatHint' in lines[i]:
                    new_lines.append(lines[i])
                    i += 1

                break
            else:
                new_lines.append(lines[i])
                i += 1
        continue

    new_lines.append(line)
    i += 1

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fixed PSSR Misc GP measure - added triple backticks and formatString")
