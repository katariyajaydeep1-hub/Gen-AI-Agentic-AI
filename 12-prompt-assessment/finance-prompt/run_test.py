"""Runs the assessment's exact scenario against FINANCE_PROMPT."""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from finance_prompt import FINANCE_PROMPT

load_dotenv(dotenv_path="../../.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CONTEXT = """Company: Infosys Ltd.

Recent Performance:
- Revenue growth: 6% YoY
- Net profit growth: 4% YoY

Market Sentiment:
- Analyst consensus: Neutral
- Recent news: Stable outlook, cautious IT spending

Valuation:
- P/E ratio: 28
- Sector average P/E: 25

Risks:
- Slowdown in global IT demand
- Currency fluctuations"""

USER_QUERY = "Should I invest in Infosys right now?"

prompt = FINANCE_PROMPT.format(context=CONTEXT, user_query=USER_QUERY)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0,
    response_format={"type": "json_object"},
)

raw = response.choices[0].message.content
parsed = json.loads(raw)

print("=" * 60)
print("ASSESSMENT QUERY:", USER_QUERY)
print("=" * 60)
print(json.dumps(parsed, indent=2))
print()
print("=" * 60)
print("VALIDATION CHECKS")
print("=" * 60)

advisory_terms = ["buy", "sell", "hold", "strong buy", "strong sell"]
rec_lower = parsed["recommendation"].lower()
print(f"[{'PASS' if not any(t in rec_lower for t in advisory_terms) else 'FAIL'}] No Buy/Sell/Hold in recommendation")
risk_phrases = [
    "market risk",
    "subject to market",
    "markets carry",
    "market-related risk",
    "carry inherent risk",
    "markets carry inherent risk",
    "markets are subject",
    "investments are subject to market",
    "equity markets carry",
]
risk_mentioned = any(phrase in rec_lower for phrase in risk_phrases)
print(f"[{'PASS' if risk_mentioned else 'FAIL'}] Market risk mentioned in recommendation")
print(f"[{'PASS' if 'sebi' in rec_lower or 'advisor' in rec_lower else 'FAIL'}] Advisor consultation mentioned")
print(f"[{'PASS' if parsed['company'] == 'Infosys Ltd.' else 'FAIL'}] Company name correct")
print(f"[{'PASS' if len(parsed['risks']) >= 2 else 'FAIL'}] At least 2 risks listed")
print(f"[{'PASS' if parsed['confidence'] in ['high', 'medium', 'low'] else 'FAIL'}] Confidence is valid enum")
