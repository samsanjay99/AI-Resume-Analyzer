# Use Python 3.11 slim image for better performance and compatibility
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables for Render
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PORT=10000

# Install system dependencies (minimal set for Streamlit and Render)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download NLTK data (required for text processing)
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/.streamlit /app/uploads /app/generated_portfolios /app/temp_portfolios

# Create Streamlit config for Render
RUN echo '[server]\n\
headless = true\n\
port = $PORT\n\
address = "0.0.0.0"\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
\n\
[browser]\n\
gatherUsageStats = false\n\
\n\
[theme]\n\
primaryColor = "#4CAF50"\n\
backgroundColor = "#0E1117"\n\
secondaryBackgroundColor = "#262730"\n\
textColor = "#FAFAFA"' > /app/.streamlit/config.toml

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose the port that Render will use
EXPOSE $PORT

# Health check for Render
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:$PORT/_stcore/health || exit 1

# Run the application with dynamic port for Render
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true 