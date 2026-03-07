"""Simple test to check if analysis returns output"""
import sys
sys.path.append('.')

from utils.ai_resume_analyzer import AIResumeAnalyzer

print("Testing Analysis Output")
print("=" * 60)

analyzer = AIResumeAnalyzer()

test_resume = """
John Doe
Software Engineer
Email: john@example.com

EXPERIENCE:
- 3 years as Python Developer

SKILLS:
Python, Django, JavaScript
"""

print("\nTesting Smart Analysis...")
result = analyzer.analyze_resume(
    resume_text=test_resume,
    job_role="Software Engineer",
    model="Smart Analysis"
)

if "error" in result:
    print(f"ERROR: {result['error']}")
else:
    print("SUCCESS: Analysis completed")
    print(f"Resume Score: {result.get('resume_score', 0)}")
    print(f"ATS Score: {result.get('ats_score', 0)}")
    
    analysis_text = result.get('analysis', '')
    if analysis_text:
        print(f"Analysis Length: {len(analysis_text)} chars")
        print(f"\nFirst 300 characters:")
        print(analysis_text[:300])
    else:
        print("WARNING: Analysis text is EMPTY!")

print("\n" + "=" * 60)
