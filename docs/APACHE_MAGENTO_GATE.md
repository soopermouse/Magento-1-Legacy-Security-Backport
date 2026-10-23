# Apache and Magento integration release gate (v0.4)

## Safety boundary
These probes are **not** a substitute for the security battery or Magento checkout tests. Run in an isolated staging VM, never on an exposed production vhost. The Apache probe directory must be protected by Apache-level `Require local` (Apache 2.4); PHP's REMOTE_ADDR check is defense in depth, not the access control. Remove the probe alias/files when finished. Do not serve a Magento directory as the probe document root.

## Apache example (Apache 2.4)

```apache
Alias /__php_patch_probe/ "/opt/magento-patch-probe/"
<Directory "/opt/magento-patch-probe/">
    Require local
    Options -Indexes
    AllowOverride None
</Directory>
```

Place `runtime-probe.php` and `upload-probe.php` in `/opt/magento-patch-probe/` and run:

```bash
bash apache-tests/run-local.sh http://127.0.0.1:8080/__php_patch_probe
```

Expect `apache2handler` and non-null `max_multipart_body_parts`; verify PHP 5.5.38 or 5.6.40 and compare the full runtime configuration to the clean baseline. The harness verifies a small normal upload only. It does **not** execute OOM or header-amplification stress against a live Apache worker; do that in an isolated, restartable test host using the existing security battery.

## Magento read-only preflight

```bash
/path/to/patched/php magento-tests/magento-readonly.php /path/to/magento-root
```

This checks files and extensions only, not Magento's version, checkout behavior, module compatibility, or database connections. `app/etc/local.xml` contains secrets: never upload or print it.

## Manual Magento functional matrix (each of 4 combinations)

| Area | Test | Expected evidence |
|---|---|---|
| Storefront | Home, category, product pages | HTTP status, PHP/Apache errors |
| Customer | Login/logout and session persistence | Session retained across requests |
| Cart | Add/update/remove product | Cart state persists |
| Checkout | Sandbox gateway + shipping/tax | Test order only, no real charge |
| Admin | Login and product edit | ACL, session and save work |
| Media | Admin product image upload | Image stored and resized |
| Cron | Run Magento cron in staging | Successful scheduled job, no fatal |
| Extensions | Inventory third-party modules | Owner signoff for upload/session dependencies |

Run under Apache mod_php with **both** PHP branches and both Magento versions. Save baseline-vs-patched results and logs; sanitize customer/payment data.

## Release blockers
- Confirm source archive digests independently.
- Apache mod_php builds and security battery for each PHP branch.
- Four Magento integration combinations with documented outcomes.
- Resolve/accept 13 regression deviations per PHP branch, including 8 upload-progress tests.
- Distribution packaging, rollback, and independent security review.
