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
   - **Explicit issue linking** with "Related Issue: Closes #N" or "Fixes #N"
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
   - **Explicitly link to related issue** using "Closes #N", "Fixes #N", or "Related Issue: #N"
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

### GitHub Cross-Referencing & Progress Tracking

**Core Principle**: Separate problem space (issues) from solution space (PRs) while maintaining bidirectional linking for session continuity.

#### Problem Space vs Solution Space Separation

**GitHub Issues - Problem Space (WHAT & WHY)**
- 🎯 **Requirements & acceptance criteria** - What needs to be built
- 🎯 **Business objectives** - Why this matters to users
- 🎯 **Scope definition** - Boundaries and constraints
- 🎯 **High-level progress** - Checkbox completion state
- 🎯 **Requirement changes** - Scope evolution and clarifications

**Pull Requests - Solution Space (HOW)**
- 🔧 **Technical implementation** - How it's being built
- 🔧 **Architecture decisions** - Technology choices and rationale
- 🔧 **Detailed progress** - Session logs and implementation steps
- 🔧 **Code review** - Quality and approach discussions
- 🔧 **Technical blockers** - Implementation challenges

#### Hybrid Workflow (Pragmatic Approach)

**Before PR Exists:**
- Use issue comments for early development progress
- Document initial technical approach and blockers
- Track session work until first substantial commit

**After PR Created:**
- Move detailed implementation discussion to PR
- Keep issue focused on requirements and high-level progress  
- Cross-reference between issue and PR for context

**Cross-Referencing Strategy:**

**1. Issue Description (Body) - Problem Definition**

**What belongs in issue body:**
- ✅ **Acceptance criteria** with checkboxes `[ ]` / `[x]`
- ✅ **Task overview** and business objectives
- ✅ **Dependencies** and references
- ✅ **High-level completion state** via checkbox updates
- ✅ **Requirements** and scope definition

**2. Issue Comments - Early Development & Problem Space Evolution**

**What belongs in comments (before PR):**
- 🔄 **Early progress** and initial technical exploration
- 🔄 **Requirements clarification** and scope changes
- 🔄 **Major blockers** that affect requirements

**What belongs in comments (after PR):**
- 🔄 **Requirement updates** from implementation learnings
- 🔄 **Scope changes** discovered during development

**3. Pull Request Description & Comments - Solution Implementation**

**What belongs in PR:**
- 🔧 **Explicit issue linking** at the top of description ("Related Issue: Closes #N")
- 🔧 **Implementation approach** and technical decisions
- 🔧 **Detailed progress updates** and session logs
- 🔧 **Code-specific discussions** and technical blockers
- 🔧 **Architecture choices** and rationale

**4. Commit Message Linking** - Bidirectional references
- Reference issue numbers in commit messages: `Add config models (#1)`
- GitHub automatically creates links: commit → issue → commit
- Use conventional format: `<type>: <description> (#issue)`
- Include issue context in commit descriptions

#### Content Separation Examples

**✅ GOOD: Issue Body (Problem Space)**
```markdown
## Overview
Users need secure configuration management for multiple wiki servers.

## Acceptance Criteria  
- [ ] Support multiple server configurations
- [ ] Secure credential storage
- [ ] TOML configuration format

## Success Metrics
- Users can authenticate to multiple wikis seamlessly
- Credentials stored securely (encrypted)
```

**✅ GOOD: Issue Comment (Early Development)**
```markdown
## Initial Technical Investigation

Started exploring Pydantic vs dataclasses for config models.
Pydantic provides better validation for URL/timeout fields.

**Next**: Create basic models and test TOML serialization.
```

**✅ GOOD: PR Description (Solution Space)**
```markdown
## Summary
Implements the configuration management system as specified in **Issue #1**.

**Related Issue**: Closes #1

## Implementation Approach

- **Models**: Using Pydantic for validation and serialization
- **Storage**: Keyring integration for token encryption  
- **Architecture**: Separate models.py, manager.py, defaults.py

## Technical Decisions
- Pydantic v2 for modern validation syntax
- XDG directories for cross-platform config location

## Progress
- [x] ServerConfig model with validation
- [x] Basic TOML serialization  
- [ ] Keyring integration pending
```

**❌ BAD: Don't mix spaces**
- Technical implementation details in issue body
- Business requirements in PR descriptions
- Detailed session logs in issue comments

#### Session Continuity Commands

Future sessions can discover context using:

```bash
# Current work context
git branch --show-current      # Shows branch with issue number
git log --oneline -3          # Shows recent commits with issue refs
gh issue list --state open    # Shows active issues
gh issue view N              # Shows current progress and context

# Find work for specific issue
git branch -a | grep "issue-N"
gh issue view N --comments   # Full development history
```

#### Progress Tracking Workflow

1. **Start Session**:
   ```bash
   # Discover current context
   git branch --show-current && gh issue view $(git branch --show-current | grep -o 'issue-[0-9]*' | cut -d'-' -f2)
   ```

2. **During Development**:
   - Update issue description with progress checkmarks
   - Make commits with issue references
   - Add implementation comments to issue

