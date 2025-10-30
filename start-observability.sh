#!/bin/bash

echo "🚀 Starting AgentGateway with Jaeger Observability"
echo "=================================================="
echo ""

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start Jaeger
echo "📊 Starting Jaeger..."
docker compose up -d

# Wait for Jaeger to be ready
echo "⏳ Waiting for Jaeger to start..."
sleep 3

# Check if Jaeger is running
if docker ps | grep -q jaeger; then
    echo "✅ Jaeger is running!"
    echo ""
    echo "🔗 Access Points:"
    echo "   Jaeger UI:  http://localhost:16686"
    echo "   Metrics:    http://localhost:15020/metrics (after starting gateway)"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Start the gateway: agentgateway --file config.yaml"
    echo "   2. Run the demo: python3 demo_proxy.py"
    echo "   3. View traces in Jaeger UI: http://localhost:16686"
    echo ""
else
    echo "❌ Failed to start Jaeger"
    exit 1
fi

