---
description: How to work with download functionality for images, videos, and talking videos across frontend, backend, and admin
---

# Download Functionality Workflow

This workflow covers the complete download system for images, videos, and talking videos across all three applications: backend API, frontend user interface, and admin panel.

## Overview

The download system supports three media types with unified architecture:

- **Images**: `FinalImage` and `PhotoModelPredictionImage`
- **Videos**: `VideoGeneration` (Kling model)
- **Talking Videos**: `TalkingVideo` (Kling Avatar model)

All downloads are tracked in a single `DownloadHistory` table with `media_type` field for differentiation.

## Before Starting Work

**Always read relevant documentation in `docs/` before making changes:**

1. **Check `docs/README.md`** — Review the documentation index to understand existing docs
2. **Search `docs/` for related topics** — Look for existing documentation about:
   - Download functionality
   - Video generation
   - License system
   - Points system
   - Any specific media type you're working with
3. **Update existing docs** — If related documentation exists, update it instead of creating duplicates
4. **Create new docs only when needed** — For new features or major bug fixes, create documentation in `docs/` following the format in `docs/documentation-requirements.md`

**Key documentation files to review:**

- `docs/README.md` — Documentation index
- `docs/VIDEO_GENERATION_TALENT_REFERENCES.md` — Video generation with talent references
- `docs/AYA_POINTS_SYSTEM.md` — Points system (green/blue points)
- `docs/API_REFERENCE.md` — API endpoint reference
- `docs/documentation-requirements.md` — Documentation guidelines

## Backend Implementation

### 1. Models & Database

#### DownloadHistory Model (`backend/app/models/download_history.py`)

- **Purpose**: Single source of truth for all download tracking
- **Key Fields**:
  - `image_id`: UUID of downloaded item (works for all media types)
  - `media_type`: `"final"`, `"photo_model"`, `"video"`, `"talking_video"`
  - `license_id`: FK to selected download license
  - `license_expired_at`: Calculated expiration time
  - `download_source`: `"s3"` or `"replicate"`

#### DownloadLicense Model (`backend/app/models/download_license.py`)

- **Purpose**: License tiers and pricing
- **Key Fields**:
  - `media_type`: Filter licenses by media type
  - `license_duration` + `license_duration_unit`: Duration calculation
  - `service_point_cost_id`: Blue points cost for talent usage

### 2. Download Endpoints

#### Image Downloads (`backend/app/routers/image/utils/interactions.py`)

```python
@router.get("/interactions/{image_id}/download")
async def download_image(image_id: UUID, db: AsyncSession, current_user: User):
    # 1. Ownership check
    # 2. Existing download check (no double charges)
    # 3. License validation
    # 4. Point deduction (green + blue for talent usage)
    # 5. Metadata embedding (PNG/JPEG/WebP support)
    # 6. DownloadHistory creation with license_expired_at
    # 7. Background task: mark is_downloaded=True
    # 8. Stream response with metadata
```

#### Video Downloads (`backend/app/routers/video.py`)

```python
@router.post("/{video_id}/download")  # Regular videos
@router.post("/talking/{video_id}/download")  # Talking videos
async def download_video(video_id: UUID, db: AsyncSession, current_user: User):
    # 1. Ownership + status check (must be SUCCEEDED)
    # 2. Existing download check
    # 3. License resolution (media_type="video" or "talking_video")
    # 4. Point deduction
    # 5. DownloadHistory creation
    # 6. Mark is_downloaded=True
    # 7. Stream video via aiohttp proxy from S3
```

### 3. License System

#### License Resolution Pattern

```python
# Fetch licenses filtered by media_type
licenses = await download_license_crud.get_multi(
    db, 
    media_type="video"  # or "talking_video", "image"
)

# Check existing download first
existing = await download_history_crud.get_user_download(
    db, user_id=current_user.id, image_id=item_id, media_type="video"
)
if existing and not is_license_expired(existing.license_expired_at):
    return stream_download()  # No additional charges
```

