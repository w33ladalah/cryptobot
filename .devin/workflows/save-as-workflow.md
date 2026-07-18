---
description: Save a repeatable multi-step process as a workflow
---

# Save as Workflow

Use this when you have a multi-step process that you'll repeat with minimal variation.

## When to Use Workflows

- **Process has 3+ steps** that must happen in order
- **You do this monthly or more**
- **Steps are discrete and deterministic**
- **Benefits from a checklist**

## Good Workflow Candidates

- Adding a new full-stack feature
- Running database migrations
- Creating a new API endpoint
- Deploying to production
- Setting up new integrations

## Bad Workflow Candidates

- One-off bug fixes
- Generic coding patterns (use skills)
- Simple 1-2 step tasks
- Purely informational context (use memories)

## File Format

Create in `.windsurf/workflows/<name>.md`:

```yaml
---
description: Clear, searchable description
---

# Workflow Title

Brief explanation of when to use this.

## Steps

1. **Step name:** Action description
2. **Step name:** Action description

## Checklist

- [ ] Step 1 done
- [ ] Step 2 done
```

## Naming Convention

- Use action verbs: `add-`, `fix-`, `deploy-`, `migrate-`
- Use kebab-case: `add-new-feature`, `fix-backend-bug`
- Keep it short but clear

## Checklist

- [ ] Process has clear, repeatable steps
- [ ] Saved to `.windsurf/workflows/<name>.md`
- [ ] Includes frontmatter with description
- [ ] Has actionable steps with checkboxes
- [ ] Tested by actually running through it once
