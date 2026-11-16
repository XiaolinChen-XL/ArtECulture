"""Run zero-shot culture-conditioned emotion prediction."""

import argparse

from common import append_jsonl, call_chat, iter_jsonl
from prompts import ZERO_SHOT_PROMPTS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="JSONL with image_path and culture fields.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-key-env", default=None)
    args = parser.parse_args()

    for record in iter_jsonl(args.input):
        culture = record["culture"]
        response = call_chat(
            args.endpoint, args.model, ZERO_SHOT_PROMPTS[culture],
            record["image_path"], args.api_key_env,
        )
        append_jsonl(args.output, {**record, "response": response})


if __name__ == "__main__":
    main()
