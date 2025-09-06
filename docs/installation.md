# Installation Guide

This guide provides detailed instructions for installing the Bible Baptist Church Barani CMS on various environments.

## System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04 LTS or higher (Ubuntu 24.04 LTS recommended)
- **Python**: 3.9 or higher
- **Memory**: 2GB RAM (4GB recommended)
- **Storage**: 10GB free space (20GB recommended)
- **Database**: MySQL 8.0 or higher

### Recommended Production Requirements
- **OS**: Ubuntu 24.04 LTS
- **CPU**: 2+ cores
- **Memory**: 4GB+ RAM
- **Storage**: 50GB+ SSD
- **Database**: MySQL 8.0 with dedicated server
- **Web Server**: Nginx with SSL certificate

## Pre-Installation Setup

### 1. Update System Packages
```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install System Dependencies
```bash
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    mysql-server \
    mysql-client \
    libmysqlclient-dev \
    build-essential \
    git \
    curl \
    nginx \
    redis-server \
    certbot \
    python3-certbot-nginx
```

### 3. Configure MySQL

#### Start and secure MySQL
```bash
sudo systemctl start mysql
sudo systemctl enable mysql
sudo mysql_secure_installation
```

#### Create database and user
```bash
# Connect to MySQL as root
sudo mysql -u root -p

# Create database
CREATE DATABASE bbcbarani_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user (replace 'your_password' with a strong password)
CREATE USER 'bbcbarani_user'@'localhost' IDENTIFIED BY 'your_password';

# Grant privileges
GRANT ALL PRIVILEGES ON bbcbarani_db.* TO 'bbcbarani_user'@'localhost';
FLUSH PRIVILEGES;

# Exit MySQL
EXIT;
```

### 4. Configure Redis
```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping
# Should return: PONG
```

## Installation Methods

### Method 1: Automated Installation (Recommended)

The automated installation script handles the complete setup process:

```bash
# Clone the repository
git clone https://github.com/Artbellsonmamuri/bbcbarani.git
cd bbcbarani

# Run the automated deployment script
sudo bash deploy/scripts/deploy.sh
```

The script will:
- Install all dependencies
- Configure the database
- Set up the virtual environment
- Configure Nginx and SSL
- Set up systemd services
- Configure security settings

### Method 2: Manual Installation

For more control over the installation process:

#### 1. Clone Repository
```bash
git clone https://github.com/Artbellsonmamuri/bbcbarani.git
cd bbcbarani
```

#### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Python Dependencies
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
```bash
# Copy environment template
cp .env.example .env

# Edit environment file
nano .env
```

Configure the following key variables:
```env
# Django Settings
DEBUG=False
SECRET_KEY=your-very-secure-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database Settings
DB_NAME=bbcbarani_db
DB_USER=bbcbarani_user
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=3306

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=Bible Baptist Church <no-reply@bbcbarani.org>

# Redis Settings
REDIS_URL=redis://localhost:6379/0

# External Services
GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX
```

#### 5. Run Django Setup
```bash
# Run database migrations
python manage.py migrate --settings=bbcbarani.settings.prod

# Create superuser account
python manage.py createsuperuser --settings=bbcbarani.settings.prod

# Collect static files
python manage.py collectstatic --noinput --settings=bbcbarani.settings.prod

# Test Django setup
python manage.py check --settings=bbcbarani.settings.prod
```

#### 6. Configure Nginx

Create Nginx configuration:
```bash
sudo cp deploy/nginx/bbcbarani.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/bbcbarani.conf /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

#### 7. Set up SSL Certificate
```bash
# Install SSL certificate with Let's Encrypt
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Set up automatic renewal
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
```

#### 8. Configure Systemd Services
```bash
# Copy systemd service files
sudo cp deploy/systemd/bbcbarani.service /etc/systemd/system/
sudo cp deploy/systemd/bbcbarani.socket /etc/systemd/system/
sudo cp deploy/systemd/bbcbarani-celery.service /etc/systemd/system/
sudo cp deploy/systemd/bbcbarani-celerybeat.service /etc/systemd/system/

# Create gunicorn run directory
sudo mkdir -p /run/gunicorn
sudo chown www-data:www-data /run/gunicorn

# Reload systemd and start services
sudo systemctl daemon-reload
sudo systemctl enable bbcbarani.socket
sudo systemctl enable bbcbarani.service
sudo systemctl enable bbcbarani-celery.service
sudo systemctl enable bbcbarani-celerybeat.service

sudo systemctl start bbcbarani.socket
sudo systemctl start bbcbarani.service
sudo systemctl start bbcbarani-celery.service
sudo systemctl start bbcbarani-celerybeat.service
```

