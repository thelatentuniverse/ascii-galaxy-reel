"""
render_galaxy_reel.py
---------------------
Renders a vertical (1080x1920, 30 fps, 20 s) "code art" reel:
  * top:    a spiral galaxy forming, drawn entirely in text characters
  * bottom: a code editor where galaxy.py types itself out, line by line

Usage:
  python src/render_galaxy_reel.py                     # full video with sound -> galaxy_reel.mp4
  python src/render_galaxy_reel.py --preview 5 14      # quick still frames
  python src/render_galaxy_reel.py --label "@yourhandle"
"""
import numpy as np, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
LABEL='galaxy.py · 2026'
W,H,FPS,DUR=1080,1920,30,20.0; NF=int(FPS*DUR)
import os
def _find(names):
    dirs=['/usr/share/fonts/truetype/dejavu','/Library/Fonts',os.path.expanduser('~/Library/Fonts'),'C:/Windows/Fonts','.']
    for d in dirs:
        for n in names:
            p=os.path.join(d,n)
            if os.path.exists(p): return p
    raise SystemExit('Monospace font not found: put DejaVuSansMono.ttf next to this script')
MONO=_find(['DejaVuSansMono.ttf','consola.ttf','Menlo.ttc'])
MONOI=_find(['DejaVuSansMono-Oblique.ttf','consolai.ttf','Menlo.ttc'])
def sm(x): x=np.clip(x,0,1); return x*x*(3-2*x)
# ---------------- art: glyph atlas ----------------
RAMP=" .'`,:;-~=+*xo%#&@"
CW,CH=10,17; COLS,ROWS=W//CW,1000//CH
gf=ImageFont.truetype(MONO,15)
atlas=np.zeros((len(RAMP),CH,CW),np.float32)
for k,c in enumerate(RAMP):
    im=Image.new('L',(CW,CH),0);d=ImageDraw.Draw(im);d.text((CW/2,CH/2),c,font=gf,fill=255,anchor='mm');atlas[k]=np.asarray(im)/255
ARMS,PITCH,R_DISK,R_BULGE,TILT=2,np.radians(13),0.42,0.07,np.radians(58)
rng=np.random.default_rng(7)
NS=9000
sr=rng.exponential(R_DISK*0.45,NS);sth=rng.uniform(0,2*np.pi,NS);hot=rng.random(NS)<0.05
# arm-concentrate stars: shift angle toward arm crest
crest=np.log(sr+1e-3)/np.tan(PITCH)+np.pi*rng.integers(0,2,NS)
mix=rng.random(NS)<0.55
sth=np.where(mix,crest+rng.normal(0,0.35,NS),sth)
x=np.linspace(-0.6,0.6,COLS);y=np.linspace(-0.6,0.6,ROWS)*ROWS*CH/(COLS*CW)
X,Y=np.meshgrid(x,y)
ARGB=np.zeros((ROWS,COLS))
def art(t):
    form=sm(t/5);amp=sm((t-4)/6);tilt=TILT*sm((t-10)/6);spin=0.12*t
    ct=max(np.cos(tilt),0.3)
    Yp=Y/ct;r=np.hypot(X,Yp);th=np.arctan2(Yp,X)-spin
    rd=R_DISK*(2.2-1.2*form)
    disk=np.exp(-r/rd)*(0.25+0.75*form)*sm((0.62-r)/0.12)
    ph=ARMS*(th-np.log(r+1e-3)/np.tan(PITCH)-0.6*t)
    wave=1+1.3*amp*np.cos(ph)
    lane=1-0.6*amp*sm((np.cos(ph-0.7)-0.6)*3)
    clump=1+0.35*np.sin(37*X+5*t)*np.sin(31*Yp-3*t)*(1-form)  # turbulent gas early
    L=disk*wave*lane*clump
    B=(0.2+1.0*form)*np.exp(-(X*X+Y*Y)/(R_BULGE**2*(1+0.8*np.cos(tilt))))
    L=L*0.85+B
    # stars
    a=sth+spin+0.05*t/np.maximum(sr,0.03)
    sx=sr*np.cos(a);sy=sr*np.sin(a)*np.cos(tilt)
    sx=sx*(1.0+1.5*(1-form));sy=sy*(1.0+1.5*(1-form))
    ci=((sx+0.6)/1.2*(COLS-1)).astype(int);ri=((sy-y[0])/(y[-1]-y[0])*(ROWS-1)).astype(int)
    ok=(ci>=0)&(ci<COLS)&(ri>=0)&(ri<ROWS)
    vis=rng.random(NS)<(0.25+0.5*form)
    ok&=vis
    S=np.zeros((ROWS,COLS));np.add.at(S,(ri[ok],ci[ok]),0.18)
    Hm=np.zeros((ROWS,COLS));okh=ok&hot;np.add.at(Hm,(ri[okh],ci[okh]),1.0*amp)
    L=L+S
    Lc=L/(1+0.9*L)
    v=np.clip((Lc-0.07)/0.75,0,1)**0.85
    v=np.where(rng.random(v.shape)<0.04*v,v*0.6,v)
    i=np.clip(v*len(RAMP),0,len(RAMP)-1).astype(int)
    # colour: core gold -> arms pale blue -> outer dust brown; hot stars pink/blue
    rr=np.hypot(X,Y/ct)
    core=np.exp(-rr*rr/0.012)
    c=np.zeros((ROWS,COLS,3))
    arm=np.array([0.62,0.75,1.0]);dustc=np.array([0.85,0.55,0.32]);gold=np.array([1.0,0.82,0.48])
    w_arm=sm((wave-1)/1.2)*amp
    base=dustc[None,None,:]*(1-w_arm[...,None])+arm[None,None,:]*w_arm[...,None]
    base=base*(1-core[...,None])+gold[None,None,:]*core[...,None]
    hh=np.clip(Hm,0,1)[...,None];base=base*(1-hh)+np.array([1.0,0.45,0.75])*hh
    bright=np.clip(0.35+0.9*L,0,1.3)[...,None]
    c=base*bright
    return i,c,int((i>0).sum())
