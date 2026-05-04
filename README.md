# Agentic Email Response System
An AI-powered application that analyzes customer emails, generates contextual responses, and simulates scheduling using a multi-agent architecture.

Streamlit App URL: https://agentic-email-response-system-automation.streamlit.app/
---

## Features

- Upload `.txt` or `.eml` email files
- Multi-agent pipeline: **Classifier → RAG → Draft → Review → Scheduler**
- AI-generated responses using LLM (Groq)
- Priority, sentiment, and category detection
- Human approval / review workflow
- Simulated response scheduling (no actual email sending)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| LLM | Groq (LLaMA 3.3 70B) |
| RAG | SentenceTransformers (`all-MiniLM-L6-v2`) |
| Vector Search | FAISS / NumPy |
| Language | Python 3.10+ |

---

## Project Structure

```
email_agent_system/
├── agents/
│   ├── classifier_agent.py   # Category · sentiment · urgency scoring
│   ├── drafting_agent.py     # Personalised response generation
│   ├── review_agent.py       # Tone · accuracy · completeness check
│   └── scheduler_agent.py    # Send-time assignment + queue persistence
├── core/
│   ├── email_parser.py       # .eml / .txt → standard dict (single + multi-email)
│   └── rag_engine.py         # FAISS vector store + semantic query
├── knowledge_base/
│   └── faq.txt               # Company policies and FAQs for RAG
├── sample_emails/
│   └── batch.txt             # Sample multi-email .txt file
├── data/
│   └── schedule_queue.json   # Auto-created — persists scheduled emails
├── app.py                    # Streamlit application entry point
├── requirements.txt
├── .env                      # API keys (not committed to git)
└── README.md
```

---

## Setup and Run

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd email_agent_system
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env` file

```env
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_hf_token_here   # optional — only needed for private HF models
```

> Get a free Groq API key at [https://console.groq.com](https://console.groq.com)

### 5. Run the application

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## How It Works

```
Email Upload (.eml / .txt)
        ↓
Email Parser       — normalises to standard dict, handles single + multi-email files
        ↓
Classifier Agent   — detects category, sentiment, urgency score (1–10) via Groq
        ↓
Priority Sort      — highest urgency emails processed first
        ↓
RAG Engine         — retrieves relevant company policy chunks from FAISS index
        ↓
Drafting Agent     — generates personalised response draft + confidence score via Groq
        ↓
Review Agent       — checks tone, accuracy, completeness via Groq
        ↓
Scheduler Agent    — assigns send time based on urgency, writes to queue
        ↓
Streamlit Dashboard — view emails, drafts, scores, approve pending reviews
```

### Urgency → Send Time Mapping

| Urgency Score | Trigger Conditions | Scheduled Send |
|---|---|---|
| 8 – 10 | Legal threat, data loss, angry + refund | Within 1 hour |
| 5 – 7 | Support issue, follow-up, frustrated tone | Within 4 hours |
| 1 – 4 | General inquiry, feedback, neutral tone | Next business day 9 AM |

### Email Status

| Status | Meaning |
|---|---|
| `scheduled` | Auto-approved, send time assigned |
| `pending_review` | Flagged for human approval (low confidence or high urgency) |
| `spam_skipped` | Classified as spam, no draft generated |
| `dispatched` | Poller confirmed send time passed |

---

## Deployment on Streamlit Cloud

1. Push code to a public GitHub repository
2. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud) and connect your repo
3. Set the main file path to `app.py`
4. Add secrets under **Settings → Secrets**:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
HF_TOKEN = "your_hf_token_here"
```

---

## Input Email Format

### Single email `.txt`

```
From: customer@example.com
Subject: Refund not received

Hi, I requested a refund 3 weeks ago and still haven't received it.
Order #12345. Please help.
```

### Multi-email `.txt` (separated by `---`)

```
From: a@example.com
Subject: Billing issue

Body of first email...

---

From: b@example.com
Subject: Login problem

Body of second email...
```

### `.eml` files

Drop any standard `.eml` file or mbox bulk export — the parser auto-detects the format.

---

## Limitations

- No real email sending (simulation only)
- Static RAG knowledge base (requires manual update)
- No multilingual support
- No email attachment parsing (PDF, images)
- No conversation memory across sessions
- Initial load may be slow due to SentenceTransformers model download from Hugging Face

---

## Future Scope

- Real email integration via SMTP or Gmail / Outlook APIs
- Multilingual email detection and response
- Attachment processing (PDF, images via OCR)
- Async and horizontally scalable pipeline
- User authentication and role-based access control
- Persistent conversation memory across sessions
- Live SMTP dispatch with retry and backoff logic

---

## Summary

This project demonstrates a modular **Agentic AI** system for automating customer email understanding and response generation, with a **human-in-the-loop** validation workflow. Each agent in the pipeline has a single responsibility, making the system easy to extend, test, and deploy independently.
