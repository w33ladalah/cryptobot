---
description: How to add a new Redux slice and thunk for the frontend
---

# Add Redux Slice Workflow

## Steps

### 1. Create the slice

Create `frontend/src/store/slices/<feature>Slice.ts`:

```typescript
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export interface FeatureState {
  items: FeatureItem[];
  loading: boolean;
  error: string | null;
}

const initialState: FeatureState = {
  items: [],
  loading: false,
  error: null,
};

const featureSlice = createSlice({
  name: "feature",
  initialState,
  reducers: {
    setItems: (state, action: PayloadAction<FeatureItem[]>) => {
      state.items = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Add thunk cases here
  },
});

export const { setItems, clearError } = featureSlice.actions;
export default featureSlice.reducer;
```

### 2. Create the thunk

Create `frontend/src/store/thunks/<feature>Thunks.ts`:

```typescript
import { createAsyncThunk } from "@reduxjs/toolkit";
import api from "@/utils/api";
import { API_ENDPOINTS } from "@/constants/apiEndpoints";
import type { AppThunkConfig } from "../store";

export const fetchFeatureItems = createAsyncThunk<
  FeatureItem[],      // Return type
  void,               // Arg type
  AppThunkConfig      // ThunkAPI config
>("feature/fetchItems", async (_, { rejectWithValue }) => {
  try {
    const response = await api.get(API_ENDPOINTS.FEATURE.LIST);
    return response.data;
  } catch (error: unknown) {
    return rejectWithValue("Failed to fetch items");
  }
});
```

### 3. Wire thunk into slice extraReducers

In the slice file, import the thunk and add cases:

```typescript
extraReducers: (builder) => {
  builder
    .addCase(fetchFeatureItems.pending, (state) => {
      state.loading = true;
      state.error = null;
    })
    .addCase(fetchFeatureItems.fulfilled, (state, action) => {
      state.loading = false;
      state.items = action.payload;
    })
    .addCase(fetchFeatureItems.rejected, (state, action) => {
      state.loading = false;
      state.error = action.payload as string;
    });
},
```

### 4. Register the reducer in the store

Edit `frontend/src/store/store.ts`:

1. Import the reducer and state type.
2. Add to `RootState` interface.
3. Add to `rootReducer` combineReducers.
4. If the slice should reset on `RESET_EXCEPT_AUTH`, add it to `clearedState`.

### 5. Add to persist whitelist (if needed)

In `store.ts`, add the slice name to `persistConfig.whitelist` only if it should survive page reloads.

### 6. Use in components

```typescript
import { useAppDispatch, useAppSelector } from "@/store/hooks";
import { fetchFeatureItems } from "@/store/thunks/featureThunks";

const dispatch = useAppDispatch();
const { items, loading } = useAppSelector((state) => state.feature);

useEffect(() => {
  dispatch(fetchFeatureItems());
}, [dispatch]);
```
