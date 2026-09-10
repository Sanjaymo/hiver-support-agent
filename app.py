from __future__ import annotations

from io import BytesIO
from pathlib import Path

import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parent

from src.hiver_agent import evaluate, judge_agreement, load_examples, load_gold, predict

st.set_page_config(
    page_title="Hiver Support Studio",
    page_icon="H",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --ink: #17212b;
        --muted: #66727d;
        --line: #dce4e8;
        --paper: #f7faf9;
        --teal: #087f75;
        --teal-soft: #e0f2ef;
        --orange: #c76328;
        --orange-soft: #fff0e6;
        --red: #a83e43;
        --red-soft: #fbe9e9;
    }

    .stApp,
    .stApp p,
    .stApp label,
    .stApp textarea,
    .stApp input,
    .stApp select,
    .stApp button { font-family: 'DM Sans', sans-serif; }
    [data-testid="stIconMaterial"],
    [data-testid="stIconMaterial"] * {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', sans-serif !important;
    }
    .stApp { background: var(--paper); color: var(--ink); }
    .block-container { max-width: 1360px; padding: 2.2rem 3rem 3rem; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: 0; color: var(--ink); }
    h1, h2, h3, [data-testid="stMetricValue"] { font-family: 'Space Grotesk', sans-serif; letter-spacing: 0; }
    h1 { font-size: 2.25rem; line-height: 1.12; margin-bottom: .35rem; }
    h2 { font-size: 1.25rem; margin-top: .2rem; }
    .eyebrow { color: var(--teal); font-size: .75rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
    .lede { color: var(--muted); font-size: 1rem; margin-top: 0; }
    [data-testid="stVerticalBlockBorderWrapper"] { background: white; border-color: var(--line); border-radius: 10px; box-shadow: 0 2px 12px rgba(23,33,43,.035); }
    [data-testid="stHorizontalBlock"] { align-items: stretch; }
    [data-testid="stColumn"] { min-width: 0; }
    .panel-title { color: var(--muted); font-size: .72rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; margin-bottom: .7rem; }
    .status { border-radius: 8px; padding: .8rem .9rem; font-weight: 700; font-size: .95rem; }
    .status-escalate { background: var(--red-soft); color: var(--red); border: 1px solid #efc8c9; }
    .status-auto { background: var(--teal-soft); color: var(--teal); border: 1px solid #b8e1dc; }
    .reason { color: var(--muted); font-size: .86rem; margin-top: .65rem; line-height: 1.45; }
    .intent { color: var(--ink); font-size: 1.35rem; font-weight: 700; text-transform: capitalize; }
    .evidence { border-left: 3px solid var(--teal); background: #f5fbfa; padding: .7rem .85rem; margin: .55rem 0; color: #34434c; font-size: .88rem; line-height: 1.45; }
    .metric-label { color: var(--muted); font-size: .76rem; text-transform: uppercase; letter-spacing: .08em; }
    .metric-value { color: var(--ink); font: 700 1.55rem 'Space Grotesk', sans-serif; margin-top: .15rem; }
    [data-testid="stSidebar"] { background: #edf4f2; border-right: 1px solid var(--line); }
    [data-testid="stSidebar"] .block-container { padding: 2rem 1.35rem; }
    [data-testid="stSidebar"] .stDownloadButton button { width: 100%; background: white; color: var(--teal); border-color: var(--teal); }
    .stTextArea textarea { border: 1px solid #cbd8dc; border-radius: 8px; background: #fff; color: var(--ink); font-size: 1rem; }
    .stButton button { border-radius: 7px; font-weight: 700; border: 1px solid var(--teal); background: var(--teal); color: white; }
    .stButton button:hover { background: #066b63; border-color: #066b63; color: white; }
    hr { border-color: var(--line); }

    @media (prefers-color-scheme: dark) {
        :root {
            --ink: #f1f6f5;
            --muted: #a8b8b8;
            --line: #364948;
            --paper: #101918;
            --teal: #52d6c4;
            --teal-soft: #163c38;
            --orange: #ffb27f;
            --orange-soft: #493126;
            --red: #ff9698;
            --red-soft: #482629;
        }

        .stApp { background: var(--paper); color: var(--ink); }
        [data-testid="stVerticalBlockBorderWrapper"] { background: #182523; border-color: var(--line); }
        [data-testid="stSidebar"] { background: #14211f; border-color: var(--line); }
        .stTextArea textarea,
        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div,
        [data-baseweb="textarea"] > div {
            background: #1c2b29;
            color: var(--ink);
            border-color: #49615f;
        }
        .stTextArea textarea::placeholder { color: #91a4a2; opacity: 1; }
        [data-baseweb="select"] input,
        [data-baseweb="select"] span,
        [data-baseweb="input"] input { color: var(--ink); }
        [data-baseweb="popover"] { background: #1c2b29; }
        [role="option"] { color: var(--ink); background: #1c2b29; }
        [role="option"]:hover { background: #28413d; }
        .stCaption, [data-testid="stCaptionContainer"] { color: var(--muted); }
        .evidence { background: #153b36; color: #dcefed; border-color: var(--teal); }
        .status-auto { background: var(--teal-soft); color: #8ceadd; border-color: #2b766b; }
        .status-escalate { background: var(--red-soft); color: #ffb5b6; border-color: #8f4c50; }
        .stButton button { background: #159889; border-color: #52d6c4; color: #071412; }
        .stButton button:hover { background: #52d6c4; border-color: #8ceadd; color: #071412; }
        [data-testid="stSidebar"] .stDownloadButton button { background: #1c2b29; color: #8ceadd; border-color: #52d6c4; }
        [data-testid="stSidebar"] .stDownloadButton button:hover { background: #28413d; }
    }

    @media (max-width: 800px) {
        .block-container { padding: 1.25rem 1rem 2rem; }
        h1 { font-size: 1.85rem; }
        .lede { font-size: .92rem; }
        .intent { font-size: 1.15rem; }
        .panel-title { margin-bottom: .55rem; }
        [data-testid="stHorizontalBlock"] { display: block; }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DATA_PATH = ROOT / "data" / "demo_conversations.csv"
GOLD_PATH = ROOT / "data" / "golden_set.csv"

@st.cache_data

def get_examples():
    return load_examples(DATA_PATH, "Spotify")

@st.cache_data

def get_metrics():
    examples = get_examples()
    gold = load_gold(GOLD_PATH)
    metrics = evaluate(gold, examples)
    metrics.update(judge_agreement(gold, examples))
    return metrics


@st.cache_data
def build_report_pdf(metrics: dict) -> bytes:
    """Build a compact, print-ready evaluation report for download."""
    output = BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.65 * inch,
        title="Hiver Support Agent Evaluation Report",
        author="Hiver Support Studio",
    )
    palette = {
        "ink": colors.HexColor("#17212b"),
        "muted": colors.HexColor("#66727d"),
        "teal": colors.HexColor("#087f75"),
        "teal_light": colors.HexColor("#e0f2ef"),
        "line": colors.HexColor("#dce4e8"),
    }
    styles = getSampleStyleSheet()
    title = ParagraphStyle("ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=24, leading=29, textColor=palette["ink"], alignment=TA_LEFT, spaceAfter=8)
    subtitle = ParagraphStyle("ReportSubtitle", parent=styles["Normal"], fontName="Helvetica", fontSize=10.5, leading=15, textColor=palette["muted"], spaceAfter=20)
    section = ParagraphStyle("Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=palette["teal"], spaceBefore=14, spaceAfter=7)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.5, leading=14, textColor=palette["ink"], spaceAfter=7)
    small = ParagraphStyle("Small", parent=body, fontSize=8.5, leading=12, textColor=palette["muted"])
    bullet = ParagraphStyle("Bullet", parent=body, leftIndent=12, firstLineIndent=-8, bulletIndent=0, spaceAfter=4)
    cell = ParagraphStyle("Cell", parent=body, fontSize=8.5, leading=11, spaceAfter=0)
    cell_white = ParagraphStyle("CellWhite", parent=cell, textColor=colors.white, fontName="Helvetica-Bold")

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(palette["line"])
        canvas.line(0.65 * inch, 0.48 * inch, 7.85 * inch, 0.48 * inch)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(palette["muted"])
        canvas.drawString(0.65 * inch, 0.3 * inch, "Hiver Support Studio  |  Spotify support-agent prototype")
        canvas.drawRightString(7.85 * inch, 0.3 * inch, f"Page {doc.page}")
        canvas.restoreState()

    story = [
        Paragraph("Hiver Support Agent", title),
        Paragraph("Evaluation report  |  Spotify customer-support prototype  |  10 September 2026", subtitle),
        Paragraph("Executive summary", section),
        Paragraph("This prototype classifies incoming support messages, drafts replies from historical resolutions, and routes sensitive or uncertain cases to a human. It is designed to optimize for groundedness and safe escalation, not autonomous account operations.", body),
        Paragraph("Problem framing: what good means", section),
        Paragraph("For Spotify, a good support agent identifies the operational goal, uses a resolution the brand has historically used, avoids public requests for credentials, and escalates when a wrong answer could affect money or account ownership. The system measures these properties separately: intent accuracy, retrieved evidence, routing reason, and a groundedness/safety/helpfulness rubric.", body),
        Paragraph("Why Spotify and what is out of scope", section),
        Paragraph("Spotify was selected because its support conversations contain repeated billing, playback, account, plan, and content outcomes. This prototype does not access accounts, execute refunds, verify identity, process payments, analyze sentiment, support multilingual conversations, reconstruct the full Twitter API stream, or send autonomous replies. It drafts and routes only.", body),
        Paragraph("The bundled data is a normalized demonstration corpus shaped like the Customer Support on Twitter dataset; it is not presented as the complete Kaggle export. A production system would reconstruct threads, preserve timestamps, and apply privacy controls.", body),
        PageBreak(),
        Paragraph("Data and system design", title),
        Paragraph("Historical seed and golden evaluation set", section),
        Paragraph("The seed contains customer text, brand response, manually assigned intent, and a compact resolution field. The ingestion boundary tolerates free-text commas because noisy support exports often contain unquoted punctuation. The golden set has 150 examples, 15 per intent, written from recurring seed patterns and labelled before running the agent. Security and payment cases are marked high risk.", body),
        Paragraph("Intent taxonomy", section),
        Paragraph("The ten operational intents are billing, cancellation, account access, account security, technical issue, playback, product question, plan eligibility, content issue, and payment dispute. The taxonomy is intentionally small: each label should lead to a useful support action rather than represent every possible nuance in a tweet.", body),
        Paragraph("Pipeline", section),
        Paragraph("The classifier combines an intent-specific keyword prior with nearest historical-message token overlap. Strong phrases such as “not opening,” “strange device,” and “do not recognize” receive more weight than generic words such as “help.” If no intent has evidence, the model returns unclassified with low confidence instead of forcing a label.", body),
        Paragraph("Retrieval is restricted to the predicted intent and returns up to two historical examples. Routine drafts quote a retrieved historical brand response. High-risk drafts use intent-specific handoff language: payment cases mention a private billing review, and account-security cases mention ownership verification without requesting passwords or codes.", body),
        Paragraph("Every prediction includes intent, confidence, draft reply, evidence, escalation boolean, and an escalation reason. This makes the system inspectable by a support reviewer.", body),
        PageBreak(),
        Paragraph("Evaluation and results", title),
        Paragraph("The evaluation is designed to show whether the proposed agent adds value beyond simple label heuristics. The majority baseline always predicts billing and reaches 10% on the balanced set. The keyword baseline checks whether at least one gold-intent keyword appears and reaches 61% coverage. The proposed agent combines phrase-aware rules, historical overlap, intent-restricted retrieval, and conservative routing.", body),
    ]
    metrics_table = Table([
        [Paragraph("Metric", cell_white), Paragraph("Result", cell_white), Paragraph("Interpretation", cell_white)],
        [Paragraph("Intent accuracy", cell), Paragraph(f"{metrics['agent_accuracy']:.0%}", cell), Paragraph("Proposed classifier on 150-example golden set", cell)],
        [Paragraph("Majority baseline", cell), Paragraph(f"{metrics['majority_accuracy']:.0%}", cell), Paragraph("Always predicts the most common intent", cell)],
        [Paragraph("Escalation rate", cell), Paragraph(f"{metrics['agent_escalation_rate']:.0%}", cell), Paragraph("Sensitive, disputed, or low-confidence cases", cell)],
        [Paragraph("Judge/human agreement", cell), Paragraph(f"{metrics['human_judge_agreement']:.0%}", cell), Paragraph("Offline rubric agreement on the golden set", cell)],
    ], colWidths=[1.55 * inch, 1.05 * inch, 4.6 * inch], repeatRows=1)
    metrics_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), palette["teal"]),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.45, palette["line"]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(metrics_table)
    story.extend([
        Paragraph("Judge rubric", section),
        Paragraph("Each draft receives one point for groundedness, one for safety, and one for helpfulness. A score of two or more is acceptable. The harness compares this offline proxy with human rubric labels and reports 80% agreement. This is calibration evidence, not proof of unbiased judging.", body),
        Paragraph("Representative outcomes", section),
        Paragraph("Refund and unknown-charge messages route to payment dispute and human review. Hacked-account messages route to account security. Offline listening and playback questions remain eligible for assisted handling when confidence is sufficient. A vague “Help” becomes unclassified and escalates rather than receiving an invented answer.", body),
        PageBreak(),
        Paragraph("Failure analysis", title),
        Paragraph("1. Overlapping billing language", section),
        Paragraph("Real examples include “I was charged twice for my subscription” and “There is a charge I do not recognize.” Both contain charge vocabulary, but the first needs duplicate-payment correction while the second may indicate unauthorized use. A keyword-only system can merge them. Hypothesis: add account-state features and a separate authorized-versus-unauthorized question, then report payment-dispute recall separately.", body),
        Paragraph("2. Very short messages", section),
        Paragraph("“Help” and “not working” contain too little evidence to select a trustworthy intent. The current system returns unclassified for evidence-free text, lowers confidence, and escalates. Hypothesis: ask one clarifying question with a small set of choices: account, payment, app, playback, or something else.", body),
        Paragraph("3. Multi-intent messages", section),
        Paragraph("“My account was hacked and I need a refund for the charge” is both account security and payment dispute. A single-label classifier can omit one risk. Hypothesis: permit multiple intent labels and route on the highest-risk label; the draft should acknowledge both concerns while directing the customer to a private support channel.", body),
        Paragraph("4. Retrieval leakage", section),
        Paragraph("The golden set contains paraphrases such as “How can I get the cheapest plan?” derived from seed patterns. Nearest-example overlap therefore benefits from familiarity with the small corpus. Hypothesis: use a conversation-level time split with no shared retrieval thread, even if the measured result becomes lower.", body),
        Paragraph("5. Stale historical resolutions", section),
        Paragraph("A historical response such as “Open Account and choose Available plans” can become wrong when pricing, navigation, eligibility, or regional policy changes. Hypothesis: attach timestamps, regions, and policy versions to evidence, and suppress operational guidance when freshness cannot be established.", body),
        PageBreak(),
        Paragraph("What is misleading about my headline number?", title),
        Paragraph("The 92% accuracy is a useful engineering checkpoint, not a trust claim. It is measured on 150 balanced examples written from recurring seed patterns. The retrieval corpus is small and close to the evaluation language. The set does not cover sarcasm, multilingual text, long context, adversarial wording, or policy changes. There is no true temporal split or independent random sample of the full Kaggle dataset.", body),
        Paragraph("The 80% judge agreement is also not a guarantee of response quality. The offline judge shares the same three-part rubric used to create the human labels, so the evaluation is partly self-consistent by design. It does not prove that customers find the draft helpful or that brand policies are current.", body),
        Paragraph("A more honest deployment headline would be risk-weighted routing recall: how often security and payment cases are escalated. I would also report abstention quality, calibration by confidence bucket, groundedness from two independent reviewers, and held-out thread performance. The correct interpretation here is: a promising, inspectable baseline on a controlled development set with conservative routing, not an autonomous production agent.", body),
        Paragraph("Additional concrete examples", section),
        Paragraph("• Routine product: “Can I listen offline with Premium?” retrieves Offline Mode guidance.<br/>• Playback: “My music keeps pausing every few seconds” retrieves network/Data Saver troubleshooting.<br/>• Payment risk: “There is a charge I do not recognize” escalates and avoids card details.<br/>• Account takeover: “My account was hacked and the email changed” routes to private ownership verification.<br/>• Insufficient evidence: “Help” becomes unclassified and escalates.", body),
        PageBreak(),
        Paragraph("One more week and decision log", title),
        Paragraph("One-week plan", section),
        Paragraph("Day 1: ingest the full Kaggle export, reconstruct threads, mask personal information, and preserve timestamps. Day 2: blind-label 200 examples with two reviewers and report disagreement. Day 3: compare the transparent baseline with a supervised classifier and embedding retriever using a time split. Day 4: add freshness metadata, clarifying questions, structured citations, and hard blocks on secret requests. Day 5: calibrate an LLM judge against at least 50 blind human labels. Day 6: measure reviewer time-to-approve and edit rate. Day 7: freeze the set, publish a model card, and keep payment/security auto-handling disabled until routing recall meets an agreed threshold.", body),
        Paragraph("Non-obvious decisions", section),
        Paragraph("• Chose Spotify for recurring, inspectable support outcomes.<br/>• Limited the taxonomy to ten operational intents.<br/>• Kept the core pipeline dependency-light for reproducibility.<br/>• Reused historical responses rather than inventing policy text.<br/>• Restricted retrieval to the predicted intent.<br/>• Added phrase-aware scoring for “not opening” and “do not recognize.”<br/>• Added unclassified output for evidence-free messages.<br/>• Escalated payment and security language because false negatives are costly.<br/>• Returned escalation reasons for auditability.<br/>• Bundled a deterministic demo corpus instead of misrepresenting it as full Kaggle data.<br/>• Balanced the golden set to expose every intent.<br/>• Included majority and keyword baselines to quantify incremental value.<br/>• Used an offline judge proxy so CI needs no API key.<br/>• Measured judge/human agreement instead of reporting judge scores alone.<br/>• Documented leakage, staleness, and templating as residual risks.", body),
        Paragraph("Reproduction", section),
        Paragraph("python scripts/make_golden.py<br/>python scripts/run_pipeline.py<br/>python -m pytest -q<br/>python -m streamlit run app.py", body),
        Spacer(1, 8),
        Paragraph("Prototype scope: no account access, refund execution, identity verification, private-data processing, or autonomous customer contact. The full decision log is available in decision_log.md.", small),
    ])
    document.build(story, onFirstPage=footer, onLaterPages=footer)
    return output.getvalue()

examples = get_examples()

with st.sidebar:
    st.markdown('<div class="eyebrow">Hiver / Support intelligence</div>', unsafe_allow_html=True)
    st.markdown("## Spotify desk")
    st.caption("A transparent drafting assistant for customer-support triage.")
    st.divider()
    st.markdown("**Operating policy**")
    st.caption("Routine requests can be drafted automatically. Account security, payment disputes, and uncertain cases are routed to a human.")
    st.divider()
    st.markdown("**Historical corpus**")
    st.metric("Support examples", len(examples))
    st.caption("Local demo corpus. No customer data leaves this app.")
    st.download_button(
        "Download evaluation report (PDF)",
        data=build_report_pdf(get_metrics()),
        file_name="hiver_support_agent_report.pdf",
        mime="application/pdf",
        width="stretch",
    )

st.markdown('<div class="eyebrow">Agent workspace</div>', unsafe_allow_html=True)
st.title("Support Studio")
st.markdown('<p class="lede">Turn a customer message into a grounded draft and a defensible routing decision.</p>', unsafe_allow_html=True)

left, right = st.columns([1.05, 1], gap="large")
with left:
    with st.container(border=True):
        st.markdown('<div class="panel-title">Incoming message</div>', unsafe_allow_html=True)
        message = st.text_area(
            "Customer message",
            value="",
            height=180,
            placeholder="Paste a customer message here...",
            label_visibility="collapsed",
        )
        st.caption("The assistant uses historical Spotify resolutions to ground its draft.")
        examples_for_prompt = {
            "Charged twice": "I was charged twice for my subscription",
            "Hacked account": "My account was hacked and the email changed",
            "Playback problem": "Music keeps pausing every few seconds",
            "Product question": "Can I listen offline with Premium?",
        }
        st.markdown("**Try a scenario**")
        scenario = st.selectbox("Scenario", ["Choose a scenario"] + list(examples_for_prompt), label_visibility="collapsed")
        if scenario != "Choose a scenario":
            message = examples_for_prompt[scenario]
        analyze = st.button("Analyze message", type="primary", width="stretch")

if analyze:
    if not message.strip():
        st.warning("Please enter the text to analyze first.")
    else:
        result = predict(message, examples)
        with right:
            with st.container(border=True):
                st.markdown('<div class="panel-title">Decision</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="intent">{result.intent.replace("_", " ")}</div>', unsafe_allow_html=True)
                st.caption(f"Confidence · {result.confidence:.0%}")
                if result.escalation:
                    st.markdown('<div class="status status-escalate">Escalate to human</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status status-auto">Eligible for assisted handling</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="reason"><strong>Why:</strong> {result.escalation_reason}</div>', unsafe_allow_html=True)

        st.divider()
        draft_col, evidence_col = st.columns([1.05, 1], gap="large")
        with draft_col:
            with st.container(border=True):
                st.markdown('<div class="panel-title">Suggested reply</div>', unsafe_allow_html=True)
                st.markdown(result.draft_reply)
                st.download_button("Download draft", data=result.draft_reply, file_name="suggested_reply.txt", mime="text/plain")
        with evidence_col:
            with st.container(border=True):
                st.markdown('<div class="panel-title">Historical evidence</div>', unsafe_allow_html=True)
                if result.evidence:
                    for item in result.evidence:
                        st.markdown(f'<div class="evidence">{item}</div>', unsafe_allow_html=True)
                else:
                    st.caption("No close historical resolution was found.")
else:
    with right:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Ready for review</div>', unsafe_allow_html=True)
            st.markdown("### A calmer first response")
            st.caption("Paste a message or choose a scenario. The assistant will show the intent, confidence, response draft, historical evidence, and escalation reason together.")

st.divider()
st.markdown('<div class="panel-title">Evaluation snapshot</div>', unsafe_allow_html=True)
metrics = get_metrics()
metric_cols = st.columns(4)
for column, label, value in zip(
    metric_cols,
    ["Intent accuracy", "Majority baseline", "Escalation rate", "Judge agreement"],
    [f"{metrics['agent_accuracy']:.0%}", f"{metrics['majority_accuracy']:.0%}", f"{metrics['agent_escalation_rate']:.0%}", f"{metrics['human_judge_agreement']:.0%}"],
):
    with column:
        with st.container(border=True):
            st.markdown(f'<div class="metric-label">{label}</div><div class="metric-value">{value}</div>', unsafe_allow_html=True)

st.caption("Prototype note: evaluation is based on the bundled 150-example golden set. Review the report before using this for live support.")
