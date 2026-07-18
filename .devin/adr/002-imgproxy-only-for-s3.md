---
trigger: model_decision
description: ADR 002 — Imgproxy only accepts S3 URLs, never Replicate URLs
---

# ADR 002: Imgproxy Accepts Only S3 URLs

**Status:** Accepted  
**Date:** 2024

## Context

The platform uses Imgproxy (`https://img.ayalive.ai`) for on-the-fly image optimization, resizing, and format conversion. AI model predictions are initially stored on Replicate's CDN before being uploaded to S3.

## Decision

`generate_imgproxy_url()` must **only** receive S3 URLs. If no S3 URL exists for an image, return `None`.

Never fall back to Replicate URLs.

## Why

1. **Access control**: Imgproxy is configured with an allowlist of our S3 bucket domain. Replicate URLs are external and will return 403 or 404 from imgproxy.
2. **Security**: Replicate URLs are temporary and publicly accessible — exposing them directly leaks the Replicate prediction URL.
3. **CDN**: S3 URLs can be cached/proxied; Replicate URLs cannot.

## Consequences

- Images without S3 upload show as null/missing in the frontend — this is acceptable behavior.
- S3 upload must complete before image is considered fully available for display.
- See `backend/app/core/s3.py` for `upload_base64_to_s3()` helper.
