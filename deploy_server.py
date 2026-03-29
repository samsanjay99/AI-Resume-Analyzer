"""
Standalone Portfolio Deployment Server
Handles Netlify deployment with real-time progress updates
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import tempfile
import zipfile
import io
import requests
import shutil
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'portfolio-deployer-secret-key'

# Store deployment status in memory (use Redis in production)
deployments = {}


def deploy_to_netlify(folder_path, deployment_id):
    """Deploy portfolio to Netlify with progress updates"""
    
    try:
        # Update status
        deployments[deployment_id]['status'] = 'deploying'
        deployments[deployment_id]['logs'].append('🔐 Authenticating with Netlify...')
        deployments[deployment_id]['progress'] = 20
        time.sleep(0.5)
        
        token = os.getenv('NETLIFY_TOKEN')
        if not token:
            raise Exception('NETLIFY_TOKEN not found in environment')
        
        # Create ZIP
        deployments[deployment_id]['logs'].append('📦 Creating deployment package...')
        deployments[deployment_id]['progress'] = 40
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, folder_path)
                    z.write(full_path, rel_path)
        
        zip_buffer.seek(0)
        
        # Deploy to Netlify
        deployments[deployment_id]['logs'].append('🚀 Uploading to Netlify...')
        deployments[deployment_id]['progress'] = 60
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/zip'
        }
        
        response = requests.post(
            'https://api.netlify.com/api/v1/sites',
            headers=headers,
            data=zip_buffer.read(),
            timeout=120
        )
        
        deployments[deployment_id]['logs'].append('🌐 Configuring site...')
        deployments[deployment_id]['progress'] = 80
        time.sleep(0.5)
        
        if response.status_code in (200, 201):
            data = response.json()
            
            deployments[deployment_id]['logs'].append('✅ Deployment completed successfully!')
            deployments[deployment_id]['progress'] = 100
            deployments[deployment_id]['status'] = 'success'
            deployments[deployment_id]['live_url'] = data.get('url')
            deployments[deployment_id]['admin_url'] = data.get('admin_url')
            deployments[deployment_id]['site_id'] = data.get('id')
        else:
            raise Exception(f'Netlify API error: {response.text}')
    
    except Exception as e:
        deployments[deployment_id]['status'] = 'failed'
        deployments[deployment_id]['logs'].append(f'❌ Error: {str(e)}')
        deployments[deployment_id]['error'] = str(e)
    
    finally:
        # Cleanup temp folder
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path, ignore_errors=True)


@app.route('/')
def index():
    """Deployment page"""
    return render_template('deploy.html')


@app.route('/deploy', methods=['POST'])
def deploy():
    """Start deployment"""
    
    if 'portfolio' not in request.files:
        return jsonify({'error': 'No portfolio file provided'}), 400
    
    portfolio_file = request.files['portfolio']
    
    # Create deployment ID
    deployment_id = f"deploy_{int(time.time())}"
    
    # Initialize deployment status
    deployments[deployment_id] = {
        'status': 'preparing',
        'progress': 0,
        'logs': ['🔷 Preparing deployment...'],
        'live_url': None,
        'error': None
    }
    
    try:
        # Extract ZIP to temp folder
        temp_dir = tempfile.mkdtemp(prefix='portfolio_')
        
        with zipfile.ZipFile(portfolio_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        deployments[deployment_id]['logs'].append('📁 Portfolio files extracted')
        deployments[deployment_id]['progress'] = 10
        
        # Start deployment in background thread
        import threading
        thread = threading.Thread(
            target=deploy_to_netlify,
            args=(temp_dir, deployment_id),
            daemon=True
        )
        thread.start()
        
        return jsonify({'deployment_id': deployment_id})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/status/<deployment_id>')
def status(deployment_id):
    """Get deployment status"""
    
    if deployment_id not in deployments:
        return jsonify({'error': 'Deployment not found'}), 404
    
    return jsonify(deployments[deployment_id])


if __name__ == '__main__':
    app.run(debug=True, port=5001, threaded=True)
