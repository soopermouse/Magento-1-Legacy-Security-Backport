#!/usr/bin/env bash
set -euo pipefail
DEST="${1:-sources}"
mkdir -p "$DEST"
for row in  '5.5.38 cb527c44b48343c8557fe2446464ff1d4695155a95601083e5d1f175df95580f'  '5.6.40 1369a51eee3995d7fbd1c5342e5cc917760e276d561595b6052b21ace2656d1c'; do
 read -r version digest <<< "$row"
 filename="php-${version}.tar.xz"
 curl --fail --location --proto '=https' --tlsv1.2 --output "$DEST/$filename" "https://museum.php.net/php5/$filename"
 printf '%s  %s
' "$digest" "$DEST/$filename" | sha256sum -c -
done
printf 'Verified upstream source archives in %s
' "$DEST"
