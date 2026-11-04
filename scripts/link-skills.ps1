# Run after adding skills: pwsh -File scripts/link-skills.ps1
[CmdletBinding()]
param(
    [string]$Destination = $(if ($env:CODEX_HOME) {
        Join-Path $env:CODEX_HOME 'skills'
    } else {
        Join-Path $HOME '.codex/skills'
    })
)

$ErrorActionPreference = 'Stop'
$source = Join-Path (Split-Path $PSScriptRoot -Parent) 'skills'
$Destination = [IO.Path]::GetFullPath($Destination)
$pending = @()

# Check every destination before creating links; never replace existing content.
foreach ($skill in Get-ChildItem -LiteralPath $source -Directory) {
    if (-not (Test-Path -LiteralPath (Join-Path $skill.FullName 'SKILL.md') -PathType Leaf)) {
        continue
    }
    $link = Join-Path $Destination $skill.Name
    $existing = Get-Item -LiteralPath $link -Force -ErrorAction SilentlyContinue
    if ($existing) {
        if ($existing.LinkType -eq 'Junction' -and
            [IO.Path]::GetFullPath(@($existing.Target)[0]) -eq $skill.FullName) {
            Write-Output "Already linked: $($skill.Name)"
            continue
        }
        throw "Cannot link '$link': destination already exists. Move it aside after checking its contents, then rerun."
    }
    $pending += @{ Path = $link; Target = $skill.FullName }
}

if ($pending.Count) {
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    foreach ($entry in $pending) {
        New-Item -ItemType Junction @entry | Out-Null
        Write-Output "Linked: $($entry.Path) -> $($entry.Target)"
    }
}
