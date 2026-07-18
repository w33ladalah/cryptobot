---
trigger: model_decision
description: Reference implementation for an admin CRUD service and list page
---

# Example: Admin CRUD Service + Page

## Service (`admin/src/services/myEntity.ts`)

```typescript
export interface MyEntity {
  id: string;
  name: string;
  created_at: string;
}

const BASE = process.env.NEXT_PUBLIC_API_URL;

export async function fetchMyEntities(token: string): Promise<MyEntity[]> {
  const res = await fetch(`${BASE}/api/admin/my-entities`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to fetch");
  return res.json();
}

export async function createMyEntity(
  token: string,
  data: Partial<MyEntity>
): Promise<MyEntity> {
  const res = await fetch(`${BASE}/api/admin/my-entities`, {
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

export async function deleteMyEntity(token: string, id: string): Promise<void> {
  const res = await fetch(`${BASE}/api/admin/my-entities/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to delete");
}
```

## List Page (`admin/src/app/my-entities/page.tsx`)

```typescript
"use client";
import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { RootState } from "@/store/store";
import { fetchMyEntities, deleteMyEntity, MyEntity } from "@/services/myEntity";
import { Pencil, Trash2 } from "lucide-react";
import Link from "next/link";

export default function MyEntitiesPage() {
  const token = useSelector((state: RootState) => state.auth.accessToken);
  const [items, setItems] = useState<MyEntity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    fetchMyEntities(token)
      .then(setItems)
      .finally(() => setLoading(false));
  }, [token]);

  const handleDelete = async (id: string) => {
    if (!token || !confirm("Delete?")) return;
    await deleteMyEntity(token, id);
    setItems(items.filter((i) => i.id !== id));
  };

  if (loading) return <div className="p-6">Loading...</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between mb-4">
        <h1 className="text-2xl font-bold">My Entities</h1>
        <Link href="/my-entities/new" className="bg-blue-600 text-white px-4 py-2 rounded">
          Create New
        </Link>
      </div>
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-gray-100">
            <th className="p-2 text-left">Name</th>
            <th className="p-2 text-left">Created</th>
            <th className="p-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id} className="border-b">
              <td className="p-2">{item.name}</td>
              <td className="p-2">{item.created_at}</td>
              <td className="p-2 flex gap-2 justify-center">
                <Link href={`/my-entities/${item.id}`}>
                  <Pencil size={16} className="text-blue-600" />
                </Link>
                <button onClick={() => handleDelete(item.id)}>
                  <Trash2 size={16} className="text-red-500" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

## Notes

- Always `"use client"` on admin pages
- Use Lucide icons (`Pencil`, `Trash2`) — not Phosphor/MUI icons
- No Axios — always native `fetch()`
- Add sidebar link to new entity in `components/Sidebar.tsx`
