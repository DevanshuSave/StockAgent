# Claude Code Hooks Setup Guide

Quick guide to enable automated skills for Stock Agent.

## 1. Locate Settings File

```bash
# Linux/Mac
~/.claude/settings.json

# Windows
%USERPROFILE%\.claude\settings.json
```

Or in Claude Code:
- Open Settings
- Look for `.claude/settings.json` file path

## 2. Copy Hooks Configuration

Open `hooks-example.json` in this repo and copy the `hooks` object.

## 3. Edit Settings File

Add to your `~/.claude/settings.json`:

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

Remove or comment it out:

```json
{
  "hooks": {
    "pre_commit": "/check-security && /lint-agent",
    "post_commit": "/generate-docs",
    // "pre_push": "/validate-config && /test-tools",
    "on_open": "/validate-config"
  }
}
```

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

- `skill.md` - Complete skill reference
- `hooks-example.json` - Full configuration with explanations
- [Claude Code Documentation](https://claude.com/claude-code)
