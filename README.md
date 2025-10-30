# AgentGateway - Complete Demo

This comprehensive demo combines **all** AgentGateway features into a single, cohesive demonstration.

## 🎯 What's Included

### Part 1: Security & Privacy
1. **Privacy & Data Leakage Prevention** - API keys stored securely in gateway
2. **PII Redaction & Data Security** - GDPR/HIPAA compliance with SSN/credit card redaction

### Part 2: Cost Controls
3. **Rate Limiting** - Prevent runaway costs with request throttling
4. **Budget Enforcement** - Per-user spending limits with real-time enforcement
5. **Cost Tracking & Chargeback** - Usage attribution for billing and reporting

### Part 3: Reliability & Flexibility
6. **Multi-Provider Strategy** - Support for multiple AI providers with failover
7. **Centralized Control & Monitoring** - Unified observability and management

## 🚀 Quick Start

### Prerequisites

1. **Docker** - For running Jaeger (observability)
2. **Python 3** - For running the demo
3. **AgentGateway** - Binary installed and in PATH
4. **API Keys** - Set your environment variables:
   ```bash
   export ANTHROPIC_API_KEY='your-anthropic-key'
   export OPENAI_API_KEY='your-openai-key'  # Optional
   ```

### Running the Complete Demo

```bash
# 1. Start observability stack (Jaeger)
./start-observability.sh

# 2. In another terminal, start the gateway
agentgateway --file config.yaml

# 3. Run the complete demo
./run-complete-demo.sh
```

The demo is interactive - you'll be prompted to press Enter between each section.

## 📁 Files Created

### Demo Files
- **`demo_complete.py`** - Complete unified demo with all 7 features
- **`run-complete-demo.sh`** - Launcher script with pre-flight checks
- **`stop-observability.sh`** - Cleanup script to stop Jaeger

### Original Demo Files (Still Available)
- **`demo_proxy.py`** - Original basic demo (privacy, rate limiting, chargeback)
- **`demo_enterprise.py`** - Original enterprise demo (PII, multi-provider, budgets)
- **`run-enterprise-demo.sh`** - Enterprise demo launcher

## 🎬 Demo Flow

The complete demo runs through all features in a logical sequence:

```
🔐 PART 1: SECURITY & PRIVACY
├── Demo 1: Privacy & API Key Protection
│   └── Shows how clients don't need API keys
└── Demo 2: PII Redaction
    └── Demonstrates SSN and credit card redaction

💰 PART 2: COST CONTROLS  
├── Demo 3: Rate Limiting
│   └── Tests 10 req/60s limit with 12 rapid requests
├── Demo 4: Budget Enforcement
│   └── Shows per-user spending limits
└── Demo 5: Cost Tracking & Chargeback
    └── Generates detailed cost reports by user/team

⚡ PART 3: RELIABILITY & FLEXIBILITY
├── Demo 6: Multi-Provider Strategy
│   └── Compares Anthropic vs OpenAI routing
└── Demo 7: Centralized Control
    └── Shows unified observability and management
```

## 📊 Observability

After running the demo, view your observability data:

### Jaeger (Distributed Tracing)
```bash
# Open in browser
open http://localhost:16686
```

### Prometheus Metrics
```bash
# View all GenAI metrics
curl http://localhost:15020/metrics | grep agentgateway_gen_ai

# Specific metrics examples:
curl http://localhost:15020/metrics | grep agentgateway_gen_ai_request_total
curl http://localhost:15020/metrics | grep agentgateway_gen_ai_request_duration
```

### Cost Reports
The demo automatically generates chargeback reports showing:
- Per-user breakdown (requests, tokens, costs)
- Per-team aggregation
- Total costs and usage

## 🧹 Cleanup

When you're done with the demo:

```bash
# Stop Jaeger and cleanup
./stop-observability.sh

# Stop the gateway (Ctrl+C in the gateway terminal)
```

## 🔧 Configuration

### Basic Configuration (`config.yaml`)
- Single Anthropic provider
- Rate limiting: 10 requests/60 seconds
- Jaeger tracing enabled

### Enterprise Configuration (`config-enterprise.yaml`)
- Multi-provider support (Anthropic + OpenAI)
- Rate limiting enabled
- Advanced routing capabilities

Choose the appropriate config when starting the gateway:
```bash
# Basic demo
agentgateway --file config.yaml

# Enterprise features
agentgateway --file config-enterprise.yaml
```

## 💡 Use Cases

This demo is perfect for:

- **Sales demonstrations** - Show all features in one flow
- **Customer onboarding** - Comprehensive feature walkthrough
- **Internal training** - Teach team members about capabilities
- **Proof of concepts** - Validate features for specific requirements
- **Documentation** - Reference implementation of best practices

## 🆚 Comparison with Individual Demos

| Feature | demo_proxy.py | demo_enterprise.py | demo_complete.py |
|---------|---------------|-------------------|------------------|
| API Key Protection | ✅ | ❌ | ✅ |
| PII Redaction | ❌ | ✅ | ✅ |
| Rate Limiting | ✅ | ❌ | ✅ |
| Budget Enforcement | ❌ | ✅ | ✅ |
| Cost Tracking | ✅ | ❌ | ✅ |
| Multi-Provider | ❌ | ✅ | ✅ |
| Centralized Control | ✅ | ❌ | ✅ |
| **Total Features** | **4** | **3** | **7** |

## 📚 Additional Documentation

- **`QUICKSTART.md`** - Basic setup and getting started
- **`ENTERPRISE-QUICKSTART.md`** - Enterprise features guide
- **`OBSERVABILITY.md`** - Detailed observability setup
- **`DEMO.md`** - Original basic demo guide
- **`ENTERPRISE-DEMO.md`** - Original enterprise demo guide

## 🔍 Troubleshooting

### Gateway not starting
```bash
# Check if port 3000 is already in use
lsof -i :3000

# Check API key is set
echo $ANTHROPIC_API_KEY
```

### Jaeger not starting
```bash
# Check if Docker is running
docker ps

# Check if port is in use
lsof -i :16686
```

### Demo script fails
```bash
# Make sure scripts are executable
chmod +x *.sh demo_complete.py

# Check Python version
python3 --version  # Should be 3.7+

# Install required packages if needed
pip3 install requests
```

## 🤝 Contributing

To add new features to the demo:

1. Add the demo function to `demo_complete.py`
2. Update the main() flow to include the new demo
3. Update this README with the new feature
4. Test the complete flow

## 📝 License

Part of the AgentGateway project.