def art_img(i,c):
    A=atlas[i]                                      # ROWS,COLS,CH,CW
    img=A[...,None]*c[:,:,None,None,:]               # ROWS,COLS,CH,CW,3
    img=img.transpose(0,2,1,3,4).reshape(ROWS*CH,COLS*CW,3)
    return np.clip(img*255,0,255).astype(np.uint8)
# background stars (static)
bgs=[(rng.integers(0,W),rng.integers(0,1000),rng.uniform(0.2,0.7)) for _ in range(70)]
# ---------------- code panel ----------------
CODE=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'galaxy.py'),encoding='utf-8').read().rstrip('\n').split('\n')
fc=ImageFont.truetype(MONO,25);fci=ImageFont.truetype(MONOI,25);fs=ImageFont.truetype(MONO,22);fl=ImageFont.truetype(MONO,21)
LH=37;X0=110;TOP=1150;NV=20
KW=set('def return for in import from as if else lambda and or not while with None True False'.split())
COL={'kw':(255,121,160),'num':(255,180,110),'com':(110,128,120),'str':(160,220,140),'fn':(255,214,120),'np':(130,190,255),'txt':(214,218,226),'op':(170,176,190)}
tok=re.compile(r'(#.*$)|("[^"]*"|\'[^\']*\')|(\b\d+\.?\d*\b)|(\b[A-Za-z_]\w*\b)|(\s+)|(.)')
def toks(line):
    out=[];prev=None
    for m in tok.finditer(line):
        s=m.group(0)
        if m.group(1):k='com'
        elif m.group(2):k='str'
        elif m.group(3):k='num'
        elif m.group(4):
            k='kw' if s in KW else ('fn' if prev=='def' else ('np' if s in('np','rng') else 'txt'))
            prev=s
        elif m.group(5):k='ws'
        else:k='op'
        out.append((s,k))
    return out
