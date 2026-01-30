# PBI Squire - Glossary

A plain-language guide to technical terms you may encounter when using this skill.

---

## Data Model Terms

### Measure
A calculation that summarizes data dynamically based on the current filter context. Measures change their results depending on what's being viewed in a report.

**Example:** "Total Sales" might show $1M for all products, but $100K when filtered to just "Electronics".

### Calculated Column
A column added to a table that computes a value for each row when data is loaded. Unlike measures, calculated columns don't change based on filters - each row has a fixed value.

**Example:** A "Full Name" column that combines first and last name for each customer.

### DAX (Data Analysis Expressions)
The formula language used in Power BI for measures and calculated columns. Similar to Excel formulas but designed for data models.

**Example:** `SUM(Sales[Amount])` adds up all values in the Amount column.

### M Code / Power Query
The language used to transform data before it loads into Power BI. Controls how data is cleaned, filtered, and combined from sources.

**Example:** Removing blank rows, combining columns, or filtering dates.

### Relationship
A connection between two tables based on matching columns. Enables filtering one table to automatically filter related tables.

**Example:** Filtering by "2024" in a Date table automatically shows only 2024 sales.

### Filter Context
The set of active filters at any point in a report. Determines what data a measure calculates against.

**Example:** When viewing a chart for "Region = West", the filter context includes that region filter.

---

## File Format Terms

### PBIP (Power BI Project)
A folder-based format where Power BI content is stored as readable text files instead of a single binary file. Enables version control and easier editing.

### PBIX
The traditional Power BI file format - a single compressed file containing everything. Cannot be version controlled or edited with text tools.

### TMDL (Tabular Model Definition Language)
Text files that define the data model structure - tables, columns, measures, relationships. Human-readable alternative to JSON.

**Location:** `YourProject.SemanticModel/definition/`

### PBIR (Power BI Enhanced Report Format)
Text files that define report pages and visuals. Each page and visual is stored as a separate JSON file.

**Location:** `YourProject.Report/`

### Semantic Model
The data layer of Power BI - tables, relationships, measures, and calculations. Separate from the visual report layer.

---

## Connection Terms

### MCP (Model Context Protocol)
A live connection to Power BI Desktop that enables real-time validation and querying. Faster and more accurate than file-only mode.

### Desktop Mode
Operating with MCP connected to a running Power BI Desktop instance. Enables live validation and data sampling.

### File-Only Mode
Operating by reading and editing TMDL/PBIR files directly without Power BI Desktop running. Slower but works offline.

### XMLA Endpoint
A connection point for Power BI datasets in the cloud (Power BI Service). Used for querying live data.

---

## Workflow Terms

### Findings File
A markdown document (`findings.md`) that tracks the analysis and changes for a specific task. Each task has its own findings file.

### Task Blackboard
A shared workspace where agents record their findings and progress. The findings file serves as the blackboard for inter-agent communication.

### Versioned Copy
A timestamped backup of your project created before making changes. Ensures you can always revert if something goes wrong.

**Example:** `MyProject_20241222-143000/` contains an exact copy from that timestamp.

### Validation Gate
A checkpoint that verifies changes are correct before proceeding. Catches errors early before they cause problems.

---

## Agent Terms

### DAX Specialist
An expert agent focused on writing and reviewing DAX formulas. Handles measures, calculated columns, and calculation groups.

### M-Code Specialist
An expert agent focused on Power Query transformations. Handles data source connections, transformations, and table definitions.

### Orchestrator
The main skill that coordinates work between specialist agents. Decides which agent to invoke and when.

---

## Common Operations

### Evaluate
Analyze existing code to understand what's wrong and propose a fix.

### Create Artifact
Build a new measure, calculated column, table, or visual from scratch.

### Implement
Apply proposed changes to the actual project files.

### Deploy
Publish changes to Power BI Service (cloud).

### Merge
Combine changes from two different project versions.

---

## Error Terms

### Circular Dependency
When measure A references measure B, and measure B references measure A. Creates an infinite loop that Power BI cannot resolve.

### Filter Context Error
When a measure doesn't behave as expected because the filter context is different than assumed.

### Query Folding
When Power Query can translate transformations into the source system's language (like SQL). Improves performance by doing work at the source.

### Syntax Error
A typo or structural mistake in DAX or M code that prevents it from being understood.

---

*For additional help, ask: "Explain [term] in simple terms"*
