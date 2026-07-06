#!/usr/bin/env bash
set -euo pipefail

TUCKER_ROOT="${AKO_TUCKER_ROOT:-/home/liuxu/projects/tucker}"
RUNNER_SCRIPT="${AKO_RUNNER_SCRIPT:-${TUCKER_ROOT}/scripts/run_ds2_fixed100_end2end.py}"
PYTHON_BIN="${AKO_BACKEND_PYTHON:-${AKO_PYTHON:-${TUCKER_ROOT}/tucker_env/bin/python}}"

if [[ "${PYTHON_BIN}" == */* && ! -x "${PYTHON_BIN}" ]]; then
  PYTHON_BIN="python3"
fi

if [[ ! -f "${RUNNER_SCRIPT}" ]]; then
  echo "[ds2_fixed100] missing runner: ${RUNNER_SCRIPT}" >&2
  exit 1
fi

serial="10.29.230.131:5555"
dataset=""
decode_tokens="16"
repeats="1"
limit="1"
start_index="0"
out_dir=""
idle_seconds="0"
sleep_between_runs_s="0"
cooldown_max_wait_s="300"
local_runner="${TUCKER_ROOT}/scripts/ds2_debug_phone_run_chat_adsp.sh"
phone_runner="/data/local/tmp/ds2_debug_phone_run_chat_adsp.sh"
phone_base="/data/local/tmp/deepseek_v2_td_qnn_aot_w8a16_20260527"
extra_env="${AKO_DS2_EXTRA_ENV:-}"
if [[ "${AKO_QWEN2_RESIDENCY_TRACE:-0}" = "1" || "${AKO_DS2_RESIDENCY_TRACE:-0}" = "1" ]]; then
  extra_env="${extra_env:+${extra_env} }MLLM_DS2_TD_RESIDENCY_TRACE=1"
fi
if [[ "${AKO_QWEN2_RESIDENCY_TRACE_EVENTS:-0}" = "1" || "${AKO_DS2_RESIDENCY_TRACE_EVENTS:-0}" = "1" ]]; then
  trace_limit="${AKO_DS2_RESIDENCY_TRACE_EVENT_LIMIT:-${AKO_QWEN2_RESIDENCY_TRACE_EVENT_LIMIT:-200}}"
  extra_env="${extra_env:+${extra_env} }MLLM_DS2_TD_RESIDENCY_TRACE_EVENTS=1 MLLM_DS2_TD_RESIDENCY_TRACE_EVENT_LIMIT=${trace_limit}"
fi
core_breakdown="${AKO_DS2_CORE_BREAKDOWN:-1}"
metric_summary="${AKO_DS2_METRIC_SUMMARY:-1}"
timing="${AKO_DS2_TIMING:-1}"
log_tokens="${AKO_DS2_LOG_TOKENS:-1}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --) shift ;;
    --serial) serial="$2"; shift 2 ;;
    --dataset) dataset="$2"; shift 2 ;;
    --decode-tokens) decode_tokens="$2"; shift 2 ;;
    --repeats) repeats="$2"; shift 2 ;;
    --limit) limit="$2"; shift 2 ;;
    --start-index) start_index="$2"; shift 2 ;;
    --out-dir) out_dir="$2"; shift 2 ;;
    --idle-seconds) idle_seconds="$2"; shift 2 ;;
    --sleep-between-runs-s) sleep_between_runs_s="$2"; shift 2 ;;
    --cooldown-max-wait-s) cooldown_max_wait_s="$2"; shift 2 ;;
    --local-runner) shift 2 ;;
    --push-runner) shift 2 ;;
    --preload-top-n|--global-cache-budget-mb|--mmap-only|--diag|--no-prefetch|--no-mbm-prefetch|--force-decode|--force-gguf-dequant-f32)
      shift 2
      ;;
    *)
      echo "[ds2_fixed100] unsupported argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "${dataset}" ]]; then
  echo "[ds2_fixed100] --dataset is required" >&2
  exit 2
fi
if [[ -z "${out_dir}" ]]; then
  out_dir="$(pwd)/results/runs/ds2_fixed100_$(date +%Y%m%d_%H%M%S)"
fi

exec "${PYTHON_BIN}" "${RUNNER_SCRIPT}" \
  --serial "${serial}" \
  --dataset "${dataset}" \
  --decode-tokens "${decode_tokens}" \
  --repeats "${repeats}" \
  --limit "${limit}" \
  --start-index "${start_index}" \
  --out-dir "${out_dir}" \
  --idle-seconds "${idle_seconds}" \
  --sleep-between-runs-s "${sleep_between_runs_s}" \
  --cooldown-max-wait-s "${cooldown_max_wait_s}" \
  --local-runner "${local_runner}" \
  --phone-runner "${phone_runner}" \
  --phone-base "${phone_base}" \
  --extra-env "${extra_env}" \
  --core-breakdown "${core_breakdown}" \
  --metric-summary "${metric_summary}" \
  --timing "${timing}" \
  --log-tokens "${log_tokens}"
