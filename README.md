# Agent skills

Reusable skills live in `skills/<name>/SKILL.md`.

## Link skills to Codex

On Windows with PowerShell 7, run from the repository root:

```powershell
pwsh -File scripts/link-skills.ps1
```

The script creates a directory junction for each skill in
`$HOME/.codex/skills` (or `$CODEX_HOME/skills` when set). Files stay in this
repository, so edits are immediately available through the links.

After adding a new skill under `skills/`, run the command again. Correct links
are skipped. Conflicting files or folders are left untouched; inspect and move
them aside before retrying. Keep the repository at its linked location.

To use another destination:

```powershell
pwsh -File scripts/link-skills.ps1 -Destination 'C:/path/to/.codex/skills'
```

## Test the linking script

```powershell
pwsh -File scripts/test-link-skills.ps1
```

Tests use temporary directories to check link creation, repeat runs, readable
skills, and preservation of conflicting folders.
