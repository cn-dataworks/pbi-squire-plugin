# XMLA Agent Installation Guide

## Step 1: Install Microsoft Analysis Services ADOMD Client

The XMLA agent requires the Microsoft Analysis Services ADOMD Client library to connect to Power BI.

### Option A: Install via SQL Server Feature Pack (Recommended)

1. Download the **Microsoft SQL Server 2019 Feature Pack** (or later)
   - Direct link: https://www.microsoft.com/en-us/download/details.aspx?id=101064
   - Or search for "SQL Server 2022 Feature Pack" for the latest version

2. Look for and download: **Microsoft Analysis Services ADOMD.NET**
   - File: `SQL_AS_ADOMD.msi` (for x64 systems)

3. Run the installer and complete the installation

### Option B: Install via NuGet (Alternative)

If you prefer to install locally without system-wide installation:

```powershell
# Download and extract the ADOMD client
nuget install Microsoft.AnalysisServices.AdomdClient.NetCore.retail.amd64 -OutputDirectory packages
```

Then add the DLL path before importing pyadomd:

```python
import sys
sys.path.append(r'C:\path\to\packages\...\lib\netstandard2.0')
```

### Option C: Install SQL Server Management Studio (SSMS)

SSMS includes all necessary Analysis Services libraries.

1. Download SSMS: https://learn.microsoft.com/sql-server/ssms/download-sql-server-management-studio-ssms
2. Install SSMS (this will install ADOMD Client automatically)

## Step 2: Verify Installation

After installing the ADOMD Client, verify it's available:

```powershell
# Check if the DLL exists
dir "C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.AnalysisServices.AdomdClient"
```

You should see the DLL files if installation was successful.

## Step 3: Install Python Dependencies

```bash
cd xmla_agent
pip install -r requirements.txt
```

## Step 4: Test Connection

```bash
python test_connection.py
```

## Troubleshooting

### Error: "Could not load file or assembly 'Microsoft.AnalysisServices.AdomdClient'"

**Solution:** Install the ADOMD Client using one of the options above.

### Error: "XMLA endpoint not enabled"

**Solution:** Your Power BI admin needs to enable it:
1. Go to Admin Portal → Capacity Settings
2. Select your Premium capacity
3. Under Workloads, set XMLA Endpoint to "Read" or "Read/Write"

### Error: "Authentication failed"

**Solution:**
1. Ensure you're logged into Azure/Power BI
2. You may need to authenticate via browser on first connection
3. Check you have access to the workspace

## Alternative: Use DAX Studio Instead

If you can't install ADOMD Client or prefer a GUI tool, use **DAX Studio**:

1. Download: https://daxstudio.org/
2. Install and open DAX Studio
3. Connect using your workspace URL
4. Run DAX queries directly in the GUI

DAX Studio is excellent for:
- Testing if XMLA is enabled
- Exploring your data model
- Running ad-hoc DAX queries
- Learning DAX syntax

Once you confirm XMLA works in DAX Studio, you can come back to the Python agent.
