#!/usr/bin/env bash
# DermAssist AI — train binary ResNet50 then EfficientNet-B0 (research only).
#
# Usage:
#   WORKFLOW_EPOCHS=1 ./compare_models_workflow.sh
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODELS="$ROOT/models"
EPOCHS="${WORKFLOW_EPOCHS:-10}"
BATCH="${WORKFLOW_BATCH_SIZE:-32}"
FOLD="${WORKFLOW_FOLD:-0}"
NUM_WORKERS="${WORKFLOW_NUM_WORKERS:-}"

if [[ "$(uname -s)" == "Darwin" ]] && [[ -z "${NUM_WORKERS}" ]]; then
  NUM_WORKERS=0
fi
if [[ -z "${NUM_WORKERS}" ]]; then
  NUM_WORKERS=4
fi

DATA_ROOT="$(python3 "$ROOT/scripts/resolve_ham10000_root.py")"
echo "Using HAM10000 data root: $DATA_ROOT"

cd "$MODELS"
if [[ -d .venv ]]; then
  # shellcheck source=/dev/null
  source .venv/bin/activate
fi

ARGS=(--data-root "$DATA_ROOT" --task binary --epochs "$EPOCHS" --batch-size "$BATCH" --fold "$FOLD" --num-workers "$NUM_WORKERS")

echo "=========================================="
echo "Step 1: Binary classification — ResNet50"
echo "=========================================="
python train.py "${ARGS[@]}" --model resnet50

CKPT_RESNET="$MODELS/checkpoints/best_binary_resnet50_fold${FOLD}.pt"
echo ""
echo "→ ResNet50 checkpoint: $CKPT_RESNET"

if [[ -t 0 ]]; then
  read -r -p "Press Enter to continue with EfficientNet-B0 training (or Ctrl+C to stop here)..." _
fi

echo "=========================================="
echo "Step 2: Binary classification — EfficientNet-B0"
echo "=========================================="
python train.py "${ARGS[@]}" --model efficientnet_b0

CKPT_EFF="$MODELS/checkpoints/best_binary_efficientnet_b0_fold${FOLD}.pt"
echo ""
echo "→ EfficientNet-B0 checkpoint: $CKPT_EFF"
echo "Done."
