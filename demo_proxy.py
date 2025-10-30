#!/usr/bin/env python3
"""
AgentGateway Demo: Privacy, Cost Control & Chargeback
======================================================
This demo shows how AgentGateway provides:
1. Data leakage prevention (API keys hidden from clients)
2. Privacy protection (metadata-only logging)
3. Cost controls (rate limiting)
4. Cost tracking & chargeback (usage attribution)
"""

import requests
import json
import time
from datetime import datetime
from collections import defaultdict

# Gateway endpoint (no API key needed on client side!)
GATEWAY_URL = "http://localhost:3000/v1/messages"

# Anthropic Claude pricing (as of 2024)
# https://www.anthropic.com/pricing
PRICING = {
    "claude-haiku-4-5-20251001": {
        "input": 0.80 / 1_000_000,   # $0.80 per million input tokens
        "output": 4.00 / 1_000_000,  # $4.00 per million output tokens
    }
}

# Cost tracking storage
cost_tracker = {
    "requests": [],
    "by_user": defaultdict(lambda: {"requests": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0}),
    "total_cost": 0.0
}

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def send_message(content, show_response=True, user_id=None, team_id=None):
    """Send a message through the gateway with user tracking"""
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
    
    # Add user identification headers for cost tracking
    if user_id:
        headers["X-User-ID"] = user_id
    if team_id:
        headers["X-Team-ID"] = team_id
    
    try:
        start_time = time.time()
        response = requests.post(GATEWAY_URL, json=payload, headers=headers)
        elapsed_time = time.time() - start_time
        
        if show_response:
            print(f"⏱️  Response time: {elapsed_time:.2f}s")
            print(f"📊 Status Code: {response.status_code}")
            
        if response.status_code == 200:
            data = response.json()
            
            # Track costs
            if "usage" in data:
                input_tokens = data["usage"].get("input_tokens", 0)
                output_tokens = data["usage"].get("output_tokens", 0)
                cost = calculate_cost(input_tokens, output_tokens)
                
                # Record the request
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
                
                if show_response:
                    print(f"💰 Cost: ${cost:.6f} (In: {input_tokens}, Out: {output_tokens} tokens)")
            
            if show_response and "content" in data:
                print(f"✅ Response: {data['content'][0]['text'][:200]}...")
            return True, response.status_code, data
        elif response.status_code == 429:
            print(f"🛑 Rate Limited! (Cost control working)")
            return False, response.status_code, None
        else:
            print(f"❌ Error: {response.status_code}")
            if show_response:
                print(f"   {response.text}")
            return False, response.status_code, None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False, None, None

def calculate_cost(input_tokens, output_tokens, model="claude-haiku-4-5-20251001"):
    """Calculate cost based on token usage"""
    pricing = PRICING.get(model, PRICING["claude-haiku-4-5-20251001"])
    input_cost = input_tokens * pricing["input"]
    output_cost = output_tokens * pricing["output"]
    return input_cost + output_cost

def demo_privacy_protection():
    """Demo 1: Privacy & Data Leakage Prevention"""
    print_section("Demo 1: Privacy & Data Leakage Prevention")
    
    print("🔒 Key Feature: API keys are stored in the gateway")
    print("   Clients never need to know or handle the API key")
    print("   This prevents:")
    print("   - API key leakage in client applications")
    print("   - Exposed keys in browser dev tools")
    print("   - Keys committed to version control")
    print()
    
    print("📝 Sending request WITHOUT API key in client code...")
    send_message("What is 2+2? Answer briefly.", user_id="demo-user")
    
    print("\n✨ Notice: The request succeeded without the client having the API key!")
    print("   The gateway handled authentication securely.")

def demo_cost_controls():
    """Demo 2: Cost Controls via Rate Limiting"""
    print_section("Demo 2: Cost Controls via Rate Limiting")
    
    print("💰 Gateway configured with rate limit: 10 requests/60 seconds")
    print("   This prevents:")
    print("   - Runaway costs from bugs or malicious usage")
    print("   - DDoS attacks on your LLM budget")
    print("   - Accidental infinite loops")
    print()
    
    print("🚀 Sending 12 rapid requests to test rate limiting...")
    print()
    
    success_count = 0
    rate_limited_count = 0
    
    for i in range(12):
        print(f"Request {i+1}/12: ", end="")
        success, status_code, _ = send_message(f"Count to {i+1}", show_response=False, user_id="rate-limit-test")
        
        if success:
            success_count += 1
            print(f"✅ Success")
        elif status_code == 429:
            rate_limited_count += 1
            print(f"🛑 Rate Limited")
        else:
            print(f"❌ Error (status: {status_code})")
        
        time.sleep(0.1)  # Small delay between requests
    
    print()
    print(f"📊 Results:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   🛑 Rate Limited: {rate_limited_count}")
    print(f"   💰 Cost saved by preventing excessive requests!")

def demo_centralized_control():
    """Demo 3: Centralized Control & Monitoring"""
    print_section("Demo 3: Centralized Control & Monitoring")
    
    print("🎛️  Gateway provides centralized control:")
    print()
    print("   ✓ Single point to update API keys")
    print("   ✓ Consistent rate limiting across all clients")
    print("   ✓ Metadata logging (not sensitive content)")
    print("   ✓ Easy to add authentication/authorization")
    print("   ✓ Model version control in one place")
    print("   ✓ Can swap providers without client changes")
    print()
    
    print("📝 Sending a sample request...")
    send_message("Explain quantum computing in one sentence.", user_id="control-demo")
    
    print("\n✨ All requests are logged at the gateway level")
    print("   without exposing sensitive prompt content.")

