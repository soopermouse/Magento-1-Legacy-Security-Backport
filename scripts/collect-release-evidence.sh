#!/usr/bin/env bash
set -euo pipefail
# Collects local build metadata only; does not access Magento credentials or live sites.
if [ "$#" -ne 3 ]; then echo "Usage: $0 <php-binary> <5.5.38|5.6.40> <output-directory>" >&2; exit 2; fi
PHP_BIN="$1"; EXPECTED="$2"; OUT="$3"
case "$EXPECTED" in 5.5.38|5.6.40) ;; *) echo 'Unsupported baseline' >&2; exit 2;; esac
[ -x "$PHP_BIN" ] || { echo 'PHP binary not executable' >&2; exit 2; }
ACTUAL="$("$PHP_BIN" -r 'echo PHP_VERSION;')"
[ "$ACTUAL" = "$EXPECTED" ] || { echo "Wrong PHP version: $ACTUAL" >&2; exit 1; }
[ ! -e "$OUT" ] || { echo 'Output already exists; refusing overwrite' >&2; exit 2; }
mkdir -m 700 -p "$OUT"
"$PHP_BIN" -v > "$OUT/php-version.txt"
"$PHP_BIN" -m > "$OUT/php-modules.txt"
"$PHP_BIN" -r 'echo "sapi=",PHP_SAPI,"\n", "php_version=",PHP_VERSION,"\n", "multipart_ini=",var_export(ini_get("max_multipart_body_parts"),true),"\n";' > "$OUT/runtime-summary.txt"
# Do not collect php -i, environment, php.ini, Magento local.xml, or authentication material.
( cd "$OUT"; sha256sum php-version.txt php-modules.txt runtime-summary.txt > SHA256SUMS )
echo "Collected sanitized CLI evidence: $OUT"
echo 'Note: CLI evidence cannot satisfy the Apache/mod_php or Magento release gates.'
