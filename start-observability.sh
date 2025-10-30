#!/bin/bash

echo "🚀 Starting AgentGateway Infrastructure"
echo "======================================="
echo ""

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start all services
echo "📊 Starting services..."
echo "   • Jaeger (Observability)"
echo "   • Presidio Analyzer (PII Detection)"
echo "   • Presidio Anonymizer (PII Redaction)"
echo ""
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 5

# Check if services are running
services_ok=true

if docker ps | grep -q jaeger; then
    echo "✅ Jaeger is running"
else
    echo "❌ Jaeger failed to start"
    services_ok=false
fi

if docker ps | grep -q presidio-analyzer; then
    echo "✅ Presidio Analyzer is running"
else
    echo "❌ Presidio Analyzer failed to start"
    services_ok=false
fi

if docker ps | grep -q presidio-anonymizer; then
    echo "✅ Presidio Anonymizer is running"
else
    echo "❌ Presidio Anonymizer failed to start"
    services_ok=false
fi

if [ "$services_ok" = true ]; then
    echo ""
    echo "🔗 Access Points:"
    echo "   Jaeger UI:           http://localhost:16686"
    echo "   Presidio Analyzer:   http://localhost:5001"
    echo "   Presidio Anonymizer: http://localhost:5002"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Start the gateway: agentgateway --file config.yaml"
    echo "   2. Run the demo: ./run-complete-demo.sh"
    echo "   3. View traces in Jaeger UI: http://localhost:16686"
    echo ""
else
    echo ""
    echo "❌ Some services failed to start"
    exit 1
fi

