# How to Protect Your AI Budget: Building a Secure LLM Gateway with Cost Controls

*Three critical problems every company faces when deploying AI—and how to solve them in production*

---

The AI revolution is here, but it's brought some expensive surprises. Last month, a developer at a major tech company accidentally committed an infinite loop to production. The result? Their Anthropic Claude bill jumped from $200 to $18,000 in just three hours.

Sound familiar? You're not alone.

As companies rush to integrate Large Language Models (LLMs) into their applications, they're discovering that production AI comes with three critical challenges:

1. **API keys leak everywhere** — dev tools, browser consoles, version control, logs
2. **Costs spiral out of control** — bugs, DDoS attacks, or just enthusiastic users
3. **No visibility into spending** — which team, user, or service is consuming your AI budget?

Today, I'll show you how to solve all three problems using an AI gateway pattern—complete with a working demo you can run in 3 minutes.

## The Problem: Your LLM Infrastructure is Leaking Money (and Secrets)

Let me paint a picture of what goes wrong when you integrate AI directly into your application:

### 🔓 Problem 1: API Key Sprawl

Your Anthropic API key needs to be everywhere:
- In your mobile app (exposed in the binary)
- In your web app (visible in browser dev tools)
- In every developer's `.env` file
- In CI/CD pipelines
- In production servers

One leaked key = your entire AI budget exposed. And keys *always* leak. It's just a matter of time.

### 💸 Problem 2: Cost Chaos

Without rate limiting at the infrastructure level:
- A single bug can run up thousands in charges overnight
- Malicious actors can DDoS your LLM budget
- You have no way to set guardrails per user or team
- Testing in production becomes terrifyingly expensive

One of our customers discovered a memory leak that caused their AI service to retry failed requests indefinitely. Their daily AI spend went from $50 to $12,000 before they noticed.

### 📊 Problem 3: Cost Attribution Mystery

Your CFO asks: "Why did our AI bill jump 300% this month?"

You have no answer because:
- No per-user tracking
- No per-team cost allocation
- No way to generate chargeback reports
- Can't identify high-usage patterns

Traditional API monitoring tools show requests, but they don't show which users or teams are driving costs.

## The Solution: An AI Gateway with Security & Cost Controls

The pattern is simple but powerful: put a gateway between your applications and your AI provider.

```
[Your Apps] ──► [AgentGateway] ──► [Anthropic Claude]
```

The gateway becomes your:
- **Vault** for API keys (clients never need them)
- **Firewall** for cost controls (rate limiting, quotas)
- **Meter** for cost tracking (per-user, per-team attribution)

Let me show you how this works in practice.

## Demo: See It In Action

I've built a complete working demo that showcases all these features. You can [try it yourself on GitHub](https://github.com/sebbycorp/agentgateway-llm-consumption-demo).

### Quick Start (3 Steps)

**Step 1:** Set your API key (only needed on the gateway)
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**Step 2:** Start the gateway
```bash
agentgateway --config config.yaml
```

**Step 3:** Run the demo
```bash
python3 demo_proxy.py
```

That's it. You'll see four demos in action:

## Demo 1: Data Leakage Prevention

**The Problem:** API keys in client code = keys leaked in version control, browser tools, mobile apps.

**The Solution:** Clients make requests through the gateway *without any API key*:

```python
# Client code - NO API KEY! 
response = requests.post(
    "http://gateway:3000/v1/messages",
    json={"model": "claude-haiku-4-5-20251001", ...}
)
```

The gateway handles authentication behind the scenes:

```yaml
# config.yaml
backendAuth:
  key: "$ANTHROPIC_API_KEY"  # Only exists on gateway
```

**Result:** Your API key lives in exactly one place—the gateway—not scattered across dozens of services and client apps.

## Demo 2: Cost Controls via Rate Limiting

**The Problem:** One bug, infinite loop, or malicious actor can drain your AI budget in hours.

**The Solution:** Token bucket rate limiting at the gateway level:

```yaml
localRateLimit:
  - maxTokens: 10           # 10 requests in the bucket
    tokensPerFill: 10       # Refill 10 tokens
    fillInterval: 60s       # Every minute
```

In the demo, we send 12 rapid requests. Here's what happens:

```
Request 1/12:  ✅ Success
Request 2/12:  ✅ Success
...
Request 10/12: ✅ Success
Request 11/12: 🛑 Rate Limited
Request 12/12: 🛑 Rate Limited
```

**Result:** No matter what goes wrong in your code, you can't exceed your configured limits. Your AI budget is protected.

### Real-World Rate Limit Configurations

For production, you'd tune this to your needs:

```yaml
# Free tier protection
maxTokens: 50
tokensPerFill: 50
fillInterval: 3600s  # 50 requests per hour

# Production service
maxTokens: 1000
tokensPerFill: 1000
fillInterval: 60s    # 1,000 requests per minute

# Development environment
maxTokens: 100
tokensPerFill: 100
fillInterval: 60s    # 100 requests per minute
```

## Demo 3: Cost Tracking & Chargeback

This is where things get really interesting. 

**The Problem:** You have a $10,000/month AI bill, but you don't know:
- Which users are heavy vs. light consumers
- Which teams should be charged what amount
- What services are driving costs

**The Solution:** User and team attribution headers that track every request:

```python
headers = {
    "X-User-ID": "alice",
    "X-Team-ID": "engineering"
}
response = requests.post(gateway_url, headers=headers, ...)
```

The demo simulates multiple users from different teams, then generates a chargeback report:

```
============================================================
  💳 CHARGEBACK REPORT
============================================================

Report Generated: 2024-10-30 14:30:00
Total Requests: 18
Total Cost: $0.003245

============================================================
PER-USER BREAKDOWN
============================================================
User            Requests   Input        Output       Cost        
------------------------------------------------------------
alice           5          1,245        3,892        $0.001654
carol           4          987          2,723        $0.000882
bob             3          678          1,445        $0.000521
david           2          289          734          $0.000188
------------------------------------------------------------
TOTAL           14         3,199        8,794        $0.003245

============================================================
PER-TEAM BREAKDOWN
============================================================
Team                 Requests        Total Cost     
------------------------------------------------------------
engineering          8               $0.002175
marketing            6               $0.001070
------------------------------------------------------------
TOTAL                14              $0.003245
```

**Result:** You can now:
- Allocate costs to teams/departments
- Set per-user budgets and alerts
- Identify high-usage patterns
- Generate monthly invoices for chargeback

### Cost Calculation

The demo uses real Anthropic pricing:

```python
PRICING = {
    "claude-haiku-4-5-20251001": {
        "input": 0.80 / 1_000_000,   # $0.80 per million tokens
        "output": 4.00 / 1_000_000,  # $4.00 per million tokens
    }
}

cost = (input_tokens * $0.80/1M) + (output_tokens * $4.00/1M)
```

Every response from Claude includes token usage:

```json
{
  "usage": {
    "input_tokens": 245,
    "output_tokens": 892
  }
}
```

Multiply by your pricing model, and you have exact cost attribution per request.

## Demo 4: Centralized Management

**The Problem:** Managing AI infrastructure across dozens of services is a nightmare:
- Update API keys → update 20 services
- Change models → deploy 20 services
- Add authentication → modify 20 codebases

**The Solution:** Centralized configuration in the gateway:

```yaml
# Single configuration file
backends:
  - ai:
      name: anthropic
      provider:
        anthropic:
          model: claude-haiku-4-5-20251001
      routes:
        /v1/messages: messages
```

**Result:** 
- Update API key → restart gateway (no client changes)
- Switch models → edit config (no client changes)
- Add policies → edit config (no client changes)

Your clients stay simple and stable. All complexity lives in one place.

## Real-World Use Cases

### Use Case 1: Multi-Tenant SaaS Platform

You're building an AI-powered SaaS product with 500 customers:

