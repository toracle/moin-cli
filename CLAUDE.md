# MoinMoin CLI Project Guidelines

## Task Documentation Strategy

**Important**: For this project, do NOT create task-specific documentation files in the local repository. Instead, use GitHub's collaborative features for task tracking and documentation.

### Task Documentation Location Priority

1. **GitHub Issues** - Primary location for task planning and tracking
   - Create issues for features, bugs, and tasks
   - Use issue templates for consistency
   - Tag with appropriate labels (feature, bug, documentation, etc.)
   - Reference related issues and PRs

2. **GitHub Issue Comments** - Task progress and discussion
   - Update progress in issue comments
   - Document decisions and rationale
   - Share code snippets and examples
   - Collaborate with other contributors

3. **Pull Request Descriptions** - Implementation documentation
   - Detailed description of changes
   - Link to related issues
   - Implementation approach explanation
   - Testing notes

4. **Pull Request Comments** - Code review and refinement
   - Code-specific discussions
   - Implementation feedback
   - Suggestions and improvements

### What NOT to create locally:

- ❌ `docs/tasks/` directories
- ❌ Task-specific markdown files
- ❌ Branch-specific documentation folders
- ❌ `PROGRESS.md` or `PLAN.md` files for specific tasks
- ❌ Temporary documentation that duplicates GitHub discussions

### What TO create locally:

- ✅ **Architectural documentation** (already in `docs/developer/`)
- ✅ **User guides** (already in `docs/user-guide/`)
- ✅ **API documentation** and protocol specs
- ✅ **Contributing guidelines** and development setup
- ✅ **Code comments** and docstrings

### Benefits of GitHub-Centric Approach:

1. **Centralized collaboration** - All team members see the same information
2. **Integrated workflow** - Issues → PRs → code changes in one place
3. **Searchable history** - GitHub's search finds discussions and decisions
4. **Notification system** - Automatic updates to relevant stakeholders
5. **Clean repository** - No task-specific clutter in the codebase
6. **Future reference** - Completed issues provide implementation history

### Implementation Workflow:

1. **Planning Phase**:
   - Create GitHub issue for the task
   - Document requirements and acceptance criteria
   - Break down into subtasks if needed
   - Assign labels and milestones

2. **Development Phase**:
   - Create feature branch
   - Update issue with progress comments
   - Reference issue in commit messages (`Closes #123`)

3. **Review Phase**:
   - Create PR with detailed description
   - Link to related issue(s)
   - Use PR comments for code-specific discussions

4. **Completion Phase**:
   - Merge PR (automatically closes linked issues)
   - GitHub maintains permanent record

### Example Workflow:

```
Issue #42: "Add multi-server authentication support"
├── Planning discussion in issue comments
├── Subtask breakdown in issue description
├── PR #45: "Implement server management commands"
│   ├── Implementation details in PR description
│   ├── Code review in PR comments
│   └── Closes issue #42
└── Historical record preserved in GitHub
```

This approach keeps the repository clean while leveraging GitHub's excellent project management and collaboration features.

## Other Project-Specific Guidelines

### Code Organization
- Follow the established `docs/` structure (user-guide/ and developer/)
- Keep technical documentation in version control
- Use clear, descriptive commit messages

### Documentation Maintenance
- Update user guides when CLI commands change
- Keep architecture docs current with code changes
- Use cross-references between documentation files

### Development Process
- Create branches for features: `feature/description-issue-N` (include issue number)
- Use descriptive commit messages with issue references (`#N`)
- Include tests for new functionality
- Update documentation with code changes
- **Use `uv run` for all Python commands** to ensure project-specific environment

## Python Environment Management with UV

**Important**: Always use `uv run` for Python commands to ensure project-specific dependency isolation and consistency.

### Core UV Commands
```bash
# ✅ GOOD: Project-aware Python execution
uv run python -c "import moin_cli; print('✅ Import works')"
uv run python -m pytest
uv run python -m mypy moin_cli/
uv run python script.py

# ❌ BAD: System/global Python (inconsistent dependencies)
python -c "import moin_cli"
python -m pytest
python script.py
```

### Benefits of UV Run
1. **Dependency Isolation** - Uses project's exact dependencies from pyproject.toml
2. **Consistency** - Same environment across team members and CI/CD
3. **Automatic Setup** - Creates/activates virtual environment automatically
4. **Version Management** - Ensures correct Python version per project

### Common Development Patterns
```bash
# Testing imports
uv run python -c "import moin_cli.config; print('Config package works')"

# Running tests
uv run pytest
uv run pytest tests/test_config.py -v

# Type checking
uv run mypy moin_cli/

# Code formatting
uv run black moin_cli/
uv run ruff check moin_cli/

# Running the CLI
uv run moin --help
uv run python -m moin_cli.main

# Installing development dependencies
uv sync --group dev
```

### Integration with Development Tools
- **AIDER**: Continue using `aider` directly (it manages its own environment)
- **Git hooks**: Use `uv run` in pre-commit hooks
- **CI/CD**: Use `uv run` in GitHub Actions workflows
- **IDE**: Configure IDE to use `uv run` for Python interpreter

This ensures all development happens in a consistent, isolated environment with the correct dependencies.

## Branch-Issue Linking for Session Continuity

**Problem**: In multi-session development, it's critical to maintain clear links between branches, GitHub issues, and implementation context.

### Branch Naming Convention
Always include the GitHub issue number in branch names:

```bash
# ✅ GOOD: Clear issue linking
feature/config-system-issue-1
bugfix/auth-token-issue-5  
refactor/xmlrpc-client-issue-12

# ❌ BAD: No issue context
feature/config-system
bugfix/auth-token
refactor/xmlrpc-client
```

### Linking Commit Strategy
Create an initial commit that references the GitHub issue:

```bash
git commit --allow-empty -m "Start implementation of [feature name]

Related to #N: [GitHub issue title]

This branch implements:
- [Key implementation points]
- [Reference to acceptance criteria]

See GitHub issue #N for detailed acceptance criteria and progress tracking."
```

### Session Discovery Commands
Future sessions can discover context using:

```bash
# Current work context
git branch --show-current      # Shows branch with issue number
git log --oneline -1          # Shows linking commit with issue reference
gh issue list --state open    # Shows active issues
gh issue view N              # Shows detailed issue content

# Find branch for specific issue
git branch -a | grep "issue-N"
```

### Benefits
1. **Session Continuity** - Any session can discover current work context
2. **Clear Traceability** - Direct path from branch → issue → requirements
3. **GitHub Integration** - Automatic issue linking in commits and PRs  
4. **Team Collaboration** - Other contributors can understand active work

### Implementation Workflow with Linking

1. **Planning Phase**:
   - Create GitHub issue with detailed acceptance criteria
   - Note the issue number (e.g., #1)

2. **Development Phase**:
   - Create branch: `feature/description-issue-N`
   - Create linking commit referencing the issue
   - Regular commits reference issue: `git commit -m "Add config models (#N)"`

3. **Session Handoff**:
   - Any future session can run discovery commands
   - Clear path from current branch to implementation requirements
   - GitHub issue serves as central coordination point

4. **Completion**:
   - PR automatically references and closes issue
   - Branch name provides permanent link to requirements