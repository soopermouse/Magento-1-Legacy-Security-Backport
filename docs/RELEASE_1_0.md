# Magento 1 Legacy Security Backport — v1.0.0

## Release classification

**Source kit v1.0.0 (release candidate for isolated staging). Not production-certified.** Version 1.0.0 freezes the completed source implementation; it does not assert completion of infrastructure-dependent acceptance tests.

## Supported target matrix

Magento CE 1.9.2.x and 1.9.3.x with PHP 5.5.38 or 5.6.40. These are **targets**, not a claim of live compatibility testing.

## Validated evidence inherited from v0.8

- Native patch generation and exact-context application were independently verified against pristine release trees on both PHP branches.
- The PHP security core was unchanged from the previously validated v0.5 baseline.
- CLI/CGI regression and security battery results were reported for both patched branches.
- v0.8 Apache build wrapper patch-application stage was independently verified for both branches.

## Unverified and blocking

- Real `--with-apxs2` configure and make, Apache module loading, HTTP/OOM/upload security probes.
- Live Magento CE 1.9.2.x / 1.9.3.x integration on both PHP branches (four combinations).
- Production packaging, rollback rehearsal, independent security signoff.

Do not describe the above as passing. No production deployment is authorized by this kit.

## Offline verification

Run `python3 scripts/verify-release.py` from the extracted package. It verifies every packaged file, rejects unlisted files, and checks Bash syntax. It does not test PHP behavior.

## Staging workflow

1. Obtain pristine, trusted release sources for PHP 5.5.38 and 5.6.40; independently verify provenance.
2. On an isolated staging host with compatible Apache development headers, run `scripts/build-modphp-staging.sh <branch> <clean-source-dir> <apxs-path> <new-build-root>` separately for each branch.
3. Inspect generated native patch and SHA-256, configure/build logs, loaded module identity, and run the Apache runtime/upload probes.
4. Test all four Magento/PHP combinations using the read-only Magento inventory and application smoke tests.
5. Capture evidence, exercise rollback, secure independent review, then complete `release/gates.example.json` as a new evidence file and run `python3 scripts/check-release-gates.py <evidence-file>`.

The release gate checker evaluates declarations and evidence references; it does not independently establish their truth.

## Change control

This release contains no PHP patch changes and no Magento core modifications. Future modifications require a new version, new hashes, and renewed testing for affected components.
