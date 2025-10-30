# AgentGateway + Presidio Architecture

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│                         CLIENT APPLICATION                               │
│                                                                          │
│  • Web App / Mobile App / Backend Service                               │
│  • Makes LLM requests with user prompts                                 │
│  • May contain PII (SSN, credit cards, emails, etc.)                    │
│                                                                          │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ HTTP Request
                                 │ User query with potential PII
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│                    APPLICATION LAYER (Python)                            │
│                      demo_complete.py                                    │
│                                                                          │
│  • Request validation                                                    │
│  • User/team attribution (X-User-ID, X-Team-ID headers)                 │
│  • Budget checking (per-user spending limits)                           │
│  • Cost tracking                                                         │
│                                                                          │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ 1. Analyze text for PII
                                 │ POST /analyze
                                 │
                                 ▼
┌──────────────────────────────────────────────┐  ┌─────────────────────┐
│                                               │  │                     │
│    PRESIDIO ANALYZER (Port 5001)             │  │   JAEGER            │
│    Sidecar Container                          │  │   Port 16686        │
│                                               │  │                     │
│  • ML-powered PII detection                   │◄─┤  • Distributed      │
│  • Named Entity Recognition (NER)             │  │    tracing          │
│  • Pattern matching (regex)                   │  │  • Request flow     │
│  • Context-aware analysis                     │  │  • Latency metrics  │
│  • 50+ entity types:                          │  │  • Error tracking   │
│    - US_SSN, CREDIT_CARD, EMAIL_ADDRESS      │  │                     │
│    - PHONE_NUMBER, PERSON, LOCATION          │  └─────────────────────┘
│    - IP_ADDRESS, CRYPTO, MEDICAL_LICENSE     │
│    - Custom entities (configurable)          │
│                                               │
│  Returns: List of detected PII entities       │
│           with positions and confidence       │
│                                               │
└────────────────────────┬──────────────────────┘
                        │
                        │ 2. Detected entities
                        │ [{entity_type: "US_SSN", start: 10, end: 21}]
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│         PRESIDIO ANONYMIZER (Port 5002)                                 │
│         Sidecar Container                                                │
│                                                                          │
│  • Receives detected entities from Analyzer                             │
│  • Applies anonymization strategies:                                    │
│    - Replace: "123-45-6789" → "<SSN>"                                   │
│    - Mask: "john@example.com" → "j***@e******.com"                     │
│    - Encrypt: Reversible encryption for later retrieval                │
│    - Hash: One-way hashing for consistency                              │
│                                                                          │
│  • Configurable per entity type                                         │
│  • Preserves text structure (sentence flow)                             │
│                                                                          │
│  Returns: Clean, redacted text safe for LLM                             │
│                                                                          │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ 3. Clean, PII-free text
                                 │ "My SSN is <SSN> and I need help"
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│              AGENTGATEWAY (Port 3000)                                   │
│              High-Performance Rust Proxy                                 │
│                                                                          │
│  POLICIES:                                                               │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │ 🔐 Backend Authentication                                     │      │
│  │    • API keys stored server-side                              │      │
│  │    • Reads from environment: $ANTHROPIC_API_KEY              │      │
│  │    • Never exposed to clients                                 │      │
│  └──────────────────────────────────────────────────────────────┘      │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │ 🚦 Local Rate Limiting (Token Bucket)                        │      │
│  │    • maxTokens: 10 requests                                   │      │
│  │    • tokensPerFill: 10                                        │      │
│  │    • fillInterval: 60s                                        │      │
│  │    • Returns 429 when exceeded                                │      │
│  └──────────────────────────────────────────────────────────────┘      │
│                                                                          │
│  ROUTING:                                                                │
│  • Multi-provider support                                                │
│  • Load balancing                                                        │
│  • Failover handling                                                     │
│                                                                          │
│  OBSERVABILITY:                                                          │
│  • OpenTelemetry traces → Jaeger                                        │
│  • Prometheus metrics (tokens, latency, errors)                         │
│  • Structured logging                                                    │
│                                                                          │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ 4. Authenticated request with clean text
                                 │ Authorization: Bearer <api-key>
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
            ▼                    ▼                    ▼
    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │              │    │              │    │              │
    │  ANTHROPIC   │    │   OPENAI     │    │  GROK (xAI)  │
    │   CLAUDE     │    │   GPT-4      │    │   Grok-2     │
    │              │    │              │    │              │
    │ Port 3000    │    │ Port 3001    │    │ Port 3002    │
    │ /v1/messages │    │ /openai/v1/  │    │ /grok/v1/    │
    │              │    │ chat/...     │    │ chat/...     │
    │              │    │              │    │              │
    └──────────────┘    └──────────────┘    └──────────────┘

         $0.80/M             $0.15/M             $2.00/M
       input tokens        input tokens        input tokens
