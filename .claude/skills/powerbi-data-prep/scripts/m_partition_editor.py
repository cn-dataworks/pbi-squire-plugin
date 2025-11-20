#!/usr/bin/env python3
"""
M Code Partition Editor for TMDL Files

Safely edit M code in Power BI TMDL partition files with proper tab handling,
indentation, and automatic backups.

Usage:
    # Edit existing partition
    python m_partition_editor.py "<tmdl-file>" --table "<TableName>" --partition "<PartitionName>" --m-code "<m-code-file>"

    # Create new table with M code
    python m_partition_editor.py "<tmdl-file>" --create-table "<TableName>" --m-code "<m-code-file>"

    # Add partition to existing table
    python m_partition_editor.py "<tmdl-file>" --table "<TableName>" --add-partition "<PartitionName>" --m-code "<m-code-file>"
"""

import sys
import os
import re
import argparse
from pathlib import Path
from datetime import datetime

class TMDLPartitionEditor:
    """Editor for M code partitions in TMDL files."""

    TAB = '\t'
    PARTITION_INDENT = 1  # Number of tabs before 'partition'
    PROPERTY_INDENT = 2   # Number of tabs before 'mode:' and 'source ='
    M_CODE_INDENT = 3     # Number of tabs before M code (let/in)

    def __init__(self, tmdl_file):
        self.tmdl_file = Path(tmdl_file)
        if not self.tmdl_file.exists():
            raise FileNotFoundError(f"TMDL file not found: {tmdl_file}")

        self.content = self.tmdl_file.read_text(encoding='utf-8')
        self.lines = self.content.splitlines(keepends=True)

    def create_backup(self):
        """Create backup of original file."""
        backup_path = self.tmdl_file.with_suffix(self.tmdl_file.suffix + '.backup')
        backup_path.write_text(self.content, encoding='utf-8')
        print(f"[BACKUP] Created: {backup_path.name}")
        return backup_path

    def save(self):
        """Save modified content to file."""
        self.tmdl_file.write_text(''.join(self.lines), encoding='utf-8')
        print(f"[SAVE] File updated: {self.tmdl_file}")

    def find_table(self, table_name):
        """Find line number where table definition starts."""
        pattern = rf'^table {re.escape(table_name)}\s*$'
        for i, line in enumerate(self.lines):
            if re.match(pattern, line.strip()):
                return i
        return None

    def find_partition(self, table_name, partition_name):
        """
        Find line range for partition within table.
        Returns (start_line, end_line) or None if not found.
        """
        table_start = self.find_table(table_name)
        if table_start is None:
            return None

        # Find partition start
        partition_pattern = rf'^\t*partition \'{re.escape(partition_name)}\' = m\s*$'
        partition_start = None

        for i in range(table_start + 1, len(self.lines)):
            line = self.lines[i]

            # Found the partition
            if re.match(partition_pattern, line):
                partition_start = i
                break

            # Hit next table or end of current table
            if re.match(r'^table\s+\w+', line.strip()) or re.match(r'^\S', line):
                break

        if partition_start is None:
            return None

        # Find partition end (next partition or next top-level element)
        partition_end = len(self.lines)
        for i in range(partition_start + 1, len(self.lines)):
            line = self.lines[i]

            # Next partition
            if re.match(r'^\t*partition\s+', line):
                partition_end = i
                break

            # Next table or top-level element
            if re.match(r'^table\s+', line.strip()) or re.match(r'^\S', line):
                partition_end = i
                break

        return (partition_start, partition_end)

    def format_m_code(self, m_code):
        """
        Format M code with correct indentation for TMDL partition.

        Args:
            m_code (str): Raw M code (from user or file)

        Returns:
            list[str]: Formatted lines with proper tabs
        """
        # Remove any leading/trailing whitespace
        m_code = m_code.strip()

        # Split into lines
        raw_lines = m_code.splitlines()

        formatted = []
        for line in raw_lines:
            # Remove existing indentation
            stripped = line.lstrip()

            if not stripped:
                # Preserve blank lines
                formatted.append('\n')
                continue

            # Determine indentation level based on content
            if stripped.startswith('let'):
                indent = self.M_CODE_INDENT
            elif stripped.startswith('in'):
                indent = self.M_CODE_INDENT
            elif stripped.startswith('//'):
                # Comments at M code level
                indent = self.M_CODE_INDENT + 1
            else:
                # M code steps (inside let-in)
                indent = self.M_CODE_INDENT + 1

            # Apply tabs
            formatted_line = (self.TAB * indent) + stripped + '\n'
            formatted.append(formatted_line)

        return formatted

    def build_partition_block(self, partition_name, m_code, mode='Import'):
        """
        Build complete partition block with proper formatting.

        Args:
            partition_name (str): Name of partition
            m_code (str): Raw M code
            mode (str): Import, DirectQuery, or Dual

        Returns:
            list[str]: Formatted partition block lines
        """
        block = []

        # Partition declaration
        block.append(f"{self.TAB * self.PARTITION_INDENT}partition '{partition_name}' = m\n")

        # Mode property
        block.append(f"{self.TAB * self.PROPERTY_INDENT}mode: {mode}\n")

        # Source property
        block.append(f"{self.TAB * self.PROPERTY_INDENT}source =\n")

        # M code
        formatted_m = self.format_m_code(m_code)
        block.extend(formatted_m)

        # Blank line after partition
        block.append('\n')

        return block

    def edit_partition(self, table_name, partition_name, new_m_code, mode='Import'):
        """
        Edit existing partition M code.

        Args:
            table_name (str): Table containing partition
            partition_name (str): Partition to edit
            new_m_code (str): New M code
            mode (str): Import, DirectQuery, or Dual

        Returns:
            bool: True if successful
        """
        partition_range = self.find_partition(table_name, partition_name)
        if partition_range is None:
            print(f"[ERROR] Partition '{partition_name}' not found in table '{table_name}'")
            return False

        start, end = partition_range

        # Build new partition block
        new_block = self.build_partition_block(partition_name, new_m_code, mode)

        # Replace old partition with new
        self.lines[start:end] = new_block

        print(f"[SUCCESS] Partition '{partition_name}' in table '{table_name}' updated")
        return True

    def add_partition(self, table_name, partition_name, m_code, mode='Import'):
        """
        Add new partition to existing table.

        Args:
            table_name (str): Table to add partition to
            partition_name (str): Name for new partition
            m_code (str): M code for partition
            mode (str): Import, DirectQuery, or Dual

        Returns:
            bool: True if successful
        """
        table_start = self.find_table(table_name)
        if table_start is None:
            print(f"[ERROR] Table '{table_name}' not found")
            return False

        # Find where to insert (after last partition or after table declaration)
        insert_point = table_start + 1

        # Look for existing partitions
        for i in range(table_start + 1, len(self.lines)):
            line = self.lines[i]

            # If we hit another table or top-level element, insert here
            if re.match(r'^table\s+', line.strip()) or re.match(r'^\S', line):
                insert_point = i
                break

            # If we find a partition, update insert point to after it
            if re.match(r'^\t*partition\s+', line):
                # Find end of this partition
                for j in range(i + 1, len(self.lines)):
                    next_line = self.lines[j]
                    if re.match(r'^\t*partition\s+', next_line) or re.match(r'^table\s+', next_line.strip()) or re.match(r'^\S', next_line):
                        insert_point = j
                        break

        # Build partition block
        new_block = self.build_partition_block(partition_name, m_code, mode)

        # Insert partition
        self.lines[insert_point:insert_point] = new_block

        print(f"[SUCCESS] Partition '{partition_name}' added to table '{table_name}'")
        return True

    def create_table(self, table_name, partition_name, m_code, mode='Import'):
        """
        Create new table with M partition.

        Args:
            table_name (str): Name for new table
            partition_name (str): Name for partition (often same as table name)
            m_code (str): M code for partition
            mode (str): Import, DirectQuery, or Dual

        Returns:
            bool: True if successful
        """
        # Check if table already exists
        if self.find_table(table_name) is not None:
            print(f"[ERROR] Table '{table_name}' already exists")
            return False

        # Build table block
        table_block = []
        table_block.append(f"table {table_name}\n")
        table_block.append('\n')

        # Add partition
        partition_block = self.build_partition_block(partition_name, m_code, mode)
        table_block.extend(partition_block)

        # Append to end of file
        self.lines.extend(table_block)

        print(f"[SUCCESS] Table '{table_name}' created with partition '{partition_name}'")
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Edit M code partitions in TMDL files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Edit existing partition
  python m_partition_editor.py "Sales.tmdl" --table "Sales" --partition "Sales-2024" --m-code "new_code.m"

  # Create new table
  python m_partition_editor.py "model.tmdl" --create-table "DateTable" --m-code "date_table.m"

  # Add partition to table
  python m_partition_editor.py "Sales.tmdl" --table "Sales" --add-partition "Sales-2025" --m-code "sales_2025.m"
        """
    )

    parser.add_argument('tmdl_file', help='Path to TMDL file')
    parser.add_argument('--table', help='Table name (for edit/add operations)')
    parser.add_argument('--partition', help='Partition name (for edit operation)')
    parser.add_argument('--add-partition', help='New partition name (for add operation)')
    parser.add_argument('--create-table', help='Create new table with this name')
    parser.add_argument('--m-code', required=True, help='Path to file containing M code')
    parser.add_argument('--mode', default='Import', choices=['Import', 'DirectQuery', 'Dual'],
                        help='Partition mode (default: Import)')

    args = parser.parse_args()

    # Validate arguments
    if not any([args.partition, args.add_partition, args.create_table]):
        parser.error("Must specify one of: --partition, --add-partition, or --create-table")

    if args.partition and not args.table:
        parser.error("--partition requires --table")

    if args.add_partition and not args.table:
        parser.error("--add-partition requires --table")

    # Read M code
    m_code_path = Path(args.m_code)
    if not m_code_path.exists():
        print(f"[ERROR] M code file not found: {args.m_code}")
        return 1

    m_code = m_code_path.read_text(encoding='utf-8')

    try:
        # Initialize editor
        editor = TMDLPartitionEditor(args.tmdl_file)

        # Create backup
        editor.create_backup()

        # Execute operation
        success = False

        if args.create_table:
            # Use create_table for new table
            partition_name = args.create_table  # Default partition name = table name
            success = editor.create_table(args.create_table, partition_name, m_code, args.mode)

        elif args.add_partition:
            # Add partition to existing table
            success = editor.add_partition(args.table, args.add_partition, m_code, args.mode)

        elif args.partition:
            # Edit existing partition
            success = editor.edit_partition(args.table, args.partition, m_code, args.mode)

        if success:
            editor.save()
            print("[COMPLETE] M code partition editing successful")
            return 0
        else:
            print("[FAILED] M code partition editing failed")
            return 1

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
