# Release gates

1. Confirm exact CVE applicability and affected code paths for each upstream source baseline.
2. Port fixes independently; document every difference from the upstream reference.
3. Run patch application checks and full compile/link of CLI, CGI, FPM and Apache SAPI.
4. Run PHP regression suite and targeted multipart/OOM/state-isolation tests; capture before/after results.
5. Test Magento 1.9.2.x and 1.9.3.x against both runtimes on staging, including login, sessions, uploads, cart, checkout and cron.
6. Build and validate vendor-specific RPMs; verify all required extensions, dependencies, upgrade/rollback and signatures.
7. Independent security review and release approval.

Until all gates pass: NO-GO for production. Never treat the prior PHP 5.4 port as proof of security on 5.5 or 5.6.
