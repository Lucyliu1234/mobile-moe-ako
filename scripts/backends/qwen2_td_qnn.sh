#!/usr/bin/env bash
set -euo pipefail

SERIAL="${AKO_SERIAL:-10.29.230.131:5555}"
DATASET="${AKO_DATASET:-}"
LIMIT="${AKO_LIMIT:-0}"
START_INDEX="${AKO_START_INDEX:-0}"
DECODE_TOKENS="${AKO_DECODE_TOKENS:-8}"
OUT_DIR="${AKO_OUT_DIR:-}"
PHONE_BASE="${AKO_QWEN2_PHONE_BASE:-/data/local/tmp/qwen2_moe_td_w8a16_clean_20260527}"
PHONE_LOG="${AKO_QWEN2_PHONE_LOG:-qwen2_td_qnn_mobile_moe_ako.log}"
PROMPT_TEXT="${AKO_PROMPT:-}"
PROMPT_ROW_JSON="{}"
RUNNER="${AKO_QWEN2_RUNNER:-mllm-qwen2-moe-td-qnn-aot-runner}"
TIMEOUT_S="${AKO_BACKEND_TIMEOUT:-900}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --serial)
      SERIAL="$2"
      shift 2
      ;;
    --decode-tokens)
      DECODE_TOKENS="$2"
      shift 2
      ;;
    --dataset)
      DATASET="$2"
      shift 2
      ;;
    --limit)
      LIMIT="$2"
      shift 2
      ;;
    --start-index)
      START_INDEX="$2"
      shift 2
      ;;
    --out-dir)
      OUT_DIR="$2"
      shift 2
      ;;
    --repeats|--local-runner|--push-runner|--preload-top-n|--global-cache-budget-mb|--mmap-only|--diag|--no-prefetch|--no-mbm-prefetch|--force-decode|--force-gguf-dequant-f32|--idle-seconds|--sleep-between-runs-s|--cooldown-max-wait-s)
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

if [[ -z "${OUT_DIR}" ]]; then
  OUT_DIR="$(pwd)/results/runs/qwen2_td_qnn_$(date +%Y%m%d_%H%M%S)"
fi

if [[ -z "${PROMPT_TEXT}" && -n "${DATASET}" && -f "${DATASET}" ]]; then
  PROMPT_ROW_JSON="$(
    python3 - "${DATASET}" "${START_INDEX}" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
start = int(sys.argv[2])
rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
if start < 0 or start >= len(rows):
    raise SystemExit(f"start-index {start} out of range for {path} ({len(rows)} rows)")
print(json.dumps(rows[start], ensure_ascii=False))
PY
  )"
  PROMPT_TEXT="$(
    python3 - "${PROMPT_ROW_JSON}" <<'PY'
import json
import sys
print(json.loads(sys.argv[1]).get("prompt", ""))
PY
  )"
fi

if [[ -z "${PROMPT_TEXT}" ]]; then
  PROMPT_TEXT="hello"
fi

mkdir -p "${OUT_DIR}/logs" "${OUT_DIR}/prompts"
LOCAL_LOG="${OUT_DIR}/logs/qwen2_td_qnn.log"
LOCAL_STDOUT="${OUT_DIR}/logs/qwen2_td_qnn.adb_stdout.log"
SUMMARY_JSONL="${OUT_DIR}/summary.jsonl"
REMOTE_SCRIPT_LOCAL="${OUT_DIR}/logs/qwen2_td_qnn_remote.sh"
REMOTE_SCRIPT_NAME="mobile_moe_ako_qwen2_td_qnn.sh"
PROMPT_ESCAPED="${PROMPT_TEXT//\'/\'\\\'\'}"

printf '%s\n' "${PROMPT_TEXT}" > "${OUT_DIR}/prompts/qwen2_td_qnn.txt"

