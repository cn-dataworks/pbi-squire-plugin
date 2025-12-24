#Requires -Version 5.1
<#
.SYNOPSIS
    Power BI Analyst Skill - State Manager (PowerShell)

.DESCRIPTION
    Manages session state, tasks, and resource locks for the Power BI Analyst skill.
    Primary state management backend for Windows environments.

.EXAMPLE
    .\state_manage.ps1 -Summary
    .\state_manage.ps1 -CreateTask "fix-yoy-calc" -Workflow "evaluate"
    .\state_manage.ps1 -Complete "fix-yoy-calc-1734872400"
    .\state_manage.ps1 -Lock "definition/tables/Sales.tmdl" -TaskId "fix-yoy-calc-1734872400"
#>

[CmdletBinding()]
param(
    [Parameter(ParameterSetName='Summary')]
    [switch]$Summary,

    [Parameter(ParameterSetName='Reset')]
    [switch]$Reset,

    [Parameter(ParameterSetName='CreateTask', Mandatory=$true)]
    [string]$CreateTask,

    [Parameter(ParameterSetName='CreateTask')]
    [ValidateSet('evaluate', 'create', 'implement', 'analyze', 'merge')]
    [string]$Workflow = 'evaluate',

    [Parameter(ParameterSetName='UpdateStage', Mandatory=$true)]
    [string]$UpdateStage,

    [Parameter(ParameterSetName='UpdateStage', Mandatory=$true)]
    [string]$Stage,

    [Parameter(ParameterSetName='Complete', Mandatory=$true)]
    [string]$Complete,

    [Parameter(ParameterSetName='Fail', Mandatory=$true)]
    [string]$Fail,

    [Parameter(ParameterSetName='Archive', Mandatory=$true)]
    [string]$Archive,

    [Parameter(ParameterSetName='ListTasks')]
    [switch]$ListTasks,

    [Parameter(ParameterSetName='Lock', Mandatory=$true)]
    [string]$Lock,

    [Parameter(ParameterSetName='Lock', Mandatory=$true)]
    [Parameter(ParameterSetName='Release', Mandatory=$true)]
    [string]$TaskId,

    [Parameter(ParameterSetName='Release', Mandatory=$true)]
    [string]$Release,

    [Parameter(ParameterSetName='ForceRelease', Mandatory=$true)]
    [string]$ForceRelease,

    [Parameter(ParameterSetName='ListLocks')]
    [switch]$ListLocks,

    [Parameter(ParameterSetName='GetSchema')]
    [switch]$GetSchema,

    [Parameter(ParameterSetName='Help')]
    [switch]$Help
)

# Configuration
$script:StatePath = ".claude/state.json"
$script:TasksDir = ".claude/tasks"

# ============================================================
# HELPER FUNCTIONS
# ============================================================

