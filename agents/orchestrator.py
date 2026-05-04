"""
Orchestrator — coordinates the 4-agent pipeline:
  1. ClassifierAgent  → sentiment, priority, urgency, category
  2. RAGAgent         → retrieves relevant knowledge base chunks via FAISS
  3. DraftingAgent    → writes personalised draft using classification + RAG context
  4. ReviewAgent      → scores confidence, checks tone, flags issues
Then SchedulerAgent assigns dispatch time based on priority.
"""

from agents.classifier import ClassifierAgent
from agents.drafter import DraftingAgent
from agents.reviewer import ReviewAgent
from agents.rag_agent import RAGAgent
from agents.scheduler import SchedulerAgent

class EmailOrchestrator:
    def __init__(self, api_key: str):
        self.classifier = ClassifierAgent(api_key)
        self.rag        = RAGAgent()
        self.drafter    = DraftingAgent(api_key)
        self.reviewer   = ReviewAgent(api_key)
        self.scheduler  = SchedulerAgent()

    def process_single(self, email: dict) -> dict:
        """Run one email through the full pipeline."""
        result = dict(email)  # carry forward original fields

        # Step 1 — Classify
        classification = self.classifier.classify(email)
        result.update(classification)

        # Step 2 — RAG knowledge lookup
        query = f"{email.get('subject','')} {email.get('body','')}"
        rag_docs = self.rag.retrieve(query, k=3)
        result["rag_context"] = rag_docs

        # Step 3 — Draft response
        draft_info = self.drafter.draft(result)
        result.update(draft_info)

        # Step 4 — Review
        review_info = self.reviewer.review(result)
        result.update(review_info)

        # Step 5 — Schedule
        schedule_info = self.scheduler.schedule(result)
        result.update(schedule_info)

        return result

    def process_batch(self, emails: list) -> list:
        """Process a list of emails and return sorted by urgency."""
        results = [self.process_single(e) for e in emails]
        results.sort(key=lambda x: x.get("urgency_score", 0), reverse=True)
        return results
