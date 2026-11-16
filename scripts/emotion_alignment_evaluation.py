"""Evaluate generated explanations using only the paper's emotion-alignment metric."""

import argparse
import json
import re

from common import append_jsonl, call_chat, iter_jsonl
from prompts import EMOTION_ALIGNMENT_PROMPTS


def parse_score(text):
    """Parse and validate an integer emotion-alignment score."""
    try:
        value = int(json.loads(text)["emotion_alignment"])
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        match = re.search(r'"emotion_alignment"\s*:\s*([1-5])', text)
        if not match:
            raise ValueError(f"Invalid judge response: {text}")
        value = int(match.group(1))
    if value not in range(1, 6):
        raise ValueError(f"Score outside 1-5: {value}")
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="JSONL with image_path, culture, predicted_emotion, and explanation.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-key-env", default=None)
    args = parser.parse_args()

    for record in iter_jsonl(args.input):
        prompt = EMOTION_ALIGNMENT_PROMPTS[record["culture"]].format(
            predicted_emotion=record["predicted_emotion"],
            explanation=record["explanation"],
        )
        response = call_chat(
            args.endpoint, args.model, prompt, record["image_path"], args.api_key_env,
        )
        append_jsonl(args.output, {**record, "emotion_alignment": parse_score(response)})


if __name__ == "__main__":
    main()
