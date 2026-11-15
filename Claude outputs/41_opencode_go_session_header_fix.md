# Fix OpenCode Go requests in OpenAiAdapter (session header, user agent, default model)

**Repo:** `w33ladalah/cryptobot`
**Issue:** #41
**Branch:** `fix/opencode-go-session-header` (create it off `main` as your first step; one branch for this prompt only)
**Recommended model:** SWE-1.7. The code change is small, but one required test must exercise the real OpenAI SDK at the HTTP level, and that needs care.

---

## 0. Read first

Before changing anything, read `docs/SOURCE_OF_TRUTH.md` in full and follow its rules. Where it conflicts with your own assumptions, it wins. Do not assume config values, architecture or scope beyond what that document and the actual code confirm. Re-read `apps/worker/llm/adapters/openai.py` and `apps/worker/tests/openai_adapter_tests.py` before editing them.

## 1. Context

- `OpenAiAdapter` (`apps/worker/llm/adapters/openai.py`) wraps the OpenAI Python SDK (`openai==1.62.0`). It builds the client in `__init__` with only `api_key=config.LLM_API_KEY...` and `base_url=config.LLM_BASE_URL`.
- The project now defaults to OpenCode Go (`LLM_BASE_URL=https://opencode.ai/zen/go/v1`) through this adapter.
- **Bug:** OpenCode Go rejects every request from this adapter with HTTP 400 `MissingSessionID` ("Request is missing x-opencode-session and cannot be routed efficiently"). The adapter catches the exception, prints a traceback and returns `None`.
- **Verified manually by the project owner (not by you):** when each request carries an `x-opencode-session: <uuid>` header and `User-Agent: cryptobot-worker/0.1`, the models `deepseek-v4.1-flash`, `glm-5.3-flash` and `deepseek-v4-pro` return valid responses over `/chat/completions`.
- **Stale default:** the current default model `deepseek-v4-flash` is no longer in OpenCode Go's model list. The new default is `deepseek-v4.1-flash`.
- You do **not** have an OpenCode API key. You must not call the live OpenCode API and must not claim any live verification.

## 2. Required changes

### 2.1 `apps/worker/llm/adapters/openai.py`

In `OpenAiAdapter.__init__`:

1. Decide whether the configured base URL points at OpenCode: parse `config.LLM_BASE_URL` with `urllib.parse.urlparse`, lowercase the `hostname`, and compare for **exact equality** with `"opencode.ai"`. Never use a substring or `endswith` check. If `config.LLM_BASE_URL` is not a non-empty `str` (for example `None`, empty, or a mock object in a test), treat it as not OpenCode and do not raise.
2. If it is OpenCode: generate `self.session_id = str(uuid.uuid4())` once per adapter instance, and construct the client with `default_headers={"x-opencode-session": self.session_id, "User-Agent": "cryptobot-worker/0.1"}` in addition to the existing arguments.
3. If it is not OpenCode: construct the client exactly as it is today. Do **not** pass a `default_headers` argument at all.
4. Define the host (`"opencode.ai"`) and the user agent (`"cryptobot-worker/0.1"`) as module-level constants.

Do not change `completions()`, its error handling, its `None` return behavior, `generation()`, or anything else in the file. Do not add retries or timeouts here.

### 2.2 `apps/worker/tests/openai_adapter_tests.py`

Keep all existing tests unchanged in behavior. Do not delete or weaken any. Check that each existing test sets `mock_config.LLM_BASE_URL` to a string; if one does not, make the smallest possible fix to that test and mention it in the PR.

Add these tests to the existing `TestOpenAiAdapter` class (or a new class in the same file):

1. **OpenCode host adds headers.** With `LLM_BASE_URL = "https://opencode.ai/zen/go/v1"` and `OpenAIClient` mocked, assert the client was constructed with a `default_headers` dict containing `x-opencode-session` (a value that parses with `uuid.UUID(...)`) and `User-Agent == "cryptobot-worker/0.1"`.
2. **Session id is stable per instance and differs between instances.** Two `completions()` calls on one adapter use the same session id; two separately constructed adapters have different session ids.
3. **Other hosts get no extra headers.** For each of `https://openrouter.ai/api/v1`, `https://api.openai.com/v1`, `https://opencode.ai.evil.example/v1`, and `https://notopencode.ai/v1`, assert the client was constructed **without** a `default_headers` argument.
4. **Wire-level test using the real SDK.** Patch `llm.adapters.openai.OpenAIClient` with a callable that builds the real `openai.OpenAI` client but forces `http_client=httpx.Client(transport=httpx.MockTransport(handler))` (for example with `functools.partial`). The handler records `request.headers` and returns a minimal valid chat-completion JSON response. Call `adapter.completions("test")` and assert that the recorded request has `x-opencode-session` equal to `adapter.session_id` and a `user-agent` header equal to `cryptobot-worker/0.1`. This proves the SDK actually sends the override on the wire, not just that the constructor received it.
   - If the SDK does not let `default_headers` override the `User-Agent` header, **stop and report that in the PR description** instead of working around it with hacks.
   - Do not call any real network endpoint in any test.

