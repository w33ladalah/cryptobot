---
description: Git commit all changes with a descriptive message
---

# Git Commit All Changes

This workflow commits all changes in the repository with a descriptive commit message.

## When to Use

- After completing a feature or bug fix
- When you want to save your work before switching branches
- Before pushing to remote repository

## Steps

1. **Check git status**

   ```bash
   git status
   ```

   This shows all modified, added, and untracked files.

2. **Stage all changes**

   ```bash
   git add -A
   ```

   This stages all changes including new, modified, and deleted files.

3. **Commit with descriptive message**

   ```bash
   git commit -m "Your commit message here"
   ```

   Best practices for commit messages:
   - Start with a type prefix (feat:, fix:, docs:, refactor:, etc.)
   - Keep the first line under 50 characters
   - Add a blank line and detailed description if needed
   - Use imperative mood ("Add feature" not "Added feature")

## Examples

### Feature commit

```bash
git commit -m "feat: Add user authentication system

- Implement login and signup endpoints
- Add JWT token handling
- Create user profile page
- Update API documentation"
```

### Bug fix commit

```bash
git commit -m "fix: Resolve memory leak in image processing

- Fix unclosed file handles in ImageProcessor
- Add proper cleanup in finally block
- Update tests to verify memory usage"
```

### Quick commit

```bash
git commit -m "docs: Update README with installation instructions"
```

## After Commiting

- To push to remote: `git push`
- To check commit history: `git log --oneline -10`
- To undo last commit: `git reset --soft HEAD~1`

## Notes

- Always review staged changes with `git diff --cached` before committing
- Use conventional commit types:
  - `feat:` New feature
  - `fix:` Bug fix
  - `docs:` Documentation changes
  - `refactor:` Code refactoring
  - `test:` Adding or updating tests
  - `chore:` Maintenance tasks
- If you need to commit specific files only: `git add path/to/file1 path/to/file2`
