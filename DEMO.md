# AgentGateway Security & Cost Control Demo

This demo showcases how AgentGateway acts as a secure proxy for Anthropic Claude, providing enterprise-grade features for data protection and cost management.

## 🎯 What This Demo Shows

### 1. **Data Leakage Prevention**
- **Problem**: API keys exposed in client code, browser dev tools, or version control
- **Solution**: Gateway stores API keys securely; clients never need them
- **Benefit**: Zero risk of key leakage from client applications

### 2. **Privacy Protection**
- **Problem**: Sensitive prompts and responses logged everywhere
- **Solution**: Gateway logs only metadata (timestamps, status codes), not content
- **Benefit**: Compliance with data privacy regulations (GDPR, HIPAA, etc.)

### 3. **Cost Controls**
- **Problem**: Runaway API costs from bugs, infinite loops, or DDoS
- **Solution**: Rate limiting at the gateway level (10 req/60s in this demo)
- **Benefit**: Predictable costs and protection against abuse

### 4. **Centralized Management**
- **Problem**: Managing API keys and policies across many clients
- **Solution**: Single configuration file for all clients
- **Benefit**: Easy updates, consistent policies, simplified operations

### 5. **Cost Tracking & Chargeback** 💰
- **Problem**: No visibility into which users/teams are consuming AI credits
- **Solution**: Track every request with user/team attribution and token usage
- **Benefit**: Accurate cost allocation, budget management, and billing

## 🚀 Running the Demo

### Step 1: Set up your environment

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Step 2: Start the gateway

```bash
agentgateway --config config.yaml
```

The gateway will start on port 3000 with:
- ✅ Rate limiting: 10 requests per 60 seconds
- ✅ Metadata-only logging
- ✅ Secure API key handling

### Step 3: Run the demo

In a new terminal:

```bash
python3 demo_proxy.py
```

## 📊 Demo Flow

### Demo 1: Privacy & Data Leakage Prevention
- Shows how clients make requests WITHOUT needing the API key
- Demonstrates secure authentication through the gateway
- Highlights how this prevents key exposure

### Demo 2: Cost Controls
- Sends 12 rapid requests to trigger rate limiting
- Shows how the gateway protects against excessive usage
- Demonstrates cost protection in action

### Demo 3: Centralized Control
- Explains benefits of centralized management
- Shows how easy it is to update policies
- Demonstrates consistent behavior across all clients

### Demo 4: Cost Tracking & Chargeback (NEW! 💰)
- Simulates multiple users from different teams
- Tracks token usage and costs per user/team
- Generates detailed chargeback report with:
  - Per-user cost breakdown
  - Per-team cost aggregation
  - Token usage statistics
  - Total spend analysis

## 🔧 Configuration Deep Dive

### Current Rate Limit Policy

```yaml
localRateLimit:
  - maxTokens: 10           # Max 10 tokens (requests) in bucket
    tokensPerFill: 10       # Refill 10 tokens
    fillInterval: 60s       # Every 60 seconds
```

**How it works (Token Bucket Algorithm):**
- You start with 10 tokens
- Each request consumes 1 token
- Every 60 seconds, 10 tokens are added back (up to maxTokens)

**Adjust for your needs:**
- Production: `maxTokens: 1000, tokensPerFill: 1000, fillInterval: 3600s` (1000/hour)
- Development: `maxTokens: 100, tokensPerFill: 100, fillInterval: 60s` (100/minute)
- Free tier protection: `maxTokens: 5, tokensPerFill: 5, fillInterval: 60s` (5/minute)

### Backend Authentication

```yaml
backendAuth:
  key: "$ANTHROPIC_API_KEY"
```

**Benefits:**
- Keys stored only in gateway environment
- Easy rotation (restart gateway with new key)
- No client code changes needed

## 💡 Real-World Use Cases

### 1. Multi-Tenant SaaS Platform
```
[Customer A App] ──┐
[Customer B App] ──┼──► [Gateway with auth] ──► [Anthropic]
[Customer C App] ──┘
```
- Single API key for all customers
- Per-customer rate limiting
- Centralized cost tracking
- **Chargeback**: Bill each customer for their actual usage

