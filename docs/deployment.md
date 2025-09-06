# Deployment Guide

This guide covers deploying the Bible Baptist Church Barani CMS to production on Ubuntu 24.04 LTS.

## Production Deployment Overview

### Deployment Architecture
```
Internet → Nginx → Gunicorn → Django Application
                ↓
              MySQL Database
                ↓
              Redis Cache
                ↓
              Celery Workers
```

### Prerequisites
- Ubuntu 24.04 LTS server
- Domain name (e.g., bbcbarani.org)
- SSL certificate capability
- Sudo access to server

## Automated Deployment

### One-Command Deployment
```bash
# Clone repository
git clone https://github.com/Artbellsonmamuri/bbcbarani.git
cd bbcbarani

# Run deployment script
sudo bash deploy/scripts/deploy.sh
```

The automated deployment handles:
- System package installation
- Database setup
- Python environment configuration
- Web server setup
- SSL certificate installation
- Service configuration
- Security hardening

## Manual Deployment Steps

### 1. Server Preparation

#### Update system packages
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```

#### Install required packages
```bash
sudo apt install -y \
    python3 python3-pip python3-venv python3-dev \
    mysql-server mysql-client libmysqlclient-dev \
    nginx redis-server git curl \
    certbot python3-certbot-nginx \
    supervisor fail2ban ufw
```

### 2. Database Configuration

#### Secure MySQL installation
```bash
sudo mysql_secure_installation
```

#### Create database and user
```bash
sudo mysql -u root -p

CREATE DATABASE bbcbarani_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'bbcbarani_user'@'localhost' IDENTIFIED BY 'STRONG_PASSWORD_HERE';
GRANT ALL PRIVILEGES ON bbcbarani_db.* TO 'bbcbarani_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Application Setup

#### Create application directory
```bash
sudo mkdir -p /var/www/bbcbarani
sudo mkdir -p /var/log/bbcbarani
sudo mkdir -p /var/backups/bbcbarani
```

#### Clone and setup application
```bash
cd /var/www/bbcbarani
sudo git clone https://github.com/Artbellsonmamuri/bbcbarani.git .
sudo python3 -m venv venv
sudo ./venv/bin/pip install -r requirements.txt
```

#### Configure environment
```bash
sudo cp .env.example .env
sudo nano .env
```

Essential environment variables:
```env
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=bbcbarani.org,www.bbcbarani.org

DB_NAME=bbcbarani_db
DB_USER=bbcbarani_user
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=3306

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

REDIS_URL=redis://localhost:6379/0
```

#### Run Django setup
```bash
cd /var/www/bbcbarani
sudo ./venv/bin/python manage.py migrate --settings=bbcbarani.settings.prod
sudo ./venv/bin/python manage.py collectstatic --noinput --settings=bbcbarani.settings.prod
sudo ./venv/bin/python manage.py createsuperuser --settings=bbcbarani.settings.prod
```

#### Set permissions
```bash
sudo chown -R www-data:www-data /var/www/bbcbarani
sudo chown -R www-data:www-data /var/log/bbcbarani
sudo chmod 600 /var/www/bbcbarani/.env
```

### 4. Web Server Configuration

#### Configure Nginx
```bash
sudo cp /var/www/bbcbarani/deploy/nginx/bbcbarani.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/bbcbarani.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

#### SSL Certificate Setup
```bash
# Install Let's Encrypt certificate
sudo certbot --nginx -d bbcbarani.org -d www.bbcbarani.org

