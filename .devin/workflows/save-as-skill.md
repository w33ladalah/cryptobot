---
description: Save a reusable code generation pattern as a skill
---

# Save as Skill

Use this when you have a repeatable code pattern that generates similar structures.

## When to Use Skills

- **Code follows a predictable pattern**
- **Variations are input-driven**
- **Can be auto-invoked by a command**
- **Generates boilerplate efficiently**

## Good Skill Candidates

- Generating CRUD services
- Creating API endpoint scaffolding
- Building React components with standard structure
- Adding Redux slices
- Creating database models

## Bad Skill Candidates

- One-time fixes
- Processes with many decision branches
- Pure documentation
- Project-specific quirks (use memories)

## File Format

Create in `.windsurf/skills/<name>.md`:

```markdown
Generate a <thing> given <inputs>.

## Inputs

- Input1: description
- Input2: description

## Output Structure

Describe the expected output format.

## Template/Example

Show an example of what good output looks like.

## Rules

1. Rule about how to generate
2. Another rule
```

## Example: Add CRUD Service

```markdown
Generate a CRUD service for a given entity.

## Inputs

- Entity name (e.g., "Product")
- Fields with types (e.g., "name: str, price: int")

## Output Structure

FastAPI router with:
- POST /{entity}s - create
- GET /{entity}s - list
- GET /{entity}s/{id} - get
- PUT /{entity}s/{id} - update
- DELETE /{entity}s/{id} - delete

## Rules

1. Use SQLAlchemy 2.0 async patterns
2. Include proper Pydantic schemas
3. Add docstrings to all endpoints
```

## Registration

Skills are auto-discovered from `.windsurf/skills/`. No registration needed.

## Checklist

- [ ] Pattern is truly repeatable
- [ ] Inputs and outputs are well-defined
- [ ] Saved to `.windsurf/skills/<name>.md`
- [ ] Includes clear examples
- [ ] Tested with different inputs
