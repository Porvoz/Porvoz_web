# Deployment Guide for Porvoz

**Status:** Ready for production Docker deployment

---

## 🚀 Pre-Deployment Checklist

```bash
# 1. Run security checks
bash scripts/security_check.sh

# 2. Run all tests
cd porvoz
python manage.py test --verbosity 2
cd ..

# 3. Check .env is not staged
git status | grep -i ".env"  # Should NOT show .env

# 4. Verify no secrets in code
git log --all --patch | grep -i "password\|secret\|token" | head -1
# Should show nothing (or only in .env.example)
```

---

## 📦 Option 1: Docker (Recommended)

### Local Docker Test
```bash
# Copy and fill .env
cp .env.example .env
# Edit .env (fill at least: TWILIO_*, EMAIL_*, GEMINI_API_KEY, DB_PASSWORD)

# Start all services
docker compose up -d

# Check status
docker compose ps
docker compose logs -f web

# Access
http://localhost           # Porvoz UI
http://localhost:5555      # Flower (Celery monitor) [profile monitoring]

# Run migrations in container
docker compose exec web python manage.py migrate

# Stop
docker compose down
```

### Production Deployment (Linux Server)

**1. Create production .env on server:**
```bash
# SSH to your server
ssh user@your-server

# Create .env with real credentials
cat > /app/porvoz/.env << 'EOF'
DJANGO_ENVIRONMENT=production
DJANGO_SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
ALLOWED_HOSTS=api.porvoz.com,porvoz.com

# Email
EMAIL_HOST_USER=porvoz-noreply@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx

# Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxx...
TWILIO_AUTH_TOKEN=your_token...
TWILIO_FROM_NUMBER=+1234567890
TWILIO_BASE_URL=https://api.porvoz.com
TWILIO_DRY_RUN=false

# Gemini
GEMINI_API_KEY=AIzaSyD...

# Database
DB_PASSWORD=your_secure_postgres_password_here

EOF
```

**2. Deploy with git + Docker:**
```bash
# Clone repo
git clone https://github.com/Porvoz/Porvoz_web.git /app/porvoz
cd /app/porvoz

# Pull latest main
git checkout main
git pull origin main

# Start services
docker compose up -d

# Run migrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput

# Check logs
docker compose logs -f web
```

**3. Nginx reverse proxy (recommended):**
```bash
# Copy nginx config
cp docker/nginx/default.conf /etc/nginx/conf.d/porvoz.conf

# Edit for your domain
sudo nano /etc/nginx/conf.d/porvoz.conf
# Change server_name to your domain

# Test and reload
sudo nginx -t
sudo systemctl reload nginx

# Get SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.porvoz.com
```

---

## 🟠 Option 2: AWS (ECS + RDS + ElastiCache)

### Create RDS Database
```bash
# AWS Console → RDS → Create Database
# - Engine: PostgreSQL 16
# - Instance: db.t3.micro (free tier)
# - DB name: porvoz
# - Username: porvoz
# - Password: (strong password, use in DB_PASSWORD secret)
# - Public: Yes (or through VPC)

# Get endpoint: porvoz-db-xxxxx.region.rds.amazonaws.com
```

### Create ElastiCache Redis
```bash
# AWS Console → ElastiCache → Create Cluster
# - Engine: Redis 7.x
# - Instance type: cache.t3.micro (free tier)
# - Get endpoint: porvoz-redis-xxxxx.region.cache.amazonaws.com
```

### Push Docker Image to ECR
```bash
# Create ECR repo
aws ecr create-repository --repository-name porvoz

# Login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -f docker/django/Dockerfile -t porvoz:latest .
docker tag porvoz:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/porvoz:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/porvoz:latest
```

### Create ECS Task Definition
```json
{
  "family": "porvoz",
  "containerDefinitions": [
    {
      "name": "web",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/porvoz:latest",
      "portMappings": [{"containerPort": 8000}],
      "environment": [
        {"name": "DJANGO_SETTINGS_MODULE", "value": "config.settings.production"}
      ],
      "secrets": [
        {"name": "DJANGO_SECRET_KEY", "valueFrom": "arn:aws:secretsmanager:..."},
        {"name": "DATABASE_URL", "valueFrom": "arn:aws:secretsmanager:..."},
        {"name": "REDIS_URL", "valueFrom": "arn:aws:secretsmanager:..."}
      ]
    }
  ]
}
```

---

## 🟢 Option 3: Simple Deployment (Railway / Render)

### Railway
```bash
# 1. Connect GitHub repo
# 2. Set environment variables in dashboard
# 3. Deploy

DJANGO_SECRET_KEY=...
ALLOWED_HOSTS=your-app.railway.app
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
# (all other Twilio, Email, Gemini vars)

# Railway auto-provisions PostgreSQL + Redis
```

### Render
```bash
# Similar to Railway
# 1. GitHub repo → New Web Service
# 2. Add environment variables
# 3. Auto-deploys on push to main
```

---

## 🔐 GitHub Secrets Configuration

**For CI/CD in `.github/workflows/deploy.yml` to work, set these in GitHub:**

Go to: **Repository → Settings → Secrets and variables → Actions**

Add:
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `EMAIL_HOST_PASSWORD`
- `GEMINI_API_KEY`
- `DB_PASSWORD`
- `DJANGO_SECRET_KEY`
- `ALLOWED_HOSTS`

See `GITHUB_SECRETS.md` for detailed instructions.

---

## ✅ Health Check

After deployment:

```bash
# Check health endpoint
curl https://api.porvoz.com/api/health/
# Expected: {"status": "ok", "database": true, "redis": true}

# Check Flower (Celery monitoring)
https://api.porvoz.com:5555  # if exposed

# Check logs
docker compose logs -f web
docker compose logs -f celery-worker
docker compose logs -f celery-beat
```

---

## 🐛 Troubleshooting

### "Connection refused" for database
- Check DATABASE_URL format: `postgresql://user:pass@host:port/dbname`
- Verify RDS security group allows inbound 5432

### Celery tasks not running
- Check Redis is healthy: `docker compose exec redis redis-cli ping`
- Check celery-worker logs: `docker compose logs celery-worker`

### Twilio webhooks not reaching app
- Check TWILIO_BASE_URL is correct and public
- Verify ngrok tunnel or public IP
- Check firewall/routing

### Email not sending
- Check EMAIL_HOST_PASSWORD is App Password (not regular password)
- Verify Gmail 2FA is enabled
- Check SMTP settings in production.py

---

## 📊 Monitoring

**Celery monitoring (Flower):**
```bash
# Enable in docker-compose
docker compose --profile monitoring up

# Access: http://localhost:5555
```

**Application logs:**
```bash
docker compose logs -f web
docker compose logs -f celery-worker
```

**Database health:**
```bash
docker compose exec db psql -U porvoz -d porvoz -c "SELECT 1;"
```

---

## 🔄 Updates & Rollback

### Update to latest
```bash
git pull origin main
docker compose pull
docker compose up -d web celery-worker celery-beat
docker compose exec web python manage.py migrate
```

### Rollback
```bash
git checkout previous-commit-hash
docker compose pull
docker compose up -d
```

---

## 📞 Emergency Contacts

If deployment breaks:
1. Check logs: `docker compose logs -f`
2. Check health: `curl https://api.porvoz.com/api/health/`
3. Rollback: `git checkout main~1 && docker compose up -d`
4. Contact team
