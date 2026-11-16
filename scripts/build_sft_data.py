"""Build one supervised fine-tuning instance per reference explanation."""

import argparse

from common import append_jsonl, iter_jsonl
from prompts import EMOTION_LABELS, SFT_INSTRUCTIONS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="JSONL with image_path, culture, emotion, and explanations.")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    for record in iter_jsonl(args.input):
        culture = record["culture"]
        emotion = EMOTION_LABELS[culture][record["emotion"]]
        for explanation in record["explanations"]:
            append_jsonl(args.output, {
                "messages": [
                    {"role": "user", "content": [
                        {"type": "image", "image": record["image_path"]},
                        {"type": "text", "text": SFT_INSTRUCTIONS[culture]},
                    ]},
                    {"role": "assistant", "content": f"[{emotion}; {explanation}]"},
                ]
            })


if __name__ == "__main__":
    main()
