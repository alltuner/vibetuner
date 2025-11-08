# Deployment

Deploy Vibetuner applications to production.

## Docker Production Build

Vibetuner includes a multi-stage Dockerfile optimized for production.

### Test Production Build Locally

```bash
just test-build-prod
```

This builds and runs the production image locally.

### Build and Push

```bash
just release
```

This builds the production image and pushes to your container registry.

## Environment Configuration

### Production Environment Variables

Create a `.env` file for production:

```bash
# Application
APP_NAME=My Application
SECRET_KEY=your-production-secret-key
DEBUG=false
ENVIRONMENT=production
# Database
DATABASE_URL=mongodb://user:password@mongodb-host:27017/myapp?authSource=admin
# Redis (if background jobs enabled)
REDIS_URL=redis://redis-host:6379/0
# Email
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
FROM_EMAIL=noreply@example.com
# OAuth
GOOGLE_CLIENT_ID=your-production-client-id
GOOGLE_CLIENT_SECRET=your-production-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-secret
# Session
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_SAMESITE=lax
SESSION_MAX_AGE=2592000
# Storage (if using S3)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=your-bucket
AWS_REGION=us-east-1
```

### Security Checklist

- [ ] Use strong, unique `SECRET_KEY`
- [ ] Set `DEBUG=false`
- [ ] Enable `SESSION_COOKIE_SECURE=true` (HTTPS)
- [ ] Use environment variables (not `.env` in image)
- [ ] Rotate secrets regularly
- [ ] Enable database authentication
- [ ] Use connection strings with credentials
- [ ] Configure CORS appropriately

## Deployment Options

### Docker Compose

Use `compose.prod.yml` for production deployment:

```bash
docker compose -f compose.prod.yml up -d
```

This starts:

- MongoDB with persistence
- Redis (if enabled)
- Your application
- Nginx reverse proxy (optional)

### Kubernetes

Example deployment:

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
name: myapp
spec:
replicas: 3
selector:
matchLabels:
app: myapp
template:
metadata:
labels:
app: myapp
spec:
containers:
- name: web
image: ghcr.io/yourorg/myapp:latest
ports:
- containerPort: 8000
env:
- name: DATABASE_URL
valueFrom:
secretKeyRef:
name: myapp-secrets
key: database-url
- name: SECRET_KEY
valueFrom:
secretKeyRef:
name: myapp-secrets
key: secret-key
```

### Cloud Platforms

#### Fly.io

```bash
# Install flyctl
brew install flyctl
# Login
flyctl auth login
# Launch app
flyctl launch
# Set secrets
flyctl secrets set SECRET_KEY=your-secret-key
flyctl secrets set DATABASE_URL=mongodb://...
# Deploy
flyctl deploy
```

#### Railway

1. Connect GitHub repository
2. Add MongoDB plugin
3. Configure environment variables
4. Deploy automatically on push

#### Render

1. Create new Web Service
2. Connect repository
3. Add environment variables
4. Render will auto-deploy

## Database Setup

### MongoDB Atlas (Recommended)

1. Create account at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create cluster
3. Create database user
4. Whitelist application IP addresses
5. Get connection string:

```text
mongodb+srv://user:password@cluster.mongodb.net/myapp?retryWrites=true&w=majority
```

### Self-Hosted MongoDB

```yaml
# docker-compose.yml
services:
mongodb:
image: mongo:7
volumes:
- mongodb_data:/data/db
environment:
MONGO_INITDB_ROOT_USERNAME: admin
MONGO_INITDB_ROOT_PASSWORD: secure-password
ports:
- "27017:27017"
volumes:
mongodb_data:
```

## Redis Setup (Optional)

Required if background jobs are enabled.

### Managed Redis

- **Redis Cloud**: [redis.com/cloud](https://redis.com/cloud/)
- **AWS ElastiCache**: [aws.amazon.com/elasticache](https://aws.amazon.com/elasticache/)
- **DigitalOcean**: [digitalocean.com/products/managed-databases-redis](https://www.digitalocean.com/products/managed-databases-redis/)

### Self-Hosted Redis

```yaml
services:
redis:
image: redis:7-alpine
volumes:
- redis_data:/data
ports:
- "6379:6379"
volumes:
redis_data:
```

## Reverse Proxy

### Nginx

```nginx
# /etc/nginx/sites-available/myapp
server {
listen 80;
server_name example.com;
location / {
proxy_pass http://localhost:8000;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
}
}
```

### Caddy

```text
example.com {
reverse_proxy localhost:8000
}
```

## SSL/TLS

### Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx
# Get certificate
sudo certbot --nginx -d example.com
```