#### 9. Set Permissions
```bash
# Create project directories
sudo mkdir -p /var/www/bbcbarani
sudo mkdir -p /var/log/bbcbarani
sudo mkdir -p /var/backups/bbcbarani

# Copy project files
sudo cp -r . /var/www/bbcbarani/

# Set ownership
sudo chown -R www-data:www-data /var/www/bbcbarani
sudo chown -R www-data:www-data /var/log/bbcbarani

# Set permissions
sudo chmod -R 755 /var/www/bbcbarani
sudo chmod 600 /var/www/bbcbarani/.env
```

## Development Installation

For local development:

### 1. Clone and Setup
```bash
git clone https://github.com/Artbellsonmamuri/bbcbarani.git
cd bbcbarani

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Development Environment
```bash
cp .env.example .env
# Edit .env for development settings
```

### 3. Setup Development Database
```bash
# For development, you can use SQLite
python manage.py migrate --settings=bbcbarani.settings.dev
python manage.py createsuperuser --settings=bbcbarani.settings.dev
```

### 4. Run Development Server
```bash
python manage.py runserver --settings=bbcbarani.settings.dev
```

Visit `http://localhost:8000` to access the development site.

## Docker Installation (Alternative)

For containerized deployment:

### 1. Create Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-mysql-client \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --settings=bbcbarani.settings.prod

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "bbcbarani.wsgi:application"]
```

### 2. Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=mysql://user:password@db:3306/bbcbarani
    depends_on:
      - db
      - redis
    volumes:
      - ./media:/app/media
      - ./static:/app/static

  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: bbcbarani
      MYSQL_USER: user
      MYSQL_PASSWORD: password
      MYSQL_ROOT_PASSWORD: rootpassword
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7-alpine

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deploy/nginx/bbcbarani.conf:/etc/nginx/conf.d/default.conf
      - ./static:/var/www/bbcbarani/static
      - ./media:/var/www/bbcbarani/media
    depends_on:
      - web

volumes:
  mysql_data:
```

### 3. Run with Docker
```bash
docker-compose up -d
```

## Post-Installation Setup

### 1. Verify Installation
```bash
# Check service status
sudo systemctl status bbcbarani.service
sudo systemctl status bbcbarani-celery.service
sudo systemctl status nginx

# Check logs
sudo journalctl -u bbcbarani.service -f
```

### 2. Access Admin Panel
- Visit: `https://yourdomain.com/admin/`
- Login with the superuser account created during installation

### 3. Configure Initial Content
1. **Site Settings**: Configure church information, contact details
2. **Users**: Create additional admin users
3. **Content**: Add welcome message, about us, ministries
4. **Theme**: Customize colors and styling
5. **Email**: Test email configuration

### 4. Set up Monitoring
```bash
# Set up log rotation
sudo cp deploy/logrotate/bbcbarani /etc/logrotate.d/

# Configure backup schedule
(crontab -l 2>/dev/null; echo "0 2 * * * /var/www/bbcbarani/deploy/scripts/backup.sh") | crontab -
```

## Troubleshooting

### Common Issues

#### Database Connection Error
```bash
# Check MySQL service
sudo systemctl status mysql

# Check database exists
mysql -u bbcbarani_user -p
USE bbcbarani_db;
SHOW TABLES;
```

#### Permission Errors
```bash
# Fix file permissions
sudo chown -R www-data:www-data /var/www/bbcbarani
sudo chmod -R 755 /var/www/bbcbarani
sudo chmod 600 /var/www/bbcbarani/.env
```

#### Service Not Starting
```bash
# Check service logs
sudo journalctl -u bbcbarani.service -n 50

# Check configuration
sudo systemctl status bbcbarani.service
```

#### SSL Certificate Issues
```bash
# Renew certificate manually
sudo certbot renew --nginx

# Check certificate status
sudo certbot certificates
```

### Getting Help

If you encounter issues:
1. Check the [troubleshooting section](troubleshooting.md)
2. Review log files in `/var/log/bbcbarani/`
3. Contact support at admin@bbcbarani.org
4. Open an issue on GitHub

## Next Steps

After successful installation:
1. Read the [User Manual](user-manual.md) for content management
2. Review the [API Documentation](api.md) for integration
3. Set up regular [backups and maintenance](maintenance.md)
4. Configure [monitoring and alerts](monitoring.md)

Congratulations! Your Bible Baptist Church Barani CMS is now installed and ready to use.
