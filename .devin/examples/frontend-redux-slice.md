---
trigger: model_decision
description: Reference implementation for a complete Redux slice + thunk pair in the frontend
---

# Example: Frontend Redux Slice + Thunk

Complete reference for adding a new Redux domain to the frontend.

## Slice (`frontend/src/store/slices/myFeatureSlice.ts`)

```typescript
import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { fetchMyFeatures } from "../thunks/myFeatureThunks";

export interface MyFeature {
  id: string;
  name: string;
}

interface MyFeatureState {
  items: MyFeature[];
  loading: boolean;
  error: string | null;
}

const initialState: MyFeatureState = {
  items: [],
  loading: false,
  error: null,
};

const myFeatureSlice = createSlice({
  name: "myFeature",
  initialState,
  reducers: {
    clearError: (state) => { state.error = null; },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMyFeatures.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMyFeatures.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchMyFeatures.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Reset on global state clears
      .addCase("RESET_STATE", () => initialState)
      .addCase("RESET_EXCEPT_AUTH", () => initialState);
  },
});

export const { clearError } = myFeatureSlice.actions;
export default myFeatureSlice.reducer;
```

## Thunk (`frontend/src/store/thunks/myFeatureThunks.ts`)

```typescript
import { createAsyncThunk } from "@reduxjs/toolkit";
import api from "@/utils/api";
import { API_ENDPOINTS } from "@/constants/apiEndpoints";
import type { AppThunkConfig } from "../store";
import type { MyFeature } from "../slices/myFeatureSlice";

export const fetchMyFeatures = createAsyncThunk<MyFeature[], void, AppThunkConfig>(
  "myFeature/fetchAll",
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get(API_ENDPOINTS.MY_FEATURE.LIST);
      return response.data;
    } catch (error: unknown) {
      return rejectWithValue("Failed to fetch features");
    }
  }
);
```

## Register in Store (`frontend/src/store/store.ts`)

```typescript
import myFeatureReducer from "./slices/myFeatureSlice";

const rootReducer = combineReducers({
  // ...existing
  myFeature: myFeatureReducer,
});
```

## Component Usage

```typescript
import { useAppDispatch, useAppSelector } from "@/store/hooks";
import { fetchMyFeatures } from "@/store/thunks/myFeatureThunks";

const dispatch = useAppDispatch();
const { items, loading, error } = useAppSelector((state) => state.myFeature);

useEffect(() => {
  dispatch(fetchMyFeatures());
}, [dispatch]);
```

## Notes

- Add to `persistConfig.whitelist` only if this slice should survive page reload
- Use `RESET_EXCEPT_AUTH` case if slice should clear on logout (but not auth wipe)
