#!/usr/bin/env python3
"""Original fixed-opcode fixture emitter, not a general assembler or translator."""
from pathlib import Path
import struct, json, hashlib
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build'
OUT.mkdir(exist_ok=True)

def boot():
    b=bytearray(b'DOS\0'+b'\0'*4+struct.pack('>I',880)); labels={}; fix=[]; listing=[]
    def emit(text,*words):
        listing.append(f'{len(b):04x}  {text}')
        b.extend(struct.pack('>'+'H'*len(words),*words))
    def label(name): labels[name]=len(b)
    def lea(name,reg):
        emit(f'lea {name}(pc),a{reg}',0x41fa+(reg<<9),0);fix.append((len(b)-2,name,'pc'))
    def branch(name,op):
        emit(f'{op:04x} branch {name}',op,0);fix.append((len(b)-2,name,'pc'))
    def move(value,reg): emit(f'move.w #${value:04x},${reg:03x}(a6)',0x3d7c,value,reg)
    emit('move.w #$2700,sr',0x46fc,0x2700)
    emit('lea $dff000,a6',0x4df9,0x00df,0xf000)
    for reg in (0x9a,0x9c,0x96): move(0x7fff,reg)
    # No bitplanes/sprites/blitter. Copper background bars and audio channel 0 only.
    for reg,value in ((0x100,0x0200),(0x8e,0x2c81),(0x90,0x2cc1),(0xa4,16),(0xa6,400),(0xa8,0)):
        move(value,reg)
    lea('sample',0);emit('move.l a0,AUD0LC(a6)',0x2d48,0x00a0)
    lea('copper',0);emit('move.l a0,COP1LC(a6)',0x2d48,0x0080)
    lea('indicator',1)
    move(0,0x88);move(0x8281,0x96)
    label('poll')
    emit('btst #6,$bfe001 ; left mouse, active low',0x0839,6,0x00bf,0xe001)
    branch('released',0x6600)
    emit('move.w #$f00,(a1)',0x32bc,0x0f00);move(64,0xa8)
    branch('poll',0x6000)
    label('released');emit('move.w #$0f0,(a1)',0x32bc,0x00f0);move(0,0xa8)
    branch('poll',0x6000)
    label('copper');emit('COLOR00',0x0180);label('indicator');emit('green/red',0x00f0)
    for words in ((0x4001,0xfffe),(0x0180,0x000f),(0x8001,0xfffe),(0x0180,0x0ff0),(0xc001,0xfffe),(0x0180,0x00ff),(0xffff,0xfffe)):
        emit('copper words',*words)
    label('sample');b.extend(bytes([64]*16+[192]*16))
    for pos,name,_ in fix: struct.pack_into('>h',b,pos,labels[name]-pos)
    used=len(b);assert used<=1024
    b.extend(bytes(1024-len(b)))
    total=0
    for n in struct.unpack('>256I',b):
        total+=n;total=(total&0xffffffff)+(total>>32)
    struct.pack_into('>I',b,4,total^0xffffffff)
    (OUT/'mini-mig.adf').write_bytes(b+bytes(901120-1024))
    (OUT/'boot.lst').write_text('\n'.join(listing)+'\n')
    return {'boot_used_bytes':used,'labels':labels,'sample_words':16,'audio_period':400,'audio_hz_estimate':3546895/(400*32)}

def atari():
    # Independent original bare-hardware XEX. Native Amiga baseline above is not a translation.
    code=bytearray(); labels={};fix=[]; listing=[]
    def emit(text,*v): listing.append(f'{0x2000+len(code):04x}  {text}');code.extend(v)
    def lda(v): emit(f'lda #${v:02x}',0xa9,v)
    def sta(addr):emit(f'sta ${addr:04x}',0x8d,addr&255,addr>>8)
    def write(addr,v):lda(v);sta(addr)
    def label(name):labels[name]=0x2000+len(code)
    def branch(op,name):emit('branch '+name,op,0);fix.append((len(code)-1,name))
    emit('sei',0x78);emit('cld',0xd8)
    for a,v in ((0xd40e,0),(0xd20e,0),(0xd400,0),(0xd01d,0),(0xd01b,0),(0xd402,0),(0xd403,0x21),(0xd017,0x0e),(0xd018,0),(0xd01a,0),(0xd208,0),(0xd20f,3),(0xd200,100),(0xd201,0)):
        write(a,v)
    write(0xd400,0x22)
    label('loop')
    emit('lda TRIG0',0xad,0x10,0xd0);branch(0xd0,'released')
    write(0xd01a,0x46);write(0xd201,0xaf)
    emit('jmp loop',0x4c,labels['loop']&255,labels['loop']>>8)
    label('released');write(0xd01a,0);write(0xd201,0)
    emit('jmp loop',0x4c,labels['loop']&255,labels['loop']>>8)
    for pos,name in fix:
        delta=labels[name]-(0x2000+pos+1);assert -128<=delta<128;code[pos]=delta&255
    assert len(code)<256
    data=bytearray(0x700);data[:len(code)]=code
    dl=bytes([0x70]*3+[0x4f,0,0x22]+[0x0f]*31+[0x41,0,0x21]);data[0x100:0x100+len(dl)]=dl
    data[0x200:]=bytes([0xaa,0x55]*640)
    # $2000-$26ff segment plus RUNAD $02e0-$02e1.
    xex=b'\xff\xff'+struct.pack('<HH',0x2000,0x26ff)+data+struct.pack('<HHH',0x02e0,0x02e1,0x2000)
    (OUT/'atari-original.xex').write_bytes(xex)
    (OUT/'atari.lst').write_text('\n'.join(listing)+'\n')
    return {'load_start':0x2000,'load_end':0x26ff,'entry':0x2000,'code_bytes':len(code),'display_list':0x2100,'screen':0x2200,'antic_mode':15,'scanlines':32,'labels':labels}

if __name__=='__main__':
    report={'native':boot(),'atari':atari()}
    (OUT/'layout.json').write_text(json.dumps(report,indent=2)+'\n')
    files=sorted(p for p in OUT.iterdir() if p.name!='SHA256SUMS' and p.is_file())
    (OUT/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files))
    print(json.dumps(report,indent=2))
