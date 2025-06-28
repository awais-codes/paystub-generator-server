# Deployment Guide

## Overview
This guide covers deploying the Paystub Generator to production environments.

## Prerequisites

- Production server (Ubuntu 20.04+ recommended)
- PostgreSQL database
- AWS S3 bucket (for file storage)
- Stripe account (for payments)
- Email service (SMTP or service like SendGrid)
- Domain name and SSL certificate

## Production Environment Setup

### 1. Server Preparation

#### Update System
```bash
sudo apt update && sudo apt upgrade -y
```

#### Install Required Packages
```bash
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib
```

#### Create Application User
```bash
sudo adduser paystub
sudo usermod -aG sudo paystub
```

### 2. Database Setup

#### Install PostgreSQL
```bash
sudo apt install -y postgresql postgresql-contrib
```

#### Create Database and User
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE paystub_generator;
CREATE USER paystub_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE paystub_generator TO paystub_user;
\q
```

### 3. Application Deployment

#### Clone Repository
```bash
sudo -u paystub git clone <repository-url> /home/paystub/paystub-generator
cd /home/paystub/paystub-generator/server
```

#### Create Virtual Environment
```bash
sudo -u paystub python3 -m venv venv
sudo -u paystub /home/paystub/paystub-generator/server/venv/bin/pip install -r requirements-prod.txt
```

#### Environment Configuration
Create production `.env` file:
```bash
sudo -u paystub nano /home/paystub/paystub-generator/server/.env
```

```env
# Django
SECRET_KEY=your_very_secure_secret_key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database
POSTGRES_DB=paystub_generator
POSTGRES_USER=paystub_user
POSTGRES_PASSWORD=secure_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=us-east-1
AWS_S3_CUSTOM_DOMAIN=your_bucket_name.s3.amazonaws.com

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your_email@gmail.com

# Static Files
STATIC_ROOT=/home/paystub/paystub-generator/server/staticfiles
MEDIA_ROOT=/home/paystub/paystub-generator/server/media
```

#### Run Migrations
```bash
sudo -u paystub /home/paystub/paystub-generator/server/venv/bin/python manage.py migrate
```

#### Collect Static Files
```bash
sudo -u paystub /home/paystub/paystub-generator/server/venv/bin/python manage.py collectstatic --noinput
```

#### Create Superuser
```bash
sudo -u paystub /home/paystub/paystub-generator/server/venv/bin/python manage.py createsuperuser
```

### 4. Gunicorn Setup

#### Install Gunicorn
```bash
sudo -u paystub /home/paystub/paystub-generator/server/venv/bin/pip install gunicorn
```

#### Create Gunicorn Service
```bash
sudo nano /etc/systemd/system/paystub.service
```

```ini
[Unit]
Description=Paystub Generator Gunicorn daemon
After=network.target

[Service]
User=paystub
Group=paystub
WorkingDirectory=/home/paystub/paystub-generator/server
Environment="PATH=/home/paystub/paystub-generator/server/venv/bin"
ExecStart=/home/paystub/paystub-generator/server/venv/bin/gunicorn --workers 3 --bind unix:/home/paystub/paystub-generator/server/paystub.sock main.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### Start Gunicorn Service
```bash
sudo systemctl start paystub
sudo systemctl enable paystub
```

### 5. Nginx Configuration

#### Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/paystub
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Static Files
    location /static/ {
        alias /home/paystub/paystub-generator/server/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media Files (if not using S3)
    location /media/ {
        alias /home/paystub/paystub-generator/server/media/;
        expires 30d;
        add_header Cache-Control "public";
    }
    
    # Application
    location / {
        proxy_pass http://unix:/home/paystub/paystub-generator/server/paystub.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
    
    # API Rate Limiting
    location /api/ {
        limit_req zone=api burst=10 nodelay;
        proxy_pass http://unix:/home/paystub/paystub-generator/server/paystub.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Configure Rate Limiting
```bash
sudo nano /etc/nginx/nginx.conf
```

Add to `http` block:
```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
```

#### Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/paystub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL Certificate (Let's Encrypt)

#### Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

#### Obtain Certificate
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

#### Auto-renewal
```bash
sudo crontab -e
```

Add:
```
0 12 * * * /usr/bin/certbot renew --quiet
```

### 7. Monitoring and Logging

#### Log Rotation
```bash
sudo nano /etc/logrotate.d/paystub
```

```
/home/paystub/paystub-generator/server/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 paystub paystub
    postrotate
        systemctl reload paystub
    endscript
}
```

#### Health Check Script
```bash
sudo nano /home/paystub/health_check.sh
```

```bash
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" https://yourdomain.com/api/templates/)
if [ $response -ne 200 ]; then
    echo "Health check failed: $response"
    exit 1
fi
echo "Health check passed"
```

### 8. Backup Strategy

#### Database Backup
```bash
sudo nano /home/paystub/backup_db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/paystub/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U paystub_user paystub_generator > $BACKUP_DIR/db_backup_$DATE.sql
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete
```

#### File Backup (if not using S3)
```bash
sudo nano /home/paystub/backup_files.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/paystub/backups"
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz /home/paystub/paystub-generator/server/media/
find $BACKUP_DIR -name "files_backup_*.tar.gz" -mtime +7 -delete
```

#### Setup Cron Jobs
```bash
sudo crontab -e
```

Add:
```
0 2 * * * /home/paystub/backup_db.sh
0 3 * * * /home/paystub/backup_files.sh
```

## Docker Deployment (Alternative)

### Docker Compose for Production
```yaml
version: '3.8'

services:
  web:
    build: .
    restart: always
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
    depends_on:
      - db
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    networks:
      - paystub_network

  db:
    image: postgres:13
    restart: always
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - paystub_network

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    networks:
      - paystub_network

volumes:
  postgres_data:
  static_volume:
  media_volume:

networks:
  paystub_network:
    driver: bridge
```

## Security Checklist

- [ ] HTTPS enabled with valid SSL certificate
- [ ] Environment variables properly configured
- [ ] Database user has minimal required privileges
- [ ] Firewall configured (UFW recommended)
- [ ] Regular security updates enabled
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting configured
- [ ] Rate limiting enabled
- [ ] Security headers configured
- [ ] File upload validation implemented

## Performance Optimization

### Database
- Add indexes for frequently queried fields
- Configure connection pooling
- Monitor slow queries

### Application
- Use caching (Redis recommended)
- Optimize static file serving
- Implement CDN for static files

### Server
- Configure proper worker processes
- Monitor resource usage
- Set up load balancing if needed

## Troubleshooting

### Common Issues

#### 502 Bad Gateway
- Check Gunicorn service status
- Verify socket file permissions
- Check application logs

#### Database Connection Issues
- Verify database credentials
- Check PostgreSQL service status
- Test connection manually

#### Static Files Not Loading
- Run `collectstatic` command
- Check Nginx configuration
- Verify file permissions

### Log Locations
- Application logs: `/home/paystub/paystub-generator/server/logs/`
- Nginx logs: `/var/log/nginx/`
- System logs: `/var/log/syslog`
- Gunicorn logs: `journalctl -u paystub` 