TOK=[toks(l) for l in CODE]
cum=np.cumsum([len(l)+4 for l in CODE]);TOT=cum[-1]
T_TYPE=18.5
def draw_code(d,t):
    nch=int(TOT*min(1,t/T_TYPE))
    cur=int(np.searchsorted(cum,nch,side='right'));cur=min(cur,len(CODE)-1)
    done_in_cur=nch-(cum[cur-1] if cur>0 else 0)
    first=max(0,min(cur-13,len(CODE)-NV))
    for k in range(NV):
        ln=first+k
        if ln>=len(CODE) or ln>cur:break
        yy=TOP+k*LH
        fade=1.0 if k<NV-3 else (1.0-0.28*(k-(NV-4)))
        if ln==cur:
            d.rectangle([0,yy-4,W,yy+LH-6],fill=(34,24,32));d.rectangle([14,yy-4,19,yy+LH-6],fill=(255,95,150))
        d.text((X0-22,yy),f'{ln+1:>3}',font=fl,fill=tuple(int(v*fade) for v in (90,96,110)),anchor='ra')
        x=X0;limit=len(CODE[ln]) if ln<cur else done_in_cur
        used=0
        for s,k2 in TOK[ln]:
            if used>=limit:break
            s2=s[:max(0,limit-used)];used+=len(s)
            if k2=='ws':x+=fc.getlength(s2);continue
            f=fci if k2=='com' else fc
            col=tuple(int(v*fade) for v in COL[k2]);d.text((x,yy),s2,font=f,fill=col);x+=f.getlength(s2)
        if ln==cur and int(t*2.5)%2==0:d.rectangle([x+2,yy+2,x+14,yy+LH-10],fill=(240,240,245))
def frame(fi):
    t=fi/FPS
    i,c,nlet=art(t)
    img=np.zeros((H,W,3),np.uint8)
    img[0:ROWS*CH,0:COLS*CW]=art_img(i,c)
    im=Image.fromarray(img);d=ImageDraw.Draw(im)
    for (bx,by,b) in bgs:
        if i[min(by//CH,ROWS-1),min(bx//CW,COLS-1)]==0:
            v=int(255*b*(0.6+0.4*np.sin(t*2+bx)));d.text((bx,by),'.',font=gf,fill=(v,v,int(v*0.9)))
    # overlays
    d.ellipse([W-262,150,W-252,160],fill=(255,95,150));d.text((W-240,141),f't {t:05.2f}s',font=fs,fill=(240,200,215))
    d.text((44,985),LABEL,font=fs,fill=(150,156,170))
    d.text((44,1015),f'arms {2*sm((t-4)/6):.2f}   tilt {58*sm((t-10)/6):4.1f}°',font=fs,fill=(150,156,170))
    d.text((44,1045),f'letters {nlet:,}',font=fs,fill=(150,156,170))
    d.text((24,1092),'$ py galaxy.py',font=fs,fill=(225,228,235))
    d.text((W-24,1092),'running · 30 fps',font=fs,fill=(150,156,170),anchor='ra')
    d.line([0,1132,W,1132],fill=(45,48,58),width=2)
    draw_code(d,t)
    return np.asarray(im)
def main():
    import argparse, os
    ap=argparse.ArgumentParser(description='Render the ASCII galaxy code-art reel.')
    ap.add_argument('--out',default='galaxy_reel.mp4',help='output video file')
    ap.add_argument('--preview',nargs='*',type=float,help='only save preview PNGs at these seconds')
    ap.add_argument('--no-audio',action='store_true',help='skip the soundtrack')
    ap.add_argument('--label',default='galaxy.py · 2026',help='small label under the art (e.g. your handle)')
    a=ap.parse_args()
    global LABEL; LABEL=a.label
    if a.preview:
        for s in a.preview:
            Image.fromarray(frame(int(s*FPS))).save(f'preview_{s:g}.png');print('saved',f'preview_{s:g}.png')
        return
    silent='_video_silent.mp4' if not a.no_audio else a.out
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
                        '-c:v','libx264','-preset','slow','-crf','15','-tune','animation','-pix_fmt','yuv420p',silent],stdin=subprocess.PIPE)
    for fi in range(NF):
        p.stdin.write(frame(fi).tobytes())
        if fi%60==0:print(f'frame {fi}/{NF}',flush=True)
    p.stdin.close();p.wait()
    if not a.no_audio:
        from soundtrack import make_soundtrack
        make_soundtrack('_audio.wav',DUR)
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',silent,'-i','_audio.wav','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',a.out],check=True)
        os.remove(silent);os.remove('_audio.wav')
    print('done ->',a.out)

if __name__=='__main__':
    main()
