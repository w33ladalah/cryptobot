---
trigger: glob
globs: backend/**
description: Points system rules — always check docs/AYA_POINTS_SYSTEM.md before implementing point logic
---

# Points System

Dual-currency: **Green Points** (AI/model operations) + **Blue Points** (human/talent services).

## Before Implementing Any Point Logic

Read `docs/AYA_POINTS_SYSTEM.md` to get:
1. Correct **service alias** for the operation
2. **Point color** (green or blue)
3. **Point cost** and unit

## Pattern

```python
from app.crud.points import PointsCRUD

# 1. Check balance first (raises HTTP 402 if insufficient)
await check_user_points_for_service(db, user_id, "imagen")

# 2. Deduct after successful operation
await deduct_points_for_service(
    db, user_id,
    service_alias="imagen",        # MUST match docs/AYA_POINTS_SYSTEM.md
    reference_id=str(prediction_id)
)
```

## Download Points

- Green: service `"download"` — every download
- Blue: service `"model_standard_license_download"` — multiplied by talent count (PhotoModel only)

## Common Service Aliases

| Feature | Alias | Color |
|---------|-------|-------|
| Image generation | `imagen` | Green |
| Image download | `download` | Green |
| Talent license download | `model_standard_license_download` | Blue |
| Video 5s | `video_5s` | Green |
| Video 10s | `video_10s` | Green |
| Talking video (script) | `talking_video_script` | Green |
| Talking video (upload) | `talking_video_upload` | Green |

Always verify in `docs/AYA_POINTS_SYSTEM.md` — costs change over time.
