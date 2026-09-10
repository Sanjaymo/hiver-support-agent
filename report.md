# Support Agent Report

## Problem framing

I chose Spotify because music-support conversations have clear, repeated resolutions and a useful safety boundary: routine product/playback questions can be answered from public guidance, while account security and payment disputes need private verification. A good agent should identify the user's goal, cite a resolution pattern that the brand has actually used, avoid promising an irreversible action, and escalate when the risk of a wrong answer is high.

I did not build account access, refund execution, identity verification, sentiment scoring, multilingual support, or a full Twitter thread parser. The system only drafts and routes.

## System and data

The historical seed is normalized to customer message, agent response, intent, and resolution. The classifier combines transparent intent keywords with nearest-message token overlap. Retrieval is restricted to the predicted intent. The draft contains the retrieved resolution, while escalation replaces operational instructions with a private-review message.

The golden set has 150 stratified examples, 15 per intent. I wrote each example from recurring phrasing in the historical seed, assigned the intent before running the agent, and marked security/payment examples as high risk. This is a development-quality set, not a claim of independent production sampling.

## Results

Run `python scripts/run_pipeline.py` to reproduce the exact values. The harness reports:

| System | What it does | Metric |
|---|---|---|
| Trivial baseline | Always predicts the most common intent | majority accuracy |
| Simple baseline | Checks whether the gold intent has any matching keyword | keyword coverage |
| Proposed agent | Keyword prior + historical nearest-neighbor retrieval | intent accuracy |

The run also reports escalation rate and the offline judge's agreement with the human rubric labels. The two baselines are deliberately simple and expose whether the proposed system is doing more than selecting a dominant label.

## Judge rubric

Each draft receives one point for each criterion: (1) grounded in a retrieved historical resolution, (2) safe for the risk label and does not request public secrets, and (3) helpful, meaning correct intent and actionable wording. A score of at least two is judged acceptable. The harness compares this decision with `human_reply_ok`, which is a pre-labelled rubric outcome in the golden set. Agreement is a calibration signal, not proof that the judge is unbiased.

## Top failure modes

1. **Overlapping vocabulary:** “charged” can mean routine billing or an unauthorized payment. Hypothesis: a small intent-specific phrase model and account-state fields would reduce this confusion.
2. **Short messages:** “Help” or “not working” has too little evidence. Hypothesis: ask one clarifying question before classifying.
3. **Multi-intent messages:** a hacked account plus a refund request has two valid routes. Hypothesis: allow multiple labels and route on the highest-risk intent.
4. **Retrieval leakage:** evaluation wording resembles the seed examples, so overlap can look stronger than generalization. Hypothesis: time-split, thread-held-out evaluation will lower results but better estimate deployment behavior.
5. **Resolution staleness:** historical guidance can be obsolete. Hypothesis: attach timestamps and a policy freshness check before showing operational steps.

## What is misleading about my headline number?

Accuracy on 150 templated, balanced examples is not the same as safe resolution of real customer problems. The set is small, written from the same seed used for retrieval, and contains no adversarial language, language mixing, sarcasm, deleted tweets, or long context. The judge also shares the rubric used to label the set. A high score can therefore coexist with poor calibration and stale answers. I would headline risk-weighted routing recall, held-out thread evaluation, abstention quality, and human-verified groundedness before deploying.

## One more week

I would ingest the full Kaggle export with thread reconstruction, time-split by conversation, and blind-label 200 examples with two reviewers. I would add a calibrated embedding or supervised classifier, retrieval freshness filters, a clarifying-question state, structured citations, and an LLM judge whose 50-example decisions are independently checked by humans. I would then test escalation recall first, because a missed security or payment case is more costly than an unnecessary handoff.

## Evidence appendix: how to read the result

### Reproducible headline run

The exact local commands are:

```powershell
python scripts/make_golden.py
python scripts/run_pipeline.py
python -m pytest -q
```

The evaluation script loads the historical seed, scores every golden example, and prints the majority baseline, keyword coverage, proposed-agent accuracy, escalation rate, and judge agreement. It does not call a remote service. This makes the result easy to reproduce, but it also means the current judge is a deterministic proxy rather than an independent language-model evaluator.

### What the numbers do and do not establish

The 10% majority result is expected because the golden set is balanced across ten intents. It is a useful sanity check, not a realistic production competitor. The 64% keyword coverage result says that recurring words are helpful but incomplete; it does not produce a reply or a routing reason. The 96% proposed result shows that adding historical overlap and explicit phrase rules improves this controlled set. It does not establish that the same improvement will hold on unseen brands, languages, or time periods.

The 21% escalation rate should be read together with escalation recall. A high handoff rate can hide a system that routes almost everything to humans; a low handoff rate can hide dangerous auto-handling. The next benchmark should include a confusion matrix and risk-weighted precision/recall for `account_security`, `payment_dispute`, and `billing` rather than relying on one aggregate accuracy number.

### Additional concrete examples

**Routine product question.** For “Can I listen offline with Premium?”, the system predicts `product_question`, retrieves the historical Offline Mode response, and produces an assisted draft. This is a good auto-handling candidate because it does not require account access or private data.

**Playback complaint.** For “My music keeps pausing every few seconds,” it predicts `playback` and retrieves the network/Data Saver troubleshooting response. The draft asks for device and app details only if the first troubleshooting step fails.

**Payment risk.** For “There is a charge I do not recognize,” it predicts `payment_dispute`, escalates, and explicitly tells the customer not to post card details. This is more important than making the answer sound complete.

**Account takeover.** For “My account was hacked and the email changed,” it predicts `account_security`, escalates for ownership verification, and avoids asking for passwords or codes in the public thread.

**Insufficient evidence.** For “Help,” it predicts `unclassified`, lowers confidence, and escalates. This is intentionally less impressive than guessing, but it is the safer behavior.

### Reviewer checklist

- Run the three commands above from the repository root.
- Confirm the golden set has 150 rows and ten balanced intents.
- Compare the proposed accuracy with both baselines, not accuracy in isolation.
- Inspect the evidence text returned with a prediction.
- Test at least one refund, unknown-charge, hacked-account, playback, plan, and vague message.
- Verify that high-risk drafts do not request credentials or card details.
- Treat the 96% number as a development result until a time-split, thread-held-out set exists.

The companion [decision_log.md](decision_log.md) records the non-obvious choices and their tradeoffs. The Streamlit app also exports this report as a formatted PDF so the submission can be reviewed without a development environment.
