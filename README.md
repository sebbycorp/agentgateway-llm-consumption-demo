# AgentGateway Complete Demo

> Production-ready LLM API management with security, cost controls, and observability

A comprehensive demonstration showcasing **7 enterprise features** of AgentGateway + Microsoft Presidio for building secure, cost-effective LLM applications.

## 🎯 What You'll Learn

This demo shows you how to:
- 🔒 **Secure API keys** and prevent data leakage
- 🛡️ **Detect and redact PII** with ML-powered tools (Microsoft Presidio)
- 💰 **Control costs** with rate limiting and budget enforcement
- 📊 **Track spending** per user/team for chargeback
- ⚡ **Route to multiple providers** (Anthropic, OpenAI, Grok)
- 🔭 **Monitor everything** with distributed tracing (Jaeger)

## 🚀 Quick Start

### Prerequisites

```bash
# Required
✓ Docker Desktop (for Jaeger + Presidio)
✓ Python 3.7+
✓ AgentGateway binary (download from GitHub releases)
✓ Anthropic API key

# Optional (for multi-provider demo)
○ OpenAI API key
○ xAI API key (Grok)
```

### Installation

```bash
# 1. Set your API keys
export ANTHROPIC_API_KEY='your-key-here'
export OPENAI_API_KEY='your-key-here'      # Optional
export XAI_API_KEY='your-key-here'         # Optional

# 2. Start infrastructure (Jaeger + Presidio)
./start-observability.sh

# This starts 3 services:
#   • Jaeger (port 16686) - Distributed tracing
#   • Presidio Analyzer (port 5001) - PII detection
#   • Presidio Anonymizer (port 5002) - PII redaction

# 3. In another terminal, start the gateway
agentgateway --file config.yaml

# 4. Run the complete demo
./run-complete-demo.sh
```

## 📋 Demo Features

### Part 1: Security & Privacy 🔐

#### 1. API Key Protection
- Keys stored server-side in gateway
- Clients never handle credentials
- Prevents key exposure in browser/mobile apps
- Easy key rotation (config update only)

#### 2. PII Redaction with Microsoft Presidio
- **ML-powered detection** of 50+ entity types
- Detects: SSN, credit cards, emails, phones, names, locations, IPs, etc.
- **Sidecar architecture** - scales independently
- **Battle-tested** - used by Microsoft in production
- **Fallback to regex** if Presidio unavailable
- **GDPR/HIPAA/SOC2 compliant**

### Part 2: Cost Controls 💰

#### 3. Rate Limiting
- Token bucket algorithm (10 req/60s default)
- Prevents runaway costs from bugs
- DDoS protection
- Returns 429 when exceeded

#### 4. Budget Enforcement
- Per-user spending limits
- Real-time cost tracking
- Automatic request blocking
- Simulated users: alice, bob, charlie, etc.

#### 5. Cost Tracking & Chargeback
- **8 users across 6 teams** (engineering, marketing, sales, data-science, support, product)
- Per-user and per-team reports
- Token usage breakdown
- Export-ready for billing systems

### Part 3: Reliability & Flexibility ⚡

#### 6. Multi-Provider Strategy
- Tests Anthropic, OpenAI, and Grok (xAI)
- Cost comparison across providers
- Automatic failover capabilities
- No client code changes needed

#### 7. Centralized Observability
- OpenTelemetry distributed tracing
- Jaeger UI for request visualization
- Prometheus metrics (tokens, latency, costs)
- Complete audit trail

## 🏗️ Architecture

```
Client Application
      ↓
Application Layer (demo_complete.py)
      ↓
Presidio Analyzer (5001) ←→ Jaeger (16686)
      ↓ (detected PII)
Presidio Anonymizer (5002)
      ↓ (clean text)
AgentGateway (3000)
      ↓ (authenticated, rate-limited)
LLM Providers
  • Anthropic Claude (3000/v1/messages)
  • OpenAI GPT (3000/openai/v1/chat/completions)
  • Grok (3000/grok/v1/chat/completions)
```

**See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed diagrams and deployment patterns.**

## 📊 What You'll See

### Demo 1: Privacy Protection
```
📋 REQUEST DETAILS:
   Query: "What is 2+2? Answer in one sentence."
   User ID: demo-user
   API Key in client code: ❌ None (handled by gateway)

✅ SUCCESS! Request completed without client having API key!
```

### Demo 2: PII Redaction
```
======================================================================
📋 TEST CASE 1: SSN in prompt
======================================================================

❌ ORIGINAL QUERY (contains PII):
   "My social security number is 123-45-6789..."

✅ REDACTED QUERY (PII removed):
   "My social security number is <SSN>..."

🔍 PII Protection:
   • Social Security Numbers → <SSN>

✅ Request successful - LLM never saw sensitive data!
```

### Demo 5: Cost Tracking & Chargeback
```
============================================================
  💳 CHARGEBACK REPORT
============================================================
Total Requests: 24
Total Cost: $0.012847

PER-USER BREAKDOWN
User            Requests   Input    Output   Cost        
------------------------------------------------------------
frank           2          95       685      $0.002816   
diana           2          88       623      $0.002562   
alice           2          82       571      $0.002350   
...

PER-TEAM BREAKDOWN
Team                 Requests        Total Cost     
------------------------------------------------------------
marketing            3               $0.004076      
sales                2               $0.002816      
engineering          3               $0.003542      
...
```

### Demo 6: Multi-Provider Comparison
```
💡 COST COMPARISON (same query across providers)
======================================================================
🥇 OpenAI GPT-4o-mini         $0.000026
🥈 Anthropic Claude Haiku     $0.000172
🥉 Grok 2 (xAI)              $0.000200

💰 Savings: $0.000174 (86.9%) by choosing cheapest
   At 1000 requests/day: $174.00/month saved
```

