#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAGE="${AKO_STAGE:-default}"
ITERATION_ID="${AKO_ITERATION_ID:-${STAGE}_$(date +%Y%m%d_%H%M%S)}"
CODE_REPO="${AKO_CODE_REPO:-/home/liuxu/projects/MNN}"
BACKEND="${AKO_BACKEND:-qwen2_td_qnn}"
BACKEND_SCRIPT="${AKO_BACKEND_SCRIPT:-${ROOT}/scripts/backends/${BACKEND}.sh}"
PARSER_PYTHON="${AKO_PARSER_PYTHON:-python3}"
OUT_ROOT="${AKO_OUT_ROOT:-${ROOT}/results/runs}"
OUT_DIR="${AKO_OUT_DIR:-${OUT_ROOT}/${ITERATION_ID}}"
METRICS_FILE="${OUT_DIR}/metrics.json"
STAGE_METRICS="${ROOT}/results/metrics_${STAGE}.jsonl"

mkdir -p "${OUT_DIR}" "$(dirname "${STAGE_METRICS}")"

compile_success=1
if [[ -n "${AKO_BUILD_CMD:-}" ]]; then
  echo "[build] ${AKO_BUILD_CMD}"
  if ! (cd "${CODE_REPO}" && bash -lc "${AKO_BUILD_CMD}"); then
    compile_success=0
  fi
fi

run_success=1
if [[ "${compile_success}" -eq 1 ]]; then
  if [[ ! -x "${BACKEND_SCRIPT}" ]]; then
    echo "[backend] missing or not executable: ${BACKEND_SCRIPT}" >&2
    run_success=0
  else
    echo "[backend] ${BACKEND_SCRIPT}"
    if ! "${BACKEND_SCRIPT}" \
    --serial "${AKO_SERIAL:-10.29.230.131:5555}" \
    --dataset "${AKO_DATASET:-/home/liuxu/projects/results/ds_tilemoe/ds2_cold20_prompts.jsonl}" \
    --decode-tokens "${AKO_DECODE_TOKENS:-8}" \
    --repeats "${AKO_REPEATS:-1}" \
    --limit "${AKO_LIMIT:-0}" \
    --start-index "${AKO_START_INDEX:-0}" \
    --local-runner "${AKO_LOCAL_RUNNER:-/home/liuxu/projects/mllm/build-android-arm64-v8a/bin/mllm-deepseek-v2-edgemoe-runner}" \
    --push-runner "${AKO_PUSH_RUNNER:-0}" \
    --preload-top-n "${AKO_PRELOAD_TOP_N:-1}" \
    --global-cache-budget-mb "${AKO_GLOBAL_CACHE_BUDGET_MB:-256}" \
    --mmap-only "${AKO_MMAP_ONLY:-1}" \
    --diag "${AKO_DIAG:-1}" \
    --no-prefetch "${AKO_NO_PREFETCH:-0}" \
    --no-mbm-prefetch "${AKO_NO_MBM_PREFETCH:-0}" \
    --force-decode "${AKO_FORCE_DECODE:-0}" \
    --force-gguf-dequant-f32 "${AKO_FORCE_GGUF_DEQUANT_F32:-0}" \
    --idle-seconds "${AKO_IDLE_SECONDS:-60}" \
    --sleep-between-runs-s "${AKO_SLEEP_BETWEEN_RUNS_S:-300}" \
    --cooldown-max-wait-s "${AKO_COOLDOWN_MAX_WAIT_S:-1800}" \
    --out-dir "${OUT_DIR}" \
    "$@"; then
      run_success=0
    fi
  fi
else
  echo "[build] failed; writing empty metrics"
fi

if [[ ! -f "${OUT_DIR}/summary.jsonl" ]]; then
  : > "${OUT_DIR}/summary.jsonl"
fi

parser_args=(
  "${ROOT}/scripts/parse_metrics.py"
  --summary "${OUT_DIR}/summary.jsonl"
  --stage "${STAGE}"
  --iteration-id "${ITERATION_ID}"
  --compile-success "${compile_success}"
  --out "${METRICS_FILE}"
)
if [[ -n "${AKO_BASELINE_METRICS:-}" ]]; then
  parser_args+=(--baseline-metrics "${AKO_BASELINE_METRICS}")
fi

"${PARSER_PYTHON}" "${parser_args[@]}" | tee -a "${STAGE_METRICS}"

if [[ "${compile_success}" -ne 1 || "${run_success}" -ne 1 ]]; then
  exit 1
fi