### Caddy (Automatic HTTPS)

Caddy automatically provisions SSL certificates:

```bash
caddy run --config Caddyfile
```

## Monitoring and Logging

### Application Logs

```bash
# Docker
docker compose logs -f web
# Kubernetes
kubectl logs -f deployment/myapp
```

### Health Checks

Vibetuner includes a health endpoint:

```bash
curl http://localhost:8000/health
```

Returns:

```json
{
"status": "healthy",
"database": "connected",
"redis": "connected"
}
```

### Monitoring Services

- **Sentry**: Error tracking and performance monitoring
- **Datadog**: Infrastructure and application monitoring
- **New Relic**: Application performance monitoring
- **Prometheus + Grafana**: Self-hosted monitoring

## Backup and Recovery

### MongoDB Backups

```bash
# Manual backup
mongodump --uri="mongodb://..." --out=/backups/$(date +%Y%m%d)
# Restore
mongorestore --uri="mongodb://..." /backups/20240101
```

### Automated Backups

Use managed database backups or schedule with cron:

```bash
# crontab
0 2 * * * /scripts/backup-mongodb.sh
```

## Scaling

### Horizontal Scaling

Run multiple instances behind a load balancer:

```yaml
# docker-compose.yml
services:
web:
image: myapp:latest
deploy:
replicas: 3
```

### Session Storage

Use Redis for session storage when running multiple instances:

```python
# config.py
SESSION_BACKEND = "redis"
SESSION_REDIS_URL = settings.REDIS_URL
```

### Database Scaling

MongoDB Atlas provides:

- Automatic scaling
- Read replicas
- Sharding for large datasets

## Performance Optimization

### Static Asset CDN

Serve static files from a CDN:

```python
# config.py
STATIC_URL = "https://cdn.example.com/static/"
```

### Caching

Add Redis caching for expensive operations:

```python
from redis import asyncio as aioredis
redis = aioredis.from_url(settings.REDIS_URL)
async def get_popular_posts():
cached = await redis.get("popular_posts")
if cached:
return json.loads(cached)
posts = await Post.find().sort(-Post.views).limit(10).to_list()
await redis.setex("popular_posts", 3600, json.dumps(posts))
return posts
```

### Database Indexes

Add indexes for frequently queried fields:

```python
class Post(Document):
title: str
published_at: datetime
class Settings:
name = "posts"
indexes = [
IndexModel([("published_at", -1)]),
IndexModel([("title", "text")]),
]
```

## Troubleshooting

### Application Won't Start

Check:

1. Environment variables are set correctly
2. Database is accessible
3. Ports aren't already in use
4. Docker image built successfully

### Database Connection Errors

Check:

1. `DATABASE_URL` is correct
2. Network connectivity
3. Database credentials
4. IP whitelist (MongoDB Atlas)

### Static Assets Not Loading

Check:

1. Assets were compiled during build
2. `STATIC_URL` is correct
3. CDN is configured properly

### High Memory Usage

Consider:

1. Reducing worker processes
2. Enabling connection pooling
3. Adding caching layer
4. Upgrading server resources

## CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
push:
tags:
- 'v*'
jobs:
deploy:
runs-on: ubuntu-latest
steps:
- uses: actions/checkout@v4
- name: Build and push Docker image
run: |
docker build -t myapp:${{ github.ref_name }} .
docker push myapp:${{ github.ref_name }}
- name: Deploy to production
run: |
# Deploy to your platform
kubectl set image deployment/myapp web=myapp:${{ github.ref_name }}
```

## Next Steps

- Monitor application performance
- Set up automated backups
- Configure alerting
- Plan for scaling
