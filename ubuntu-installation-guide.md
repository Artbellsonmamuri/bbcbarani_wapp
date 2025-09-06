# Bible Baptist Church CMS - Ubuntu LTS Installation Guide

## 🚀 Complete Installation Instructions

**Repository:** https://github.com/Artbellsonmamuri/bbcbarani_wapp.git  
**Target System:** Ubuntu 24.04 LTS  
**Installation Type:** Production-Ready Deployment  

---

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 24.04 LTS (or 22.04 LTS)
- **RAM**: Minimum 2GB (4GB+ recommended)
- **Storage**: Minimum 20GB free space
- **Network**: Internet connection for package downloads
- **Access**: SSH/sudo access to the server

---

## 🛠️ Step 1: System Preparation

### Update System Packages
```bash
sudo apt update
sudo apt upgrade -y
sudo reboot
```

### Install Essential System Dependencies
```bash
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    mysql-server \
    mysql-client \
    libmysqlclient-dev \
    pkg-config \
    nginx \
    redis-server \
    git \
    curl \
    wget \
    unzip \
    certbot \
    python3-certbot-nginx \
    supervisor \
    fail2ban \
    ufw \
    htop \
    tree
```

---

## 🗄️ Step 2: Database Configuration

### Secure MySQL Installation
```bash
sudo mysql_secure_installation
```
**Follow prompts:**
- Set root password: `Yes` (use a strong password)
- Remove anonymous users: `Yes`
- Disallow root login remotely: `Yes` 
- Remove test database: `Yes`
- Reload privilege tables: `Yes`

### Create Database and User
```bash
sudo mysql -u root -p
```

**In MySQL shell, run these commands:**
```sql
-- Create database
CREATE DATABASE bbcbarani_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user (replace 'STRONG_PASSWORD' with your password)
CREATE USER 'bbcbarani_user'@'localhost' IDENTIFIED BY 'STRONG_PASSWORD';

-- Grant privileges
GRANT ALL PRIVILEGES ON bbcbarani_db.* TO 'bbcbarani_user'@'localhost';
FLUSH PRIVILEGES;

-- Verify database creation
SHOW DATABASES;
EXIT;
```

### Test Database Connection
```bash
mysql -u bbcbarani_user -p bbcbarani_db
# Enter your password, then type 'EXIT;' to quit
```

---

## 📁 Step 3: Project Setup

### Create Project Directory
```bash
sudo mkdir -p /var/www/bbcbarani
sudo chown $USER:$USER /var/www/bbcbarani
cd /var/www/bbcbarani
```

### Clone Repository
```bash
git clone https://github.com/Artbellsonmamuri/bbcbarani_wapp.git .
```

### Verify Repository Structure
```bash
ls -la
# Should show: manage.py, requirements.txt, bbcbarani/, apps/, etc.
```

---

## 🐍 Step 4: Python Environment Setup

### Create Virtual Environment
```bash
cd /var/www/bbcbarani
python3 -m venv venv
source venv/bin/activate
```

### Upgrade pip and Install Dependencies
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**If you encounter any dependency issues, try:**
```bash
pip install --upgrade pip
pip install wheel
pip install mysqlclient
pip install -r requirements.txt --no-cache-dir
```

---

## ⚙️ Step 5: Django Configuration

### Configure Environment Variables
```bash
cp .env.example .env
nano .env
```

**Edit the .env file with your settings:**
```env
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-change-this-now-very-long-and-random
DJANGO_SETTINGS_MODULE=bbcbarani.settings.prod
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,SERVER_IP_ADDRESS

# Database Configuration
DB_NAME=bbcbarani_db
DB_USER=bbcbarani_user
DB_PASSWORD=STRONG_PASSWORD_YOU_SET_ABOVE
DB_HOST=localhost
DB_PORT=3306

# Email Configuration (Gmail example)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=Bible Baptist Church Barani <no-reply@your-domain.com>

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Church Information
CHURCH_NAME=Bible Baptist Church Barani
CHURCH_ADDRESS=Your Church Address Here
CHURCH_PHONE=+1 (555) 123-4567
CHURCH_EMAIL=info@your-domain.com

# Social Media (Optional)
FACEBOOK_URL=https://facebook.com/your-church
TWITTER_URL=https://twitter.com/your-church
YOUTUBE_URL=https://youtube.com/your-church
```