Run only this test file, inside the worker container, using the repo's existing way of running tests (check the README and existing test files for the convention). Do **not** run the whole test suite. In the PR description, include the exact command you ran and the pasted output.

### 2.3 `env_vars/.env.example` and `apps/worker/.env.example`

In the active (uncommented) OpenCode Go LLM block of both files, change `LLM_MODEL_NAME="deepseek-v4-flash"` to `LLM_MODEL_NAME="deepseek-v4.1-flash"`. Leave every other line unchanged, including the commented Replicate alternative block and `LLM_API_KEY` (which stays blank). If the line is not found exactly as described, stop and report instead of guessing.

### 2.4 `docs/SOURCE_OF_TRUTH.md`

Make only these edits, keeping the surrounding style. Do not touch any other section, and do not edit the roadmap or milestone text.

1. In section 2, the LLM default bullet: change the model name to `deepseek-v4.1-flash`, and replace the sentence that says it is currently blocked by issue #41 with a statement that `OpenAiAdapter` now sends an `x-opencode-session` header (a per-instance UUID) and `User-Agent: cryptobot-worker/0.1` when the base URL host is exactly `opencode.ai`. Keep the statement that end-to-end validation with OpenCode Go is still pending (issue #24). Do not claim it has been validated.
2. In section 7, the OpenCode limitation bullet: add one sentence saying OpenCode Go requires the `x-opencode-session` header and that the adapter adds it automatically only for the `opencode.ai` host.
3. In section 8, add a short entry for issue #41 in the same format as the existing entries (problem, direction taken).

## 3. Scope boundary

You may touch **only** these five files:

- `apps/worker/llm/adapters/openai.py`
- `apps/worker/tests/openai_adapter_tests.py`
- `env_vars/.env.example`
- `apps/worker/.env.example`
- `docs/SOURCE_OF_TRUTH.md`

Do not touch `config/settings.py`, `llm_analysis.py`, `tasks/analyzer.py`, any other adapter, any `docker/` file, or `requirements.txt` (no new dependencies). Do not edit or commit the gitignored local `env_vars/.env` or `docker/run-development-compose.yaml`. Do not create any other file or folder in the repo. Touching anything outside the list is scope creep and will be flagged in audit even if the change is correct.

Run `grep -rn "deepseek-v4-flash"` across the repo. If it appears anywhere outside the five files above, do not edit it; list the locations in the PR description.

## 4. Safety

- No real API key in code, tests, logs or the PR. The session id is a random UUID and not a secret, but do not log it either.
- Never commit `env_vars/.env`.
- Run Python and tests inside the worker container, never on the host.
- Do not run `docker compose down` or any volume prune.

## 5. Acceptance criteria

- With `LLM_BASE_URL` host exactly `opencode.ai`, the client is built with `x-opencode-session` (a UUID4 generated once per adapter instance) and `User-Agent: cryptobot-worker/0.1`.
- For every other base URL, including lookalike hosts, the client is built without `default_headers`.
- The wire-level test proves the SDK sends both headers.
- `completions()` is byte-for-byte unchanged, and all pre-existing tests still pass.
- Both `.env.example` files default to `deepseek-v4.1-flash`, with no other line changed.
- The SOT has exactly the three edits above and no claim of live validation.
- The diff touches only the five files listed, and every commit on the branch belongs to this prompt.

## 6. Git and PR

- Create `fix/opencode-go-session-header` off `main` first. Do not push to `main` directly.
- Open the PR with `gh pr create`. The body must contain `Closes #41`.
- Write your own implementation summary in the PR description: what changed, the exact test command and its pasted output, and an explicit list of what you did **not** verify. State plainly that the live OpenCode API was not called. Do not write "verified" or "tested" for anything you did not actually run.

## 7. Docs to update

Only `docs/SOURCE_OF_TRUTH.md` (the three edits in 2.4) and the two `.env.example` files (2.3). No other documentation changes.
