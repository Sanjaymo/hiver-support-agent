from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hiver_agent import evaluate, judge_agreement, load_examples, load_gold, predict


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Hiver support-agent demo")
    parser.add_argument("--brand", default="Spotify")
    parser.add_argument("--data", default="data/demo_conversations.csv")
    parser.add_argument("--gold", default="data/golden_set.csv")
    parser.add_argument("--message", help="Predict one message instead of only evaluating")
    args = parser.parse_args()
    examples = load_examples(ROOT / args.data, args.brand)
    gold = load_gold(ROOT / args.gold)
    metrics = evaluate(gold, examples)
    metrics.update(judge_agreement(gold, examples))
    print(json.dumps({"brand": args.brand, "metrics": metrics}, indent=2))
    if args.message:
        prediction = predict(args.message, examples)
        print(json.dumps({"prediction": prediction.__dict__}, indent=2))


if __name__ == "__main__":
    main()