cat > "${REMOTE_SCRIPT_LOCAL}" <<EOF
#!/system/bin/sh
cd '${PHONE_BASE}' || exit 127
log='${PHONE_LOG}'
rm -f "\$log"
export LD_LIBRARY_PATH=.
export ADSP_LIBRARY_PATH="${PHONE_BASE};${PHONE_BASE}/;/vendor/lib64/rfs/dsp;/vendor/dsp/cdsp;/vendor/dsp"
export MLLM_QNN_TD_LOG_TOKEN_TEXT=0
unset MLLM_QNN_TD_LOG_TOKENS
export MLLM_QNN_TD_RAW_PROMPT=1
export MLLM_QNN_TD_TIMING=0
export MLLM_QNN_TD_LOG_ROUTING_SUMMARY=0
export MLLM_QNN_TD_SG0_PREEMBED=1
export MLLM_QNN_TD_EXTERNAL_LM_HEAD=1
export MLLM_QNN_TD_SHARED_EXPERT_GPU=1
export MLLM_QNN_AOT_SKIP_SHARED_EXPERT=1
export MLLM_QNN_TD_ASYNC_CONTEXT_RETRIEVE=1
export MLLM_QNN_TD_ASYNC_CONTEXT_RETRIEVE_WRAP=1
export MLLM_QNN_TD_ASYNC_CONTEXT_PRELOAD_LOOKAHEAD=2
export MLLM_QNN_TD_ASYNC_CONTEXT_PRELOAD_SLOTS=4
export MLLM_QNN_TD_HYBRID_NPU_GPU_CPU=1
export MLLM_QNN_TD_HYBRID_GPU_FULL_MOE=1
export MLLM_QNN_TD_HYBRID_COLD_FULL_GPU=1
export MLLM_QNN_TD_HYBRID_COLD_DELTA_INPUT=1
export MLLM_QNN_TD_HYBRID_GPU_COLD_DELTA=1
export MLLM_QNN_TD_HYBRID_COLD_FINAL_GPU=1
export MLLM_QNN_TD_HYBRID_GPU_ASYNC_PREWARM=1
export MLLM_QNN_TD_HYBRID_GPU_ASYNC_PREWARM_DECODE=1
export MLLM_QNN_TD_HYBRID_GPU_ASYNC_PREWARM_FACTORS=1
export MLLM_QNN_TD_HYBRID_GPU_PREWARM_LOW_PRIORITY=1
export MLLM_QNN_TD_HYBRID_GPU_PREWARM_NO_EVICT=1
export MLLM_QNN_TD_HYBRID_GPU_FACTOR_CACHE_BUDGET_MIB=1600
export MLLM_QNN_TD_HYBRID_GPU_KEEP_FACTOR_LAYERS=28
export MLLM_QNN_TD_SHARED_EXPERT_GPU_FACTOR_CACHE_BUDGET_MIB=1280
export MLLM_QNN_TD_SHARED_EXPERT_GPU_KEEP_FACTOR_LAYERS=10
export MLLM_QNN_TD_SHARED_EXPERT_GPU_PIN_LAYERS=10
export MLLM_QNN_TD_SHARED_EXPERT_GPU_PIN_POLICY=uniform
export MLLM_QNN_TD_SHARED_EXPERT_GPU_ARENA_LAYERS=10
export MLLM_QNN_TD_SHARED_EXPERT_GPU_PREFETCH_WINDOW=1
export MLLM_QNN_TD_SHARED_EXPERT_GPU_SEPARATE_EXECUTOR=1
export MLLM_QNN_TD_HYBRID_GPU_PACKED_PAYLOAD_ARENA=1
export MLLM_QNN_TD_HYBRID_GPU_EXPERT_MISS_FULL=1
export MLLM_QNN_TD_HYBRID_GPU_EXPERT_PAYLOAD_ARENA=1
export MLLM_QNN_TD_HYBRID_GPU_CORE_PAGE_TOUCH_MODE=2
export MLLM_QNN_TD_HYBRID_GPU_CORE_HOST_RETAINED=0
export MLLM_QNN_TD_HYBRID_GPU_CORE_STAGED_UPLOAD=0
export MLLM_QNN_TD_HYBRID_GPU_CACHE_CAPACITY=8
export MLLM_QNN_TD_HYBRID_GPU_MAX_BATCH=8
export MLLM_QNN_TD_HYBRID_GPU_AUTO_ARENA_CAPACITY=0
export MLLM_QNN_TD_HYBRID_GPU_REQUIRED_BATCH_UPLOAD_EXPERTS=8
export MLLM_QNN_TD_HYBRID_GPU_NEXT_LAYER_PREWARM=0
export MLLM_QNN_TD_HYBRID_GPU_HOT_RESIDENT_CORE=1
export MLLM_QNN_TD_HYBRID_GPU_CORE_OPENCL_WINDOW=28
export MLLM_QNN_TD_HYBRID_GPU_CORE_ARENA_BUDGET_MIB=3072
export MLLM_QNN_TD_HYBRID_GPU_HOT_RESIDENT_WINDOW=32
export MLLM_QNN_TD_HYBRID_GPU_HOT_RESIDENT_MIN_HITS=1
export MLLM_QNN_TD_HYBRID_GPU_PREWARM_MAX_EXPERTS=4
export MLLM_QNN_TD_HYBRID_GPU_ASYNC_PREWARM_CANDIDATES=16
printf '%s\nexit\n' '${PROMPT_ESCAPED}' | ./${RUNNER} \\
  -m "" \\
  -b . \\
  -t qwen2-tokenizer.json \\
  -c config_57B_A14B.json \\
  -td global_rank_allocation.json \\
  --context_len 384 \\
  --ar_len 1 \\
  --max_new_tokens ${DECODE_TOKENS} \\
  --embed_tokens_bin embed_tokens.bin \\
  --embed_tokens_index embed_tokens_index.json \\
  --lm_head_bin lm_head.bin \\
  --lm_head_index lm_head_index.json \\
  --expert_cores_gpu_v3_layer_dir_pattern "gpu_v3_scale12_layers_expertpayload_only/layer{layer}" \\
  --td_factors_layer_dir_pattern "td_factors_lpbq_int4_layers/layer{layer}" \\
  --shared_expert_layer_dir_pattern "shared_mnn_w4_layers/layer{layer}" \\
  --moe_gate_bin moe_gate_weights.bin \\
  --moe_gate_index moe_gate_weights_index.json \\
  > "\$log" 2>&1
