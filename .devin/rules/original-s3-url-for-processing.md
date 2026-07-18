---
trigger: glob frontend/src/components/quick-tools/**
---

# Decode Imgproxy URLs for Backend Image Processing

## Rule

When sending images from the sidebar/gallery to backend processing endpoints (expand, enhance, edit, etc.), **decode the imgproxy URL on the frontend** to extract the original S3 URL instead of passing imgproxy URLs or `original_s3_url` through the component tree.

## Why

- **Security**: Avoids exposing imgproxy endpoints in API payloads
- **Quality**: Decoded S3 URLs provide full-resolution images without watermarks
- **Simplicity**: No need to pass `original_s3_url` through multiple component layers

## Implementation Pattern

### 1. Decode Function (in tool component)
```typescript
function decodeImgproxyUrl(imgproxyUrl: string): string | null {
  try {
    // Extract last segment without extension
    const segments = imgproxyUrl.split('/');
    const lastSegment = segments[segments.length - 1];
    if (!lastSegment) return null;

    // Remove extension
    const withoutExtension = lastSegment.includes('.') ? lastSegment.split('.')[0] : lastSegment;

    // Add padding if needed for base64 decoding
    const padded = withoutExtension + '='.repeat((4 - withoutExtension.length % 4) % 4);

    // Decode base64url
    const decoded = atob(padded.replace(/-/g, '+').replace(/_/g, '/'));
    return decoded;
  } catch (error) {
    console.error('Failed to decode imgproxy URL:', error);
    return null;
  }
}
```

### 2. Tool Component (e.g., ExpandTool.tsx)
```typescript
const handleGenerate = async () => {
  if (!imagePreview) return;
  try {
    const contentType = file?.type || 'image/png';
    const isFromSidebar = !file && imagePreview.startsWith('http');

    let decodedUrl: string | undefined;
    if (isFromSidebar) {
      // Decode imgproxy URL to get original S3 URL
      decodedUrl = decodeImgproxyUrl(imagePreview) || undefined;
    }

    await dispatch(
      expandImageReplicate({
        imageData: imagePreview,
        imageUrl: decodedUrl,  // Send decoded S3 URL
        imageId: sidebarImageId,
        contentType,
        // ...
      })
    ).unwrap();
  } catch (err) {
    console.error("Failed to expand image:", err);
  }
};
```

### 3. Thunk (quickToolsThunks.ts)
```typescript
interface ExpandImageReplicateParams {
  imageData: string;
  imageUrl?: string;  // Decoded S3 URL
  imageId?: string;
  contentType?: string;
  // ...
}

// Send to API
if (imageUrl) {
  payload.image_url = imageUrl;  // Prioritize decoded URL
} else if (imageId) {
  payload.image_id = imageId;
} else {
  payload.image_base64 = imageData;
}
```

### 4. Backend (replicate_quick_tools.py)
```python
class ExpandImageReplicateRequest(BaseModel):
    image_base64: Optional[str] = None
    image_url: Optional[str] = None  # Decoded S3 URL
    image_id: Optional[str] = None
    content_type: Optional[str] = Field("image/png")
    # ...

async def _resolve_image_source(
    image_base64: Optional[str] = None,
    image_url: Optional[str] = None,
    image_id: Optional[str] = None,
    user_id: Optional[str] = None,
    db: Optional[AsyncSession] = None,
) -> bytes:
    if image_id and db and user_id:
        # Fetch from DB with ownership check
        # ...
    if image_base64:
        return _decode_base64(image_base64)
    if image_url:
        return await _fetch_image_from_url(image_url)  # Direct S3 fetch
    raise ValueError("Either image_id, image_base64, or image_url must be provided")
```

## Priority Chain

1. `image_url` - Decoded S3 URL (from imgproxy) - highest quality
2. `image_id` - Fetch from DB with ownership check
3. `image_base64` - Uploaded file

## Fallback Behavior

If `decodeImgproxyUrl` returns null (invalid format or decode error):
- `imageUrl` becomes undefined
- Thunk falls back to `imageId` or `image_base64`
- User gets an error if no valid source is available

## Reference Implementation

- Frontend: `ExpandTool.tsx` - `decodeImgproxyUrl()` function
- Backend: `replicate_quick_tools.py` - `expand_image_replicate()` endpoint

## Affected Files
- `frontend/src/components/quick-tools/tools/ExpandTool.tsx`
- `frontend/src/store/thunks/quickToolsThunks.ts`
- `backend/app/routers/image/enhance/replicate_quick_tools.py`
