#!/usr/bin/env python3
"""
Deployment setup script for Smart AI Resume Analyzer
"""

import os
import subprocess
import sys

def setup_deployment():
    """Setup the application for deployment"""
    print("🚀 Setting up Smart AI Resume Analyzer for deployment...")
    
    # Create necessary directories
    directories = ['uploads', 'generated_portfolios', 'temp_portfolios']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
    
    # Initialize database
    try:
        from config.database import init_database
        init_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
    
    # Download NLTK data if needed
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✅ NLTK data downloaded")
    except Exception as e:
        print(f"⚠️ NLTK download warning: {e}")
    
    print("🎉 Deployment setup completed!")
    print("📧 Admin Login: sam@gmail.com")
    print("🔑 Password: sanjay2026")

if __name__ == "__main__":
    setup_deployment()