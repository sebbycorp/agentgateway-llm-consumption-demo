# Quick Start: AgentGateway Demo

Run this demo in **4 simple steps** to see data protection, cost controls, and observability in action!

## Step 1: Start Jaeger (Observability)
```bash
./start-observability.sh
```

Or manually with docker compose:
```bash
docker compose up -d
```

This starts Jaeger on:
- 🔍 **Jaeger UI**: http://localhost:16686

## Step 2: Set Your API Key
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

## Step 3: Start the Gateway
```bash
agentgateway --file config.yaml
```

You should see output like:
```
🚀 AgentGateway started on port 3000
✅ Anthropic backend configured
✅ Rate limiting: 10 req/60s
✅ Tracing enabled (OTLP endpoint: http://localhost:4317)
```

## Step 4: Run the Demo (in a new terminal)
```bash
python3 demo_proxy.py
```

## 🎯 What You'll See

### ✅ Security in Action
- Requests succeed WITHOUT API keys in client code
- Keys are hidden and managed by the gateway
- Prevents data leakage from clients

### ✅ Cost Controls
- Rate limiting kicks in after 10 requests
- Protects against runaway costs
- Shows real-time request throttling

### ✅ Privacy Protection
- Only metadata is logged (no sensitive content)
- Compliant with data privacy regulations
- Full audit trail without exposing data

### ✅ Cost Tracking & Chargeback 💰
- Track usage per user and team
- Calculate actual costs based on token usage
- Generate detailed chargeback reports
- Identify high-usage users and teams

### ✅ Observability with Jaeger 🔍
- Distributed tracing for all LLM requests
- Token usage metrics (input/output)
- Request/response latency tracking
- Visual trace timeline in Jaeger UI

## 🔧 Quick Configuration Changes

### Test Stricter Rate Limits
Edit `config.yaml` line 10-13:
```yaml
localRateLimit:
  - maxTokens: 5         # Only 5 requests
    tokensPerFill: 5
    fillInterval: 60s    # per minute
```

### Allow More Requests
```yaml
localRateLimit:
  - maxTokens: 100       # 100 requests
    tokensPerFill: 100
    fillInterval: 60s    # per minute
```

## 💡 Test It Yourself

### Manual cURL Test
```bash
# Request through gateway (no API key needed!)
curl -X POST http://localhost:3000/v1/messages \
  -H "Content-Type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 1024,
    "messages": [{
      "role": "user",
      "content": "Say hello!"
    }]
  }'
```

### Trigger Rate Limiting
```bash
# Run this 11 times quickly to hit the rate limit
for i in {1..11}; do
  echo "Request $i"
  curl -X POST http://localhost:3000/v1/messages \
    -H "Content-Type: application/json" \
    -H "anthropic-version: 2023-06-01" \
    -d '{"model": "claude-haiku-4-5-20251001", "max_tokens": 100, "messages": [{"role": "user", "content": "Hi"}]}'
  echo ""
done
```

## 🚨 Troubleshooting

### Gateway won't start
- ✅ Check if port 3000 is already in use: `lsof -i :3000`
- ✅ Verify ANTHROPIC_API_KEY is set: `echo $ANTHROPIC_API_KEY`

### Demo script fails
- ✅ Is the gateway running? Check terminal window
- ✅ Install requests: `pip3 install requests`
- ✅ Check gateway is on port 3000: `curl http://localhost:3000/v1/models`

### Rate limit not working
- ✅ Wait 60 seconds for window to reset
- ✅ Check config.yaml has localRateLimit section
- ✅ Restart gateway after config changes

## 🔍 View Observability Data

### Jaeger UI (Traces)
Open http://localhost:16686 and:
1. Select "agentgateway" from the Service dropdown
2. Click "Find Traces" to see all LLM requests
3. Click on a trace to see detailed timing breakdown

### Metrics
View LLM token usage metrics:
```bash
curl http://localhost:15020/metrics | grep agentgateway_gen_ai
```

Key metrics:
- `agentgateway_gen_ai_client_token_usage`: Token usage histogram
- `agentgateway_gen_ai_server_request_duration`: Request duration
- Labels: `gen_ai_token_type` (input/output), `gen_ai_system` (anthropic)

## 📚 Learn More

- Full documentation: `DEMO.md`
- Configuration options: `config.yaml`
- Gateway docs: https://agentgateway.dev/docs/llm/observability/

---

**🎉 That's it! You now have a secure AI proxy with cost controls, privacy protection, and full observability!**

