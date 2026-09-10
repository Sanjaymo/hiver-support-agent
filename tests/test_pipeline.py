import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from hiver_agent import load_examples, predict

ROOT = Path(__file__).parents[1]


def test_security_message_escalates():
    examples = load_examples(ROOT / "data/demo_conversations.csv")
    result = predict("My account was hacked and there is an unknown charge", examples)
    assert result.escalation is True
    assert result.intent in {"account_security", "payment_dispute"}


def test_routine_product_question_is_grounded():
    examples = load_examples(ROOT / "data/demo_conversations.csv")
    result = predict("Can I listen offline with Premium?", examples)
    assert result.intent == "product_question"
    assert result.evidence
    assert result.escalation is False


def test_refund_reply_matches_payment_dispute():
    examples = load_examples(ROOT / "data/demo_conversations.csv")
    result = predict("I want a refund for my subscription.", examples)
    assert result.intent == "payment_dispute"
    assert result.escalation is True
    assert "refund" in result.draft_reply.lower()
    assert "billing team" in result.draft_reply.lower()


def test_security_reply_matches_account_security():
    examples = load_examples(ROOT / "data/demo_conversations.csv")
    result = predict("My account was hacked and the email changed.", examples)
    assert result.intent == "account_security"
    assert result.escalation is True
    assert "account-security" in result.draft_reply.lower()
    assert "password" in result.draft_reply.lower()


def test_phrase_signal_prefers_technical_issue():
    examples = load_examples(ROOT / "data/demo_conversations.csv")
    result = predict("The app is not opening.", examples)
    assert result.intent == "technical_issue"
    assert result.escalation is False


def test_vague_message_is_unclassified_and_escalated():
    examples = load_examples(ROOT / "data/demo_conversations.csv")
    result = predict("Help", examples)
    assert result.intent == "unclassified"
    assert result.escalation is True
    assert "low classifier confidence" in result.escalation_reason


def test_explicit_plan_language_prefers_plan_eligibility():
    examples = load_examples(ROOT / "data/demo_conversations.csv")
    result = predict("How can I get the student plan?", examples)
    assert result.intent == "plan_eligibility"


def test_cheapest_plan_reply_is_not_account_access():
    examples = load_examples(ROOT / "data/demo_conversations.csv")
    result = predict("How can I get the cheapest plan?", examples)
    assert result.intent == "plan_eligibility"
    assert "email update" not in result.draft_reply.lower()
    assert "available plans" in result.draft_reply.lower()
