"""
ClassifierAgent — Agent 1
Uses Groq (llama-3.1-8b-instant, temp=0.3) to analyse incoming email and return:
  - sentiment       : angry | frustrated | neutral | satisfied | inquiry
  - priority        : critical | high | medium | low
  - urgency_score   : 0–100
  - category        : billing | technical_support | complaint | returns | ...
  - escalation_required : bool
  - key_issues      : list[str]
"""

import json
import re
from groq import Groq


SYSTEM_PROMPT = """You are an expert email classification agent for a customer support system.

Analyse the given customer email and respond ONLY with a valid JSON object — no markdown, no explanation.

Return exactly these keys:
{
  "sentiment": one of [angry, frustrated, neutral, satisfied, inquiry],
  "priority": one of [critical, high, medium, low],
  "urgency_score": integer 0-100,
  "category": one of [billing, technical_support, complaint, returns_refunds, shipping, account_access, product_inquiry, feedback, escalation, general],
  "escalation_required": true or false,
  "key_issues": [list of 1-3 short issue strings]
}

Priority rules:
- critical: safety issue, legal threat, account locked, data breach mention
- high:     angry/frustrated tone, billing dispute, service down
- medium:   general complaint, delayed shipping, product question
- low:      positive feedback, general inquiry, compliment
"""


class ClassifierAgent:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model  = "llama-3.1-8b-instant"

    def classify(self, email: dict) -> dict:
        prompt = (
            f"From: {email.get('sender','')}\n"
            f"Subject: {email.get('subject','')}\n"
            f"Body:\n{email.get('body','')}"
        )
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=0.3,
                max_tokens=400,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt},
                ],
            )
            raw = resp.choices[0].message.content.strip()
            # Strip potential markdown fences
            raw = re.sub(r"```json|```", "", raw).strip()
            return json.loads(raw)
        except Exception as e:
            # Graceful fallback
            return {
                "sentiment": "neutral",
                "priority": "medium",
                "urgency_score": 50,
                "category": "general",
                "escalation_required": False,
                "key_issues": [str(e)],
            }
