#!/bin/bash

echo "🚀 AgentGateway Complete Demo Setup"
echo "===================================="
echo ""

# Check API keys
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY not set"
    echo "   Run: export ANTHROPIC_API_KEY='your-key-here'"
    exit 1
fi

echo "✅ ANTHROPIC_API_KEY configured"

# OpenAI is optional for this demo
if [ -z "$OPENAI_API_KEY" ]; then
    echo "ℹ️  OPENAI_API_KEY not set (optional - multi-provider demo will be limited)"
else
    echo "✅ OPENAI_API_KEY configured"
fi

echo ""

# Check if gateway is running
if ! curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo "⚠️  Gateway not detected on port 3000"
    echo ""
    echo "Please start the gateway in another terminal:"
    echo "  agentgateway --file config.yaml"
    echo ""
    read -p "Press Enter when gateway is started..."
fi

echo "✅ Gateway is running"
echo ""

# Check if Jaeger is running (optional)
if docker ps | grep -q jaeger; then
    echo "✅ Jaeger observability is running"
    echo "   View traces: http://localhost:16686"
else
    echo "ℹ️  Jaeger not running (optional)"
    echo "   To enable: ./start-observability.sh"
fi

echo ""
echo "🎬 Starting Complete AgentGateway Demo..."
echo ""
echo "This comprehensive demo includes:"
echo ""
echo "  PART 1: SECURITY & PRIVACY"
echo "    1. Privacy & Data Leakage Prevention"
echo "    2. PII Redaction & Data Security"
echo ""
echo "  PART 2: COST CONTROLS"
echo "    3. Rate Limiting"
echo "    4. Budget Enforcement"
echo "    5. Cost Tracking & Chargeback"
echo ""
echo "  PART 3: RELIABILITY & FLEXIBILITY"
echo "    6. Multi-Provider Strategy"
echo "    7. Centralized Control & Monitoring"
echo ""
echo "Press Ctrl+C to stop at any time"
echo ""
sleep 2

# Run the complete demo
python3 demo_complete.py

echo ""
echo "✅ Complete demo finished!"
echo ""
echo "📊 Next steps:"
echo "  • View traces: http://localhost:16686"
echo "  • View metrics: curl http://localhost:15020/metrics | grep agentgateway_gen_ai"
echo "  • Stop observability: ./stop-observability.sh"
echo "  • Read documentation: cat QUICKSTART.md"
echo ""

