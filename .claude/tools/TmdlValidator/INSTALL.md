# Installation Instructions for TMDL Validator

## Prerequisites

The C# TMDL Validator requires .NET 8.0 SDK to build.

### Installing .NET 8.0 SDK

1. **Download .NET 8.0 SDK**
   Visit: https://dotnet.microsoft.com/download/dotnet/8.0

   Direct link: https://aka.ms/dotnet/8.0/dotnet-sdk-win-x64.exe

2. **Install the SDK**
   Run the downloaded installer and follow the installation wizard.

3. **Verify Installation**
   Open a new terminal and run:
   ```bash
   dotnet --version
   ```

   You should see output like: `8.0.xxx`

## Building the Validator

Once .NET 8.0 SDK is installed:

```powershell
cd C:\Users\anorthrup\Documents\power_bi_analyst\.claude\tools\TmdlValidator
.\build.ps1
```

This will:
- Restore NuGet packages (Microsoft.AnalysisServices, etc.)
- Compile the C# code
- Publish as a self-contained executable (~50MB)
- Copy `TmdlValidator.exe` to `.claude/tools/` directory

## Using Pre-Built Executable (Alternative)

If you prefer not to build from source, you can:

1. Download a pre-built release from the GitHub releases page
2. Place `TmdlValidator.exe` in `.claude/tools/` directory
3. Ensure it has execute permissions

## Troubleshooting

### "dotnet command not found"
- .NET SDK not installed or not in PATH
- Restart terminal after installing .NET SDK
- Verify with `dotnet --version`

### "Failed to restore packages"
- Check internet connection (NuGet packages download from nuget.org)
- Clear NuGet cache: `dotnet nuget locals all --clear`
- Try again

### "Access denied" when copying executable
- Close any running instances of TmdlValidator.exe
- Run PowerShell as Administrator

## System Requirements

- **OS**: Windows 10/11 x64
- **SDK** (build time): .NET 8.0 SDK
- **Runtime** (execution): Self-contained - no runtime required
- **Disk Space**: ~50MB for executable
