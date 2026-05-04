"""
RAGAgent — Knowledge Base via FAISS + sentence-transformers
Uses all-MiniLM-L6-v2 (384-dim dense embeddings) for genuine semantic search.
Model is ~22 MB, downloads once and is cached automatically by HuggingFace.
Falls back to TF-IDF if sentence-transformers is not installed.
"""
import os
import numpy as np
from sentence_transformers import SentenceTransformer

# ── Knowledge Base Documents ───
KNOWLEDGE_BASE = [
    ## This is a dummy Knowledge base ##
    # Billing
    "Our refund policy allows full refunds within 30 days of purchase for unused items. "
    "Partial refunds may be issued for opened or used items at our discretion.",

    "Billing disputes must be submitted within 60 days of the charge date. "
    "We will investigate and respond within 3-5 business days.",

    "We accept Visa, Mastercard, American Express, PayPal, and bank transfers. "
    "Subscriptions are billed monthly or annually as selected.",

    # Shipping
    "Standard shipping takes 5-7 business days. Express shipping (2-3 days) is available "
    "for an additional fee. Free shipping on orders over $50.",

    "Lost or damaged packages must be reported within 14 days of the expected delivery date. "
    "We will file a claim with the carrier and send a replacement if confirmed lost.",

    "International orders may be subject to customs duties and taxes. "
    "Delivery times vary from 10-21 business days for international orders.",

    # Technical Support
    "For technical issues, first try clearing browser cache and cookies. "
    "Ensure you are using a supported browser: Chrome, Firefox, Safari, Edge (latest versions).",

    "Account access issues can be resolved by resetting your password via the 'Forgot Password' link. "
    "If the issue persists, contact support with your account email.",

    "Service outages are monitored at status.ourcompany.com. "
    "We aim to resolve all P1 outages within 4 hours and communicate status every 30 minutes.",

    # Returns
    "Items must be returned in original packaging with all accessories included. "
    "Return shipping is free for defective or wrong items. Customer pays shipping for change-of-mind returns.",

    "Return requests can be initiated in your account portal under 'Orders > Return Request'. "
    "Once approved, a prepaid label is emailed within 24 hours.",

    # Account
    "To close your account, please submit a request to privacy@ourcompany.com. "
    "Account data is retained for 90 days before permanent deletion per our data policy.",

    "Two-factor authentication is available and recommended for all accounts. "
    "Enable it under Account Settings > Security.",

    # General Policies
    "Our customer support team is available Monday–Friday 9am–6pm EST. "
    "Emergency support for critical issues is available 24/7 via our priority line.",

    "We are committed to responding to all customer emails within 24 hours on business days. "
    "Complex issues may take up to 72 hours for full resolution.",

    # Complaint Handling
    "We take all complaints seriously. Escalated complaints are reviewed by our senior support team "
    "and a resolution is guaranteed within 48 hours.",

    "For unresolved issues after 3 attempts, customers may request escalation to our Customer Experience Manager.",

    # Product Info
    "Our products come with a 1-year manufacturer warranty covering defects in materials and workmanship. "
    "Extended warranty plans are available for purchase.",

    "Product manuals and troubleshooting guides are available at help.ourcompany.com/docs.",
]


class RAGAgent:
    """
    Retrieves relevant knowledge base passages using:
      - Embedding model : all-MiniLM-L6-v2 via sentence-transformers
                          (~22 MB, cached after first run, CPU-friendly)
      - Vector index    : FAISS IndexFlatIP (cosine similarity on L2-normalised vecs)
      - Fallback        : NumPy cosine if faiss-cpu not installed
    """

    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self):
        self._model      = None
        self._index      = None
        self._embeddings = None
        self._use_faiss  = False
        self._load_model()
        self._build_index()

    # ── Model loading ──────────────────────────────────────────────────────────
    def _load_model(self):
        try:
            hf_token = os.getenv("HF_TOKEN")

            if hf_token:
                self._model = SentenceTransformer(
                    self.MODEL_NAME,
                    token=hf_token
                )
            else:
                self._model = SentenceTransformer(self.MODEL_NAME)

        except ImportError:
            self._model = None

    # ── Embedding helpers ──────────────────────────────────────────────────────
    def _encode(self, texts: list) -> np.ndarray:
        """Dense 384-dim embeddings, L2-normalised for cosine via inner product."""
        if self._model is not None:
            vecs = self._model.encode(texts, normalize_embeddings=True,
                                      show_progress_bar=False)
            return np.array(vecs, dtype=np.float32)
        # ── TF-IDF fallback ────────────────────────────────────────────────────
        vocab: dict = {}
        for text in texts:
            for w in text.lower().split():
                if w not in vocab:
                    vocab[w] = len(vocab)
        self._vocab = vocab
        mat = np.zeros((len(texts), len(vocab)), dtype=np.float32)
        for i, text in enumerate(texts):
            for w in text.lower().split():
                if w in vocab:
                    mat[i, vocab[w]] += 1
            norm = np.linalg.norm(mat[i])
            if norm > 0:
                mat[i] /= norm
        return mat

    def _encode_query(self, query: str) -> np.ndarray:
        if self._model is not None:
            vec = self._model.encode([query], normalize_embeddings=True,
                                     show_progress_bar=False)
            return np.array(vec, dtype=np.float32)
        # TF-IDF fallback
        vec = np.zeros(len(self._vocab), dtype=np.float32)
        for w in query.lower().split():
            if w in self._vocab:
                vec[self._vocab[w]] += 1
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec.reshape(1, -1)

    # ── Index building ─────────────────────────────────────────────────────────
    def _build_index(self):
        self._embeddings = self._encode(KNOWLEDGE_BASE)
        try:
            import faiss
            dim = self._embeddings.shape[1]
            self._index = faiss.IndexFlatIP(dim)
            self._index.add(self._embeddings)
            self._use_faiss = True
        except ImportError:
            self._use_faiss = False  # numpy fallback in retrieve()

    # ── Public API ─────────────────────────────────────────────────────────────
    def retrieve(self, query: str, k: int = 3) -> list:
        """Return top-k semantically relevant knowledge base passages."""
        q_vec = self._encode_query(query)           # shape (1, dim)

        if self._use_faiss:
            _, indices = self._index.search(q_vec, k)
            return [KNOWLEDGE_BASE[i] for i in indices[0]
                    if 0 <= i < len(KNOWLEDGE_BASE)]

        # NumPy cosine fallback (vectors already normalised)
        scores = self._embeddings @ q_vec[0]
        top_k  = np.argsort(scores)[::-1][:k]
        return [KNOWLEDGE_BASE[i] for i in top_k]
