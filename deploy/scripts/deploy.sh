#!/bin/bash
# Deployment script for Bible Baptist Church Barani CMS
# Run with: bash deploy/scripts/deploy.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="bbcbarani"
PROJECT_DIR="/var/www/${PROJECT_NAME}"
VENV_DIR="${PROJECT_DIR}/venv"
BACKUP_DIR="/var/backups/${PROJECT_NAME}"
NGINX_SITE="/etc/nginx/sites-available/${PROJECT_NAME}.conf"
SYSTEMD_DIR="/etc/systemd/system"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

install_dependencies() {
    log_info "Installing system dependencies..."

    # Update system
    apt-get update

    # Install required packages
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        mysql-server \
        mysql-client \
        libmysqlclient-dev \
        nginx \
        redis-server \
        git \
        curl \
        certbot \
        python3-certbot-nginx \
        supervisor \
        logrotate \
        fail2ban

    # Install Node.js (for frontend build tools if needed)
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    apt-get install -y nodejs

    log_info "System dependencies installed successfully"
}

setup_mysql() {
    log_info "Setting up MySQL database..."

    # Check if database exists
    if mysql -e "USE ${PROJECT_NAME}_db;" 2>/dev/null; then
        log_warning "Database ${PROJECT_NAME}_db already exists"
    else
        mysql -e "CREATE DATABASE ${PROJECT_NAME}_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        log_info "Database created successfully"
    fi

    # Create database user (if not exists)
    if mysql -e "SELECT User FROM mysql.user WHERE User='${PROJECT_NAME}_user';" | grep -q "${PROJECT_NAME}_user"; then
        log_warning "Database user ${PROJECT_NAME}_user already exists"
    else
        read -s -p "Enter password for database user ${PROJECT_NAME}_user: " DB_PASSWORD
        echo
        mysql -e "CREATE USER '${PROJECT_NAME}_user'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';"
        mysql -e "GRANT ALL PRIVILEGES ON ${PROJECT_NAME}_db.* TO '${PROJECT_NAME}_user'@'localhost';"
        mysql -e "FLUSH PRIVILEGES;"
        log_info "Database user created successfully"
    fi
}

setup_project() {
    log_info "Setting up project directory..."

    # Create project directory
    mkdir -p ${PROJECT_DIR}
    mkdir -p ${BACKUP_DIR}
    mkdir -p /var/log/${PROJECT_NAME}
    mkdir -p /var/run/celery
    mkdir -p /var/log/celery

    # Set ownership
    chown -R www-data:www-data ${PROJECT_DIR}
    chown -R www-data:www-data /var/log/${PROJECT_NAME}
    chown -R www-data:www-data /var/run/celery
    chown -R www-data:www-data /var/log/celery

    # Set permissions
    chmod -R 755 ${PROJECT_DIR}

    log_info "Project directory setup completed"
}

setup_python_environment() {
    log_info "Setting up Python virtual environment..."

    cd ${PROJECT_DIR}

    # Create virtual environment
    python3 -m venv ${VENV_DIR}
    source ${VENV_DIR}/bin/activate

    # Upgrade pip
    pip install --upgrade pip setuptools wheel

    # Install Python dependencies
    pip install -r requirements.txt

    log_info "Python environment setup completed"
}

setup_django() {
    log_info "Setting up Django application..."

    cd ${PROJECT_DIR}
    source ${VENV_DIR}/bin/activate

    # Collect static files
    python manage.py collectstatic --noinput --settings=bbcbarani.settings.prod

    # Run migrations
    python manage.py migrate --settings=bbcbarani.settings.prod

    # Create superuser (if needed)
    if python manage.py shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.filter(is_superuser=True).exists())" --settings=bbcbarani.settings.prod | grep -q "False"; then
        log_info "Creating Django superuser..."
        python manage.py createsuperuser --settings=bbcbarani.settings.prod
    else
        log_warning "Superuser already exists"
    fi

    log_info "Django setup completed"
}

