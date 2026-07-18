---
description: Rule to reference image generation documentation when working on related features
---

# Image Generation Documentation Reference Rule

## When to Apply

This rule applies whenever you are:

1. Modifying or debugging image generation features
2. Working with the UnifiedPromptForm component
3. Making changes to any part of the image generation flow
4. Adding new image-related features
5. Investigating image generation bugs

## Required Action

Before making changes to image generation features, ALWAYS:

1. Read `docs/IMAGE_GENERATION_FLOW_ANALYSIS.md` to understand the complete flow
2. Read `docs/PHOTO_MODEL_S3_UPLOAD_FIX.md` if working with PhotoModelPredictionImage S3 uploads
3. Check how your changes affect the overall system
4. Update the documentation if you make architectural changes

## File Patterns

This rule triggers for files matching:

- `frontend/src/app/generate/**/*`
- `frontend/src/components/UnifiedPromptForm.tsx`
- `frontend/src/components/ImageGrid.tsx`
- `backend/app/routers/image/generate/**/*`
- `backend/app/models/image.py`
- `backend/app/models/prediction.py`
- `backend/app/crud/photo_model.py`
- Any file related to image generation

## Why This Rule

- The image generation system is complex with many interconnected parts
- UnifiedPromptForm is used across multiple generation modes (generate, edit, enhance, video)
- Changes can have unintended consequences across the system
- Having comprehensive understanding prevents breaking existing functionality
- Documentation ensures consistency and knowledge transfer

## Checklist

- [ ] Read IMAGE_GENERATION_FLOW_ANALYSIS.md before starting
- [ ] Identified all affected components in your change
- [ ] Considered impact on other generation modes
- [ ] Updated documentation if architecture changed
- [ ] Tested all generation modes after changes
