# Future Semantic/Logic Validators for TMDL

## Overview

This document outlines potential semantic and logical validation checks for Power BI TMDL files. These go beyond syntax/format validation to detect logical errors, semantic inconsistencies, and common DAX mistakes that would pass syntax validation but cause runtime errors or incorrect results.

## Current State

**Existing Validators:**
- `tmdl_format_validator.py` - Format/syntax/indentation validation
- `TmdlValidator.exe` - Microsoft TmdlSerializer syntax validation
- Both catch **syntax errors** but NOT **semantic/logical errors**

**Gap:**
Neither validator detects logically incorrect but syntactically valid DAX code.

---

## Proposed Semantic Validation Categories

### 1. Reference Validation (High Priority)

**Impact:** Very High - Catches the most common deployment errors

#### 1.1 Missing Measure/Column References
**Problem:** DAX references a measure or column that doesn't exist
```dax
// ERROR: [Total Sales] doesn't exist
measure 'Sales Growth' = [Total Sales] - [Previous Sales]
```

**Detection:**
- Parse all measure/column references in DAX expressions
- Cross-reference with actual measures/columns in the model
- Report missing references

**Error Code:** TMDL_SEM_001

#### 1.2 Missing Table References
**Problem:** DAX references a table that doesn't exist
```dax
// ERROR: 'Customer' table doesn't exist
measure 'Customer Count' = COUNTROWS(Customer)
```

**Detection:**
- Parse table references in DAX (CALCULATE, FILTER, SUMX, etc.)
- Cross-reference with actual tables in the model
- Report missing tables

**Error Code:** TMDL_SEM_002

#### 1.3 Invalid Relationship References
**Problem:** RELATED/RELATEDTABLE used on non-existent relationships
```dax
// ERROR: No relationship between Sales and Product
column 'Product Name' = RELATED(Product[Name])
```

**Detection:**
- Parse RELATED/RELATEDTABLE functions
- Check if relationship exists between tables
- Validate relationship direction (1-to-many vs many-to-1)

**Error Code:** TMDL_SEM_003

---

### 2. Circular Dependency Detection (High Priority)

**Impact:** High - Causes model loading failures

**Problem:** Measure A depends on Measure B which depends on Measure A
```dax
measure 'A' = [B] + 10
measure 'B' = [A] * 2  // Circular reference!
```

**Detection:**
- Build dependency graph of all measures/columns
- Detect cycles using graph algorithms
- Report circular dependency chains

**Error Code:** TMDL_SEM_004

**Implementation:**
```python
def detect_circular_dependencies(measures):
    graph = build_dependency_graph(measures)
    cycles = find_cycles(graph)
    for cycle in cycles:
        report_error(f"Circular dependency: {' → '.join(cycle)}")
```

---

### 3. Type Validation (Medium Priority)

**Impact:** Medium - Causes runtime errors or unexpected results

#### 3.1 Type Mismatches in Comparisons
**Problem:** Comparing incompatible types
```dax
// ERROR: Comparing string to number
measure 'Invalid Filter' = CALCULATE([Sales], Customer[ID] = "123")
// Customer[ID] is numeric, "123" is string
```

**Detection:**
- Parse filter expressions in CALCULATE, FILTER
- Check data types of columns being compared
- Validate operand type compatibility

**Error Code:** TMDL_SEM_005

#### 3.2 Aggregation Over Aggregation
**Problem:** Aggregating a measure that's already aggregated
```dax
// WARNING: [Total Sales] already contains SUM()
measure 'Double Sum' = SUM([Total Sales])
```

**Detection:**
- Identify measures containing aggregation functions
- Detect when these measures are wrapped in another aggregation
- Report as WARNING (sometimes intentional with iterator functions)

**Error Code:** TMDL_SEM_006

---

### 4. Time Intelligence Validation (Medium Priority)

**Impact:** Medium - Common mistake with time intelligence

#### 4.1 Time Intelligence Without Date Table
**Problem:** Using time intelligence functions without a marked date table
```dax
// ERROR: No date table marked in model
measure 'YoY Growth' = SAMEPERIODLASTYEAR([Sales])
```

**Detection:**
- Check if any table has `type: time` annotation
- Parse DAX for time intelligence functions (SAMEPERIODLASTYEAR, DATEADD, etc.)
- Report error if time intelligence used but no date table marked

