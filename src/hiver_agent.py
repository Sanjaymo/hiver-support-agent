"""Small, reproducible support-agent pipeline for one Twitter-support brand.

The implementation intentionally has no model downloads or API keys. It uses
character/word token overlap for retrieval, transparent intent rules, and a
conservative escalation policy. A real Kaggle export can be normalized to the
same columns as data/demo_conversations.csv.
"""
from __future__ import annotations

import csv
import math
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

TOKEN_RE = re.compile(r"[a-z0-9']+")

INTENT_KEYWORDS = {
    "billing": {"charged", "charge", "subscription", "payment", "bill", "duplicate"},
    "cancellation": {"cancel", "cancellation", "stop", "end", "unsubscribe"},
    "account_access": {"login", "log in", "password", "email", "verify", "verification", "locked"},
    "account_security": {"hacked", "hack", "stolen", "security", "another device", "unknown login", "logged in", "strange device"},
    "technical_issue": {"crash", "crashing", "bug", "error", "app", "not opening"},
    "playback": {"pause", "pausing", "buffer", "quality", "audio", "skip", "stutter", "playing quietly", "playing slowly", "not playing"},
    "product_question": {"how", "can i", "offline", "speaker", "feature", "available"},
    "plan_eligibility": {"student", "family", "discount", "plan", "eligible", "eligibility"},
    "content_issue": {"missing", "playlist", "episode", "song", "podcast", "disappeared", "liked music"},
    "payment_dispute": {"refund", "unrecognized", "unauthorized", "fraud", "do not recognize"},
}

UNCLASSIFIED_INTENT = "unclassified"

ESCALATE_TERMS = {
    "hacked", "hack", "stolen", "unauthorized", "unrecognized", "fraud", "refund",
    "charged twice", "legal", "safety", "minor", "delete my data", "identity",
}

@dataclass
class Example:
    conversation_id: str
    brand: str
    customer_text: str
    agent_text: str
    intent: str
    resolution: str

@dataclass
class Prediction:
    intent: str
    confidence: float
    draft_reply: str
    escalation: bool
    escalation_reason: str
    evidence: list[str]


def tokens(text: str) -> set[str]:
    return set(TOKEN_RE.findall(text.lower()))


def load_examples(path: str | Path, brand: str = "Spotify") -> list[Example]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = csv.reader(handle)
        next(rows, None)
        examples = []
        for row in rows:
            if len(row) < 6:
                continue
            if len(row) > 6:
                # Real exports often contain unquoted commas in free text.
                row = row[:3] + [", ".join(row[3:-2]), row[-2], row[-1]]
            example = Example(*row[:6])
            if example.brand.lower() == brand.lower():
                examples.append(example)
        return examples


def _keyword_score(text: str, intent: str) -> float:
    lowered = text.lower()
    hits = sum(1 for keyword in INTENT_KEYWORDS[intent] if keyword in lowered)
    phrase_hits = sum(
        1
        for keyword in INTENT_KEYWORDS[intent]
        if " " in keyword and len(keyword) > 5 and keyword in lowered
    )
    return min(1.0, hits / max(1, len(INTENT_KEYWORDS[intent])) + phrase_hits * 0.45)


def classify(text: str, examples: Iterable[Example]) -> tuple[str, float]:
    """Transparent classifier: keyword prior + nearest historical example."""
    examples = list(examples)
    word_set = tokens(text)
    scores: dict[str, float] = {}
    for intent in INTENT_KEYWORDS:
        scores[intent] = _keyword_score(text, intent) * 0.65
    if "plan" in text.lower() and any(
        term in text.lower()
        for term in (
            "student", "family", "discount", "duo", "annual", "premium",
            "cheapest", "trial", "available", "eligible", "upgrade", "switch", "new",
        )
    ):
        scores["plan_eligibility"] = max(scores["plan_eligibility"], 0.7)
    for example in examples:
        overlap = len(word_set & tokens(example.customer_text))
        similarity = overlap / max(1, len(word_set | tokens(example.customer_text)))
        scores[example.intent] = max(scores.get(example.intent, 0.0), similarity * 0.9)
    intent, score = max(scores.items(), key=lambda item: item[1])
    if score == 0:
        return UNCLASSIFIED_INTENT, 0.05
    ranked = sorted(scores.values(), reverse=True)
    margin = score - (ranked[1] if len(ranked) > 1 else 0.0)
    confidence = min(0.99, max(0.05, 0.5 + score * 0.45 + margin * 0.35))
    return intent, confidence