#### Expiration Calculation

```python
from app.core.license_utils import calculate_license_expiration

license_expired_at = None
if license and license.license_duration and license.license_duration_unit:
    license_expired_at = calculate_license_expiration(
        datetime.now(timezone.utc),
        license.license_duration,
        license.license_duration_unit
    )
```

### 4. Point System

#### Green Points (Base Downloads)

- Service: `"download"`
- Always deducted for every download

#### Blue Points (Talent Usage)

- Service: `"model_standard_license_download"`
- Multiplied by talent count
- Only for images using talent models

### 5. Metadata Embedding (Images Only)

#### AYA Metadata Structure

```python
metadata = {
    "prediction_id": str(prediction_id),
    "talents": [
        {"id": str(talent.id), "name": talent.name},
        # ... multiple talents for multi-talent usage
    ],
    "image_id": str(image_id),
    "prediction_type": "photo_model" | "text_to_image"
}
```

#### Talent Extraction for PhotoModel Images

```python
# Always use TalentUsage records (multi-talent support)
talents_list = []
for talent_usage in pred.talent_usages:
    if talent_usage.talent:
        talents_list.append({
            "id": str(talent_usage.talent.id),
            "name": talent_usage.talent.talent_name or talent_usage.talent.file_name
        })
```

## Frontend Implementation

### 1. Download Modals

#### Image Downloads (`DownloadLicenseModal.tsx`)

- Fetches licenses with `media_type='image'`
- Shows metadata panel (dimensions, talent info)
- Handles license selection and point deduction
- Uses Redux thunk `downloadImage` for actual download

#### Video Downloads (`VideoDownloadLicenseModal.tsx`)

- Fetches licenses based on video type:
  - Regular videos: `media_type='video'`
  - Talking videos: `media_type='talking_video'`
- Shows video preview and metadata
- Uses local state (not Redux) to avoid cache conflicts

### 2. Download Flow

#### Image Download Pattern

```typescript
// 1. Check download eligibility
const response = await api.get(`/api/images/image/${imageId}/info`);

// 2. If not downloaded, show license modal
if (!response.data.is_downloaded) {
  dispatch(openDownloadLicenseModal({ imageId }));
  return;
}

// 3. Direct download (blob response)
const res = await api.get(downloadUrl, { responseType: 'blob' });
const blob = new Blob([res.data], { type: 'image/jpeg' });
const objectUrl = window.URL.createObjectURL(blob);
// Trigger download via temporary anchor element
```

#### Video Download Pattern

```typescript
// Similar to images but uses POST endpoint
const res = await api.post(downloadUrl, 
  { license_id: selectedLicense.id }, 
  { responseType: 'blob' }
);
const blob = new Blob([res.data], { type: 'video/mp4' });
// Same blob-to-anchor download pattern
```

### 3. Error Handling for Blob Responses

```typescript
try {
  const res = await api.post(url, data, { responseType: 'blob' });
  // Success: handle blob
} catch (error) {
  // Error responses with responseType: "blob" arrive as Blob
  if (error.response?.data instanceof Blob) {
    const errorText = await error.response.data.text();
    const errorData = JSON.parse(errorText);
    showError(errorData.detail);
  } else {
    showError(error.message);
  }
}
```

### 4. Downloads Page (`Downloads.tsx`)

#### Unified History API

```typescript
// GET /api/user/downloads/history
// Backend branches on media_type to fetch appropriate data
interface DownloadedImage {
  id: string;
  image_id: string;
  media_type: string;  // "final", "photo_model", "video", "talking_video"
  downloaded_at: string;
  license_expired_at: string | null;
  // For images: image_url, thumbnail_url, prompt
  // For videos: video_url, prompt, duration, resolution
}
```

#### Rendering Logic

