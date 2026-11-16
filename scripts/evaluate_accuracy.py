"""Compute emotion-prediction accuracy.

Reads the JSONL written by `zero_shot_emotion_prediction.py`,
`retrieval_augmented_inference.py`, or SFT inference. The emotion label is
extracted from the model output by matching the nine emotion categories, and an
output that matches none of them is counted as incorrect.

Accuracy is reported per culture and overall (Table 2), and, when records carry
a `region` field and --by-region is set, for the supplementary regional analysis.
`--dump-parsed` additionally writes the predicted emotion and the explanation
in the form expected by `emotion_alignment_evaluation.py`.
"""

import argparse
from collections import defaultdict

from common import append_jsonl, iter_jsonl

INVALID = "__invalid__"

# Surface forms of the nine categories in the three culture-conditioned prompts.
LABEL_ALIASES = {
    "amusement": "amusement", "awe": "awe", "contentment": "contentment",
    "excitement": "excitement", "anger": "anger", "disgust": "disgust",
    "fear": "fear", "sadness": "sadness", "something else": "something else",
    "好笑": "amusement", "惊叹": "awe", "满足": "contentment",
    "兴奋": "excitement", "愤怒": "anger", "嫌恶": "disgust",
    "恐惧": "fear", "伤感": "sadness", "其它情感": "something else",
    "المتعة": "amusement", "الذهول": "awe", "الرضا": "contentment",
    "الحماس": "excitement", "الغضب": "anger", "الاشمئزاز": "disgust",
    "الخوف": "fear", "الحزن": "sadness", "أخرى": "something else",
    # Wording variants a model may return instead of the prompt's surface form.
    "满意": "contentment", "其它": "something else", "其他": "something else",
    "悲伤": "sadness", "التسلية": "amusement", "الرهبة": "awe",
    "شيء آخر": "something else",
}

LABEL_LINE_PREFIXES = ("emotion:", "情感：", "情感:", "الشعور:", "الشعور：")
EXPLANATION_PREFIXES = ("explanation:", "解释：", "解释:", "التفسير:", "التفسير：")


def scan(text):
    """Return the earliest matching category in `text`, or None."""
    lowered = text.lower()
    best_label, best_position, best_length = None, -1, 0
    for surface, canonical in LABEL_ALIASES.items():
        position = lowered.find(surface.lower())
        if position < 0:
            continue
        if best_label is None or position < best_position or (
            position == best_position and len(surface) > best_length
        ):
            best_label, best_position, best_length = canonical, position, len(surface)
    return best_label


def extract_emotion(text):
    """Match the model output against the nine categories."""
    if not text:
        return INVALID
    for line in text.splitlines():
        stripped = line.strip().lstrip("*-• ").strip()
        if any(stripped.lower().startswith(prefix) for prefix in LABEL_LINE_PREFIXES):
            label = scan(stripped.split(":", 1)[-1].split("：", 1)[-1])
            if label is not None:
                return label
    label = scan(text)
    return label if label is not None else INVALID


def split_explanation(text):
    """Recover the explanation part of a model output.

    Handles the `Explanation:` line of the zero-shot and retrieval prompts and
    the `[emotion; explanation]` target sequence produced after SFT.
    """
    if not text:
        return ""
    for line in text.splitlines():
        stripped = line.strip().lstrip("*-• ").strip()
        if any(stripped.lower().startswith(prefix) for prefix in EXPLANATION_PREFIXES):
            return stripped.split(":", 1)[-1].split("：", 1)[-1].strip()
    stripped = text.strip()
    if stripped.startswith("[") and stripped.endswith("]") and ";" in stripped:
        return stripped[1:-1].split(";", 1)[1].strip()
    return stripped


def accuracy(rows):
    return 100.0 * sum(gold == pred for gold, pred in rows) / len(rows) if rows else 0.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="JSONL with gold 'emotion' and model 'response'.")
    parser.add_argument("--response-field", default="response")
    parser.add_argument("--dump-parsed", default=None,
                        help="Optional JSONL with predicted_emotion and explanation "
                             "for emotion_alignment_evaluation.py.")
    parser.add_argument("--by-region", action="store_true", help="Report the supplementary Western/non-Western breakdown.")
    args = parser.parse_args()

    overall = []
    by_culture = defaultdict(list)
    by_culture_region = defaultdict(list)

    for record in iter_jsonl(args.input):
        response = str(record.get(args.response_field, ""))
        gold = extract_emotion(str(record["emotion"]))
        pred = extract_emotion(response)
        culture = record.get("culture", "all")
        overall.append((gold, pred))
        by_culture[culture].append((gold, pred))
        if args.by_region and record.get("region"):
            by_culture_region[(culture, record["region"])].append((gold, pred))

        if args.dump_parsed and pred != INVALID:
            append_jsonl(args.dump_parsed, {
                **{key: record[key] for key in ("image_path", "culture") if key in record},
                "predicted_emotion": pred,
                "explanation": split_explanation(response),
            })

    for culture in sorted(by_culture):
        print(f"{culture:<10} n={len(by_culture[culture]):<6} acc={accuracy(by_culture[culture]):.2f}")
        for (name, region), rows in sorted(by_culture_region.items()):
            if name == culture:
                print(f"  {region:<8} n={len(rows):<6} acc={accuracy(rows):.2f}")
    print(f"{'overall':<10} n={len(overall):<6} acc={accuracy(overall):.2f}")


if __name__ == "__main__":
    main()