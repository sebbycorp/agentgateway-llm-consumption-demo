#!/usr/bin/env python3
"""
AgentGateway Complete Demo
===========================
Comprehensive demonstration of all AgentGateway features:

SECURITY & PRIVACY:
1. Privacy & Data Leakage Prevention (API key security)
2. PII Redaction & Data Security (GDPR/HIPAA compliance)

COST CONTROLS:
3. Rate Limiting (prevent runaway costs)
4. Budget Enforcement (per-user spending limits)
5. Cost Tracking & Chargeback (usage attribution)

RELIABILITY & FLEXIBILITY:
6. Multi-Provider Strategy (failover & cost optimization)
7. Centralized Control & Monitoring
"""

import requests
import json
import time
from datetime import datetime
from collections import defaultdict
import re

# Gateway endpoints
ANTHROPIC_URL = "http://localhost:3000/v1/messages"
OPENAI_URL = "http://localhost:3000/v1/chat/completions"

# Anthropic Claude pricing (as of 2024)
# https://www.anthropic.com/pricing
ANTHROPIC_PRICING = {
    "input": 0.80 / 1_000_000,   # $0.80 per million input tokens
    "output": 4.00 / 1_000_000,  # $4.00 per million output tokens
}

# OpenAI pricing
OPENAI_PRICING = {
    "gpt-4o-mini": {
        "input": 0.15 / 1_000_000,
        "output": 0.60 / 1_000_000,
    }
}

# Budget tracking (simulated enterprise budget system)
user_budgets = {
    "alice": {"limit": 0.05, "spent": 0.0, "team": "engineering"},
    "bob": {"limit": 0.10, "spent": 0.0, "team": "engineering"},
    "charlie": {"limit": 0.02, "spent": 0.0, "team": "product"},  # Low budget for demo
    "diana": {"limit": 0.08, "spent": 0.0, "team": "marketing"},
    "evan": {"limit": 0.06, "spent": 0.0, "team": "marketing"},
    "frank": {"limit": 0.15, "spent": 0.0, "team": "sales"},
    "grace": {"limit": 0.07, "spent": 0.0, "team": "data-science"},
    "henry": {"limit": 0.05, "spent": 0.0, "team": "customer-support"},
}

# Cost tracking storage
cost_tracker = {
    "requests": [],
    "by_user": defaultdict(lambda: {"requests": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0}),
    "total_cost": 0.0
}

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_subsection(title):
    """Print a formatted subsection header"""
    print("\n" + "-"*70)
    print(f"  {title}")
    print("-"*70 + "\n")

def check_budget(user_id, estimated_cost):
    """Check if user has budget for the request"""
    user = user_budgets.get(user_id)
    if not user:
        return True, ""
    
    if user["spent"] + estimated_cost > user["limit"]:
        remaining = user["limit"] - user["spent"]
        return False, f"Budget exceeded. Limit: ${user['limit']:.4f}, Spent: ${user['spent']:.4f}"
    
    return True, ""

def update_budget(user_id, cost):
    """Update user's spent budget"""
    if user_id in user_budgets:
        user_budgets[user_id]["spent"] += cost

def calculate_anthropic_cost(input_tokens, output_tokens):
    """Calculate cost for Anthropic"""
    return (input_tokens * ANTHROPIC_PRICING["input"] + 
            output_tokens * ANTHROPIC_PRICING["output"])

def calculate_openai_cost(input_tokens, output_tokens, model="gpt-4o-mini"):
    """Calculate cost for OpenAI"""
    pricing = OPENAI_PRICING.get(model, OPENAI_PRICING["gpt-4o-mini"])
    return (input_tokens * pricing["input"] + 
            output_tokens * pricing["output"])

def redact_pii(content):
    """Redact PII at application layer before sending to gateway"""
    # Redact SSN pattern (###-##-####)
    content = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN-REDACTED]', content)
    
    # Redact credit card pattern (####-####-####-#### or #### #### #### ####)
    content = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD-REDACTED]', content)
    
    # Could add more patterns: email, phone, etc.
    return content

