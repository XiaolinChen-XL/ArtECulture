"""Filter generated knowledge using two independent reverse-emotion judges."""

import argparse
import re

from common import append_jsonl, call_chat, iter_jsonl
from prompts import EMOTIONS, REVERSE_VALIDATION_PROMPTS


def normalize_prediction(text):
    """Recover one canonical English emotion label from a judge response."""
    aliases = {
        "好笑": "amusement", "惊叹": "awe", "满足": "contentment", "满意": "contentment",
        "兴奋": "excitement", "愤怒": "anger", "嫌恶": "disgust",
        "恐惧": "fear", "伤感": "sadness", "其它情感": "something else",
        "المتعة": "amusement", "الذهول": "awe", "الرضا": "contentment",
        "الحماس": "excitement", "الغضب": "anger", "الاشمئزاز": "disgust",
        "الخوف": "fear", "الحزن": "sadness", "أخرى": "something else",
    }
    for label, canonical in aliases.items():
        if label in text:
            return canonical
    normalized = re.sub(r"[^a-z ]", " ", text.lower())
    for emotion in sorted(EMOTIONS, key=len, reverse=True):
        if re.search(rf"\b{re.escape(emotion)}\b", normalized):
            return emotion
    return text.strip().lower()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="JSONL with culture, dominant_emotion, and rationales.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--judge", action="append", nargs=3, metavar=("ENDPOINT", "MODEL", "KEY_ENV"), required=True)
    args = parser.parse_args()
    if len(args.judge) != 2:
        raise SystemExit("Exactly two independent judges are required by the paper protocol.")

    for record in iter_jsonl(args.input):
        prompt = REVERSE_VALIDATION_PROMPTS[record["culture"]].format(
            rationales="\n".join(record["rationales"]),
        )
        raw = [call_chat(endpoint, model, prompt, api_key_env=key_env) for endpoint, model, key_env in args.judge]
        predictions = [normalize_prediction(text) for text in raw]
        dominant = record["dominant_emotion"].strip().lower()
        append_jsonl(args.output, {
            **record,
            "judge_predictions": predictions,
            "flagged_for_human_review": any(prediction != dominant for prediction in predictions),
        })


if __name__ == "__main__":
    main()
