# Magento 1 Legacy Security Backport — Technical Reference

**Edition:** 1.0.0 · **Audience:** PHP maintainers, security reviewers, build engineers, Magento operators, release approvers  
**Classification:** Source-level security backport kit; **NOT production-certified**  
**Target PHP:** 5.5.38 and 5.6.40  
**Target Magento:** Community Edition 1.9.2.x and 1.9.3.x  
**Security workstream identifiers:** CVE-2026-109618 and CVE-2026-109619 (project scope; confirm authoritative advisories and per-hunk attribution independently)

> **Release boundary.** The v1.0.0 implementation is frozen at the source level. Independent reports confirm patch generation, zero-fuzz patch application on pristine PHP release tags, and targeted CLI/CGI testing on both branches. Neither an actual Apache `mod_php` build/runtime nor the four Magento/PHP combinations has been certified. The release gate remains **NO-GO**. Version `1.0.0` describes package maturity, not deployment authorization.

## 1. Executive engineering summary

This repository provides an isolated, reproducible path to adapt a security reference patch originating in PHP 5.4 to **two specific legacy PHP release baselines**. It is **not a Magento extension** and **does not patch Magento core**. The modified code resides in the PHP interpreter and its request-handling machinery. The kit includes branch-aware patch generation, source and package checks, an Apache staging build wrapper, PHP/Apache/Magento probes, evidence collection, and fail-closed administrative release gates.

The implementation addresses targeted OOM/error-handling, multipart-request accounting, executor/request cleanup, and configuration registration paths represented in the bundled patches. The exact security semantics must be assessed against the C source and the authoritative CVE advisories; this document does not invent a one-to-one CVE-to-function mapping. The changes are **not** a general remediation for the security risks of end-of-life PHP or Magento.

**What a consumer receives:** source patch reference; generator for branch-specific SAPI and INI modifications; a generator that produces a **single native patch** for a particular clean PHP tree; a staging-only Apache build script; probes and release-governance tools. **What a consumer does not receive:** PHP binaries, RPM/DEB packages, Magento changes, source tarballs, a preconfigured VM, completed Apache/Magento evidence, or production authorization.

## 2. System boundary and threat model

### 2.1 Architecture and trust boundaries

```text
Trusted upstream PHP 5.5.38 / 5.6.40 source (verified externally)
             |
             v
   generate-native-patch.sh
      |                |
      | common 5.4-derived security patch (temporary, fuzz tolerated)
      | branch-specific SAPI / INI patch (temporary, fuzz=0)
      v
  branch-native Git diff + round-trip verification
             |
             v
   build-modphp-staging.sh
   version guard -> git apply --check -> git apply
             |
             v
   isolated configure + make (NO make install)
             |
             v
   separate Apache staging instance -> HTTP probes / stress tests
             |
             v
   four Magento integration cells -> package / rollback -> approval
```

The **common patch** is an input to the *generator*, not an artifact to stack on top of a generated native patch. The **native patch** is intended to apply to the **same exact pristine source revision** used to generate it. Neither patch may be assumed to apply to vendor-modified PHP SRPMs without a fresh rebase and full review.

### 2.2 Relevant attack and failure surfaces

- **Multipart parsing:** adversarially shaped form-data requests and excessive multipart sections can stress request parsing and resource limits. A body-parts cap is part of the target mitigation; verify its actual enforcement with both benign and adversarial requests.
- **Memory exhaustion:** fatal out-of-memory handling must avoid unsafe recovery paths, unexpected shutdown callbacks, stale executor state, or crashes. Validate in a disposable process with explicit resource limits.
- **Request state cleanup:** request-info strings freed during shutdown must not remain accessible through stale pointers. Confirm the cleanup order for each PHP branch and SAPI.
- **Configuration drift:** the new INI entry must exist, have the expected value and scope, and affect the intended parser behavior under the **loaded Apache SAPI**, not only CLI.
- **Legacy deployment:** ABI mismatches, extension changes, older cryptographic dependencies, shared-host configuration, third-party Magento modules, and outdated vendor packages are independent risks.

### 2.3 Out of scope

This kit does not secure all of PHP 5.5/5.6, Apache, Magento 1, database services, TLS, extensions, or operating-system packages. It does not remediate every possible multipart/OOM weakness, promise immunity to denial of service, or authorize internet exposure of a legacy stack. All real stress tests must run in an isolated, restartable environment.

## 3. Supported baseline and compatibility policy

| PHP branch | Expected upstream source | Magento CE 1.9.2.x | Magento CE 1.9.3.x |
|---|---|---|---|
| 5.5 | **5.5.38** | Target; live test pending | Target; live test pending |
| 5.6 | **5.6.40** | Target; live test pending | Target; live test pending |

