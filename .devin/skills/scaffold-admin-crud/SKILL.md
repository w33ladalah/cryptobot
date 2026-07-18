---
name: scaffold-admin-crud
description: Scaffold an admin CRUD service and page for managing a backend entity
---

# Scaffold Admin CRUD Service + Page

Given an **entity name** and its **API response fields**, create the admin panel files:

## What to generate

### 1. Service — `admin/src/services/<entity>.ts`

- Define the TypeScript `interface` matching the backend `<Entity>Response` schema.
- Export async functions using `fetch()`:
  - `fetch<Entities>(token: string)` → `GET /api/admin/<entities>`
  - `fetch<Entity>(token: string, id: string)` → `GET /api/admin/<entities>/{id}`
  - `create<Entity>(token: string, data: Partial<Entity>)` → `POST /api/admin/<entities>`
  - `update<Entity>(token: string, id: string, data: Partial<Entity>)` → `PUT /api/admin/<entities>/{id}`
  - `delete<Entity>(token: string, id: string)` → `DELETE /api/admin/<entities>/{id}`
- Use `process.env.NEXT_PUBLIC_API_URL` as base URL.
- Always include `Authorization: Bearer ${token}` header.

### 2. List Page — `admin/src/app/<entity>/page.tsx`

- `"use client"` directive.
- Table layout showing all entities with columns for key fields.
- Action buttons: Edit, Delete (using Lucide icons: `Pencil`, `Trash2`).
- "Create New" button at top.
- Loading and error states.
- Style with TailwindCSS.

### 3. Create/Edit Page — `admin/src/app/<entity>/[id]/page.tsx`

- Form with fields matching the entity schema.
- Handles both create (new) and edit (existing) modes.
- Submit calls the appropriate service function.
- Redirect to list page on success.

### 4. Navigation

- Remind user to add a sidebar link to the new page.

## Style Guidelines

- Use **Lucide React** for icons (not MUI, not Phosphor).
- Use **TailwindCSS** classes for all styling.
- Match the look and feel of existing admin pages.
