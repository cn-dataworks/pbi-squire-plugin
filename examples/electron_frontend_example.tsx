/**
 * Electron Frontend Example - React + TypeScript
 *
 * This demonstrates how the desktop app UI would work with the
 * Agent SDK backend to provide a user-friendly interface for
 * Power BI project analysis and modification.
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';

// ============================================================================
// Type Definitions
// ============================================================================

interface WorkflowState {
  workflow_id: string;
  workflow_type: 'evaluate' | 'create' | 'implement' | 'merge';
  project_path: string;
  timestamp: string;
  status: 'running' | 'completed' | 'failed';

  prerequisites?: {
    format: string;
    status: string;
    project_metadata: any;
  };

  section_1a_code_investigation?: {
    items: Array<{
      type: string;
      name: string;
      file_path: string;
      line_number: number;
      code: string;
      parent_object?: string;
    }>;
  };

  section_2a_code_changes?: Array<{
    change_type: 'CREATE' | 'MODIFY';
    target_location: string;
    proposed_code: string;
    change_rationale: string;
  }>;

  verification_verdict?: 'PASS' | 'WARNING' | 'FAIL';
}

interface ProgressMessage {
  message: string;
  timestamp: string;
}

// ============================================================================
// API Client
// ============================================================================

class WorkflowAPI {
  private baseURL = 'http://localhost:8000/api';

  async evaluateProject(params: {
    projectPath: string;
    description: string;
    workspace?: string;
    dataset?: string;
  }): Promise<{ workflow_id: string }> {
    const response = await axios.post(`${this.baseURL}/workflows/evaluate`, params);
    return response.data;
  }

  async getWorkflowState(workflowId: string): Promise<WorkflowState> {
    const response = await axios.get(`${this.baseURL}/workflows/${workflowId}`);
    return response.data;
  }

  async implementChanges(workflowId: string, deployEnv?: string): Promise<any> {
    const response = await axios.post(
      `${this.baseURL}/workflows/${workflowId}/implement`,
      { deploy_environment: deployEnv }
    );
    return response.data;
  }

  // WebSocket for real-time progress
  connectProgressWebSocket(
    workflowId: string,
    onMessage: (msg: ProgressMessage) => void
  ): WebSocket {
    const ws = new WebSocket(`ws://localhost:8000/ws/progress/${workflowId}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    return ws;
  }
}

const api = new WorkflowAPI();

// ============================================================================
// Main Evaluation View Component
// ============================================================================

export const EvaluateProjectView: React.FC = () => {
  // Form state
  const [projectPath, setProjectPath] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [workspace, setWorkspace] = useState<string>('');
  const [dataset, setDataset] = useState<string>('');

  // Workflow state
  const [workflowId, setWorkflowId] = useState<string | null>(null);
  const [workflowState, setWorkflowState] = useState<WorkflowState | null>(null);
  const [progressMessages, setProgressMessages] = useState<ProgressMessage[]>([]);
  const [isRunning, setIsRunning] = useState<boolean>(false);

  // WebSocket connection
  useEffect(() => {
    if (!workflowId) return;

    const ws = api.connectProgressWebSocket(workflowId, (msg) => {
      setProgressMessages(prev => [...prev, msg]);
    });

    return () => ws.close();
  }, [workflowId]);

  // Poll for workflow state updates
  useEffect(() => {
    if (!workflowId || !isRunning) return;

    const interval = setInterval(async () => {
      const state = await api.getWorkflowState(workflowId);
      setWorkflowState(state);

      if (state.status === 'completed' || state.status === 'failed') {
        setIsRunning(false);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [workflowId, isRunning]);

  const handleBrowseProject = async () => {
    // Use Electron's dialog API to select folder
    // @ts-ignore
    const path = await window.electron.selectFolder();
    if (path) setProjectPath(path);
  };

  const handleEvaluate = async () => {
    try {
      setIsRunning(true);
      setProgressMessages([]);

      const result = await api.evaluateProject({
        projectPath,
        description,
        workspace: workspace || undefined,
        dataset: dataset || undefined
      });

      setWorkflowId(result.workflow_id);
    } catch (error) {
      console.error('Evaluation failed:', error);
      setIsRunning(false);
    }
  };

  const handleImplement = async (deployEnv?: string) => {
    if (!workflowId) return;

    try {
      await api.implementChanges(workflowId, deployEnv);
      alert('Implementation started!');
    } catch (error) {
      console.error('Implementation failed:', error);
    }
  };

  return (
    <div className="evaluate-container">
      {/* Header */}
      <header className="header">
        <h1>Evaluate Power BI Project</h1>
        <p className="subtitle">
          Analyze and diagnose Power BI project issues with AI-powered analysis
        </p>
      </header>

      {/* Configuration Form */}
      <div className="config-section">
        <h2>Project Configuration</h2>

        <div className="form-group">
          <label htmlFor="project-path">Project Path *</label>
          <div className="input-with-button">
            <input
              id="project-path"
              type="text"
              value={projectPath}
              onChange={(e) => setProjectPath(e.target.value)}
              placeholder="C:\Projects\SalesReport.pbip"
              disabled={isRunning}
            />
            <button onClick={handleBrowseProject} disabled={isRunning}>
              Browse...
            </button>
          </div>
          <small>Select a Power BI Project folder (.pbip) or PBIX file</small>
        </div>

        <div className="form-group">
          <label htmlFor="description">Problem Description *</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the issue you're experiencing..."
            rows={4}
            disabled={isRunning}
          />
          <small>
            Be specific about what's wrong or what needs to be changed
          </small>
        </div>

        <details className="optional-settings">
          <summary>Optional: Data Sampling Settings</summary>

          <div className="form-group">
            <label htmlFor="workspace">Power BI Workspace</label>
            <input
              id="workspace"
              type="text"
              value={workspace}
              onChange={(e) => setWorkspace(e.target.value)}
              placeholder="Sales Analytics"
              disabled={isRunning}
            />
          </div>

          <div className="form-group">
            <label htmlFor="dataset">Dataset Name</label>
            <input
              id="dataset"
              type="text"
              value={dataset}
              onChange={(e) => setDataset(e.target.value)}
              placeholder="Sales Model"
              disabled={isRunning}
            />
          </div>

          <small>
            Provide workspace and dataset to enable data sampling for better analysis
          </small>
        </details>

        <button
          className="btn-primary"
          onClick={handleEvaluate}
          disabled={!projectPath || !description || isRunning}
        >
          {isRunning ? 'Running Analysis...' : 'Start Evaluation'}
        </button>
      </div>

      {/* Progress Section */}
      {isRunning && (
        <div className="progress-section">
          <h2>Analysis Progress</h2>
          <div className="progress-log">
            {progressMessages.map((msg, idx) => (
              <div key={idx} className="progress-message">
                <span className="timestamp">{msg.timestamp}</span>
                <span className="message">{msg.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Results Section */}
      {workflowState && workflowState.status === 'completed' && (
        <div className="results-section">
          <h2>Analysis Results</h2>

          {/* Prerequisites */}
          {workflowState.prerequisites && (
            <div className="results-card">
              <h3>Project Information</h3>
              <table>
                <tbody>
                  <tr>
                    <td>Format:</td>
                    <td>{workflowState.prerequisites.format}</td>
                  </tr>
                  <tr>
                    <td>Status:</td>
                    <td>
                      <span className={`status ${workflowState.prerequisites.status}`}>
                        {workflowState.prerequisites.status}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}

          {/* Code Investigation */}
          {workflowState.section_1a_code_investigation && (
            <div className="results-card">
              <h3>Code Investigation</h3>
              {workflowState.section_1a_code_investigation.items.map((item, idx) => (
                <div key={idx} className="code-item">
                  <div className="code-header">
                    <span className="code-type">{item.type}</span>
                    <strong>{item.name}</strong>
                    {item.parent_object && (
                      <span className="parent">in {item.parent_object}</span>
                    )}
                  </div>
                  <div className="code-location">
                    📄 {item.file_path}:{item.line_number}
                  </div>
                  <pre className="code-block">
                    <code>{item.code}</code>
                  </pre>
                </div>
              ))}
            </div>
          )}

          {/* Proposed Changes */}
          {workflowState.section_2a_code_changes && (
            <div className="results-card">
              <h3>Proposed Changes</h3>
              {workflowState.section_2a_code_changes.map((change, idx) => (
                <div key={idx} className="change-item">
                  <div className="change-header">
                    <span className={`change-type ${change.change_type}`}>
                      {change.change_type}
                    </span>
                    <strong>{change.target_location}</strong>
                  </div>
                  <div className="change-rationale">
                    {change.change_rationale}
                  </div>
                  <pre className="code-block">
                    <code>{change.proposed_code}</code>
                  </pre>
                </div>
              ))}
            </div>
          )}

          {/* Verification Verdict */}
          {workflowState.verification_verdict && (
            <div className={`results-card verdict-${workflowState.verification_verdict.toLowerCase()}`}>
              <h3>Verification Verdict</h3>
              <div className="verdict">
                <span className={`verdict-badge ${workflowState.verification_verdict}`}>
                  {workflowState.verification_verdict}
                </span>
                {workflowState.verification_verdict === 'PASS' && (
                  <p>✅ All proposed changes have been verified and are safe to implement.</p>
                )}
                {workflowState.verification_verdict === 'WARNING' && (
                  <p>⚠️ Changes verified with warnings. Review carefully before implementing.</p>
                )}
                {workflowState.verification_verdict === 'FAIL' && (
                  <p>❌ Critical issues found. Changes need revision before implementation.</p>
                )}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="action-buttons">
            <button
              className="btn-secondary"
              onClick={() => {
                // Export findings to markdown
                alert('Export functionality coming soon!');
              }}
            >
              Export Findings
            </button>

            {workflowState.verification_verdict !== 'FAIL' && (
              <>
                <button
                  className="btn-primary"
                  onClick={() => handleImplement()}
                >
                  Implement Changes
                </button>

                <button
                  className="btn-success"
                  onClick={() => {
                    const env = prompt('Enter deployment environment (DEV, TEST, PROD):');
                    if (env) handleImplement(env);
                  }}
                >
                  Implement & Deploy
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// ============================================================================
// Findings Viewer Component (for browsing past analyses)
// ============================================================================

export const FindingsViewer: React.FC<{ workflowId: string }> = ({ workflowId }) => {
  const [state, setState] = useState<WorkflowState | null>(null);
  const [markdownView, setMarkdownView] = useState<boolean>(false);

  useEffect(() => {
    const loadState = async () => {
      const data = await api.getWorkflowState(workflowId);
      setState(data);
    };
    loadState();
  }, [workflowId]);

  if (!state) return <div>Loading...</div>;

  return (
    <div className="findings-viewer">
      <div className="viewer-toolbar">
        <button onClick={() => setMarkdownView(!markdownView)}>
          {markdownView ? 'Structured View' : 'Markdown View'}
        </button>
      </div>

      {markdownView ? (
        <div className="markdown-view">
          {/* Render findings as markdown */}
          <pre>{JSON.stringify(state, null, 2)}</pre>
        </div>
      ) : (
        <div className="structured-view">
          {/* Render findings as structured components */}
          {/* Similar to results section above */}
        </div>
      )}
    </div>
  );
};

// ============================================================================
// Styling (CSS-in-JS or separate stylesheet)
// ============================================================================

const styles = `
.evaluate-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  font-size: 1rem;
}

.config-section {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group small {
  display: block;
  margin-top: 0.25rem;
  color: #666;
  font-size: 0.875rem;
}

.input-with-button {
  display: flex;
  gap: 0.5rem;
}

.input-with-button input {
  flex: 1;
}

.btn-primary,
.btn-secondary,
.btn-success {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary {
  background: #0078d4;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #106ebe;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.results-card {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.results-card h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.25rem;
}

.code-block {
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 1rem;
  overflow-x: auto;
}

.verdict-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 1.25rem;
}

.verdict-badge.PASS {
  background: #d4edda;
  color: #155724;
}

.verdict-badge.WARNING {
  background: #fff3cd;
  color: #856404;
}

.verdict-badge.FAIL {
  background: #f8d7da;
  color: #721c24;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}
`;

// ============================================================================
// Electron Main Process Integration
// ============================================================================

/**
 * In your Electron main process (main.ts):
 *
 * import { app, BrowserWindow, ipcMain, dialog } from 'electron';
 * import { spawn } from 'child_process';
 * import path from 'path';
 *
 * let pythonProcess: any = null;
 *
 * // Start Python backend when app starts
 * app.on('ready', () => {
 *   // Start Python FastAPI backend
 *   const pythonPath = path.join(app.getAppPath(), 'backend', 'main.py');
 *   pythonProcess = spawn('python', [pythonPath]);
 *
 *   pythonProcess.stdout.on('data', (data) => {
 *     console.log(`Backend: ${data}`);
 *   });
 *
 *   // Wait for backend to start
 *   setTimeout(() => {
 *     createWindow();
 *   }, 2000);
 * });
 *
 * // Handle folder selection
 * ipcMain.handle('select-folder', async () => {
 *   const result = await dialog.showOpenDialog({
 *     properties: ['openDirectory']
 *   });
 *
 *   if (!result.canceled && result.filePaths.length > 0) {
 *     return result.filePaths[0];
 *   }
 *
 *   return null;
 * });
 *
 * // Clean up Python process on exit
 * app.on('will-quit', () => {
 *   if (pythonProcess) {
 *     pythonProcess.kill();
 *   }
 * });
 */
