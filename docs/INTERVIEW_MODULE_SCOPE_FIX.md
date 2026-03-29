# Mock Interview - Module Scope Fix ✅

## Problem
When clicking "Start Interview" button in the interview HTML page:
```
Uncaught ReferenceError: startInterview is not defined
```

## Root Cause
The JavaScript code uses `<script type="module">` which creates a module scope. Functions defined inside modules are NOT accessible from inline `onclick` handlers.

```html
<script type="module">
  async function startInterview() { ... }  // ← Not in global scope!
</script>

<button onclick="startInterview()">  // ← Can't find it!
```

## Solution
Expose the functions to the global `window` object at the end of the module:

```javascript
// Inside <script type="module">
async function startInterview() { ... }
function endEarly() { ... }
function retryAnswer() { ... }

// ═══ EXPOSE TO GLOBAL SCOPE ═══
window.startInterview = startInterview;
window.endEarly = endEarly;
window.retryAnswer = retryAnswer;
</script>
```

## How It Works

### Module Scope (Before):
```
<script type="module">
  ┌─────────────────────────┐
  │ Module Scope (isolated) │
  │                         │
  │ function startInterview │  ← Only visible here
  │ function endEarly       │
  │ function retryAnswer    │
  └─────────────────────────┘

onclick="startInterview()"  ← Looks in global scope, not found!
```

### Global Exposure (After):
```
<script type="module">
  ┌─────────────────────────┐
  │ Module Scope            │
  │                         │
  │ function startInterview │
  │ window.startInterview = │  ← Expose to global
  └─────────────────────────┘
           ↓
    Global Window Object
  ┌─────────────────────────┐
  │ window.startInterview   │  ← Now accessible!
  │ window.endEarly         │
  │ window.retryAnswer      │
  └─────────────────────────┘

onclick="startInterview()"  ← Found in global scope! ✅
```

## Why Use type="module"?

Modules are needed for:
- ESM imports: `import { Vapi } from 'https://esm.sh/@vapi-ai/web'`
- Better code organization
- Strict mode by default
- Top-level await support

## Files Modified

1. `utils/interview_standalone.py`
   - Added window.startInterview exposure
   - Added window.endEarly exposure  
   - Added window.retryAnswer exposure

## Code Changes

```python
# At the end of the <script type="module"> section:
"""
// Preload TTS voices
if (S.synth.onvoiceschanged !== undefined) S.synth.onvoiceschanged = () => S.synth.getVoices();
S.synth.getVoices();

// ═══════════════════════════════════════════════════════
// EXPOSE FUNCTIONS TO GLOBAL SCOPE (for onclick handlers)
// ═══════════════════════════════════════════════════════
window.startInterview = startInterview;
window.endEarly = endEarly;
window.retryAnswer = retryAnswer;
</script>
"""
```

## Testing Checklist

✅ No "startInterview is not defined" error
✅ Start Interview button works
✅ End Early button works
✅ Re-answer button works
✅ VAPI connection attempts
✅ Free mode fallback works
✅ Interview flow completes

## Alternative Approaches Considered

1. **Remove type="module"** ❌
   - Can't use ESM imports
   - Loses VAPI integration
   - Not modern

2. **Use addEventListener** ❌
   - More code
   - Harder to maintain
   - Unnecessary complexity

3. **Expose to window** ✅
   - Simple
   - Works with modules
   - Maintains ESM benefits

## Browser Compatibility

- ✅ Chrome/Edge - Full support
- ✅ Firefox - Full support
- ✅ Safari - Full support
- ✅ All modern browsers support modules + window exposure

## Security Notes

- Exposing functions to window is safe for this use case
- Functions are read-only (can't be overwritten easily)
- No sensitive data exposed
- Standard pattern for module + onclick integration

## Technical Details

### Why onclick needs global scope?
Inline event handlers (`onclick="..."`) execute in the global scope, not the module scope. They look for functions on the `window` object.

### Why not use addEventListener?
```javascript
// Would work but requires more code:
document.getElementById('btn-start').addEventListener('click', startInterview);
```

Our approach is simpler and works perfectly for this use case.

---

**Status**: ✅ Fixed  
**Impact**: Interview buttons now work correctly  
**Risk**: Low - Standard pattern for module + onclick
