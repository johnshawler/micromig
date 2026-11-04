"""Structural checks only. No CPU execution or hardware emulation is claimed."""
from pathlib import Path
import struct,json,hashlib
root=Path(__file__).resolve().parents[1];b=root/'build';results=[]
a=(b/'mini-mig.adf').read_bytes();assert len(a)==901120 and a[:4]==b'DOS\0'
s=0
for word in struct.unpack('>256I',a[:1024]):
    s+=word;s=(s&0xffffffff)+(s>>32)
assert s==0xffffffff;results.append('ADF size, DOS0 signature and independent boot checksum: PASS')
x=(b/'atari-original.xex').read_bytes();assert x[:2]==b'\xff\xff';pos=2;segments=[]
while pos<len(x):
    lo,hi=struct.unpack_from('<HH',x,pos);pos+=4;assert lo<=hi
    data=x[pos:pos+hi-lo+1];assert len(data)==hi-lo+1;pos+=len(data);segments.append((lo,hi,data))
assert [(lo,hi) for lo,hi,_ in segments]==[(0x2000,0x26ff),(0x2e0,0x2e1)]
assert segments[1][2]==b'\x00\x20'
dl=segments[0][2][0x100:0x100+40];assert dl[:6]==bytes([0x70,0x70,0x70,0x4f,0,0x22])
assert dl[6:37]==bytes([0x0f]*31) and dl[37:40]==bytes([0x41,0,0x21])
results.append('XEX segment bounds, RUNAD and 32-line ANTIC display list: PASS')
for line in (b/'SHA256SUMS').read_text().splitlines():
    digest,name=line.split('  ');assert hashlib.sha256((b/name).read_bytes()).hexdigest()==digest
results.append('Build artifact SHA-256 manifest: PASS')
m=json.loads((root/'optional/manifest.json').read_text())
for entry in m:
    if 'path' not in entry:continue
    p=root/'optional'/entry['path'];entry['bytes']=p.stat().st_size;entry['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
(root/'optional/manifest.json').write_text(json.dumps(m,indent=2)+'\n')
results.append('Optional fetched sources indexed and hashed; none executed')
report='\n'.join(results)+'\nNative Amiga, Atari800 and physical hardware execution: NOT RUN\n'
(root/'evidence/structural-checks.txt').write_text(report);print(report,end='')
