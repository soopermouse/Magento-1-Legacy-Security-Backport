#!/usr/bin/env python3
"""Offline, read-only integrity and static packaging verification."""
import hashlib, pathlib, subprocess, sys
root = pathlib.Path(__file__).resolve().parent.parent
errors = []
manifest = root / 'SHA256SUMS'
seen = set()
for n, line in enumerate(manifest.read_text().splitlines(), 1):
    if not line.strip(): continue
    if len(line) < 67 or line[64:66] != '  ':
        errors.append(f'line {n}: invalid SHA256SUMS entry'); continue
    digest, name = line[:64], line[66:]
    if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
        errors.append(f'line {n}: invalid digest'); continue
    p = root / name
    if name in seen or p.resolve().parent != (root / name).resolve().parent or not p.is_file() or not p.resolve().is_relative_to(root):
        errors.append(f'line {n}: duplicate, missing, or unsafe path: {name}'); continue
    seen.add(name)
    if hashlib.sha256(p.read_bytes()).hexdigest() != digest:
        errors.append(f'checksum mismatch: {name}')
files = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name != 'SHA256SUMS'}
for name in sorted(files - seen): errors.append(f'unlisted file: {name}')
for name in sorted(seen - files): errors.append(f'manifest-only file: {name}')
for p in sorted((root/'scripts').glob('*.sh')):
    proc = subprocess.run(['bash', '-n', str(p)], capture_output=True, text=True)
    if proc.returncode: errors.append(f'bash syntax: {p.name}: {proc.stderr.strip()}')
for e in errors: print('FAIL:', e)
print(f'{"FAIL" if errors else "PASS"}: {len(seen)} checksums, {len(files)} packaged files, {len(errors)} errors')
sys.exit(bool(errors))
