# v0.6 Apache staging build handoff

**Status: tooling only; not a verified mod_php build.** Run only on an isolated disposable host. Do not install into system Apache or overwrite vendor PHP.

The build script accepts a verified clean PHP 5.5.38 or 5.6.40 source tree, the matching Apache `apxs` binary and a **nonexistent** output directory. It creates branch-specific SAPI/INI hunks, applies the frozen common patch with standard patch fuzz tolerance, configures PHP with the Apache module and Magento-oriented extensions, and compiles without installing. Extension configure flags and dependencies differ across platforms; failed configure is a blocked gate, not permission to silently drop extensions.

Example:

```sh
scripts/build-modphp-staging.sh 5.5.38 /srv/sources/php-5.5.38 /usr/bin/apxs /srv/builds/php55-modphp
scripts/build-modphp-staging.sh 5.6.40 /srv/sources/php-5.6.40 /usr/bin/apxs /srv/builds/php56-modphp
```

**Important:** PHP 5.5/5.6 may not compile against current Apache/APR/OpenSSL/compiler stacks without compatibility work. Build each branch in a compatible isolated VM. Do not mix both modules in one Apache instance. The command does not provision the OS, validate cryptographic archive digests, deploy Apache, configure Magento, run CVE probes, sign packages or perform rollback. These remain explicit release blockers.

After compilation, use `docs/APACHE_MAGENTO_GATE.md` on a dedicated Apache instance, confirm `apache2handler` over real HTTP, and run the existing four-cell Magento test matrix. Capture actual results, not inferred PASS values.

Current local environment contains Apache 2.4.68 and PHP 8.4 CLI but no `apxs` or PHP 5.5/5.6 source/build, so it cannot demonstrate a real legacy mod_php build.

## v0.6.1 correction

The common PHP 5.4-derived patch needs standard `patch` context fuzz tolerance on pristine PHP 5.5.38 and 5.6.40 source tags, as demonstrated by independent application tests. The generated SAPI/INI patch retains `--fuzz=0`. A clean apply with zero rejects is necessary but not sufficient for release: inspect offsets/fuzz in the patch output, verify the patched security-sensitive code and run the full regression battery. No mod_php build is claimed by this correction.
