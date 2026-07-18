# Redux Persist Reset Reducer Rule

When a Redux slice is persisted via redux-persist, the reset reducer should NOT clear fields that should persist across page navigation.

## Pattern

```typescript
// CORRECT - Don't reset persisted fields
resetVideoState: (state) => {
  state.currentVideo = null;
  state.isGenerating = false;
  state.progress = 0;
  state.buttonText = 'Generate Video';
  state.isSubmitted = false;
  state.error = null;
  // Don't reset prompt - it should persist across navigation
},

// WRONG - Resets everything including persisted fields
resetVideoState: (state) => {
  state.currentVideo = null;
  state.isGenerating = false;
  state.progress = 0;
  state.buttonText = 'Generate Video';
  state.isSubmitted = false;
  state.error = null;
  state.prompt = ''; // ❌ This clears persisted prompt
},
```

## When to Apply

- A slice is in `persistConfig.whitelist` in `store.ts`
- The field should persist when user navigates away and back
- Common examples: prompt text, form inputs, user preferences

## Current Persisted Slices

- `generator` - Photo model generation state
- `auth` - Authentication state
- `ui` - UI state
- `video` - Video generation state (including prompt)

## Trigger

File pattern: `frontend/src/store/slices/*.ts` - When adding or modifying reset reducers
