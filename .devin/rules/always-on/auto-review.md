---
trigger: always_on
description: Automatically run code review workflow after making code changes
---

# Automatic Code Review

After making code changes, always run the `/review` workflow to identify potential bugs and code improvements.

## When to Trigger

Run the review workflow after:

- Completing any code changes (bug fixes, new features, refactoring)
- Making edits to `apps/api`, `apps/worker`, or `apps/webapp` code
- Modifying database models or schemas
- Adding or updating API endpoints or Celery tasks
- Changing trade-execution logic in `apps/worker/core/trading/`

## How to Use

After completing your code changes, invoke the review workflow by using the `/review` slash command or workflow.

The review workflow will:

1. Analyze the code changes for logic errors
2. Check for edge cases and null/undefined issues
3. Identify security vulnerabilities
4. Verify proper resource management
5. Ensure API contract compliance
6. Check caching behavior
7. Validate adherence to code patterns and conventions
