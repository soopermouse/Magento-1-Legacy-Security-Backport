# v0.5 staging and rollback runbook

**Not production-ready.** The engine-level tests reported by the external tester do not establish Apache or Magento compatibility. Do not test OOM denial-of-service cases against a production server.

## Staging prerequisites

1. Provision an isolated, access-controlled staging host or VM with a tested snapshot/restore process. Use synthetic customers and sandbox payment credentials only.
2. Record OS, architecture, compiler, Apache version, PHP configure flags, loaded modules, package manager and exact Magento patch version for every run. PHP 5.5 and 5.6 must run in separate instances or isolated Apache configurations.
3. Obtain PHP 5.5.38 and PHP 5.6.40 sources and independently verify their official archive digests. Record provenance of any distribution patches.
4. Compile mod_php against the target Apache development headers; verify `apache2handler` from an actual Apache HTTP request, not CLI. Run `apache-tests/run-local.sh` against loopback-only test endpoints.
5. Ensure probe files and aliases are restricted at the Apache configuration layer (`Require local`) and remove them immediately after testing. Loopback checks in PHP are defense in depth, not access control.
6. Exercise multipart limits and OOM behavior only in an isolated disposable environment. Compare baseline and patched builds.
7. For each of the four combinations, test storefront, login/logout, cart persistence, checkout with sandbox gateway, admin, media upload, cron, cache, sessions and installed extensions. Record PASS/FAIL with evidence, never customer data.
8. Review 13 known PHPT deviations per branch, including the eight session upload-progress tests and five OOM diagnostics tests. Validate whether installed Magento extensions use session upload progress.

## Packaging and installation

- No installable RPM is shipped in this release. Produce separate RPM builds for each distribution/package family; do not overwrite vendor PHP packages with generic upstream binaries.
- Inventory and preserve installed PHP extension ABI, configuration, Apache module dependencies and package ownership. Keep backup copies of PHP configuration outside the web root.
- Build and test installation in a disposable clone; verify package signatures and dependency closure. Do not enable automatic production upgrade.
- Before production consideration, capture approved backups, maintenance-window plan, health checks, and rollback decision criteria.

## Rollback drill (required)

1. Snapshot the VM and back up package database, PHP/Apache config and Magento database/files using approved procedures.
2. Install the candidate package on staging; verify HTTP/Apache SAPI, PHP modules, sessions, uploads and checkout sandbox.
3. Simulate rollback to the *exact previous package set*, restore configuration, restart services and rerun smoke tests.
4. Record downtime, failure modes, recovery time, and signoff. If rollback fails, the release gate stays blocked.

## Evidence and approval

Use `scripts/collect-release-evidence.sh` for sanitized CLI build metadata and `release/gates.example.json` as a starting point for the manual release gate record. Never publish credentials, `app/etc/local.xml`, full `phpinfo()` output or unredacted server logs.

`python3 scripts/check-release-gates.py release/gates.example.json` must return nonzero until all four Magento combinations, both Apache branches, package rollback and independent review are completed. A passing JSON gate is an administrative check, **not** proof that testing occurred.