```typescript
// Branch on media_type for rendering
{record.media_type === 'video' || record.media_type === 'talking_video' ? (
  <video controls src={record.video_url} />
) : (
  <Image src={record.image_url} />
)}
```

## Admin Implementation

### 1. Download License Management

#### List Page (`admin/src/app/download-licenses/page.tsx`)

- Displays all download licenses across media types
- Media type badges (green=image, blue=video, purple=talking video)
- CRUD operations (Create, Edit, Delete, Toggle Active)

#### Create/Edit Form

- Media type selector dropdown
- License duration fields (value + unit)
- Service point cost association
- Rich text content areas for license terms

### 2. License Service (`admin/src/services/downloadLicenses.ts`)

```typescript
class DownloadLicensesService {
  async list(): Promise<DownloadLicense[]>  // All media types
  async get(id: string): Promise<DownloadLicense>
  async create(data: CreateDownloadLicenseRequest): Promise<DownloadLicense>
  async update(id: string, data: UpdateDownloadLicenseRequest): Promise<DownloadLicense>
  async delete(id: string): Promise<void>
}
```

## Key Patterns & Best Practices

### 1. URL Generation

- **Never expose raw S3 URLs** to frontend
- Always use `generate_imgproxy_url()` for images
- Video downloads stream through backend proxy

### 2. Async Operations

- S3 uploads in async contexts: use `asyncio.to_thread()`
- Video streaming: use `aiohttp` for non-blocking proxy
- Image downloads: use `StreamingResponse` with generators

### 3. Database Patterns

- **Single DownloadHistory table** for all media types
- **media_type field** for differentiation
- **license_expired_at** calculated on creation, not backfilled
- **is_downloaded flag** on media models for cleanup exclusion

### 4. Error Handling

- Wrap blob responses in try/catch for JSON error parsing
- Use proper HTTP status codes (401, 403, 404, 402)
- Validate ownership before any operations

### 5. Testing Strategy

- Test download flow for each media type
- Verify license expiration logic
- Test point deduction accuracy
- Verify metadata embedding for images
- Test video streaming integrity

## Common Issues & Solutions

### Issue: Double Charging

**Solution**: Always check existing download first before charging points.

### Issue: License Expiration Not Set

**Solution**: Calculate `license_expired_at` on creation, don't leave NULL.

### Issue: Circular Import photo_model ↔ photo_utils

**Solution**: Use lazy imports inside functions when needed.

### Issue: Video Download Blob Errors

**Solution**: Parse blob as text then JSON for error messages.

### Issue: Mixed Timezones

**Solution**: Use UTC for database, GMT+7 for user-facing timestamps.

## Migration Requirements

When modifying download functionality:

1. **Model changes**: Generate Alembic migration immediately
2. **New media types**: Add to `media_type` enum/constraints
3. **License changes**: Update default licenses and sort orders
4. **Point costs**: Update `service_point_costs` table

## Files Reference

### Backend Core Files

- `backend/app/models/download_history.py` - Download tracking
- `backend/app/models/download_license.py` - License definitions
- `backend/app/routers/image/utils/interactions.py` - Image downloads
- `backend/app/routers/video.py` - Video downloads
- `backend/app/core/license_utils.py` - License calculations
- `backend/app/utils/image_metadata.py` - Metadata embedding

### Frontend Core Files

- `frontend/src/components/DownloadLicenseModal.tsx` - Image license modal
- `frontend/src/components/VideoDownloadLicenseModal.tsx` - Video license modal
- `frontend/src/components/user/Downloads.tsx` - Download history
- `frontend/src/hooks/useImageDownload.ts` - Download utility hook
- `frontend/src/store/thunks/generatorThunks.ts` - Image download thunk

### Admin Core Files

- `admin/src/app/download-licenses/page.tsx` - License list
- `admin/src/app/download-licenses/new/page.tsx` - Create license
- `admin/src/services/downloadLicenses.ts` - License service

This workflow provides the complete foundation for working with download functionality across all media types in the Aya AI platform.
