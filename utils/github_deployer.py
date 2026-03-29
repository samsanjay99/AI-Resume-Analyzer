"""
GitHub Portfolio Deployer
Automatically deploys portfolio websites to GitHub Pages
"""

import os
import requests
import base64
import json
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class GitHubDeployer:
    def __init__(self):
        """Initialize GitHub deployer with token from environment"""
        self.token = os.getenv('GITHUB_TOKEN')
        self.username = os.getenv('GITHUB_USERNAME', 'AI-resume-portfolios')
        self.base_url = 'https://api.github.com'
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def create_repository(self, repo_name, description="Portfolio website"):
        """
        Create a new GitHub repository
        
        Args:
            repo_name: Name of the repository
            description: Repository description
            
        Returns:
            dict: Repository information or error
        """
        if not self.token:
            return {
                'success': False,
                'error': 'GitHub token not configured. Please add GITHUB_TOKEN to .env file'
            }
        
        url = f'{self.base_url}/user/repos'
        data = {
            'name': repo_name,
            'description': description,
            'homepage': f'https://{self.username}.github.io/{repo_name}',
            'private': False,
            'has_issues': False,
            'has_projects': False,
            'has_wiki': False,
            'auto_init': True
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 201:
                repo_data = response.json()
                return {
                    'success': True,
                    'repo_name': repo_data['name'],
                    'repo_url': repo_data['html_url'],
                    'clone_url': repo_data['clone_url']
                }
            elif response.status_code == 422:
                # Repository already exists
                return {
                    'success': False,
                    'error': 'Repository already exists',
                    'repo_exists': True
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to create repository: {response.json().get("message", "Unknown error")}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error creating repository: {str(e)}'
            }
    
    def upload_file(self, repo_name, file_path, file_content, commit_message="Add file"):
        """
        Upload a file to GitHub repository
        
        Args:
            repo_name: Repository name
            file_path: Path in repository (e.g., 'index.html')
            file_content: File content as string
            commit_message: Commit message
            
        Returns:
            dict: Upload result
        """
        if not self.token:
            return {'success': False, 'error': 'GitHub token not configured'}
        
        url = f'{self.base_url}/repos/{self.username}/{repo_name}/contents/{file_path}'
        
        # Encode content to base64
        content_bytes = file_content.encode('utf-8')
        content_base64 = base64.b64encode(content_bytes).decode('utf-8')
        
        data = {
            'message': commit_message,
            'content': content_base64
        }
        
        try:
            # Check if file exists
            check_response = requests.get(url, headers=self.headers)
            
            if check_response.status_code == 200:
                # File exists, need to update with SHA
                existing_file = check_response.json()
                data['sha'] = existing_file['sha']
            
            # Upload or update file
            response = requests.put(url, headers=self.headers, json=data)
            
            if response.status_code in [200, 201]:
                return {'success': True}
            else:
                return {
                    'success': False,
                    'error': f'Failed to upload file: {response.json().get("message", "Unknown error")}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error uploading file: {str(e)}'
            }
    
    def enable_github_pages(self, repo_name, branch='main'):
        """
        Enable GitHub Pages for a repository
        
        Args:
            repo_name: Repository name
            branch: Branch to use for GitHub Pages
            
        Returns:
            dict: Result of enabling GitHub Pages
        """
        if not self.token:
            return {'success': False, 'error': 'GitHub token not configured'}
        
        url = f'{self.base_url}/repos/{self.username}/{repo_name}/pages'
        
        data = {
            'source': {
                'branch': branch,
                'path': '/'
            }
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 201:
                pages_data = response.json()
                return {
                    'success': True,
                    'url': pages_data.get('html_url', f'https://{self.username}.github.io/{repo_name}')
                }
            elif response.status_code == 409:
                # GitHub Pages already enabled
                return {
                    'success': True,
                    'url': f'https://{self.username}.github.io/{repo_name}',
                    'already_enabled': True
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to enable GitHub Pages: {response.json().get("message", "Unknown error")}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error enabling GitHub Pages: {str(e)}'
            }
    
    def deploy_portfolio(self, portfolio_files, candidate_name):
        """
        Deploy a complete portfolio to GitHub Pages
        
        Args:
            portfolio_files: Dictionary of {filename: content}
            candidate_name: Name of the candidate (used for repo name)
            
        Returns:
            dict: Deployment result with URL
        """
        import time
        
        # Generate repository name
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        safe_name = ''.join(c if c.isalnum() else '-' for c in candidate_name.lower())
        repo_name = f'portfolio-{safe_name}-{timestamp}'
        
        # Step 1: Create repository
        print(f"Creating repository: {repo_name}")
        repo_result = self.create_repository(
            repo_name,
            f"Portfolio website for {candidate_name}"
        )
        
        if not repo_result['success']:
            return repo_result
        
        # Wait for repository to be fully initialized
        print("Waiting for repository initialization...")
        time.sleep(3)
        
        # Step 2: Upload files
        print("Uploading portfolio files...")
        for filename, content in portfolio_files.items():
            print(f"  Uploading {filename}...")
            upload_result = self.upload_file(
                repo_name,
                filename,
                content,
                f"Add {filename}"
            )
            
            if not upload_result['success']:
                return {
                    'success': False,
                    'error': f'Failed to upload {filename}: {upload_result["error"]}'
                }
            
            # Small delay between uploads
            time.sleep(0.5)
        
        # Step 3: Enable GitHub Pages
        print("Enabling GitHub Pages...")
        time.sleep(2)  # Wait before enabling pages
        pages_result = self.enable_github_pages(repo_name)
        
        if not pages_result['success']:
            return pages_result
        
        # Success!
        return {
            'success': True,
            'repo_name': repo_name,
            'repo_url': f'https://github.com/{self.username}/{repo_name}',
            'live_url': pages_result['url'],
            'message': 'Portfolio deployed successfully! It may take 1-2 minutes to be live.'
        }
    
    def delete_repository(self, repo_name):
        """
        Delete a GitHub repository
        
        Args:
            repo_name: Repository name to delete
            
        Returns:
            dict: Deletion result
        """
        if not self.token:
            return {'success': False, 'error': 'GitHub token not configured'}
        
        url = f'{self.base_url}/repos/{self.username}/{repo_name}'
        
        try:
            response = requests.delete(url, headers=self.headers)
            
            if response.status_code == 204:
                return {'success': True}
            else:
                return {
                    'success': False,
                    'error': f'Failed to delete repository: {response.json().get("message", "Unknown error")}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error deleting repository: {str(e)}'
            }


# Test function
if __name__ == '__main__':
    deployer = GitHubDeployer()
    
    # Test with a simple HTML file
    test_files = {
        'index.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>Test Portfolio</title>
</head>
<body>
    <h1>Test Portfolio</h1>
    <p>This is a test deployment.</p>
</body>
</html>
        '''
    }
    
    result = deployer.deploy_portfolio(test_files, 'Test User')
    print(json.dumps(result, indent=2))
