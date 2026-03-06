param(
    [string]$Message = "",
    [string]$Branch = "main",
    [string]$Remote = "origin",
    [switch]$NoPush
)

$ErrorActionPreference = "Stop"

function Fail([string]$msg) {
    Write-Host "[ERROR] $msg" -ForegroundColor Red
    exit 1
}

function Info([string]$msg) {
    Write-Host "[INFO] $msg" -ForegroundColor Cyan
}

try {
    git --version *> $null
} catch {
    Fail "Git not found. Please install Git first."
}

try {
    $inside = git rev-parse --is-inside-work-tree 2>$null
} catch {
    $inside = ""
}
if ($inside -ne "true") {
    Fail "Current directory is not a Git repository."
}

if ([string]::IsNullOrWhiteSpace($Message)) {
    $Message = "chore: auto push $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
}

# Stage all tracked/untracked changes
git add -A

# Check if there is anything to commit
$pending = git diff --cached --name-only
if ([string]::IsNullOrWhiteSpace($pending)) {
    Info "No staged changes. Nothing to commit."
    exit 0
}

Info "Committing changes..."
git commit -m $Message

if ($NoPush) {
    Info "Commit done. --NoPush set, skipping push."
    exit 0
}

# Validate remote exists
$remoteExists = git remote | Select-String -SimpleMatch $Remote
if (-not $remoteExists) {
    Fail "Remote '$Remote' not found. Use: git remote add $Remote <repo-url>"
}

Info "Pushing to $Remote/$Branch ..."
git push -u $Remote $Branch
Info "Done."