echo RET:\$? >> "\$log"
grep -aE "Prefill|Decode|Generated tokens|Hybrid GPU shadow|External lm_head|RET:|Response|ERROR|Error|QNN|Backend created|Device created|Loaded context" "\$log" | tail -n 160
EOF

adb -s "${SERIAL}" shell "mkdir -p '${PHONE_BASE}'"
adb -s "${SERIAL}" push "${REMOTE_SCRIPT_LOCAL}" "${PHONE_BASE}/${REMOTE_SCRIPT_NAME}" >/dev/null
adb -s "${SERIAL}" shell "chmod +x '${PHONE_BASE}/${REMOTE_SCRIPT_NAME}'"

set +e
timeout "${TIMEOUT_S}" adb -s "${SERIAL}" shell "cd '${PHONE_BASE}' && sh './${REMOTE_SCRIPT_NAME}'" > "${LOCAL_STDOUT}" 2>&1
ADB_STATUS=$?
adb -s "${SERIAL}" pull "${PHONE_BASE}/${PHONE_LOG}" "${LOCAL_LOG}" >/dev/null 2>&1
set -e

cat "${LOCAL_STDOUT}"

python3 - "${LOCAL_LOG}" "${SUMMARY_JSONL}" "${SERIAL}" "${PHONE_BASE}/${PHONE_LOG}" "${ADB_STATUS}" "${DECODE_TOKENS}" "${PROMPT_ROW_JSON}" <<'PY'
import json
import math
import re
import sys
from pathlib import Path

log_path = Path(sys.argv[1])
summary_path = Path(sys.argv[2])
serial = sys.argv[3]
phone_log = sys.argv[4]
adb_status = int(sys.argv[5])
decode_tokens_requested = int(sys.argv[6])
prompt_row = json.loads(sys.argv[7]) if len(sys.argv) > 7 and sys.argv[7].strip() else {}
text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
KV_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)")

def num(pattern):
    m = re.search(pattern, text, re.I)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None

def parse_value(raw):
    value = raw.rstrip(",")
    for suffix in ("MiB", "KiB", "ms"):
        if value.endswith(suffix):
            value = value[: -len(suffix)]
            break
    try:
        if re.fullmatch(r"[-+]?\d+", value):
            return int(value)
        if re.fullmatch(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)", value):
            return float(value)
    except ValueError:
        pass
    return raw

