#!/usr/bin/env bash
set -euo pipefail
src="${1:?Usage: audit-source.sh /path/to/extracted/php-source}"
for f in Zend/zend_alloc.c Zend/zend_execute_API.c Zend/zend_llist.c ext/session/session.c main/SAPI.c main/main.c main/rfc1867.c; do
 test -f "$src/$f" || { echo "Missing: $src/$f" >&2; exit 1; }
 echo "===== $f ====="
 grep -nE 'shutdown_executor|zend_mm|multipart|upload_progress|content_type_dup|sapi_deactivate|php_request_shutdown|zend_llist' "$src/$f" | head -n 30 || true
done
