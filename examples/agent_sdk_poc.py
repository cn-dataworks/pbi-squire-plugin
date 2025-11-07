"""
Proof of Concept: Converting Power BI Agents to Claude Agent SDK Tools

This demonstrates how to convert your existing Power BI analyst agents
into Claude Agent SDK custom tools and orchestrate them in a workflow.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import json
import asyncio

# Note: These imports would be from claude-agent-sdk once installed
# pip install claude-agent-sdk
from claude_agent_sdk import ClaudeSDKClient, Tool


# ============================================================================
# Data Models (replacing findings.md with structured state)
# ============================================================================

@dataclass
class WorkflowState:
    """
    Structured state object that replaces findings.md
    Can be serialized to JSON for persistence or converted to Markdown
    """
    workflow_id: str
    workflow_type: str  # evaluate, create, implement, merge
    project_path: str
    timestamp: str
    status: str  # running, completed, failed

    # Prerequisites
    prerequisites: Dict[str, Any] = None

    # Section 1: Investigation
    data_model_schema: Optional[Dict] = None
    section_1a_code_investigation: Optional[Dict] = None
    section_1b_visual_investigation: Optional[Dict] = None
    data_context: Optional[Dict] = None

    # Section 2: Proposed Changes
    section_2a_code_changes: Optional[List[Dict]] = None
    section_2b_visual_changes: Optional[List[Dict]] = None

    # Section 3: Verification
    verification_verdict: Optional[str] = None
    verification_notes: Optional[List[str]] = None

    # Section 4: Implementation Results
    implementation_results: Optional[Dict] = None
    versioned_project_path: Optional[str] = None

    def to_json(self) -> str:
        """Serialize to JSON for API responses"""
        return json.dumps(self.__dict__, indent=2)

    def to_findings_markdown(self) -> str:
        """
        Generate findings.md in your current format
        This maintains backward compatibility
        """
        md = f"# Power BI Analyst Findings\n\n"
        md += f"**Workflow ID:** {self.workflow_id}\n"
        md += f"**Type:** {self.workflow_type}\n"
        md += f"**Project:** {self.project_path}\n"
        md += f"**Timestamp:** {self.timestamp}\n"
        md += f"**Status:** {self.status}\n\n"

        # Add sections as they're populated
        if self.prerequisites:
            md += "## Prerequisites\n\n"
            md += f"- Project Format: {self.prerequisites.get('format')}\n"
            md += f"- Validation Status: {self.prerequisites.get('status')}\n\n"

        if self.section_1a_code_investigation:
            md += "## Section 1.A: Calculation Code Investigation\n\n"
            for item in self.section_1a_code_investigation.get('items', []):
                md += f"### {item['name']}\n"
                md += f"**File:** `{item['file_path']}`\n\n"
                md += f"```dax\n{item['code']}\n```\n\n"

        # Continue for other sections...

        return md


# ============================================================================
# Custom Tools (converted from your agents)
# ============================================================================

class PowerBIVerifyProjectTool(Tool):
    """
    Converted from: .claude/agents/powerbi-verify-pbiproject-folder-setup.md

    Validates Power BI project structure and detects format (PBIP, PBIX, pbi-tools)
    """
    name = "powerbi_verify_project"
    description = """
    Validates Power BI project folder structure and detects format.
    Returns validation status and project metadata.

    Use this tool FIRST in any workflow to ensure project is valid.
    """

    async def execute(
        self,
        project_path: str,
        user_action: str = "none"  # none, extract_with_pbitools
    ) -> Dict[str, Any]:
        """
        Execute project validation

        Args:
            project_path: Path to project folder or PBIX file
            user_action: Action to perform if needed

        Returns:
            {
                "status": "validated" | "requires_extraction" | "invalid",
                "format": "pbip" | "pbix" | "pbi-tools",
                "project_metadata": {...},
                "validation_errors": [...]
            }
        """
        project = Path(project_path)

        # Detect format
        if project.is_file() and project.suffix == ".pbix":
            if user_action == "extract_with_pbitools":
                # Call pbi-tools extraction
                extracted_path = await self._extract_pbix(project_path)
                return {
                    "status": "validated",
                    "format": "pbip",
                    "project_path": extracted_path,
                    "project_metadata": await self._get_metadata(extracted_path)
                }
            else:
                return {
                    "status": "requires_extraction",
                    "format": "pbix",
                    "message": "PBIX file needs extraction with pbi-tools"
                }

        elif project.is_dir():
            # Check for .pbip format
            pbip_file = list(project.glob("*.pbip"))
            if pbip_file:
                # Validate TMDL structure
                is_valid = await self._validate_tmdl_structure(project)
                if is_valid:
                    return {
                        "status": "validated",
                        "format": "pbip",
                        "project_path": str(project),
                        "project_metadata": await self._get_metadata(project)
                    }
                else:
                    return {
                        "status": "invalid",
                        "format": "pbip",
                        "validation_errors": ["Invalid TMDL structure"]
                    }

            # Check for pbi-tools format
            elif (project / "Model").exists() or (project / "Report").exists():
                return {
                    "status": "validated",
                    "format": "pbi-tools",
                    "project_path": str(project),
                    "requires_compilation": True,
                    "project_metadata": await self._get_metadata(project)
                }

        return {
            "status": "invalid",
            "message": "Unrecognized project format"
        }

    async def _extract_pbix(self, pbix_path: str) -> str:
        """Extract PBIX using pbi-tools"""
        # Implementation would call pbi-tools CLI
        pass

    async def _validate_tmdl_structure(self, project_path: Path) -> bool:
        """Validate TMDL folder structure"""
        # Implementation would check for required folders/files
        pass

    async def _get_metadata(self, project_path: Path) -> Dict:
        """Extract project metadata"""
        # Implementation would read model.tmdl, report.json, etc.
        pass


class PowerBICodeLocatorTool(Tool):
    """
    Converted from: .claude/agents/powerbi-code-locator.md

    Identifies specific code locations in Power BI projects
    """
    name = "powerbi_locate_code"
    description = """
    Locates specific measures, tables, columns, or M code in Power BI project.
    Returns file paths and code snippets.

    Use this when user mentions specific calculations or objects to modify.
    """

    async def execute(
        self,
        project_path: str,
        search_target: str,  # measure name, table name, etc.
        search_type: str = "auto"  # measure, table, column, query, auto
    ) -> Dict[str, Any]:
        """
        Locate code in project

        Returns:
            {
                "found": bool,
                "items": [
                    {
                        "type": "measure" | "table" | "column" | "query",
                        "name": str,
                        "file_path": str,
                        "line_number": int,
                        "code": str,
                        "parent_object": str (for columns/measures)
                    }
                ]
            }
        """
        # Implementation would:
        # 1. Search TMDL files for the target
        # 2. Parse file structure
        # 3. Extract code snippets
        # 4. Return structured results

        # Example return:
        return {
            "found": True,
            "items": [
                {
                    "type": "measure",
                    "name": "Total Revenue",
                    "file_path": "Project.SemanticModel/definition/tables/Sales.tmdl",
                    "line_number": 42,
                    "code": "SUM(Sales[Amount])",
                    "parent_object": "Sales",
                    "format_string": "\"$#,0.00\"",
                    "display_folder": "Revenue Metrics"
                }
            ]
        }


class PowerBIDashboardUpdatePlannerTool(Tool):
    """
    Converted from: .claude/agents/powerbi-dashboard-update-planner.md

    Unified planner for calculation and/or visual changes
    """
    name = "powerbi_plan_changes"
    description = """
    Plans changes for Power BI projects (calculation, visual, or hybrid).
    Analyzes current code/state and designs coordinated modifications.

    Use this after locating existing code to plan the fix/update.
    """

    async def execute(
        self,
        problem_statement: str,
        current_code: Optional[Dict] = None,  # from code locator
        current_visuals: Optional[Dict] = None,  # from visual locator
        data_context: Optional[Dict] = None  # from data context agent
    ) -> Dict[str, Any]:
        """
        Plan changes based on investigation results

        Returns:
            {
                "change_type": "calculation" | "visual" | "hybrid",
                "coordination_summary": str (for hybrid),
                "section_2a_code_changes": [...],  # if applicable
                "section_2b_visual_changes": [...],  # if applicable
                "dependencies": [...]
            }
        """
        # Implementation would:
        # 1. Analyze problem and current state
        # 2. Determine change type
        # 3. Design coordinated changes
        # 4. Generate DAX/M code or XML edit plans
        # 5. Document dependencies

        # This is where you'd integrate Claude's reasoning
        # to diagnose issues and generate fixes

        pass


class PowerBICodeImplementerTool(Tool):
    """
    Converted from: .claude/agents/powerbi-code-implementer-apply.md

    Applies code changes to Power BI project
    """
    name = "powerbi_implement_code"
    description = """
    Applies code changes from Section 2.A to Power BI project.
    Creates versioned copy and modifies TMDL files.

    Use this to apply planned changes to the project.
    """

    async def execute(
        self,
        project_path: str,
        changes: List[Dict],  # from Section 2.A
        create_version: bool = True
    ) -> Dict[str, Any]:
        """
        Apply code changes

        Returns:
            {
                "status": "success" | "failed",
                "versioned_project_path": str,
                "applied_changes": [...],
                "errors": [...]
            }
        """
        # Implementation would:
        # 1. Create timestamped copy if requested
        # 2. Parse change operations (CREATE, MODIFY)
        # 3. Apply changes using tmdl_measure_replacer.py
        # 4. Validate syntax
        # 5. Return results

        pass


# ============================================================================
# Workflow Orchestrator
# ============================================================================

class PowerBIWorkflowEngine:
    """
    Main workflow orchestrator using Agent SDK
    Equivalent to your slash commands
    """

    def __init__(self, api_key: str):
        """
        Initialize workflow engine with Agent SDK client

        Args:
            api_key: Claude API key
        """
        self.tools = [
            PowerBIVerifyProjectTool(),
            PowerBICodeLocatorTool(),
            PowerBIDashboardUpdatePlannerTool(),
            PowerBICodeImplementerTool(),
            # ... register all 23 tools
        ]

        self.client = ClaudeSDKClient(
            api_key=api_key,
            tools=self.tools
        )

    async def evaluate_project(
        self,
        project_path: str,
        description: str,
        workspace: Optional[str] = None,
        dataset: Optional[str] = None,
        callback=None  # For UI progress updates
    ) -> WorkflowState:
        """
        Equivalent to /evaluate-pbi-project-file command

        Orchestrates the evaluation workflow:
        1. Validate project
        2. Classify problem type
        3. Investigate (code and/or visual)
        4. Plan changes
        5. Verify changes

        Args:
            project_path: Path to Power BI project
            description: Problem description
            workspace: Power BI workspace (optional, for data sampling)
            dataset: Dataset name (optional)
            callback: Function to call with progress updates

        Returns:
            WorkflowState object with complete findings
        """
        # Create initial state
        state = WorkflowState(
            workflow_id=self._generate_id(),
            workflow_type="evaluate",
            project_path=project_path,
            timestamp=self._get_timestamp(),
            status="running"
        )

        # Create Agent SDK session
        session = await self.client.create_session()

        try:
            # Phase 1: Validation
            if callback:
                callback("Validating project structure...")

            validation_result = await session.query(
                f"""Validate the Power BI project at '{project_path}'.

                Use the powerbi_verify_project tool to check project structure
                and format. Return the validation results."""
            )

            state.prerequisites = validation_result

            if validation_result.get("status") != "validated":
                state.status = "failed"
                return state

            # Phase 2: Problem Classification
            if callback:
                callback("Classifying problem type...")

            classification = await session.query(
                f"""Analyze this problem description and classify it:

                Problem: {description}

                Determine if this requires:
                - calculation changes (DAX/M/TMDL modifications)
                - visual changes (PBIR layout/formatting)
                - both (hybrid)

                Return: {{"change_type": "calculation|visual|hybrid"}}
                """
            )

            change_type = classification.get("change_type")

            # Phase 3: Investigation (conditional parallel)
            investigation_tasks = []

            if change_type in ["calculation", "hybrid"]:
                if callback:
                    callback("Investigating calculation code...")

                investigation_tasks.append(
                    session.query(
                        f"""Locate the calculation code related to this problem:

                        Problem: {description}
                        Project: {project_path}

                        Use powerbi_locate_code tool to find relevant measures,
                        tables, columns, or M queries. Return the code locations
                        and current implementations."""
                    )
                )

            if change_type in ["visual", "hybrid"]:
                if callback:
                    callback("Investigating visual state...")

                investigation_tasks.append(
                    session.query(
                        f"""Locate the visual components related to this problem:

                        Problem: {description}
                        Project: {project_path}

                        Find relevant PBIR visual.json files and extract current
                        layout, configuration, and data bindings."""
                    )
                )

            # Execute investigation in parallel
            investigation_results = await asyncio.gather(*investigation_tasks)

            if change_type in ["calculation", "hybrid"]:
                state.section_1a_code_investigation = investigation_results[0]
            if change_type in ["visual", "hybrid"]:
                idx = 1 if change_type == "hybrid" else 0
                state.section_1b_visual_investigation = investigation_results[idx]

            # Phase 4: Planning
            if callback:
                callback("Planning changes...")

            planning_result = await session.query(
                f"""Design changes to fix this problem:

                Problem: {description}
                Current Code: {state.section_1a_code_investigation}
                Current Visuals: {state.section_1b_visual_investigation}

                Use powerbi_plan_changes tool to:
                1. Diagnose root cause
                2. Design corrected implementation
                3. Generate Section 2 (code changes and/or visual changes)
                4. Document dependencies

                For hybrid changes, ensure calculation names match visual references.
                """
            )

            state.section_2a_code_changes = planning_result.get("section_2a_code_changes")
            state.section_2b_visual_changes = planning_result.get("section_2b_visual_changes")

            # Phase 5: Verification
            if callback:
                callback("Verifying proposed changes...")

            verification = await session.query(
                f"""Review and verify these proposed changes:

                Code Changes: {state.section_2a_code_changes}
                Visual Changes: {state.section_2b_visual_changes}

                Check for:
                - Semantic correctness
                - Performance implications
                - Breaking changes
                - Dependency issues

                Return verification verdict: PASS, WARNING, or FAIL
                """
            )

            state.verification_verdict = verification.get("verdict")
            state.status = "completed"

            if callback:
                callback("Evaluation complete!")

        except Exception as e:
            state.status = "failed"
            if callback:
                callback(f"Error: {str(e)}")

        return state

    async def implement_changes(
        self,
        state: WorkflowState,
        callback=None
    ) -> WorkflowState:
        """
        Equivalent to /implement-changes command

        Applies changes from WorkflowState to actual project
        Creates versioned copy with modifications
        """
        session = await self.client.create_session()

        try:
            # Phase 1: Code Implementation
            if state.section_2a_code_changes:
                if callback:
                    callback("Applying code changes...")

                impl_result = await session.query(
                    f"""Apply these code changes to the project:

                    Project: {state.project_path}
                    Changes: {state.section_2a_code_changes}

                    Use powerbi_implement_code tool to:
                    1. Create versioned copy
                    2. Apply all changes
                    3. Validate TMDL syntax
                    4. Validate DAX logic
                    5. Return results with versioned project path
                    """
                )

                state.implementation_results = impl_result
                state.versioned_project_path = impl_result.get("versioned_project_path")

            # Phase 2: Visual Implementation
            if state.section_2b_visual_changes:
                if callback:
                    callback("Applying visual changes...")

                visual_result = await session.query(
                    f"""Apply these visual changes to the project:

                    Project: {state.versioned_project_path or state.project_path}
                    Changes: {state.section_2b_visual_changes}

                    Use powerbi_implement_visual tool to:
                    1. Apply PBIR visual modifications
                    2. Validate visual.json structure
                    3. Return results
                    """
                )

                # Merge results
                if state.implementation_results:
                    state.implementation_results.update(visual_result)
                else:
                    state.implementation_results = visual_result

            state.status = "implemented"

            if callback:
                callback(f"Implementation complete! Project saved to: {state.versioned_project_path}")

        except Exception as e:
            state.status = "implementation_failed"
            if callback:
                callback(f"Error: {str(e)}")

        return state

    def _generate_id(self) -> str:
        """Generate unique workflow ID"""
        import uuid
        return str(uuid.uuid4())

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# ============================================================================
# Usage Example
# ============================================================================

async def main():
    """
    Example usage of the workflow engine
    This would be called from your desktop app's backend API
    """
    # Initialize workflow engine
    engine = PowerBIWorkflowEngine(api_key="your-api-key")

    # Define progress callback for UI updates
    def progress_callback(message: str):
        print(f"[Progress] {message}")

    # Run evaluate workflow
    print("Starting evaluation workflow...")
    state = await engine.evaluate_project(
        project_path="C:/Projects/SalesReport.pbip",
        description="Total Sales measure showing different total than sum of rows",
        workspace="Sales Analytics",
        dataset="Sales Model",
        callback=progress_callback
    )

    # Convert to markdown for display
    findings_md = state.to_findings_markdown()
    print(f"\nFindings:\n{findings_md}")

    # User reviews findings and approves...

    # Run implementation workflow
    print("\nStarting implementation workflow...")
    implemented_state = await engine.implement_changes(
        state=state,
        callback=progress_callback
    )

    print(f"\nImplementation status: {implemented_state.status}")
    print(f"Versioned project: {implemented_state.versioned_project_path}")
    print(f"\nYou can now open the modified project in Power BI Desktop!")


if __name__ == "__main__":
    asyncio.run(main())


# ============================================================================
# Desktop App Integration Example
# ============================================================================

"""
FastAPI Backend for Desktop App:

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for Electron frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Global workflow engine instance
workflow_engine = PowerBIWorkflowEngine(api_key=os.getenv("CLAUDE_API_KEY"))


