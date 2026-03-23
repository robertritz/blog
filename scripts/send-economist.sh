#!/bin/bash
# Send The Economist to Kindle via email
# Downloads the latest Calibre recipe from GitHub, converts to EPUB, and emails it.
#
# Required environment variables:
#   SMTP_HOST     - SMTP server (e.g. smtp.gmail.com)
#   SMTP_PORT     - SMTP port (e.g. 587)
#   SMTP_USER     - SMTP username/email
#   SMTP_PASS     - SMTP password / app password
#   KINDLE_EMAIL  - Destination email (e.g. user@kindle.com)
#
# Prerequisites: calibre must be installed (provides ebook-convert and calibre-smtp)

set -euo pipefail

WORK_DIR=$(mktemp -d)
RECIPE_URL="https://raw.githubusercontent.com/kovidgoyal/calibre/master/recipes/economist.recipe"

cleanup() {
    rm -rf "$WORK_DIR"
}
trap cleanup EXIT

echo "$(date): Starting Economist download..."

# Download fresh recipe from Calibre GitHub repo
echo "Downloading latest Economist recipe..."
curl -sL "$RECIPE_URL" -o "$WORK_DIR/economist.recipe"

# Convert recipe to EPUB
OUTPUT="$WORK_DIR/The_Economist_$(date +%Y-%m-%d).epub"
echo "Fetching and converting The Economist to EPUB..."
ebook-convert "$WORK_DIR/economist.recipe" "$OUTPUT" 2>&1

if [ ! -f "$OUTPUT" ]; then
    echo "ERROR: Conversion failed, no output file produced."
    exit 1
fi

FILE_SIZE=$(du -h "$OUTPUT" | cut -f1)
echo "Conversion complete: $OUTPUT ($FILE_SIZE)"

# Send via email using calibre-smtp
echo "Sending to $KINDLE_EMAIL via $SMTP_HOST..."
calibre-smtp \
    --relay "$SMTP_HOST" \
    --port "$SMTP_PORT" \
    --username "$SMTP_USER" \
    --password "$SMTP_PASS" \
    --encryption-method TLS \
    --subject "The Economist - $(date +%Y-%m-%d)" \
    --attachment "$OUTPUT" \
    "$SMTP_USER" \
    "$KINDLE_EMAIL" \
    "The Economist - $(date +%Y-%m-%d)"

echo "$(date): Done! The Economist sent to $KINDLE_EMAIL"
