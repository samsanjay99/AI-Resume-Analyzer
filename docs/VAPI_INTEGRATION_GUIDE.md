# VAPI Integration Guide — How We Made It Work

## The Problem in One Line

VAPI/Daily.co requires a **real HTTP origin** to function. Streamlit cannot provide one natively.

---

## Why VAPI Kept Failing — The Full Journey

### Attempt 1: `components.html()`
Streamlit's `components.html()` renders inside a sandboxed `about:srcdoc` iframe.
- `window.location.origin` inside that iframe returns `"null"`
- Daily.co's internal postMessage calls require a real target origin
- Result: `daily-error` → `daily-call-join-error` → `start-method-error`

### Attempt 2: `data:text/html;base64,...` URLs
Tried encoding the HTML as a base64 data URL and opening it in a new tab.
- Data URLs also have `null` origin
- `localStorage` is blocked on null origins
- Result: Same VAPI errors, plus `startInterview is not defined` because `<script type="module">` scoping doesn't expose functions to `onclick` handlers

### Attempt 3: Streamlit `enableStaticServing = true`
Set `enableStaticServing = true` in `.streamlit/config.toml`, saved HTML to `./static/`, used `st.link_button("/app/static/interview_X.html")`.
- On Windows locally, `st.link_button` with a relative path opened `file:///C:/...` instead of `http://localhost:8501/...`
- Even with the correct URL, Streamlit's static file server sends `.html` files as `Content-Type: text/plain`
- Browser renders raw HTML source code instead of executing it
- Result: Blank page showing raw HTML text

### Attempt 4: JS button with `window.location.origin`
Tried building the URL in JavaScript inside `components.html()`.
- `window.location.origin` inside `about:srcdoc` iframe = `"null"`
- URL became `http://localhost:8501/null/app/static/interview_X.html`
- Result: Streamlit served its own React app for that path, breaking everything

### Final Fix: Mini Python HTTP Server ✅

The root cause: **no component of Streamlit can serve `.html` files with `text/html` content-type**.

Solution: spin up a tiny `ThreadingHTTPServer` on `127.0.0.1:8765` that serves the `static/` directory with correct MIME types.

---

## The Working Architecture

```
User clicks "Open Interview"
        │
        ▼
st.link_button → http://127.0.0.1:8765/interview_25.html
        │
        ▼
InterviewHandler (Python ThreadingHTTPServer)
  Content-Type: text/html; charset=utf-8  ← this is the key
        │
        ▼
Browser loads interview page at real HTTP origin
  window.location.origin = "http://127.0.0.1:8765"  ← VAPI works!
        │
        ▼
VAPI SDK loads via ESM: import Vapi from "https://esm.sh/@vapi-ai/web"
        │
        ▼
vapi.start(ASSISTANT_ID, { variableValues: {...} })
        │
        ▼
Interview runs (VAPI voice OR free browser STT/TTS fallback)
        │
        ▼
sendResults() → window.location.href = "http://localhost:8501/?iv_done=ID&iv_data=..."
        │
        ▼
Streamlit reads st.query_params → transitions to evaluation phase
```

---

## Files Changed / Created

### `utils/interview_server.py` (NEW)
The mini HTTP server. Key points:
- Uses Python's built-in `http.server.ThreadingHTTPServer` — no extra dependencies
- Runs as a **daemon thread** so it dies when Streamlit stops
- Singleton pattern: only one server instance ever starts (`_SERVER` global)
- Overrides `extensions_map` to force `text/html; charset=utf-8` for `.html` files
- Adds `Access-Control-Allow-Origin: *` header for VAPI cross-origin requests
- Suppresses request logs so Streamlit terminal stays clean
- Default port: `8765` (configurable via `INTERVIEW_HTTP_PORT` env var)

```python
def ensure_interview_server(directory: str | Path) -> str:
    # Returns "http://127.0.0.1:8765"
    # Starts server on first call, reuses on subsequent calls
```

### `utils/interview_standalone.py` (MODIFIED)
Generates the self-contained interview HTML page.

Key changes:
1. `streamlit_base_url` parameter is now **actually used** (was previously ignored)
2. `return_url_base` is computed from it and baked into the HTML at generation time
3. `sendResults()` JS function uses the baked-in URL instead of `window.location.origin`

