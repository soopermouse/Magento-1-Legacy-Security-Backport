#!/usr/bin/env python3
"""Fail-closed source identity and CVE touchpoint inventory; not a security test."""
import argparse, hashlib, json, pathlib, re, sys
p=argparse.ArgumentParser()
p.add_argument('source',help='extracted PHP source root')
p.add_argument('--branch',required=True,choices=['5.5','5.6'])
p.add_argument('--output',help='write JSON report')
a=p.parse_args()
root=pathlib.Path(a.source)
expected={'5.5':'5.5.38','5.6':'5.6.40'}[a.branch]
version_file=root/'main/php_version.h'
if not version_file.is_file(): sys.exit('ERROR: main/php_version.h missing')
text=version_file.read_text(errors='replace')
m=re.search(r'^#define\s+PHP_VERSION\s+"([^"]+)"',text,re.M)
if not m or m.group(1)!=expected:sys.exit('ERROR: expected PHP '+expected+', found '+(m.group(1) if m else 'unknown'))
files=['Zend/zend_alloc.c','Zend/zend_alloc.h','Zend/zend_execute_API.c','Zend/zend_llist.c','Zend/zend_strtod.c','ext/session/session.c','main/SAPI.c','main/main.c','main/rfc1867.c']
needles={'Zend/zend_alloc.c':['zend_mm','zend_mm_safe_error'], 'Zend/zend_execute_API.c':['shutdown_executor'], 'main/rfc1867.c':['multipart','Content-Disposition'], 'main/SAPI.c':['sapi_deactivate'], 'main/main.c':['php_request_shutdown'], 'ext/session/session.c':['upload_progress']}
report={'branch':a.branch,'version':expected,'source':str(root.resolve()),'files':{},'warnings':[],'status':'SOURCE_INVENTORY_ONLY'}
for rel in files:
 f=root/rel
 if not f.is_file():sys.exit('ERROR: missing '+rel)
 data=f.read_bytes(); t=data.decode('latin1')
 report['files'][rel]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'symbols':{s:len(re.findall(re.escape(s),t,re.I)) for s in needles.get(rel,[])}}
for rel,symbols in needles.items():
 for sym in symbols:
  if report['files'][rel]['symbols'][sym]==0:report['warnings'].append('No occurrence of '+sym+' in '+rel+'; inspect manually')
serialized=json.dumps(report,indent=2,sort_keys=True)+'\n'
if a.output:pathlib.Path(a.output).write_text(serialized)
print(serialized,end='')
print('NOTE: this does not apply patches or prove CVE remediation.',file=sys.stderr)
