import streamlit as st
from dotenv import load_dotenv
import os
from datetime import datetime
from agents.orchestrator import EmailOrchestrator

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN") or st.secrets.get("HF_TOKEN", None)

if HF_TOKEN:
    os.environ["HF_TOKEN"] = HF_TOKEN
    
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY not found in .env file")
    st.stop()

st.set_page_config(
    page_title="Agentic AI for Email Automation",
    page_icon="📧",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #0f1117;
    color: #ffffff;
}

.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

.card {
    background: #171f2f;
    border: 1px solid #2b3448;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 16px;
}

.metric {
    text-align: center;
    padding: 16px;
    border-radius: 12px;
    background: #171f2f;
    border: 1px solid #2b3448;
}

.metric-title {
    color: #9ca3af;
    font-size: 13px;
}

.metric-value {
    font-size: 20px;
    font-weight: 700;
}

.priority-critical { color: #ef4444; }
.priority-high { color: #f97316; }
.priority-medium { color: #eab308; }
.priority-low { color: #22c55e; }

.response-box {
    background: #111827;
    border-left: 4px solid #3b82f6;
    padding: 18px;
    border-radius: 10px;
    white-space: pre-wrap;
    line-height: 1.6;
}

.stButton > button {
    border-radius: 10px;
    height: 44px;
    font-weight: 600;
}

div[data-testid="stFileUploader"] {
    background: #171f2f;
    border: 1px dashed #3b82f6;
    border-radius: 14px;
    padding: 14px;
}
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def get_orchestrator():
    return EmailOrchestrator(GROQ_API_KEY)


if "results" not in st.session_state:
    st.session_state.results = []

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False


tab1, tab2 = st.tabs(["📧 Email Processing", "🧠 Orchestration"])


with tab1:
    st.title("📧 Agentic Email Response System")
    st.caption("Classify → Draft → Review → Schedule → Approve")

    st.markdown("### Upload Emails")

    uploaded_files = st.file_uploader(
        "Choose .txt or .eml files",
        type=["txt", "eml"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) uploaded successfully.")

        with st.expander("Preview uploaded emails", expanded=False):
            for file in uploaded_files:
                content = file.getvalue().decode("utf-8", errors="ignore")
                st.markdown(f"#### {file.name}")
                st.write(content[:1000])
                st.markdown("---")

        process_clicked = st.button(
            "🚀 Process Emails",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.is_processing
        )

        if process_clicked:
            st.session_state.is_processing = True

            email_batch = []

            for uploaded in uploaded_files:
                content = uploaded.getvalue().decode("utf-8", errors="ignore")

                email_batch.append({
                    "name": "Customer",
                    "subject": uploaded.name,
                    "body": content,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })

            with st.spinner("Running agent pipeline..."):
                orchestrator = get_orchestrator()
                results = orchestrator.process_batch(email_batch)

            st.session_state.results = results
            st.session_state.is_processing = False
            st.success("Emails processed successfully.")

    if st.session_state.results:
        st.markdown("## Agent Outputs")

        for i, r in enumerate(st.session_state.results):
            priority = r.get("priority", "low")
            sentiment = r.get("sentiment", "neutral")
            category = r.get("category", "general")
            confidence = r.get("confidence", 0)
            urgency = r.get("urgency_score", 0)

            with st.expander(
                f"📩 {i + 1}. {r.get('subject', 'No Subject')} — {priority.upper()}",
                expanded=(i == 0)
            ):
                c1, c2, c3, c4, c5 = st.columns(5)

                c1.markdown(f"""
                <div class="metric">
                    <div class="metric-title">Priority</div>
                    <div class="metric-value priority-{priority}">{priority.upper()}</div>
                </div>
                """, unsafe_allow_html=True)

                c2.markdown(f"""
                <div class="metric">
                    <div class="metric-title">Sentiment</div>
                    <div class="metric-value">{sentiment.title()}</div>
                </div>
                """, unsafe_allow_html=True)

                c3.markdown(f"""
                <div class="metric">
                    <div class="metric-title">Category</div>
                    <div class="metric-value">{category.replace("_", " ").title()}</div>
                </div>
                """, unsafe_allow_html=True)

                c4.markdown(f"""
                <div class="metric">
                    <div class="metric-title">Urgency</div>
                    <div class="metric-value">{urgency}%</div>
                </div>
                """, unsafe_allow_html=True)

                c5.markdown(f"""
                <div class="metric">
                    <div class="metric-title">Confidence</div>
                    <div class="metric-value">{confidence:.0%}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("### Original Email")

                st.markdown(f"""
                <div class="card">
                    <b>Subject:</b> {r.get("subject", "")}<br>
                    <b>Received:</b> {r.get("timestamp", "")}
                    <br><br>
                    {r.get("body", "")}
                
                """, unsafe_allow_html=True)

                st.markdown("### Drafted Response")

                edited_response = st.text_area(
                    "Edit response before approval",
                    value=r.get("response_draft", ""),
                    height=240,
                    key=f"edited_response_{i}"
                )

                st.markdown("### Review Agent")

                st.markdown(f"""
                <div class="card">
                    <b>Review Notes:</b> {r.get("review_notes", "None")}<br>
                    <b>Tone Used:</b> {r.get("tone_used", "Professional")}<br>
                    <b>Tone Appropriate:</b> {"Yes ✅" if r.get("tone_appropriate", True) else "No ⚠️"}<br>
                    <b>Addresses All Issues:</b> {"Yes ✅" if r.get("addresses_all_issues", True) else "No ⚠️"}<br>
                    <b>Escalation Required:</b> {"Yes ⚠️" if r.get("escalation_required") else "No ✅"}
                </div>
                """, unsafe_allow_html=True)

                st.markdown("### Scheduler Agent")

                st.markdown(f"""
                <div class="card">
                    <b>Scheduled Time:</b> {r.get("scheduled_time", "N/A")}<br>
                    <b>Delay Window:</b> {r.get("delay_minutes", 0)} minutes<br>
                    <i>No emails are sent. This only simulates scheduling.</i>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("### Approval")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        "✅ Approve Response",
                        key=f"approve_{i}",
                        type="primary",
                        use_container_width=True
                    ):
                        st.session_state.results[i]["response_draft"] = edited_response
                        st.session_state.results[i]["approved"] = True
                        st.session_state.results[i]["human_review"] = False
                        st.success("Response approved.")

                with col2:
                    if st.button(
                        "👤 Send for Human Review",
                        key=f"human_{i}",
                        use_container_width=True
                    ):
                        st.session_state.results[i]["approved"] = False
                        st.session_state.results[i]["human_review"] = True
                        st.warning("Marked for human review.")

                status = "Pending ⏳"

                if st.session_state.results[i].get("approved"):
                    status = "Approved ✅"
                elif st.session_state.results[i].get("human_review"):
                    status = "Human Review 👤"

                st.markdown(f"""
                <div class="card">
                    <b>Status:</b> {status}<br>
                    <i>No emails are sent from this app.</i>
                </div>
                """, unsafe_allow_html=True)

                if st.session_state.results[i].get("approved"):
                    st.markdown("### Final Approved Response")
                    st.markdown(f"""
                    <div class="response-box">
                    {st.session_state.results[i].get("response_draft")}
                    </div>
                    """, unsafe_allow_html=True)

    if st.session_state.results:
        if st.button("🗑️ Clear All Results", use_container_width=True):
            st.session_state.results = []
            st.rerun()


with tab2:
    st.subheader("🧠 Agent Orchestration Strategy")

    st.markdown("""
### Agent Flow

1. **Email Ingestion Agent**  
Reads `.eml` or `.txt` email files and converts them into structured email objects.

2. **Email Classifier Agent**  
Analyzes customer sentiment, category, urgency, and priority.

3. **RAG Agent**  
Retrieves relevant internal knowledge base passages for better contextual grounding.

4. **Drafting Agent**  
Generates a personalized response using customer context, classification metadata, and RAG context.

5. **Review Agent**  
Checks response quality, tone, confidence score, and whether escalation is required.

6. **Scheduler Agent**  
Assigns a dispatch time based on priority. No actual email is sent.

7. **Human Approval Layer**  
Allows the user to approve the response or mark it for manual review.

---

### Prioritization Logic

- **Critical** → legal/safety issue, account locked, data breach, highly urgent issue  
- **High** → angry/frustrated tone, billing dispute, service down  
- **Medium** → general complaint, delayed shipping, product question  
- **Low** → positive feedback, general inquiry, compliment  

---

### Scheduling Logic

- **Critical** → 15 minutes  
- **High** → 30 minutes  
- **Medium** → 60 minutes  
- **Low** → 4 hours  
""")