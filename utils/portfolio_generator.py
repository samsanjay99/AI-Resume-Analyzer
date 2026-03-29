import os
import shutil
import zipfile
import tempfile
import re
import datetime as dt
from typing import Dict, List, Optional, Any
import json
import sys
import importlib.util

# Import the placeholders configuration
try:
    from config.portfolio_placeholders import (
        get_all_placeholders, get_placeholder_value, PERSONAL_DATA, 
        DEFAULT_DATA, SKILLS_DATA, EXPERIENCE_DATA, EDUCATION_DATA, PROJECTS_DATA
    )
except ImportError:
    print("Warning: Could not import portfolio_placeholders config. Using fallback defaults.")
    # Fallback function if config is not available
    def get_all_placeholders(extracted_data=None, use_personal_data=True):
        return {
            'FULL_NAME': 'Professional Developer',
            'FIRST_NAME': 'Professional',
            'EMAIL': 'contact@example.com',
            'JOB_TITLE': 'Software Developer',
            'PROFESSIONAL_SUMMARY': 'Passionate software developer with expertise in modern technologies.',
        }

class PortfolioGenerator:
    def __init__(self):
        self.template_base_path = "resume-to-portfoliov2"
        self.generated_portfolios_path = "generated_portfolios"
        self.temp_portfolios_path = "temp_portfolios"
        
        # Available templates
        self.available_templates = {
            'tech-style': {
                'name': 'Tech Style',
                'description': 'Modern tech portfolio with dark theme',
                'path': '',  # Root template
                'preview_image': 'assets/tech-preview.png'
            },
            'dark-developer': {
                'name': 'Dark Developer',
                'description': 'Sleek dark theme for developers',
                'path': 'dark-developer-portfolio',
                'preview_image': 'assets/dark-preview.png'
            },
            'creative': {
                'name': 'Creative Portfolio',
                'description': 'Creative and colorful design',
                'path': 'creative-portfolio',
                'preview_image': 'assets/creative-preview.png'
            },
            'professional': {
                'name': 'Professional',
                'description': 'Clean professional layout',
                'path': 'professional-portfolio',
                'preview_image': 'assets/professional-preview.png'
            }
        }
        
        # Ensure directories exist
        os.makedirs(self.generated_portfolios_path, exist_ok=True)
        os.makedirs(self.temp_portfolios_path, exist_ok=True)
        
        # Auto-cleanup old temp files on initialization (older than 1 hour)
        self._cleanup_old_temp_files()
        
        # AI prompt for filling missing data
        self.ai_prompt_template = """
You are given resume content. Your task is to convert this resume into a structured JSON object following the exact placeholder schema below.

If a field is not explicitly mentioned in the resume, you must generate a reasonable value based on the resume content (e.g., infer a job title, create a short professional summary, or estimate skills from context). Only if nothing can be inferred at all, use a generic fallback value.

Return only valid JSON in the required format.

Schema (placeholders to fill):

Basic Information:
- FULL_NAME → Full name of the person
- FIRST_NAME → First name (auto-extracted from full name)
- EMAIL → Email address
- PHONE → Phone number
- LOCATION → Location/address

Professional Information:
- JOB_TITLE → Current job title
- CURRENT_POSITION → Current position
- PROFESSIONAL_SUMMARY → Professional summary text
- ABOUT_DESCRIPTION → About section description

Social Links:
- LINKEDIN_URL
- GITHUB_URL
- TWITTER_URL
- RESUME_DOWNLOAD_LINK

Statistics:
- YEARS_EXPERIENCE
- PROJECT_COUNT
- SKILL_COUNT

Education:
- EDUCATION_DEGREE → Latest/highest degree
- EDUCATION_HISTORY → Full education history formatted as HTML

Skills:
- PRIMARY_SKILLS → List of top skills
- PROGRAMMING_LANGUAGES → Skills section in HTML
- FRAMEWORKS → Skills section in HTML
- DATABASES_TOOLS → Skills section in HTML
- CLOUD_DEVOPS → Skills section in HTML

Content:
- CONTACT_MESSAGE → Contact section message
- WORK_EXPERIENCE → Work experience section formatted as HTML
- PROJECTS_LIST → Projects section formatted as HTML

Typewriter Effect Titles:
- SECONDARY_TITLE_1
- SECONDARY_TITLE_2
- SECONDARY_TITLE_3

Resume Content:
{resume_content}

Return the JSON object with all fields filled based on the resume content above.
"""
    
    def get_available_templates(self) -> Dict[str, Dict[str, str]]:
        """Get all available portfolio templates"""
        return self.available_templates
    
    def generate_portfolio_with_ai(self, resume_text: str, ai_analyzer, user_id: str = None, template_style: str = 'tech-style') -> Dict[str, Any]:
        """
        Generate portfolio using AI to fill missing data intelligently.
        
        Flow:
        1. Keep raw template untouched
        2. Create temporary copy for generation
        3. Use AI to fill missing fields with intelligent inference
        4. Preview with iframe using srcdoc
        5. Download as zip
        6. Auto-cleanup temp files after ZIP creation
        
        Args:
            resume_text: Resume content as text
            ai_analyzer: AI analyzer instance
            user_id: User identifier
            template_style: Template style key (tech-style, dark-developer, creative, professional)
        """
        temp_portfolio_path = None
        try:
            if not user_id:
                user_id = f"user_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Validate template style
            if template_style not in self.available_templates:
                template_style = 'tech-style'  # Default fallback
            
            # Step 1: Extract basic data from resume
            extracted_data = self.extract_basic_resume_data(resume_text)
            
            # Step 2: Use AI to fill missing fields intelligently
            ai_filled_data = self.fill_missing_data_with_ai(resume_text, extracted_data, ai_analyzer)
            
            # Step 3: Create temporary copy of template
            temp_portfolio_path = self.create_temp_portfolio_copy(user_id, template_style)
            
            # Step 4: Replace placeholders in temp copy
            self.replace_placeholders_in_temp_copy(temp_portfolio_path, ai_filled_data)
            
            # Step 5: Generate preview HTML
            preview_html = self.generate_preview_html(temp_portfolio_path)
            
            # Step 6: Create zip file
            zip_path = self.create_portfolio_zip(temp_portfolio_path, user_id, ai_filled_data.get('FULL_NAME', 'Portfolio'))
            
            # Step 7: Clean up temp files immediately after ZIP creation
            # This prevents storage accumulation in cloud deployments
            self.cleanup_temp_portfolio(user_id)
            
            return {
                'success': True,
                'message': 'Portfolio generated successfully',
                'html_content': preview_html,
                'zip_path': zip_path,
                'user_id': user_id,
                'portfolio_data': ai_filled_data,
                'temp_path': None,  # Already cleaned up
                'template_style': template_style
            }
            
        except Exception as e:
            print(f"Error generating portfolio with AI: {str(e)}")
            # Clean up temp files even on error
            if temp_portfolio_path and user_id:
                self.cleanup_temp_portfolio(user_id)
            return {
                'success': False,
                'message': f'Portfolio generation failed: {str(e)}',
                'error': str(e)
            }
    
    def extract_basic_resume_data(self, resume_text: str) -> Dict[str, Any]:
        """Extract basic data from resume text using simple parsing"""
        try:
            # Basic extraction using regex patterns
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
            
            email = re.search(email_pattern, resume_text)
            phone = re.search(phone_pattern, resume_text)
            
            # Extract name from first few lines
            lines = resume_text.split('\n')[:5]
            name = None
            for line in lines:
                line = line.strip()
                if line and not any(keyword in line.lower() for keyword in ['resume', 'cv', 'email', 'phone', '@']):
                    words = line.split()
                    if 2 <= len(words) <= 4 and all(word[0].isupper() for word in words if word.isalpha()):
                        name = line
                        break
            
            return {
                'raw_text': resume_text,
                'extracted_email': email.group() if email else None,
                'extracted_phone': phone.group() if phone else None,
                'extracted_name': name,
                'text_length': len(resume_text)
            }
            
        except Exception as e:
            print(f"Error in basic extraction: {str(e)}")
            return {'raw_text': resume_text}
    
    def fill_missing_data_with_ai(self, resume_text: str, extracted_data: Dict, ai_analyzer) -> Dict[str, Any]:
        """Use AI to intelligently fill missing resume fields"""
        try:
            # Check if AI analyzer has API key configured
            if not hasattr(ai_analyzer, 'google_api_key') or not ai_analyzer.google_api_key:
                print("No Google API key configured, using fallback data generation")
                return self.create_fallback_data(extracted_data)
            
            # Prepare prompt with resume content
            prompt = self.ai_prompt_template.format(resume_content=resume_text)
            
            # Call AI analyzer to get structured data
            ai_response = ai_analyzer.analyze_resume_with_gemini(prompt)
            
            if 'analysis' in ai_response:
                # Try to extract JSON from AI response
                analysis_text = ai_response['analysis']
                
                # Look for JSON in the response
                json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                if json_match:
                    try:
                        ai_data = json.loads(json_match.group())
                        return self.validate_and_clean_ai_data(ai_data, extracted_data)
                    except json.JSONDecodeError:
                        print("Failed to parse AI JSON response, using fallback")
                
            # Fallback to manual extraction if AI fails
            return self.create_fallback_data(extracted_data)
            
        except Exception as e:
            print(f"Error filling data with AI: {str(e)}")
            return self.create_fallback_data(extracted_data)
    
    def validate_and_clean_ai_data(self, ai_data: Dict, extracted_data: Dict) -> Dict[str, Any]:
        """Validate and clean AI-generated data"""
        try:
            # Ensure all required fields exist with fallbacks
            validated_data = {
                'FULL_NAME': ai_data.get('FULL_NAME', extracted_data.get('extracted_name', 'Professional Developer')),
                'FIRST_NAME': ai_data.get('FIRST_NAME', ai_data.get('FULL_NAME', 'Professional').split()[0]),
                'EMAIL': ai_data.get('EMAIL', extracted_data.get('extracted_email', 'contact@example.com')),
                'PHONE': ai_data.get('PHONE', extracted_data.get('extracted_phone', '+1 (555) 123-4567')),
                'LOCATION': ai_data.get('LOCATION', 'Available Worldwide'),
                'JOB_TITLE': ai_data.get('JOB_TITLE', 'Software Developer'),
                'CURRENT_POSITION': ai_data.get('CURRENT_POSITION', ai_data.get('JOB_TITLE', 'Software Developer')),
                'PROFESSIONAL_SUMMARY': ai_data.get('PROFESSIONAL_SUMMARY', 'Passionate professional with expertise in technology and innovation.'),
                'ABOUT_DESCRIPTION': ai_data.get('ABOUT_DESCRIPTION', ai_data.get('PROFESSIONAL_SUMMARY', 'Dedicated to delivering high-quality solutions.')),
                'LINKEDIN_URL': ai_data.get('LINKEDIN_URL', 'https://linkedin.com/in/yourprofile'),
                'GITHUB_URL': ai_data.get('GITHUB_URL', 'https://github.com/yourusername'),
                'TWITTER_URL': ai_data.get('TWITTER_URL', 'https://twitter.com/yourusername'),
                'RESUME_DOWNLOAD_LINK': ai_data.get('RESUME_DOWNLOAD_LINK', '#'),
                'YEARS_EXPERIENCE': str(ai_data.get('YEARS_EXPERIENCE', '2')),
                'PROJECT_COUNT': str(ai_data.get('PROJECT_COUNT', '5')),
                'SKILL_COUNT': str(ai_data.get('SKILL_COUNT', '8')),
                'EDUCATION_DEGREE': ai_data.get('EDUCATION_DEGREE', 'Bachelor\'s Degree'),
                'EDUCATION_HISTORY': ai_data.get('EDUCATION_HISTORY', '<div class="education-item"><h4>Bachelor\'s Degree</h4><p>University Name - 2020</p></div>'),
                'PRIMARY_SKILLS': ai_data.get('PRIMARY_SKILLS', 'Problem Solving, Communication, Teamwork'),
                'PROGRAMMING_LANGUAGES': ai_data.get('PROGRAMMING_LANGUAGES', '<ul><li>Python - Intermediate</li><li>JavaScript - Intermediate</li></ul>'),
                'FRAMEWORKS': ai_data.get('FRAMEWORKS', '<ul><li>React - Beginner</li><li>Node.js - Beginner</li></ul>'),
                'DATABASES_TOOLS': ai_data.get('DATABASES_TOOLS', '<ul><li>MySQL - Beginner</li><li>Git - Intermediate</li></ul>'),
                'CLOUD_DEVOPS': ai_data.get('CLOUD_DEVOPS', '<ul><li>AWS - Beginner</li><li>Docker - Beginner</li></ul>'),
                'CONTACT_MESSAGE': ai_data.get('CONTACT_MESSAGE', 'I am open to exciting new opportunities. Let\'s connect!'),
                'WORK_EXPERIENCE': ai_data.get('WORK_EXPERIENCE', '<div class="experience-item"><h4>Professional Experience</h4><p>Contributed to various projects and initiatives.</p></div>'),
                'PROJECTS_LIST': ai_data.get('PROJECTS_LIST', '<div class="project-item"><h4>Portfolio Project</h4><p>A showcase of technical skills and creativity.</p></div>'),
                'SECONDARY_TITLE_1': ai_data.get('SECONDARY_TITLE_1', 'Problem Solver'),
                'SECONDARY_TITLE_2': ai_data.get('SECONDARY_TITLE_2', 'Creative Thinker'),
                'SECONDARY_TITLE_3': ai_data.get('SECONDARY_TITLE_3', 'Team Player')
            }
            
            # Clean and validate URLs
            for url_field in ['LINKEDIN_URL', 'GITHUB_URL', 'TWITTER_URL']:
                url = validated_data[url_field]
                if url and not url.startswith('http'):
                    validated_data[url_field] = f"https://{url}"
            
            return validated_data
            
        except Exception as e:
            print(f"Error validating AI data: {str(e)}")
            return self.create_fallback_data(extracted_data)
    
    def create_fallback_data(self, extracted_data: Dict) -> Dict[str, Any]:
        """Create fallback data when AI processing fails"""
        name = extracted_data.get('extracted_name', 'Professional Developer')
        first_name = name.split()[0] if name else 'Professional'
        
        return {
            'FULL_NAME': name,
            'FIRST_NAME': first_name,
            'EMAIL': extracted_data.get('extracted_email', 'contact@example.com'),
            'PHONE': extracted_data.get('extracted_phone', '+1 (555) 123-4567'),
            'LOCATION': 'Available Worldwide',
            'JOB_TITLE': 'Software Developer',
            'CURRENT_POSITION': 'Software Developer',
            'PROFESSIONAL_SUMMARY': 'Passionate professional with expertise in technology and innovation.',
            'ABOUT_DESCRIPTION': 'Dedicated to delivering high-quality solutions and continuous learning.',
            'LINKEDIN_URL': 'https://linkedin.com/in/yourprofile',
            'GITHUB_URL': 'https://github.com/yourusername',
            'TWITTER_URL': 'https://twitter.com/yourusername',
            'RESUME_DOWNLOAD_LINK': '#',
            'YEARS_EXPERIENCE': '2',
            'PROJECT_COUNT': '5',
            'SKILL_COUNT': '8',
            'EDUCATION_DEGREE': 'Bachelor\'s Degree',
            'EDUCATION_HISTORY': '<div class="education-item"><h4>Bachelor\'s Degree</h4><p>University Name - 2020</p></div>',
            'PRIMARY_SKILLS': 'Problem Solving, Communication, Teamwork, Project Management',
            'PROGRAMMING_LANGUAGES': '<ul><li>Python - Intermediate</li><li>JavaScript - Intermediate</li></ul>',
            'FRAMEWORKS': '<ul><li>React - Beginner</li><li>Node.js - Beginner</li></ul>',
            'DATABASES_TOOLS': '<ul><li>MySQL - Beginner</li><li>Git - Intermediate</li></ul>',
            'CLOUD_DEVOPS': '<ul><li>AWS - Beginner</li><li>Docker - Beginner</li></ul>',
            'CONTACT_MESSAGE': 'I am open to exciting new opportunities. Let\'s connect!',
            'WORK_EXPERIENCE': '<div class="experience-item"><h4>Professional Experience</h4><p>Contributed to various projects and initiatives with focus on quality and collaboration.</p></div>',
            'PROJECTS_LIST': '<div class="project-item"><h4>Portfolio Project</h4><p>A showcase of technical skills and creativity, demonstrating problem-solving abilities.</p></div>',
            'SECONDARY_TITLE_1': 'Problem Solver',
            'SECONDARY_TITLE_2': 'Creative Thinker',
            'SECONDARY_TITLE_3': 'Team Player'
        }
    
    def create_temp_portfolio_copy(self, user_id: str, template_style: str = 'tech-style') -> str:
        """Create a temporary copy of the selected portfolio template"""
        try:
            temp_path = os.path.join(self.temp_portfolios_path, user_id)
            
            # Remove existing temp directory if it exists
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path)
            
            # Get template path based on style
            template_info = self.available_templates.get(template_style, self.available_templates['tech-style'])
            template_subpath = template_info['path']
            
            # Build full template path
            if template_subpath:
                source_template_path = os.path.join(self.template_base_path, template_subpath)
            else:
                source_template_path = self.template_base_path
            
            # Verify template exists
            if not os.path.exists(source_template_path):
                raise FileNotFoundError(f"Template not found: {source_template_path}")
            
            # Copy the entire template directory to temp location
            shutil.copytree(source_template_path, temp_path)
            
            return temp_path
            
        except Exception as e:
            print(f"Error creating temp portfolio copy: {str(e)}")
            raise e
    
    def replace_placeholders_in_temp_copy(self, temp_path: str, data: Dict[str, Any]):
        """Replace placeholders in the temporary portfolio copy"""
        try:
            # Process all HTML, CSS, and JS files in the temp directory
            for root, dirs, files in os.walk(temp_path):
                for file in files:
                    if file.endswith(('.html', '.css', '.js')):
                        file_path = os.path.join(root, file)
                        
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Replace all placeholders
                        for key, value in data.items():
                            placeholder = f"{{{{{key}}}}}"
                            content = content.replace(placeholder, str(value))
                        
                        # Write back the modified content
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
            
        except Exception as e:
            print(f"Error replacing placeholders: {str(e)}")
            raise e
    
    def generate_preview_html(self, temp_path: str) -> str:
        """Generate HTML content for iframe preview"""
        try:
            index_path = os.path.join(temp_path, 'index.html')
            
            if not os.path.exists(index_path):
                return "<p>Error: Portfolio template not found</p>"
            
            # Read the main HTML file
            with open(index_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Inline CSS for better preview
            css_path = os.path.join(temp_path, 'main.css')
            if os.path.exists(css_path):
                with open(css_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                
                # Inject CSS into HTML
                css_tag = f"<style>{css_content}</style>"
                html_content = html_content.replace('</head>', f'{css_tag}</head>')
            
            # Inject JavaScript to handle navigation links and prevent page reloads in iframe
            navigation_fix_script = """
            <script>
            // IFRAME PREVIEW FIX: Prevent navigation from breaking out of iframe
            // This script runs after DOMContentLoaded to override template's navigation
            (function() {
                // Wait for template's scripts to load, then override navigation
                function fixIframeNavigation() {
                    // Override all anchor link clicks with capturing phase (runs before template handlers)
                    document.addEventListener('click', function(e) {
                        const target = e.target.closest('a');
                        if (!target) return;
                        
                        const href = target.getAttribute('href');
                        
                        // Handle internal anchor links (#section)
                        if (href && href.startsWith('#')) {
                            e.preventDefault();
                            e.stopPropagation();
                            e.stopImmediatePropagation();
                            
                            const targetId = href.substring(1);
                            const targetElement = document.getElementById(targetId);
                            
                            if (targetElement) {
                                // Smooth scroll to target
                                targetElement.scrollIntoView({
                                    behavior: 'smooth',
                                    block: 'start'
                                });
                                
                                // Update URL hash without navigation (for iframe)
                                if (window.history && window.history.pushState) {
                                    window.history.pushState(null, null, href);
                                }
                            }
                            
                            return false;
                        }
                        
                        // Handle external links (http, https, mailto, etc.)
                        if (href && (href.startsWith('http') || href.startsWith('mailto') || target.getAttribute('target') === '_blank')) {
                            e.preventDefault();
                            e.stopPropagation();
                            e.stopImmediatePropagation();
                            
                            // Show alert for external links in preview
                            alert('🔗 External links are disabled in preview mode.\\n\\nDownload the portfolio to access all links and full functionality.');
                            
                            return false;
                        }
                    }, true); // Use capture phase to run before other handlers
                }
                
                // Run after page loads and template scripts initialize
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', function() {
                        setTimeout(fixIframeNavigation, 500); // Delay to ensure template scripts run first
                    });
                } else {
                    setTimeout(fixIframeNavigation, 500);
                }
            })();
            </script>
            """
            
            # Inject the script before closing body tag
            html_content = html_content.replace('</body>', f'{navigation_fix_script}</body>')
            
            return html_content
            
        except Exception as e:
            print(f"Error generating preview HTML: {str(e)}")
            return f"<p>Error generating preview: {str(e)}</p>"
    
    def create_portfolio_zip(self, temp_path: str, user_id: str, full_name: str) -> str:
        """Create a zip file of the generated portfolio"""
        try:
            # Clean filename
            safe_name = re.sub(r'[^\w\s-]', '', full_name).strip()
            safe_name = re.sub(r'[-\s]+', '_', safe_name)
            
            zip_filename = f"{safe_name}_portfolio_{user_id}.zip"
            zip_path = os.path.join(self.generated_portfolios_path, zip_filename)
            
            # Create zip file
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Calculate relative path for zip
                        arcname = os.path.relpath(file_path, temp_path)
                        zipf.write(file_path, arcname)
            
            return zip_path
            
        except Exception as e:
            print(f"Error creating portfolio zip: {str(e)}")
            raise e
    
    def cleanup_temp_portfolio(self, user_id: str):
        """Clean up temporary portfolio files"""
        try:
            temp_path = os.path.join(self.temp_portfolios_path, user_id)
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path)
                print(f"✅ Cleaned up temp portfolio for user: {user_id}")
        except Exception as e:
            print(f"Error cleaning up temp portfolio: {str(e)}")
    
    def _cleanup_old_temp_files(self, max_age_hours: int = 1):
        """
        Automatically clean up old temporary files
        This prevents storage accumulation in cloud deployments
        """
        try:
            if not os.path.exists(self.temp_portfolios_path):
                return
            
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            cleaned_count = 0
            
            for item in os.listdir(self.temp_portfolios_path):
                item_path = os.path.join(self.temp_portfolios_path, item)
                
                # Check if it's a directory and how old it is
                if os.path.isdir(item_path):
                    item_age = current_time - os.path.getmtime(item_path)
                    
                    if item_age > max_age_seconds:
                        shutil.rmtree(item_path)
                        cleaned_count += 1
            
            if cleaned_count > 0:
                print(f"🧹 Auto-cleanup: Removed {cleaned_count} old temp portfolio(s)")
                
        except Exception as e:
            print(f"Warning: Auto-cleanup failed: {str(e)}")
    
    def cleanup_generated_portfolio(self, user_id: str):
        """Clean up generated portfolio files"""
        try:
            # Clean up temp files
            self.cleanup_temp_portfolio(user_id)
            
            # Clean up zip files
            for file in os.listdir(self.generated_portfolios_path):
                if user_id in file:
                    file_path = os.path.join(self.generated_portfolios_path, file)
                    os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up generated portfolio: {str(e)}")
    
    # Legacy methods for backward compatibility
    def extract_resume_data(self, resume_text: str, analyzer) -> Dict[str, Any]:
        """Extract structured data from resume text using existing analyzer (legacy method)"""
        return self.extract_basic_resume_data(resume_text)
    
    def generate_portfolio(self, resume_text: str, analyzer, user_id: str = None) -> Dict[str, Any]:
        """Legacy method - redirects to AI-powered generation"""
        # Import AI analyzer for legacy support
        try:
            from utils.ai_resume_analyzer import AIResumeAnalyzer
            ai_analyzer = AIResumeAnalyzer()
            return self.generate_portfolio_with_ai(resume_text, ai_analyzer, user_id)
        except Exception as e:
            return {
                'success': False,
                'message': f'Legacy portfolio generation failed: {str(e)}',
                'error': str(e)
            }