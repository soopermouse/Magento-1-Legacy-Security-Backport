#!/usr/bin/env bash
set -euo pipefail
BASE="${1:-http://127.0.0.1:8080}"; BASE="${BASE%/}"
case "$BASE" in http://127.0.0.1:*|http://localhost:*|http://\[::1\]:*) ;; *) echo 'ERROR: loopback URL required' >&2; exit 2;; esac
command -v curl >/dev/null || { echo 'curl missing' >&2; exit 2; }
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
printf 'upload-smoke' > "$TMP/test.txt"
echo '[1] Apache runtime (must report apache2handler)'
curl --fail --silent --show-error --max-time 15 "$BASE/runtime-probe.php" | tee "$TMP/runtime.json"; echo
if ! grep -q '"sapi":"apache2handler"' "$TMP/runtime.json"; then echo 'FAIL: not mod_php apache2handler' >&2; exit 1; fi
if ! grep -q '"max_multipart_body_parts"' "$TMP/runtime.json"; then echo 'FAIL: INI key missing' >&2; exit 1; fi
if grep -q '"max_multipart_body_parts":null' "$TMP/runtime.json"; then echo 'FAIL: INI entry unavailable' >&2; exit 1; fi
echo '[2] Normal multipart upload'
curl --fail --silent --show-error --max-time 15 -F "sample=@$TMP/test.txt" "$BASE/upload-probe.php" | tee "$TMP/upload.json"; echo
if ! grep -q '"is_uploaded":true' "$TMP/upload.json"; then echo 'FAIL: upload not accepted' >&2; exit 1; fi
echo 'PASS: mod_php identification, INI registration and normal upload'