3. **End Session**:
   ```bash
   # Commit with issue reference
   git commit -m "Implement config models (#1)
   
   - Add ServerConfig, Settings, Config Pydantic models
   - Include validation and default values
   - Matches user guide specification format
   
   Progress: 60% complete - models done, manager pending"
   ```

#### Benefits

- **Session Handoff** - Any session can discover current context quickly
- **Bidirectional Links** - GitHub creates automatic cross-references
- **Development History** - Issues contain complete implementation timeline
- **Progress Visibility** - Issue descriptions show current completion state
- **Context Preservation** - Commits link back to requirements and decisions

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
- **Follow spiral development** - implement minimal core first, then expand
- **Check existing documentation BEFORE implementing** - avoid reinventing specs

## Spiral Development Principle

**Core Philosophy**: Start with the essential minimum that creates a working end-to-end system, then incrementally add features through successive iterations.

### Why Spiral Development?
1. **Early Validation** - Get working system quickly to validate approach
2. **Risk Reduction** - Discover integration issues early with simple implementation
3. **User Feedback** - Working system enables early user testing and feedback
4. **Confidence Building** - Each iteration builds on proven foundation
5. **Scope Management** - Prevents over-engineering and feature creep

### Implementation Strategy

#### Phase 1: Minimal Viable Core
Implement the absolute minimum needed for basic functionality:
- **Goal**: Get primary use case working end-to-end
- **Focus**: Essential path only, hardcoded values acceptable
- **Quality**: Basic error handling, no edge cases
- **Documentation**: Simple usage examples

#### Phase 2: Essential Features  
Add the most critical missing pieces:
- **Goal**: Handle common use cases reliably
- **Focus**: Configuration, error handling, user experience
- **Quality**: Robust error messages, validation
- **Documentation**: Complete user guides

#### Phase 3: Enhanced Features
Polish and add advanced capabilities:
- **Goal**: Production-ready with advanced features
- **Focus**: Security, performance, edge cases
- **Quality**: Comprehensive testing, security features
- **Documentation**: Advanced usage, API docs

### Example: Configuration System

Instead of implementing full configuration system with encryption, keyring, XDG directories, etc.:

**❌ Big Bang Approach:**
```
Implement: ServerConfig + Settings + Config + Manager + Encryption + Keyring + XDG + TOML + Validation + Error handling
Result: Complex, slow, many integration points, hard to debug
```

**✅ Spiral Approach:**

**Iteration 1**: Hardcoded connection
```python
# Just get CLI connecting to wiki server
wiki_url = "http://localhost:8080"
username = "admin" 
# Focus: Does basic connection work?
```

**Iteration 2**: Simple config file
```python
# Add basic TOML config file support
config = {"url": "...", "username": "..."}
# Focus: Does file-based config work?
```

**Iteration 3**: Multiple servers + security
```python
# Add server management and secure storage
# Focus: Does multi-server management work?
```

### Benefits Applied to Current Task

For our configuration system, minimal core would be:
1. **Basic connection** - hardcoded URL, get one command working
2. **Simple config** - plain TOML file, no encryption
3. **Server management** - add/list servers
4. **Security layer** - encryption, keyring integration

This gets us a working CLI much faster, with each iteration adding real value.

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

## Documentation-First Development

**Critical Principle**: Always check existing documentation before implementing new features or formats.

### The Problem: Reinventing Specifications

**What happened**: During config system implementation, I created my own TOML format instead of checking the existing user guide specification:

```toml
# ❌ My invented format (WRONG)
[wikis.local]
url = "http://localhost:8080"
token = "abc123"

# ✅ Documented format (docs/user-guide/configuration.md)
[settings]
default_server = "local"

[server.local]
name = "local" 
url = "http://localhost:8080"
access_token = "abc123"
```

**Impact**: Implementation didn't match documented specification, requiring complete rework.

### Documentation Check Workflow

#### Simple Workflow:

1. **Quick search first**: `rg -i "your-feature" docs/`
2. **Read what you find** - Follow existing specs if they exist  
3. **Implement to match** - Don't reinvent documented formats

#### Documentation Sources to Check:

- **User guides** (`docs/user-guide/`) - User-facing specifications
- **Developer docs** (`docs/developer/`) - Technical implementation details  
- **Architecture docs** - System design and patterns
- **API specs** - Interface definitions and formats
- **README files** - Setup and usage instructions

### Simple Implementation Pattern

```bash
# ✅ GOOD: 30 seconds prevents hours of rework
rg -i "configuration" docs/  # Found user-guide/configuration.md!
# Read it, implement to match

# ❌ BAD: Excitement-driven development  
# Start coding immediately, discover conflicts later
```

### Benefits of Documentation-First

1. **Consistency** - Implementation matches user expectations
2. **Efficiency** - Avoid rework from specification conflicts
3. **Quality** - Follow established patterns and best practices
4. **Collaboration** - Other developers understand documented formats
5. **User Experience** - Behavior matches documentation

### When Documentation Doesn't Exist

If no documentation exists for what you're implementing:
1. **Create the specification first** - Document the format/API before coding
2. **Review with team** - Get feedback on the specification
3. **Implement to spec** - Build exactly what was documented
4. **Update docs** - Keep documentation current with implementation

This ensures documentation and implementation stay in sync from the start.

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