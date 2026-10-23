# Magento 1.9.2 / 1.9.3 — PHP 5.5 and 5.6 security backports

Independent product targeting Magento Community Edition 1.9.2.x and 1.9.3.x on legacy PHP 5.5 and PHP 5.6.

**Current release: development baseline, not a security patch.** No PHP 5.5 or 5.6 CVE backport has been implemented or tested yet. Do not deploy this repository as a mitigation. The earlier PHP 5.4.16 RHEL7 patch is **not** compatible by assumption.

## Baselines

- PHP 5.5.38 — final upstream PHP 5.5 release
- PHP 5.6.40 — final upstream PHP 5.6 release
- Magento CE 1.9.2.x / 1.9.3.x — four validation combinations

Use `scripts/fetch-sources.sh` to download and SHA-256 verify official source tarballs. Run `scripts/audit-source.sh` to inventory relevant symbols before porting. Original upstream sources are not redistributed in this repository.

## Layout

- `php55/`, `php56/`: independent branch-specific port status and eventual patches
- `reference/`: list of PHP 5.4 source paths to examine; no PHP 5.4 patch is presented as a 5.5/5.6 fix
- `magento-tests/`: non-destructive CLI preflight for extension and PHP version checks
- `docs/`: compatibility matrix and release acceptance gates

## Release policy

Separate security review, complete PHP builds (CLI/CGI/FPM/Apache), upstream regressions, OOM and multipart security tests, Magento storefront/admin/cart/checkout/cron tests, and distribution-specific package validation are required for **each** PHP branch. Neither upstream branch is maintained by PHP.net; backporting two CVEs does not secure the entire runtime.

## Next engineering increment (v0.2)

`check-port-baseline.py` verifies the exact extracted PHP source version and inventories the nine key files before porting. See `docs/PORTING_PLAN.md` and `docs/TEST_MATRIX.md`. No security patch for PHP 5.5/5.6 has been produced or validated yet.

## v0.3 local source rebase tooling

See `docs/PORT_REBASE_V03.md`. The security reference and generator are **not installable or validated fixes**.

### v0.3.1 generator correction

The PHP 5.6.40 SAPI rebase excludes legacy `post_data` and `raw_post_data` fields removed in that branch. Expected fields remain mandatory: missing `efree` calls cause an error rather than silently dropping security cleanup. Generated C patches remain subject to source review and compile/regression testing.

## v0.4 Apache/Magento integration gate

Added local-only Apache mod_php identification/upload probes, a read-only Magento preflight, and a four-combination manual acceptance matrix. These are test harnesses, **not evidence that Apache or Magento has passed**. Source-level CLI/CGI builds and security tests for both PHP versions have been reported by the external tester; Apache and Magento integration remain open. See `docs/APACHE_MAGENTO_GATE.md`.

## v0.5 — deployment readiness (2026-10-22)

**Current status supersedes the early scaffold statements above:** external testing reports both PHP 5.5.38 and 5.6.40 ports build under CLI/CGI and pass the targeted OOM/multipart battery. Thirteen PHPT deviations per branch require formal release review. This repository does **not** contain prebuilt or installable PHP packages and is **not production approved**.

New staging/rollback runbook: `docs/STAGING_AND_ROLLBACK.md`. New offline, fail-closed release gate: `scripts/check-release-gates.py release/gates.example.json`. The four Magento integration combinations and real Apache mod_php remain untested. The security patch reference and generator are unchanged from v0.4.
