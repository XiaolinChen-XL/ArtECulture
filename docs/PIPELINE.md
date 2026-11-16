# Research workflow

Run from the repository root. Every output path in these examples should be new: scripts reject existing result files to avoid silently appending duplicated runs. The shell examples use Bash. API endpoints, models, and credentials must be supplied by the user; no remote inference is performed by data preparation or validation.

## Zero-shot prediction

```bash
python scripts/prepare_inputs.py --split test --output runs/test.jsonl
export MODEL_ENDPOINT='https://your-provider.example/v1/chat/completions'
export MODEL_NAME='your-vision-model'
export MODEL_API_KEY='your-key'
python scripts/zero_shot_emotion_prediction.py --input runs/test.jsonl --output runs/zero_shot.jsonl --endpoint "$MODEL_ENDPOINT" --model "$MODEL_NAME" --api-key-env MODEL_API_KEY
python scripts/evaluate_accuracy.py --input runs/zero_shot.jsonl --dump-parsed runs/zero_shot_parsed.jsonl
```

Report accuracy for English, Chinese, Arabic, and overall, as in Table 2. For the supplementary Western/non-Western breakdown, add `--by-region`.

## Retrieval with the supplied knowledge base

This release starts from pre-extracted visual concepts. Concept extraction code and precomputed concept files are not included.

Prepare `runs/test_concepts_by_culture.jsonl` with one record per image and target culture. Required fields are `image_path`, `culture` (`english`, `chinese`, or `arabic`), and `concepts` (a list of strings). Preserve `image_id`, `emotion`, and `region` from the evaluation inputs for scoring. `emotion` is the gold label and is not sent to the prediction model. Supply concepts extracted from the image, without using its gold emotion or reference explanations.

```bash
python -m pip install -r requirements-retrieval.txt
python scripts/retrieval_augmented_inference.py --input runs/test_concepts_by_culture.jsonl --knowledge-base knowledge_base/all.jsonl --output runs/retrieval.jsonl --embedding-model /path/to/embedding/model --endpoint "$MODEL_ENDPOINT" --model "$MODEL_NAME" --api-key-env MODEL_API_KEY
python scripts/evaluate_accuracy.py --input runs/retrieval.jsonl
```

Retrieval uses exact matches followed by semantic similarity (default threshold 0.85, maximum five tuples).

## Knowledge construction from training data

Start from training-image records containing pre-extracted `concepts` and `culture_emotions`. `prepare_inputs.py --split train --mode concepts` supplies the image metadata and labels; add the extracted concept lists before running the following stages. Concept extraction itself is not included in this release.

1. `build_concept_emotion_associations.py`: accepts `concepts` and `culture_emotions`.
2. `cultural_rationale_generation.py`: requires endpoint/model/key environment variable.
3. `parse_rationales.py`: optionally write parse failures using `--errors`.
4. `reverse_emotion_validation.py`: requires two `--judge ENDPOINT MODEL KEY_ENV` arguments.
5. `build_knowledge_base.py`: takes optional `--human-review` JSONL records of `concept`, `culture`, and boolean `keep`. Flagged entries without decisions are dropped by default.

Construct the knowledge base using the training split only. The paper uses Gemini 3.5 Flash for training-image concept extraction and rationale generation, and GPT-5.5 plus Claude Opus 4.8 for reverse-emotion validation. Supply the corresponding provider model identifiers to the scripts.

## SFT

```bash
python -m pip install -r requirements-sft.txt
python scripts/prepare_inputs.py --split train --mode sft --output runs/train_references.jsonl
python scripts/prepare_inputs.py --split val --mode sft --output runs/val_references.jsonl
python scripts/build_sft_data.py --input runs/train_references.jsonl --output runs/sft_train.jsonl
python scripts/build_sft_data.py --input runs/val_references.jsonl --output runs/sft_val.jsonl
python scripts/prepare_sft_inference.py --input runs/test.jsonl --output runs/sft_test.jsonl
```

The expected SFT sizes are 73,785 training instances, 9,082 validation instances, and 2,037 user-only test prompts. Set `MODEL_PATH`, `TRAIN_DATA`, `VALID_DATA`, and `OUTPUT_DIR`, then run `bash scripts/sft_train.sh`. For inference set `MODEL_PATH`, `ADAPTER_PATH`, `TEST_DATA`, and `RESULT_PATH`, then run `bash scripts/sft_inference.sh`.

```bash
python scripts/align_sft_predictions.py --predictions "$RESULT_PATH" --reference runs/test.jsonl --output runs/sft_aligned.jsonl
python scripts/evaluate_accuracy.py --input runs/sft_aligned.jsonl
```

Prediction alignment uses image paths and culture instructions. SFT requires a GPU environment compatible with the selected model and ms-swift.

## Explanation alignment

Evaluate emotion alignment on a five-point scale using Claude Sonnet 5 and GLM-4.5V separately, as in Table 6. Each judge receives the image, target culture, predicted emotion, and generated explanation.

```bash
python scripts/evaluate_accuracy.py --input runs/retrieval.jsonl --dump-parsed runs/retrieval_parsed.jsonl
python scripts/emotion_alignment_evaluation.py --input runs/retrieval_parsed.jsonl --output runs/alignment_c5.jsonl --endpoint "$C5_ENDPOINT" --model "$C5_MODEL" --api-key-env C5_API_KEY
python scripts/emotion_alignment_evaluation.py --input runs/retrieval_parsed.jsonl --output runs/alignment_g4v.jsonl --endpoint "$G4V_ENDPOINT" --model "$G4V_MODEL" --api-key-env G4V_API_KEY
```

Configure each endpoint and model identifier for the corresponding judge. Report the two judges separately; do not combine their scores into a new metric.
