<#
.SYNOPSIS
    Antigravity S-Tier Configuration Installer (Windows PowerShell)
.DESCRIPTION
    Automates the installation of all Antigravity S-Tier skills (98+),
    global rules (GEMINI.md, AGENTS.md), project guardrails, plugins,
    and MCP servers into ~/.gemini.
#>

param (
    [switch]$Force = $false,
    [switch]$SkipMcp = $false
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  ANTIGRAVITY S-TIER ENTERPRISE SETUP INSTALLER (Windows) " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$userHome = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::UserProfile)
$geminiDir = Join-Path $userHome ".gemini"
$configDir = Join-Path $geminiDir "config"
$skillsDir = Join-Path $configDir "skills"
$templatesDir = Join-Path $geminiDir "templates"
$pluginsDir = Join-Path $configDir "plugins"
$mcpDir = Join-Path $geminiDir "mcp-servers"

$repoRoot = $PSScriptRoot

Write-Host "`n[1/6] Target Environment:" -ForegroundColor Yellow
Write-Host "  User Profile : $userHome"
Write-Host "  Gemini Home  : $geminiDir"

# Create directories
New-Item -ItemType Directory -Path $geminiDir -Force | Out-Null
New-Item -ItemType Directory -Path $configDir -Force | Out-Null
New-Item -ItemType Directory -Path $skillsDir -Force | Out-Null
New-Item -ItemType Directory -Path $templatesDir -Force | Out-Null
New-Item -ItemType Directory -Path $pluginsDir -Force | Out-Null
New-Item -ItemType Directory -Path $mcpDir -Force | Out-Null

# 1. Install Skills
Write-Host "`n[2/6] Installing 98+ S-Tier Skills..." -ForegroundColor Yellow
$srcSkills = Join-Path $repoRoot "skills"
if (Test-Path $srcSkills) {
    Copy-Item -Path "$srcSkills\*" -Destination $skillsDir -Recurse -Force
    $count = (Get-ChildItem $skillsDir -Directory).Count
    Write-Host "  -> Successfully installed $count skills in $skillsDir" -ForegroundColor Green
}

# 2. Install Guardrails & Templates
Write-Host "`n[3/6] Installing Project Guardrails & Templates..." -ForegroundColor Yellow
$srcTemplates = Join-Path $repoRoot "templates"
if (Test-Path $srcTemplates) {
    Copy-Item -Path "$srcTemplates\*" -Destination $templatesDir -Recurse -Force
    Write-Host "  -> Guardrails & templates synced to $templatesDir" -ForegroundColor Green
}

# 3. Install Global Rules (GEMINI.md & AGENTS.md)
Write-Host "`n[4/6] Installing Global Cognitive Rules & Invariants..." -ForegroundColor Yellow
$srcRules = Join-Path $repoRoot "rules"
if (Test-Path $srcRules) {
    Copy-Item -Path "$srcRules\GEMINI.md" -Destination $geminiDir -Force
    Copy-Item -Path "$srcRules\AGENTS.md" -Destination $geminiDir -Force
    Write-Host "  -> Copied GEMINI.md and AGENTS.md to $geminiDir" -ForegroundColor Green
}

# 4. Install Plugins
Write-Host "`n[5/6] Installing Plugins..." -ForegroundColor Yellow
$srcPlugins = Join-Path $repoRoot "plugins"
if (Test-Path $srcPlugins) {
    Copy-Item -Path "$srcPlugins\*" -Destination $pluginsDir -Recurse -Force
    Write-Host "  -> Plugins synced to $pluginsDir" -ForegroundColor Green
}

# 5. Setup Custom MCP Servers & MCP Config
Write-Host "`n[6/6] Configuring MCP Servers..." -ForegroundColor Yellow
if (-not $SkipMcp) {
    $srcMcpServers = Join-Path $repoRoot "mcp\custom-servers"
    if (Test-Path $srcMcpServers) {
        Copy-Item -Path "$srcMcpServers\*" -Destination $mcpDir -Recurse -Force
        Write-Host "  -> Custom MCP servers copied to $mcpDir" -ForegroundColor Green
    }

    $templateFile = Join-Path $repoRoot "mcp\mcp_config.template.json"
    $targetMcpConfig = Join-Path $configDir "mcp_config.json"

    if (Test-Path $templateFile) {
        # Backup existing
        if ((Test-Path $targetMcpConfig) -and (-not $Force)) {
            Copy-Item -Path $targetMcpConfig -Destination "$targetMcpConfig.bak" -Force
            Write-Host "  -> Backed up existing mcp_config.json to .bak" -ForegroundColor Cyan
        }

        # Replace {{USER_HOME}} with actual $userHome
        $escapedHome = $userHome.Replace('\', '\\')
        $rawTemplate = Get-Content -Path $templateFile -Raw -Encoding UTF8
        $finalConfig = $rawTemplate.Replace('{{USER_HOME}}', $escapedHome)

        # Update specific custom-servers path to point to $mcpDir
        $escapedMcpDir = $mcpDir.Replace('\', '\\')
        $finalConfig = $finalConfig.Replace("{{USER_HOME}}\\security_repos", $escapedMcpDir)

        $finalConfig | Set-Content -Path $targetMcpConfig -Encoding UTF8
        Write-Host "  -> Successfully generated active $targetMcpConfig" -ForegroundColor Green
    }
}

# 6. Install Lessons & Postmortems DB
Write-Host "`n[7/8] Installing Epistemic Lessons & Incident Postmortems..." -ForegroundColor Yellow
$godkillerDir = Join-Path $geminiDir "godkiller_data"
New-Item -ItemType Directory -Path $godkillerDir -Force | Out-Null
$srcLessonsDb = Join-Path $repoRoot "lessons\lessons.db"
if (Test-Path $srcLessonsDb) {
    Copy-Item -Path $srcLessonsDb -Destination "$godkillerDir\lessons.db" -Force
    Write-Host "  -> Epistemic lessons database synced to $godkillerDir\lessons.db" -ForegroundColor Green
}
$srcUiArt = Join-Path $repoRoot "lessons\ui_artifacts"
if (Test-Path $srcUiArt) {
    $dstUiArt = Join-Path $godkillerDir "arena\results\ui_artifacts"
    New-Item -ItemType Directory -Path $dstUiArt -Force | Out-Null
    Copy-Item -Path "$srcUiArt\*" -Destination $dstUiArt -Force
    Write-Host "  -> Synced 21 QA journey verification manifests to $dstUiArt" -ForegroundColor Green
}

# 7. Install Antigravity System Internals (MCP Schemas, Builtin Skills, Bin, Prompting)
Write-Host "`n[8/8] Installing Antigravity System Internals (MCP Tool Schemas, Builtins, Tools)..." -ForegroundColor Yellow
$agSystemDir = Join-Path $geminiDir "antigravity"
New-Item -ItemType Directory -Path $agSystemDir -Force | Out-Null
$srcAgSystem = Join-Path $repoRoot "antigravity-system"
if (Test-Path $srcAgSystem) {
    Copy-Item -Path "$srcAgSystem\*" -Destination $agSystemDir -Recurse -Force
    Write-Host "  -> Antigravity MCP tool schemas (33 tool suites) & builtin skills deployed to $agSystemDir" -ForegroundColor Green
}

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "  INSTALLATION COMPLETE! ANTIGRAVITY IS NOW S-TIER READY   " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "What's now active:" -ForegroundColor Cyan
Write-Host "  [+] 153+ Production Skills (Frontend 5-Source, Stitch, OWASP, SecuritySkills, Semgrep, etc.)"
Write-Host "  [+] 4 Native Antigravity Built-in Skills (agy-customizations, generative_ui, etc.)"
Write-Host "  [+] 33 MCP Tool Schema Suites (Godkiller, Canva, Notion, Playwright, Semgrep, etc.)"
Write-Host "  [+] 4-Layer Git Push Safety Policy (git-push-policy.md)"
Write-Host "  [+] User Persona (Senior Dev Voice, Cognitive Thinking Reference & Archive)"
Write-Host "  [+] API Incident Lessons (lessons.db, sprint-1-auth-api-fix, BOLA/BFLA guards)"
Write-Host "  [+] 21 UI Journey Verification Manifests (godkiller_data/arena/results/ui_artifacts)"
Write-Host "  [+] Enterprise Guardrails (Mermaid Parity, AI-Slop Audits, Boundary Checks)"
Write-Host "  [+] Global Persona & Anti-AI Template Rules (GEMINI.md / AGENTS.md)"
Write-Host "  [+] Complete MCP Server Mesh (Godkiller, Notion, Canva, Semgrep, Playwright, etc.)"
Write-Host "`nTo verify, start Antigravity and ask: 'ตอนนี้ skill และ mcp ที่มีทั้งหมดมีอะไรบ้าง'`n"
