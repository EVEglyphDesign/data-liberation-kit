#!/usr/bin/env bash
# LLM-sweep — point your configured LLM at _incoming/ and let it drop
# content into the base-model layout.
#
# The kit provides the base-model layout definition (docs/design.md) and
# the manifest schema. Your LLM applies those rules to any content it
# finds in _incoming/, producing correctly-placed files with valid
# manifest entries.
#
# This is intentionally a shell wrapper rather than a hardcoded
# implementation, because your LLM will do a better job at "figure out
# where this document belongs" than a rules engine ever will.

set -euo pipefail
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." &> /dev/null && pwd)"
INCOMING="${REPO_ROOT}/_incoming"

if [ ! -d "${INCOMING}" ] || [ -z "$(ls -A "${INCOMING}" 2>/dev/null)" ]; then
    echo "nothing to sweep. Drop content into ${INCOMING}/ first."
    exit 0
fi

echo "LLM sweep — point your LLM at the following:"
echo
echo "  Source folder:    ${INCOMING}/"
echo "  Target repo root: ${REPO_ROOT}/"
echo "  Base model:       ${REPO_ROOT}/docs/design.md"
echo "  Manifest schema:  see docs/design.md section 'Manifest schema'"
echo
echo "Ask your LLM to:"
echo "  1. Read docs/design.md so it knows the layout."
echo "  2. For each item in _incoming/, decide the correct target path under media/, history/, or interactions/."
echo "  3. Emit a valid manifest entry in the correct manifests/YYYY-MM.jsonl file."
echo "  4. Move the file (don't copy) so _incoming/ drains as the sweep progresses."
echo "  5. Preserve the original content_hash-verified fidelity."
echo
echo "The LLM does the routing. This script exists to point at the right files."
