#!/usr/bin/env python3
"""Original cloud-isolation probe; run concurrently in TWO published-env tasks.
Not an emulator test. A successful local run does not verify cloud isolation.
"""
import argparse,json,os,pathlib,socket,time
p=argparse.ArgumentParser();p.add_argument('token',choices=['micro-mig-probe-a','micro-mig-probe-b']);p.add_argument('--hold-seconds',type=int,default=30);args=p.parse_args()
if not 1<=args.hold_seconds<=30:p.error('hold-seconds must be 1..30')
# Intentionally identical path/loopback port: independent cloud runtimes must not conflict.
folder=pathlib.Path('/tmp/micro-mig-isolation-probe');folder.mkdir(exist_ok=True)
marker=folder/'owner';owned=False;sock=socket.socket();report={'token':args.token,'hostname':socket.gethostname(),'pid':os.getpid(),'port':47651,'cloud_publication_verified':False}
try:
 with marker.open('x') as f:f.write(args.token);owned=True
 sock.bind(('127.0.0.1',47651));sock.listen(1)
 for key,path in [('net_namespace','/proc/self/ns/net'),('mount_namespace','/proc/self/ns/mnt')]:
  try:report[key]=os.readlink(path)
  except OSError:report[key]=None
 print(json.dumps({**report,'status':'holding-original-probe'}),flush=True)
 for _ in range(args.hold_seconds):
  if marker.read_text()!=args.token:raise RuntimeError('marker changed by another task')
  time.sleep(1)
 report['status']='probe-completed';report['marker_remained_owned']=True
except Exception as e:
 report['status']='probe-failed';report['error']=str(e);raise
finally:
 sock.close()
 if owned and marker.exists() and marker.read_text()==args.token:marker.unlink()
 print(json.dumps(report),flush=True)
