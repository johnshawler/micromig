#!/usr/bin/env python3
"""Reviewed install preparation. --plan performs no network or emulator execution."""
import argparse,json,os,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=json.loads((ROOT/'environment/requirements.json').read_text())
p=argparse.ArgumentParser();p.add_argument('action',choices=['plan','install'],default='plan',nargs='?');args=p.parse_args()
pins=[f'{name}={version}' for name,version in spec['pinned_packages'].items()]
cmd=['apt-get','install','--no-install-recommends','-y',*pins,*spec['build_and_capture_packages']]
print(json.dumps({'name':spec['name'],'previous_name':spec['previous_name'],'snapshot':spec['package_snapshot'],'commands':[['apt-get','-o','APT::Update::Error-Mode=any','update'],cmd],'network_attempted':False,'publication_performed':False},indent=2),flush=True)
if args.action=='plan':sys.exit(0)
osinfo={}
for line in pathlib.Path('/etc/os-release').read_text().splitlines():
 if '=' in line:
  k,v=line.split('=',1);osinfo[k]=v.strip('"')
arch=subprocess.check_output(['dpkg','--print-architecture'],text=True).strip()
if osinfo.get('ID')!='debian' or osinfo.get('VERSION_ID')!='13' or arch!='amd64':
 sys.exit('This proposed pin set requires Debian 13 amd64; create/review a separate lock for another base.')
if os.geteuid()!=0:sys.exit('Installation requires the environment setup owner/root; do not bypass filesystem permissions.')
# Require the operator to keep the existing fixed snapshot configured. Never rewrite it here.
sources=[]
for path in [pathlib.Path('/etc/apt/sources.list'),*pathlib.Path('/etc/apt/sources.list.d').glob('*'),*pathlib.Path('/etc/apt/applied-artifactory/sources.list.d').glob('*')]:
 if path.is_file():
  try:sources.append(path.read_text())
  except PermissionError:sys.exit('APT source is unreadable; resolve setup access first.')
if not any(spec['package_snapshot'] in text and 'contrib' in text for text in sources):
 sys.exit('Required fixed Debian snapshot with main/contrib is not configured. Resolve this in environment setup; this script will not change sources or route around restrictions.')
subprocess.run(['apt-get','-o','APT::Update::Error-Mode=any','update'],check=True)
subprocess.run(cmd,check=True,env={**os.environ,'DEBIAN_FRONTEND':'noninteractive'})
evidence=ROOT/'evidence/environment';evidence.mkdir(parents=True,exist_ok=True)
# Save exact versions of the complete successful installation; no pretend lock before success.
lock=subprocess.check_output(['dpkg-query','-W','-f=${binary:Package}\t${Version}\n'],text=True)
(evidence/'resolved-packages.tsv').write_text(lock)
subprocess.run([sys.executable,str(ROOT/'environment/startup.py')],check=True)