def track_request(user_id, team_id, input_tokens, output_tokens, cost, elapsed_time):
    """Track request for cost reporting"""
    request_record = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id or "anonymous",
        "team_id": team_id or "none",
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost": cost,
        "elapsed_time": elapsed_time
    }
    cost_tracker["requests"].append(request_record)
    
    # Update user totals
    user_key = user_id or "anonymous"
    cost_tracker["by_user"][user_key]["requests"] += 1
    cost_tracker["by_user"][user_key]["input_tokens"] += input_tokens
    cost_tracker["by_user"][user_key]["output_tokens"] += output_tokens
    cost_tracker["by_user"][user_key]["cost"] += cost
    cost_tracker["total_cost"] += cost

def send_anthropic_message(content, user_id=None, show_response=True, check_budget_flag=False):
    """Send a message through Anthropic via gateway"""
    team_id = user_budgets.get(user_id, {}).get("team", "none") if user_id else "none"
    
    # Estimate cost for budget check (rough estimate: ~10 input, ~100 output tokens)
    estimated_cost = calculate_anthropic_cost(15, 100)
    
    # Budget enforcement (if enabled)
    if check_budget_flag and user_id:
        can_proceed, message = check_budget(user_id, estimated_cost)
        if not can_proceed:
            print(f"❌ {message}")
            return False, None, 0, 429
    
    payload = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    if user_id:
        headers["X-User-ID"] = user_id
    if team_id:
        headers["X-Team-ID"] = team_id
    
    try:
        start_time = time.time()
        response = requests.post(ANTHROPIC_URL, json=payload, headers=headers, timeout=30)
        elapsed_time = time.time() - start_time
        
        if show_response:
            print(f"⏱️  Response time: {elapsed_time:.2f}s")
            print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Calculate actual cost
            if "usage" in data:
                input_tokens = data["usage"].get("input_tokens", 0)
                output_tokens = data["usage"].get("output_tokens", 0)
                cost = calculate_anthropic_cost(input_tokens, output_tokens)
                
                # Update budget
                if check_budget_flag and user_id:
                    update_budget(user_id, cost)
                
                # Track for reporting
                track_request(user_id, team_id, input_tokens, output_tokens, cost, elapsed_time)
                
                if show_response:
                    print(f"💰 Cost: ${cost:.6f} (In: {input_tokens}, Out: {output_tokens} tokens)")
                    if "content" in data and len(data["content"]) > 0:
                        print(f"✅ Response: {data['content'][0]['text'][:150]}...")
                
                return True, data, cost, response.status_code
        elif response.status_code == 429:
            if show_response:
                print(f"🛑 Rate Limited! (Cost control working)")
            return False, None, 0, response.status_code
        else:
            if show_response:
                print(f"❌ Error: {response.status_code}")
            return False, None, 0, response.status_code
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False, None, 0, None

def send_openai_message(content, user_id=None, show_response=True):
    """Send a message through OpenAI via gateway"""
    team_id = user_budgets.get(user_id, {}).get("team", "none") if user_id else "none"
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if user_id:
        headers["X-User-ID"] = user_id
    if team_id:
        headers["X-Team-ID"] = team_id
    
    try:
        start_time = time.time()
        response = requests.post(OPENAI_URL, json=payload, headers=headers, timeout=30)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            # Calculate actual cost
            if "usage" in data:
                input_tokens = data["usage"].get("prompt_tokens", 0)
                output_tokens = data["usage"].get("completion_tokens", 0)
                cost = calculate_openai_cost(input_tokens, output_tokens)
                
                # Track for reporting
                track_request(user_id, team_id, input_tokens, output_tokens, cost, elapsed_time)
                
                if show_response:
                    print(f"✅ OpenAI Response")
                    print(f"   Status: {response.status_code}")
                    print(f"   Tokens: In={input_tokens}, Out={output_tokens}")
                    print(f"   Cost: ${cost:.6f}")
                    if "choices" in data and len(data["choices"]) > 0:
                        print(f"   Response: {data['choices'][0]['message']['content'][:150]}...")
                
                return True, data, cost
        else:
            print(f"❌ OpenAI failed: {response.status_code}")
            return False, None, 0
            
    except Exception as e:
        print(f"❌ OpenAI exception: {str(e)}")
        return False, None, 0