**Error Code:** TMDL_SEM_007

#### 4.2 Time Intelligence on Non-Date Column
**Problem:** Time intelligence function referencing non-date column
```dax
// ERROR: Customer[ID] is not a date column
measure 'Bad Time Intel' = SAMEPERIODLASTYEAR(Customer[ID])
```

**Detection:**
- Parse time intelligence function arguments
- Validate that column arguments have date/datetime dataType
- Report type mismatch

**Error Code:** TMDL_SEM_008

---

### 5. Context Validation (Low-Medium Priority)

**Impact:** Medium - Causes incorrect results but not errors

#### 5.1 Missing Row Context in Iterators
**Problem:** Referencing columns outside iterator without row context
```dax
// ERROR: Sales[Amount] requires row context
measure 'Bad Calc' = Sales[Amount] + 10
// Should be: SUMX(Sales, Sales[Amount] + 10)
```

**Detection:**
- Detect direct column references in measure expressions
- Validate they're within iterator context (SUMX, FILTER, etc.)
- Report missing row context

**Error Code:** TMDL_SEM_009

---

### 6. Performance Anti-Patterns (Low Priority - Warnings)

**Impact:** Low severity but high performance impact

#### 6.1 FILTER(ALL(Table)) Pattern
**Problem:** Inefficient pattern that should use CALCULATETABLE
```dax
// WARNING: Use CALCULATETABLE instead
measure 'Inefficient' =
    CALCULATE([Sales], FILTER(ALL(Products), Products[Category] = "Bikes"))
// Better: CALCULATE([Sales], Products[Category] = "Bikes")
```

**Detection:**
- Parse for `FILTER(ALL(table), ...)` pattern
- Suggest using CALCULATETABLE or direct filter arguments
- Report as WARNING

**Error Code:** TMDL_SEM_010

#### 6.2 Nested CALCULATE
**Problem:** Multiple nested CALCULATE functions
```dax
// WARNING: Flatten nested CALCULATE
measure 'Nested' =
    CALCULATE(
        CALCULATE([Sales], Products[Color] = "Red"),
        Customer[Country] = "USA"
    )
// Better: CALCULATE([Sales], Products[Color] = "Red", Customer[Country] = "USA")
```

**Detection:**
- Parse for CALCULATE inside CALCULATE
- Suggest flattening into single CALCULATE
- Report as WARNING

**Error Code:** TMDL_SEM_011

---

### 7. Field Parameter Validation (Very Low Priority)

**Impact:** Very Low - Specific to one pattern

#### 7.1 Field Parameter Ordinal Mismatch
**Problem:** SWITCH ordinals don't match field parameter definition
```dax
// Field parameter defines: 0, 1, 2
// But SWITCH uses: 1, 2, 3
measure 'Dynamic Metric' =
    SWITCH(
        SELECTEDVALUE('Metric Selection'[Index]),
        1, [Measure A],  // Should be 0
        2, [Measure B],  // Should be 1
        3, [Measure C]   // Should be 2
    )
```

**Detection:**
- Identify field parameter tables via `PBI_FieldParameterMetadata` annotation
- Find SWITCH statements referencing field parameter index column
- Extract ordinals from field parameter expression
- Compare with SWITCH case values
- Report mismatch

**Error Code:** TMDL_SEM_012

**Note:** This is very specific and low ROI. Consider implementing only if frequent issue.

---

## Implementation Priority

### Phase 1 - High Value (Implement First)
1. **Missing measure/column references** (TMDL_SEM_001)
2. **Missing table references** (TMDL_SEM_002)
3. **Circular dependencies** (TMDL_SEM_004)

These catch the most common errors that cause deployment failures.

### Phase 2 - Medium Value
4. **Invalid relationship references** (TMDL_SEM_003)
5. **Type mismatches** (TMDL_SEM_005)
6. **Time intelligence without date table** (TMDL_SEM_007)

These catch common logical errors that cause incorrect results.

### Phase 3 - Low Value (Warnings)
7. **Performance anti-patterns** (TMDL_SEM_010, TMDL_SEM_011)
8. **Aggregation over aggregation** (TMDL_SEM_006)

These improve code quality but don't cause failures.

### Phase 4 - Very Low Value (Skip or Low Priority)
9. **Field parameter ordinal mismatch** (TMDL_SEM_012)
10. **Missing row context** (TMDL_SEM_009) - Hard to detect accurately

