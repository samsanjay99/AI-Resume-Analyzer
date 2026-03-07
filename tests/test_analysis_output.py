"""Test to check if analysis is returning proper output"""
import sys
sys.path.append('.')

from utils.ai_resume_analyzer import AIResumeAnalyzer

print("=" * 70)
print("TESTING ANALYSIS OUTPUT")
print("=" * 70)

# Create analyzer
analyzer = AIResumeAnalyzer()

# Test with a simple resume text
test_resume = """
John Doe
Software Engineer
Email: john@example.com
Phone: 123-456-7890

EXPERIENCE:
- 3 years as Python Developer
- Built web applications using Django

SKILLS:
Python, Django, JavaScript, SQL

EDUCATION:
BS Computer Science, 2020
"""

print("\n1. Testing Smart Analysis...")
try:
    result = analyzer.analyze_resume(
        resume_text=test_resume,
        job_role="Software Engineer",
        model="🚀 Smart Analysis"
    )
    
    if "error" in result:
        print(f"   ❌ Error: {result['error']}")
    else:
        print(f"   ✅ Analysis returned")
        print(f"   - Resume Score: {result.get('resume_score', 'N/A')}")
        print(f"   - ATS Score: {result.get('ats_score', 'N/A')}")
        print(f"   - Model Used: {result.get('model_used', 'N/A')}")
        
        analysis_text = result.get('analysis', '')
        if analysis_text:
            print(f"   - Analysis Length: {len(analysis_text)} characters")
            print(f"   - First 200 chars: {analysis_text[:200]}...")
        else:
            print("   ❌ Analysis text is EMPTY!")
            
except Exception as e:
    print(f"   ❌ Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n2. Testing Deep Analysis...")
try:
    result = analyzer.analyze_resume(
        resume_text=test_resume,
        job_role="Software Engineer",
        model="🔬 Deep Analysis"
    )
    
    if "error" in result:
        print(f"   ❌ Error: {result['error']}")
    else:
        print(f"   ✅ Analysis returned")
        print(f"   - Resume Score: {result.get('resume_score', 'N/A')}")
        print(f"   - ATS Score: {result.get('ats_score', 'N/A')}")
        print(f"   - Model Used: {result.get('model_used', 'N/A')}")
        
        analysis_text = result.get('analysis', '')
        if analysis_text:
            print(f"   - Analysis Length: {len(analysis_text)} characters")
            print(f"   - First 200 chars: {analysis_text[:200]}...")
        else:
            print("   ❌ Analysis text is EMPTY!")
            
except Exception as e:
    print(f"   ❌ Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