def retrieve(text: str, intent: str, examples: Iterable[Example], limit: int = 2) -> list[Example]:
    query = tokens(text)
    ranked = []
    for example in examples:
        if example.intent != intent:
            continue
        candidate = tokens(example.customer_text)
        similarity = len(query & candidate) / max(1, len(query | candidate))
        ranked.append((similarity, example))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [example for _, example in ranked[:limit]]


def should_escalate(text: str, intent: str, confidence: float) -> tuple[bool, str]:
    lowered = text.lower()
    matched = next((term for term in ESCALATE_TERMS if term in lowered), None)
    if matched:
        return True, f"sensitive or financial-risk term detected: {matched}"
    if confidence < 0.58:
        return True, "low classifier confidence; request needs human review"
    if intent in {"payment_dispute", "account_security"}:
        return True, f"{intent} requires private verification"
    return False, "routine request with sufficient confidence"


def draft_reply(text: str, intent: str, evidence: list[Example], escalation: bool) -> str:
    if escalation:
        escalation_replies = {
            "payment_dispute": "Thanks for reaching out. I’m routing your refund or payment concern to our billing team for a private review. Refund eligibility depends on how and where you paid, so please share the receipt only through the official support channel and do not post payment details here.",
            "billing": "Thanks for reaching out. I’m routing this billing concern to our support team so they can privately verify the charge and correct any duplicate payment. Please do not share card details publicly.",
            "account_security": "Thanks for letting us know. I’m routing this account-security issue to our support team for private ownership verification. Please do not share passwords, login codes, or personal account details publicly.",
        }
        return escalation_replies.get(
            intent,
            "Thanks for reaching out. I’m routing this request to our support team for a private review. Please do not share payment or login details publicly.",
        )
    if evidence:
        historical_reply = evidence[0].agent_text.strip()
        return f"Thanks for reaching out. Based on a similar {intent.replace('_', ' ')} case: {historical_reply} If that does not resolve it, reply with your device and app version so we can investigate further."
    return "Thanks for reaching out. We need a little more information to investigate this request."


def predict(text: str, examples: list[Example]) -> Prediction:
    intent, confidence = classify(text, examples)
    evidence = retrieve(text, intent, examples)
    escalate, reason = should_escalate(text, intent, confidence)
    return Prediction(intent, confidence, draft_reply(text, intent, evidence, escalate), escalate, reason, [e.agent_text for e in evidence])


def evaluate(gold: list[dict], examples: list[Example]) -> dict:
    labels = [row["intent"] for row in gold]
    majority = Counter(labels).most_common(1)[0][0]
    majority_correct = sum(label == majority for label in labels)
    predictions = [predict(row["customer_text"], examples) for row in gold]
    correct = sum(p.intent == row["intent"] for p, row in zip(predictions, gold))
    baseline_hits = sum(_keyword_score(row["customer_text"], row["intent"]) > 0 for row in gold)
    escalations = sum(p.escalation for p in predictions)
    return {
        "n": len(gold),
        "majority_accuracy": round(majority_correct / len(gold), 4),
        "keyword_coverage": round(baseline_hits / len(gold), 4),
        "agent_accuracy": round(correct / len(gold), 4),
        "agent_escalation_rate": round(escalations / len(gold), 4),
        "majority_label": majority,
    }


def load_gold(path: str | Path) -> list[dict]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def judge_reply(row: dict, prediction: Prediction) -> dict:
    """Offline proxy for the LLM judge; rubric is also used by the optional judge."""
    grounded = bool(prediction.evidence) and any(word in prediction.draft_reply.lower() for word in ("based on", "similar"))
    safe = prediction.escalation if row.get("risk", "0") == "1" else not prediction.escalation or "support team" in prediction.draft_reply
    helpful = prediction.intent == row["intent"] and len(prediction.draft_reply) >= 50
    return {"grounded": int(grounded), "safe": int(safe), "helpful": int(helpful), "score": int(grounded) + int(safe) + int(helpful)}


def judge_agreement(gold: list[dict], examples: list[Example]) -> dict:
    labels = []
    judged = []
    for row in gold:
        prediction = predict(row["customer_text"], examples)
        # Human labels encode whether a response is acceptable under the same rubric.
        human = int(row.get("human_reply_ok", "0"))
        automatic = int(sum(judge_reply(row, prediction).values()) >= 2)
        labels.append(human)
        judged.append(automatic)
    agreement = sum(a == b for a, b in zip(labels, judged)) / max(1, len(labels))
    return {"human_judge_agreement": round(agreement, 4), "n": len(labels)}
