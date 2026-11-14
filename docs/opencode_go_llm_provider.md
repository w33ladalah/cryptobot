# OpenCode Go as the default LLM provider (config + docs only)

**Repo:** `w33ladalah/cryptobot`
**Branch:** `chore/opencode-go-llm-provider` — create it off `main` as your first step.
**Recommended model:** SWE-1.6. This is a fully specified, mechanical edit to three text files. There are no judgment calls, so do not "improve" anything beyond what is written here.

---

## 0. Read first

Read `docs/SOURCE_OF_TRUTH.md` **in full** before changing anything. Where it conflicts with your own assumptions, it wins. (You will edit that file below, so read it first.)

## 1. Context

- LLM providers live behind `apps/worker/llm/adapters/` and are selected by `config.LLM_ADAPTER_CLASS`. `LLM_PROVIDER` is descriptive only and is not read by `load_client_class()`.
- The `.env.example` files currently default to `ReplicateAdapter` with `google/gemini-2.5-flash`.
- The project owner now has an **OpenCode Go** subscription. OpenCode Go exposes an OpenAI-compatible `/chat/completions` endpoint, so the **existing** `OpenAiAdapter` (`apps/worker/llm/adapters/openai.py`) already works with it. It reads `LLM_BASE_URL` and `LLM_API_KEY` from config. **No adapter code needs to change.**
- This task only switches the documented default to OpenCode Go and keeps Replicate as a commented alternative.
- You do **not** have an OpenCode API key. You cannot and must not claim to have called the API. Live validation is a separate, later task (issue #24).

## 2. Required changes — exactly three files

### 2.1 `env_vars/.env.example`

In the LLM section, replace these six lines (currently `LLM_PROVIDER` through `LLM_REPLICATE_PREDICTION_TIMEOUT_SECONDS`) with the block below. Leave `SYSTEM_PROMPT` and every other line in the file untouched.

```
LLM_PROVIDER="opencode-go"
LLM_BASE_URL="https://opencode.ai/zen/go/v1"
LLM_API_KEY=
LLM_MODEL_NAME="deepseek-v4-flash"
LLM_ADAPTER_CLASS="OpenAiAdapter"

# Alternative: Replicate. Comment out the OpenCode Go block above and uncomment this one.
# LLM_PROVIDER="replicate"
# LLM_BASE_URL=
# LLM_API_KEY=
# LLM_MODEL_NAME="google/gemini-2.5-flash"
# LLM_ADAPTER_CLASS="ReplicateAdapter"
# LLM_REPLICATE_PREDICTION_TIMEOUT_SECONDS=120
```

`LLM_API_KEY` stays blank. Never put a real key in an example file.

### 2.2 `apps/worker/.env.example`

Make the identical replacement to the same six LLM lines (currently `LLM_PROVIDER` through `LLM_REPLICATE_PREDICTION_TIMEOUT_SECONDS`). Leave all other lines untouched, including the `OPENROUTER_*` lines.

### 2.3 `docs/SOURCE_OF_TRUTH.md`

Make three edits and keep the surrounding style:

1. **The "LLM adapter default switched…" bullet** (in the "Working/done" list). Rewrite it to say:
   - The default LLM path is now `OpenAiAdapter` pointed at OpenCode Go (`LLM_BASE_URL=https://opencode.ai/zen/go/v1`, `LLM_MODEL_NAME=deepseek-v4-flash` in `.env.example`). It was previously `ReplicateAdapter`.
   - `ReplicateAdapter` remains available as a commented alternative in `.env.example`. Its async prediction polling and `LLM_REPLICATE_PREDICTION_TIMEOUT_SECONDS` apply to that adapter only.
   - Keep the existing note that the config field is `LLM_ADAPTER_CLASS`, not `ADAPTER_CLASS`, and that `LLM_PROVIDER` is descriptive-only.
   - Add: "Not yet validated end-to-end with OpenCode Go — see issue #24."
2. **The Worker architecture bullet** that says `(current default: ReplicateAdapter)`. Change it to `(current default: OpenAiAdapter, pointed at OpenCode Go)`. Change nothing else in that bullet.
3. **A new limitation note.** Add one bullet to whichever section of the doc lists provider or platform limitations. If there is no such section, put it directly under the LLM adapter bullet. Use this wording:
   > `OpenAiAdapter` only calls `/chat/completions`. OpenCode Go models served only through `/responses` (e.g. `gpt-5.6-luna`) or `/messages` (e.g. `qwen3.6-plus`) will not work with it without adapter changes. Models that exist only on OpenCode Zen return model-not-found on Go. OpenCode's endpoints have changed over time — confirm the base URL and available models with `GET <LLM_BASE_URL>/models` and a real key before relying on them.

Do not edit any other part of `SOURCE_OF_TRUTH.md`.

## 3. Scope boundary — do NOT touch

- Any Python file. This includes `llm/adapters/*.py`, `config/settings.py` (its defaults stay as they are), and every test file.
- `apps/worker/requirements.txt`. `replicate` stays, because `ReplicateAdapter` remains.
- `docker/services/worker.yaml` already forwards every `LLM_*` variable. Its `:-20` timeout default differs from `settings.py`'s 120. That is a known discrepancy and out of scope.
- Gitignored local files: `env_vars/.env` and `docker/run-*-compose.yaml`. Never create, edit or reference real values from them.
- `OpenAiAdapter` behavior. Do not add a timeout, reasoning-content handling or retry logic. If those turn out to be needed, they get their own issue after live validation.
- No new tests, scratch scripts, debug files or helper scripts. Do not run the project's test suite, since no code changes.

Every commit on this branch must trace to this prompt. Make one commit. Do not add unrelated fixes, even trivial ones.

## 4. Acceptance criteria

Verify each with `git` commands against **tracked files only** (use `git grep`, not plain `grep`):

1. `git diff --name-only main...HEAD` lists exactly: `apps/worker/.env.example`, `docs/SOURCE_OF_TRUTH.md`, `env_vars/.env.example`.
2. In both `.env.example` files, `git grep -n "LLM_ADAPTER_CLASS"` shows `LLM_ADAPTER_CLASS="OpenAiAdapter"` as an **active** line and `# LLM_ADAPTER_CLASS="ReplicateAdapter"` as a **commented** line.
3. The active `LLM_*` values are identical in both `.env.example` files: provider `opencode-go`, base URL `https://opencode.ai/zen/go/v1`, model `deepseek-v4-flash`, adapter `OpenAiAdapter`, key blank.
4. `git grep -n "current default" docs/SOURCE_OF_TRUTH.md` no longer mentions `ReplicateAdapter` as the default.
5. The new limitation bullet from 2.3 is present.
6. `git diff main...HEAD | grep -E "^\+" | grep -iE "r8_|sk-|Bearer "` returns nothing. No secrets appear in the diff.

## 5. After implementation: update the docs

The `SOURCE_OF_TRUTH.md` edit in 2.3 **is** the docs update. No other docs need changes.

Open the PR against `main`. In the PR description:

- List the three files changed.
- State that this is config and docs only.
- State that it has **not** been validated against the live OpenCode Go API, which is tracked in issue #24.
- Do not claim any live call, test run or "verified" result.

Commit message: `chore: default LLM provider to OpenCode Go via OpenAiAdapter (issue #39)`

The tracking issue for this change is **#39**. Do not reference #24 (the later live-validation issue) or this prompt's filename number.
