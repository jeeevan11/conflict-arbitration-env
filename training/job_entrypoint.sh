#!/usr/bin/env bash
set -euo pipefail

# This script is what the HF Job container runs.
# Required env vars at job submission:
#   HF_TOKEN     — write token (auto-injected by `hf jobs run`)
#   ENV_URL      — your live HF Space URL (e.g. https://testingaccc-conflict-arbitration-env.hf.space)
#   UPLOAD_REPO  — HF model repo to upload results to (e.g. testingaccc/conflict-arbitrator-model)
#   SEED         — integer seed (default 42)
#   STEPS        — training steps (default 2000)
#   SPACE_REPO   — your Space repo URL to clone the code from

SEED="${SEED:-42}"
STEPS="${STEPS:-2000}"

# Run from current dir — code is expected to already be cloned.
echo "[job] cwd: $(pwd)"
echo "[job] python: $(python --version)"
echo "[job] gpu:"
nvidia-smi || true

echo "[job] installing deps"
python -m pip install --upgrade pip
# Upgrade torch to 2.5+ so unsloth_zoo (which needs torch._inductor.config) works.
python -m pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
python -m pip install fastapi uvicorn pydantic matplotlib huggingface_hub
python -m pip install "transformers>=4.50.3,<4.55.0"
python -m pip install "accelerate>=1.0.0" "peft>=0.13.0" "datasets>=3.0.0"
python -m pip install "trl>=0.12.0,<0.16.0"
python -m pip install bitsandbytes
# Plain unsloth (skip flash-attn extras — needs build-time torch which pip isolation hides)
python -m pip install --no-deps unsloth_zoo
python -m pip install --no-deps unsloth
python -m pip install xformers --index-url https://download.pytorch.org/whl/cu121 || true
python -m pip install triton tyro typeguard cut_cross_entropy sentence-transformers msgspec hf_transfer

# Sanity check: confirm unsloth + GPU
python -c "import torch; print('[job] torch', torch.__version__, 'cuda?', torch.cuda.is_available())"
python -c "import unsloth; from unsloth import FastLanguageModel; print('[job] unsloth import OK')"

export PYTHONPATH=.
echo "[job] starting training: seed=$SEED steps=$STEPS env=$ENV_URL upload=$UPLOAD_REPO"

python -m training.train \
  --env-url "$ENV_URL" \
  --upload-repo "$UPLOAD_REPO" \
  --seed "$SEED" \
  --steps "$STEPS"

echo "[job] done"
