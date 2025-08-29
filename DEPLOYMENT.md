# 🚀 OralSmart Docker Deployment Guide

This guide covers deploying the OralSmart Django ML application using Docker containers with PyTorch model support.

## 📋 Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0+
- At least 4GB RAM available for containers
- 2GB free disk space

## 🏗️ Deployment Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Nginx     │────│ Django App   │────│   MySQL     │
│ (Port 80)   │    │ (Port 8000)  │    │ (Port 3306) │
└─────────────┘    └──────────────┘    └─────────────┘
       │                   │                   │
       │                   └───────────────────┼─────────────┐
       │                                       │             │
   ┌───▼────┐                             ┌────▼───┐    ┌───▼────┐
   │ Static │                             │ Redis  │    │ Volume │
   │ Files  │                             │ Cache  │    │ Data   │
   └────────┘                             └────────┘    └────────┘
```

## 🚀 Quick Start

### 1. **Setup Environment**

```bash
# Clone your repository (if not already local)
cd /path/to/oralsmart

# Copy environment template
cp .env.example .env

# Edit .env with your settings
notepad .env  # Windows
nano .env     # Linux/Mac
```

### 2. **Deploy with One Command**

**Windows:**
```batch
deploy.bat
```

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Manual Deployment:**
```bash
# Build and start services
docker-compose build
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser (if needed)
docker-compose exec web python manage.py createsuperuser
```

### 3. **Access Application**

- 🌐 **Web App**: http://localhost:8000
- 👤 **Admin**: http://localhost:8000/admin
- 🔍 **Health**: http://localhost:8000/health/
- 🤖 **ML API**: http://localhost:8000/ml/

## 📁 File Structure

```
oralsmart/
├── 🐳 Dockerfile.prod          # Production container
├── 🐳 docker-compose.yml       # Development setup
├── 🐳 docker-compose.prod.yml  # Production setup
├── 📝 requirements-prod.txt    # Production dependencies
├── 🔧 .env.example            # Environment template
├── 🚀 deploy.sh               # Linux/Mac deployment
├── 🚀 deploy.bat              # Windows deployment
├── 📄 .dockerignore           # Docker build exclusions
└── docker/
    ├── nginx/
    │   └── nginx.conf         # Reverse proxy config
    └── ssl/                   # SSL certificates
```

## ⚙️ Configuration Files

### **Environment Variables (.env)**

```bash
# Database
DB_NAME=oralsmart
DB_USER=oralsmart
DB_PASSWORD=your-secure-password
DB_HOST=db
DB_PORT=3306

# Django
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,your-domain.com

# ML Models
USE_GPU=True
MODEL_PATH=/app/ml_models/saved_models

# Redis
REDIS_URL=redis://redis:6379/0
```

### **Key Features**

✅ **GPU Support**: PyTorch models with CUDA acceleration  
✅ **Auto Scaling**: Gunicorn with multiple workers  
✅ **Load Balancing**: Nginx reverse proxy  
✅ **Health Checks**: Built-in monitoring endpoints  
✅ **Static Files**: Optimized serving with caching  
✅ **Database**: MySQL with persistent storage  
✅ **Security**: Non-root containers, rate limiting  

## 🎯 Deployment Options

### **Development Deployment**
```bash
docker-compose up -d
```
- Single server setup
- Debug mode available
- Hot reloading (with volumes)
- SQLite database option

### **Production Deployment**
```bash
docker-compose -f docker-compose.prod.yml up -d
```
- Multi-container architecture
- Nginx load balancer
- MySQL database
- Redis caching
- SSL/TLS ready
- Performance optimized

## 🔧 Management Commands

### **Service Management**
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart web

# Stop all services
docker-compose down

# Update and restart
docker-compose build --no-cache
docker-compose up -d
```

### **Django Management**
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic

# Train ML model
docker-compose exec web python manage.py train_ml_model

# Shell access
docker-compose exec web python manage.py shell
```

### **Database Management**
```bash
# Database shell
docker-compose exec db mysql -u oralsmart -p oralsmart

# Backup database
docker-compose exec db mysqldump -u oralsmart -p oralsmart > backup.sql

# Restore database
docker-compose exec -T db mysql -u oralsmart -p oralsmart < backup.sql
```

## 🧪 Testing Deployment

### **Health Checks**
```bash
# Check application health
curl http://localhost:8000/health/

# Expected response:
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "ml_models": "loaded",
    "static_files": "available",
    "media_files": "available"
  }
}
```

### **ML Model Testing**
```bash
# Test ML prediction endpoint
curl -X POST http://localhost:8000/ml/predict/ \
  -H "Content-Type: application/json" \
  -d '{"dental_data": {...}, "dietary_data": {...}}'
```

### **Performance Testing**
```bash
# Load test (requires apache2-utils)
ab -n 100 -c 10 http://localhost:8000/

# Memory usage
docker stats

# Service status
docker-compose ps
```

## 🔒 Security Considerations

### **SSL/TLS Setup**
1. Generate SSL certificates:
```bash
# Self-signed (development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/ssl/server.key \
  -out docker/ssl/server.crt

# Let's Encrypt (production)
certbot certonly --standalone -d your-domain.com
```

2. Update nginx configuration with SSL paths

### **Security Headers**
The nginx configuration includes:
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Rate limiting on API endpoints

## 🚨 Troubleshooting

### **Common Issues**

**1. Port Already in Use**
```bash
# Find process using port
netstat -tulpn | grep :8000
# Kill process
sudo kill -9 <PID>
```

**2. Database Connection Failed**
```bash
# Check database logs
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up -d
```

**3. ML Model Loading Error**
```bash
# Check model files exist
docker-compose exec web ls -la /app/ml_models/saved_models/

# Retrain model
docker-compose exec web python manage.py train_ml_model
```

**4. Permission Denied**
```bash
# Fix file permissions
sudo chown -R $(whoami):$(whoami) .
chmod +x deploy.sh
```

**5. Out of Memory**
```bash
# Check memory usage
docker system df
docker system prune -a

# Increase Docker memory limit in settings
```

### **Log Analysis**
```bash
# Application logs
docker-compose logs web

# Database logs
docker-compose logs db

# Nginx logs
docker-compose logs nginx

# Real-time monitoring
docker-compose logs -f --tail=100
```

## 🚀 Production Deployment

### **Cloud Deployment (AWS/Azure/GCP)**

1. **Setup cloud infrastructure**
2. **Configure environment variables**
3. **Deploy with production compose file**
4. **Setup domain and SSL**
5. **Configure monitoring**

### **Scaling**

```yaml
# docker-compose.prod.yml
services:
  web:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
```

## 📊 Monitoring

### **Container Monitoring**
- Built-in health checks
- Resource usage tracking
- Log aggregation

### **Application Monitoring**
- Django admin interface
- ML model performance metrics
- API response times

## 🔄 CI/CD Integration

Example GitHub Actions workflow:
```yaml
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          ssh user@server 'cd /app && docker-compose -f docker-compose.prod.yml up -d'
```

## 📞 Support

For issues with deployment:
1. Check the logs: `docker-compose logs -f`
2. Verify health endpoint: `curl http://localhost:8000/health/`
3. Review environment variables in `.env`
4. Ensure ML models are present in `saved_models/`

---

**🎉 Your OralSmart ML application is now ready for production deployment!**
