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
# Database (MongoDB)
MONGODB_URL=mongodb://user:password@mongodb-host:27017/myapp?authSource=admin
# Or SQL database (PostgreSQL, MySQL, MariaDB, SQLite)
DATABASE_URL=postgresql+asyncpg://user:password@postgres-host:5432/myapp
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

### Docker Compose (Recommended)

Use `compose.prod.yml` for production deployment:

```bash
docker compose -f compose.prod.yml up -d
```

This starts:

- MongoDB with persistence
- Redis (if enabled)
- Your application

### Simple Cloud Deployment

For most use cases, Docker Compose deployment on a single VM is sufficient:

1. **Choose a cloud provider** (DigitalOcean, Hetzner, AWS EC2, etc.)
2. **Create a VM** with Docker installed
3. **Deploy using Docker Compose** as shown above
4. **Set up a reverse proxy** (Nginx or Caddy) for SSL

### Platform-as-a-Service Options

Some PaaS providers support Docker deployments:

- **Railway**: Connect GitHub repository, add MongoDB plugin, configure environment variables
- **Render**: Create Web Service, connect repository, add environment variables

Note: These platforms may have limitations compared to full Docker Compose control.

## Database Setup

Choose the database that fits your project needs.

### MongoDB Atlas

1. Create account at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create cluster
3. Create database user
4. Whitelist application IP addresses
5. Get connection string:

```text
mongodb+srv://user:password@cluster.mongodb.net/myapp?retryWrites=true&w=majority
```

### PostgreSQL (Managed)

Popular managed PostgreSQL providers:

- **Neon**: [neon.tech](https://neon.tech/) - Serverless PostgreSQL
- **Supabase**: [supabase.com](https://supabase.com/) - PostgreSQL with extras
- **AWS RDS**: [aws.amazon.com/rds/postgresql](https://aws.amazon.com/rds/postgresql/)

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

### Self-Hosted PostgreSQL

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: myapp
      POSTGRES_PASSWORD: secure-password
      POSTGRES_DB: myapp
    ports:
      - "5432:5432"
volumes:
  postgres_data:
```

For SQL databases, run `vibetuner db create-schema` after deployment to create tables.

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

Vibetuner includes health endpoints:

```bash
# Simple ping check
curl http://localhost:8000/health/ping
```

Returns:

```json
{"ping": "ok"}
```

For detailed instance information:

```bash
curl http://localhost:8000/health/id
```

Returns:

```json
{
"app": "myapp",
"port": 8000,
"debug": false,
"status": "healthy",
"root_path": "/app",
"process_id": 1,
"startup_time": "2024-01-01T00:00:00"
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

## Scaling Considerations

### Basic Scaling

For simple scaling needs:

1. **Upgrade server resources** (CPU, RAM)
2. **Use MongoDB Atlas** for managed database scaling
3. **Add Redis** for session storage and caching

### Advanced Scaling

When you need to scale beyond a single server:

1. **Load balancer** (Nginx, Caddy, or cloud LB)
2. **Multiple app instances** behind the load balancer
3. **Redis for shared sessions**
4. **MongoDB Atlas** for database scaling

Note: Advanced scaling requires careful planning and monitoring.

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

### Basic GitHub Actions

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
    - name: Deploy to server
      run: |
        # SSH into your server and pull the new image
        ssh user@your-server "cd /app && docker compose pull && docker compose up -d"
```

## Next Steps

- Monitor application performance
- Set up automated backups
- Configure alerting
- Plan for scaling
