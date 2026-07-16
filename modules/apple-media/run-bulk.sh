#!/usr/bin/env bash
# Apple media bulk off-ramp via USB (libimobiledevice).
#
# Pulls the full photo/video archive off a connected iPhone into the repo,
# converts HEIC/HEVC to open formats (originals preserved), and emits
# manifest entries.
#
# Requires libimobiledevice + ideviceinfo + idevicebackup2 on PATH.
# Requires ImageMagick and ffmpeg for the format conversion pass.

set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." &> /dev/null && pwd)"
STAGING="${REPO_ROOT}/.liberation-kit/staging/apple-bulk-$(date -u +%Y%m%dT%H%M%SZ)"
CONFIG="${REPO_ROOT}/.liberation-kit/config.yaml"

log() { printf '%s %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*"; }
die() { log "ERROR: $*" >&2; exit 1; }

require() { command -v "$1" &>/dev/null || die "missing binary: $1 (install libimobiledevice/ImageMagick/ffmpeg)"; }
require ideviceinfo
require idevicebackup2
require magick || require convert
require ffmpeg
require python3
require jq

log "detecting connected device..."
DEVICE_UDID="$(ideviceinfo -k UniqueDeviceID 2>/dev/null || true)"
[ -n "${DEVICE_UDID}" ] || die "no device detected. Plug in your iPhone and trust this computer."

DEVICE_NAME="$(ideviceinfo -k DeviceName 2>/dev/null || echo unknown)"
log "device: ${DEVICE_NAME} (${DEVICE_UDID})"

if [ -f "${CONFIG}" ]; then
    REQUIRE_CONFIRM="$(python3 -c "import yaml,sys; print(yaml.safe_load(open('${CONFIG}')).get('apple-media',{}).get('bulk',{}).get('require_confirmation',True))")"
    if [ "${REQUIRE_CONFIRM}" = "True" ]; then
        read -r -p "Pull full archive from ${DEVICE_NAME}? [y/N] " ans
        [ "${ans:-N}" = "y" ] || [ "${ans:-N}" = "Y" ] || { log "aborted"; exit 0; }
    fi
fi

mkdir -p "${STAGING}"
log "staging into ${STAGING}"

log "running idevicebackup2 backup..."
idevicebackup2 backup --full "${STAGING}" || die "backup failed"

log "extracting media assets via afc-mount..."
python3 "$(dirname -- "${BASH_SOURCE[0]}")/bulk-extract.py" \
    --staging "${STAGING}" \
    --repo-root "${REPO_ROOT}" \
    --device-udid "${DEVICE_UDID}"

log "converting HEIC -> JPEG and HEVC -> MP4 where configured..."
python3 "$(dirname -- "${BASH_SOURCE[0]}")/convert-formats.py" \
    --repo-root "${REPO_ROOT}"

log "done. Staging can be removed: rm -rf ${STAGING}"
