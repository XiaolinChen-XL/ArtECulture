#!/usr/bin/env bash
set -euo pipefail

# Supply the trained adapter and evaluation data at runtime.
: "${MODEL_PATH:?Set MODEL_PATH}"
: "${ADAPTER_PATH:?Set ADAPTER_PATH}"
: "${TEST_DATA:?Set TEST_DATA}"
: "${RESULT_PATH:?Set RESULT_PATH}"

swift infer \
  --model "${MODEL_PATH}" \
  --adapters "${ADAPTER_PATH}" \
  --val_dataset "${TEST_DATA}" \
  --result_path "${RESULT_PATH}" \
  --temperature 0 \
  --max_new_tokens 256