The source-version guard reads `main/php_version.h` and requires the exact `PHP_VERSION` string. That is a necessary check, **not proof of source provenance**: a modified tree can retain the same version string. Independently establish source archive signatures/checksums, exact Git tags/commit IDs, distribution patches, and a clean working tree. PHP 5.5.38 and 5.6.40 are upstream release baselines; distro vendor builds may differ in source, dependencies, ABI, and build flags.

**PHP 5.5 vs PHP 5.6 distinction:** `scripts/rebase-local-source.py` has explicit SAPI cleanup allowlists. PHP 5.5 requires nulling seven request-info fields: `post_data`, `raw_post_data`, `auth_user`, `auth_password`, `auth_digest`, `content_type_dup`, `current_user`. PHP 5.6 requires five: `auth_user`, `auth_password`, `auth_digest`, `content_type_dup`, `current_user`; it rejects unexpected legacy POST-data fields. The generator fails if expected `efree` sites are absent, rather than silently emitting a partial cleanup patch.

## 4. Source layout and component contracts

| Path | Purpose | Operational rule |
|---|---|---|
| `reference/php54-security-non-sapi-non-ini.patch` | Frozen common C security patch | Reference input to generator; inspect every hunk |
| `scripts/rebase-local-source.py` | Generates branch-aware SAPI cleanup and multipart INI patch | Reads clean source; output patch only |
| `scripts/generate-native-patch.sh` | Generates one source-specific unified Git diff | Requires clean exact source; refuses existing output |
| `scripts/build-modphp-staging.sh` | Native-patch application and isolated Apache build | Requires `apxs`; never installs on host |
| `scripts/check-port-baseline.py` | Source-version/file inventory | Does not authenticate upstream provenance |
| `scripts/fetch-sources.sh` | Upstream source acquisition/checks | Independently verify source hashes and transport |
| `scripts/audit-source.sh` | Relevant source-symbol inventory | Audit aid, not a security verdict |
| `apache-tests/` | Apache SAPI and normal upload probes | Isolated local staging only |
| `magento-tests/` | PHP preflight and read-only Magento inventory | Not functional acceptance testing |
| `scripts/collect-release-evidence.sh` | Staging evidence collection | Review collected data for secrets |
| `scripts/check-release-gates.py` | Offline declaration-based gate checker | Passing JSON does not prove evidence |
| `scripts/verify-release.py` | File checksum completeness and shell syntax | Does not execute PHP tests |
| `release/gates.example.json` | Unapproved gate template | Never edit into a false PASS |
| `docs/` | Specific runbooks and history | This reference consolidates, not supersedes, test evidence |

The original source files and Magento installations are intentionally **not bundled**. Do not distribute customer databases, payment data, Magento `app/etc/local.xml`, or production credentials as test evidence.

## 5. Security change inventory and review method

The native patch is produced by applying the frozen common patch and the generated SAPI/INI patch to a copy of a pristine source tree. Review the **generated native diff** as the definitive patch artifact for the selected source revision. Reported independent tests observed **nine modified files** in each branch's generated native patch (387 lines for 5.5.38; 375 for 5.6.40). These counts are regression observations, not a permanent format contract.

### 5.1 Multipart body-parts limit

The generated SAPI/INI patch registers `max_multipart_body_parts` in `main/main.c` adjacent to the existing `max_file_uploads` entry, with default `-1` and flags `PHP_INI_SYSTEM|PHP_INI_PERDIR`. The common patch supplies the corresponding parsing behavior. Confirm the effective default and overrides in the actual Apache runtime. Test the configured small limit, the default, and `0`, along with legitimate uploads and adversarial header/part amplification. Do not assume that merely seeing the INI entry proves enforcement.

### 5.2 OOM handling and `zend_mm_safe_error_ex`

The common patch includes a change involving `zend_mm_safe_error_ex` in Zend allocation/error-handling code. Independently reported CLI/CGI tests found a fail-closed process exit on the tested OOM path and suppression of unsafe shutdown behavior. Review C-level control flow, allocation-failure branches, and the fatal-error path for both PHP versions. Verify that the same property holds in Apache worker execution and that no unexpected callbacks, crashes, or stale request state occur.

### 5.3 Executor/module reset

The common patch includes a `modules_activated = 0` reset in `main.c`. Inspect the placement and lifecycle impact; confirm that request teardown remains safe when initialization is incomplete or error handling exits early. Exercise normal request sequences, failed requests, and repeated requests within a long-lived Apache worker.

