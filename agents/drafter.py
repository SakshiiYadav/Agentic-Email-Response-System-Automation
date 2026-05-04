"""
DraftingAgent — Agent 2
Uses Groq (llama-3.1-70b-versatile, temp=0.7) to draft a personalised
customer response incorporating:
  - Classification context (priority, sentiment, category)
  - RAG-retrieved knowledge base passages
  - Appropriate tone mapped to sentiment
"""

import re
import json
from groq import Groq


TONE_MAP = {
    "angry":      "empathetic, calm, and solution-focused",
    "frustrated": "understanding, apologetic, and action-oriented",
    "neutral":    "professional, clear, and helpful",
    "satisfied":  "warm, appreciative, and reinforcing",
    "inquiry":    "informative, friendly, and thorough",
}

SYSTEM_PROMPT = """You are a senior customer support specialist drafting email responses.

You will receive:
- The original customer email
- Classification metadata (priority, sentiment, category, key issues)
- Relevant knowledge base passages for reference

Write a professional, personalised response that:
1. Opens with an appropriate greeting using the customer's name if available
2. Acknowledges the customer's concern with empathy (match the tone instruction)
3. Addresses each key issue directly using knowledge base info where relevant
4. Provides clear next steps or resolution
5. Closes warmly with your name: "Alex from Customer Support"

IMPORTANT:
- Do NOT use placeholder brackets like [X] or [INSERT]. Write a complete, ready-to-send response.
- Keep it concise: 100-200 words
- Do not repeat the knowledge base passages verbatim; synthesise naturally
- Output ONLY the email body text, no subject line, no metadata
"""


class DraftingAgent:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model  = "llama-3.1-8b-instant"

    def draft(self, email_data: dict) -> dict:
        tone      = TONE_MAP.get(email_data.get("sentiment", "neutral"), "professional and helpful")
        rag_ctx   = "\n".join(f"- {doc}" for doc in email_data.get("rag_context", []))
        key_issues= ", ".join(email_data.get("key_issues", []))
        name      = email_data.get("name", "Valued Customer")

        user_prompt = f"""CUSTOMER EMAIL:
From: {email_data.get('sender','')} ({name})
Subject: {email_data.get('subject','')}
Body:
{email_data.get('body','')}

CLASSIFICATION:
- Priority: {email_data.get('priority','medium')}
- Sentiment: {email_data.get('sentiment','neutral')} → use tone: {tone}
- Category: {email_data.get('category','general')}
- Key Issues: {key_issues}
- Escalation Required: {email_data.get('escalation_required', False)}

KNOWLEDGE BASE CONTEXT:
{rag_ctx if rag_ctx else 'No specific KB entries found — use general best practices.'}

Draft the response now:"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=0.7,
                max_tokens=600,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_prompt},
                ],
            )
            draft = resp.choices[0].message.content.strip()
            return {
                "response_draft": draft,
                "tone_used": tone,
            }
        except Exception as e:
            return {
                "response_draft": f"[Draft generation failed: {e}]",
                "tone_used": tone,
            }
