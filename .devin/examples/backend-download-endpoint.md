---
trigger: model_decision
description: Reference implementation for a backend download endpoint with license, points, and history recording
---

# Example: Backend Download Endpoint

Complete pattern for a download endpoint (image/video/talking-video).

```python
@router.get("/{item_id}/download")
async def download_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # 1. Ownership check
    item = await item_crud.get(db, item_id)
    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Not found")

    # 2. Status check
    if item.status != ItemStatus.SUCCEEDED:
        raise HTTPException(status_code=400, detail="Item not ready")

    # 3. Check for existing download (idempotent — don't double-charge)
    existing = await db.execute(
        select(DownloadHistory).where(
            DownloadHistory.image_id == item_id,
            DownloadHistory.user_id == current_user.id,
            DownloadHistory.media_type == "your_media_type",
        ).limit(1)
    )
    already_downloaded = existing.scalars().first() is not None

    if not already_downloaded:
        # 4. Resolve license
        resolved_license = await resolve_download_license(db, media_type="your_media_type")

        # 5. Check + deduct green points
        await check_user_points_for_service(db, current_user.id, "download")
        await deduct_points_for_service(db, current_user.id, "download", str(item_id))

        # 6. Calculate license expiration at creation time
        license_expired_at = None
        if resolved_license and resolved_license.license_duration and resolved_license.license_duration_unit:
            license_expired_at = calculate_license_expiration(
                datetime.now(timezone.utc),
                resolved_license.license_duration,
                resolved_license.license_duration_unit,
            )

        # 7. Record download history
        await DownloadHistoryCRUD(db).create(
            user_id=current_user.id,
            image_id=item_id,
            media_type="your_media_type",
            license_id=resolved_license.id if resolved_license else None,
            license_expired_at=license_expired_at,
        )

        # 8. Mark item as downloaded (background task to avoid holding response)
        background_tasks.add_task(mark_item_downloaded, db, item_id)

    # 9. Stream response
    async def stream():
        async with aiohttp.ClientSession() as session:
            async with session.get(item.s3_url) as resp:
                async for chunk in resp.content.iter_chunked(1024 * 256):
                    yield chunk

    return StreamingResponse(
        stream(),
        media_type="video/mp4",
        headers={"Content-Disposition": f'attachment; filename="{item_id}.mp4"'},
    )
```

## Key Points

- Always check for existing download FIRST to avoid double-charging
- Calculate `license_expired_at` at creation time — never leave NULL
- `mark_item_downloaded` via background task to not delay response
- `media_type` values: `"final"`, `"photo_model"`, `"video"`, `"talking_video"`
