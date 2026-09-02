#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./build.sh                              # DEB + unsigned IPA
#   SIGN_IDENTITY='Apple Development: …' PROVISIONING_PROFILE=/path/profile.mobileprovision ./build.sh
#   ./build.sh /path/to/index.html          # replace the offline fallback before building

PROJECT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$PROJECT_DIR"

if [[ -n "${1:-}" ]]; then
  cp "$1" Resources/index.html
fi

: "${THEOS:?Set THEOS to your Theos installation directory first.}"
make clean
make package
make verify-ipa SIGN_IDENTITY="${SIGN_IDENTITY:-}" PROVISIONING_PROFILE="${PROVISIONING_PROFILE:-}"

echo "Finished. See packages/ for the DEB and IPA."
