#!/usr/bin/env bash
set -euo pipefail
# Produce a branch-native, zero-fuzz-applicable unified diff from a clean source tree.
if [[ $# -ne 3 ]]; then echo "Usage: $0 <5.5.38|5.6.40> <clean-source> <output.patch>" >&2; exit 2; fi
branch=$1; source=$(realpath "$2"); output=$(realpath -m "$3")
case "$branch" in 5.5.38|5.6.40) ;; *) echo "Unsupported branch" >&2; exit 2;; esac
[[ -f "$source/main/php_version.h" && -f "$source/main/SAPI.c" ]] || { echo "Source missing" >&2; exit 2; }
[[ ! -e "$output" ]] || { echo "Output exists; refusing overwrite" >&2; exit 2; }
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
# Work on a copy only; do not touch original source.
mkdir "$tmp/tree"
cp -a "$source/." "$tmp/tree/"
cd "$tmp/tree"
# Never include existing repository metadata or build artifacts in the generated diff.
rm -rf .git
if find . -name '*.rej' -o -name '*.orig' | grep -q .; then echo "Source has patch artifacts" >&2; exit 1; fi
python3 "$root/scripts/rebase-local-source.py" --source "$source" --branch "$branch" --output "$tmp/sapi.patch"
git init -q
git -c core.autocrlf=false add -A
git -c user.name='Patch Builder' -c user.email='builder@localhost' commit -qm baseline
patch --batch --no-backup-if-mismatch -p1 < "$root/reference/php54-security-non-sapi-non-ini.patch" > "$tmp/common-apply.log"
patch --batch --fuzz=0 -p1 < "$tmp/sapi.patch" > "$tmp/sapi-apply.log"
if find . -name '*.rej' -o -name '*.orig' | grep -q .; then echo "Patch rejects or backups detected" >&2; exit 1; fi
# Emit exact before/after context, no reliance on patch fuzz during future installs.
git diff --no-ext-diff --binary HEAD > "$tmp/native.patch"
[[ -s "$tmp/native.patch" ]] || { echo "Empty native patch" >&2; exit 1; }
# Verify the output against the exact source snapshot with zero-fuzz semantics.
mkdir "$tmp/verify"
cp -a "$source/." "$tmp/verify/"
cd "$tmp/verify"
git apply --check "$tmp/native.patch"
git apply "$tmp/native.patch"
for file in $(cd "$tmp/tree" && git diff --name-only HEAD); do
  cmp "$tmp/tree/$file" "$tmp/verify/$file" || { echo "Verification mismatch: $file" >&2; exit 1; }
done
mkdir -p "$(dirname "$output")"
cp "$tmp/native.patch" "$output"
echo "Generated and verified native patch: $output"
echo "Source-specific patch: review hunks, archive source commit and hashes, then run regression tests."