### 5.4 SAPI request-info pointer nulling

For every expected `efree(SG(request_info).field)` site, the branch-specific generator inserts a corresponding `SG(request_info).field = NULL;` if not already present. This is a cleanup/lifetime measure, not a generic permission to null unrelated fields. Review all generated hunks against actual source structure and test both normal and error shutdown paths. Missing required fields, unexpected legacy fields in PHP 5.6, and incompatible source formatting are hard failures.

### 5.5 Source-review checklist

For each branch, reviewers should record: pristine source ID and digest; native patch digest; changed file list; complete hunk review; expected security markers; error-path and cleanup-order reasoning; source compile results; PHPT deviations; Apache runtime results; Magento compatibility outcomes; and explicit reviewer signoff. **Presence of a marker is evidence of a textual change, not proof of CVE remediation.**

## 6. Native patch generation: exact sequence

Prerequisites: Bash, Python 3, GNU `patch`, Git, coreutils, and an exact, clean source tree for the selected PHP release. Use separate directories for each branch.

```bash
# Example paths only; verify source provenance before proceeding.
scripts/generate-native-patch.sh 5.5.38 /srv/src/php-5.5.38 /srv/patches/php55-native.patch
scripts/generate-native-patch.sh 5.6.40 /srv/src/php-5.6.40 /srv/patches/php56-native.patch
sha256sum /srv/patches/php55-native.patch /srv/patches/php56-native.patch
```

Internally the generator:

1. Resolves input/output paths, refuses unsupported branch names and existing output files.
2. Copies the supplied source to a disposable working tree; does not modify the original.
3. Generates branch-specific SAPI/INI hunks from the exact source.
4. Creates a temporary Git baseline and applies the common patch using normal fuzz tolerance **with `--no-backup-if-mismatch`**.
5. Applies the generated SAPI/INI patch with **`--fuzz=0`**; refuses `.rej` and `.orig` artifacts.
6. Emits one native `git diff --no-ext-diff --binary HEAD` patch.
7. Applies the native patch to a fresh copy using `git apply --check` and `git apply` and byte-compares changed files.
8. Writes the requested output only after successful verification.

**Important distinctions:** fuzzy matching is allowed only during generation of the native patch from the frozen common reference; deployment of the native patch uses Git's exact-context check. The generator's byte comparison verifies changed files in the generated output, not a complete security proof or full source-tree equivalence. Re-run the generator if the source tree changes. Do not apply the native patch **after** applying the common/SAPI patches; that would double-apply the same modifications.

### 6.1 Known historical defects and their resolutions

| Version | Defect | Resolution retained in v1.0.0 |
|---|---|---|
| v0.6 | Common reference patch failed with `--fuzz=0` | v0.6.1 allowed standard fuzz for common patch |
| v0.7 | GNU `patch` emitted benign `.orig` backups, tripping generator guard | v0.7.1 added `--no-backup-if-mismatch` |
| v0.8 | Multiple patch paths in staging build | Consolidated on validated native generator and `git apply` |

The security core itself was reported byte-identical across these wrapper fixes. The packaging verifier should be run on the **actual extracted archive**.

## 7. Isolated Apache mod_php staging build

**Do not run on production.** Provision an isolated VM/container with compatible PHP 5-era dependencies, compiler toolchain, Apache development headers and an executable `apxs`. The script expects four positional arguments and a **nonexistent** build-root path.

```bash
scripts/build-modphp-staging.sh \
  5.5.38 /srv/src/php-5.5.38 /usr/bin/apxs /srv/builds/php55-modphp
scripts/build-modphp-staging.sh \
  5.6.40 /srv/src/php-5.6.40 /usr/bin/apxs /srv/builds/php56-modphp
```

The wrapper checks the `PHP_VERSION` string, generates and verifies the native patch, copies the source into the build root, performs `git apply --check` followed by `git apply`, checks for `.rej`/`.orig`, saves `native.patch.sha256`, runs `configure --with-apxs2=<apxs>` with Magento-oriented extensions, then invokes `make`. It captures `configure.log` and `build.log`. **It never executes `make install`.** It does not configure or load the module in Apache, build an RPM, or deploy PHP.

The included configure options request session, CLI/CGI, mbstring, XML/DOM/SimpleXML, PDO/MySQL, mysqli, zlib, curl, OpenSSL, GD, mcrypt, SOAP, and ZIP. This is a build attempt, **not** proof those extensions compile or work with the target host's libraries. Failed configure or build is a blocked gate; do not silently remove Magento-required extensions to manufacture a PASS. In particular, contemporary Apache/APR/OpenSSL/toolchain combinations may not build historical PHP unmodified.

