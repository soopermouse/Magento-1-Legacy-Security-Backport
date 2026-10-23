# PHP 5.5 / 5.6 branch-specific rebase

The `reference/php54-security-non-sapi-non-ini.patch` file retains the original PHP 5.4 combined security hunks **except** the entire `main/SAPI.c` section and the standalone `main/main.c` INI registration section. It is a **porting reference**, not a validated PHP 5.5/5.6 release patch.

For each **clean** PHP source checkout:

```sh
python3 scripts/rebase-local-source.py --source /path/to/php-5.5.38 --branch 5.5.38 --output php55/patches/sapi-ini-rebased.patch
python3 scripts/rebase-local-source.py --source /path/to/php-5.6.40 --branch 5.6.40 --output php56/patches/sapi-ini-rebased.patch
```

Then apply the reference patch and branch-specific patch to separate disposable source copies. Check patch rejects and audit all hunks. Do not apply to trees that already contain some 5.4 patch hunks; the generator requires clean source and detects only the INI marker, not all prior edits.

**Security review required:** confirm that all SAPI cleanup paths are covered, no pointer is subsequently used, no double-free occurs, and multipart limit is honored by rfc1867.c. The generator adds NULL immediately after known `efree(SG(request_info).field)` calls, but cannot prove lifecycle correctness. The original 5.4 patch contained duplicated NULL assignments; those were intentionally excluded.

**Not validated:** this environment does not contain the 5.5.38/5.6.40 sources and cannot download them. No PHP compilation or Magento tests have been run for these ports. The previous external patch-application report is not a compiled regression result.

### v0.3.1 PHP 5.6 correction

The generator uses explicit per-branch field lists: seven request-info fields on PHP 5.5.38, five on PHP 5.6.40. It rejects unexpected legacy POST-data fields in 5.6 and missing `efree` for any field expected in the chosen branch. This avoids silently masking a source-layout change.
