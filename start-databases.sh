#!/bin/bash
# Start PostgreSQL and Redis for Agent Dream Team

echo "🚀 Starting databases..."
docker-compose up -d

echo "⏳ Waiting for databases to be ready..."
sleep 5

echo "✅ Databases started!"
echo ""
echo "📊 Core Services:"
echo "  PostgreSQL: localhost:5432"
echo "  Redis: localhost:6379"
echo "  Neo4j: bolt://localhost:7687"
echo "  RabbitMQ: localhost:5672"
echo "  Elasticsearch: localhost:9200"
echo "  MinIO: localhost:9000"
echo ""
echo "🌐 Web Interfaces:"
echo "  PgAdmin: http://localhost:5050"
echo "  Redis Commander: http://localhost:8081"
echo "  Neo4j Browser: http://localhost:7474"
echo "  RabbitMQ Management: http://localhost:15672 (user: agent_user)"
echo "  MinIO Console: http://localhost:9001 (user: minioadmin)"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana: http://localhost:3000 (user: admin)"
echo ""
echo "💡 Install Python dependencies:"
echo "  pip install -r requirements_db.txt"
