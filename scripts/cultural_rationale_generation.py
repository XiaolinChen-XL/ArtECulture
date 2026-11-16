"""Generate culture-specific rationales for concept-emotion associations."""

import argparse
import json

from common import append_jsonl, call_chat, iter_jsonl
from prompts import RATIONALE_GENERATION_PROMPTS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="JSONL with concept, culture, and emotion_distribution.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-key-env", default=None)
    args = parser.parse_args()

    for record in iter_jsonl(args.input):
        prompt = RATIONALE_GENERATION_PROMPTS[record["culture"]].format(
            concept=record["concept"],
            emotion_distribution=json.dumps(record["emotion_distribution"], ensure_ascii=False),
        )
        response = call_chat(args.endpoint, args.model, prompt, api_key_env=args.api_key_env)
        append_jsonl(args.output, {**record, "rationale_response": response})


if __name__ == "__main__":
    main()
