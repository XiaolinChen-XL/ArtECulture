# Data schema

All files use UTF-8. Each JSONL line contains one record.

## Benchmark metadata

`data/metadata.csv` contains one row per artwork. `data/splits/train.csv`, `val.csv`, and `test.csv` contain the corresponding split records.

| Field | Description |
|---|---|
| `image_id` | Stable image identifier, including filename extension. |
| `image_path` | Image path relative to the repository root. |
| `english_emotion`, `chinese_emotion`, `arabic_emotion` | Culture-level majority emotion labels. |
| `country` | Source country or artistic tradition. |
| `region_group` | `western` or `non-western`. |
| `split` | `train`, `val`, or `test`. |

Join annotations using `image_id`; load images using `image_path`.

## Emotion explanations

`data/explanations/en.jsonl`, `zh.jsonl`, and `ar.jsonl` contain the English, Chinese, and Arabic annotations. Each record has `image_id`, `image_path`, `split`, `language`, and an `explanations` list. Each explanation has:

- `emotion`: the individual annotation's emotion label.
- `text`: the explanation text.
- `source`: the annotation source.

Individual emotion annotations may differ from the culture-level majority label in the metadata.

## Cultural emotion knowledge base

`knowledge_base/en.jsonl`, `zh.jsonl`, and `ar.jsonl` contain culture-specific entries. `all.jsonl` combines the three files for retrieval.

Each entry contains `concept`, `culture`, `dominant_emotion`, and `rationales`, corresponding to the knowledge tuple used in the method. `emotion_distribution` and `has_cultural_meaning` are also included, along with translated concept/association fields where available.

`dominant_emotion` is the maximum-probability emotion in `emotion_distribution`. Ties follow the emotion order in `scripts/prompts.py`. `rationales` contains the supplied concept associations.

## Model inputs

`prepare_inputs.py` converts the data into model inputs: `evaluation` gives one record per image and culture; `concepts` gives one record per image with culture-level labels; `sft` includes reference explanations for train/val. SFT creates one target per explanation using the culture-level majority label. Test prompts produced by `prepare_sft_inference.py` contain no reference answers.