```
[Customer A App] ──┐
[Customer B App] ──┼──► [Gateway] ──► [Anthropic]
[Customer C App] ──┘
```

**Before the gateway:**
- 500 API keys to manage (one per customer? shared?)
- No way to rate limit per customer
- Can't bill customers for actual usage
- One customer's bug affects everyone

**With the gateway:**
- One API key (in the gateway)
- Per-customer rate limits
- Detailed usage tracking for billing
- Isolated blast radius

### Use Case 2: Internal Developer Platform

Your company has 15 teams building AI features:

```
[Team 1 App] ──┐
[Team 2 App] ──┼──► [Gateway] ──► [Anthropic]
[Team 3 App] ──┘
```

**Before the gateway:**
- Each team needs the API key
- No cost allocation per team
- No centralized rate limiting
- Hard to audit usage

**With the gateway:**
- Teams request access (no key sharing)
- Automatic cost tracking per team
- Platform team controls all policies
- Full audit trail

**Chargeback in action:**
```
Monthly Report:
- Engineering:  $2,450
- Marketing:    $890
- Sales:        $320
- Support:      $1,200
```

Your finance team can now allocate AI costs to departmental budgets.

### Use Case 3: Production Application with Multiple Clients

You have a web app, mobile app, and backend services all using AI:

```
[Web App]      ──┐
[Mobile App]   ──┼──► [Gateway] ──► [Anthropic]
[Backend API]  ──┘
```

**Before the gateway:**
- API key in web app (exposed in browser)
- API key in mobile app (exposed in binary)
- No rate limiting per client type
- Can't track web vs. mobile vs. backend usage

**With the gateway:**
- No keys in client apps
- Different rate limits for each client type
- Track costs: "Mobile app cost us $500 this week"
- Easy to add authentication

## Advanced Features You Can Add

Once you have this foundation, you can extend it:

### 1. Budget Alerts

```python
USER_BUDGETS = {
    "alice": 100.00,
    "bob": 50.00
}

if user_cost > USER_BUDGETS[user_id]:
    send_alert(f"User {user_id} exceeded budget!")
    # Or: block_user(user_id)
```

### 2. Export to Database

```python
# Store in PostgreSQL for historical analysis
cursor.execute("""
    INSERT INTO llm_usage (timestamp, user_id, team_id, 
                          input_tokens, output_tokens, cost)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (timestamp, user_id, team_id, input_tokens, output_tokens, cost))
```

### 3. Monthly Billing Reports

```sql
-- Generate monthly invoice per team
SELECT 
    team_id,
    DATE_TRUNC('month', timestamp) as month,
    SUM(cost) as total_cost,
    COUNT(*) as total_requests
FROM llm_usage
WHERE timestamp >= '2024-10-01'
GROUP BY team_id, month
ORDER BY total_cost DESC;
```

### 4. Content Filtering

Prevent sensitive data from being sent to the AI:

```yaml
policies:
  contentFilter:
    patterns:
      - creditCard: true
      - ssn: true
      - apiKey: true
```

### 5. Multi-Provider Routing

Route to different AI providers based on use case:

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

Route based on cost sensitivity:
- Cheap queries → Haiku (faster, cheaper)
- Complex queries → Opus (slower, more capable)

## Security Best Practices

A few critical security considerations:

### 1. Don't Expose the Gateway Publicly

```yaml
# ❌ BAD: Publicly accessible
binds:
- port: 3000
  address: 0.0.0.0

# ✅ GOOD: Internal only
binds:
- port: 3000
  address: 127.0.0.1
```

Use a VPN, private network, or add authentication.

### 2. Add Client Authentication

```yaml
policies:
  auth:
    apiKey:
      keys:
        - name: mobile-app
          key: "$MOBILE_APP_KEY"
        - name: web-app
          key: "$WEB_APP_KEY"
```

### 3. Use Secret Management

