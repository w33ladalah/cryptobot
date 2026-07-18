---
description: Decide if a fix or change is worth saving as workflow, skill, rule, or memory
---

# Should I Save This Knowledge?

Use this when you've fixed a bug, made a change, or learned something and want to decide if it's worth preserving for future use.

## Decision Flow

### 1. Will you need to do this EXACT same thing again?

**Yes, repeatedly with similar steps** → Save as `/save-as-workflow`
- Examples: Adding a feature, running migrations, deploying
- Indicators: Multiple discrete steps, happens monthly+

**Yes, but with variations** → Save as `/save-as-skill`
- Examples: Creating CRUD services, adding API endpoints, building pages
- Indicators: Same pattern, different inputs

**No / Not sure** → Continue to Question 2

### 2. Does this define HOW things should ALWAYS be done?

**Yes, it's a universal project rule** → Save as `/save-as-rule`
- Examples: Import ordering, naming conventions, Docker commands
- Indicators: Applies to all future code, triggered by file patterns

**No, it's context-specific** → Continue to Question 3

### 3. Is this a PROJECT-SPECIFIC fact that future you should know?

**Yes, it's unique to this project** → Save as `/save-as-memory`
- Examples: API quirks, domain logic, third-party limitations
- Indicators: Would confuse someone new, explains "why" not "how"

**No, it's generic knowledge** → Don't save (or document inline)

## Quick Reference

| Format | When to Use | Trigger | Example |
|--------|-------------|---------|---------|
| **Workflow** | Multi-step process, executed repeatedly | `/command` | Database migration |
| **Skill** | Code generation pattern | Auto-invoked | Create CRUD |
| **Rule** | Always-on convention | File pattern | Import order |
| **Memory** | Project context/facts | Retrieved by AI | API limitation |

## Checklist

- [ ] Determined the knowledge type using the decision flow
- [ ] Saved using the appropriate `/save-as-*` workflow
- [ ] Verified the saved knowledge is retrievable