---

## Technical Approach

### DAX Parsing Strategy

**Option 1: Regex-Based (Lightweight)**
- Use regex patterns to extract measure/column references
- Fast but fragile for complex expressions
- Good for Phase 1 checks (reference validation)

**Option 2: Full DAX Parser (Robust)**
- Use DAX parser library (if available)
- Build full AST (Abstract Syntax Tree)
- Enables all semantic checks
- More complex implementation

**Recommendation:** Start with regex-based for Phase 1, evaluate parser library for Phase 2+

### Model Schema Extraction

```python
class TmdlSemanticValidator:
    def __init__(self, semantic_model_path):
        self.model = self._load_model_schema(semantic_model_path)

    def _load_model_schema(self, path):
        """Extract tables, columns, measures, relationships from TMDL"""
        schema = {
            'tables': {},
            'measures': {},
            'columns': {},
            'relationships': []
        }
        # Parse all .tmdl files in model
        for tmdl_file in glob(f"{path}/definition/**/*.tmdl"):
            self._parse_tmdl_file(tmdl_file, schema)
        return schema

    def validate_references(self):
        """Check all measure/column references are valid"""
        for measure in self.model['measures'].values():
            refs = self._extract_references(measure['expression'])
            for ref in refs:
                if not self._reference_exists(ref):
                    self._report_error('TMDL_SEM_001', ref, measure)
```

### Integration with Existing Workflow

**Add to powerbi-tmdl-syntax-validator agent:**
```python
# In powerbi-tmdl-syntax-validator agent
# After format validation passes, run semantic validation

# 1. Format validation (existing)
format_result = run_format_validator(tmdl_file)

# 2. Syntax validation (existing)
syntax_result = run_csharp_validator(semantic_model_path)

# 3. Semantic validation (NEW)
if format_result and syntax_result:
    semantic_result = run_semantic_validator(semantic_model_path)
    report_semantic_issues(semantic_result)
```

---

## Example Output

```
================================================================================
TMDL SEMANTIC VALIDATION REPORT
================================================================================
Model: PSSR Commissions Pre Prod v2
Total Measures: 127
Total Columns: 89
Total Tables: 18
================================================================================

[SUMMARY]
  Errors:   2
  Warnings: 3

[ERRORS] (Must Fix):
--------------------------------------------------------------------------------

Line 2045 [ERROR] TMDL_SEM_001: Measure reference not found
  Measure: PSSR Labor Commission
  Missing: [Previous Year Sales]
  > VAR _py = [Previous Year Sales]

Line 1234 [ERROR] TMDL_SEM_004: Circular dependency detected
  Chain: [Measure A] → [Measure B] → [Measure C] → [Measure A]
  Break the cycle by refactoring one of these measures.

[WARNINGS] (Should Review):
--------------------------------------------------------------------------------

Line 3456 [WARNING] TMDL_SEM_010: Performance anti-pattern detected
  Measure: Regional Sales
  Pattern: FILTER(ALL(Products), ...)
  Suggestion: Use CALCULATETABLE or direct filter arguments
  > CALCULATE([Sales], FILTER(ALL(Products), Products[Category] = "Bikes"))

================================================================================
```

---

## Future Enhancements

### Advanced Semantic Checks
- **Dead code detection** - Measures never referenced anywhere
- **Unused columns** - Columns not used in any relationship or calculation
- **Inconsistent formatting** - Detect measures with inconsistent format strings
- **Security validation** - RLS expressions that may have logical holes

### DAX Best Practices Linter
- Naming convention validation
- Code complexity metrics
- Documentation completeness (measure descriptions)

---

## Conclusion

**Recommended Implementation:**
1. **Start with Phase 1** - Reference validation catches 80% of semantic errors
2. **Evaluate ROI** - Measure how often each error type occurs in real projects
3. **Incremental rollout** - Add validators as needed based on actual pain points

**Effort Estimate:**
- Phase 1 (Reference validation): 2-3 days
- Phase 2 (Type/relationship validation): 3-5 days
- Phase 3 (Performance warnings): 1-2 days

**Expected Impact:**
- Catch 80-90% of semantic errors before deployment
- Reduce Power BI Desktop testing cycles
- Improve code quality and maintainability
