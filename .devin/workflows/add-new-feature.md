---
description: End-to-end workflow for adding a new full-stack feature
---

# Add New Feature (Full-Stack Workflow)

Use this when adding a feature that touches backend + frontend (and optionally admin).

## Steps

### Phase 1 — Backend

1. **Model:** Create/update SQLAlchemy model in `backend/app/models/`.
   - Register in `backend/app/models/__init__.py`.

2. **Migration:** Generate and apply Alembic migration (see `/database-migration` workflow).

3. **Schema:** Create Pydantic schemas in `backend/app/schemas/`.

4. **CRUD:** Create CRUD class in `backend/app/crud/`.

5. **Router:** Create router in `backend/app/routers/` (see `/add-api-endpoint` workflow).

6. **Register router** in `backend/app/api/__init__.py` (protected) or `backend/main.py` (public).

7. **Celery task (if needed):** Add task in `backend/app/tasks/`, register in `celery_app.py` include list.

### Phase 2 — Frontend

8. **API endpoint:** Add to `frontend/src/constants/apiEndpoints.ts`.

9. **Types:** Add TypeScript types in `frontend/src/types/` if needed.

10. **Redux slice + thunk:** Create slice in `store/slices/` and thunk in `store/thunks/` (see `/add-redux-slice` workflow).

11. **Register reducer** in `frontend/src/store/store.ts`.

12. **Components:** Create UI components in `frontend/src/components/`.

13. **Page:** Create the page in `frontend/src/app/<feature>/page.tsx`.

### Phase 3 — Admin (if applicable)

14. **Admin service:** Create in `admin/src/services/`.

15. **Admin page:** Create in `admin/src/app/<feature>/page.tsx` (see `/add-admin-page` workflow).

### Phase 4 — Documentation

16. Run `/update-docs` workflow:
    - Create `docs/<FEATURE_NAME>.md`
    - Update `docs/README.md`
    - Update `docs/API_REFERENCE.md` with new endpoints
    - Update `docs/FEATURES.md` with the new capability

## Checklist

- [ ] Backend model + migration applied
- [ ] Backend schemas, CRUD, router created and registered
- [ ] Frontend API endpoints added
- [ ] Frontend Redux slice + thunk created and registered in store
- [ ] Frontend page and components created
- [ ] Admin service and page created (if needed)
- [ ] Tested end-to-end (API → Frontend UI)
- [ ] `docs/<FEATURE_NAME>.md` created
- [ ] `docs/README.md`, `docs/API_REFERENCE.md`, `docs/FEATURES.md` updated
