from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
rows = []
templates = [
    ("billing", "I was charged {x} for Premium", "0", "1"),
    ("cancellation", "How do I cancel my {x} plan?", "0", "1"),
    ("account_access", "I cannot {x} into my account", "0", "1"),
    ("account_security", "Someone {x} my account", "1", "0"),
    ("technical_issue", "The app is {x} on my phone", "0", "1"),
    ("playback", "My music keeps {x}", "0", "1"),
    ("product_question", "Can Spotify {x}?", "0", "1"),
    ("plan_eligibility", "How can I get the {x} plan?", "0", "1"),
    ("content_issue", "My {x} is missing", "0", "1"),
    ("payment_dispute", "I need a {x} for this charge", "1", "0"),
]
values = {
    "billing": ["twice", "today", "after renewal", "a second time", "this month", "for last month", "after upgrading", "unexpectedly", "on my card", "for a subscription", "again", "when I cancelled", "but I was promised a trial", "for Premium", "and need help"],
    "cancellation": ["Premium", "subscription", "student", "family", "paid", "current", "monthly", "annual", "my", "the account", "today", "before renewal", "right now", "without losing playlists", "from my phone"],
    "account_access": ["log", "sign", "get", "access", "sign", "log", "open", "recover", "verify", "get", "sign", "log", "access", "enter", "use"],
    "account_security": ["changed my email", "logged in", "took over", "was hacked", "has an unknown login", "changed my password", "is compromised", "was accessed", "has another user", "was stolen", "is not mine", "has a strange device", "was hacked today", "has fraud", "looks unsafe"],
    "technical_issue": ["crashing", "not opening", "showing an error", "freezing", "closing", "stuck", "broken", "slow", "not loading", "failing", "blank", "unresponsive", "glitchy", "down", "stopping"],
    "playback": ["pausing", "buffering", "skipping", "stuttering", "stopping", "playing quietly", "sounding bad", "cutting out", "playing slowly", "losing audio", "distorting", "not playing", "dropping", "starting over", "going silent"],
    "product_question": ["work offline", "play on a speaker", "download music", "use on a TV", "share a playlist", "work abroad", "support podcasts", "play without data", "connect to a car", "offer lyrics", "work on my watch", "include audiobooks", "support multiple devices", "have a free tier", "play with Bluetooth"],
    "plan_eligibility": ["student", "family", "discount", "duo", "annual", "Premium", "new", "cheapest", "student discount", "family", "trial", "available", "eligible", "upgrade", "switch"],
    "content_issue": ["playlist", "podcast episode", "saved song", "album", "download", "liked music", "episode", "playlist", "song", "podcast", "library item", "artist", "track", "show", "music"],
    "payment_dispute": ["refund", "charge", "payment", "subscription charge", "duplicate charge", "unknown payment", "money", "billing", "card charge", "purchase", "renewal", "unexpected charge", "transaction", "subscription", "fee"],
}
for intent, template, risk, ok in templates:
    for index, value in enumerate(values[intent]):
        rows.append({"id": f"g{len(rows)+1:03d}", "brand": "Spotify", "customer_text": template.format(x=value), "intent": intent, "risk": risk, "human_reply_ok": ok})
with (ROOT / "data/golden_set.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(f"wrote {len(rows)} golden examples")
