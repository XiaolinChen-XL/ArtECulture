"""Build frequency-driven concept-emotion associations from the training split."""

import argparse
from collections import Counter, defaultdict

from common import append_jsonl, iter_jsonl
from prompts import EMOTIONS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="JSONL with concepts and culture_emotions fields.")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    counts = defaultdict(Counter)
    totals = Counter()
    for record in iter_jsonl(args.input):
        for concept in set(record["concepts"]):
            for culture, emotion in record["culture_emotions"].items():
                counts[(concept, culture)][emotion] += 1
                totals[(concept, culture)] += 1

    for (concept, culture), emotion_counts in sorted(counts.items()):
        total = totals[(concept, culture)]
        distribution = {emotion: emotion_counts[emotion] / total for emotion in EMOTIONS}
        dominant = max(EMOTIONS, key=distribution.get)
        append_jsonl(args.output, {
            "concept": concept,
            "culture": culture,
            "emotion_distribution": distribution,
            "dominant_emotion": dominant,
        })


if __name__ == "__main__":
    main()
