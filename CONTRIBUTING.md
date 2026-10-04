# Contributing to Stock Agent

## Development Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your API credentials
3. Run setup verification: `python -m tests.test_setup`

## Git Workflow

### Optional: Set up Git hooks for automated checks

Git hooks run validation before commits and pushes to catch issues early.

#### Linux / macOS

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
set -e
echo 'Running pre-commit checks...'
python -m tests.test_setup
echo 'Pre-commit checks passed'
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

#### Windows (PowerShell)

```powershell
$hookContent = @'
#!/bin/bash
set -e
python -m tests.test_setup
'@
Set-Content -Path .git/hooks/pre-commit -Value $hookContent -Encoding UTF8
git config core.hooksPath .git/hooks
```

### Available Git hooks

- **pre-commit**: Runs before `git commit` — validates setup and tests
- **pre-push**: Runs before `git push` — final validation before remote push
- **post-merge**: Runs after `git pull` or merge — ensures changes don't break setup

Adjust the scripts in `.git/hooks/` to match your validation needs.

## Code Style

- Run `python -m tests.test_setup` before commits to verify your changes
- Keep the codebase clean and well-tested

## Testing

Run the full setup verification:
```bash
python -m tests.test_setup
```

This validates:
- Python version (3.11+)
- All imports
- Configuration
- Portfolio operations
- Tool definitions
- ChromaDB / RAG availability

## Endpoints and Models

- **Standard Anthropic endpoint**: Uses Claude Haiku 4.5 by default. Override with `ANTHROPIC_MODEL` env var.
- **Custom endpoints**: Leave `ANTHROPIC_MODEL` empty to use the endpoint's deployment default. Set it to override.

See `.env.example` for configuration details.
