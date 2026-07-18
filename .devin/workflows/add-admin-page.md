---
description: How to add a new admin CRUD page
---

# Add Admin Page Workflow

## Steps

### 1. Create the API service

Create `admin/src/services/<entity>.ts`:

```typescript
export interface Entity {
  id: string;
  name: string;
  // ... fields matching the backend schema
  created_at: string;
  updated_at: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function fetchEntities(token: string): Promise<Entity[]> {
  const res = await fetch(`${API_URL}/api/admin/<entities>`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to fetch");
  return res.json();
}

export async function createEntity(token: string, data: Partial<Entity>): Promise<Entity> {
  const res = await fetch(`${API_URL}/api/admin/<entities>`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create");
  return res.json();
}

// Add update, delete functions following the same pattern
```

### 2. Create the page

Create `admin/src/app/<entity>/page.tsx`:

- Use `"use client"` directive.
- Fetch data using the service functions.
- Use TailwindCSS for styling.
- Use Lucide icons for action buttons.
- Follow existing admin page patterns (table layout with actions).

### 3. Create sub-pages (if needed)

- `admin/src/app/<entity>/[id]/page.tsx` — Detail/edit page.
- `admin/src/app/<entity>/create/page.tsx` — Create form page.

### 4. Add navigation

Update the admin sidebar/navigation component to include a link to the new page.

### 5. Ensure backend admin routes exist

The admin page needs corresponding backend routes:

- `GET /api/admin/<entities>` — List all
- `POST /api/admin/<entities>` — Create
- `PUT /api/admin/<entities>/{id}` — Update
- `DELETE /api/admin/<entities>/{id}` — Delete

These should be in `backend/app/routers/admin_<entity>.py` and registered in `backend/app/api/__init__.py`. If the endpoints doesn't exists yet, created it.

## Key Differences from Frontend

- Admin uses plain `fetch()` with token, not the shared Axios instance.
- Admin uses Lucide React for icons, not Phosphor/MUI icons.
- Admin uses server-side `Metadata` exports in layouts (not `"use client"` layouts).
- Admin has no redux-persist.
