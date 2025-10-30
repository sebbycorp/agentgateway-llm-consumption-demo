# AgentGateway Observability Guide

Complete guide to monitoring and observability for AgentGateway, based on the [official documentation](https://agentgateway.dev/docs/llm/observability/).

## 🎯 What You Can Observe

1. **Traces** - Request flow and timing via Jaeger
2. **Metrics** - Token usage and performance metrics
3. **Logs** - Request/response details in stdout

## 🚀 Quick Start

### 1. Start Jaeger

```bash
./start-observability.sh
```

Or manually:
```bash
docker compose up -d
```

### 2. Configure Gateway

The `config.yaml` already includes tracing:

```yaml
config:
  tracing:
    otlpEndpoint: http://localhost:4317
    randomSampling: true
```

### 3. Start Gateway

```bash
agentgateway --file config.yaml
```

### 4. Send Requests

```bash
python3 demo_proxy.py
```

## 🔍 Viewing Traces in Jaeger

### Access Jaeger UI
Open http://localhost:16686

### Finding Traces
1. Select **Service**: `agentgateway`
2. Click **Find Traces**
3. Click on any trace to see details

### What You'll See

Each trace shows:
- **Total duration** of the request
- **Span breakdown**:
  - Gateway processing time
  - Backend (Anthropic) request time
  - Response time
- **Tags** including:
  - `http.method`: POST
  - `http.url`: The endpoint
  - `gen_ai.system`: anthropic
  - `gen_ai.request.model`: claude-haiku-4-5-20251001
  - `gen_ai.response.model`: claude-haiku-4-5-20251001
- **Logs** within spans
- **Errors** if any occurred

### Trace Examples

#### Successful Request
```
agentgateway
├─ POST /v1/messages (2.3s)
   ├─ backend: anthropic (2.1s)
   │  ├─ input_tokens: 25
   │  └─ output_tokens: 450
   └─ response: 200 OK
```

#### Rate Limited Request
```
agentgateway
├─ POST /v1/messages (20ms)
   └─ error: rate limit exceeded
       status: 429
```

## 📊 Viewing Metrics

### Access Metrics Endpoint

AgentGateway exposes metrics on port **15020** (stats port):

```bash
curl http://localhost:15020/metrics
```

### Key LLM Metrics

#### Token Usage Histogram
```bash
curl http://localhost:15020/metrics | grep agentgateway_gen_ai_client_token_usage
```

**Metric Structure**:
```
agentgateway_gen_ai_client_token_usage_bucket{
  gen_ai_operation_name="chat",
  gen_ai_request_model="claude-haiku-4-5-20251001",
  gen_ai_response_model="claude-haiku-4-5-20251001",
  gen_ai_system="anthropic",
  gen_ai_token_type="input",
  le="1000"
} 15
```

**Labels Explained**:
- `gen_ai_token_type`: 
  - `input` - Tokens in the request (prompt)
  - `output` - Tokens in the response (completion)
- `gen_ai_operation_name`: The operation type (e.g., `chat`, `completion`)
- `gen_ai_system`: The LLM provider (e.g., `anthropic`, `openai`)
- `gen_ai_request_model`: Model specified in request
- `gen_ai_response_model`: Model used by provider

### Calculating Costs from Metrics

You can use the token metrics to calculate costs:

```bash
# Get input tokens
INPUT_TOKENS=$(curl -s http://localhost:15020/metrics | \
  grep 'gen_ai_token_type="input"' | \
  grep '_sum' | \
  awk '{print $2}')

# Get output tokens  
OUTPUT_TOKENS=$(curl -s http://localhost:15020/metrics | \
  grep 'gen_ai_token_type="output"' | \
  grep '_sum' | \
  awk '{print $2}')

# Calculate cost (Anthropic Claude Haiku pricing)
COST=$(echo "scale=6; ($INPUT_TOKENS * 0.80 / 1000000) + ($OUTPUT_TOKENS * 4.00 / 1000000)" | bc)

echo "Total Cost: \$$COST"
```

## 📝 Viewing Logs

### Stdout Logs

AgentGateway automatically logs to stdout. View in your terminal where the gateway is running.

### Successful Request Log
```
2025-10-30T14:30:08.686967Z info request 
  gateway=bind/3000 
  listener=listener0 
  route_rule=route0/default 
  route=route0 
  endpoint=api.anthropic.com:443 
  src.addr=127.0.0.1:54140 
  http.method=POST 
  http.host=0.0.0.0 
  http.path=/v1/messages 
  http.version=HTTP/1.1 
  http.status=200 
  llm.provider=anthropic 
  llm.request.model=claude-haiku-4-5-20251001 
  llm.request.tokens=25 
  llm.response.model=claude-haiku-4-5-20251001 
  llm.response.tokens=450 
  duration=2305ms
```

### Rate Limited Request Log
```
2025-10-30T14:40:18.687849Z info request 
  gateway=bind/3000 
  listener=listener0 
  route_rule=route0/default 
  route=route0 
  endpoint=api.anthropic.com:443 
  src.addr=127.0.0.1:51794 
  http.method=POST 
  http.host=0.0.0.0 
  http.path=/v1/messages 
  http.version=HTTP/1.1 
  http.status=429 
  error=rate limit exceeded 
  duration=20ms
```

### Log Fields for Cost Tracking

Key fields for chargeback:
- `llm.request.tokens` - Input tokens (cost = tokens × $0.80/1M)
- `llm.response.tokens` - Output tokens (cost = tokens × $4.00/1M)
- `llm.provider` - Provider name
- `llm.request.model` - Model used
- `duration` - Time taken (for performance tracking)
- `src.addr` - Client IP (for attribution)

## 🔧 Integration Examples

### Export to Prometheus

1. Configure Prometheus to scrape metrics:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'agentgateway'
    static_configs:
      - targets: ['localhost:15020']
    metrics_path: '/metrics'
```

2. Run Prometheus:
```bash
prometheus --config.file=prometheus.yml
```

3. Create Grafana dashboards for:
   - Token usage over time
   - Cost per user/team
   - Rate limit violations
   - Request latency

### Export Traces to Other Backends

Change the OTLP endpoint in config.yaml:

```yaml
config:
  tracing:
    # For DataDog
    otlpEndpoint: https://trace.agent.datadoghq.com:4317
    randomSampling: true

# Or for Honeycomb
config:
  tracing:
    otlpEndpoint: https://api.honeycomb.io:443
    randomSampling: true

# Or for Grafana Tempo
config:
  tracing:
    otlpEndpoint: http://tempo:4317
    randomSampling: true
```

### Parse Logs with ELK Stack

1. Ship logs to Logstash:
```bash
agentgateway --config config.yaml 2>&1 | nc logstash-host 5000
```

2. Parse structured log fields in Logstash:
```ruby
filter {
  grok {
    match => { "message" => "%{TIMESTAMP_ISO8601:timestamp}.*llm.request.tokens=%{NUMBER:input_tokens}.*llm.response.tokens=%{NUMBER:output_tokens}" }
  }
  
  mutate {
    convert => {
      "input_tokens" => "integer"
      "output_tokens" => "integer"
    }
  }
}
```

3. Create Kibana dashboards for cost analysis

## 📈 Monitoring Best Practices

### Set Up Alerts

**High Token Usage**:
```yaml
# Prometheus alert
- alert: HighTokenUsage
  expr: rate(agentgateway_gen_ai_client_token_usage_sum[5m]) > 10000
  annotations:
    summary: "High token usage detected"
```

**Rate Limit Violations**:
```yaml
- alert: FrequentRateLimits
  expr: rate(agentgateway_requests{status="429"}[5m]) > 0.1
  annotations:
    summary: "Frequent rate limiting"
```

**High Latency**:
```yaml
- alert: SlowLLMResponses
  expr: histogram_quantile(0.95, agentgateway_duration_bucket) > 5000
  annotations:
    summary: "95th percentile latency > 5s"
```

### Create Dashboards

**Cost Dashboard**:
- Total spend (calculated from token metrics)
- Spend by user/team
- Spend by model
- Trend over time

**Performance Dashboard**:
- Request rate
- Latency (p50, p95, p99)
- Error rate
- Rate limit hit rate

**Usage Dashboard**:
- Active users
- Requests per user
- Token usage distribution
- Popular models

## 🛠️ Troubleshooting

### Traces Not Appearing in Jaeger

1. **Check Jaeger is running**:
```bash
docker ps | grep jaeger
```

2. **Verify OTLP endpoint**:
```bash
curl http://localhost:4317
```

3. **Check gateway logs** for tracing errors

4. **Verify config**:
```yaml
config:
  tracing:
    otlpEndpoint: http://localhost:4317
    randomSampling: true
```

### Metrics Not Showing Token Usage

1. **Make sure requests are successful** (status 200)
2. **Check the LLM returns usage data** in response
3. **Verify metrics endpoint**:
```bash
curl http://localhost:15020/metrics | grep agentgateway_gen_ai
```

### Logs Missing LLM Fields

1. **Check that backend is configured** with `ai` type
2. **Verify provider returns token counts**
3. **Ensure request succeeds** (not rate limited)

## 🔗 Additional Resources

- [Official Observability Docs](https://agentgateway.dev/docs/llm/observability/)
- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Prometheus Metrics](https://prometheus.io/docs/concepts/metric_types/)

## 🎉 Summary

With AgentGateway observability, you get:

✅ **Full visibility** into LLM requests and responses  
✅ **Token usage metrics** for accurate cost tracking  
✅ **Distributed tracing** for debugging and performance  
✅ **Structured logs** for audit and compliance  
✅ **Integration** with popular observability tools  

This enables:
- Accurate chargeback and cost allocation
- Performance optimization
- Issue debugging
- Usage analytics
- Compliance and audit trails

