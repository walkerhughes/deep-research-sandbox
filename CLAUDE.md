# Claude Code Development Guidelines

## Git Worktree Workflow (Required)

This repository uses **git worktrees** for parallel development. When working on any issue, you MUST use a dedicated worktree rather than working directly in the main repository.

### Setup for New Issues

Before starting work on any issue, create a worktree:

```bash
# 1. Fetch latest changes
git fetch origin

# 2. Create worktree with a new branch for your issue
# Pattern: git worktree add ../deep-research-sandbox-issue-{NUMBER} -b {BRANCH_NAME}
# Branch naming: feat|fix|chore/short-description

# Examples:
git worktree add ../deep-research-sandbox-issue-1 -b feat/project-setup
git worktree add ../deep-research-sandbox-issue-6 -b feat/database-schema
git worktree add ../deep-research-sandbox-issue-14 -b feat/eval-judges

# 3. Enter your worktree
cd ../deep-research-sandbox-issue-{NUMBER}

# 4. Verify setup
pwd      # Should be: {REPO_PARENT_DIR}/deep-research-sandbox-issue-{NUMBER}
git branch  # Your branch should have * next to it
```

### Working in Your Worktree

**All work happens in your worktree directory.** Never work directly in the main repo.

```bash
# Your working directory (the worktree)
../deep-research-sandbox-issue-{NUMBER}

# NOT this (the main repo)
./deep-research-sandbox
```

#### Commit Conventions

- Commit frequently with clear messages
- Reference the issue number in commits
- Push regularly so other agents can see your work

```bash
# Commit message format
git commit -m "feat(#{ISSUE}): short description"
git commit -m "fix(#{ISSUE}): short description"
git commit -m "chore(#{ISSUE}): short description"

# Examples
git commit -m "feat(#1): add pyproject.toml with uv workspace config"
git commit -m "feat(#6): create initial database migrations"
git commit -m "fix(#14): correct judge prompt template"

# Push to remote
git push -u origin {BRANCH_NAME}
```

### Viewing Other Agents' Work

To see what other agents have committed (without leaving your worktree):

```bash
# Fetch all remote branches
git fetch origin

# List all remote branches
git branch -r

# View recent commits on another branch
git log origin/{OTHER_BRANCH} --oneline -10

# View a specific file from another branch
git show origin/{OTHER_BRANCH}:path/to/file.py

# Diff your branch against another
git diff origin/{OTHER_BRANCH} -- path/to/file
```

### Incorporating Other Agents' Changes

If you depend on work from another agent's branch:

```bash
# Option 1: Merge their branch (preserves history)
git fetch origin
git merge origin/{OTHER_BRANCH}

# Option 2: Rebase onto their branch (cleaner linear history)
git fetch origin
git rebase origin/{OTHER_BRANCH}

# Option 3: Cherry-pick specific commits
git fetch origin
git cherry-pick {COMMIT_HASH}
```

### Completing Your Work

When your issue is complete:

```bash
# 1. Ensure all changes are committed and pushed
git status  # Should be clean
git push origin {BRANCH_NAME}

# 2. Create a pull request
gh pr create --base main --head {BRANCH_NAME} --title "feat(#{ISSUE}): title" --body "Closes #{ISSUE}"

# 3. Do NOT delete the worktree - leave cleanup to the repo owner
```

### Rules

1. **Always use a worktree** - Never commit directly to main or work in the main repo directory
2. **Never checkout other branches** in your worktree - Use `git show` or `git fetch` to view other work
3. **Commit and push frequently** - Other agents may depend on your work
4. **Fetch before checking for updates** - Always `git fetch origin` before looking at other branches
5. **Use conventional commits** - `feat|fix|chore(#issue): description`

### Worktree Management Reference

```bash
# List all worktrees
git worktree list

# Remove a worktree (only repo owner should do this)
git worktree remove ../deep-research-sandbox-issue-{NUMBER}

# Prune stale worktree references
git worktree prune
```

---

## Project Structure

```
deep-research-sandbox/
├── apps/
│   ├── api/                 # FastAPI backend + Pydantic AI agents
│   └── web/                 # Next.js frontend
├── packages/
│   └── shared/              # Shared types (Python + TypeScript)
├── evals/                   # Evaluation suite
├── infra/                   # Infrastructure configs
└── pyproject.toml           # Root workspace config
```

## Testing

This repository follows **Test-Driven Development (TDD)**. Write tests before implementing features.

### Test Organization

```
tests/
├── conftest.py              # Shared fixtures and test configuration
├── unit/                    # Fast, isolated unit tests
│   ├── conftest.py          # Unit-specific fixtures (optional)
│   └── ...
└── integration/             # Tests that involve external systems/dependencies
    ├── conftest.py          # Integration-specific fixtures (optional)
    └── ...
```

### TDD Workflow

1. **Red** - Write a failing test for the new functionality
2. **Green** - Write the minimum code to make the test pass
3. **Refactor** - Clean up the code while keeping tests green

### Guidelines

- Place shared fixtures in the root `tests/conftest.py`
- Unit tests should be fast and have no external dependencies
- Integration tests may use databases, APIs, or other services
- Run tests frequently during development: `pytest tests/`
- Run only unit tests for quick feedback: `pytest tests/unit/`

---

## Issue Tracking

All work is tracked via GitHub Issues.

**Issue #16** is the meta/documentation issue that serves as the **roadmap for repository development**. Reference it to:
- See the full architecture overview
- Understand issue dependencies and recommended implementation order
- Plan parallel work across multiple agents
- Track overall project progress

Roadmap: https://github.com/walkerhughes/deep-research-sandbox/issues/16

Before starting any work:
1. Review issue #16 to understand where your issue fits in the roadmap
2. Check your specific issue for requirements and acceptance criteria
3. Note any blocking dependencies on other issues
4. Create your worktree and branch
5. Reference the issue number in all commits