## 🔧 Configuration

### Gateway Config (`config.yaml`)

```yaml
config:
  tracing:
    otlpEndpoint: http://localhost:4317
    randomSampling: true

binds:
- port: 3000
  listeners:
  - routes:
    # Anthropic with rate limiting
    - policies:
        localRateLimit:
          - maxTokens: 10
            tokensPerFill: 10
            fillInterval: 60s
        backendAuth:
          key: "$ANTHROPIC_API_KEY"
      backends:
      - ai:
          provider:
            anthropic:
              model: claude-haiku-4-5-20251001
```

### Infrastructure (`docker-compose.yaml`)

```yaml
services:
  # Observability
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports: ["16686:16686", "4317:4317"]
  
  # PII Detection (Sidecar Pattern)
  presidio-analyzer:
    image: mcr.microsoft.com/presidio-analyzer:latest
    ports: ["5001:5001"]
    
  presidio-anonymizer:
    image: mcr.microsoft.com/presidio-anonymizer:latest
    ports: ["5002:5002"]
```

## 📁 Project Structure

```
agentgateway-oss/
├── README.md                    # ← You are here (Starter Guide)
├── BLOG-POST.md                 # Marketing/publication content
├── ARCHITECTURE.md              # Technical deep dive
│
├── demo_complete.py             # Complete unified demo
├── run-complete-demo.sh         # Demo launcher with pre-checks
│
├── start-observability.sh       # Start Jaeger + Presidio
├── stop-observability.sh        # Cleanup all services
│
├── config.yaml                  # AgentGateway configuration
└── docker-compose.yaml          # Infrastructure (Jaeger + Presidio)
```

## 🔍 Exploring Results

### Jaeger UI (Distributed Tracing)
```bash
open http://localhost:16686

# Search for:
- Service: "agentgateway"
- Operation: "gen_ai.request"
- Look for: Rate limited requests (429 status)
```

### Presidio APIs (PII Detection)
```bash
# Test PII detection directly
curl -X POST http://localhost:5001/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "My SSN is 123-45-6789",
    "language": "en",
    "entities": ["US_SSN"]
  }'

# Test PII redaction
curl -X POST http://localhost:5002/anonymize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "My SSN is 123-45-6789",
    "anonymizers": {"US_SSN": {"type": "replace", "new_value": "<SSN>"}}
  }'
```

### Prometheus Metrics
```bash
# View GenAI metrics
curl http://localhost:15020/metrics | grep agentgateway_gen_ai

# Key metrics:
# - agentgateway_gen_ai_request_total
# - agentgateway_gen_ai_request_duration_bucket
# - agentgateway_gen_ai_usage_input_tokens
# - agentgateway_gen_ai_usage_output_tokens
```

## 🧹 Cleanup

```bash
# Stop all infrastructure
./stop-observability.sh

# Stop gateway (Ctrl+C in gateway terminal)
```

## 🆘 Troubleshooting

### "Connection refused" to Presidio
```bash
# Check if Presidio containers are running
docker ps | grep presidio

# If not running, restart infrastructure
./stop-observability.sh
./start-observability.sh
```

### "Rate limited" errors
```bash
# Expected behavior! This demonstrates rate limiting.
# Wait 60 seconds for token bucket to refill.
```

### Gateway won't start
```bash
# Check if port 3000 is in use
lsof -i :3000

# Verify API keys are set
echo $ANTHROPIC_API_KEY
```

### Demo fails on budget enforcement
```bash
# This is expected! Charlie has a low budget ($0.02)
# The demo shows automatic blocking when limits are reached.
```

## 💡 Use Cases

Perfect for:
- **Sales Demos** - Complete feature showcase in 10 minutes
- **Customer Onboarding** - Interactive feature walkthrough
- **Proof of Concepts** - Validate specific requirements
- **Training** - Teach teams about LLM gateway patterns
- **Reference Implementation** - Production deployment patterns

## 📚 Additional Resources

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Complete technical architecture, deployment patterns, scaling strategies
- **[BLOG-POST.md](./BLOG-POST.md)** - Publication-ready content with real-world impact stories
- **[AgentGateway Docs](https://agentgateway.dev)** - Official documentation
- **[Microsoft Presidio](https://github.com/microsoft/presidio)** - PII detection/anonymization

## 🎓 Learning Path

1. **Run the Demo** → `./run-complete-demo.sh` to see all features
2. **Explore Traces** → Open Jaeger UI to understand request flows
3. **Test Presidio** → Use curl to test PII detection directly
4. **Customize Config** → Edit `config.yaml` to try different settings
5. **Review Architecture** → Read `ARCHITECTURE.md` for deployment patterns
6. **Integrate** → Apply patterns to your production environment

## 🎯 Key Takeaways

After running this demo, you'll understand:

✅ How to secure LLM API keys in production  
✅ How to detect and redact PII using ML (Presidio)  
✅ How to prevent cost overruns with rate limiting  
✅ How to enforce per-user budget limits  
✅ How to track and allocate LLM costs by team  
✅ How to route across multiple LLM providers  
✅ How to monitor everything with distributed tracing  

## 🤝 Contributing

This demo is part of AgentGateway OSS. Contributions welcome!

- 🐛 Report bugs: [GitHub Issues](https://github.com/solo-io/agentgateway/issues)
- 💡 Suggest features: [GitHub Discussions](https://github.com/solo-io/agentgateway/discussions)
- 📖 Improve docs: Submit a PR

## 📝 License

Apache 2.0 - See LICENSE file for details

---

**Ready to get started?** 

```bash
./start-observability.sh
agentgateway --file config.yaml
./run-complete-demo.sh
```

🚀 **Let's go!**
