# 📧 Agentic Email Response System — Documentation

## Overview

This system is an **Agentic AI pipeline** that autonomously reads, classifies, drafts responses to, and schedules dispatch of customer emails — without any manual intervention. It is built with **Groq API** (fast LLM inference), **FAISS** (vector similarity search for RAG), and a **Streamlit** UI.

---

## System Architecture

```
Customer Emails (file / manual / sample)
            │
            ▼
 ┌─────────────────────────────┐
 │   Orchestrator              │  coordinates all agents sequentially
 └─────────────────────────────┘
            │
    ┌───────┴──────────────────────────────┐
    ▼                                      │
 ┌──────────────────────────┐              │
 │  Agent 1: Classifier     │  Groq        │
 │  llama-3.1-8b, temp=0.3  │  LLM call   │
 │  • Sentiment (5 types)   │              │
 │  • Priority (4 levels)   │              │
 │  • Urgency score 0–100   │              │
 │  • Category (10 types)   │              │
 │  • Escalation flag       │              │
 └──────────────────────────┘              │
            │                              │
            ▼                              │
 ┌──────────────────────────┐              │
 │  RAG Agent               │  FAISS +    │
 │  • FAISS IndexFlatIP     │  Transformer based Embedding│
 │  • 19 KB documents       │  vectors    │
 │  • Returns top-3 chunks  │              │
 └──────────────────────────┘              │
            │                              │
            ▼                              │
 ┌──────────────────────────┐              │
 │  Agent 2: Drafter        │  Groq        │
 │  llama-3.1-8b, temp=0.7  │  LLM call   │
 │  • Uses classification   │              │
 │  • Uses RAG context      │              │
 │  • Tone-matched response │              │
 └──────────────────────────┘              │
            │                              │
            ▼                              │
 ┌──────────────────────────┐              │
 │  Agent 3: Reviewer       │  Groq        │
 │  llama-3.1-8b, temp=0.1  │  LLM call   │
 │  • Confidence 0.0–1.0    │              │
 │  • Tone check            │              │
 │  • Placeholder detection │              │
 │  • Auto-approve ≥0.75    │              │
 └──────────────────────────┘              │
            │                              │
            ▼                              │
 ┌──────────────────────────┐              │
 │  Scheduler (Rule-based)  │◄─────────────┘
 │  CRITICAL → 15 min       │
 │  HIGH     → 30 min       │
 │  MEDIUM   → 60 min       │
 │  LOW      → 4 hours      │
 └──────────────────────────┘
            │
            ▼
    SQLite Database (audit trail)
            │
            ▼
    Streamlit Dashboard
```

---

## Agent Orchestration Strategy

The **Orchestrator** (`agents/orchestrator.py`) implements a **sequential pipeline** pattern:

1. Each agent receives the **accumulated result dict** (grows richer at each step)
2. Every agent call is **independent** — agents cannot call each other
3. The Orchestrator is the **single point of control**
4. Failures in any agent are **caught and handled gracefully** — the pipeline continues
5. Final results are **sorted by urgency score** (highest first) before display

This design is intentional: sequential pipelines are easier to debug and demo than parallel or agentic loops, while still providing clear separation of concerns.

---

## File & Module Structure

```
email_agent/
├── app.py                        # Streamlit UI — all tabs, layout, interaction
├── requirements.txt              # Dependencies
│
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py           # Pipeline coordinator
│   ├── classifier.py             # Agent 1 — email classification (Groq)
│   ├── rag_agent.py              # RAG — FAISS knowledge retrieval
│   ├── drafter.py                # Agent 2 — response drafting (Groq)
│   ├── reviewer.py               # Agent 3 — quality review (Groq)
│   └── scheduler.py              # Rule-based dispatch scheduler
│
└── utils/
    ├── __init__.py
    ├── database.py               # SQLite persistence
    └── sample_emails.py          # 8 diverse demo emails
```

---

## Agent Details

### Agent 1 — ClassifierAgent

**File:** `agents/classifier.py`  
**Model:** `llama-3.1-8b-instant`  
**Temperature:** `0.3` (low randomness = consistent classification)

**Input:** Raw email dict `{sender, subject, body, timestamp}`

**Output (JSON):**
```json
{
  "sentiment": "angry | frustrated | neutral | satisfied | inquiry",
  "priority": "critical | high | medium | low",
  "urgency_score": 85,
  "category": "billing | technical_support | complaint | ...",
  "escalation_required": true,
  "key_issues": ["unauthorized account access", "payment data exposure"]
}
```

**Priority Logic (in system prompt):**
| Priority | Conditions |
|----------|-----------|
| Critical | Safety, legal threat, account breach, data exposure |
| High | Angry/frustrated, billing dispute, service outage |
| Medium | General complaint, shipping delay, product question |
| Low | Positive feedback, general inquiry |

---

### RAGAgent — Knowledge Retrieval

**File:** `agents/rag_agent.py`  
**Method:** FAISS   
**Embedding:** SentenceTransformers (all-MiniLM-L6-v2)

**Knowledge Base:** 19 curated documents covering:
- Refund & billing policies
- Shipping timelines and claims
- Technical troubleshooting steps
- Account management
- Complaint escalation procedures
- Product warranty information

**Retrieval:** Top-3 most semantically relevant passages per email query.

---

### Agent 2 — DraftingAgent

**File:** `agents/drafter.py`  
**Model:** `llama-3.1-8b-instant`  
**Temperature:** `0.7` (higher = more natural, varied language)

**Input:** Full pipeline dict including classification + RAG context  
**Output:** Complete email response body (100–200 words), signed by "Alex from Customer Support"

