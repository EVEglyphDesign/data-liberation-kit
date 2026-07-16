#!/usr/bin/env bash
# First-run setup for data-liberation-kit.
#
# Asks the user three questions, writes .liberation-kit/config.yaml,
# initialises the credential store, and installs dependencies for the
# selected modules.

set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." &> /dev/null && pwd)"
CONFIG_DIR="${REPO_ROOT}/.liberation-kit"
CONFIG_FILE="${CONFIG_DIR}/config.yaml"

mkdir -p "${CONFIG_DIR}"

echo "data-liberation-kit — first-run setup"
echo
echo "This is a max-vector design. You don't have to use everything."
echo "Turn on the modules you want, ignore the rest."
echo

# Q1: which modules
declare -A MODULES=(
    [apple-media]="Apple photos and videos off-ramp"
    [google-media]="Google Photos parallel path"
    [llm-history]="LLM chat-history export (ChatGPT, Claude, Perplexity, Copilot, Gemini)"
)

echo "1) Which modules do you want on?"
enabled_modules=()
for key in "${!MODULES[@]}"; do
    read -r -p "   ${key} — ${MODULES[$key]}. Enable? [Y/n] " ans
    if [ "${ans:-Y}" != "n" ] && [ "${ans:-Y}" != "N" ]; then
        enabled_modules+=("${key}")
    fi
done
echo

# Q2: storage target
echo "2) Where should your data land?"
echo "   1. GitHub-LFS (your own private repo)"
echo "   2. S3-compatible bucket (AWS S3 / Cloudflare R2 / Backblaze B2 / MinIO)"
echo "   3. Local NAS or folder + GitHub index"
read -r -p "   Choice [1]: " storage_choice
storage_choice="${storage_choice:-1}"

case "${storage_choice}" in
    1) storage_target="github-lfs" ;;
    2) storage_target="s3-compatible" ;;
    3) storage_target="local-index" ;;
    *) echo "invalid choice; defaulting to github-lfs"; storage_target="github-lfs" ;;
esac
echo

# Q3: LLM binding
llm_models_json="{}"
if printf '%s\n' "${enabled_modules[@]}" | grep -q "llm-history"; then
    echo "3) Which LLMs do you want to export from?"
    for m in chatgpt claude perplexity copilot gemini; do
        read -r -p "   ${m}? [Y/n] " ans
        if [ "${ans:-Y}" != "n" ] && [ "${ans:-Y}" != "N" ]; then
            llm_models_json="${llm_models_json/\}/,\"${m}\":true\}}"
        else
            llm_models_json="${llm_models_json/\}/,\"${m}\":false\}}"
        fi
    done
    # Clean up leading comma
    llm_models_json="$(echo "${llm_models_json}" | sed 's/{,/{/')"
fi
echo

# Write config.yaml
python3 - <<PYEOF
import json, yaml, pathlib
enabled = ${#enabled_modules[@]}
mods = ${llm_models_json:-{}}
config = {}

if "apple-media" in "${enabled_modules[*]}":
    config["apple-media"] = {
        "enabled": True,
        "modes": {"continuous": True, "bulk": True},
        "formats": {"keep_originals": True, "convert_heic_to_jpg": True, "convert_hevc_to_mp4": True},
        "continuous": {"poll_interval_seconds": 300},
        "bulk": {"trigger_on_usb_connect": True, "require_confirmation": True},
    }
if "google-media" in "${enabled_modules[*]}":
    config["google-media"] = {
        "enabled": True,
        "modes": {"continuous": True, "bulk": True},
        "continuous": {"poll_interval_seconds": 900},
        "bulk": {"schedule_cron": "0 3 1 * *"},
    }
if "llm-history" in "${enabled_modules[*]}":
    config["llm-history"] = {"enabled": True, "models": mods, "schedule": "0 4 * * *"}

config["storage"] = {"target": "${storage_target}"}
config["schema_version"] = "0.1.0"

pathlib.Path("${CONFIG_FILE}").write_text(yaml.safe_dump(config, sort_keys=False))
print("wrote ${CONFIG_FILE}")
PYEOF

# Install python deps
echo "installing python dependencies..."
pip install --quiet pyyaml requests cryptography 2>/dev/null || pip3 install --quiet pyyaml requests cryptography

if printf '%s\n' "${enabled_modules[@]}" | grep -q "apple-media"; then
    pip install --quiet pyicloud 2>/dev/null || pip3 install --quiet pyicloud || true
fi
if printf '%s\n' "${enabled_modules[@]}" | grep -q "google-media"; then
    pip install --quiet playwright 2>/dev/null || pip3 install --quiet playwright || true
fi
if [ "${storage_target}" = "s3-compatible" ]; then
    pip install --quiet boto3 2>/dev/null || pip3 install --quiet boto3 || true
fi

# Initialise credential store
python3 "${REPO_ROOT}/scripts/credentials.py" --init

echo
echo "setup complete."
echo "next: run individual modules on demand, e.g."
echo "  ./modules/apple-media/run-continuous.sh"
echo "  ./modules/llm-history/run.sh"
echo
echo "or schedule them via cron/launchd/systemd — sample units in scripts/."
