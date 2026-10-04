# Stock Agent Development Guide

Reference guide for developing and testing the Stock Agent project.

**Note:** The commands documented below are examples of how to structure development workflows. To create actual Claude Code skills (invokable via `/command`), define them in `.claude/skills/` or use the Skill tool.

## Built-in Testing

### python -m tests.test_setup

**Description:** Run comprehensive setup verification

**Usage:**
```bash
python -m tests.test_setup
```

**What it validates:**
- Python version (3.11-3.13)
- Configuration and environment variables
- Portfolio operations
- Tool definitions
- ChromaDB / RAG availability

Run this before committing to ensure the system is in working order.

## Development Workflow

**Before committing:**
1. Run `python -m tests.test_setup` to ensure everything works
2. Review your changes
3. Create a commit with meaningful message

**After pulling changes:**
1. Run `python -m tests.test_setup` to verify merged changes work
2. Check if `.env` needs any new variables
3. Update local setup if needed

## Git Hooks (Optional)

For automated validation before commits/pushes, set up Git hooks. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions.

## Notes

- All commands and scripts should be run from the project root directory
- Always run `python -m tests.test_setup` before pushing changes
- Check [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and Git hooks
