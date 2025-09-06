#!/bin/bash
# Backup script for Bible Baptist Church Barani CMS
# Run with: bash deploy/scripts/backup.sh

set -e

# Configuration
PROJECT_NAME="bbcbarani"
PROJECT_DIR="/var/www/${PROJECT_NAME}"
BACKUP_DIR="/var/backups/${PROJECT_NAME}"
DB_NAME="${PROJECT_NAME}_db"
DB_USER="${PROJECT_NAME}_user"
RETENTION_DAYS=30

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

# Create backup directory
create_backup_dir() {
    local backup_date=$(date +%Y%m%d_%H%M%S)
    CURRENT_BACKUP_DIR="${BACKUP_DIR}/${backup_date}"
    mkdir -p ${CURRENT_BACKUP_DIR}
    log_info "Created backup directory: ${CURRENT_BACKUP_DIR}"
}

# Backup database
backup_database() {
    log_info "Backing up database..."

    mysqldump \
        --user=${DB_USER} \
        --password=${DB_PASSWORD} \
        --single-transaction \
        --routines \
        --triggers \
        ${DB_NAME} > ${CURRENT_BACKUP_DIR}/database.sql

    # Compress database backup
    gzip ${CURRENT_BACKUP_DIR}/database.sql

    log_info "Database backup completed"
}

# Backup media files
backup_media() {
    log_info "Backing up media files..."

    if [ -d "${PROJECT_DIR}/media" ]; then
        tar -czf ${CURRENT_BACKUP_DIR}/media.tar.gz -C ${PROJECT_DIR} media/
        log_info "Media backup completed"
    else
        log_warning "Media directory not found"
    fi
}

# Backup configuration files
backup_config() {
    log_info "Backing up configuration files..."

    # Create config backup directory
    mkdir -p ${CURRENT_BACKUP_DIR}/config

    # Backup environment file
    if [ -f "${PROJECT_DIR}/.env" ]; then
        cp ${PROJECT_DIR}/.env ${CURRENT_BACKUP_DIR}/config/
    fi

    # Backup nginx configuration
    if [ -f "/etc/nginx/sites-available/${PROJECT_NAME}.conf" ]; then
        cp /etc/nginx/sites-available/${PROJECT_NAME}.conf ${CURRENT_BACKUP_DIR}/config/
    fi

    # Backup systemd services
    cp /etc/systemd/system/${PROJECT_NAME}*.service ${CURRENT_BACKUP_DIR}/config/ 2>/dev/null || true
    cp /etc/systemd/system/${PROJECT_NAME}*.socket ${CURRENT_BACKUP_DIR}/config/ 2>/dev/null || true

    log_info "Configuration backup completed"
}

# Create backup summary
create_backup_info() {
    log_info "Creating backup information file..."

    cat > ${CURRENT_BACKUP_DIR}/backup_info.txt << EOF
Bible Baptist Church Barani CMS Backup
=====================================

Backup Date: $(date)
Backup Directory: ${CURRENT_BACKUP_DIR}
Project Directory: ${PROJECT_DIR}
Database: ${DB_NAME}

Files included:
- Database dump (database.sql.gz)
- Media files (media.tar.gz)
- Configuration files (config/)

Backup created by: $(whoami)
Server: $(hostname)
EOF

    log_info "Backup information file created"
}

# Clean old backups
cleanup_old_backups() {
    log_info "Cleaning up old backups (keeping last ${RETENTION_DAYS} days)..."

    find ${BACKUP_DIR} -type d -name "20*" -mtime +${RETENTION_DAYS} -exec rm -rf {} + 2>/dev/null || true

    log_info "Old backups cleaned up"
}

# Verify backup
verify_backup() {
    log_info "Verifying backup integrity..."

    # Check if database backup exists and is valid
    if [ -f "${CURRENT_BACKUP_DIR}/database.sql.gz" ]; then
        gunzip -t ${CURRENT_BACKUP_DIR}/database.sql.gz
        if [ $? -eq 0 ]; then
            log_info "Database backup is valid"
        else
            log_error "Database backup is corrupted"
            exit 1
        fi
    fi

    # Check media backup
    if [ -f "${CURRENT_BACKUP_DIR}/media.tar.gz" ]; then
        tar -tzf ${CURRENT_BACKUP_DIR}/media.tar.gz > /dev/null
        if [ $? -eq 0 ]; then
            log_info "Media backup is valid"
        else
            log_error "Media backup is corrupted"
            exit 1
        fi
    fi

    log_info "Backup verification completed"
}

# Send notification (optional)
send_notification() {
    log_info "Sending backup notification..."

    # Calculate backup size
    local backup_size=$(du -sh ${CURRENT_BACKUP_DIR} | cut -f1)

    # Email notification (requires mail command to be configured)
    if command -v mail &> /dev/null; then
        echo "Bible Baptist Church CMS backup completed successfully.

Backup Details:
- Date: $(date)
- Location: ${CURRENT_BACKUP_DIR}
- Size: ${backup_size}
- Files: Database, Media, Configuration

The backup has been verified and is ready for use if needed." | \
        mail -s "CMS Backup Completed - $(date +%Y-%m-%d)" admin@bbcbarani.org
    fi
}

# Main function
main() {
    log_info "Starting backup process for Bible Baptist Church Barani CMS..."

    create_backup_dir
    backup_database
    backup_media
    backup_config
    create_backup_info
    verify_backup
    cleanup_old_backups
    send_notification

    local backup_size=$(du -sh ${CURRENT_BACKUP_DIR} | cut -f1)

    log_info "Backup completed successfully!"
    log_info "Backup location: ${CURRENT_BACKUP_DIR}"
    log_info "Backup size: ${backup_size}"
    log_info ""
    log_info "To restore from this backup, run:"
    log_info "bash deploy/scripts/restore.sh ${CURRENT_BACKUP_DIR}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    log_warning "Running as root. Consider running as www-data user for better security."
fi

# Run main function
main "$@"