**Build evidence minimum:** exact OS/compiler/Apache/apxs versions; upstream PHP source digest and commit/tag; patch digest; complete configure command and logs; `make` logs and exit status; module artifact hash and binary dependencies; loaded Apache module identity; and runtime PHP version/SAPI. Run each branch in an independent Apache environment—never load both PHP modules into the same instance.

## 8. Apache HTTP acceptance procedure

Follow `docs/APACHE_MAGENTO_GATE.md` for the concrete local-only alias example. Protect probe files using Apache-level `Require local`, disable directory indexing, and remove the alias after testing. Do not rely solely on PHP `REMOTE_ADDR` checks for access control.

```bash
# Run only after deploying a compiled module into an isolated Apache test instance.
bash apache-tests/run-local.sh http://127.0.0.1:8080/__php_patch_probe
```

**Normal HTTP checks:** the response reports `apache2handler` rather than CLI/CGI; exact PHP version; expected `max_multipart_body_parts` value; normal multipart upload accepted; no unexpected warnings/fatals; stable sessions and repeated requests. Archive raw request/response samples and sanitized Apache/PHP logs.

**Security battery (separate, disposable environment):** repeat the targeted multipart amplification and body-parts cap tests, including limit `2`, `0`, and default; execute bounded OOM/fatal-shutdown scenarios; verify fail-closed behavior and absence of worker crashes or state corruption. A small successful upload **does not** substitute for these adversarial tests. Stress testing should not be directed at internet-facing or shared production servers.

## 9. Magento functional acceptance: four mandatory cells

For each of the four PHP/Magento combinations, record the exact Magento patch level, extensions/modules, database version, Apache module identity, and environment configuration. `magento-tests/magento-readonly.php` checks inventory only; it does not prove business-flow compatibility.

| Area | Required staging observation |
|---|---|
| Storefront | Home, category, product routes; HTTP status and errors |
| Customer | Login/logout; cookie and session persistence |
| Cart | Add, update and remove items; state retained |
| Checkout | Test gateway, shipping/tax, **sandbox-only** order |
| Admin | Login, authorization and test product save |
| Media | Product image upload and resize |
| Cron | Staging cron invocation and successful job execution |
| Extensions | Third-party module inventory and upload/session compatibility review |
| Operational | Error logs, DB connectivity, XML/SOAP/GD/curl/crypto dependencies |

Run baseline and patched builds under comparable conditions. Keep disposable test accounts, no real payment charges, and sanitized logs. One passing Magento version or one PHP branch cannot be extrapolated to the other three combinations.

## 10. PHP regression and deviations

Independent earlier testing reported successful CLI/CGI build/link and targeted OOM/multipart security checks for both branches. It also reported **13 PHPT deviations per branch**: eight related to session upload-progress behavior and five concerning OOM message location. Those deviations are **not automatically harmless** and require explicit classification, rationale, and reviewer acceptance before production. Preserve the original test names, outputs, expected outputs, environment details, and any reproducer. A count alone is insufficient release evidence.

Review: normal uploads; session upload progress; multipart parser limits; error/exception paths; shutdown functions; repeated requests; memory-limit handling; extension initialization; and Magento-specific functional paths. Do not infer mod_php results from CLI/CGI tests because the SAPI, worker lifetime and request context differ.

## 11. Evidence, release governance and approval

`release/gates.example.json` is a **template with incomplete gates**, not a signed test report. Create a separate evidence file, retaining the schema. `scripts/check-release-gates.py` requires, for **each** PHP branch, boolean `true` for `source_integrity`, `source_patch_review`, `cli_cgi_security`, `regression_review`, `apache_mod_php`, `apache_security_battery`, `package_install_rollback`, `independent_security_review`, and both Magento matrix entries (`1.9.2`, `1.9.3`), plus nonempty `evidence_refs`.

```bash
python3 scripts/verify-release.py
python3 scripts/check-release-gates.py /secure/evidence/gates-reviewed.json
```

The gate checker is **administrative**: it validates declarations and presence of reference strings; it cannot inspect the referenced files or authenticate a reviewer's claims. An all-green JSON file must be independently audited against signed reports, source hashes, logs, actual binary artifacts, and rollback evidence. Do not flip gate booleans simply to obtain exit code zero.

Suggested evidence directory (outside this package):

```text
evidence/
  source-provenance/{php55,php56}/
  patch-review/{php55,php56}/
  cli-cgi/{php55,php56}/
  apache-build/{php55,php56}/
  apache-security/{php55,php56}/
  magento/{192-55,193-55,192-56,193-56}/
  package-and-rollback/
  security-signoff/
  gates-reviewed.json
```

