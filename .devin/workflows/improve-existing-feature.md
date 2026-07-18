---
description: Workflow for improving or enhancing an existing feature
---

# Improve Existing Feature

Use this when enhancing, refactoring, or optimizing an existing feature (backend, frontend, or admin).

## Steps

### Phase 1 — Analysis

1. **Understand current implementation:**
   - Read the existing code for the feature
   - Identify the files involved (backend models, routers, frontend components, etc.)
   - Check existing documentation in `docs/` if any

2. **Identify improvement areas:**
   - Performance bottlenecks
   - Code quality issues (duplication, complexity)
   - User experience problems
   - Missing features or capabilities
   - Security concerns
   - Accessibility improvements

3. **Plan the changes:**
   - Define what needs to be changed and why
   - Determine the scope (backend only, frontend only, or full-stack)
   - Consider impact on existing functionality
   - Plan testing approach

### Phase 2 — Implementation

1. **Backend changes (if applicable):**
   - Update models in `backend/app/models/` if schema changes needed
   - Generate and apply Alembic migration if model changed (see `/database-migration`)
   - Update schemas in `backend/app/schemas/`
   - Update CRUD operations in `backend/app/crud/`
   - Update routers in `backend/app/routers/`
   - Update Celery tasks if relevant

2. **Frontend changes (if applicable):**
   - Update API endpoints in `frontend/src/constants/apiEndpoints.ts`
   - Update TypeScript types in `frontend/src/types/`
   - Update Redux slices/thunks in `frontend/src/store/`
   - Update components in `frontend/src/components/`
   - Update pages in `frontend/src/app/`

3. **Admin changes (if applicable):**
   - Update admin services in `admin/src/services/`
   - Update admin pages in `admin/src/app/`

### Phase 3 — Testing

1. **Test the changes:**
   - Manual testing of the improved feature
   - Check that existing functionality still works (regression testing)
   - Test edge cases and error scenarios
   - Verify performance improvements if applicable

2. **Verify in browser:**
   - Test frontend changes in the browser
   - Check console for errors
   - Verify UI/UX improvements

### Phase 4 — Documentation

1. **Update documentation:**
   - If the improvement is significant, update existing docs in `docs/`
   - Update API reference if endpoints changed
   - Update feature documentation if behavior changed
   - Run `/update-docs` workflow if major changes

### Phase 5 — Commit

1. **Commit changes:**
    - Use descriptive commit message: `feat(backend): improve <feature>` or `refactor(frontend): optimize <component>`
    - Group related changes in a single commit
    - Reference related issues if applicable

## Checklist

- [ ] Current implementation understood
- [ ] Improvement areas identified
- [ ] Changes planned and scoped
- [ ] Backend changes implemented (if applicable)
- [ ] Database migration applied (if model changed)
- [ ] Frontend changes implemented (if applicable)
- [ ] Admin changes implemented (if applicable)
- [ ] Changes tested manually
- [ ] Regression testing completed
- [ ] Documentation updated (if significant)
- [ ] Changes committed with descriptive message

## Important Notes

- **Stability:** This is a production codebase — prefer minimal, focused changes over broad refactoring
- **Testing:** Always test improvements thoroughly to avoid breaking existing functionality
- **Documentation:** Update docs for significant changes that affect user-facing behavior
- **Backend:** Never restart the backend container — uvicorn `--reload` picks up changes
- **Docker:** Always run backend commands inside Docker: `docker compose exec backend <command>`