Why bake it in: the interview page is served from port `8765`, so `window.location.origin` = `http://127.0.0.1:8765`. We need to redirect back to Streamlit on port `8501`, not back to the interview server.

```python
return_url_base = streamlit_base_url.rstrip("/") if streamlit_base_url else "http://localhost:8501"
```

In the JS:
```javascript
// Before (broken — pointed back to interview server):
const returnUrl = window.location.origin + '/?iv_done=' + IV_ID + '&iv_data=' + encoded;

// After (correct — points to Streamlit):
const returnUrl = 'http://localhost:8501/?iv_done=' + IV_ID + '&iv_data=' + encoded;
```

### `pages/mock_interview.py` — `render_live()` (MODIFIED)
1. Detects Streamlit base URL using `st.context.headers.get("Host")` — works locally and on Streamlit Cloud
2. Passes `streamlit_base_url` into `build_standalone_html()`
3. Calls `ensure_interview_server(static_dir)` to get `http://127.0.0.1:8765`
4. Builds `interview_url = f"{server_base}/{filename}"` — a real HTTP URL
5. Uses `st.link_button(interview_url)` — now opens a real HTTP page, not a file path

---

## VAPI SDK — Correct Import

Always use the ESM import, matching the working `test-vapi/app.html`:

```javascript
// In <script type="module">
const mod = await import('https://esm.sh/@vapi-ai/web');
const VapiClass = mod.default || mod.Vapi || mod;
const vapi = new VapiClass(VAPI_TOKEN);
```

Do NOT use `cdn.jsdelivr.net` — it serves the wrong module format.

---

## VAPI Credentials

| Variable | Value |
|---|---|
| `VAPI_WEB_TOKEN` | `YOUR_VAPI_WEB_TOKEN` |
| `VAPI_ASSISTANT_ID` | `YOUR_VAPI_ASSISTANT_ID` |

Set in `.env` locally. Set in Streamlit Cloud secrets for deployment.

---

## Free Voice Fallback

When VAPI fails (network error, quota, etc.), the page automatically falls back to:
- **TTS**: `window.speechSynthesis` (browser built-in)
- **STT**: `window.SpeechRecognition` / `window.webkitSpeechRecognition` (Chrome/Edge only)
- Smart silence detection: 3-second countdown bar, submits answer after pause
- If `SpeechRecognition` is not available (Firefox), shows an error and stops — does NOT loop through all questions automatically

---

## Results Flow (Interview → Streamlit)

The interview page sends results back to Streamlit via URL params:

```
http://localhost:8501/?iv_done=25&iv_data=[{"role":"user","content":"..."},...]
```

`render_live()` checks `st.query_params` on every render:
```python
params = st.query_params
if params.get("iv_done") == str(iv_id) and "iv_data" in params:
    transcript = json.loads(params["iv_data"])
    st.session_state.iv_transcript = transcript
    st.session_state.iv_phase = "evaluating"
    st.rerun()
```

The "Get My Results" button also manually triggers this check in case the auto-redirect didn't fire.

---

## Streamlit Cloud Deployment Notes

On Streamlit Cloud, port `8765` is **not publicly accessible** — the mini server only binds to `127.0.0.1` (localhost). This is fine because:
- The interview HTML is served to the user's browser
- The browser then makes requests to `127.0.0.1:8765` — but that's the **server's** localhost, not the user's

**This means the mini HTTP server approach only works locally.**

For Streamlit Cloud, the correct approach is to use a proper hosting solution for the HTML file, or use Streamlit's `enableStaticServing` with a workaround for the MIME type issue (e.g., serve via a CDN or a separate hosted page).

For now, the app works correctly in local development. Cloud deployment of the interview feature requires additional setup.

---

## Quick Reference — What Breaks VAPI

| Cause | Symptom |
|---|---|
| `about:srcdoc` iframe | `daily-error`, `daily-call-join-error` |
| `data:` URL | Same errors + null origin |
| `file:///` URL | Browser blocks mic access |
| Wrong MIME type (`text/plain`) | Raw HTML shown, JS never runs |
| `window.location.origin = "null"` | URL becomes `/null/app/static/...` |
| Wrong CDN for SDK | Module load errors |
| Return URL pointing to wrong port | Results never reach Streamlit |
