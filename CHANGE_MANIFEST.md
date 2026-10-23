# v1.0.0 change manifest

Baseline: independently reviewed v0.8. No modifications to security patches, patch generators, Apache build wrapper, probes, or gate checker.

## ADD
- `docs/TECHNICAL_REFERENCE.md` — comprehensive security architecture, source/patch workflow, Apache/Magento test matrix, release evidence, rollback and limitations.
- `docs/RELEASE_1_0.md` — final release scope, validation boundaries, and staging instructions.
- `scripts/verify-release.py` — offline fail-closed package integrity and shell syntax verification.

## REPLACE
- `CHANGE_MANIFEST.md` — this version-specific change record.
- `SHA256SUMS` — regenerated to include all v1.0.0 files.

## DELETE
- None. Do not reuse old staging build directories.

## Status
Source implementation frozen as v1.0.0; documentation-only update. Production remains NO-GO until documented Apache, Magento, packaging/rollback and security-review gates pass.
