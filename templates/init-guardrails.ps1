# ==============================================================================
# 🚀 Global Project Guardrails Auto-Scaffolder
# Installs CLAUDE.md, backup script, autocommit watcher, and CI/CD into ANY project
# ==============================================================================
param (
    [string]$TargetDir = (Get-Location).Path
)

$ErrorActionPreference = "Stop"
$TemplateDir = "C:\Users\ffram\.gemini\templates\project-guardrails"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "🚀 Initializing S-Tier Guardrails in: $TargetDir" -ForegroundColor Cyan
Write-Host "=========================================================="

if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
}

# 1. Initialize Git if not present
Push-Location $TargetDir
try {
    if (-not (Test-Path (Join-Path $TargetDir ".git"))) {
        git init --quiet
        Write-Host "[+] Initialized Git repository." -ForegroundColor Green
    }
} finally {
    Pop-Location
}

# 2. Copy CLAUDE.md
$ClaudeDest = Join-Path $TargetDir "CLAUDE.md"
if (-not (Test-Path $ClaudeDest)) {
    Copy-Item (Join-Path $TemplateDir "CLAUDE.md") $ClaudeDest -Force
    Write-Host "[+] Generated CLAUDE.md (Anti-Amnesia, Anti-Phantom UI, Disaster Recovery)" -ForegroundColor Green
}

# 3. Copy backup-project.ps1
$BackupDest = Join-Path $TargetDir "backup-project.ps1"
if (-not (Test-Path $BackupDest)) {
    Copy-Item (Join-Path $TemplateDir "backup-project.ps1") $BackupDest -Force
    Write-Host "[+] Generated backup-project.ps1 (Disaster Recovery Snapshot)" -ForegroundColor Green
}

# 4. Copy watch-autocommit.ps1
$WatchDest = Join-Path $TargetDir "watch-autocommit.ps1"
if (-not (Test-Path $WatchDest)) {
    Copy-Item (Join-Path $TemplateDir "watch-autocommit.ps1") $WatchDest -Force
    Write-Host "[+] Generated watch-autocommit.ps1 (Automated Git Safety Net)" -ForegroundColor Green
}

# 5. Copy .github/workflows/ci.yml
$GithubWorkflowDir = Join-Path $TargetDir ".github\workflows"
if (-not (Test-Path $GithubWorkflowDir)) {
    New-Item -ItemType Directory -Path $GithubWorkflowDir -Force | Out-Null
}
$CiDest = Join-Path $GithubWorkflowDir "ci.yml"
if (-not (Test-Path $CiDest)) {
    Copy-Item (Join-Path $TemplateDir "ci.yml") $CiDest -Force
    Write-Host "[+] Generated .github/workflows/ci.yml (Automated CI/CD Gatekeeper)" -ForegroundColor Green
}

# 6. Generate .gitignore if missing
$GitIgnoreDest = Join-Path $TargetDir ".gitignore"
if (-not (Test-Path $GitIgnoreDest)) {
    @'
node_modules
.next
dist
build
coverage
.turbo
.env
.env.local
.env.*.local
*.tar.gz
*.zip
logs
*.log
'@ | Out-File -FilePath $GitIgnoreDest -Encoding utf8
    Write-Host "[+] Generated .gitignore (Zero-Exposure & Cache Exclusions)" -ForegroundColor Green
}

# 7. Copy .gitattributes (Anti-Build-Pollution export-ignore rules)
$GitAttributesDest = Join-Path $TargetDir ".gitattributes"
if (-not (Test-Path $GitAttributesDest)) {
    Copy-Item (Join-Path $TemplateDir ".gitattributes") $GitAttributesDest -Force
    Write-Host "[+] Generated .gitattributes (Anti-Build-Pollution export-ignore rules)" -ForegroundColor Green
}

# 8. Copy export-clean-delivery.ps1
$ExportDest = Join-Path $TargetDir "export-clean-delivery.ps1"
if (-not (Test-Path $ExportDest)) {
    Copy-Item (Join-Path $TemplateDir "export-clean-delivery.ps1") $ExportDest -Force
    Write-Host "[+] Generated export-clean-delivery.ps1 (Clean Client Delivery Exporter)" -ForegroundColor Green
}

# 9. Copy audit-ai-slop.ps1
$AuditSlopDest = Join-Path $TargetDir "audit-ai-slop.ps1"
if (-not (Test-Path $AuditSlopDest)) {
    Copy-Item (Join-Path $TemplateDir "audit-ai-slop.ps1") $AuditSlopDest -Force
    Write-Host "[+] Generated audit-ai-slop.ps1 (Anti-AI Slop Language & Test Leak Linter)" -ForegroundColor Green
}

# 10. Copy audit-mermaid-parity.ps1
$AuditMermaidDest = Join-Path $TargetDir "audit-mermaid-parity.ps1"
if (-not (Test-Path $AuditMermaidDest)) {
    Copy-Item (Join-Path $TemplateDir "audit-mermaid-parity.ps1") $AuditMermaidDest -Force
    Write-Host "[+] Generated audit-mermaid-parity.ps1 (Automated Mermaid Parity & Architecture Linter)" -ForegroundColor Green
}

# 11. Copy .dependency-cruiser.js
$DepCruiseDest = Join-Path $TargetDir ".dependency-cruiser.js"
if (-not (Test-Path $DepCruiseDest)) {
    Copy-Item (Join-Path $TemplateDir ".dependency-cruiser.js") $DepCruiseDest -Force
    Write-Host "[+] Generated .dependency-cruiser.js (Architectural Boundary Rules)" -ForegroundColor Green
}

# 12. Copy audit-architecture-boundaries.ps1
$AuditArchDest = Join-Path $TargetDir "audit-architecture-boundaries.ps1"
if (-not (Test-Path $AuditArchDest)) {
    Copy-Item (Join-Path $TemplateDir "audit-architecture-boundaries.ps1") $AuditArchDest -Force
    Write-Host "[+] Generated audit-architecture-boundaries.ps1 (Architectural Boundary Linter)" -ForegroundColor Green
}

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "🎉 All S-Tier Guardrails successfully installed!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