function Get-IsoTimestamp {
    return (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

function Get-UnixTimestamp {
    return [int][double]::Parse((Get-Date -UFormat %s))
}

function ConvertTo-SafeName {
    param([string]$Name)
    return ($Name.ToLower() -replace '[^a-z0-9-]', '-' -replace '-+', '-').Trim('-')
}

function Initialize-State {
    $dir = Split-Path $script:StatePath -Parent
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    if (-not (Test-Path $script:StatePath)) {
        $initialState = @{
            session = @{
                started = Get-IsoTimestamp
                last_activity = Get-IsoTimestamp
                skill_version = "1.0.0"
                state_backend = "powershell"
                mcp_available = $false
                capability_probe = @{
                    tested_at = Get-IsoTimestamp
                    claude_native = $false
                    powershell = $true
                    cmd = $false
                    bash = $false
                }
            }
            model_schema = @{
                tables = @()
                relationships = @()
            }
            active_tasks = @{}
            resource_locks = @{}
            archived_tasks = @()
        }
        $initialState | ConvertTo-Json -Depth 10 | Set-Content $script:StatePath -Encoding UTF8
    }
}

function Get-State {
    Initialize-State
    return Get-Content $script:StatePath -Raw | ConvertFrom-Json
}

function Save-State {
    param([object]$State)
    $State.session.last_activity = Get-IsoTimestamp
    $State | ConvertTo-Json -Depth 10 | Set-Content $script:StatePath -Encoding UTF8
}

# ============================================================
# SESSION OPERATIONS
# ============================================================

function Show-Summary {
    Initialize-State
    $state = Get-State

    $taskCount = if ($state.active_tasks -is [hashtable]) { $state.active_tasks.Count } else { 0 }
    $lockCount = if ($state.resource_locks -is [hashtable]) { $state.resource_locks.Count } else { 0 }
    $archiveCount = if ($state.archived_tasks -is [array]) { $state.archived_tasks.Count } else { 0 }

    $summary = @{
        session_started = $state.session.started
        last_activity = $state.session.last_activity
        state_backend = $state.session.state_backend
        mcp_available = $state.session.mcp_available
        active_task_count = $taskCount
        lock_count = $lockCount
        archived_count = $archiveCount
    }

    return $summary | ConvertTo-Json
}

function Reset-State {
    if (Test-Path $script:StatePath) {
        Remove-Item $script:StatePath -Force
    }
    Write-Output "State reset complete"
}

# ============================================================
# TASK OPERATIONS
# ============================================================

function New-Task {
    param(
        [string]$Name,
        [string]$WorkflowType
    )

    Initialize-State
    $state = Get-State

    $sanitized = ConvertTo-SafeName $Name
    $timestamp = Get-UnixTimestamp
    $taskId = "$sanitized-$timestamp"
    $taskPath = Join-Path $script:TasksDir $taskId

    # Create task directory
    New-Item -ItemType Directory -Path $taskPath -Force | Out-Null

    # Create findings.md
    $findingsContent = @"
# Task Blackboard: $Name

**Status:** in_progress
**Task ID:** $taskId
**Workflow:** $WorkflowType
**Created:** $(Get-IsoTimestamp)
**Backend:** powershell

---

## Section 1: Requirements
*Pending...*
"@
    Set-Content -Path (Join-Path $taskPath "findings.md") -Value $findingsContent -Encoding UTF8

    # Update state - handle both hashtable and PSCustomObject
    if ($state.active_tasks -isnot [hashtable]) {
        $state.active_tasks = @{}
    }

    $state.active_tasks[$taskId] = @{
        path = $taskPath
        status = "in_progress"
        workflow_type = $WorkflowType
        created = Get-IsoTimestamp
        updated = Get-IsoTimestamp
        current_stage = "init"
    }

    Save-State $state
    Write-Output $taskId
}

function Update-TaskStage {
    param(
        [string]$TaskId,
        [string]$StageName
    )

    $state = Get-State

    if (-not $state.active_tasks.$TaskId) {
        throw "Task not found: $TaskId"
    }

    $state.active_tasks.$TaskId.current_stage = $StageName
    $state.active_tasks.$TaskId.updated = Get-IsoTimestamp

    Save-State $state
    Write-Output "OK"
}

function Complete-Task {
    param([string]$TaskId)

    $state = Get-State

    if (-not $state.active_tasks.$TaskId) {
        throw "Task not found: $TaskId"
    }

    $task = $state.active_tasks.$TaskId
    $task.status = "completed"

    # Add completed_at property (handles PSCustomObject from JSON)
    if ($task.PSObject.Properties['completed_at']) {
        $task.completed_at = Get-IsoTimestamp
    } else {
        $task | Add-Member -NotePropertyName 'completed_at' -NotePropertyValue (Get-IsoTimestamp)
    }

    # Release any locks held by this task
    if ($state.resource_locks.PSObject.Properties.Count -gt 0) {
        $locksToRemove = @()
        foreach ($prop in $state.resource_locks.PSObject.Properties) {
            if ($prop.Value -eq $TaskId) {
                $locksToRemove += $prop.Name
            }
        }
        foreach ($lock in $locksToRemove) {
            $state.resource_locks.PSObject.Properties.Remove($lock)
        }
    }

    Save-State $state
    Write-Output "OK"
}

function Set-TaskFailed {
    param([string]$TaskId)

    $state = Get-State

    if (-not $state.active_tasks.$TaskId) {
        throw "Task not found: $TaskId"
    }

    $task = $state.active_tasks.$TaskId
    $task.status = "failed"

    # Add failed_at property (handles PSCustomObject from JSON)
    if ($task.PSObject.Properties['failed_at']) {
        $task.failed_at = Get-IsoTimestamp
    } else {
        $task | Add-Member -NotePropertyName 'failed_at' -NotePropertyValue (Get-IsoTimestamp)
    }

    Save-State $state
    Write-Output "OK"
}

function Move-TaskToArchive {
    param([string]$TaskId)

    $state = Get-State

    if (-not $state.active_tasks.$TaskId) {
        throw "Task not found: $TaskId"
    }

    $task = $state.active_tasks.$TaskId

    # Add to archive
    if ($state.archived_tasks -isnot [array]) {
        $state.archived_tasks = @()
    }

    $completedAt = if ($task.PSObject.Properties['completed_at'] -and $task.completed_at) {
        $task.completed_at
    } else {
        Get-IsoTimestamp
    }

    $archiveEntry = @{
        task_id = $TaskId
        workflow_type = $task.workflow_type
        completed_at = $completedAt
        status = $task.status
    }
    $state.archived_tasks += $archiveEntry

    # Remove from active
    $state.active_tasks.PSObject.Properties.Remove($TaskId)

    # Release locks (handles PSCustomObject from JSON)
    if ($state.resource_locks.PSObject.Properties.Count -gt 0) {
        $locksToRemove = @()
        foreach ($prop in $state.resource_locks.PSObject.Properties) {
            if ($prop.Value -eq $TaskId) {
                $locksToRemove += $prop.Name
            }
        }
        foreach ($lock in $locksToRemove) {
            $state.resource_locks.PSObject.Properties.Remove($lock)
        }
    }

    Save-State $state
    Write-Output "OK"
}

function Get-Tasks {
    Initialize-State
    $state = Get-State
    return $state.active_tasks | ConvertTo-Json -Depth 5
}

# ============================================================
# LOCK OPERATIONS
# ============================================================

function Add-Lock {
    param(
        [string]$Resource,
        [string]$TaskId
    )

    Initialize-State
    $state = Get-State

    # Get current owner (handles PSCustomObject from JSON)
    $owner = $null
    if ($state.resource_locks.PSObject.Properties[$Resource]) {
        $owner = $state.resource_locks.$Resource
    }

    if ($owner -and $owner -ne $TaskId) {
        Write-Output "LOCKED:$owner"
        exit 1
    }

    # Add or update lock (handles PSCustomObject from JSON)
    if ($state.resource_locks.PSObject.Properties[$Resource]) {
        $state.resource_locks.$Resource = $TaskId
    } else {
        $state.resource_locks | Add-Member -NotePropertyName $Resource -NotePropertyValue $TaskId
    }

    Save-State $state
    Write-Output "OK"
}

function Remove-Lock {
    param(
        [string]$Resource,
        [string]$TaskId
    )

    $state = Get-State

    # Get current owner (handles PSCustomObject from JSON)
    $owner = $null
    if ($state.resource_locks.PSObject.Properties[$Resource]) {
        $owner = $state.resource_locks.$Resource
    }

    if (-not $owner) {
        Write-Output "OK"
        return
    }

    if ($owner -ne $TaskId) {
        throw "Cannot release lock owned by: $owner"
    }

    $state.resource_locks.PSObject.Properties.Remove($Resource)
    Save-State $state
    Write-Output "OK"
}

function Remove-LockForce {
    param([string]$Resource)

    $state = Get-State

    if ($state.resource_locks.PSObject.Properties[$Resource]) {
        $state.resource_locks.PSObject.Properties.Remove($Resource)
        Save-State $state
    }

    Write-Output "OK"
}

function Get-Locks {
    Initialize-State
    $state = Get-State
    return $state.resource_locks | ConvertTo-Json
}

# ============================================================
# SCHEMA OPERATIONS
# ============================================================

function Get-ModelSchema {
    Initialize-State
    $state = Get-State
    return $state.model_schema | ConvertTo-Json -Depth 5
}

# ============================================================
# HELP
# ============================================================

function Show-Help {
    @"
Power BI Analyst Skill - State Manager (PowerShell)

USAGE:
    state_manage.ps1 -Summary                              Show state summary
    state_manage.ps1 -CreateTask "name" [-Workflow type]   Create new task
    state_manage.ps1 -UpdateStage "id" -Stage "stage"      Update task stage
    state_manage.ps1 -Complete "task_id"                   Mark task completed
    state_manage.ps1 -Fail "task_id"                       Mark task failed
    state_manage.ps1 -Archive "task_id"                    Archive task
    state_manage.ps1 -ListTasks                            List active tasks
    state_manage.ps1 -Lock "path" -TaskId "id"             Acquire lock
    state_manage.ps1 -Release "path" -TaskId "id"          Release lock
    state_manage.ps1 -ForceRelease "path"                  Force release lock
    state_manage.ps1 -ListLocks                            List all locks
    state_manage.ps1 -GetSchema                            Get model schema
    state_manage.ps1 -Reset                                Reset all state
    state_manage.ps1 -Help                                 Show this help

EXAMPLES:
    .\state_manage.ps1 -CreateTask "fix-yoy-calc" -Workflow "evaluate"
    .\state_manage.ps1 -Lock "definition/tables/Sales.tmdl" -TaskId "fix-yoy-calc-1734872400"
    .\state_manage.ps1 -Complete "fix-yoy-calc-1734872400"
"@
}

# ============================================================
# MAIN
# ============================================================

try {
    switch ($PSCmdlet.ParameterSetName) {
        'Summary' { Show-Summary }
        'Reset' { Reset-State }
        'CreateTask' { New-Task -Name $CreateTask -WorkflowType $Workflow }
        'UpdateStage' { Update-TaskStage -TaskId $UpdateStage -StageName $Stage }
        'Complete' { Complete-Task -TaskId $Complete }
        'Fail' { Set-TaskFailed -TaskId $Fail }
        'Archive' { Move-TaskToArchive -TaskId $Archive }
        'ListTasks' { Get-Tasks }
        'Lock' { Add-Lock -Resource $Lock -TaskId $TaskId }
        'Release' { Remove-Lock -Resource $Release -TaskId $TaskId }
        'ForceRelease' { Remove-LockForce -Resource $ForceRelease }
        'ListLocks' { Get-Locks }
        'GetSchema' { Get-ModelSchema }
        'Help' { Show-Help }
        default { Show-Help }
    }
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
