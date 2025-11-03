#!/bin/bash
# Backup script for Agent Dream Team

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"

echo "🔄 Starting backup..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup PostgreSQL
echo "📦 Backing up PostgreSQL..."
docker exec agent-team-postgres pg_dump -U agent_user agent_team > "$BACKUP_DIR/postgres_$TIMESTAMP.sql"

# Backup Redis
echo "📦 Backing up Redis..."
docker exec agent-team-redis redis-cli --rdb /data/dump.rdb SAVE
docker cp agent-team-redis:/data/dump.rdb "$BACKUP_DIR/redis_$TIMESTAMP.rdb"

# Backup Neo4j
echo "📦 Backing up Neo4j..."
docker exec agent-team-neo4j neo4j-admin database dump neo4j --to-path=/tmp
docker cp agent-team-neo4j:/tmp/neo4j.dump "$BACKUP_DIR/neo4j_$TIMESTAMP.dump"

# Backup MinIO
echo "📦 Backing up MinIO..."
docker exec agent-team-minio mc mirror /data "$BACKUP_DIR/minio_$TIMESTAMP"

# Backup application data
echo "📦 Backing up application data..."
cp -r agent_sessions "$BACKUP_DIR/agent_sessions_$TIMESTAMP" 2>/dev/null || true
cp .env "$BACKUP_DIR/env_$TIMESTAMP" 2>/dev/null || true

# Create compressed archive
echo "🗜️  Compressing backup..."
tar -czf "$BACKUP_FILE" -C "$BACKUP_DIR" \
    "postgres_$TIMESTAMP.sql" \
    "redis_$TIMESTAMP.rdb" \
    "neo4j_$TIMESTAMP.dump" \
    "env_$TIMESTAMP" 2>/dev/null || true

# Clean up individual files
rm -f "$BACKUP_DIR/postgres_$TIMESTAMP.sql"
rm -f "$BACKUP_DIR/redis_$TIMESTAMP.rdb"
rm -f "$BACKUP_DIR/neo4j_$TIMESTAMP.dump"
rm -f "$BACKUP_DIR/env_$TIMESTAMP"
rm -rf "$BACKUP_DIR/minio_$TIMESTAMP"
rm -rf "$BACKUP_DIR/agent_sessions_$TIMESTAMP"

# Keep only last 7 backups
echo "🧹 Cleaning old backups..."
ls -t "$BACKUP_DIR"/backup_*.tar.gz | tail -n +8 | xargs -r rm

echo "✅ Backup completed: $BACKUP_FILE"
echo "📊 Backup size: $(du -h "$BACKUP_FILE" | cut -f1)"
