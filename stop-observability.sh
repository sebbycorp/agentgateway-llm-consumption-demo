#!/bin/bash

echo "🛑 Stopping AgentGateway Infrastructure"
echo "======================================="
echo ""

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running."
    exit 1
fi

# Check if any containers are running
if docker ps | grep -qE '(jaeger|presidio)'; then
    echo "📊 Stopping all services..."
    echo "   • Jaeger"
    echo "   • Presidio Analyzer"
    echo "   • Presidio Anonymizer"
    echo ""
    docker compose down
    
    # Wait a moment and verify
    sleep 2
    
    if docker ps | grep -qE '(jaeger|presidio)'; then
        echo "❌ Failed to stop some services"
        exit 1
    else
        echo "✅ All services stopped successfully!"
    fi
else
    echo "ℹ️  No services are running"
fi

echo ""
echo "🧹 Cleanup complete!"
echo ""
echo "💡 To restart infrastructure:"
echo "   ./start-observability.sh"
echo ""