```

## Request Flow Example

### User Query with PII
```
"My social security number is 123-45-6789 and email is john@example.com"
```

### Step 1: Presidio Analyzer Detection
```json
POST http://localhost:5001/analyze
{
  "text": "My social security number is 123-45-6789...",
  "language": "en",
  "entities": ["US_SSN", "EMAIL_ADDRESS"]
}

Response:
[
  {
    "entity_type": "US_SSN",
    "start": 33,
    "end": 44,
    "score": 0.95,
    "analysis_explanation": "Detected as SSN pattern"
  },
  {
    "entity_type": "EMAIL_ADDRESS", 
    "start": 58,
    "end": 76,
    "score": 1.0
  }
]
```

### Step 2: Presidio Anonymizer Redaction
```json
POST http://localhost:5002/anonymize
{
  "text": "My social security number is 123-45-6789...",
  "anonymizers": {
    "US_SSN": {"type": "replace", "new_value": "<SSN>"},
    "EMAIL_ADDRESS": {"type": "replace", "new_value": "<EMAIL>"}
  },
  "analyzer_results": [...]
}

Response:
{
  "text": "My social security number is <SSN> and email is <EMAIL>"
}
```

### Step 3: Clean Request to LLM
```json
POST http://localhost:3000/v1/messages
Headers:
  X-User-ID: alice
  X-Team-ID: engineering

{
  "model": "claude-haiku-4-5-20251001",
  "messages": [{
    "role": "user",
    "content": "My social security number is <SSN> and email is <EMAIL>"
  }]
}

✅ LLM never sees actual PII
✅ Response is attributed to user/team
✅ Cost tracked: $0.000428
✅ Trace recorded in Jaeger
```

## Deployment Architecture

### Docker Compose (Development/Demo)
```yaml
services:
  # Observability
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports: ["16686:16686", "4317:4317"]
  
  # PII Detection Sidecars
  presidio-analyzer:
    image: mcr.microsoft.com/presidio-analyzer:latest
    ports: ["5001:5001"]
    
  presidio-anonymizer:
    image: mcr.microsoft.com/presidio-anonymizer:latest
    ports: ["5002:5002"]
