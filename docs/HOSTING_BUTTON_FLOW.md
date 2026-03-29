# Portfolio Hosting Button - Execution Flow Diagram

## The Problem (Before Fix)
```
User Action: Click "Host Portfolio Online"
     ↓
Page Reruns (Streamlit behavior)
     ↓
Session state cleared (no persistence)
     ↓
❌ Portfolio preview disappears
❌ Back to upload screen
❌ No deployment result shown
```

## The Solution (After Fix)
```
═══════════════════════════════════════════════════════════════
STEP 1: Generate Portfolio
═══════════════════════════════════════════════════════════════
User clicks "Generate Portfolio"
     ↓
Portfolio generated
     ↓
st.session_state.portfolio_result = {
    'html_content': '...',
    'portfolio_data': {...},
    'zip_path': '...',
    'success': True
}
     ↓
✅ Preview displays (reads from session state)

═══════════════════════════════════════════════════════════════
STEP 2: Click Host Button (Page Reruns)
═══════════════════════════════════════════════════════════════
User clicks "Host Portfolio Online"
     ↓
Page reruns (normal Streamlit behavior)
     ↓
Code checks: if 'portfolio_result' in st.session_state
     ↓
✅ YES! Portfolio data still there
     ↓
Preview displays again (from session state)
     ↓
Code reaches: if st.button("Host Portfolio Online")
     ↓
Button was clicked, so condition is True
     ↓
with st.spinner("Deploying..."):
    deploy_result = deployer.deploy_portfolio(...)
    st.session_state.deployment_result = deploy_result
     ↓
Deployment completes
     ↓
Code continues to next section...
     ↓
Code checks: if 'deployment_result' in st.session_state
     ↓
✅ YES! Deployment result just stored
     ↓
Display success message with URL
     ↓
st.balloons()

═══════════════════════════════════════════════════════════════
STEP 3: After Deployment (Subsequent Reruns)
═══════════════════════════════════════════════════════════════
Any interaction (scroll, click, etc.)
     ↓
Page reruns
     ↓
Code checks: if 'portfolio_result' in st.session_state
     ↓
✅ YES! Still there
     ↓
Preview displays
     ↓
Code checks: if 'deployment_result' in st.session_state
     ↓
✅ YES! Still there
     ↓
Success message displays
     ↓
✅ Both preview AND deployment result visible

═══════════════════════════════════════════════════════════════
STEP 4: Clear Deployment Message (Optional)
═══════════════════════════════════════════════════════════════
User clicks "Got it! Clear this message"
     ↓
del st.session_state.deployment_result
     ↓
st.rerun()
     ↓
Page reruns
     ↓
Code checks: if 'portfolio_result' in st.session_state
     ↓
✅ YES! Still there
     ↓
Preview displays
     ↓
Code checks: if 'deployment_result' in st.session_state
     ↓
❌ NO! Was deleted
     ↓
Success message doesn't display
     ↓
✅ Only preview visible (clean state)
```

## Session State Contents at Each Step

### After Generate Portfolio:
```python
st.session_state = {
    'portfolio_result': {
        'html_content': '<html>...</html>',
        'portfolio_data': {'FULL_NAME': 'John Doe', ...},
        'zip_path': 'generated_portfolios/...',
        'success': True,
        'user_id': 'user_20260223_...'
    }
}
```

### After Hosting (Success):
```python
st.session_state = {
    'portfolio_result': {  # Still here!
        'html_content': '<html>...</html>',
        'portfolio_data': {'FULL_NAME': 'John Doe', ...},
        'zip_path': 'generated_portfolios/...',
        'success': True,
        'user_id': 'user_20260223_...'
    },
    'deployment_result': {  # New!
        'success': True,
        'repo_name': 'portfolio-john-doe-20260223...',
        'repo_url': 'https://github.com/AI-resume-portfolios/...',
        'live_url': 'https://ai-resume-portfolios.github.io/...',
        'message': 'Portfolio deployed successfully!'
    },
    'balloons_shown': True  # Prevent duplicate balloons
}
```

### After Clearing Message:
```python
st.session_state = {
    'portfolio_result': {  # Still here!
        'html_content': '<html>...</html>',
        'portfolio_data': {'FULL_NAME': 'John Doe', ...},
        'zip_path': 'generated_portfolios/...',
        'success': True,
        'user_id': 'user_20260223_...'
    }
    # deployment_result deleted
    # balloons_shown deleted
}
```

## Key Principles

### 1. Session State is Persistent
- Data stored in `st.session_state` survives page reruns
- This is THE way to maintain state in Streamlit

### 2. Button Clicks Cause Reruns
- Every button click triggers a full page rerun
- This is normal and expected Streamlit behavior
- Can't be prevented, must be embraced

### 3. Conditional Rendering
- Use `if 'key' in st.session_state` to check for data
- Display content based on what's in session state
- Content appears/disappears based on session state

### 4. Separation of Concerns
```python
# Section 1: Button and action
if st.button("Do Something"):
    result = do_something()
    st.session_state.result = result  # Store it!

# Section 2: Display result (separate)
if 'result' in st.session_state:
    display_result(st.session_state.result)
```

## Why This Pattern Works

1. **Generate Portfolio** stores data → Preview persists
2. **Host Button** stores deployment result → Both persist
3. **Clear Button** removes deployment → Preview still persists
4. **Clean Files** removes portfolio → Back to upload screen

Each action modifies session state appropriately, and the UI reflects the current session state on every rerun.

## Comparison with Generate Portfolio Button

Both buttons follow the EXACT same pattern:

| Aspect | Generate Portfolio | Host Portfolio |
|--------|-------------------|----------------|
| Button Click | Triggers generation | Triggers deployment |
| Processing | `with st.spinner()` | `with st.spinner()` |
| Store Result | `st.session_state.portfolio_result` | `st.session_state.deployment_result` |
| Display | Check session state → show preview | Check session state → show URL |
| Persistence | Survives reruns | Survives reruns |
| Clear | "Clear Generated Files" button | "Got it!" button |

This consistency makes the UX predictable and reliable!
