#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}>>> Starting Build Process...${NC}"

PROJECT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$PROJECT_DIR"

if [[ -n "${1:-}" ]]; then
  if [[ -f "$1" ]]; then
    echo -e "${YELLOW}>>> Updating offline HTML fallback...${NC}"
    mkdir -p Resources
    cp "$1" Resources/index.html
    echo -e "${GREEN}>>> Successfully copied $1 to Resources/index.html${NC}"
  else
    echo -e "${RED}>>> Warning: File '$1' not found. Skipping HTML update.${NC}"
  fi
fi

: "${THEOS:?Error: Set THEOS to your Theos installation directory first (e.g., export THEOS=\$HOME/theos).}"

echo -e "${YELLOW}>>> Cleaning previous builds...${NC}"
make clean

echo -e "${YELLOW}>>> Building DEB Package (make package)...${NC}"
make package

echo -e "${YELLOW}>>> Building and Verifying IPA (make ipa)...${NC}"
make verify-ipa SIGN_IDENTITY="${SIGN_IDENTITY:-}" PROVISIONING_PROFILE="${PROVISIONING_PROFILE:-}"

echo -e "${GREEN}====================================================${NC}"
echo -e "${GREEN}✅ Finished! Check the 'packages/' folder for DEB and IPA.${NC}"
echo -e "${GREEN}====================================================${NC}"
