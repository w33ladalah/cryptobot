---
description: Save project-specific context and facts as a memory
---

# Save as Memory

Use this when you have project-specific knowledge that explains "why" things are the way they are.

## When to Use Memories

- **Explains project quirks or limitations**
- **Documents API-specific behavior**
- **Captures domain knowledge**
- **Records decisions and their rationale**
- **Future developers (including you) would be confused without it**

## Good Memory Candidates

- API rate limits or quirks
- Database schema decisions
- Third-party integration limitations
- Business logic explanations
- Why certain libraries were chosen
- Gotchas that cost you debugging time

## Bad Memory Candidates

- Generic programming knowledge
- Steps to do something (use workflows)
- Code patterns (use skills)
- Style conventions (use rules)

## File Format

Create/update via the `create_memory` tool with:

```python
{
    "Title": "Clear, searchable title",
    "Content": "The knowledge content",
    "Tags": ["relevant", "tags"],
    "CorpusNames": ["technical-garislurus/garis-generator"],
    "UserTriggered": true,
    "Action": "create"
}
```

Or save to `docs/<topic>.md` and summarize as memory.

## Memory Categories

| Category | Examples |
|----------|----------|
| **API Behavior** | Rate limits, error patterns, response quirks |
| **Database** | Schema decisions, migration history, query optimization |
| **Integrations** | Third-party quirks, auth flows, webhook behavior |
| **Domain Logic** | Business rules, calculation methods, edge cases |
| **Debugging History** | Bugs that took time, root causes, solutions |

## How Memories Are Retrieved

- Automatically by semantic similarity to user queries
- Via `@memory_name` mentions
- Through `trajectory_search` for related conversations

## Checklist

- [ ] Knowledge is project-specific
- [ ] Would save future debugging time
- [ ] Explains "why" not just "what"
- [ ] Saved via `create_memory` tool or documented
- [ ] Has relevant tags for retrieval
