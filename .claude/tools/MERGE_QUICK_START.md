# Power BI Project Merge - Quick Start Guide

## What is this?

A workflow to compare two Power BI projects and selectively merge changes from one into the other.

## When to use it?

- You have two versions of a Power BI report
- You want to pick and choose which changes to keep
- You need to understand the business impact of differences before merging

## Quick Start

### 1. Run the command

```
/merge-powerbi-projects --main "path/to/main.pbip" --comparison "path/to/other.pbip"
```

**What each parameter means:**
- `--main`: Your baseline project (the one you want to modify)
- `--comparison`: The project containing changes you might want to merge in

### 2. Wait for analysis

The system will:
1. Find all technical differences (measures, tables, visuals, etc.)
2. Explain what each difference means in business terms
3. Present you with a choice list

### 3. Make your decisions

You'll see something like:

```
Diff diff_001: Measure - "Total Revenue"

Technical Details:
- Main Version: SUM(Sales[Amount])
- Comparison Version: SUMX(Sales, Sales[Quantity] * Sales[Price])

Business Impact:
This changes how Total Revenue is calculated. The MAIN version uses a
pre-calculated column, while COMPARISON calculates it dynamically...

Your Choice: [Respond with: "diff_001: Main" or "diff_001: Comparison"]
```

### 4. Respond with your choices

**Option A: Individual decisions**
```
diff_001: Comparison
diff_002: Main
diff_003: Comparison
```

**Option B: Choose one version for everything**
```
all Main
```
or
```
all Comparison
```

### 5. Get your merged project

The system will:
1. Create a new timestamped folder (e.g., `merged_20250128_143022.pbip`)
2. Copy your main project as the base
3. Apply your chosen changes from the comparison project
4. Give you a detailed log of what was changed

## Example Session

```
You: /merge-powerbi-projects --main "C:/reports/sales_v1.pbip" --comparison "C:/reports/sales_v2.pbip"

System: [Analyzing projects... Found 12 differences]

System: [Presenting differences with business impact...]

Diff diff_001: Measure - "YoY Growth"
Status: Modified
Main: DIVIDE([This Year], [Last Year]) - 1
Comparison: Uses SAMEPERIODLASTYEAR for time intelligence...
Business Impact: The comparison version is more accurate for fiscal year reporting...

You: diff_001: Comparison
     diff_002: Main
     ...

System: [Executing merge... Done!]
Your merged project is at: C:/reports/merged_20250128_143022.pbip
12 decisions processed, 7 changes applied, 0 errors
```

## Important Notes

### Non-Destructive
- Your original projects are NEVER modified
- The merge creates a NEW folder
- You can always go back to the originals

### What gets compared?
- **Data Model**: Tables, measures, calculated columns, relationships
- **Report**: Pages, visuals, filters
- **Files**: Any added or deleted files

### What doesn't get compared?
- Data source credentials
- Refresh schedules
- Power BI Service settings

## After the merge

1. **Open in Power BI Desktop**
   - Navigate to the merged folder
   - Open the `.pbip` file
   - Verify visuals load correctly

2. **Test thoroughly**
   - Check all measures calculate correctly
   - Verify visuals display expected data
   - Test filters and slicers

3. **Deploy if satisfied**
   - Use normal deployment process
   - Or run further comparisons if needed

## Tips for choosing

### Choose MAIN when:
- You're unsure about the comparison change
- The main version is the production version
- The comparison change might break dependencies

### Choose COMPARISON when:
- The change is a clear improvement
- It fixes a known bug
- You're intentionally adopting new features

### When in doubt:
- Choose MAIN (safer)
- Run the merge again later with different choices
- You can always re-merge!

## Common Scenarios

### Scenario 1: Merge a bug fix
```
Your main project has a broken measure. Your colleague fixed it.

Action: Choose "Comparison" for just that measure, "Main" for everything else
Result: You get the fix without adopting other changes
```

### Scenario 2: Adopt all new features
```
A new version has multiple improvements.

Action: Review each difference, choose "Comparison" for improvements
Result: Selective adoption of new features
```

### Scenario 3: Keep everything but one change
```
The comparison version is mostly good but has one bad change.

Action: Choose "Comparison" for that one diff, "Main" for all others
Result: You adopt everything except the problematic change
```

## Troubleshooting

### "Invalid project path"
- Check that paths are correct and exist
- Ensure they point to `.pbip` folders, not `.pbix` files
- Use absolute paths for clarity

### "No differences found"
- The projects are identical
- You may have compared a project to itself

### "Merge completed with warnings"
- Check the error log in the results
- Common: missing files, parse errors
- The merge still succeeded for other changes

### "Visual broken after merge"
- May indicate dependencies between changes
- Re-run merge and choose "Comparison" for related diffs
- Or manually fix in Power BI Desktop

## Getting Help

If you encounter issues:
1. Check the detailed merge log
2. Review the business impact analysis
3. Try merging in smaller batches
4. Ask for clarification on specific diffs

## Advanced Usage

### Merging multiple times
You can run the merge workflow multiple times:
```
/merge-powerbi-projects --main "merged_v1.pbip" --comparison "another_version.pbip"
```

This lets you incrementally merge changes from multiple sources.

### Comparing specific versions
Use version control to compare different commits:
```
# Check out version 1
git checkout v1

# Copy project
cp -r project.pbip /tmp/v1.pbip

# Check out version 2
git checkout v2

# Now merge
/merge-powerbi-projects --main "/tmp/v1.pbip" --comparison "project.pbip"
```

## Summary

1. **Run**: `/merge-powerbi-projects --main "path1" --comparison "path2"`
2. **Review**: Read business impact for each difference
3. **Decide**: Choose Main or Comparison for each diff
4. **Test**: Open merged project in Power BI Desktop
5. **Deploy**: Use your normal deployment process

The workflow is designed to be safe, non-destructive, and to give you full control over what changes get merged.
