#!/usr/bin/env python3
"""Offline dependency/readiness check; never launches an emulator or contacts network."""
import json,pathlib,shutil,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=json.loads((ROOT/'environment/requirements.json').read_text())
required=['python3','make','gcc','autoconf','automake','pkg-config','m68k-linux-gnu-as','ca65','fs-uae','atari800','Xvfb','xvfb-run','xauth','xdotool','ffmpeg']
commands={name:shutil.which(name) for name in required};versions={};errors=[]
for package,wanted in spec['pinned_packages'].items():
 result=subprocess.run(['dpkg-query','-W','-f=${Version}',package],capture_output=True,text=True)
 actual=result.stdout.strip() if result.returncode==0 else None;versions[package]={'expected':wanted,'installed':actual}
 if actual!=wanted:errors.append(f'{package}: expected {wanted}, found {actual}')
for name,path in commands.items():
 if not path:errors.append(f'missing executable: {name}')
config=(ROOT/'config/mini-mig.fs-uae').read_text()
for setting in ['cpu = 68000','uae_chipset = ocs','chip_memory = 512','slow_memory = 0','fast_memory = 0','ntsc_mode = 0']:
 if setting not in config:errors.append(f'target setting absent: {setting}')
build=subprocess.run(['make','check'],cwd=ROOT,capture_output=True,text=True)
if build.returncode:errors.append('original fixture checks failed')
report={'environment':spec['name'],'previous_name':spec['previous_name'],'readiness':'blocked' if errors else 'dependencies-ready','commands':commands,'package_versions':versions,'original_fixture_checks':'pass' if build.returncode==0 else 'fail','emulator_execution':'not attempted','native_hardware_validation':'not established','published':False,'errors':errors}
out=ROOT/'evidence/environment';out.mkdir(parents=True,exist_ok=True)
(out/'startup-readiness.json').write_text(json.dumps(report,indent=2)+'\n');(out/'fixture-checks.log').write_text(build.stdout+build.stderr)
print(json.dumps(report,indent=2));sys.exit(1 if errors else 0)
