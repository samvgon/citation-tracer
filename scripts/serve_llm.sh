#!/usr/bin/env bash
# Launch llama-server (Vulkan) on the Radeon iGPU. OpenAI-compatible API on $PORT.
# Usage: scripts/serve_llm.sh [MODEL_FILE [extra llama-server args]]  (default: Qwen3-30B-A3B-Instruct-2507 Q4_K_M)
# Overrides: LLAMA_DIR, MODEL_DIR, PORT, CTX, ALIAS, VK_DEVICE
set -euo pipefail

LLAMA_DIR="${LLAMA_DIR:-$HOME/llama.cpp}"
MODEL_DIR="${MODEL_DIR:-$HOME/models}"
MODEL="${1:-$MODEL_DIR/Qwen3-30B-A3B-Instruct-2507-Q4_K_M.gguf}"
PORT="${PORT:-8080}"
CTX="${CTX:-32768}"
ALIAS="${ALIAS:-local-model}"   # matches llm.model in config/default.yaml
VK_DEVICE="${VK_DEVICE:-Vulkan0}"  # Radeon 8060S; llvmpipe is never selected

SERVER="$LLAMA_DIR/build/bin/llama-server"
[[ -x "$SERVER" ]] || { echo "missing $SERVER (build llama.cpp first, see README)" >&2; exit 1; }
[[ -f "$MODEL" ]] || { echo "missing model $MODEL" >&2; exit 1; }

# Ollama keeps models resident in GPU memory; warn rather than touch it.
if command -v ollama >/dev/null && [[ -n "$(ollama ps 2>/dev/null | tail -n +2)" ]]; then
  echo "warning: Ollama has loaded models (see 'ollama ps'); they hold GPU memory" >&2
fi

echo "Devices llama.cpp can see:" >&2
"$SERVER" --list-devices >&2

exec "$SERVER" -m "$MODEL" --alias "$ALIAS" --device "$VK_DEVICE" \
  -ngl 99 -c "$CTX" --host 127.0.0.1 --port "$PORT" --jinja "${@:2}"
