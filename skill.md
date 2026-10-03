# Stock Agent Development Skills

Custom Claude Code commands for developing, testing, and managing the Stock Agent project.

## Available Commands

### /test-agent
**Description:** Run the agent with a test query to validate functionality

**Usage:**
```bash
/test-agent [query]
```

**Examples:**
- `/test-agent` - Run with default query "which stock should I buy with $2000?"
- `/test-agent "Analyze Apple stock"` - Test with custom query

**What it does:**
- Validates API connection and model configuration
- Tests agent orchestration and tool execution
- Provides sample output for verification
- Useful after config changes or updates

---

### /validate-config
**Description:** Verify environment configuration and API setup

**Usage:**
```bash
/validate-config
```

**What it does:**
- Checks if .env file exists and has required keys
- Validates API key format
- Verifies model configuration
- Checks Python version compatibility for RAG
- Reports any missing dependencies
- Suggests fixes for common issues

---

### /lint-agent
**Description:** Run code quality checks on Python files

**Usage:**
```bash
/lint-agent [path]
```

**Examples:**
- `/lint-agent` - Check all Python files
- `/lint-agent agent/` - Check only agent directory
- `/lint-agent config.py` - Check specific file

**What it does:**
- Check Python syntax
- Identify unused imports
- Find code style issues
- Report potential bugs
- Suggest improvements

---

### /test-tools
**Description:** Run unit tests for individual tools

**Usage:**
```bash
/test-tools [tool_name]
```

**Examples:**
- `/test-tools` - Run all tool tests
- `/test-tools stock_data` - Test stock data tools only
- `/test-tools portfolio` - Test portfolio tools only

**What it does:**
- Execute tool unit tests
- Validate tool outputs
- Check error handling
- Report test coverage
- Identify broken tools

---

### /validate-portfolio
**Description:** Test portfolio operations and RAG features

**Usage:**
```bash
/validate-portfolio [action]
```

**Examples:**
- `/validate-portfolio` - Run all validation checks
- `/validate-portfolio add` - Test adding positions
- `/validate-portfolio search` - Test RAG search
- `/validate-portfolio rag` - Test RAG embedding

**What it does:**
- Validate portfolio JSON structure
- Test add/remove position operations
- Test RAG semantic search (if available)
- Check portfolio calculations (gains, diversification)
- Generate sample analysis

---

### /check-security
**Description:** Scan for security issues and exposed credentials

**Usage:**
```bash
/check-security
```

**What it does:**
- Scan for hardcoded API keys
- Check for SQL injection vulnerabilities
- Verify .env is in .gitignore
- Scan for exposed secrets in git history
- Report security recommendations

---

### /generate-docs
**Description:** Update documentation from code

**Usage:**
```bash
/generate-docs [section]
```

**Examples:**
- `/generate-docs` - Update all documentation
- `/generate-docs tools` - Generate tool reference
- `/generate-docs config` - Document configuration options
- `/generate-docs architecture` - Update architecture docs

**What it does:**
- Extract tool definitions and generate reference
- Document all configuration options
- Create usage examples
- Generate API documentation
- Keep README in sync

---

### /run-agent
**Description:** Quick launcher for the Stock Agent CLI

**Usage:**
```bash
/run-agent [--fresh] [--debug]
```

**Examples:**
- `/run-agent` - Start agent normally
- `/run-agent --fresh` - Reset portfolio first
- `/run-agent --debug` - Start with debug logging

**What it does:**
- Activate virtual environment
- Validate configuration
- Launch the agent CLI
- Pass through command arguments

---

### /commit-changes
**Description:** Stage changes and create a descriptive commit

**Usage:**
```bash
/commit-changes [type] [message]
```

**Examples:**
- `/commit-changes fix "resolve API timeout issue"`
- `/commit-changes feature "add alert system"`
- `/commit-changes docs "update README"`

**Types:** `feature`, `fix`, `docs`, `refactor`, `test`, `chore`

**What it does:**
- Automatically stage relevant files
- Format commit message
- Run pre-commit checks
- Create standardized commits
- Add co-author signature

---

### /debug-rag
**Description:** Troubleshoot RAG/ChromaDB issues

**Usage:**
```bash
/debug-rag
```

**What it does:**
- Check ChromaDB availability
- Verify Python version compatibility
- Test embeddings
- Check collection status
- Suggest fixes for common issues
- Show fallback status

---

## Command Structure (for reference)

A skill command in skill.md follows this structure:

```markdown
### /command-name
**Description:** Brief explanation

**Usage:**
```bash
/command-name [args]
```

**Examples:**
- Example 1
- Example 2

**What it does:**
- Action 1
- Action 2
- Action 3
```

## Skill Categories

| Category | Commands |
|----------|----------|
| **Testing** | /test-agent, /test-tools, /validate-portfolio |
| **Configuration** | /validate-config, /check-security |
| **Development** | /lint-agent, /generate-docs, /commit-changes |
| **Debugging** | /debug-rag |
| **Execution** | /run-agent |

## Common Workflows

**Before committing:**
1. `/validate-config` - Ensure setup is correct
2. `/lint-agent` - Check code quality
3. `/test-agent` - Validate agent works
4. `/commit-changes feature "description"` - Commit with proper message

**Debugging issues:**
1. `/validate-config` - Check configuration
2. `/debug-rag` - If RAG isn't working
3. `/test-tools` - If specific tools are failing
4. `/test-agent` - Overall agent test

**After adding features:**
1. `/test-tools` - Test new tool
2. `/validate-portfolio` - Full validation
3. `/generate-docs` - Update documentation
4. `/commit-changes feature "new feature description"` - Commit changes

## Notes

- All commands are designed to be run from the project root directory
- Commands validate prerequisites before execution
- Failed commands provide helpful error messages and suggestions
- Use `--help` flag on any command for detailed usage
- Commands are safe and non-destructive (except commits)