```

### Kubernetes (Production)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-gateway
spec:
  replicas: 3
  template:
    spec:
      containers:
      # Main application
      - name: app
        image: your-app:latest
        env:
        - name: PRESIDIO_ANALYZER_URL
          value: "http://localhost:5001"
        - name: AGENTGATEWAY_URL
          value: "http://localhost:3000"
      
      # Presidio sidecar
      - name: presidio-analyzer
        image: mcr.microsoft.com/presidio-analyzer
        ports:
        - containerPort: 5001
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
      
      - name: presidio-anonymizer
        image: mcr.microsoft.com/presidio-anonymizer
        ports:
        - containerPort: 5002
      
      # AgentGateway sidecar
      - name: agentgateway
        image: agentgateway:latest
        ports:
        - containerPort: 3000
        volumeMounts:
        - name: config
          mountPath: /config.yaml
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-secrets
              key: anthropic-key
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **AgentGateway** | Rust | High-performance LLM proxy |
| **Presidio Analyzer** | Python + spaCy | ML-powered PII detection |
| **Presidio Anonymizer** | Python | PII redaction/masking |
| **Jaeger** | Go | Distributed tracing |
| **Application** | Python | Demo orchestration |

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| **Gateway Latency** | <1ms | Proxy overhead |
| **Presidio Analyze** | 50-200ms | Depends on text length |
| **Presidio Anonymize** | 10-50ms | Fast replacement |
| **Total Overhead** | ~100-250ms | PII detection + gateway |
| **LLM Latency** | 1-5 seconds | Varies by model |
| **Throughput** | 100+ req/s | Per pod (can scale) |

## Scaling Strategy

### Horizontal Scaling
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Pod 1     │     │   Pod 2     │     │   Pod 3     │
│  ┌────────┐ │     │  ┌────────┐ │     │  ┌────────┐ │
│  │  App   │ │     │  │  App   │ │     │  │  App   │ │
│  ├────────┤ │     │  ├────────┤ │     │  ├────────┤ │
│  │Presidio│ │     │  │Presidio│ │     │  │Presidio│ │
│  ├────────┤ │     │  ├────────┤ │     │  ├────────┤ │
│  │Gateway │ │     │  │Gateway │ │     │  │Gateway │ │
│  └────────┘ │     │  └────────┘ │     │  └────────┘ │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                    Load Balancer
```

### Vertical Scaling
- **Presidio Analyzer**: CPU-intensive (NER models)
  - Recommendation: 2-4 CPUs per pod
- **Presidio Anonymizer**: Memory-light
  - Recommendation: 512MB-1GB RAM
- **AgentGateway**: I/O bound
  - Recommendation: 1 CPU, 512MB RAM

## Security Model

```
┌──────────────────────────────────────────────────────────┐
│                    Security Layers                        │
├──────────────────────────────────────────────────────────┤
│ Layer 1: PII Redaction (Presidio)                        │
│   • Removes sensitive data at source                     │
│   • ML + pattern matching                                │
│   • Configurable per regulation (GDPR/HIPAA/CCPA)       │
├──────────────────────────────────────────────────────────┤
│ Layer 2: API Key Protection (AgentGateway)              │
│   • Keys stored server-side only                         │
│   • Never exposed to clients                             │
│   • Easy rotation (config update)                        │
├──────────────────────────────────────────────────────────┤
│ Layer 3: Rate Limiting (AgentGateway)                   │
│   • Prevents abuse and cost overruns                     │
│   • Token bucket algorithm                               │
│   • Per-route configuration                              │
├──────────────────────────────────────────────────────────┤
│ Layer 4: Budget Enforcement (Application)               │
│   • Per-user/team spending limits                        │
│   • Real-time cost tracking                              │
│   • Automatic cutoff                                     │
├──────────────────────────────────────────────────────────┤
│ Layer 5: Observability (Jaeger + Metrics)              │
│   • Complete audit trail                                 │
│   • Compliance reporting                                 │
│   • Anomaly detection                                    │
└──────────────────────────────────────────────────────────┘
```

## Cost Optimization

### Per-Request Cost Breakdown
```
Presidio Detection: $0.0001 (amortized compute)
AgentGateway:       $0.0000 (negligible)
LLM API Call:       $0.0002 - $0.0050 (varies by model)
────────────────────────────────────────────────
Total:              ~$0.0003 - $0.0051 per request
```

### Cost Savings Strategies
1. **Smart routing** - Use cheaper models for simple queries
2. **Caching** - Cache similar queries (50-80% cost reduction)
3. **Rate limiting** - Prevent runaway costs from bugs
4. **Budget enforcement** - Hard caps per user/team
5. **Chargeback** - Allocate costs to departments

---

**Last Updated:** October 30, 2025  
**Version:** 1.0 (with Presidio integration)

