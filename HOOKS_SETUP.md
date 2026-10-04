# Hooks Setup Guide

## Git Hooks (Recommended)

For automated validation on git commit/push, set up Git hooks in `.git/hooks/`. 

**See [CONTRIBUTING.md](CONTRIBUTING.md) for complete Git hooks setup instructions** for:
- Linux/macOS setup
- Windows PowerShell setup  
- Available hooks: pre-commit, pre-push, post-merge

## Claude Code Hooks (Not Currently Supported)

⚠️ **Note:** Claude Code does not currently support the lifecycle hook names shown below. This section is retained for reference only. For automated checks, use Git hooks instead (see CONTRIBUTING.md).

## Reference: Unsupported Claude Code Hook Format

These hook names and formats are not currently supported by Claude Code. For working automation, use Git hooks (see [CONTRIBUTING.md](CONTRIBUTING.md)).

Example of unsupported configuration (for reference):

```json
{
  "hooks": {
    "pre_commit": "/check-security && /lint-agent && /test-agent 'test query'",
    "post_commit": "/generate-docs",
    "pre_push": "/validate-config && /test-tools",
    "on_open": "/validate-config",
    "post_fetch": "/validate-config"
  }
}
```

## 4. Restart Claude Code

Close and reopen Claude Code for hooks to activate.

## 5. Test

Try these to verify hooks work:

```bash
# Should run pre_commit hooks
git commit -m "test"

# Should run pre_push hooks
git push
```

## What Each Hook Does

| Hook | When | Skills |
|------|------|--------|
| `on_open` | Project opens | Validates configuration |
| `pre_commit` | Before commit | Checks security, lints code, tests agent |
| `post_commit` | After commit | Updates documentation |
| `pre_push` | Before push | Final validation and tool tests |
| `post_fetch` | After pull | Validates setup |

## If Hooks Don't Work

1. Check file is at `~/.claude/settings.json` (not `.local.json`)
2. Verify JSON syntax is correct (use online JSON validator)
3. Restart Claude Code completely
4. Check logs: `~/.claude/logs/`

## Disable a Hook

Remove the hook from the configuration. For example, to disable `pre_push`:

```json
{
  "hooks": {
    "pre_commit": "/check-security && /lint-agent",
    "post_commit": "/generate-docs",
    "on_open": "/validate-config"
  }
}
```

(Note: `pre_push` was removed from the example above)

## Customize Hooks

Make them faster by removing slower skills:

```json
{
  "pre_commit": "/check-security && /lint-agent"
}
```

Or more thorough:

```json
{
  "pre_commit": "/check-security && /lint-agent && /test-agent && /test-tools"
}
```

## See Also

- [CONTRIBUTING.md](CONTRIBUTING.md) - Git hooks setup and development workflow
- [skill.md](skill.md) - Development guide and testing
- [Claude Code Documentation](https://claude.com/claude-code)