Record dates, tool versions, operator, host identity, environment constraints, test inputs, expected/observed outputs, and disposition of every failure. Avoid secrets and personally identifiable data. Preserve failed runs as well as successful ones.

## 12. Packaging, deployment and rollback

The kit is **source-only**. Production packaging must be created for the exact target OS/vendor PHP packaging model; do not assume upstream source compatibility implies binary compatibility with RHEL/CentOS packages. Check package ownership, Apache module ABI, dependencies, extension ABI, filesystem paths, permissions, service scripts, and co-installation/isolation. Generate and archive checksums for every installed binary and package.

Before any approved deployment: snapshot/backup the original PHP package/module/configuration, verify restore capability, record original package versions and hashes, and perform a timed rollback drill on staging. Confirm service restart behavior, configuration restoration, no database/schema changes, restored storefront/admin behavior, and reproducible post-rollback health checks. This kit deliberately does not run `make install`, alter Apache configs, change Magento core, or touch a database.

**Rollback trigger examples:** build or ABI mismatch, Apache failure to start, unexpected PHP SAPI/version, regression in sessions/uploads/checkout, security battery failure, or unexplained PHPT deviation. Follow `docs/STAGING_AND_ROLLBACK.md` for operational detail; adapt the procedure to the actual distribution.

## 13. Failure modes and troubleshooting

| Symptom | Likely cause | Safe response |
|---|---|---|
| `PHP_VERSION mismatch` | Wrong release tag or modified tree | Stop; verify exact source revision |
| Common patch rejects during native generation | Unexpected source drift or patch context | Stop; do not force patch; review source |
| `.orig`/`.rej` artifacts | Existing dirty source or failed application | Stop; start from pristine tree |
| Native `git apply --check` fails | Patch/source mismatch | Regenerate from the exact source; no fuzzy deployment |
| Generator output exists | Clobber protection | Use a new versioned output path |
| Build root exists | Clobber protection | Use a new isolated build root |
| Configure cannot find `apxs` or extensions | Missing/incompatible build dependencies | Fix isolated toolchain; document changes |
| `make` fails | Legacy PHP/toolchain incompatibility | Preserve logs; do not claim build PASS |
| Probe says `cli`/`cgi-fcgi` | Wrong Apache PHP handler | Correct staging configuration and rerun |
| INI marker present, behavior wrong | Registration without enforcement or runtime drift | Investigate C code and Apache configuration |
| Gate checker reports PASS | Declarations complete, not necessarily tests | Independently inspect evidence and signoff |

## 14. Release state and change control

| Workstream | v1.0.0 disposition |
|---|---|
| Frozen common patch and branch SAPI/INI generator | DONE — previously tested |
| Branch-native patch generation / zero-fuzz application | DONE — independently tested on pristine tags |
| CLI/CGI targeted security tests | DONE — reported, preserve raw evidence |
| Source-level Apache build wrapper | DONE — patch phase tested |
| Actual Apache mod_php configure/build/load | OPEN — staging required |
| Apache HTTP security battery | OPEN — staging required |
| Magento 1.9.2.x/1.9.3.x × PHP 5.5/5.6 | OPEN — four cells |
| Distribution package install/rollback | OPEN |
| Independent final security review | OPEN |
| Production release | **NO-GO** |

Changes to the security patch, generator, configure flags, dependency versions, or target source revision require impact assessment and retesting. For file-based releases, provide explicit **ADD / REPLACE / DELETE** lists. Never describe a scaffold, probe, or administrative gate as equivalent to an executed integration test.

## 15. Primary companion documents

- `docs/RELEASE_1_0.md` — release classification and acceptance boundary.
- `docs/NATIVE_PATCH_V07.md` — generator semantics and v0.7.1 correction.
- `docs/FINAL_STAGING_HANDOFF.md` — concise staging handoff.
- `docs/APACHE_MAGENTO_GATE.md` — local HTTP probes and four-cell acceptance checklist.
- `docs/STAGING_AND_ROLLBACK.md` — evidence and rollback runbook.
- `docs/RELEASE_GATES.md` — administrative release-gate operation.
- `docs/PORT_REBASE_V03.md` and `docs/PORTING_PLAN.md` — historical source-port context.
- `docs/TEST_MATRIX.md` — historical matrix; **not** a record of completed Apache/Magento testing.

**Final release rule:** approve production only when the actual target binaries, Apache HTTP behavior, all four Magento combinations, packaging/rollback, regression deviations, and independent security review are evidenced and signed off. Until then, distribute as a **v1.0.0 source-level staging kit**, not as a production-certified fix.
