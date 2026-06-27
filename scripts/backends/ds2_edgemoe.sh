#!/usr/bin/env bash
set -euo pipefail

TUCKER_ROOT="${AKO_TUCKER_ROOT:-/home/liuxu/projects/tucker}"
RUNNER_SCRIPT="${AKO_RUNNER_SCRIPT:-${TUCKER_ROOT}/scripts/run_ds2_edgemoe_end2end.py}"
PYTHON_BIN="${AKO_BACKEND_PYTHON:-${AKO_PYTHON:-${TUCKER_ROOT}/tucker_env/bin/python}}"

if [[ "${PYTHON_BIN}" == */* && ! -x "${PYTHON_BIN}" ]]; then
  PYTHON_BIN="python3"
fi

if [[ ! -f "${RUNNER_SCRIPT}" ]]; then
  echo "[ds2_edgemoe] missing runner: ${RUNNER_SCRIPT}" >&2
  exit 1
fi

exec "${PYTHON_BIN}" "${RUNNER_SCRIPT}" "$@"
