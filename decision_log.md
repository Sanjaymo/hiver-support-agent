# Decision Log

- Chose Spotify so the domain has recurring, recognizable support resolutions.
- Limited the taxonomy to ten intents to keep labels operational rather than exhaustive.
- Kept the core implementation standard-library-only so a reviewer can reproduce it without credentials or model downloads.
- Used historical agent responses as retrieval evidence instead of inventing a knowledge base.
- Restricted retrieval to the predicted intent to reduce cross-intent answer contamination.
- Escalated security and payment language by policy even when the classifier is confident.
- Escalated low confidence instead of forcing a polished but unsupported answer.
- Returned an escalation reason as a first-class output for auditability.
- Included a deterministic bundled dataset because the full Kaggle download is too large for a fast take-home smoke run.
- Made the real-data schema explicit rather than pretending the demo is the Kaggle export.
- Used a balanced 150-row golden set so majority accuracy is a meaningful but intentionally weak baseline.
- Included a simple keyword baseline to show the benefit of combining rules with retrieval.
- Used an offline judge proxy so CI works without an LLM API key.
- Measured judge agreement with human rubric labels rather than reporting judge scores alone.
- Documented leakage and templating as limitations of the headline number.