**Save and exit:** `Ctrl + X`, then `Y`, then `Enter`

### Set Secure Permissions on .env
```bash
chmod 600 .env
```

### Generate Django Secret Key
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print('SECRET_KEY=' + get_random_secret_key())"
```
**Copy the generated key and update your .env file**

---

## 🔧 Step 6: Django Application Setup

### Run Database Migrations
```bash
source venv/bin/activate
python manage.py migrate --settings=bbcbarani.settings.prod
```

### Create Django Superuser
```bash
python manage.py createsuperuser --settings=bbcbarani.settings.prod
```
**Enter:**
- Username (e.g., `admin`)
- Email address 
- Password (make it strong!)

### Collect Static Files
```bash
python manage.py collectstatic --noinput --settings=bbcbarani.settings.prod
```

### Test Django Application
```bash
python manage.py runserver 0.0.0.0:8000 --settings=bbcbarani.settings.prod
```
**Test in browser:** `http://YOUR_SERVER_IP:8000`  
**Stop with:** `Ctrl + C`

---

## 🌐 Step 7: Web Server Configuration

### Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/bbcbarani
```

**Add this configuration (replace YOUR_DOMAIN with your actual domain):**
```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN www.YOUR_DOMAIN;
    
    # Redirect HTTP to HTTPS (will be configured later)
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name YOUR_DOMAIN www.YOUR_DOMAIN;
    
    # SSL Configuration (certificates will be added later)
    ssl_certificate /etc/letsencrypt/live/YOUR_DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/YOUR_DOMAIN/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    
    # Client upload size
    client_max_body_size 10M;
    
    # Static files
    location /static/ {
        alias /var/www/bbcbarani/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/bbcbarani/media/;
        expires 1M;
        add_header Cache-Control "public";
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### Enable the Site
```bash
sudo ln -s /etc/nginx/sites-available/bbcbarani /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 Step 8: SSL Certificate (Let's Encrypt)

### Install SSL Certificate
```bash
# Replace YOUR_DOMAIN with your actual domain
sudo certbot --nginx -d YOUR_DOMAIN -d www.YOUR_DOMAIN
```

**Follow prompts:**
- Enter email address for notifications
- Agree to terms: `A`
- Share email with EFF: `Y` or `N` (your choice)

### Test SSL Auto-Renewal
```bash
sudo certbot renew --dry-run
```

### Schedule Auto-Renewal
```bash
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
```

---

## 🔧 Step 9: Production Server Setup

### Create Gunicorn Configuration
```bash
nano /var/www/bbcbarani/gunicorn.conf.py
```

**Add this configuration:**
```python
# Gunicorn configuration for Bible Baptist Church CMS
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 60
keepalive = 2
preload_app = True
user = "www-data"
group = "www-data"
tmp_upload_dir = None
secure_scheme_headers = {
    'X-FORWARDED-PROTO': 'https',
}
```

### Create Systemd Service
```bash
sudo nano /etc/systemd/system/bbcbarani.service
```

**Add this configuration:**
```ini
[Unit]
Description=Bible Baptist Church CMS
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/bbcbarani
Environment=DJANGO_SETTINGS_MODULE=bbcbarani.settings.prod
EnvironmentFile=/var/www/bbcbarani/.env
ExecStart=/var/www/bbcbarani/venv/bin/gunicorn \
    --config /var/www/bbcbarani/gunicorn.conf.py \
    --access-logfile /var/log/bbcbarani/access.log \
    --error-logfile /var/log/bbcbarani/error.log \
    bbcbarani.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

### Create Log Directory
```bash
sudo mkdir -p /var/log/bbcbarani
sudo chown www-data:www-data /var/log/bbcbarani
```

### Set File Permissions
```bash
sudo chown -R www-data:www-data /var/www/bbcbarani
sudo chmod -R 755 /var/www/bbcbarani
sudo chmod 600 /var/www/bbcbarani/.env
```

### Start and Enable Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable bbcbarani.service
sudo systemctl start bbcbarani.service
sudo systemctl enable nginx
sudo systemctl enable mysql
sudo systemctl enable redis-server
```

---

## 🛡️ Step 10: Security Configuration

### Configure Firewall
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### Configure fail2ban
```bash
sudo nano /etc/fail2ban/jail.local
```

**Add this configuration:**
```ini
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-noscript]
enabled = true
```

```bash
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban
```

---

## 📊 Step 11: Additional Setup

### Configure Redis
```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### Create Media Directory
```bash
mkdir -p /var/www/bbcbarani/media
sudo chown -R www-data:www-data /var/www/bbcbarani/media
```

