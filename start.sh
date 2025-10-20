#!/bin/bash

# Start script for Render deployment
echo "🚀 Starting Smart AI Resume Analyzer on Render..."

# Set default port if not provided
export PORT=${PORT:-10000}

echo "📡 Server will run on port: $PORT"

# Initialize database and setup
echo "🔧 Initializing application..."
python -c "
try:
    from config.database import init_database
    init_database()
    print('✅ Database initialized')
except Exception as e:
    print(f'⚠️ Database initialization warning: {e}')
"

# Start Streamlit
echo "🌟 Starting Streamlit server..."
exec streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false