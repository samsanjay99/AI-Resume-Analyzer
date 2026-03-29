"""Test API calls directly"""
import sys
sys.path.append('.')

from utils.ai_resume_analyzer import AIResumeAnalyzer

print("Testing Direct API Calls")
print("=" * 60)

analyzer = AIResumeAnalyzer()

test_resume = "John Doe, Software Engineer with 3 years Python experience"

print("\n1. Testing A4F API...")
if analyzer.a4f_api_key:
    result = analyzer.analyze_resume_with_a4f(
        prompt_text=f"Analyze this resume: {test_resume}",
        job_role="Software Engineer",
        model_name="provider-6/llama-4-scout-17b-16e-instruct"
    )
    print(f"Result keys: {result.keys()}")
    if "error" in result:
        print(f"ERROR: {result['error']}")
    else:
        analysis = result.get('analysis', '')
        print(f"Analysis length: {len(analysis)}")
        if analysis:
            print(f"First 200 chars: {analysis[:200]}")
        else:
            print("Analysis is EMPTY!")
else:
    print("A4F API key not configured")

print("\n2. Testing Google Gemini API...")
if analyzer.google_api_key:
    result = analyzer.analyze_resume_with_gemini(
        prompt_text=f"Analyze this resume: {test_resume}",
        job_role="Software Engineer"
    )
    print(f"Result keys: {result.keys()}")
    if "error" in result:
        print(f"ERROR: {result['error']}")
    else:
        analysis = result.get('analysis', '')
        print(f"Analysis length: {len(analysis)}")
        if analysis:
            print(f"First 200 chars: {analysis[:200]}")
        else:
            print("Analysis is EMPTY!")
else:
    print("Google API key not configured")

print("\n" + "=" * 60)
