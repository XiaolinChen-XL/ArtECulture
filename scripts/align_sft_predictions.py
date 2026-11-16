import argparse

from common import append_jsonl, iter_jsonl
from prompts import SFT_INSTRUCTIONS


def prediction_image(record):
    """Recover the image path from a SWIFT prediction record, if present."""
    for key in ("images", "image", "image_path"):
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
        if isinstance(value, list) and value:
            first = value[0]
            if isinstance(first, str):
                return first
            if isinstance(first, dict):
                for inner in ("image", "path", "image_path"):
                    if isinstance(first.get(inner), str):
                        return first[inner]
    for message in record.get("messages", []):
        content = message.get("content")
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "image":
                    path = item.get("image") or item.get("image_path")
                    if isinstance(path, str):
                        return path
    return None


def prediction_culture(record):
    """Recover the culture from the instruction text of a prediction record."""
    texts = []
    for message in record.get("messages", []):
        if message.get("role") != "user":
            continue
        content = message.get("content")
        if isinstance(content, str):
            texts.append(content)
        elif isinstance(content, list):
            texts.extend(item["text"] for item in content
                         if isinstance(item, dict) and isinstance(item.get("text"), str))
    for key in ("query", "prompt", "instruction"):
        if isinstance(record.get(key), str):
            texts.append(record[key])
    for text in texts:
        for culture, instruction in SFT_INSTRUCTIONS.items():
            if instruction in text:
                return culture
    return None


def prediction_text(record, response_field):
    """Recover the generated text from a SWIFT prediction record."""
    value = record.get(response_field)
    if isinstance(value, str):
        return value
    for message in reversed(record.get("messages", [])):
        if message.get("role") == "assistant" and isinstance(message.get("content"), str):
            return message["content"]
    return ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", required=True, help="SWIFT result JSONL from sft_inference.sh.")
    parser.add_argument("--reference", required=True,
                        help="Test JSONL with image_path, culture, emotion, and optionally region.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--response-field", default="response")
    parser.add_argument("--match", choices=["image", "order"], default="image")
    args = parser.parse_args()

    reference = list(iter_jsonl(args.reference))
    predictions = list(iter_jsonl(args.predictions))

    if args.match == "order":
        if len(predictions) != len(reference):
            raise SystemExit(
                f"Positional matching needs equal lengths: "
                f"{len(predictions)} predictions vs {len(reference)} reference records."
            )
        pairs = zip(predictions, reference)
    else:
        index = {}
        for record in reference:
            index.setdefault((record["image_path"], record["culture"]), []).append(record)
        pairs = []
        for prediction in predictions:
            image = prediction_image(prediction)
            culture = prediction_culture(prediction)
            if image is None or culture is None:
                raise SystemExit(
                    "A prediction record lacks an image path or a recognizable "
                    "instruction; rerun with --match order."
                )
            bucket = index.get((image, culture))
            if not bucket:
                raise SystemExit(f"No reference record for image {image} under culture {culture}.")
            pairs.append((prediction, bucket.pop(0)))

        remaining = sum(len(bucket) for bucket in index.values())
        if remaining:
            raise SystemExit(f"Incomplete predictions: {remaining} reference records were not matched.")

    written = 0
    for prediction, record in pairs:
        aligned = {
            "image_path": record["image_path"],
            "culture": record["culture"],
            "emotion": record["emotion"],
            "response": prediction_text(prediction, args.response_field),
        }
        if record.get("region"):
            aligned["region"] = record["region"]
        if record.get("image_id"):
            aligned["image_id"] = record["image_id"]
        append_jsonl(args.output, aligned)
        written += 1

    print(f"aligned {written} predictions")


if __name__ == "__main__":
    main()
