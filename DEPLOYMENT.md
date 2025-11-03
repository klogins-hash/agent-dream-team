# 🚀 Docker Deployment Guide

Deploy Agent Dream Team on any machine with Docker.

## Prerequisites

- Docker 24.0+
- Docker Compose 2.0+
- 4GB+ RAM recommended
- 20GB+ disk space

## Quick Deploy

### 1. Clone Repository

```bash
git clone https://github.com/klogins-hash/agent-dream-team.git
cd agent-dream-team
```

### 2. Configure Environment

```bash
# Copy production environment template
cp .env.production .env

# Edit with your values
nano .env
```

**Required Changes:**
- `OPENROUTER_API_KEY` - Your OpenRouter API key
- All passwords (search for `CHANGE_ME`)

### 3. Start Services

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f agent-app
```

### 4. Verify Deployment

```bash
# Check health
curl http://localhost/health

# Test agent connection
docker exec -it agent-dream-team-app python -c "from database import get_postgres; print('DB OK')"
```

## Architecture

```
┌─────────────┐
│   Nginx     │ :80, :443 (reverse proxy)
└──────┬──────┘
       │
┌──────▼──────┐
│  Agent App  │ (Python application)
└──────┬──────┘
       │
       ├──────► PostgreSQL (relational data)
       ├──────► Redis (cache)
       ├──────► Neo4j (knowledge graph)
       ├──────► RabbitMQ (messaging)
       ├──────► Elasticsearch (search)
       └──────► MinIO (object storage)
```

## Configuration

### Resource Limits

Edit `docker-compose.prod.yml` to add resource limits:

```yaml
services:
  agent-app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Scaling

Scale the agent application:

```bash
docker-compose -f docker-compose.prod.yml up -d --scale agent-app=3
```

### Backup

```bash
# Backup all data
./backup.sh

# Restore from backup
./restore.sh backup-2024-01-01.tar.gz
```

## Security

### 1. Change Default Passwords

**Critical**: Change all passwords in `.env` before deploying!

### 2. Enable HTTPS

```bash
# Get SSL certificates (Let's Encrypt)
sudo apt-get install certbot
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./ssl/key.pem

# Uncomment HTTPS block in nginx.conf
```

### 3. Firewall Rules

```bash
# Allow only necessary ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 4. Network Isolation

Services communicate on internal network only. Only Nginx is exposed.

## Monitoring

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f agent-app

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 agent-app
```

### Prometheus Metrics

Access at: http://your-server:9090

### Grafana Dashboards

Access at: http://your-server:3000
- Username: admin
- Password: (from .env)

## Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build agent-app
```

### Database Migrations

```bash
# Run migrations
docker exec -it agent-dream-team-app python -c "from database import get_postgres; # run migrations"
```

### Clean Up

```bash
# Remove stopped containers
docker-compose -f docker-compose.prod.yml down

# Remove volumes (WARNING: deletes all data)
docker-compose -f docker-compose.prod.yml down -v

# Clean up Docker system
docker system prune -a
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs agent-app

# Check resource usage
docker stats

# Restart specific service
docker-compose -f docker-compose.prod.yml restart agent-app
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
docker exec -it agent-team-postgres psql -U agent_user -d agent_team

# Test Redis connection
docker exec -it agent-team-redis redis-cli -a your-redis-password ping

# Test Neo4j connection
docker exec -it agent-team-neo4j cypher-shell -u neo4j -p your-neo4j-password
```

### Out of Memory

```bash
# Check memory usage
docker stats

# Increase swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Disk Space Issues

```bash
# Check disk usage
df -h

# Clean Docker
docker system prune -a --volumes

# Check large files
du -sh /var/lib/docker/*
```

## Production Checklist

- [ ] Changed all default passwords
- [ ] Set OPENROUTER_API_KEY
- [ ] Configured SSL certificates
- [ ] Set up firewall rules
- [ ] Configured backup strategy
- [ ] Set up monitoring alerts
- [ ] Tested disaster recovery
- [ ] Documented custom configurations
- [ ] Set up log rotation
- [ ] Configured resource limits

## Cloud Deployment

### AWS EC2

```bash
# Launch t3.large or larger
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone and deploy
git clone https://github.com/klogins-hash/agent-dream-team.git
cd agent-dream-team
cp .env.production .env
# Edit .env with your values
docker-compose -f docker-compose.prod.yml up -d
```

### DigitalOcean

Use Docker Droplet (4GB+ RAM recommended)

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT-ID/agent-team

# Deploy
gcloud run deploy agent-team \
  --image gcr.io/PROJECT-ID/agent-team \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Container Instances

```bash
# Create resource group
az group create --name agent-team-rg --location eastus

# Deploy
az container create \
  --resource-group agent-team-rg \
  --name agent-team \
  --image your-registry/agent-team:latest \
  --dns-name-label agent-team \
  --ports 80
```

## Support

- **Issues**: https://github.com/klogins-hash/agent-dream-team/issues
- **Discussions**: https://github.com/klogins-hash/agent-dream-team/discussions

## License

See LICENSE file for details.