```bash
# ❌ BAD: Hardcoded in config
backendAuth:
  key: "sk-ant-api03-..."

# ✅ GOOD: Environment variable
backendAuth:
  key: "$ANTHROPIC_API_KEY"

# ✅ BETTER: Secret manager
backendAuth:
  key: "${vault:secret/anthropic/api-key}"
```

### 4. Enable Audit Logging

```yaml
logging:
  level: info
  # Log metadata only, not sensitive content
  redactSensitiveData: true
```

## The Business Case

Let's talk ROI. Here's what this pattern delivers:

### Cost Savings

**Before:**
- Mystery $10K spike in AI costs
- No way to identify the cause
- Can't prevent it from happening again

**After:**
- Instant visibility: "Team X's new feature caused the spike"
- Rate limits prevent future spikes
- Budget alerts catch problems early

**Estimated savings:** 20-40% of AI spend through waste reduction

### Security Risk Reduction

**Before:**
- API keys in git history
- Keys in browser dev tools
- Keys in mobile app binaries
- Keys in logs

**After:**
- One key, secured in one place
- Zero client-side key exposure
- Centralized key rotation

**Value:** Prevents security incidents that could cost millions

### Operational Efficiency

**Before:**
- 2 hours to update API keys across 15 services
- Each team maintains their own AI integration
- No standardization

**After:**
- 2 minutes to update key (restart gateway)
- One integration maintained by platform team
- Consistent patterns across organization

**Value:** Saves ~20 engineering hours per month

### Financial Visibility

**Before:**
- "AI costs money, we don't know why"
- No per-team or per-user attribution
- Can't charge back to departments

**After:**
- "Engineering spent $2,450 this month on AI"
- Clear cost breakdown per team/user
- Monthly chargeback reports

**Value:** Enables proper budgeting and cost allocation

## Getting Started

Ready to try it? Here's your roadmap:

### Phase 1: Local Demo (30 minutes)

1. Clone the [demo repository](https://github.com/sebbycorp/agentgateway-llm-consumption-demo)
2. Run through all four demos
3. Experiment with rate limiting
4. Check out the chargeback reports

### Phase 2: Development Deployment (1 day)

1. Deploy AgentGateway in your dev environment
2. Configure authentication
3. Update one application to use the gateway
4. Add cost tracking headers
5. Verify everything works

### Phase 3: Production Rollout (1 week)

1. Deploy gateway in production (with monitoring)
2. Migrate applications one at a time
3. Configure rate limits for your use case
4. Set up cost tracking database
5. Create chargeback reporting dashboard

### Phase 4: Advanced Features (ongoing)

1. Budget alerts per user/team
2. Multi-provider routing
3. Content filtering
4. A/B testing different models
5. Cost optimization automation

## Conclusion: Take Control of Your AI Infrastructure

The AI revolution is real, but it doesn't have to break your budget or compromise your security.

By implementing an AI gateway pattern, you get:
- ✅ **Security**: API keys never leave your infrastructure
- ✅ **Cost Control**: Rate limiting prevents runaway spending  
- ✅ **Visibility**: Track every dollar spent on AI
- ✅ **Simplicity**: Centralized management for all AI access

The best part? You can implement this in an afternoon. The demo is ready to run, the code is open source, and the pattern is battle-tested.

Don't wait until your API key leaks or your AI bill hits $50,000. Set up proper guardrails now.

---

## Resources

- **Demo Repository**: [github.com/sebbycorp/agentgateway-llm-consumption-demo](https://github.com/sebbycorp/agentgateway-llm-consumption-demo)
- **AgentGateway Documentation**: [docs.solo.io/agentgateway](https://docs.solo.io/agentgateway)
- **Rate Limiting Best Practices**: [cloud.google.com/architecture/rate-limiting-strategies-techniques](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)

---

**Questions? Comments?** Drop them below or reach out on Twitter. I'd love to hear about your AI infrastructure challenges and how you're solving them.

*Have you experienced runaway AI costs or API key leakage? Share your war stories in the comments! 💬*

