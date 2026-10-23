# v0.7 — Native patches for PHP 5.5.38 and PHP 5.6.40

The frozen common patch has historically required default fuzz when applied directly. This tool **generates branch-native patches** from clean, verified source trees, then verifies that each resulting diff applies using `git apply --check` and reproduces the modified source byte-for-byte. The generated patches do not require fuzzy matching on the same exact source revision.

```bash
scripts/generate-native-patch.sh 5.5.38 /srv/src/php-5.5.38 /srv/output/php55-native.patch
scripts/generate-native-patch.sh 5.6.40 /srv/src/php-5.6.40 /srv/output/php56-native.patch
```

Use clean release tags and record exact Git commit IDs. Source revision matters: a patch for one commit is not automatically suitable for another distribution's PHP build. Generated patches are not shipped as prevalidated artifacts because the clean source trees were not available here. Do not apply a native patch on top of the common or SAPI/INI patches. Use **either** the existing two-step patch flow **or** the generated native patch, never both.

This generator does not constitute security validation. Manually review all hunks, especially OOM handling, SAPI cleanup, executor reset, multipart parser, and INI registration. Run the previously documented full regression and Apache/Magento gates before deployment. If the source contains generated files or local modifications, clean it first.

## v0.7.1 generator correction

The common patch uses standard fuzz tolerance with `--no-backup-if-mismatch` to avoid benign `.orig` backups caused by offset/fuzz application. Actual `.rej` files and unexpected existing backup artifacts remain fatal. The exact generated SAPI patch still requires `--fuzz=0`. The requested output path is resolved before entering temporary working directories, so relative paths refer to the caller’s original directory. These are generator-only changes; they do not change the frozen security patch.

The generator has not been executed against real PHP source trees in this package environment; independent validation is still required.