### 2. Internal Developer Platform
```
[Dev Team 1] ──┐
[Dev Team 2] ──┼──► [Gateway] ──► [Anthropic]
[Dev Team 3] ──┘
```
- Developers don't need API keys
- Prevent accidental cost overruns
- Audit all AI usage
- **Chargeback**: Allocate AI costs to team budgets

### 3. Production Application
```
[Mobile App]    ──┐
[Web App]       ──┼──► [Gateway] ──► [Anthropic]
[Backend APIs]  ──┘
```
- API keys never in client code
- Rate limiting prevents abuse
- Easy to switch AI providers
- **Chargeback**: Track costs per application/service

## 🛡️ Security Best Practices

1. **Never expose the gateway directly to the internet**
   - Use VPN or private network
   - Add authentication layer
   - Use firewall rules

2. **Add client authentication**
   ```yaml
   policies:
     auth:
       apiKey:
         keys:
           - name: mobile-app
             key: "$MOBILE_APP_KEY"
   ```

3. **Monitor and alert**
   - Set up alerts for rate limit hits
   - Monitor unusual usage patterns
   - Track costs per client

4. **Use environment variables**
   - Never commit keys to git
   - Use secret management (Vault, AWS Secrets Manager)
   - Rotate keys regularly

## 💰 Chargeback Implementation

The demo tracks costs using:

### User Identification
```python
headers = {
    "X-User-ID": "alice",
    "X-Team-ID": "engineering"
}
```

### Cost Calculation
Based on Anthropic's pricing:
- Input tokens: $0.80 per million
- Output tokens: $4.00 per million

### Sample Chargeback Report
```
============================================================
  💳 CHARGEBACK REPORT
============================================================

Report Generated: 2024-10-30 14:30:00
Total Requests: 15
Total Cost: $0.002450

============================================================
PER-USER BREAKDOWN
============================================================
User            Requests   Input        Output       Cost        
------------------------------------------------------------
alice           3          245          892          $0.000754
carol           3          189          723          $0.000630
bob             2          178          445          $0.000521
david           1          89           234          $0.000107
------------------------------------------------------------
TOTAL           9          701          2,294        $0.002012

============================================================
PER-TEAM BREAKDOWN
============================================================
Team                 Requests        Total Cost     
------------------------------------------------------------
engineering          5               $0.001275
marketing            4               $0.000737
------------------------------------------------------------
TOTAL                9               $0.002012
```

## 📈 Next Steps

### Export Chargeback Data
Store tracking data in a database or export to CSV:
```python
import csv
import json

# Export to CSV
with open('chargeback_report.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['timestamp', 'user_id', 'team_id', 'cost'])
    writer.writeheader()
    writer.writerows(cost_tracker['requests'])

# Export to JSON
with open('chargeback_report.json', 'w') as f:
    json.dump(cost_tracker, f, indent=2)
```

### Set Up Budget Alerts
```python
# Alert if user exceeds budget
USER_BUDGETS = {"alice": 10.0, "bob": 5.0}

if cost_tracker["by_user"][user_id]["cost"] > USER_BUDGETS[user_id]:
    send_alert(f"User {user_id} exceeded budget!")
```

### Add Content Filtering
Prevent sensitive data from being sent to AI:
```yaml
policies:
  contentFilter:
    patterns:
      - creditCard: true
      - ssn: true
      - email: true
```

### Add Request/Response Transformation
Modify requests before they reach the AI:
```yaml
policies:
  transform:
    request:
      headers:
        x-user-id: "$USER_ID"
```

### Add Multiple AI Providers
Route to different providers based on criteria:
```yaml
backends:
  - ai:
      name: anthropic-fast
      provider:
        anthropic:
          model: claude-haiku-4-5-20251001
  - ai:
      name: anthropic-smart
      provider:
        anthropic:
          model: claude-opus-4-20250514
```

## 🤝 Contributing

Have ideas for additional security or cost control features? Open an issue or PR!

## 📚 Additional Resources

- [AgentGateway Documentation](https://docs.solo.io/agentgateway)
- [Anthropic API Reference](https://docs.anthropic.com)
- [Rate Limiting Best Practices](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)