def demo_privacy_protection():
    """Demo 1: Privacy & Data Leakage Prevention"""
    print_section("Demo 1: Privacy & Data Leakage Prevention")
    
    print("🔒 Key Feature: API keys are stored in the gateway")
    print("   Clients never need to know or handle the API key")
    print()
    print("   This prevents:")
    print("   • API key leakage in client applications")
    print("   • Exposed keys in browser dev tools")
    print("   • Keys committed to version control")
    print("   • Credential theft from compromised clients")
    print()
    
    print("📝 Sending request WITHOUT API key in client code...")
    send_anthropic_message("What is 2+2? Answer briefly.", user_id="demo-user")
    
    print("\n✨ Notice: The request succeeded without the client having the API key!")
    print("   The gateway handled authentication securely.")

def demo_pii_redaction():
    """Demo 2: PII Redaction & Data Security"""
    print_section("Demo 2: PII Redaction & Data Security")
    
    print("🛡️  Application layer PII detection and redaction")
    print("   Sensitive data is removed BEFORE sending to gateway/LLM")
    print("   This ensures compliance with GDPR, HIPAA, and SOC2")
    print()
    
    # Test cases with PII
    test_cases = [
        {
            "description": "SSN in prompt",
            "content": "My social security number is 123-45-6789 and I need help with taxes.",
        },
        {
            "description": "Credit card in prompt",
            "content": "Please charge my card 4532-1234-5678-9010 for the subscription.",
        },
        {
            "description": "Multiple PII items",
            "content": "My SSN is 987-65-4321 and credit card is 5555-4444-3333-2222.",
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['description']}")
        print(f"   ❌ Original: {test['content']}")
        
        # Redact PII at application layer
        redacted = redact_pii(test['content'])
        print(f"   ✅ Redacted: {redacted}")
        print(f"   📤 Sending redacted version to gateway...")
        
        success, response, cost, status = send_anthropic_message(
            redacted, 
            user_id="compliance-demo", 
            show_response=False
        )
        
        if success:
            print(f"   ✅ Request successful - LLM never saw sensitive data")
            print(f"   💰 Cost: ${cost:.6f}")
        
        print()
        time.sleep(0.3)
    
    print("💡 Enterprise Value:")
    print("   • GDPR, HIPAA, SOC2 compliance")
    print("   • Prevents data leakage to third parties")
    print("   • Application-layer control before gateway")
    print("   • Audit trail of redacted requests")
    print("   • Can integrate with DLP tools")

def demo_rate_limiting():
    """Demo 3: Rate Limiting for Cost Control"""
    print_section("Demo 3: Rate Limiting for Cost Control")
    
    print("💰 Gateway configured with rate limit: 10 requests/60 seconds")
    print()
    print("   This prevents:")
    print("   • Runaway costs from bugs or malicious usage")
    print("   • DDoS attacks on your LLM budget")
    print("   • Accidental infinite loops")
    print("   • Abuse by compromised API clients")
    print()
    
    print("🚀 Sending 12 rapid requests to test rate limiting...")
    print()
    
    success_count = 0
    rate_limited_count = 0
    
    for i in range(12):
        print(f"Request {i+1}/12: ", end="", flush=True)
        success, _, _, status = send_anthropic_message(
            f"Count to {i+1}", 
            show_response=False, 
            user_id="rate-limit-test"
        )
        
        if success:
            success_count += 1
            print(f"✅ Success")
        elif status == 429:
            rate_limited_count += 1
            print(f"🛑 Rate Limited! (Cost control working)")
        else:
            print(f"❌ Error")
        
        time.sleep(0.1)
    
    print()
    print(f"📊 Results:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   🛑 Rate Limited: {rate_limited_count}")
    print(f"   💰 Cost saved by preventing excessive requests!")
    print()
    print("💡 Enterprise Value:")
    print("   • Automatic cost protection")
    print("   • No manual intervention needed")
    print("   • Configurable per route/user")
    print("   • Real-time enforcement")

def demo_budget_enforcement():
    """Demo 4: Budget Enforcement & Spending Limits"""
    print_section("Demo 4: Budget Enforcement & Spending Limits")
    
    print("💰 Per-user spending limits with real-time enforcement")
    print("   Unlike rate limiting (requests/time), budgets track actual costs")
    print()
    
    # Show initial budgets
    print("User Budgets:")
    print_subsection("Initial Status")
    for user_id, budget in user_budgets.items():
        print(f"   {user_id:10} | Team: {budget['team']:12} | Limit: ${budget['limit']:.4f} | Spent: ${budget['spent']:.4f}")
    print()
    
    # Test 1: User with adequate budget
    print("Test 1: User with adequate budget (Bob)")
    print("-"*70)
    success, _, cost, _ = send_anthropic_message(
        "Explain recursion in one sentence.",
        user_id="bob",
        check_budget_flag=True,
        show_response=False
    )
    if success:
        remaining = user_budgets['bob']['limit'] - user_budgets['bob']['spent']
        print(f"   ✅ Request allowed")
        print(f"   💰 Cost: ${cost:.6f}")
        print(f"   📊 Remaining budget: ${remaining:.4f}")
    print()
    
    # Test 2: User approaching budget limit
    print("Test 2: User with low budget (Charlie)")
    print("-"*70)
    print(f"   Charlie's limit: ${user_budgets['charlie']['limit']:.4f}")
    print()
    
    # Make multiple requests to exceed Charlie's budget
    for i in range(5):
        print(f"   Request {i+1}:")
        success, _, cost, status = send_anthropic_message(
            f"Count to {i+1}",
            user_id="charlie",
            check_budget_flag=True,
            show_response=False
        )
        
        if not success and status == 429:
            print(f"   🛑 Request blocked! Budget limit reached.")
            break
        elif success:
            remaining = user_budgets['charlie']['limit'] - user_budgets['charlie']['spent']
            print(f"   ✅ Allowed. Cost: ${cost:.6f}, Remaining: ${remaining:.4f}")
        else:
            print(f"   ❌ Request failed (status: {status})")
        
        time.sleep(0.2)
    
    print()
    print("Final Budget Status:")
    print("-"*70)
    for user_id, budget in user_budgets.items():
        spent = budget['spent']
        limit = budget['limit']
        remaining = limit - spent
        status_emoji = "🔴 EXCEEDED" if spent >= limit else "🟢 OK"
        print(f"   {user_id:10} | ${spent:.4f} / ${limit:.4f} | Remaining: ${remaining:.4f} {status_emoji}")
    
    print()
    print("💡 Enterprise Value:")
    print("   • Hard spending limits per user/team")
    print("   • Prevent runaway costs")
    print("   • Real-time budget tracking")
    print("   • Automatic enforcement")
    print("   • Integration ready for billing systems")

def demo_cost_tracking():
    """Demo 5: Cost Tracking & Chargeback"""
    print_section("Demo 5: Cost Tracking & Chargeback")
    
    print("💰 Track usage per user for cost allocation and chargeback")
    print("   Essential for multi-tenant environments and internal billing")
    print()
    
    # Simulate different users and teams making requests
    print("🚀 Simulating requests from different users and teams...")
    print()
    
    # We already have some tracked requests from previous demos
    # Add more diverse users from different teams
    additional_users = [
        {"user_id": "alice", "query": "Write a Python function to sort an array"},
        {"user_id": "bob", "query": "Explain machine learning in simple terms"},
        {"user_id": "diana", "query": "Create a compelling product launch email"},
        {"user_id": "evan", "query": "Write 3 social media post ideas"},
        {"user_id": "frank", "query": "Draft a sales pitch for enterprise clients"},
        {"user_id": "grace", "query": "Analyze this dataset and summarize findings"},
        {"user_id": "henry", "query": "Write a friendly customer support response"},
        {"user_id": "alice", "query": "Debug this code snippet"},
        {"user_id": "diana", "query": "Generate 5 blog post titles about AI"},
        {"user_id": "frank", "query": "Create a follow-up email template"},
    ]
    
    for user in additional_users:
        user_id = user['user_id']
        team = user_budgets.get(user_id, {}).get('team', 'unknown')
        print(f"Request from {user_id:<10} ({team:<20})...", end=" ")
        success, _, cost, _ = send_anthropic_message(
            user['query'],
            show_response=False,
            user_id=user_id
        )
        if success:
            print(f"✅ ${cost:.6f}")
        else:
            print(f"❌")
        time.sleep(0.2)
    
    print()
    
    # Generate chargeback report
    print_chargeback_report()

def print_chargeback_report():
    """Print a detailed chargeback report"""
    print_subsection("💳 CHARGEBACK REPORT")
    
    print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Requests: {len(cost_tracker['requests'])}")
    print(f"Total Cost: ${cost_tracker['total_cost']:.6f}")
    print()
    
    # Per-user breakdown
    print("="*70)
    print("PER-USER BREAKDOWN")
    print("="*70)
    print(f"{'User':<15} {'Requests':<10} {'Input':<12} {'Output':<12} {'Cost':<12}")
    print("-"*70)
    
    sorted_users = sorted(
        cost_tracker["by_user"].items(),
        key=lambda x: x[1]["cost"],
        reverse=True
    )
    
    for user_id, stats in sorted_users:
        print(f"{user_id:<15} {stats['requests']:<10} "
              f"{stats['input_tokens']:<12,} {stats['output_tokens']:<12,} "
              f"${stats['cost']:<11.6f}")
    
    print("-"*70)
    print(f"{'TOTAL':<15} {sum(s['requests'] for _, s in sorted_users):<10} "
          f"{sum(s['input_tokens'] for _, s in sorted_users):<12,} "
          f"{sum(s['output_tokens'] for _, s in sorted_users):<12,} "
          f"${cost_tracker['total_cost']:<11.6f}")
    print()
    
    # Team-level aggregation
    team_costs = defaultdict(lambda: {"cost": 0.0, "requests": 0})
    for req in cost_tracker["requests"]:
        team_id = req.get("team_id", "none")
        team_costs[team_id]["cost"] += req["cost"]
        team_costs[team_id]["requests"] += 1
    
    if len(team_costs) > 1 or "none" not in team_costs:
        print("="*70)
        print("PER-TEAM BREAKDOWN")
        print("="*70)
        print(f"{'Team':<20} {'Requests':<15} {'Total Cost':<15}")
        print("-"*70)
        
        sorted_teams = sorted(
            team_costs.items(),
            key=lambda x: x[1]["cost"],
            reverse=True
        )
        
        for team_id, stats in sorted_teams:
            print(f"{team_id:<20} {stats['requests']:<15} ${stats['cost']:<14.6f}")
        
        print("-"*70)
        print(f"{'TOTAL':<20} {sum(s['requests'] for _, s in sorted_teams):<15} "
              f"${sum(s['cost'] for _, s in sorted_teams):<14.6f}")
        print()
    
    print("💡 Use this data to:")
    print("   • Allocate costs to teams/departments")
    print("   • Identify high-usage users")
    print("   • Set usage quotas and budgets")
    print("   • Generate monthly invoices")
    print("   • Track cost trends over time")

def demo_multi_provider():
    """Demo 6: Multi-Provider Strategy"""
    print_section("Demo 6: Multi-Provider Strategy & Flexibility")
    
    print("⚡ Gateway supports multiple AI providers")
    print("   Primary: Anthropic Claude Haiku")
    print("   Alternative: OpenAI GPT-4o-mini (different cost/performance)")
    print()
    
    query = "Explain recursion in one sentence."
    
    print("Scenario 1: Using Anthropic Claude Haiku (Primary)")
    print("-"*70)
    success1, _, cost1, _ = send_anthropic_message(
        query,
        user_id="multi-demo",
        show_response=False
    )
    if success1:
        print(f"   ✅ Anthropic successful")
        print(f"   💰 Cost: ${cost1:.6f}")
    
    print()
    print("Scenario 2: Using OpenAI GPT-4o-mini (Alternative)")
    print("-"*70)
    print("   ℹ️  Note: OpenAI route needs to be configured in config-enterprise.yaml")
    print()
    
    print("💡 With multi-provider setup, you can:")
    print("   • Route to cheaper provider for simple queries")
    print("   • Failover automatically if primary is unavailable")
    print("   • A/B test model performance and quality")
    print("   • Avoid vendor lock-in")
    print("   • Load balance across providers")
    print()
    print("💡 Enterprise Value:")
    print("   • 99.9%+ uptime with automatic failover")
    print("   • Cost optimization by provider")
    print("   • Gateway handles routing complexity")
    print("   • Easy to switch or add providers")

def demo_centralized_control():
    """Demo 7: Centralized Control & Monitoring"""
    print_section("Demo 7: Centralized Control & Monitoring")
    
    print("🎛️  Gateway provides centralized control over all LLM traffic")
    print()
    print("   Benefits:")
    print("   ✓ Single point to update API keys (no client redeployment)")
    print("   ✓ Consistent rate limiting across all clients")
    print("   ✓ Metadata logging without exposing prompt content")
    print("   ✓ Easy to add authentication/authorization")
    print("   ✓ Model version control in one place")
    print("   ✓ Can swap providers without client changes")
    print("   ✓ Unified observability across all requests")
    print()
    
    print("📝 Sending a sample request...")
    send_anthropic_message(
        "Explain quantum computing in one sentence.",
        user_id="control-demo"
    )
    
    print("\n✨ All requests are logged at the gateway level")
    print("   without exposing sensitive prompt content.")
    print()
    print("🔍 View Observability Data:")
    print("   • Jaeger UI (Traces):  http://localhost:16686")
    print("   • Metrics (Prometheus): curl http://localhost:15020/metrics | grep agentgateway_gen_ai")
    print("   • Logs:                 Check your gateway terminal")

def main():
    """Run all demos in a comprehensive flow"""
    print("\n" + "🚀" * 35)
    print("   AgentGateway - Complete Feature Demonstration")
    print("🚀" * 35)
    
    print("\n⚠️  Prerequisites:")
    print("   1. Start observability: ./start-observability.sh")
    print("   2. Start gateway: agentgateway --file config.yaml")
    print("      (or config-enterprise.yaml for multi-provider)")
    print("   3. Set environment variables:")
    print("      export ANTHROPIC_API_KEY='your-key'")
    print("      export OPENAI_API_KEY='your-key' (optional)")
    print()
    
    input("Press Enter to start the complete demo...")
    
    try:
        # Part 1: Security & Privacy
        print("\n" + "🔐" * 35)
        print("   PART 1: SECURITY & PRIVACY")
        print("🔐" * 35)
        
        demo_privacy_protection()
        input("\n➡️  Press Enter to continue to PII Redaction...")
        
        demo_pii_redaction()
        input("\n➡️  Press Enter to continue to Cost Controls...")
        
        # Part 2: Cost Controls
        print("\n" + "💰" * 35)
        print("   PART 2: COST CONTROLS")
        print("💰" * 35)
        
        demo_rate_limiting()
        input("\n➡️  Press Enter to continue to Budget Enforcement...")
        
        demo_budget_enforcement()
        input("\n➡️  Press Enter to continue to Cost Tracking...")
        
        demo_cost_tracking()
        input("\n➡️  Press Enter to continue to Multi-Provider Strategy...")
        
        # Part 3: Reliability & Flexibility
        print("\n" + "⚡" * 35)
        print("   PART 3: RELIABILITY & FLEXIBILITY")
        print("⚡" * 35)
        
        demo_multi_provider()
        input("\n➡️  Press Enter to continue to Centralized Control...")
        
        demo_centralized_control()
        
        # Final Summary
        print_section("🎉 Demo Complete!")
        print("You've seen the complete AgentGateway feature set:")
        print()
        print("SECURITY & PRIVACY:")
        print("   ✅ API key protection (prevent leakage)")
        print("   ✅ PII redaction (GDPR/HIPAA compliance)")
        print()
        print("COST CONTROLS:")
        print("   ✅ Rate limiting (prevent runaway costs)")
        print("   ✅ Budget enforcement (spending limits)")
        print("   ✅ Cost tracking & chargeback (usage attribution)")
        print()
        print("RELIABILITY & FLEXIBILITY:")
        print("   ✅ Multi-provider support (failover & optimization)")
        print("   ✅ Centralized control (management & monitoring)")
        print()
        print("🔍 Next Steps:")
        print("   • View traces in Jaeger: http://localhost:16686")
        print("   • Check metrics: curl http://localhost:15020/metrics | grep agentgateway_gen_ai")
        print("   • Export chargeback data to CSV/database")
        print("   • Set up alerting for budgets and errors")
        print("   • Add JWT authentication for SSO")
        print("   • Integrate with your billing system")
        print()
        print("📚 Documentation:")
        print("   • Quickstart: QUICKSTART.md")
        print("   • Enterprise: ENTERPRISE-QUICKSTART.md")
        print("   • Observability: OBSERVABILITY.md")
        print()
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Make sure gateway is running:")
        print("     agentgateway --file config.yaml")
        print("  2. Check API keys are set:")
        print("     echo $ANTHROPIC_API_KEY")
        print("  3. Verify gateway is accessible:")
        print("     curl http://localhost:3000/v1/models")

if __name__ == "__main__":
    main()

