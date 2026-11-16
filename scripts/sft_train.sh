#!/usr/bin/env bash
set -euo pipefail

# Supply all paths explicitly; no machine-specific paths are stored in this release.
: "${MODEL_PATH:?Set MODEL_PATH}"
: "${TRAIN_DATA:?Set TRAIN_DATA}"
: "${VALID_DATA:?Set VALID_DATA}"
: "${OUTPUT_DIR:?Set OUTPUT_DIR}"

swift sft \
  --model "${MODEL_PATH}" \
  --train_type lora \
  --dataset "${TRAIN_DATA}" \
  --val_dataset "${VALID_DATA}" \
  --output_dir "${OUTPUT_DIR}" \
  --num_train_epochs 1 \
  --learning_rate 5e-5 \
  --per_device_train_batch_size 1 \
  --per_device_eval_batch_size 1 \
  --gradient_accumulation_steps 16 \
  --gradient_checkpointing true \
  --bf16 true \
  --eval_steps 100 \
  --save_steps 100 \
  --lora_rank 8 \
  --seed 42
