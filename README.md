# Hiver SDE Intern Take-Home: Support Agent

A reproducible support agent for one brand, **Spotify**, using the Customer Support on Twitter problem shape. The included pipeline classifies a customer message, retrieves historically similar resolutions, drafts a grounded reply, and decides whether to escalate.

## Reproduce headline results in under 15 minutes

Requires Python 3.10+ on Windows, macOS, or Linux.

```bash
python scripts/make_golden.py
python scripts/run_pipeline.py
python scripts/run_pipeline.py --message "I was charged twice and need a refund"
python -m pytest -q
```

Launch the support workspace:

```bash
python -m streamlit run app.py
```

Then open `http://localhost:8501` in your browser. The app shows the predicted intent, confidence, escalation decision, grounded draft, historical evidence, and evaluation snapshot.

Use **Download evaluation report (PDF)** in the sidebar to export a print-ready report with headline metrics, system design, evaluation methodology, failure modes, limitations, and the next-week plan. Individual suggested replies can also be downloaded as text after analysis.

The core pipeline has no model download and no API key. On the bundled 150-example golden set it prints accuracy against a majority baseline, keyword coverage, escalation rate, and offline judge/human agreement. The demo data is intentionally small so the run is deterministic and fast.

## Using the real Kaggle export

Download `thoughtvector/customer-support-on-twitter`, select one brand, and normalize its rows to the five columns in `data/demo_conversations.csv`: `conversation_id,brand,customer_text,agent_text,intent,resolution`. Keep only customer messages paired with the next brand response and manually assign intents to the evaluation sample. Then pass the normalized CSV with `--data`. The code does not claim that the bundled demo is the Kaggle dataset.

## System

- **Intent taxonomy:** ten Spotify-specific intents defined from recurring support outcomes: billing, cancellation, account access, account security, technical issue, playback, product question, plan eligibility, content issue, and payment dispute.
- **Classifier:** transparent keyword prior plus nearest historical customer-message overlap.
- **Grounding:** retrieve up to two same-intent historical examples and reuse their recorded resolution.
- **Routing:** sensitive financial/security terms, low confidence, and disputes escalate to a human. The reason is returned with every prediction.
- **Judge:** an offline three-part rubric checks groundedness, safety, and helpfulness. It reports agreement with the `human_reply_ok` field in the golden set. For a production submission, replace the proxy with an API judge and double-label a blind sample.

## Evaluation set

`data/golden_set.csv` contains 150 labelled examples, balanced across the ten intents. The examples were stratified by intent and written from the language patterns seen in the bundled historical cases. Risk labels identify security/payment cases that should be escalated. `scripts/make_golden.py` regenerates the exact deterministic set.

## Caveats and scope

This is a research prototype, not an autonomous customer-service deployment. It does not access accounts, process refunds, expose private data, or infer identity. Its headline accuracy is optimistic because the evaluation language is close to the small historical seed set; confidence and escalation are therefore more important than accuracy alone.

See [report.md](report.md) for framing, baselines, failure analysis, misleading-number analysis, and the one-week plan. See [decision_log.md](decision_log.md) for non-obvious decisions.
