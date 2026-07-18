---
description: How to add a new frontend page or feature
---

# Add Frontend Page Workflow

Use this when adding a new page or feature to the frontend (Next.js) that doesn't require backend changes.

## Steps

### 1. Define API Endpoints

Add endpoints to `frontend/src/constants/apiEndpoints.ts`:

```typescript
export const API_ENDPOINTS = {
  // ... existing endpoints
  NEW_FEATURE: {
    LIST: '/new-feature',
    CREATE: '/new-feature',
    UPDATE: '/new-feature/:id',
    DELETE: '/new-feature/:id',
  },
};
```

### 2. Add TypeScript Types

Create types in `frontend/src/types/` if needed:

```typescript
// newFeature.ts
export interface NewFeature {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateNewFeatureRequest {
  name: string;
  description?: string;
}
```

### 3. Create Redux Slice and Thunk

#### Slice (`frontend/src/store/slices/newFeatureSlice.ts`):

```typescript
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { NewFeature } from '@/types/newFeature';

interface NewFeatureState {
  items: NewFeature[];
  loading: boolean;
  error: string | null;
  selectedItem: NewFeature | null;
}

const initialState: NewFeatureState = {
  items: [],
  loading: false,
  error: null,
  selectedItem: null,
};

const newFeatureSlice = createSlice({
  name: 'newFeature',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    setItems: (state, action: PayloadAction<NewFeature[]>) => {
      state.items = action.payload;
    },
    addItem: (state, action: PayloadAction<NewFeature>) => {
      state.items.push(action.payload);
    },
    updateItem: (state, action: PayloadAction<NewFeature>) => {
      const index = state.items.findIndex(item => item.id === action.payload.id);
      if (index !== -1) {
        state.items[index] = action.payload;
      }
    },
    removeItem: (state, action: PayloadAction<string>) => {
      state.items = state.items.filter(item => item.id !== action.payload);
    },
    setSelectedItem: (state, action: PayloadAction<NewFeature | null>) => {
      state.selectedItem = action.payload;
    },
    resetState: () => initialState,
  },
});

export const {
  setLoading,
  setError,
  setItems,
  addItem,
  updateItem,
  removeItem,
  setSelectedItem,
  resetState,
} = newFeatureSlice.actions;

export default newFeatureSlice.reducer;
```

#### Thunk (`frontend/src/store/thunks/newFeatureThunks.ts`)

```typescript
import { createAsyncThunk } from '@reduxjs/toolkit';
import { AppThunkConfig } from '@/store/store';
import api from '@/utils/api';
import { API_ENDPOINTS } from '@/constants/apiEndpoints';
import { NewFeature, CreateNewFeatureRequest } from '@/types/newFeature';
import {
  setLoading,
  setError,
  setItems,
  addItem,
  updateItem,
  removeItem,
} from '@/store/slices/newFeatureSlice';

export const fetchNewFeatures = createAsyncThunk<
  NewFeature[],
  void,
  AppThunkConfig
>('newFeature/fetchAll', async (_, { dispatch, rejectWithValue }) => {
  try {
    dispatch(setLoading(true));
    const response = await api.get(API_ENDPOINTS.NEW_FEATURE.LIST);
    dispatch(setItems(response.data));
    return response.data;
  } catch (error: any) {
    dispatch(setError(error.message));
    return rejectWithValue(error.message);
  } finally {
    dispatch(setLoading(false));
  }
});

export const createNewFeature = createAsyncThunk<
  NewFeature,
  CreateNewFeatureRequest,
  AppThunkConfig
>('newFeature/create', async (data, { dispatch, rejectWithValue }) => {
  try {
    dispatch(setLoading(true));
    const response = await api.post(API_ENDPOINTS.NEW_FEATURE.CREATE, data);
    dispatch(addItem(response.data));
    return response.data;
  } catch (error: any) {
    dispatch(setError(error.message));
    return rejectWithValue(error.message);
  } finally {
    dispatch(setLoading(false));
  }
});

// Add update and delete thunks following the same pattern
```

### 4. Register Reducer

Add the reducer to `frontend/src/store/store.ts`:

