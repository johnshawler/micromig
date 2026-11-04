"""Bounded original opcode runner with register stubs; NOT an Atari emulator.
Executes only the original fixture's 8-opcode subset. No device timing, DMA,
interrupts, graphics rendering, or sound generation is modeled.
"""
from pathlib import Path
import struct,json
root=Path(__file__).resolve().parents[1];x=(root/'build/atari-original.xex').read_bytes()
mem=bytearray(65536);pos=2
while pos<len(x):
    lo,hi=struct.unpack_from('<HH',x,pos);pos+=4;n=hi-lo+1;mem[lo:hi+1]=x[pos:pos+n];pos+=n
pc=int.from_bytes(mem[0x2e0:0x2e2],'little');a=0;zero=False;writes=[];steps=0
trace=[]
def step():
    global pc,a,zero,steps
    op=mem[pc];pc+=1;steps+=1
    if op in (0x78,0xd8):return
    if op==0xa9:a=mem[pc];pc+=1;zero=(a==0);return
    if op in (0xad,0x8d,0x4c):
        addr=int.from_bytes(mem[pc:pc+2],'little');pc+=2
        if op==0xad:a=mem[addr];zero=(a==0)
        elif op==0x8d:mem[addr]=a;writes.append([addr,a])
        else:pc=addr
        return
    if op==0xd0:
        delta=mem[pc];pc+=1
        if not zero:pc+=(delta if delta<128 else delta-256)
        return
    raise AssertionError(f'unsupported opcode {op:02x} at {pc-1:04x}')
# Reach the first input read. Independent pattern scan avoids importing emitter labels.
for _ in range(100):
    if mem[pc:pc+3]==bytes([0xad,0x10,0xd0]):break
    step()
else:raise AssertionError('initialization did not reach input poll')
loop=pc
assert mem[0xd400]==0x22 and mem[0xd402:0xd404]==bytes([0,0x21])
assert mem[0xd017]==0x0e and mem[0xd018]==0
assert mem[0xd40e]==mem[0xd20e]==0
assert mem[0xd200]==100 and mem[0xd208]==0 and mem[0xd20f]==3
for trig,bg,aud in ((1,0,0),(0,0x46,0xaf),(1,0,0)):
    mem[0xd010]=trig;before=len(writes)
    for _ in range(20):
        step()
        if pc==loop:break
    else:raise AssertionError('fixture failed to return to polling loop')
    assert writes[before:]==[[0xd01a,bg],[0xd201,aud]]
    trace.append({'TRIG0':trig,'writes':writes[before:],'instructions_total':steps})
report={'scope':'Original bounded 6502 instruction runner with register stubs only','result':'PASS','instructions':steps,'scenarios':trace,'hardware_validation':False}
(root/'evidence/fixture-trace.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
