# Claude Config Sync Script v5.0
# Sync rules/agents/skills/CLAUDE.md + FormatConvert + Rollback

param(
    [switch]$DryRun,
    [switch]$Backup,
    [switch]$FormatConvert,
    [switch]$Rollback,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$SOURCE_DIR = $env:USERPROFILE + "\.claude"
$BACKUP_DIR = "$env:USERPROFILE\.claude\backups"
$BACKUP_TIMESTAMP = Get-Date -Format 'yyyyMMdd-HHmmss'

# Sync targets
$TARGETS = @{
    "Cursor"   = "$env:USERPROFILE\.cursor"
    "Windsurf" = "$env:USERPROFILE\.windsurf"
    "Trae"     = "$env:USERPROFILE\.trae"
}

# Sync items
$SYNC_ITEMS = @(
    @{ Source = "CLAUDE.md"; Dest = "CLAUDE.md"; Type = "file" }
    @{ Source = "rules"; Dest = "rules"; Type = "directory" }
    @{ Source = "agents"; Dest = "agents"; Type = "directory" }
    @{ Source = "skills"; Dest = "skills"; Type = "directory" }
)

# Exclude
$EXCLUDE_DIRS = @("hooks", ".git", "sessions", "plans", "projects", "logs", "cache", "temp", "backups")
$EXCLUDE_FILES = @(".mcp.json", "settings.json", ".claude.json", "sync.ps1", "SYNC_GUIDE.md", "README.md")

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $colorMap = @{
        "INFO" = "White"
        "WARN" = "Yellow"
        "ERROR" = "Red"
        "SUCCESS" = "Green"
        "DIFF" = "Cyan"
    }
    $color = if ($colorMap.ContainsKey($Level)) { $colorMap[$Level] } else { "White" }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

# ========== Format Convert ==========

function Convert-ConfigForEditor {
    param([string]$TargetEditor, [string]$SourcePath, [string]$DestPath)

    $content = Get-Content $SourcePath -Raw -Encoding UTF8

    if ($SourcePath -match "\.json$") {
        $content = $content -replace '"_comment":\s*"([^"]*)"', '// $1'
        $content = $content -replace '"_note":\s*"([^"]*)"', '// $1'
        $content = $content -replace '"_section":\s*"([^"]*)"', '// $1'
        $content = $content -replace '"_description":\s*"([^"]*)"', '// $1'
    }

    return $content
}

function Invoke-FormatConvert {
    param([string]$TargetName, [string]$TargetPath)

    Write-Log "===== Format Convert: $TargetName =====" "INFO"

    $settingsSource = "$SOURCE_DIR\settings.json"
    $settingsDest = "$TARGETPATH\settings.json"

    if (Test-Path $settingsSource) {
        $converted = Convert-ConfigForEditor -TargetEditor $TargetName -SourcePath $settingsSource -DestPath $settingsDest
        if ($DryRun) {
            Write-Log "[DRYRUN] Format convert: $settingsSource -> $settingsDest" "DIFF"
        } else {
            $converted | Set-Content -Path $settingsDest -Encoding UTF8
            Write-Log "Converted: $settingsDest" "SUCCESS"
        }
    }
}

# ========== Rollback ==========

function Get-LatestBackup {
    $backups = Get-ChildItem -Path $BACKUP_DIR -Directory -Filter "sync-*" | Sort-Object LastWriteTime -Descending
    if ($backups) { return $backups[0].FullName }
    return $null
}

function Invoke-Rollback {
    Write-Log "===== Rollback =====" "INFO"

    if ($DryRun) {
        Write-Log "[DRYRUN] Will rollback" "WARN"
        return
    }

    $latestBackup = Get-LatestBackup
    if (-not $latestBackup) {
        Write-Log "No backup found" "ERROR"
        return
    }

    Write-Log "Using backup: $latestBackup" "INFO"

    foreach ($target in $TARGETS.Keys) {
        $backupTarget = "$latestBackup\$target"
        $targetPath = $TARGETS[$target]
        if (Test-Path $backupTarget) {
            Copy-Item -Path "$backupTarget\*" -Destination $targetPath -Recurse -Force
            Write-Log "Rolled back: $targetPath" "SUCCESS"
        }
    }
    Write-Log "Rollback complete" "SUCCESS"
}

# ========== Backup ==========

function New-Backup {
    Write-Log "Create backup: $BACKUP_DIR\sync-$BACKUP_TIMESTAMP" "INFO"
    if (-not $DryRun) {
        $backupPath = "$BACKUP_DIR\sync-$BACKUP_TIMESTAMP"
        New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
        foreach ($target in $TARGETS.Keys) {
            $targetPath = $TARGETS[$target]
            if (Test-Path $targetPath) {
                $backupTarget = "$backupPath\$target"
                New-Item -ItemType Directory -Path $backupTarget -Force | Out-Null
                Copy-Item -Path "$targetPath\*" -Destination $backupTarget -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
        Write-Log "Backup complete" "SUCCESS"
    }
}

# ========== Sync Core ==========

function Sync-File {
    param([string]$SourcePath, [string]$DestPath)

    if (-not (Test-Path $SourcePath)) {
        Write-Log "Source not found: $SourcePath" "WARN"
        return $false
    }

    $destDir = Split-Path -Parent $DestPath
    if (-not (Test-Path $destDir)) {
        if (-not $DryRun) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
    }

    if ($DryRun) {
        $sourceSize = (Get-Item $SourcePath).Length
        $action = if (Test-Path $DestPath) { "UPDATE" } else { "CREATE" }
        Write-Log "[DRYRUN] [$action] $sourceSize bytes $SourcePath -> $DestPath" "DIFF"
        return $true
    }

    if ((Test-Path $DestPath) -and ((Get-Item $DestPath).LastWriteTime -ge (Get-Item $SourcePath).LastWriteTime)) {
        if ($Verbose) { Write-Log "Skip (unchanged): $DestPath" "INFO" }
        return $false
    }

    Copy-Item -Path $SourcePath -Destination $DestPath -Force
    Write-Log "Synced: $DestPath" "SUCCESS"
    return $true
}

function Sync-Directory {
    param([string]$SourceDir, [string]$DestDir)

    if (-not (Test-Path $SourceDir)) {
        Write-Log "Source dir not found: $SourceDir" "WARN"
        return
    }

    if (-not (Test-Path $DestDir)) {
        if (-not $DryRun) { New-Item -ItemType Directory -Path $DestDir -Force | Out-Null }
    }

    $items = Get-ChildItem -Path $SourceDir -Recurse -ErrorAction SilentlyContinue
    $syncCount = 0

    foreach ($item in $items) {
        if ($EXCLUDE_DIRS -contains $item.Name) { continue }

        $relativePath = $item.FullName.Substring($SourceDir.Length).TrimStart("\")
        $destPath = Join-Path $DestDir $relativePath

        if ($item.PSIsContainer) {
            if (-not (Test-Path $destPath)) {
                if (-not $DryRun) { New-Item -ItemType Directory -Path $destPath -Force | Out-Null }
            }
        } else {
            $fileName = Split-Path -Leaf $item.FullName
            if ($EXCLUDE_FILES -contains $fileName) { continue }

            if ($SourceDir -match "skills$") {
                if ($fileName -ne "SKILL.md" -and $fileName -ne "README.md") { continue }
            }

            if (Sync-File -SourcePath $item.FullName -DestPath $destPath) { $syncCount++ }
        }
    }
    return $syncCount
}

function Invoke-Sync {
    param([string]$TargetName, [string]$TargetPath)

    Write-Log "===== Sync to $TargetName =====" "INFO"

    if (-not (Test-Path $TargetPath)) {
        Write-Log "Target dir not found: $TargetPath" "WARN"
        if (-not $DryRun) { New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null }
    }

    $totalSynced = 0
    foreach ($item in $SYNC_ITEMS) {
        $sourcePath = Join-Path $SOURCE_DIR $item.Source
        $destPath = Join-Path $TargetPath $item.Dest

        switch ($item.Type) {
            "file" {
                if (Test-Path $sourcePath) { Sync-File -SourcePath $sourcePath -DestPath $destPath }
            }
            "directory" {
                $count = Sync-Directory -SourceDir $sourcePath -DestDir $destPath
                $totalSynced += $count
            }
        }
    }

    if ($FormatConvert) { Invoke-FormatConvert -TargetName $TargetName -TargetPath $TargetPath }

    Write-Log "$TargetName sync complete (+$totalSynced files)`n" "SUCCESS"
}

# ========== Main ==========

Write-Log "===== Claude Config Sync v5.0 =====" "INFO"
Write-Log "Source: $SOURCE_DIR" "INFO"

if ($DryRun) { Write-Log "[DRYRUN] Preview only" "WARN" }
if ($FormatConvert) { Write-Log "[FormatConvert] Claude Code -> Editor compatible" "INFO" }

if ($Rollback) {
    Invoke-Rollback
    exit 0
}

if ($Backup) { New-Backup }

$successCount = 0
$failCount = 0

foreach ($target in $TARGETS.Keys) {
    try {
        Invoke-Sync -TargetName $target -TargetPath $TARGETS[$target]
        $successCount++
    } catch {
        Write-Log "Sync failed: $_" "ERROR"
        $failCount++
    }
}

Write-Log "===== Sync Report =====" "INFO"
Write-Log "Success: $successCount / $($TARGETS.Count)" $(if ($failCount -eq 0) { "SUCCESS" } else { "WARN" })
Write-Log "Failed: $failCount" $(if ($failCount -gt 0) { "ERROR" } else { "INFO" })

if ($failCount -gt 0 -and -not $DryRun) {
    Write-Log "Use -Rollback to restore" "WARN"
}
