"""Assemble the cultural emotion knowledge base after judge filtering.

Consumes the output of `reverse_emotion_validation.py` and writes the tuples
that constitute the knowledge base K used by
`retrieval_augmented_inference.py`.

Tuples flagged by either judge are resolved by native-speaker review, supplied
through `--human-review` as a JSONL of
`{"concept": ..., "culture": ..., "keep": true|false}`.
"""

import argparse
from collections import Counter

from common import append_jsonl, iter_jsonl


def load_review(path):
    """Map (concept, culture) to a native-speaker keep/drop decision."""
    decisions = {}
    if path:
        for record in iter_jsonl(path):
            decisions[(record["concept"], record["culture"])] = bool(record["keep"])
    return decisions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="JSONL from reverse_emotion_validation.py.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--human-review", default=None, help="JSONL of native-speaker decisions.")
    parser.add_argument("--unreviewed", choices=["drop", "keep"], default="drop",
                        help="Policy for flagged tuples without a review decision.")
    args = parser.parse_args()

    decisions = load_review(args.human_review)
    tuples = Counter()
    rationales = Counter()

    for record in iter_jsonl(args.input):
        if record.get("flagged_for_human_review"):
            key = (record["concept"], record["culture"])
            keep = decisions.get(key, args.unreviewed == "keep")
            if not keep:
                continue
        append_jsonl(args.output, {
            "concept": record["concept"],
            "culture": record["culture"],
            "dominant_emotion": record["dominant_emotion"],
            "rationales": record["rationales"],
        })
        tuples[record["culture"]] += 1
        rationales[record["culture"]] += len(record["rationales"])

    for culture in sorted(tuples):
        print(f"{culture:<10} tuples={tuples[culture]:<7} rationales={rationales[culture]}")
    print(f"{'total':<10} tuples={sum(tuples.values()):<7} rationales={sum(rationales.values())}")


if __name__ == "__main__":
    main()
