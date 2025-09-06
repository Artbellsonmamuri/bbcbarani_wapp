#!/bin/bash
# Restore script for Bible Baptist Church Barani CMS
# Run with: bash deploy/scripts/restore.sh /path/to/backup/directory

set -e

# Configuration
PROJECT_NAME="bbcbarani"
PROJECT_DIR="/var/www/${PROJECT_NAME}"
DB_NAME="${PROJECT_NAME}_db"
DB_USER="${PROJECT_NAME}_user"

# Load environment variables
if [ -f "${PROJECT_DIR}/.env" ]; then
    export $(grep -v '^#' ${PROJECT_DIR}/.env | xargs)
fi

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check arguments
if [ $# -ne 1 ]; then
    log_error "Usage: $0 /path/to/backup/directory"
    exit 1
fi

BACKUP_DIR="$1"

if [ ! -d "$BACKUP_DIR" ]; then
    log_error "Backup directory does not exist: $BACKUP_DIR"
    exit 1
fi

# Verify backup directory
verify_backup() {
    log_info "Verifying backup directory..."

    if [ ! -f "${BACKUP_DIR}/database.sql.gz" ]; then
        log_error "Database backup not found in ${BACKUP_DIR}"
        exit 1
    fi

    if [ ! -f "${BACKUP_DIR}/backup_info.txt" ]; then
        log_warning "Backup info file not found"
    else
        log_info "Backup info:"
        cat ${BACKUP_DIR}/backup_info.txt
    fi

    log_info "Backup directory verified"
}

# Confirm restore
confirm_restore() {
    log_warning "This will restore the CMS from backup and OVERWRITE current data!"
    log_warning "Current database and media files will be replaced."
    echo
    read -p "Are you sure you want to continue? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        log_info "Restore cancelled"
        exit 0
    fi

    log_info "Starting restore process..."
}

# Stop services
stop_services() {
    log_info "Stopping CMS services..."

    systemctl stop ${PROJECT_NAME}.service || true
    systemctl stop ${PROJECT_NAME}-celery.service || true
    systemctl stop ${PROJECT_NAME}-celerybeat.service || true

    log_info "Services stopped"
}

# Start services
start_services() {
    log_info "Starting CMS services..."

    systemctl start ${PROJECT_NAME}.service
    systemctl start ${PROJECT_NAME}-celery.service
    systemctl start ${PROJECT_NAME}-celerybeat.service

    log_info "Services started"
}

# Restore database
restore_database() {
    log_info "Restoring database..."

    # Create a backup of current database
    log_info "Creating backup of current database..."
    mysqldump \
        --user=${DB_USER} \
        --password=${DB_PASSWORD} \
        ${DB_NAME} > /tmp/${DB_NAME}_pre_restore_$(date +%Y%m%d_%H%M%S).sql

    # Drop and recreate database
    mysql -u ${DB_USER} -p${DB_PASSWORD} -e "DROP DATABASE IF EXISTS ${DB_NAME};"
    mysql -u ${DB_USER} -p${DB_PASSWORD} -e "CREATE DATABASE ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

    # Restore from backup
    gunzip -c ${BACKUP_DIR}/database.sql.gz | mysql -u ${DB_USER} -p${DB_PASSWORD} ${DB_NAME}

    log_info "Database restored successfully"
}

# Restore media files
restore_media() {
    log_info "Restoring media files..."

    if [ -f "${BACKUP_DIR}/media.tar.gz" ]; then
        # Backup current media directory
        if [ -d "${PROJECT_DIR}/media" ]; then
            log_info "Backing up current media directory..."
            mv ${PROJECT_DIR}/media ${PROJECT_DIR}/media_backup_$(date +%Y%m%d_%H%M%S)
        fi

        # Extract media backup
        tar -xzf ${BACKUP_DIR}/media.tar.gz -C ${PROJECT_DIR}/

        # Set permissions
        chown -R www-data:www-data ${PROJECT_DIR}/media
        chmod -R 755 ${PROJECT_DIR}/media

        log_info "Media files restored successfully"
    else
        log_warning "No media backup found"
    fi
}

# Restore configuration files
restore_config() {
    log_info "Restoring configuration files..."

    if [ -d "${BACKUP_DIR}/config" ]; then
        # Backup current config files
        log_info "Backing up current configuration..."

        if [ -f "${PROJECT_DIR}/.env" ]; then
            cp ${PROJECT_DIR}/.env ${PROJECT_DIR}/.env.backup.$(date +%Y%m%d_%H%M%S)
        fi

        # Restore config files (be careful with .env)
        if [ -f "${BACKUP_DIR}/config/.env" ]; then
            read -p "Do you want to restore the .env file? (yes/no): " restore_env
            if [ "$restore_env" = "yes" ]; then
                cp ${BACKUP_DIR}/config/.env ${PROJECT_DIR}/
                chown www-data:www-data ${PROJECT_DIR}/.env
                chmod 600 ${PROJECT_DIR}/.env
                log_info "Environment file restored"
            fi
        fi

        log_info "Configuration files processed"
    else
        log_warning "No configuration backup found"
    fi
}

# Run Django migrations and collect static
post_restore_django() {
    log_info "Running Django post-restore tasks..."

    cd ${PROJECT_DIR}
    source venv/bin/activate

    # Run migrations
    python manage.py migrate --settings=bbcbarani.settings.prod

    # Collect static files
    python manage.py collectstatic --noinput --settings=bbcbarani.settings.prod

    # Clear cache
    python manage.py shell --settings=bbcbarani.settings.prod -c "from django.core.cache import cache; cache.clear()"

    log_info "Django post-restore tasks completed"
}

# Verify restore
verify_restore() {
    log_info "Verifying restore..."

    # Check if Django can start
    cd ${PROJECT_DIR}
    source venv/bin/activate
    python manage.py check --settings=bbcbarani.settings.prod

    if [ $? -eq 0 ]; then
        log_info "Django check passed"
    else
        log_error "Django check failed"
        exit 1
    fi

    # Check if services are running
    sleep 5

    for service in ${PROJECT_NAME}.service ${PROJECT_NAME}-celery.service ${PROJECT_NAME}-celerybeat.service; do
        if systemctl is-active --quiet $service; then
            log_info "$service is running"
        else
            log_error "$service is not running"
            systemctl status $service
        fi
    done

    log_info "Restore verification completed"
}

# Main function
main() {
    log_info "Starting restore process for Bible Baptist Church Barani CMS..."
    log_info "Backup directory: $BACKUP_DIR"

    verify_backup
    confirm_restore
    stop_services
    restore_database
    restore_media
    restore_config
    post_restore_django
    start_services
    verify_restore

    log_info "Restore completed successfully!"
    log_info ""
    log_info "Your CMS has been restored from backup."
    log_info "Please check the website and admin panel to ensure everything is working correctly."
    log_info "Website: https://bbcbarani.org"
    log_info "Admin: https://bbcbarani.org/admin/"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root (use sudo)"
    exit 1
fi

# Run main function
main "$@"
