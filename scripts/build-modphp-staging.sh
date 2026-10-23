#!/usr/bin/env bash
set -euo pipefail
# Run on a disposable host with Apache development headers, build dependencies and clean PHP source.
if [[ $# -ne 4 ]]; then
  echo "Usage: $0 <5.5.38|5.6.40> <clean-source-dir> <apxs-path> <build-root>" >&2
  exit 2
fi
branch=$1; source_dir=$(realpath "$2"); apxs=$(realpath "$3"); build_root=$4
case "$branch" in 5.5.38|5.6.40) ;; *) echo "Unsupported PHP branch" >&2; exit 2;; esac
[[ -x "$apxs" && -f "$source_dir/main/SAPI.c" && -f "$source_dir/main/main.c" && -f "$source_dir/main/php_version.h" ]] || { echo "Missing apxs or source" >&2; exit 2; }
[[ ! -e "$build_root" ]] || { echo "Build root already exists; refusing overwrite" >&2; exit 2; }
# Source must be a clean checkout of the requested release.
version=$(sed -n 's/^#define PHP_VERSION "\([^"]*\)".*/\1/p' "$source_dir/main/php_version.h" | head -n 1)
[[ "$version" == "$branch" ]] || { echo "Source PHP_VERSION mismatch: expected $branch, found ${version:-unknown}" >&2; exit 2; }
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
root=$(cd "$script_dir/.." && pwd)
mkdir -p "$build_root"
build_root=$(realpath "$build_root")
# Generate a branch-native patch using the already validated v0.7.1 generator.
# The generator round-trips the patch against the pristine source before returning.
"$root/scripts/generate-native-patch.sh" "$branch" "$source_dir" "$build_root/native.patch"
cp -a "$source_dir" "$build_root/php-source"
cd "$build_root/php-source"
# Git apply uses exact context and refuses mismatches; no fuzzy patching in staging builds.
git apply --check "$build_root/native.patch"
git apply "$build_root/native.patch"
if find . \( -name '*.rej' -o -name '*.orig' \) -print -quit | grep -q .; then
  echo "Patch artifacts found; refusing build" >&2; exit 1
fi
sha256sum "$build_root/native.patch" > "$build_root/native.patch.sha256"

mkdir -p "$build_root/build"
cd "$build_root/build"
"$build_root/php-source/configure" --prefix="$build_root/install" --with-apxs2="$apxs" --disable-all --enable-session --enable-cli --enable-cgi --enable-mbstring --enable-xml --enable-dom --enable-simplexml --enable-pdo --with-pdo-mysql --with-mysqli --with-zlib --with-curl --with-openssl --with-gd --with-mcrypt --enable-soap --enable-zip > "$build_root/configure.log" 2>&1 || {
  echo "Configure failed; inspect $build_root/configure.log (extensions require host dependencies)" >&2; exit 1;
}
make -j"${JOBS:-2}" > "$build_root/build.log" 2>&1
echo "Build completed. Do NOT run make install against the host."
echo "Inspect the module artifact and configure/build logs; deploy only in isolated Apache staging."
