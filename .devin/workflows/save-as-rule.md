---
description: Save an always-on convention or constraint as a rule
---

# Save as Rule

Use this when you have a convention, constraint, or requirement that should ALWAYS be followed.

## When to Use Rules

- **Applies to all code in certain files**
- **Should be enforced automatically**
- **Non-compliance causes bugs/issues**
- **Triggered by file patterns**

## Good Rule Candidates

- Import ordering conventions
- Naming conventions for specific file types
- Docker command patterns (always use exec, not restart)
- Code style requirements for specific frameworks
- Security constraints

## Bad Rule Candidates

- One-time fixes
- Situational advice
- Project history (use memories)
- Multi-step processes (use workflows)

## File Format

Create in `.windsurf/rules/<name>.md`:

```markdown
---
trigger: <glob_pattern or "always">
---

# Rule Title

Clear statement of the rule.

## Details

Explain the "why" behind this rule.

## Examples

**Good:**

```python
code example
```

**Bad:**

```python
code example
```

## Enforcement

When this rule applies, you must:

1. Check requirement 1
2. Check requirement 2
```

## Trigger Patterns

- `always` - Applied to every request
- `apps/api/**,apps/worker/**` - Applied to API/worker files
- `apps/webapp/**` - Applied to webapp files
- `*.py` - Applied to all Python files

## Examples of Existing Rules

| Rule | Trigger | Purpose |
|------|---------|---------|
| `rules/backend/conventions.md` | `apps/api/**,apps/worker/**` | FastAPI/Celery patterns |
| `rules/infra/docker-commands.md` | `apps/api/**,apps/worker/**,docker/**` | Docker command convention |
| `rules/frontend/conventions.md` | `apps/webapp/**` | React/Vite patterns |

## Checklist

- [ ] Rule is truly universal for the target files
- [ ] Saved to `.windsurf/rules/<name>.md`
- [ ] Has appropriate trigger pattern
- [ ] Includes good/bad examples
- [ ] Explains the "why" behind it