@app.post("/api/workflows/evaluate")
async def evaluate_project(request: EvaluateRequest):
    '''
    API endpoint for evaluate workflow
    Called from Electron frontend
    '''
    state = await workflow_engine.evaluate_project(
        project_path=request.project_path,
        description=request.description,
        workspace=request.workspace,
        dataset=request.dataset
    )

    return {
        "workflow_id": state.workflow_id,
        "status": state.status,
        "findings": state.to_json()
    }


@app.websocket("/ws/progress/{workflow_id}")
async def websocket_progress(websocket: WebSocket, workflow_id: str):
    '''
    WebSocket for real-time progress updates
    Frontend connects to receive streaming updates
    '''
    await websocket.accept()

    def callback(message: str):
        asyncio.create_task(
            websocket.send_json({"message": message})
        )

    # Run workflow with callback
    # ...


@app.post("/api/workflows/{workflow_id}/implement")
async def implement_changes(workflow_id: str):
    '''
    API endpoint for implementation workflow
    Creates versioned copy with changes applied
    '''
    # Load state from database
    state = load_workflow_state(workflow_id)

    # Run implementation
    implemented_state = await workflow_engine.implement_changes(
        state=state
    )

    return {
        "status": implemented_state.status,
        "versioned_project_path": implemented_state.versioned_project_path,
        "results": implemented_state.implementation_results
    }


@app.get("/api/projects/{project_path}/versions")
async def list_project_versions(project_path: str):
    '''
    List all versioned copies of a project
    '''
    # Implementation to find all timestamped versions
    pass
"""