```typescript
import newFeatureReducer from './slices/newFeatureSlice';

const persistConfig = {
  key: 'root',
  storage,
  whitelist: ['generator', 'auth', 'ui'], // Don't persist newFeature unless needed
  // ...
};

const rootReducer = combineReducers({
  // ... existing reducers
  newFeature: newFeatureReducer,
});
```

### 5. Create Components

Create UI components in `frontend/src/components/newFeature/`:

```typescript
// NewFeatureList.tsx
import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { fetchNewFeatures } from '@/store/thunks/newFeatureThunks';

export const NewFeatureList: React.FC = () => {
  const dispatch = useAppDispatch();
  const { items, loading, error } = useAppSelector(state => state.newFeature);

  useEffect(() => {
    dispatch(fetchNewFeatures());
  }, [dispatch]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="space-y-4">
      {items.map(item => (
        <div key={item.id} className="p-4 border rounded">
          <h3>{item.name}</h3>
          <p>{item.description}</p>
        </div>
      ))}
    </div>
  );
};
```

### 6. Create the Page

Create `frontend/src/app/new-feature/page.tsx` (client component):

```typescript
'use client';

import React from 'react';
import { NewFeatureList } from '@/components/newFeature/NewFeatureList';

export default function NewFeaturePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">New Feature</h1>
      <NewFeatureList />
    </div>
  );
}
```

Or create a layout file for metadata:

`frontend/src/app/new-feature/layout.tsx`:

```typescript
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'New Feature - Aya AI',
  description: 'Manage new features',
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
```

### 7. Add Navigation

Update the navigation component to include a link to the new page:

```typescript
// In Header.tsx or navigation component
<Link href="/new-feature" className="nav-link">
  New Feature
</Link>
```

### 8. Add Sub-pages (if needed)

- `frontend/src/app/new-feature/[id]/page.tsx` — Detail/edit page
- `frontend/src/app/new-feature/create/page.tsx` — Create form page

### 9. Add Real-time Updates (Optional)

If your feature needs real-time updates:

```typescript
// Create a WebSocket service in services/newFeatureWebSocket.ts
import { WebSocketService } from '@/services/websocket';

class NewFeatureWebSocket extends WebSocketService {
  constructor() {
    super('/ws/new-feature/');
  }

  onFeatureUpdate(callback: (data: any) => void) {
    this.on('feature_update', callback);
  }
}

export const newFeatureWS = new NewFeatureWebSocket();
```

Then use it in your component:

```typescript
useEffect(() => {
  newFeatureWS.connect();
  newFeatureWS.onFeatureUpdate((data) => {
    dispatch(updateItem(data));
  });
  return () => newFeatureWS.disconnect();
}, [dispatch]);
```

## Key Patterns

### State Management
- Use Redux Toolkit for state management
- One slice + one thunk per domain
- Use typed hooks: `useAppDispatch()` and `useAppSelector()`
- Don't persist unless necessary (add to whitelist in store.ts)
- Handle `RESET_STATE` and `RESET_EXCEPT_AUTH` actions in your slice if needed:

  ```typescript
  extraReducers: (builder) => {
    builder.addCase('RESET_STATE', () => initialState);
    builder.addCase('RESET_EXCEPT_AUTH', () => initialState);
  },
  ```

### API Calls
- Use the centralized Axios instance from `@/utils/api`
- All endpoints defined in `apiEndpoints.ts`
- Handle loading states and errors consistently
- For real-time features, consider using WebSocket patterns (see `services/websocket/`)

### Styling
- Use TailwindCSS classes for styling
- Follow existing component patterns
- Use MUI components for complex UI elements (modals, forms)

### TypeScript
- Always define types for API responses and requests
- Use proper typing for Redux actions and state
- Export types from dedicated files in `types/`

## Checklist

- [ ] API endpoints added to `apiEndpoints.ts`
- [ ] TypeScript types defined in `types/`
- [ ] Redux slice created with proper initial state
- [ ] Redux thunks created for async operations
- [ ] Reducer registered in `store.ts`
- [ ] Components created with proper TypeScript typing
- [ ] Page created with metadata
- [ ] Navigation updated
- [ ] Responsive design considered
- [ ] Error handling implemented
- [ ] Loading states implemented
- [ ] Page tested in browser
