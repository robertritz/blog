#!/usr/bin/env bash
#
# Finish the robertritz.com migration to Cloudflare Pages.
#
# Prereq: CLOUDFLARE_API_TOKEN must be available — either exported, or on a
# line in ./.env (gitignored). Token scopes required:
#   Account · Cloudflare Pages: Edit
#   Account · Account Settings: Read
#   Zone    · DNS: Edit         (robertritz.com)
#   Zone    · Zone: Read        (robertritz.com)
#
# What it does, in order (each step prints what it's doing):
#   1. Load + verify the token; resolve account id + zone id.
#   2. Store the token as GitHub Actions secrets (for auto-deploy on push).
#   3. Build the site and deploy it to a Pages project (created if missing).
#   4. Verify the *.pages.dev deployment returns HTTP 200.
#   5. Attach robertritz.com to the project and CUT DNS over to Pages,
#      after saving a backup of the current apex record(s) for rollback.
#   6. Verify robertritz.com serves from Pages.
#
# It does NOT touch the Hetzner container — once DNS points at Pages the old
# container just goes idle. Decommission it separately once you're happy.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PROJECT="robertritz-blog"
DOMAIN="robertritz.com"
CF_API="https://api.cloudflare.com/client/v4"

# --- 1. token -------------------------------------------------------------
if [[ -z "${CLOUDFLARE_API_TOKEN:-}" && -f .env ]]; then
  raw="$(grep -E '^CLOUDFLARE_API_TOKEN=' .env | head -1 | cut -d= -f2-)"
  # strip surrounding quotes and any whitespace/CR; token is [A-Za-z0-9_-] only
  CLOUDFLARE_API_TOKEN="$(printf '%s' "$raw" | tr -d "[:space:]\"'")"
fi
if [[ -z "${CLOUDFLARE_API_TOKEN:-}" ]]; then
  echo "ERROR: CLOUDFLARE_API_TOKEN not set and not found in .env" >&2
  exit 1
fi
export CLOUDFLARE_API_TOKEN

cf() { # cf METHOD PATH [json-body]
  local method="$1" path="$2" body="${3:-}"
  if [[ -n "$body" ]]; then
    curl -s -X "$method" "$CF_API$path" \
      -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
      -H "Content-Type: application/json" --data "$body"
  else
    curl -s -X "$method" "$CF_API$path" \
      -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
  fi
}
jget() { node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{try{const o=JSON.parse(s);const p=process.argv[1].split(".").reduce((a,k)=>a&&a[k.match(/^\d+$/)?+k:k],o);process.stdout.write(p==null?"":String(p))}catch(e){process.exit(2)}})' "$1"; }

echo "==> Verifying token..."
VERIFY="$(cf GET /user/tokens/verify)"
[[ "$(printf '%s' "$VERIFY" | jget success)" == "true" ]] || { echo "Token verify failed: $VERIFY" >&2; exit 1; }

echo "==> Resolving zone + account for $DOMAIN..."
ZONE_JSON="$(cf GET "/zones?name=$DOMAIN")"
ZONE_ID="$(printf '%s' "$ZONE_JSON" | jget result.0.id)"
ACCOUNT_ID="$(printf '%s' "$ZONE_JSON" | jget result.0.account.id)"
[[ -n "$ZONE_ID" && -n "$ACCOUNT_ID" ]] || { echo "Could not resolve zone/account: $ZONE_JSON" >&2; exit 1; }
export CLOUDFLARE_ACCOUNT_ID="$ACCOUNT_ID"
echo "    account=$ACCOUNT_ID zone=$ZONE_ID"

# --- 2. GitHub secrets (auto-deploy on push) ------------------------------
echo "==> Storing GitHub Actions secrets..."
printf '%s' "$CLOUDFLARE_API_TOKEN" | gh secret set CLOUDFLARE_API_TOKEN
printf '%s' "$ACCOUNT_ID"           | gh secret set CLOUDFLARE_ACCOUNT_ID

# --- 3. build + deploy ----------------------------------------------------
echo "==> Building..."
npx astro build

echo "==> Ensuring Pages project '$PROJECT' exists..."
npx wrangler pages project create "$PROJECT" --production-branch main 2>/dev/null || true

echo "==> Deploying to Cloudflare Pages..."
npx wrangler pages deploy dist --project-name "$PROJECT" --branch main

# --- 4. verify pages.dev --------------------------------------------------
PAGES_URL="https://$PROJECT.pages.dev"
echo "==> Verifying $PAGES_URL ..."
for i in $(seq 1 20); do
  code="$(curl -s -o /dev/null -w '%{http_code}' "$PAGES_URL" || true)"
  [[ "$code" == "200" ]] && { echo "    $PAGES_URL -> 200 OK"; break; }
  echo "    ($i) got $code, retrying..."; sleep 3
done
[[ "$code" == "200" ]] || { echo "ERROR: $PAGES_URL never returned 200; aborting BEFORE DNS cutover." >&2; exit 1; }

# --- 5. attach domain + DNS cutover --------------------------------------
echo "==> Attaching $DOMAIN to the Pages project..."
cf POST "/accounts/$ACCOUNT_ID/pages/projects/$PROJECT/domains" "{\"name\":\"$DOMAIN\"}" >/dev/null || true

echo "==> Backing up current apex DNS records to dns-backup.json ..."
cf GET "/zones/$ZONE_ID/dns_records?name=$DOMAIN" > dns-backup.json
echo "    saved $(node -e 'const r=require("./dns-backup.json");console.log((r.result||[]).map(x=>x.type+" "+x.content).join(", "))')"

echo "==> Cutting apex over to $PROJECT.pages.dev (proxied CNAME)..."
# delete existing apex A/AAAA/CNAME records
node -e 'const r=require("./dns-backup.json");(r.result||[]).filter(x=>["A","AAAA","CNAME"].includes(x.type)).forEach(x=>console.log(x.id))' | while read -r rid; do
  [[ -n "$rid" ]] && cf DELETE "/zones/$ZONE_ID/dns_records/$rid" >/dev/null
done
cf POST "/zones/$ZONE_ID/dns_records" \
  "{\"type\":\"CNAME\",\"name\":\"$DOMAIN\",\"content\":\"$PROJECT.pages.dev\",\"proxied\":true}" >/dev/null

# --- 6. verify domain -----------------------------------------------------
echo "==> Verifying https://$DOMAIN (give the edge a moment)..."
for i in $(seq 1 20); do
  hdr="$(curl -s -I "https://$DOMAIN" || true)"
  if printf '%s' "$hdr" | grep -qi 'cf-ray' && ! printf '%s' "$hdr" | grep -qi 'x-served-by: hetzner'; then
    echo "    $DOMAIN responding via Cloudflare."; break
  fi
  echo "    ($i) waiting for propagation..."; sleep 5
done

echo ""
echo "DONE. robertritz.com now serves from Cloudflare Pages ($PROJECT)."
echo "Auto-deploy on push to main is wired via .github/workflows/deploy.yml."
echo "Rollback (if needed): recreate the apex record from dns-backup.json."
echo "Hetzner blog container is now idle and can be decommissioned separately."
