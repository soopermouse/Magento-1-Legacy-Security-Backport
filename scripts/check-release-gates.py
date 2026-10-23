#!/usr/bin/env python3
"""Fail-closed, offline release gate checker; never substitutes for independent review."""
import argparse
import json
import pathlib
import sys

BRANCHES = ('5.5.38', '5.6.40')
MAGENTOS = ('1.9.2', '1.9.3')
REQUIRED = ('source_integrity', 'source_patch_review', 'cli_cgi_security',
            'regression_review', 'apache_mod_php', 'apache_security_battery',
            'package_install_rollback', 'independent_security_review')


def check(data):
    errors = []
    if data.get('schema_version') != 1:
        errors.append('schema_version must be 1')
    branches = data.get('branches', {})
    if not isinstance(branches, dict):
        return ['branches must be an object']
    for branch in BRANCHES:
        record = branches.get(branch, {})
        if not isinstance(record, dict):
            errors.append(f'{branch}: invalid branch object')
            continue
        for gate in REQUIRED:
            if record.get(gate) is not True:
                errors.append(f'{branch}: {gate} not passed')
        magento = record.get('magento', {})
        if not isinstance(magento, dict):
            errors.append(f'{branch}: magento matrix missing')
            continue
        for version in MAGENTOS:
            if magento.get(version) is not True:
                errors.append(f'{branch}: Magento {version} not passed')
        evidence = record.get('evidence_refs', [])
        if not isinstance(evidence, list) or not evidence or not all(isinstance(x, str) and x.strip() for x in evidence):
            errors.append(f'{branch}: evidence_refs required')
    return errors


def main():
    p = argparse.ArgumentParser()
    p.add_argument('evidence_json', type=pathlib.Path)
    args = p.parse_args()
    data = json.loads(args.evidence_json.read_text(encoding='utf-8'))
    errors = check(data)
    for err in errors:
        print('BLOCKED:', err)
    if errors:
        print(f'RELEASE BLOCKED: {len(errors)} outstanding gates')
        return 1
    print('All declared gates marked passed; independently verify linked evidence before release.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