**Tone Mapping:**
| Sentiment | Tone Applied |
|-----------|-------------|
| Angry | Empathetic, calm, solution-focused |
| Frustrated | Understanding, apologetic, action-oriented |
| Neutral | Professional, clear, helpful |
| Satisfied | Warm, appreciative, reinforcing |
| Inquiry | Informative, friendly, thorough |

---

### Agent 3 — ReviewAgent

**File:** `agents/reviewer.py`  
**Model:** `llama-3.1-8b-instant`  
**Temperature:** `0.1` (near-deterministic = consistent scoring)

**Input:** Original email + drafted response  
**Output (JSON):**
```json
{
  "confidence": 0.88,
  "review_notes": "Response is empathetic and addresses all key issues clearly.",
  "tone_appropriate": true,
  "addresses_all_issues": true,
  "contains_placeholders": false,
  "approved": true
}
```

**Auto-approval rule:** `confidence >= 0.75 AND contains_placeholders == false`

---

### Scheduler — Rule-based

**File:** `agents/scheduler.py`  
**Type:** Deterministic (no LLM required)

| Priority | Delay | Rationale |
|----------|-------|-----------|
| Critical | 15 min | Account/security emergencies |
| High | 30 min | Angry customers, billing disputes |
| Medium | 60 min | Standard complaints |
| Low | 4 hours | General inquiries, positive feedback |

---

## Email Prioritization Logic

Prioritization is two-tier:

1. **Priority label** assigned by ClassifierAgent (critical/high/medium/low)
2. **Urgency score** (0–100) used for fine-grained sorting within the same priority tier

The inbox queue always displays emails **sorted by urgency score** descending, ensuring the most time-sensitive emails are always at the top.

---

## RAG (Retrieval-Augmented Generation) — How It Works

```
Query = email_subject + email_body
    │
    ▼
SentenceTransformers vectorization → query vector (normalized)
    │
    ▼
FAISS IndexFlatIP.search(query_vector, k=3)
    │
    ▼
Returns top-3 knowledge base documents by cosine similarity
    │
    ▼
Documents injected into DraftingAgent prompt as context
```

This allows the drafted response to accurately reference company policies (e.g. exact refund windows, support hours) rather than hallucinating them.

---

## Database Schema

**Table:** `emails` (SQLite, file: `email_agent.db`)

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| sender | TEXT | Customer email address |
| subject | TEXT | Email subject |
| body | TEXT | Full email body |
| sentiment | TEXT | Classified sentiment |
| priority | TEXT | Priority level |
| urgency_score | INTEGER | 0–100 urgency |
| category | TEXT | Issue category |
| escalation_required | INTEGER | 0 or 1 |
| key_issues | TEXT | JSON array |
| rag_context | TEXT | JSON array of retrieved docs |
| response_draft | TEXT | AI drafted response |
| confidence | REAL | Review confidence score |
| review_notes | TEXT | Reviewer feedback |
| approved | INTEGER | 0 or 1 |
| scheduled_time | TEXT | Dispatch datetime |
| processed_at | TEXT | Pipeline run timestamp |

---

## Setup & Running

### Prerequisites
- Python 3.9+
- Groq API key (free at console.groq.com)

### Install
```bash
cd email_agent
pip install -r requirements.txt
```

### Run
```bash
streamlit run app.py
```

### Usage
1. Open the app in your browser (usually http://localhost:8501)
2. Paste your **Groq API key** in the sidebar
3. Click **"Load Sample Emails"** to see the full pipeline in action
4. Click any email card → **"View →"** to inspect classification, RAG context, drafted response, confidence score, and schedule
5. Use the **"Edit Response"** area to make adjustments
6. Click **"✅ Approve & Mark Scheduled"** to approve a response
7. Check the **Analytics** tab for aggregate metrics

### Add your own emails
- Use the **"➕ Add Email"** tab to paste any email
- Or upload a `.txt` or `.eml` file

---

## Technology Choices & Rationale

| Component | Technology | Why |
|-----------|-----------|-----|
| LLM inference | Groq API (llama-3.1-8b) | Free, extremely fast (~10x faster than OpenAI), JSON mode reliable |
| Vector DB | FAISS (faiss-cpu) | Industry standard, runs fully in-memory, no server needed |
| Embeddings | `all-MiniLM-L6-v2` (sentence-transformers) | 384-dim dense vectors, ~22 MB, genuine semantic similarity, CPU-friendly |
| UI | Streamlit | Fastest Python UI for demos, zero HTML/JS needed |
| Database | SQLite | Zero configuration, file-based, full audit trail |
| Orchestration | Python classes | Simple, debuggable, no framework overhead |

---

## Key Design Decisions

1. **Temperature tuning per agent:**  Classifier at 0.3 (deterministic), Drafter at 0.7 (creative), Reviewer at 0.1 (strict scoring) — each tuned for its specific role.

2. **JSON-only LLM outputs for Classifier & Reviewer:** System prompts enforce pure JSON response. Regex strips any accidental markdown fences before `json.loads()`.

3. **Graceful degradation:** Every agent has a try/except returning sane defaults. The pipeline never crashes — a failed agent step yields fallback values.

4. **No circular dependencies:** Agents are one-directional. Drafter never re-calls Classifier. Reviewer never re-calls Drafter. The Orchestrator is the only component that coordinates.

5. **FAISS with TF-IDF instead of embedding model:** Avoids the need to download a 400MB+ sentence-transformers model at demo time. Works offline. For production, swap `_embed` for `sentence-transformers` for better semantic search quality.
