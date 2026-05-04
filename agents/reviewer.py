"""
ReviewAgent — Agent 3
Uses Groq (llama-3.1-8b-instant, temp=0.1) to evaluate the drafted response and return:
  - confidence     : float 0.0–1.0
  - review_notes   : string with any flags or suggestions
  - approved       : bool (auto-approved if confidence >= 0.75)
"""

import json
import re
from groq import Groq


SYSTEM_PROMPT = """You are a quality assurance agent reviewing AI-drafted customer support emails.

Evaluate the response against the original email and return ONLY valid JSON — no markdown, no explanation:

{
  "confidence": float between 0.0 and 1.0,
  "review_notes": "short one-sentence note on quality or issues",
  "tone_appropriate": true or false,
  "addresses_all_issues": true or false,
  "contains_placeholders": true or false,
  "approved": true or false
}

Scoring guide:
- 0.9–1.0: Excellent — fully addresses issues, perfect tone, ready to send
- 0.75–0.9: Good — minor improvements possible but approvable
- 0.5–0.75: Needs work — misses issues or wrong tone
- < 0.5:   Poor — significant problems, do not approve

Set approved=true if confidence >= 0.75 AND contains_placeholders=false
"""


class ReviewAgent:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model  = "llama-3.1-8b-instant"

    def review(self, email_data: dict) -> dict:
        prompt = f"""ORIGINAL EMAIL:
Subject: {email_data.get('subject','')}
Body: {email_data.get('body','')}

SENTIMENT: {email_data.get('sentiment','')}
KEY ISSUES: {', '.join(email_data.get('key_issues',[]))}

DRAFTED RESPONSE:
{email_data.get('response_draft','')}

Evaluate this response:"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=0.1,
                max_tokens=300,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt},
                ],
            )
            raw = resp.choices[0].message.content.strip()
            raw = re.sub(r"```json|```", "", raw).strip()
            data = json.loads(raw)
            return {
                "confidence":            float(data.get("confidence", 0.7)),
                "review_notes":          data.get("review_notes", ""),
                "tone_appropriate":      data.get("tone_appropriate", True),
                "addresses_all_issues":  data.get("addresses_all_issues", True),
                "contains_placeholders": data.get("contains_placeholders", False),
                "approved":              data.get("approved", False),
            }
        except Exception as e:
            return {
                "confidence":   0.65,
                "review_notes": f"Review agent error: {e}",
                "approved":     False,
            }
