"""Parse rationale-generation responses into structured tuples.

Bridges `cultural_rationale_generation.py`, which stores the raw model output
in `rationale_response`, and `reverse_emotion_validation.py`, which expects a
`rationales` list. The dominant emotion is the frequency-derived one from
Eq. (1) and is carried through unchanged.
"""

import argparse
import json

from common import append_jsonl, iter_jsonl


def parse_response(text):
    """Recover the rationale list from a JSON response, tolerating code fences."""
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError(f"No JSON object found in response: {text}")
    payload = json.loads(text[start:end + 1])
    rationales = payload.get("rationales", [])
    if isinstance(rationales, str):
        rationales = [rationales]
    cleaned, seen = [], set()
    for item in rationales:
        rationale = str(item).strip()
        if rationale and rationale not in seen:
            seen.add(rationale)
            cleaned.append(rationale)
    return cleaned


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="JSONL from cultural_rationale_generation.py.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--errors", default=None, help="Optional JSONL for unparsable responses.")
    args = parser.parse_args()

    for record in iter_jsonl(args.input):
        try:
            rationales = parse_response(record["rationale_response"])
        except (ValueError, KeyError, json.JSONDecodeError) as error:
            if args.errors:
                append_jsonl(args.errors, {**record, "parse_error": str(error)})
            continue
        if not rationales:
            if args.errors:
                append_jsonl(args.errors, {**record, "parse_error": "empty rationale list"})
            continue
        append_jsonl(args.output, {
            "concept": record["concept"],
            "culture": record["culture"],
            "emotion_distribution": record.get("emotion_distribution"),
            "dominant_emotion": record["dominant_emotion"],
            "rationales": rationales,
        })


if __name__ == "__main__":
    main()
