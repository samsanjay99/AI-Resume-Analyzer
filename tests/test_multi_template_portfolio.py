"""
Test script to verify multi-template portfolio generator functionality
"""

import os
import sys
from utils.portfolio_generator import PortfolioGenerator

def test_template_availability():
    """Test that all templates are available and properly configured"""
    print("=" * 60)
    print("TEST 1: Template Availability")
    print("=" * 60)
    
    generator = PortfolioGenerator()
    templates = generator.get_available_templates()
    
    print(f"\n✓ Found {len(templates)} templates:")
    for key, info in templates.items():
        print(f"\n  Template: {key}")
        print(f"    Name: {info['name']}")
        print(f"    Description: {info['description']}")
        print(f"    Path: {info['path'] if info['path'] else '(root)'}")
        
        # Check if template directory exists
        if info['path']:
            template_path = os.path.join(generator.template_base_path, info['path'])
        else:
            template_path = generator.template_base_path
            
        if os.path.exists(template_path):
            print(f"    Status: ✓ Directory exists")
            
            # Check for required files
            index_html = os.path.join(template_path, 'index.html')
            main_css = os.path.join(template_path, 'main.css')
            
            if os.path.exists(index_html):
                print(f"    index.html: ✓ Found")
            else:
                print(f"    index.html: ✗ MISSING")
                
            if os.path.exists(main_css):
                print(f"    main.css: ✓ Found")
            else:
                print(f"    main.css: ✗ MISSING")
        else:
            print(f"    Status: ✗ DIRECTORY NOT FOUND")
    
    return len(templates) == 4

def test_placeholder_consistency():
    """Test that all templates use consistent placeholders"""
    print("\n" + "=" * 60)
    print("TEST 2: Placeholder Consistency")
    print("=" * 60)
    
    generator = PortfolioGenerator()
    templates = generator.get_available_templates()
    
    # Required placeholders that should be in all templates
    required_placeholders = [
        'FULL_NAME', 'FIRST_NAME', 'EMAIL', 'PHONE', 'LOCATION',
        'JOB_TITLE', 'PROFESSIONAL_SUMMARY', 'YEARS_EXPERIENCE',
        'PROJECT_COUNT', 'SKILL_COUNT', 'LINKEDIN_URL', 'GITHUB_URL',
        'TWITTER_URL', 'RESUME_DOWNLOAD_LINK'
    ]
    
    all_consistent = True
    
    for key, info in templates.items():
        print(f"\n  Checking template: {info['name']}")
        
        if info['path']:
            template_path = os.path.join(generator.template_base_path, info['path'])
        else:
            template_path = generator.template_base_path
            
        index_html = os.path.join(template_path, 'index.html')
        
        if os.path.exists(index_html):
            with open(index_html, 'r', encoding='utf-8') as f:
                content = f.read()
            
            missing = []
            for placeholder in required_placeholders:
                if f"{{{{{placeholder}}}}}" not in content:
                    missing.append(placeholder)
            
            if missing:
                print(f"    ✗ Missing placeholders: {', '.join(missing)}")
                all_consistent = False
            else:
                print(f"    ✓ All required placeholders present")
        else:
            print(f"    ✗ index.html not found")
            all_consistent = False
    
    return all_consistent

def test_template_structure():
    """Test that all templates have proper HTML structure"""
    print("\n" + "=" * 60)
    print("TEST 3: Template Structure")
    print("=" * 60)
    
    generator = PortfolioGenerator()
    templates = generator.get_available_templates()
    
    # Required sections
    required_sections = ['home', 'about', 'skills', 'experience', 'projects', 'contact']
    
    all_valid = True
    
    for key, info in templates.items():
        print(f"\n  Checking template: {info['name']}")
        
        if info['path']:
            template_path = os.path.join(generator.template_base_path, info['path'])
        else:
            template_path = generator.template_base_path
            
        index_html = os.path.join(template_path, 'index.html')
        
        if os.path.exists(index_html):
            with open(index_html, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for basic HTML structure
            has_doctype = '<!DOCTYPE html>' in content
            has_html_tag = '<html' in content
            has_head = '<head>' in content
            has_body = '<body>' in content
            
            print(f"    DOCTYPE: {'✓' if has_doctype else '✗'}")
            print(f"    HTML tag: {'✓' if has_html_tag else '✗'}")
            print(f"    HEAD section: {'✓' if has_head else '✗'}")
            print(f"    BODY section: {'✓' if has_body else '✗'}")
            
            # Check for sections
            missing_sections = []
            for section in required_sections:
                if f'id="{section}"' not in content and f"id='{section}'" not in content:
                    missing_sections.append(section)
            
            if missing_sections:
                print(f"    ✗ Missing sections: {', '.join(missing_sections)}")
                all_valid = False
            else:
                print(f"    ✓ All required sections present")
                
            if not (has_doctype and has_html_tag and has_head and has_body):
                all_valid = False
        else:
            print(f"    ✗ index.html not found")
            all_valid = False
    
    return all_valid

def test_css_files():
    """Test that all templates have valid CSS files"""
    print("\n" + "=" * 60)
    print("TEST 4: CSS Files")
    print("=" * 60)
    
    generator = PortfolioGenerator()
    templates = generator.get_available_templates()
    
    all_valid = True
    
    for key, info in templates.items():
        print(f"\n  Checking template: {info['name']}")
        
        if info['path']:
            template_path = os.path.join(generator.template_base_path, info['path'])
        else:
            template_path = generator.template_base_path
            
        main_css = os.path.join(template_path, 'main.css')
        
        if os.path.exists(main_css):
            file_size = os.path.getsize(main_css)
            print(f"    ✓ main.css found ({file_size:,} bytes)")
            
            # Check if CSS is not empty
            if file_size < 100:
                print(f"    ⚠ Warning: CSS file seems too small")
                all_valid = False
        else:
            print(f"    ✗ main.css not found")
            all_valid = False
    
    return all_valid

def test_assets_directory():
    """Test that templates have assets directories"""
    print("\n" + "=" * 60)
    print("TEST 5: Assets Directory")
    print("=" * 60)
    
    generator = PortfolioGenerator()
    templates = generator.get_available_templates()
    
    for key, info in templates.items():
        print(f"\n  Checking template: {info['name']}")
        
        if info['path']:
            template_path = os.path.join(generator.template_base_path, info['path'])
        else:
            template_path = generator.template_base_path
            
        assets_path = os.path.join(template_path, 'assets')
        
        if os.path.exists(assets_path):
            print(f"    ✓ assets/ directory exists")
        else:
            print(f"    ⚠ assets/ directory not found (optional)")
    
    return True

def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "=" * 60)
    print("MULTI-TEMPLATE PORTFOLIO GENERATOR TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Template Availability", test_template_availability),
        ("Placeholder Consistency", test_placeholder_consistency),
        ("Template Structure", test_template_structure),
        ("CSS Files", test_css_files),
        ("Assets Directory", test_assets_directory)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' failed with error: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All tests passed! Multi-template system is ready.")
        return True
    else:
        print(f"\n  ⚠ {total - passed} test(s) failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
