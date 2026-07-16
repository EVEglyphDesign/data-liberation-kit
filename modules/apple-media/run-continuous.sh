#!/usr/bin/env bash
# Wrapper for run-continuous.py so peers can `./modules/apple-media/run-continuous.sh`.
set -euo pipefail
DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
exec python3 "${DIR}/run-continuous.py" "$@"
