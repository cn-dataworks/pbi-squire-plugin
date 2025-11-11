# Power BI Analyst Agent - Desktop App Examples

This directory contains proof-of-concept examples demonstrating how to convert the Power BI Analyst Agent workflows into a desktop application using the Claude Agent SDK.

**Scope**: These examples focus on **desktop editing only** - analyzing and modifying Power BI projects locally. The examples do NOT include:
- Deployment to Power BI Service
- Automated testing with Playwright
- pbi-tools compilation/packaging

The workflow is: **Analyze → Implement → Open in Power BI Desktop**

## Files

### 1. `agent_sdk_poc.py`

**Python backend demonstrating:**
- Converting your existing agents to Agent SDK custom tools
- Workflow orchestration using the Agent SDK client
- State management (replacing findings.md with structured data)
- FastAPI integration for desktop app backend
- **Scope**: Desktop editing only (no deployment/testing)

**Key Classes:**
- `WorkflowState`: Structured state object (replaces findings.md)
- `PowerBIVerifyProjectTool`: Example agent converted to SDK tool
- `PowerBICodeLocatorTool`: Example code location agent as SDK tool
- `PowerBIDashboardUpdatePlannerTool`: Example planning agent as SDK tool
- `PowerBICodeImplementerTool`: Example implementation agent as SDK tool
- `PowerBIWorkflowEngine`: Main orchestrator (equivalent to slash commands)

**Usage:**
```bash
# Install dependencies
pip install claude-agent-sdk fastapi uvicorn

# Run the example
python agent_sdk_poc.py
```

### 2. `electron_frontend_example.tsx`

**React + TypeScript frontend demonstrating:**
- User interface for Power BI project evaluation
- Real-time progress updates via WebSocket
- Findings viewer with structured/markdown views
- Integration with Python backend via REST API
- Electron integration (file dialogs, folder browsing)
- **Focus**: Desktop workflow (analyze → implement → open in Power BI Desktop)

**Key Components:**
- `EvaluateProjectView`: Main evaluation workflow UI
- `FindingsViewer`: Display analysis results
- `WorkflowAPI`: API client for backend communication

**Usage:**
```bash
# Install dependencies
npm install react axios

# This would be part of an Electron app
# See the Electron main process integration comments in the file
```

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│         Electron Desktop App                 │
│  ┌───────────────────────────────────────┐  │
│  │  React Frontend                       │  │
│  │  (electron_frontend_example.tsx)      │  │
│  └─────────────┬─────────────────────────┘  │
│                │ REST API / WebSocket        │
│  ┌─────────────▼─────────────────────────┐  │
│  │  Python Backend (FastAPI)             │  │
│  │  (agent_sdk_poc.py)                   │  │
│  │                                        │  │
│  │  ┌──────────────────────────────────┐ │  │
│  │  │  Claude Agent SDK                │ │  │
│  │  │  - 23 Custom Tools               │ │  │
│  │  │  - Workflow Orchestration        │ │  │
│  │  │  - Session Management            │ │  │
│  │  └──────────────────────────────────┘ │  │
│  │                                        │  │
│  │  ┌──────────────────────────────────┐ │  │
│  │  │  Your Existing Tools             │ │  │
│  │  │  - Python Utilities              │ │  │
│  │  │  - TMDL Validator                │ │  │
│  │  │  - PBIR Editor                   │ │  │
│  │  │  - XMLA Agent (data sampling)    │ │  │
│  │  └──────────────────────────────────┘ │  │
│  └────────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

## Key Concepts

### 1. Agent → Tool Conversion

Each of your 23 agents becomes a **custom tool** in the Agent SDK:

```python
class PowerBIVerifyProjectTool(Tool):
    name = "powerbi_verify_project"
    description = "Validates Power BI project structure"

    async def execute(self, project_path: str) -> dict:
        # Your existing agent logic
        pass
```

### 2. Slash Command → Workflow Function

Your slash commands become **workflow orchestrator functions**:

```python
async def evaluate_project(
    self,
    project_path: str,
    description: str
) -> WorkflowState:
    # Orchestrate tools using Agent SDK
    pass
```

### 3. findings.md → Structured State

The findings file becomes a **data structure**:

```python
@dataclass
class WorkflowState:
    workflow_id: str
    section_1a_code_investigation: Optional[Dict]
    section_2a_code_changes: Optional[List[Dict]]
    # ...

    def to_findings_markdown(self) -> str:
        # Convert to markdown for compatibility
        pass
```

### 4. User Interaction → GUI

User prompts become **UI components**:

```tsx
<EvaluateProjectView
  onEvaluate={(config) => startWorkflow(config)}
  onProgressUpdate={(msg) => showProgress(msg)}
/>
```

## Next Steps

### 1. Set Up Development Environment

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Run the Examples

```bash
# Start backend (terminal 1)
python examples/agent_sdk_poc.py

# Start frontend (terminal 2)
cd frontend
npm start
```

### 3. Customize for Your Needs

- Add your remaining agents as tools
- Implement complete workflows
- Design your UI components
- Add authentication and settings

## Migration Path

### Phase 1: Proof of Concept (Current Stage)
- ✅ Example agent-to-tool conversion
- ✅ Example workflow orchestration
- ✅ Example frontend UI
- 🔄 Test with real Power BI project

### Phase 2: Convert Core Agents
- Convert all 23 agents to SDK tools
- Implement evaluate workflow fully
- Create comprehensive UI

### Phase 3: Full Desktop App
- Package with Electron Builder
- Add settings and preferences
- Implement credential management
- Create installers

## Resources

- **Main Analysis Document**: `../DESKTOP_APP_ANALYSIS.md`
- **Claude Agent SDK Docs**: https://docs.claude.com/en/api/agent-sdk/overview
- **Electron Documentation**: https://www.electronjs.org/docs/latest
- **FastAPI Documentation**: https://fastapi.tiangolo.com/

## Questions?

Refer to the comprehensive analysis in `DESKTOP_APP_ANALYSIS.md` for:
- Detailed architecture recommendations
- Technology stack choices
- Implementation roadmap
- Challenges and solutions
- Estimated timeline and resources
