# 🚀 Deployment Guide

Complete guide for deploying Smart Resume AI to production.

## Deployment Options

1. [Streamlit Cloud](#streamlit-cloud) - Easiest, free tier available
2. [Render](#render) - Good for production, free tier available
3. [Railway](#railway) - Modern platform, free tier available
4. [Heroku](#heroku) - Traditional PaaS
5. [Docker](#docker) - Self-hosted

---

## Streamlit Cloud

### Prerequisites
- GitHub account
- Streamlit Cloud account (free)
- Neon PostgreSQL database

### Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Connect to Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Select your repository
   - Choose `app.py` as main file

3. **Add Secrets**
   - Click "Advanced settings"
   - Add secrets in TOML format:
   ```toml
   DATABASE_URL = "postgresql://user:pass@host/db"
   GOOGLE_API_KEY = "your_api_key"
   NETLIFY_TOKEN = "your_token"
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment (2-3 minutes)
   - Your app is live!

### Custom Domain
- Go to app settings
- Add custom domain
- Update DNS records

---

## Render

### Prerequisites
- GitHub account
- Render account (free)
- Neon PostgreSQL database

### Steps

1. **Create `render.yaml`**
   ```yaml
   services:
     - type: web
       name: smart-resume-ai
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
       envVars:
         - key: DATABASE_URL
           sync: false
         - key: GOOGLE_API_KEY
           sync: false
         - key: NETLIFY_TOKEN
           sync: false
   ```

2. **Push to GitHub**
   ```bash
   git add render.yaml
   git commit -m "Add Render config"
   git push
   ```

3. **Deploy on Render**
   - Go to https://render.com/
   - Click "New +" → "Web Service"
   - Connect your repository
   - Render auto-detects configuration

4. **Add Environment Variables**
   - Go to Environment tab
   - Add all required variables
   - Click "Save Changes"

5. **Deploy**
   - Render automatically deploys
   - Wait for build (3-5 minutes)

---

## Railway

### Prerequisites
- GitHub account
- Railway account (free)
- Neon PostgreSQL database

### Steps

1. **Create `Procfile`**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Create `railway.json`**
   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

3. **Push to GitHub**
   ```bash
   git add Procfile railway.json
   git commit -m "Add Railway config"
   git push
   ```

4. **Deploy on Railway**
   - Go to https://railway.app/
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

5. **Add Environment Variables**
   - Click on your service
   - Go to "Variables" tab
   - Add all required variables

6. **Deploy**
   - Railway automatically deploys
   - Get your public URL

---

## Docker

### Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run app
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - NETLIFY_TOKEN=${NETLIFY_TOKEN}
    volumes:
      - ./uploads:/app/uploads
      - ./generated_portfolios:/app/generated_portfolios
    restart: unless-stopped
```

### Build and Run

```bash
# Build image
docker build -t smart-resume-ai .

# Run container
docker run -p 8501:8501 \
  -e DATABASE_URL="your_db_url" \
  -e GOOGLE_API_KEY="your_api_key" \
  -e NETLIFY_TOKEN="your_token" \
  smart-resume-ai

# Or use docker-compose
docker-compose up -d
```

---

## Environment Variables

### Required

```env
DATABASE_URL=postgresql://user:pass@host:5432/db
GOOGLE_API_KEY=your_google_gemini_api_key
NETLIFY_TOKEN=your_netlify_token
```

### Optional

```env
OPENROUTER_API_KEY=your_openrouter_key
A4F_API_KEY=your_a4f_key
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

---

## Database Setup

### Neon PostgreSQL (Recommended)

1. **Create Database**
   - Go to https://neon.tech/
   - Create new project
   - Copy connection string

2. **Initialize Schema**
   ```bash
   python scripts/optimize_database_indexes.py
   ```

3. **Verify Connection**
   ```bash
   python tests/test_postgres_migration.py
   ```

---

## Post-Deployment

### 1. Verify Deployment

```bash
# Check health
curl https://your-app.com/_stcore/health

# Test login
# Visit https://your-app.com and login
```

### 2. Change Default Credentials

- Login with `sam@gmail.com` / `sanjay99`
- Go to Admin Dashboard
- Change password immediately

### 3. Monitor Performance

- Check admin dashboard metrics
- Review logs for errors
- Monitor database connections

### 4. Set Up Monitoring

**Uptime Monitoring:**
- Use UptimeRobot (free)
- Monitor every 5 minutes
- Get alerts on downtime

**Error Tracking:**
- Check Streamlit Cloud logs
- Set up email alerts
- Monitor database errors

---

## Scaling

### Horizontal Scaling

For high traffic:
1. Use load balancer
2. Deploy multiple instances
3. Use Redis for session storage
4. Implement CDN for static assets

### Database Scaling

1. **Connection Pooling** (already implemented)
   - 2-20 connections per instance
   - Automatic connection reuse

2. **Read Replicas**
   - Use Neon read replicas
   - Route read queries to replicas

3. **Caching** (already implemented)
   - 5-minute TTL cache
   - Reduces database load by 80%

---

## Backup & Recovery

### Database Backups

**Neon (Automatic):**
- Daily automatic backups
- Point-in-time recovery
- 7-day retention

**Manual Backup:**
```bash
pg_dump $DATABASE_URL > backup.sql
```

### File Backups

```bash
# Backup uploads
tar -czf uploads-backup.tar.gz uploads/

# Backup generated files
tar -czf portfolios-backup.tar.gz generated_portfolios/
```

---

## Security Checklist

- [ ] Change default admin credentials
- [ ] Use HTTPS (automatic on most platforms)
- [ ] Set strong database password
- [ ] Rotate API keys regularly
- [ ] Enable rate limiting
- [ ] Monitor for suspicious activity
- [ ] Keep dependencies updated
- [ ] Use environment variables (never commit secrets)

---

## Troubleshooting

### App Won't Start

**Check logs:**
```bash
# Streamlit Cloud: View logs in dashboard
# Render: View logs in service page
# Railway: View logs in deployment page
```

**Common issues:**
- Missing environment variables
- Database connection failed
- Port already in use

### Slow Performance

1. Check database indexes
2. Review cache hit rates
3. Monitor connection pool
4. Check API rate limits

### Database Connection Errors

1. Verify DATABASE_URL
2. Check database is running
3. Verify network connectivity
4. Check connection pool settings

---

## Maintenance

### Regular Tasks

**Daily:**
- Monitor error logs
- Check uptime status

**Weekly:**
- Review performance metrics
- Check database size
- Update dependencies

**Monthly:**
- Optimize database
- Review user feedback
- Update documentation

---

## Cost Optimization

### Free Tier Limits

**Streamlit Cloud:**
- 1 private app
- Unlimited public apps
- 1GB RAM per app

**Render:**
- 750 hours/month
- 512MB RAM
- Sleeps after 15min inactivity

**Railway:**
- $5 free credit/month
- Pay for usage

**Neon:**
- 10GB storage
- 100 hours compute/month

### Tips

1. Use caching to reduce API calls
2. Optimize database queries
3. Use CDN for static assets
4. Monitor usage regularly

---

## Support

- **Documentation**: Check `docs/` folder
- **Issues**: Open GitHub issue
- **Community**: Join discussions
- **Email**: your.email@example.com

---

**Your app is now live!** 🎉
