# PHP 5.5 / PHP 5.6 porting work plan

This repository does **not** yet contain a CVE fix for either branch. The existing PHP 5.4.16-48.el7 patch was developed against a distribution-patched source tree and must not be applied indiscriminately to these upstream releases.

## Baselines and source provenance

- PHP 5.5.38, upstream final PHP 5.5 release. SHA-256 of official `.tar.xz`: `cb527c44b48343c8557fe2446464ff1d4695155a95601083e5d1f175df95580f`.
- PHP 5.6.40, upstream final PHP 5.6 release. SHA-256 of official `.tar.xz`: `1369a51eee3995d7fbd1c5342e5cc917760e276d561595b6052b21ace2656d1c`.
- These tarball hashes identify **upstream** sources, not any RHEL/SCL/third-party RPM build. Downstream packaging requires a separate source baseline and patches audit.

Run `scripts/fetch-sources.sh sources` on a networked machine. Extract each archive, then run:

```sh
python3 scripts/check-port-baseline.py sources/php-5.5.38 --branch 5.5 --output php55-inventory.json
python3 scripts/check-port-baseline.py sources/php-5.6.40 --branch 5.6 --output php56-inventory.json
```

The inventory tool fails on the wrong source version or missing files. It **does not** check whether a vulnerability exists or has been fixed.

## Engineering sequence, separately for each branch

1. Diff allocator OOM paths, integer arithmetic, bailout/shutdown behavior, executor globals, SAPI request pointer lifetime, session upload progress, and RFC1867 multipart parser against the upstream security reference.
2. Create a *branch-specific* patch with context appropriate to that branch. Preserve existing downstream security fixes; do not overwrite them.
3. Add targeted PHPT tests: OOM inside request and shutdown, integer overflow, multipart part cap, 300k junk headers, folded and duplicate headers, repeated requests, and upload progress.
4. Build CLI, CGI, FPM, and Apache SAPIs; run PHP regression suite with baseline comparison. Treat failures as unresolved until investigated.
5. Test Magento 1.9.2.x and 1.9.3.x with each runtime: admin/storefront, sessions, product media upload, cart, checkout sandbox, cron and installed extensions.
6. Only after tests: build/sign packages for each specific distribution source release, stage, verify rollback, and seek independent security review.

## Known blocker

The two upstream PHP tarballs were not available in the local build workspace when this package was assembled. No PHP 5.5/5.6 patch is asserted to apply, compile, or remediate the CVEs. Network fetching must happen in an authorized build environment.
