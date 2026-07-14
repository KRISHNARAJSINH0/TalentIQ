#!/bin/bash

# Configuration
BACKUP_DIR="/var/backups/resumeai"
DB_CONTAINER="resumeai_db_prod"
DB_NAME="resumeai_db"
DB_USER="postgres"
MEDIA_DIR="/app/media"
RETENTION_DAYS=7
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create backup directory if it does not exist
mkdir -p "$BACKUP_DIR"

echo "Starting ResumeAI Backup - $TIMESTAMP"

# 1. Database Backup (pg_dump)
DB_BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"
echo "Backing up database to $DB_BACKUP_FILE..."

if [ "$(docker ps -q -f name=$DB_CONTAINER)" ]; then
    docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$DB_BACKUP_FILE"
else
    # Fallback to local pg_dump if not inside docker
    pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$DB_BACKUP_FILE"
fi

if [ $? -eq 0 ]; then
    echo "Database backup successful."
else
    echo "Database backup failed!" >&2
fi

# 2. Media Files Backup
MEDIA_BACKUP_FILE="$BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz"
echo "Backing up media files to $MEDIA_BACKUP_FILE..."

if [ -d "$MEDIA_DIR" ]; then
    tar -czf "$MEDIA_BACKUP_FILE" -C "$(dirname "$MEDIA_DIR")" "$(basename "$MEDIA_DIR")"
    if [ $? -eq 0 ]; then
        echo "Media backup successful."
    else
        echo "Media backup failed!" >&2
    fi
else
    echo "Media directory $MEDIA_DIR not found. Skipping media backup."
fi

# 3. Cleanup & Retention Policy (Keep last RETENTION_DAYS backups)
echo "Applying retention policy (keeping last $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -name "*.gz" -delete

echo "Backup process finished."
