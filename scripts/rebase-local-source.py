#!/usr/bin/env python3
"""Rebase source-specific SAPI pointer cleanup and multipart INI registration.
Requires a CLEAN, locally supplied PHP 5.5.38 or 5.6.40 source checkout.
Outputs a standalone unified patch; does not mutate source.
"""
import argparse, difflib, pathlib, re, sys
p=argparse.ArgumentParser()
p.add_argument('--source',type=pathlib.Path,required=True)
p.add_argument('--branch',choices=['5.5.38','5.6.40'],required=True)
p.add_argument('--output',type=pathlib.Path,required=True)
a=p.parse_args()
root=a.source.resolve()
ver=(root/'main/php_version.h')
if not ver.is_file(): sys.exit('ERROR: main/php_version.h missing')
v=ver.read_text(errors='replace')
m=re.search(r'^#define\s+PHP_VERSION\s+"([^"]+)"',v,re.M)
if not m or m.group(1)!=a.branch: sys.exit(f'ERROR: expected PHP {a.branch}; found {m.group(1) if m else "unknown"}')
changes={}
def load(name):
    path=root/name
    if not path.is_file(): sys.exit(f'ERROR: missing {name}')
    data=path.read_bytes()
    if b'\r\n' in data: sys.exit(f'ERROR: CRLF source unsupported: {name}')
    return data.decode('latin1')
sapi=load('main/SAPI.c')
# Only insert after explicit efree(SG(request_info).FIELD) occurrences.
# Preserve already-correct nulling. Do not modify unrelated pointers.
# PHP 5.6 removed the old POST-data request-info fields. Keep an explicit
# branch allowlist so a missing efree for an expected field fails closed.
fields_by_branch={
    '5.5.38': ['post_data','raw_post_data','auth_user','auth_password','auth_digest','content_type_dup','current_user'],
    '5.6.40': ['auth_user','auth_password','auth_digest','content_type_dup','current_user'],
}
fields=fields_by_branch[a.branch]
if a.branch=='5.6.40':
    for obsolete in ('post_data','raw_post_data'):
        if re.search(r'SG\(request_info\)\.'+obsolete+r'\b',sapi):
            sys.exit(f'ERROR: unexpected legacy request field {obsolete} in PHP 5.6 SAPI.c; manual audit required')
new=sapi
for field in fields:
    pattern=re.compile(r'(?m)^(?P<indent>[ \t]*)efree\(SG\(request_info\)\.'+field+r'\);(?P<nl>\n)')
    matches=list(pattern.finditer(new))
    if not matches: sys.exit(f'ERROR: expected efree for {field} in PHP {a.branch} SAPI.c; manual audit required')
    def replace(m):
        after=new[m.end():]
        following=after.split('\n',1)[0].strip()
        if following==f'SG(request_info).{field} = NULL;': return m.group(0)
        return m.group(0)+m.group('indent')+f'SG(request_info).{field} = NULL;\n'
    new=pattern.sub(replace,new)
changes['main/SAPI.c']=(sapi,new)
main=load('main/main.c')
needle='PHP_INI_ENTRY("max_multipart_body_parts"'
if needle in main: sys.exit('ERROR: INI already present; source is not a clean baseline')
lines=main.splitlines(keepends=True)
spots=[i for i,line in enumerate(lines) if re.search(r'\bPHP_INI_ENTRY\s*\(\s*"max_file_uploads"',line)]
if len(spots)!=1: sys.exit(f'ERROR: expected exactly one max_file_uploads INI entry; found {len(spots)}')
idx=spots[0]; line=lines[idx]
if not line.endswith('\n'): sys.exit('ERROR: unexpected INI source formatting')
indent=re.match(r'^\s*',line).group(0)
lines.insert(idx+1,indent+'PHP_INI_ENTRY("max_multipart_body_parts", "-1", PHP_INI_SYSTEM|PHP_INI_PERDIR, NULL)\n')
changes['main/main.c']=(main,''.join(lines))
patch=''
for name,(before,after) in changes.items():
    if before==after: sys.exit(f'ERROR: no change in {name}')
    patch+=''.join(difflib.unified_diff(before.splitlines(keepends=True),after.splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name,n=3))
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_bytes(patch.encode('latin1'))
print('WROTE',a.output,'for PHP',a.branch)
print('Review SAPI.c pointer lifetimes and cleanup ordering before building.')