def add_kvs(out, prefix, kv_text):
    for key, raw_value in KV_RE.findall(kv_text):
        value = parse_value(raw_value)
        if isinstance(value, (int, float)) and math.isfinite(float(value)):
            out[f"{prefix}_{key}"] = value

ret_matches = re.findall(r"RET:(-?\d+)", text)
ret = int(ret_matches[-1]) if ret_matches else None
generated = num(r"Generated tokens\s*:\s*(\d+)")
decode_s = None
decode_tok_s = None
m = re.search(r"Decode(?:\s+time)?\s*:\s*([-+0-9.]+)\s*(?:us|µs|μs)\s*\(\s*([-+0-9.]+)\s+(?:tok/s|tokens/s)\s*\)", text, re.I)
if m:
    decode_s = float(m.group(1)) / 1_000_000.0
    decode_tok_s = float(m.group(2))
else:
    avg_ms = num(r"Avg decode time\s*:\s*([-+0-9.]+)\s*(?:ms|milliseconds)")
    if avg_ms and avg_ms > 0:
        decode_tok_s = 1000.0 / avg_ms
        if generated:
            decode_s = generated / decode_tok_s
if generated and decode_s and not decode_tok_s:
    decode_tok_s = generated / decode_s

prefill_s = None
prefill_us = num(r"Prefill(?:\s+time)?\s*:\s*([-+0-9.]+)\s*(?:us|µs|μs)")
if prefill_us is not None:
    prefill_s = prefill_us / 1_000_000.0

hybrid = {}
hybrid_matches = re.findall(r"Hybrid GPU shadow\s*:\s*(.*)", text)
if hybrid_matches:
    add_kvs(hybrid, "hybrid", hybrid_matches[-1])

row = {
    "baseline": "qwen2_td_qnn",
    "run_id": "qwen2_td_qnn_once",
    "id": prompt_row.get("id"),
    "category": prompt_row.get("category"),
    "source": prompt_row.get("source"),
    "source_idx": prompt_row.get("source_idx"),
    "prompt_tokens_dataset": prompt_row.get("prompt_tokens"),
    "serial": serial,
    "adb_status": adb_status,
    "ret": ret,
    "generated": int(generated) if generated is not None and math.isfinite(generated) else None,
    "decode_tokens_requested": decode_tokens_requested,
    "decode_s": decode_s,
    "decode_tok_s": decode_tok_s,
    "prefill_s": prefill_s,
    "phone_log": phone_log,
    "local_log": str(log_path),
}
row.update(hybrid)
generated_i = row.get("generated")
if generated_i:
    core_up = row.get("hybrid_core_up")
    req_mat_mib = row.get("hybrid_req_mat_mib")
    req_service = row.get("hybrid_req_service")
    if isinstance(core_up, (int, float)):
        row["uploaded_expert_mib_per_token_metric"] = float(core_up) / generated_i
    if isinstance(req_mat_mib, (int, float)):
        row["required_miss_mib_per_token_metric"] = float(req_mat_mib) / generated_i
    if isinstance(req_service, (int, float)):
        row["required_miss_service_ms_per_token_metric"] = float(req_service) / generated_i
req_hit = row.get("hybrid_req_hit")
req_miss = row.get("hybrid_req_miss")
if isinstance(req_hit, (int, float)) and isinstance(req_miss, (int, float)) and req_hit + req_miss > 0:
    row["metric_required_hit_rate"] = float(req_hit) / (float(req_hit) + float(req_miss))
pre_hit = row.get("hybrid_pre_hit")
pre_miss = row.get("hybrid_pre_miss")
if isinstance(pre_hit, (int, float)) and isinstance(pre_miss, (int, float)) and pre_hit + pre_miss > 0:
    row["hybrid_pre_hit_rate"] = float(pre_hit) / (float(pre_hit) + float(pre_miss))
summary_path.parent.mkdir(parents=True, exist_ok=True)
summary_path.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
PY

RET="$(python3 - "${SUMMARY_JSONL}" <<'PY'
import json, sys
row = json.loads(open(sys.argv[1], encoding="utf-8").readline())
print(row.get("ret") if row.get("ret") is not None else "")
PY
)"

if [[ "${ADB_STATUS}" -ne 0 ]]; then
  exit 1
fi
if [[ -n "${RET}" && "${RET}" -ne 0 ]]; then
  exit 1
fi
