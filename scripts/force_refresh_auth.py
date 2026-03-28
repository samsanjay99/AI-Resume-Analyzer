"""
Force browser cache refresh for authentication pages
Run this after making UI changes to ensure styles are applied
"""
import time

print("=" * 60)
print("FORCE REFRESH AUTHENTICATION UI")
print("=" * 60)
print()
print("To see the new sunset theme with proper styling:")
print()
print("1. STOP the Streamlit server (Ctrl+C)")
print("2. Clear browser cache:")
print("   - Chrome/Edge: Ctrl+Shift+Delete → Clear cached images and files")
print("   - Or use Incognito/Private mode")
print("3. Restart Streamlit:")
print("   streamlit run app.py")
print("4. Hard refresh the page:")
print("   - Windows: Ctrl+F5 or Ctrl+Shift+R")
print("   - Mac: Cmd+Shift+R")
print()
print("Expected result:")
print("✓ Sunset gradient background (#ffd1b3 → #ffb3ba → #d4a5d4)")
print("✓ Transparent inputs with white bottom border only")
print("✓ White title text (not cyan)")
print("✓ Centered 370px glass card")
print("✓ No scrolling")
print("✓ Flying birds, sun, particles, mountains")
print()
print("=" * 60)