setup_nginx() {
    log_info "Setting up Nginx..."

    # Copy Nginx configuration
    cp deploy/nginx/${PROJECT_NAME}.conf ${NGINX_SITE}

    # Enable site
    ln -sf ${NGINX_SITE} /etc/nginx/sites-enabled/${PROJECT_NAME}.conf

    # Remove default site if exists
    rm -f /etc/nginx/sites-enabled/default

    # Test Nginx configuration
    nginx -t

    # Restart Nginx
    systemctl restart nginx
    systemctl enable nginx

    log_info "Nginx setup completed"
}

setup_ssl() {
    log_info "Setting up SSL certificate..."

    # Get SSL certificate with Certbot
    certbot --nginx -d bbcbarani.org -d www.bbcbarani.org --non-interactive --agree-tos --email admin@bbcbarani.org

    # Setup automatic renewal
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

    log_info "SSL setup completed"
}

setup_systemd() {
    log_info "Setting up systemd services..."

    # Copy systemd service files
    cp deploy/systemd/${PROJECT_NAME}.service ${SYSTEMD_DIR}/
    cp deploy/systemd/${PROJECT_NAME}.socket ${SYSTEMD_DIR}/
    cp deploy/systemd/${PROJECT_NAME}-celery.service ${SYSTEMD_DIR}/
    cp deploy/systemd/${PROJECT_NAME}-celerybeat.service ${SYSTEMD_DIR}/

    # Create gunicorn run directory
    mkdir -p /run/gunicorn
    chown www-data:www-data /run/gunicorn

    # Reload systemd and enable services
    systemctl daemon-reload

    # Enable and start services
    systemctl enable ${PROJECT_NAME}.socket
    systemctl enable ${PROJECT_NAME}.service
    systemctl enable ${PROJECT_NAME}-celery.service
    systemctl enable ${PROJECT_NAME}-celerybeat.service

    systemctl start ${PROJECT_NAME}.socket
    systemctl start ${PROJECT_NAME}.service
    systemctl start ${PROJECT_NAME}-celery.service
    systemctl start ${PROJECT_NAME}-celerybeat.service

    log_info "Systemd services setup completed"
}

setup_logrotate() {
    log_info "Setting up log rotation..."

    cat > /etc/logrotate.d/${PROJECT_NAME} << EOF
/var/log/${PROJECT_NAME}/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 www-data www-data
}

/var/log/celery/${PROJECT_NAME}*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload ${PROJECT_NAME}-celery.service
        systemctl reload ${PROJECT_NAME}-celerybeat.service
    endscript
}
EOF

    log_info "Log rotation setup completed"
}

setup_security() {
    log_info "Setting up security configurations..."

    # Configure fail2ban
    cat > /etc/fail2ban/jail.d/${PROJECT_NAME}.conf << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true

[nginx-noscript]
enabled = true

[nginx-badbots]
enabled = true

[nginx-noproxy]
enabled = true
EOF

    # Restart fail2ban
    systemctl restart fail2ban
    systemctl enable fail2ban

    # Set up firewall rules (basic UFW configuration)
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 'Nginx Full'
    ufw --force enable

    log_info "Security setup completed"
}

main() {
    log_info "Starting deployment of Bible Baptist Church Barani CMS..."

    check_root
    install_dependencies
    setup_mysql
    setup_project
    setup_python_environment
    setup_django
    setup_nginx
    setup_ssl
    setup_systemd
    setup_logrotate
    setup_security

    log_info "Deployment completed successfully!"
    log_info "Your CMS is now available at: https://bbcbarani.org"
    log_info "Admin panel: https://bbcbarani.org/admin/"
    log_info ""
    log_info "Next steps:"
    log_info "1. Configure your .env file with proper settings"
    log_info "2. Set up regular backups with backup.sh"
    log_info "3. Monitor logs in /var/log/${PROJECT_NAME}/"
    log_info "4. Test all functionality"
}

# Run main function
main "$@"
