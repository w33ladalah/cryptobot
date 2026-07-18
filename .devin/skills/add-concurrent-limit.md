Generate concurrent operation limit with Redis atomic counter and Redux state management.

## Inputs

- Entity name (e.g., "video", "image", "talking_video")
- Max concurrent operations (e.g., 3)
- Backend router file path
- Frontend slice file path
- Frontend thunk file path

## Output Structure

**Backend:**
- Redis atomic counter in router endpoint
- Helper function to decrement counter
- Decrement calls in all completion paths (success, fail, cancel, timeout)
- 429 error when limit exceeded

**Frontend:**
- Redux slice with activeOperations array
- Redux thunks to add/update/remove active operations
- UI showing progress for concurrent operations
- Error modal when limit reached
- State persistence across navigation
- Restoration from backend on page load

## Template/Example

### Backend (video router):

```python
from app.db.redis import get_redis

async def decrement_video_gen_count(user_id: UUID, redis_client):
    """Decrement the Redis counter for active video generations."""
    redis_key = f"video_gen_count:{user_id}"
    try:
        await redis_client.decr(redis_key)
    except Exception as e:
        logger.error(f"Failed to decrement video gen count for user {user_id}: {e}")

@router.post("/generate")
async def generate_video(...):
    redis_client = await get_redis()
    MAX_CONCURRENT = 3
    redis_key = f"video_gen_count:{current_user.id}"
    
    current_count = await redis_client.incr(redis_key)
    if current_count == 1:
        await redis_client.expire(redis_key, 3600)
    
    if current_count > MAX_CONCURRENT:
        await redis_client.decr(redis_key)
        raise HTTPException(status_code=429, detail="Limit reached")
    
    # ... generation logic ...
    
    # On completion:
    await decrement_video_gen_count(video.user_id, redis_client)
```

### Frontend (slice):

```typescript
interface ActiveOperation {
  id: string;
  prompt: string;
  progress: number;
  status: 'starting' | 'processing' | 'succeeded' | 'failed' | 'canceled';
  created_at: string;
}

const slice = createSlice({
  name: 'video',
  initialState: {
    activeGenerations: [] as ActiveOperation[],
  },
  reducers: {
    addActiveGeneration: (state, action) => {
      state.activeGenerations.push(action.payload);
    },
    updateActiveGeneration: (state, action) => {
      const idx = state.activeGenerations.findIndex(g => g.id === action.payload.id);
      if (idx !== -1) state.activeGenerations[idx] = { ...state.activeGenerations[idx], ...action.payload };
    },
    removeActiveGeneration: (state, action) => {
      state.activeGenerations = state.activeGenerations.filter(g => g.id !== action.payload);
    },
  },
});
```

### Frontend (thunks):

```typescript
// Restore active operations on page load
export const restoreActiveGenerations = createAsyncThunk(
  'video/restoreActiveGenerations',
  async (_, { getState, dispatch }) => {
    const response = await api.get(API_ENDPOINTS.VIDEO.LIST);
    const videos = response.data?.videos || [];
    const activeVideos = videos.filter(v => v.status === 'starting' || v.status === 'processing');
    
    const state = getState();
    const existingIds = new Set(state.video.activeGenerations.map((g: { id: string }) => g.id));
    
    activeVideos.forEach(video => {
      if (!existingIds.has(video.id)) {
        dispatch(addActiveGeneration({ ...video }));
      }
      dispatch(pollVideoStatus(video.id));
    });
  }
);
```

### Frontend (page):

```typescript
useEffect(() => {
  const restoredRef = useRef(false);
  useEffect(() => {
    if (!restoredRef.current) {
      restoredRef.current = true;
      dispatch(restoreActiveGenerations());
    }
  }, []);
}, []);
```

## Rules

1. **Always use Redis atomic counter** - Never use database count for rate limiting (race condition risk)
2. **Decrement in ALL completion paths** - success, fail, cancel, timeout, exception
3. **Set expiration on first increment** - Prevents stale keys (e.g., 1 hour)
4. **Check for duplicates when restoring** - Prevent React key errors
5. **Persist slice in Redux store** - Add to persistConfig.whitelist
6. **Fetch from backend on restore** - More reliable than localStorage alone
