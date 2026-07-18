---
trigger: glob
globs: backend/**
description: Known bugs and gotchas in the backend that must not be reintroduced
---

# Backend Known Bugs & Gotchas

## 1. `belongs_to_user()` UUID vs String Bug

**File:** `backend/app/crud/photo_model_image.py`

`belongs_to_user()` compares `Prediction.user_id == str(user_id)` — UUID column vs string — always returns `False`.

**Do NOT use it.** Use inline query instead:

```python
# CORRECT
result = await db.execute(
    select(PhotoModelPrediction).where(PhotoModelPrediction.user_id == current_user.id)
)
```

## 2. Replicate `Prediction.wait()` Returns None

`wait()` mutates the prediction in-place and returns `None`. Never reassign from it.

```python
# WRONG — replicate_prediction becomes None
replicate_prediction = await run_in_threadpool(replicate_prediction.wait)

# CORRECT
await run_in_threadpool(replicate_prediction.wait)
# replicate_prediction.status and .output are now updated
```

When using a fallback chain: check for `canceled` status before continuing — cancellation must stop the chain.

## 3. TalkingVideoStatus Enum String Representation

`str(video.status)` returns `"TalkingVideoStatus.SUCCEEDED"`, NOT `"succeeded"`.

```python
# CORRECT
if video.status != TalkingVideoStatus.SUCCEEDED:
    raise HTTPException(...)

# WRONG
if str(video.status) not in ("succeeded",):
    raise HTTPException(...)
```

## 4. SQLEnum str Enum Values

When using `str` enums with SQLAlchemy `SQLEnum`, always use `values_callable`:

```python
# CORRECT
status: Mapped[MyStatus] = mapped_column(
    SQLEnum(MyStatus, values_callable=lambda x: [e.value for e in x]),
    nullable=False,
)

# WRONG — stores uppercase enum member names instead of lowercase values
status: Mapped[MyStatus] = mapped_column(SQLEnum(MyStatus), nullable=False)
```

## 5. Circular Import: photo_model.py ↔ photo_utils.py

These two modules have a circular dependency. Use lazy imports inside functions:

```python
def my_function():
    from app.utils.photo_utils import upload_base64_to_s3  # lazy import
    ...
```

## 6. imgproxy URL Decoding (Talent Detection)

Frontend passes imgproxy URLs like `https://img.ayalive.ai/<sig>/<transforms>/<base64_s3_url>.<ext>`.

```python
last_segment = ref_img.rstrip('/').split('/')[-1]
last_segment = last_segment.rsplit('.', 1)[0] if '.' in last_segment else last_segment
padded = last_segment + '=' * (-len(last_segment) % 4)
decoded_url = base64.urlsafe_b64decode(padded).decode('utf-8')
# Only treat as talent if '/talent/' in decoded_url
```

Always wrap in `try/except` — not all URLs are valid base64.
