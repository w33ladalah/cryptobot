---
trigger: model_decision
description: Reference implementation for async S3 upload in backend async context
---

# Example: Async S3 Upload in Backend

Use this pattern when uploading images to S3 from an async FastAPI context (routes or Celery tasks).

```python
import asyncio
import base64
import httpx
from mimetypes import guess_type

from app.core.s3 import upload_base64_to_s3
from app.core.config import settings


async def upload_image_url_to_s3(image_url: str, folder: str = "generated/") -> str | None:
    """Download an image URL and upload to S3. Returns S3 URL or None on failure."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(image_url)
            response.raise_for_status()

        mime_type = guess_type(image_url)[0] or "image/jpeg"
        base64_data = base64.b64encode(response.content).decode("utf-8")
        data_url = f"data:{mime_type};base64,{base64_data}"

        # upload_base64_to_s3 is synchronous — wrap in asyncio.to_thread
        s3_url = await asyncio.to_thread(
            upload_base64_to_s3,
            data_url,
            settings.AWS_S3_BUCKET_NAME,
            s3_folder=folder,
        )
        return s3_url
    except Exception:
        return None  # Caller handles missing S3 gracefully
```

## Usage in a Route or Task

```python
s3_url = await upload_image_url_to_s3(replicate_output_url, folder="generated/")
if s3_url:
    prediction.s3_url = s3_url
    prediction.s3_uploaded = True
    await db.flush()
```

## Key Points

- Use `httpx.AsyncClient` — never `requests` in async context
- Wrap `upload_base64_to_s3` in `asyncio.to_thread()` — it's synchronous (boto3)
- Always wrap in try/except and return None on failure — continue without S3 if upload fails
- Never pass Replicate URLs directly to imgproxy — always upload to S3 first
