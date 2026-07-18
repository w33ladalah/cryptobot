---
trigger: model_decision
description: ADR 001 — All download types stored in a single download_histories table
---

# ADR 001: Single Download History Table

**Status:** Accepted  
**Date:** 2024

## Context

The platform has multiple downloadable media types: images (FinalImage, PhotoModelPrediction), videos (VideoGeneration), and talking videos (TalkingVideo). Initial implementation used separate history tables per media type.

## Decision

Store **all downloads** in a single `download_histories` table with a `media_type` discriminator column.

**Values:** `"final"` | `"photo_model"` | `"video"` | `"talking_video"`

The `image_id` column stores the ID of the downloaded entity regardless of type.

## Consequences

**Good:**
- Single query for user download history across all media types
- Consistent license tracking per download record
- Unified point deduction audit trail
- `is_downloaded` flag on each image/video model for cleanup exclusion

**Constraint:**
- The old `video_download_histories` table was dropped in migration `20260504_1200` — do not recreate it.
- Any new downloadable media type must use this same table with a new `media_type` value.
