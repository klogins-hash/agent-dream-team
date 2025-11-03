#!/bin/bash
# Restore script for Agent Dream Team

set -e

if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup-file.tar.gz>"
    exit 1
fi

BACKUP_FILE="$1"
RESTORE_DIR="./restore_temp"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  WARNING: This will overwrite existing data!"
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

echo "🔄 Starting restore from $BACKUP_FILE..."

# Extract backup
echo "📦 Extracting backup..."
mkdir -p "$RESTORE_DIR"
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR"

# Restore PostgreSQL
if [ -f "$RESTORE_DIR"/postgres_*.sql ]; then
    echo "📥 Restoring PostgreSQL..."
    POSTGRES_FILE=$(ls "$RESTORE_DIR"/postgres_*.sql)
    docker exec -i agent-team-postgres psql -U agent_user agent_team < "$POSTGRES_FILE"
fi

# Restore Redis
if [ -f "$RESTORE_DIR"/redis_*.rdb ]; then
    echo "📥 Restoring Redis..."
    REDIS_FILE=$(ls "$RESTORE_DIR"/redis_*.rdb)
    docker cp "$REDIS_FILE" agent-team-redis:/data/dump.rdb
    docker restart agent-team-redis
fi

# Restore Neo4j
if [ -f "$RESTORE_DIR"/neo4j_*.dump ]; then
    echo "📥 Restoring Neo4j..."
    NEO4J_FILE=$(ls "$RESTORE_DIR"/neo4j_*.dump)
    docker cp "$NEO4J_FILE" agent-team-neo4j:/tmp/neo4j.dump
    docker exec agent-team-neo4j neo4j-admin database load neo4j --from-path=/tmp
    docker restart agent-team-neo4j
fi

# Clean up
echo "🧹 Cleaning up..."
rm -rf "$RESTORE_DIR"

echo "✅ Restore completed successfully!"
echo "💡 Restart all services: docker-compose -f docker-compose.prod.yml restart"