def demo_cost_tracking_chargeback():
    """Demo 4: Cost Tracking & Chargeback"""
    print_section("Demo 4: Cost Tracking & Chargeback")
    
    print("💰 Simulate multiple users from different teams making requests")
    print("   Gateway tracks usage per user for cost allocation")
    print()
    
    # Simulate different users and teams
    users = [
        {"user_id": "alice", "team_id": "engineering", "query": "Write a function to sort an array"},
        {"user_id": "bob", "team_id": "engineering", "query": "Explain recursion"},
        {"user_id": "carol", "team_id": "marketing", "query": "Write a product description"},
        {"user_id": "david", "team_id": "marketing", "query": "Create a social media post"},
        {"user_id": "alice", "team_id": "engineering", "query": "Debug this code"},
        {"user_id": "carol", "team_id": "marketing", "query": "Suggest email subject lines"},
    ]
    
    print("🚀 Sending requests from different users...\n")
    
    for i, user in enumerate(users, 1):
        print(f"Request {i}/6 - User: {user['user_id']} (Team: {user['team_id']})")
        success, _, _ = send_message(
            user['query'],
            show_response=False,
            user_id=user['user_id'],
            team_id=user['team_id']
        )
        if success:
            # Get the last recorded cost
            last_request = cost_tracker["requests"][-1]
            print(f"   💰 Cost: ${last_request['cost']:.6f}")
            print(f"   📊 Tokens: In={last_request['input_tokens']}, Out={last_request['output_tokens']}")
        print()
        time.sleep(0.5)
    
    # Generate chargeback report
    print_chargeback_report()

def print_chargeback_report():
    """Print a detailed chargeback report"""
    print_section("💳 CHARGEBACK REPORT")
    
    print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Requests: {len(cost_tracker['requests'])}")
    print(f"Total Cost: ${cost_tracker['total_cost']:.6f}")
    print()
    
    # Per-user breakdown
    print("=" * 60)
    print("PER-USER BREAKDOWN")
    print("=" * 60)
    print(f"{'User':<15} {'Requests':<10} {'Input':<12} {'Output':<12} {'Cost':<12}")
    print("-" * 60)
    
    sorted_users = sorted(
        cost_tracker["by_user"].items(),
        key=lambda x: x[1]["cost"],
        reverse=True
    )
    
    for user_id, stats in sorted_users:
        print(f"{user_id:<15} {stats['requests']:<10} "
              f"{stats['input_tokens']:<12,} {stats['output_tokens']:<12,} "
              f"${stats['cost']:<11.6f}")
    
    print("-" * 60)
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
        print("=" * 60)
        print("PER-TEAM BREAKDOWN")
        print("=" * 60)
        print(f"{'Team':<20} {'Requests':<15} {'Total Cost':<15}")
        print("-" * 60)
        
        sorted_teams = sorted(
            team_costs.items(),
            key=lambda x: x[1]["cost"],
            reverse=True
        )
        
        for team_id, stats in sorted_teams:
            print(f"{team_id:<20} {stats['requests']:<15} ${stats['cost']:<14.6f}")
        
        print("-" * 60)
        print(f"{'TOTAL':<20} {sum(s['requests'] for _, s in sorted_teams):<15} "
              f"${sum(s['cost'] for _, s in sorted_teams):<14.6f}")
        print()
    
    print("💡 Use this data to:")
    print("   • Allocate costs to teams/departments")
    print("   • Identify high-usage users")
    print("   • Set usage quotas and budgets")
    print("   • Generate monthly invoices")
    print()

def main():
    """Run all demos"""
    print("\n" + "🌟" * 30)
    print("   AgentGateway Security & Cost Control Demo")
    print("🌟" * 30)
    
    print("\n⚠️  Prerequisites:")
    print("   1. Start the gateway: agentgateway --config config.yaml")
    print("   2. Set ANTHROPIC_API_KEY environment variable")
    print()
    
    input("Press Enter to start the demo...")
    
    try:
        demo_privacy_protection()
        input("\nPress Enter to continue to cost controls demo...")
        
        demo_cost_controls()
        input("\nPress Enter to continue to centralized control demo...")
        
        demo_centralized_control()
        input("\nPress Enter to continue to cost tracking & chargeback demo...")
        
        demo_cost_tracking_chargeback()
        
        print_section("Demo Complete!")
        print("🎉 You've seen how AgentGateway provides:")
        print("   • Data leakage prevention (API key security)")
        print("   • Privacy protection (metadata-only logging)")
        print("   • Cost controls (rate limiting)")
        print("   • Centralized management")
        print("   • Cost tracking & chargeback (usage attribution)")
        print()
        print("💡 Next steps:")
        print("   • Export chargeback data to CSV/database")
        print("   • Set up monthly billing reports")
        print("   • Add budget alerts per user/team")
        print("   • Integrate with your billing system")
        print()
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure the gateway is running:")
        print("  agentgateway --config config.yaml")

if __name__ == "__main__":
    main()

