# v0.8 staging handoff — not production certification

## Validated
PHP 5.5.38 and 5.6.40 CLI/CGI security testing, branch-native patch generation and zero-fuzz application were independently reported passing on pristine release tags. The security core is unchanged from v0.7.1.

## Build in isolated staging
On a host with matching legacy Apache development headers (`apxs`) and compatible PHP build dependencies:

```sh
scripts/build-modphp-staging.sh 5.5.38 /sources/php-5.5.38 /usr/bin/apxs /staging/build55
scripts/build-modphp-staging.sh 5.6.40 /sources/php-5.6.40 /usr/bin/apxs /staging/build56
```

Each build generates and verifies a native patch, applies it with `git apply --check`, checks the PHP_VERSION source header, saves the patch hash, then configures and compiles without `make install`. Use separate clean sources and build roots. The build does not deploy Apache modules.

## Mandatory acceptance gates
1. Compile each mod_php variant on the actual target Apache stack; archive configure/build logs and loaded module identity.
2. Execute Apache HTTP runtime and upload probes, including OOM and multipart stress regression cases; confirm Apache SAPI, INI and fail-closed behavior.
3. Test Magento CE 1.9.2.x and 1.9.3.x under both PHP 5.5.38 and 5.6.40: four combinations; record login, checkout, admin, upload and session behavior.
4. Verify production packaging, checksums, installation isolation, restore/rollback and independent security signoff.
5. Complete `release/gates.example.json` evidence and run `scripts/check-release-gates.py` as described in `docs/RELEASE_GATES.md`.

**NO-GO** until all gates pass. Do not claim live Magento or mod_php validation from this source-only release.