# Set up auto-renewal
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
```

### 5. Application Services

#### Configure systemd services
```bash
sudo cp /var/www/bbcbarani/deploy/systemd/*.service /etc/systemd/system/
sudo cp /var/www/bbcbarani/deploy/systemd/*.socket /etc/systemd/system/
sudo systemctl daemon-reload
```

#### Start services
```bash
sudo systemctl enable bbcbarani.socket
sudo systemctl enable bbcbarani.service
sudo systemctl enable bbcbarani-celery.service
sudo systemctl enable bbcbarani-celerybeat.service

sudo systemctl start bbcbarani.socket
sudo systemctl start bbcbarani.service
sudo systemctl start bbcbarani-celery.service
sudo systemctl start bbcbarani-celerybeat.service
```

### 6. Security Configuration

#### Configure firewall
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

#### Configure fail2ban
```bash
sudo cp /var/www/bbcbarani/deploy/security/fail2ban-bbcbarani.conf /etc/fail2ban/jail.d/
sudo systemctl restart fail2ban
```

### 7. Monitoring and Logging

#### Configure log rotation
```bash
sudo tee /etc/logrotate.d/bbcbarani << EOF
/var/log/bbcbarani/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload bbcbarani.service
    endscript
}
EOF
```

#### Set up backup cron job
```bash
sudo crontab -e
# Add this line:
0 2 * * * /var/www/bbcbarani/deploy/scripts/backup.sh
```

## Docker Deployment

### Docker Compose Setup

#### Create docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=bbcbarani.settings.prod
    env_file:
      - .env
    depends_on:
      - db
      - redis
    volumes:
      - ./media:/app/media
      - ./logs:/app/logs

  db:
    image: mysql:8.0
    restart: unless-stopped
    environment:
      MYSQL_DATABASE: bbcbarani_db
      MYSQL_USER: bbcbarani_user
      MYSQL_PASSWORD: ${DB_PASSWORD}
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deploy/nginx/bbcbarani.conf:/etc/nginx/conf.d/default.conf
      - ./static:/var/www/bbcbarani/static
      - ./media:/var/www/bbcbarani/media
      - ./ssl:/etc/letsencrypt
    depends_on:
      - web

  celery:
    build: .
    restart: unless-stopped
    command: celery -A bbcbarani worker -l info
    environment:
      - DJANGO_SETTINGS_MODULE=bbcbarani.settings.prod
    env_file:
      - .env
    depends_on:
      - db
      - redis
    volumes:
      - ./media:/app/media
      - ./logs:/app/logs

  celerybeat:
    build: .
    restart: unless-stopped
    command: celery -A bbcbarani beat -l info
    environment:
      - DJANGO_SETTINGS_MODULE=bbcbarani.settings.prod
    env_file:
      - .env
    depends_on:
      - db
      - redis
    volumes:
      - ./media:/app/media
      - ./logs:/app/logs

volumes:
  mysql_data:
  redis_data:
```

#### Deploy with Docker
```bash
# Build and start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

## Deployment Verification

### 1. Service Health Checks
```bash
# Check all services are running
sudo systemctl status bbcbarani.service
sudo systemctl status bbcbarani-celery.service
sudo systemctl status nginx
sudo systemctl status mysql
sudo systemctl status redis

# Check ports are listening
sudo netstat -tlnp | grep -E ':80|:443|:3306|:6379'
```

### 2. Application Testing
```bash
# Test Django application
cd /var/www/bbcbarani
sudo -u www-data ./venv/bin/python manage.py check --settings=bbcbarani.settings.prod

# Test database connection
sudo -u www-data ./venv/bin/python manage.py dbshell --settings=bbcbarani.settings.prod

# Test static files
curl -I https://bbcbarani.org/static/css/main.css
```

### 3. API Testing
```bash
# Test API endpoints
curl -X GET https://bbcbarani.org/api/cms/
curl -X POST https://bbcbarani.org/api/prayer/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Test prayer request"}'
```

### 4. Performance Testing
```bash
# Test response times
curl -w "Time: %{time_total}s\n" -o /dev/null -s https://bbcbarani.org/

# Test concurrent connections
ab -n 100 -c 10 https://bbcbarani.org/
```

## Post-Deployment Tasks

### 1. Initial Configuration
1. **Admin Setup**
   - Access admin panel: `https://bbcbarani.org/admin/`
   - Configure site settings
   - Add initial content

2. **User Management**
   - Create additional admin users
   - Set up user roles and permissions

3. **Content Setup**
   - Add church information
   - Create initial blog posts
   - Set up ministries and events

### 2. Email Configuration
```bash
# Test email sending
cd /var/www/bbcbarani
sudo -u www-data ./venv/bin/python manage.py shell --settings=bbcbarani.settings.prod
```

```python
from django.core.mail import send_mail
send_mail(
    'Test Email',
    'Testing email configuration.',
    'no-reply@bbcbarani.org',
    ['admin@bbcbarani.org']
)
```

### 3. Analytics Setup
1. Configure Google Analytics
2. Set up error tracking (Sentry)
3. Monitor application performance

### 4. Backup Verification
```bash
# Test backup script
sudo /var/www/bbcbarani/deploy/scripts/backup.sh

# Test restore process
sudo /var/www/bbcbarani/deploy/scripts/restore.sh /var/backups/bbcbarani/latest
```

## Maintenance Procedures

### Regular Updates
```bash
# Update application code
cd /var/www/bbcbarani
sudo git pull origin main
sudo ./venv/bin/pip install -r requirements.txt
sudo ./venv/bin/python manage.py migrate --settings=bbcbarani.settings.prod
sudo ./venv/bin/python manage.py collectstatic --noinput --settings=bbcbarani.settings.prod
sudo systemctl restart bbcbarani.service
```

### Database Maintenance
```bash
# Optimize database
mysql -u bbcbarani_user -p bbcbarani_db
OPTIMIZE TABLE django_session;
ANALYZE TABLE blog_blogpost;
```

### Log Monitoring
```bash
# Monitor application logs
sudo tail -f /var/log/bbcbarani/django.log

# Monitor Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Monitor system logs
sudo journalctl -u bbcbarani.service -f
```

## Troubleshooting

### Common Issues

#### 502 Bad Gateway
```bash
# Check Gunicorn service
sudo systemctl status bbcbarani.service
sudo journalctl -u bbcbarani.service -n 50

# Check socket file
ls -la /run/gunicorn/bbcbarani.sock
```

#### Database Connection Issues
```bash
# Check MySQL service
sudo systemctl status mysql

# Test database connection
mysql -u bbcbarani_user -p bbcbarani_db
```

#### Static Files Not Loading
```bash
# Check file permissions
sudo ls -la /var/www/bbcbarani/static/

# Recollect static files
cd /var/www/bbcbarani
sudo -u www-data ./venv/bin/python manage.py collectstatic --clear --noinput --settings=bbcbarani.settings.prod
```

#### SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew --nginx --dry-run
```

### Performance Issues
```bash
# Monitor resource usage
htop
df -h
free -h

# Check database performance
mysql -u root -p
SHOW PROCESSLIST;
SHOW ENGINE INNODB STATUS;
```

### Log Analysis
```bash
# Parse error logs
sudo grep -i error /var/log/bbcbarani/django.log | tail -20

# Check failed requests
sudo grep " 5[0-9][0-9] " /var/log/nginx/access.log | tail -10
```

## Rollback Procedures

### Application Rollback
```bash
# Rollback to previous version
cd /var/www/bbcbarani
sudo git log --oneline -n 5
sudo git checkout <previous_commit_hash>
sudo systemctl restart bbcbarani.service
```

### Database Rollback
```bash
# Restore from backup
sudo /var/www/bbcbarani/deploy/scripts/restore.sh /var/backups/bbcbarani/20240101_020000
```

## Security Updates

### System Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
cd /var/www/bbcbarani
sudo ./venv/bin/pip install --upgrade -r requirements.txt
```

### Security Monitoring
```bash
# Check fail2ban status
sudo fail2ban-client status

# Review security logs
sudo grep "Failed password" /var/log/auth.log
```

## Production Checklist

- [ ] All services running and healthy
- [ ] SSL certificate installed and auto-renewal configured
- [ ] Database backups scheduled and tested
- [ ] Monitoring and logging configured
- [ ] Security measures implemented
- [ ] Performance optimizations applied
- [ ] Error tracking configured
- [ ] Email functionality tested
- [ ] API endpoints tested
- [ ] Admin panel accessible
- [ ] Content management tested
- [ ] Mobile responsiveness verified

Your Bible Baptist Church Barani CMS is now successfully deployed to production!