### Setup Log Rotation
```bash
sudo nano /etc/logrotate.d/bbcbarani
```

**Add this configuration:**
```
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
```

---

## ✅ Step 12: Verification and Testing

### Check Service Status
```bash
sudo systemctl status bbcbarani.service
sudo systemctl status nginx
sudo systemctl status mysql
sudo systemctl status redis-server
```

### Test Website Access
1. **Visit your domain:** `https://your-domain.com`
2. **Admin panel:** `https://your-domain.com/admin/`
3. **API test:** `https://your-domain.com/api/cms/`

### Check Logs
```bash
# Application logs
sudo tail -f /var/log/bbcbarani/error.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u bbcbarani.service -f
```

### Performance Test
```bash
curl -I https://your-domain.com
```

---

## 🎯 Step 13: Initial Configuration

### Login to Admin Panel
1. Visit `https://your-domain.com/admin/`
2. Login with the superuser credentials you created
3. Configure your church information
4. Add initial content and users

### Create Additional Users
- Go to **Users** in admin panel
- Create accounts for church staff
- Assign appropriate roles (Admin, Ministry Lead, Member)

### Configure Content
- **Welcome Section**: Add church welcome message
- **Services**: Add service times and locations  
- **Ministries**: Add your church ministries
- **About**: Add church mission and vision
- **Contact**: Add contact information

---

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Issue: Gunicorn Won't Start
```bash
# Check for errors
sudo journalctl -u bbcbarani.service -n 20

# Test manually
cd /var/www/bbcbarani
source venv/bin/activate
python manage.py check --settings=bbcbarani.settings.prod
```

#### Issue: Database Connection Error
```bash
# Test database connection
mysql -u bbcbarani_user -p bbcbarani_db

# Check settings
cd /var/www/bbcbarani
grep DB_ .env
```

#### Issue: Static Files Not Loading
```bash
# Recollect static files
cd /var/www/bbcbarani
source venv/bin/activate
python manage.py collectstatic --clear --settings=bbcbarani.settings.prod

# Check permissions
ls -la /var/www/bbcbarani/static/
```

#### Issue: SSL Certificate Problems
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew
```

### Getting Help
- Check logs: `/var/log/bbcbarani/error.log`
- System logs: `sudo journalctl -u bbcbarani.service`
- Nginx logs: `/var/log/nginx/error.log`

---

## 🔄 Maintenance Tasks

### Regular Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
cd /var/www/bbcbarani
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Restart application
sudo systemctl restart bbcbarani.service
```

### Database Backup
```bash
# Create backup script
sudo nano /usr/local/bin/backup-bbcbarani.sh
```

**Add backup script:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u bbcbarani_user -p bbcbarani_db > /var/backups/bbcbarani_$DATE.sql
tar -czf /var/backups/bbcbarani_files_$DATE.tar.gz /var/www/bbcbarani/media/
find /var/backups/ -name "bbcbarani_*" -mtime +30 -delete
```

```bash
sudo chmod +x /usr/local/bin/backup-bbcbarani.sh
sudo mkdir -p /var/backups
```

### Schedule Automatic Backups
```bash
sudo crontab -e
# Add this line for daily backups at 2 AM:
0 2 * * * /usr/local/bin/backup-bbcbarani.sh
```

---

## 🎉 Installation Complete!

### What You Have Now
✅ **Fully functional Bible Baptist Church CMS**  
✅ **Secure HTTPS with SSL certificate**  
✅ **Production-ready configuration**  
✅ **Automated backups and security**  
✅ **Professional admin panel**  
✅ **Mobile-responsive design**  
✅ **Complete API for future mobile app**  

### Next Steps
1. **Configure church content** in admin panel
2. **Train staff** on content management
3. **Add church photos** and media
4. **Set up email notifications**
5. **Customize theme** and colors
6. **Test all functionality**
7. **Announce launch** to congregation

### Support
- **Admin Panel**: `https://your-domain.com/admin/`
- **Documentation**: Check `docs/` directory
- **Repository**: https://github.com/Artbellsonmamuri/bbcbarani_wapp.git

---

**Congratulations! Your Bible Baptist Church CMS is now live and ready to serve your community! 🎊**