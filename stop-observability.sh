#!/bin/bash

echo "🛑 Stopping AgentGateway Observability Stack"
echo "============================================"
echo ""

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running."
    exit 1
fi

# Check if Jaeger container is running
if docker ps | grep -q jaeger; then
    echo "📊 Stopping Jaeger..."
    docker compose down
    
    # Wait a moment and verify
    sleep 2
    
    if docker ps | grep -q jaeger; then
        echo "❌ Failed to stop Jaeger"
        exit 1
    else
        echo "✅ Jaeger stopped successfully!"
    fi
else
    echo "ℹ️  Jaeger is not running"
fi

echo ""
echo "🧹 Cleanup complete!"
echo ""
echo "💡 To restart observability:"
echo "   ./start-observability.sh"
echo ""

