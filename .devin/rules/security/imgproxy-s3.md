---
trigger: model_decision
description: Image URL security — never expose raw S3 or Replicate URLs to frontend
---

# Image URL Security

## Rule

**Never expose raw S3 URLs or Replicate URLs** to the frontend.

All image URLs returned in API responses must be proxied via `generate_imgproxy_url()`.

## Correct Pattern

```python
# CORRECT — S3 URL through imgproxy, None if no S3 URL
img_url = generate_imgproxy_url(image.s3_url, width=380, height=0) if image.s3_url else None
```

## Wrong Patterns

```python
# WRONG — exposes raw S3 URL
return {"image_url": image.s3_url}

# WRONG — passes Replicate URL to imgproxy (imgproxy can't access it)
source = image.s3_url or image.replicate_url
img_url = generate_imgproxy_url(source, ...)

# WRONG — exposes replicate_url in response
return {"image_url": image.s3_url or image.replicate_url}
```

## Why

- imgproxy is configured to only proxy from our S3 bucket
- Replicate URLs are temporary, external, and inaccessible to imgproxy
- Exposing raw S3 URLs bypasses imgproxy optimizations and CDN
- Security: direct S3 URLs expose bucket structure

## If No S3 URL

Return `None` for the image URL. The frontend handles null image URLs gracefully.

## Affected Files

Any file that returns image URLs in API responses — search for `replicate_url` in responses as an anti-pattern check.
