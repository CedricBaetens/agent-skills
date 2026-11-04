$ErrorActionPreference = 'Stop'
$testRoot = Join-Path ([IO.Path]::GetTempPath()) ('skill-links-' + [guid]::NewGuid())
$destination = Join-Path $testRoot 'skills'
$source = Join-Path (Split-Path $PSScriptRoot -Parent) 'skills'
$skills = @(Get-ChildItem -LiteralPath $source -Directory | Where-Object {
    Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') -PathType Leaf
})
if (-not $skills.Count) { throw 'No skills available for test.' }

try {
    & "$PSScriptRoot/link-skills.ps1" -Destination $destination
    & "$PSScriptRoot/link-skills.ps1" -Destination $destination
    foreach ($skill in $skills) {
        $link = Get-Item -LiteralPath (Join-Path $destination $skill.Name)
        if ($link.LinkType -ne 'Junction' -or @($link.Target)[0] -ne $skill.FullName) {
            throw "Incorrect link: $($skill.Name)"
        }
        if (-not (Test-Path -LiteralPath (Join-Path $link.FullName 'SKILL.md'))) {
            throw 'Linked skill is unreadable.'
        }
    }

    $conflict = Join-Path $testRoot 'conflict'
    $conflictingSkill = Join-Path $conflict $skills[0].Name
    New-Item -ItemType Directory -Path $conflictingSkill -Force | Out-Null
    $sentinel = Join-Path $conflictingSkill 'keep.txt'
    Set-Content -LiteralPath $sentinel -Value 'preserve me'
    $rejected = $false
    try { & "$PSScriptRoot/link-skills.ps1" -Destination $conflict } catch { $rejected = $true }
    if (-not $rejected -or (Get-Content -LiteralPath $sentinel) -ne 'preserve me') {
        throw 'Conflict was not preserved.'
    }
    if (@(Get-ChildItem -LiteralPath $conflict).Count -ne 1) {
        throw 'Conflict caused partial installation.'
    }
    Write-Output 'PASS: creation, repeat runs, readable links, and conflict preservation.'
} finally {
    # Delete only known temporary entries, never recurse through junction targets.
    if (Test-Path -LiteralPath $destination) {
        Get-ChildItem -LiteralPath $destination | ForEach-Object {
            Remove-Item -LiteralPath $_.FullName -Force
        }
        Remove-Item -LiteralPath $destination
    }
    if ($sentinel -and (Test-Path -LiteralPath $sentinel)) { Remove-Item -LiteralPath $sentinel }
    if ($conflictingSkill -and (Test-Path -LiteralPath $conflictingSkill)) { Remove-Item -LiteralPath $conflictingSkill }
    if ($conflict -and (Test-Path -LiteralPath $conflict)) { Remove-Item -LiteralPath $conflict }
    if (Test-Path -LiteralPath $testRoot) { Remove-Item -LiteralPath $testRoot }
}
