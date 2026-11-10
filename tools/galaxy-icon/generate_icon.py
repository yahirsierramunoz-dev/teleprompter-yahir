import sys
import asyncio, base64, json, sys
from playwright.async_api import async_playwright

JS = r"""
(cfg) => {
  const N = 1024;
  const hash=(x,y,s)=>{let n=Math.sin(x*127.1+y*311.7+s*74.7)*43758.5453;return n-Math.floor(n);};
  const vn=(x,y,s)=>{const xi=Math.floor(x),yi=Math.floor(y),xf=x-xi,yf=y-yi;
    const u=xf*xf*(3-2*xf),v=yf*yf*(3-2*yf);
    const a=hash(xi,yi,s),b=hash(xi+1,yi,s),c=hash(xi,yi+1,s),d=hash(xi+1,yi+1,s);
    return (a+(b-a)*u)*(1-v)+(c+(d-c)*u)*v;};
  const fbm=(x,y,s,o)=>{let sum=0,amp=.5,f=1,norm=0;for(let i=0;i<o;i++){sum+=amp*vn(x*f,y*f,s+i*3.1);norm+=amp;f*=2.03;amp*=.5;}return sum/norm;};
  const sm=(a,b,x)=>{const t=Math.min(1,Math.max(0,(x-a)/(b-a)));return t*t*(3-2*t);};
  const mix=(a,b,t)=>a+(b-a)*t;

  const cv=document.createElement('canvas');cv.width=N;cv.height=N;
  const ctx=cv.getContext('2d');
  const img=ctx.createImageData(N,N);
  const pa=cfg.pa*Math.PI/180, cs=Math.cos(pa), sn=Math.sin(pa);
  const S=cfg.seed;
  for(let j=0;j<N;j++){
    for(let i=0;i<N;i++){
      const x0=(i/N)*2-1, y0=(j/N)*2-1;
      let xr=x0*cs+y0*sn, yr=-x0*sn+y0*cs;
      yr/=cfg.incl;
      const r=Math.hypot(xr,yr)/cfg.R;
      const th=Math.atan2(yr,xr);
      const nx=xr*4, ny=yr*4;
      const phi=th-cfg.k*Math.log(r+0.05);
      const warp=(fbm(nx,ny,S,4)-0.5)*1.8;
      const a=0.5+0.5*Math.cos(cfg.m*phi+warp*2.6);
      const armShape=Math.pow(a,cfg.sharp);
      const disc=Math.exp(-r*cfg.fall)*(1-sm(0.82,1.08,r))*sm(0.02,0.18,r);
      const fine=fbm(nx*3,ny*3,S+5,4);
      const armDens=disc*(0.12+armShape*1.7)*(0.45+fine*1.0);
      const ad=0.5+0.5*Math.cos(cfg.m*(phi+cfg.dustShift)+warp*2.6);
      let dust=Math.pow(ad,3.0)*sm(0.07,0.28,r)*(1-sm(0.55,0.95,r))*(0.45+fbm(nx*5,ny*5,S+9,4)*1.0)*cfg.dust;
      dust=Math.min(0.88,dust);
      const bl=r/cfg.rb;
      const bulge=1/Math.pow(1+bl*bl,1.55);
      const nucleus=Math.exp(-r*r/0.0011)*2.4;
      const hv=Math.max(0,fbm(nx*7,ny*7,S+13,3)-0.54)*2.3;
      const hii=Math.pow(hv,2.0)*armShape*disc*cfg.hii;
      const tcol=sm(0.08,0.75,r);
      const ar=mix(cfg.arm1[0],cfg.arm2[0],tcol), ag=mix(cfg.arm1[1],cfg.arm2[1],tcol), ab=mix(cfg.arm1[2],cfg.arm2[2],tcol);
      let R_=cfg.bulgeCol[0]*(bulge*cfg.bulgeGain+nucleus*cfg.nucGain)+ar*armDens*cfg.armGain+cfg.hiiCol[0]*hii;
      let G_=cfg.bulgeCol[1]*(bulge*cfg.bulgeGain+nucleus*cfg.nucGain)+ag*armDens*cfg.armGain+cfg.hiiCol[1]*hii;
      let B_=cfg.bulgeCol[2]*(bulge*cfg.bulgeGain+nucleus*cfg.nucGain)+ab*armDens*cfg.armGain+cfg.hiiCol[2]*hii;
      const dk=1-dust;
      R_*=dk;G_*=dk;B_*=dk;
      const halo=Math.exp(-r*1.5)*cfg.haloAmt;
      R_+=cfg.halo[0]*halo;G_+=cfg.halo[1]*halo;B_+=cfg.halo[2]*halo;
      const vig=1-0.55*Math.min(1,Math.hypot(x0,y0)*0.9);
      R_+=cfg.bg[0]*vig;G_+=cfg.bg[1]*vig;B_+=cfg.bg[2]*vig;
      const ex=cfg.exposure;
      const o=(j*N+i)*4;
      img.data[o]=Math.pow(1-Math.exp(-R_*ex),1/1.12)*255;
      img.data[o+1]=Math.pow(1-Math.exp(-G_*ex),1/1.12)*255;
      img.data[o+2]=Math.pow(1-Math.exp(-B_*ex),1/1.12)*255;
      img.data[o+3]=255;
    }
  }
  ctx.putImageData(img,0,0);
  // stars
  let seed=cfg.seed*9301+49297; const rnd=()=>{seed=(seed*9301+49297)%233280;return seed/233280;};
  ctx.globalCompositeOperation='lighter';
  const star=(x,y,rad,col,al)=>{const g=ctx.createRadialGradient(x,y,0,x,y,rad);
    g.addColorStop(0,`rgba(${col},${al})`);g.addColorStop(.35,`rgba(${col},${al*0.35})`);g.addColorStop(1,`rgba(${col},0)`);
    ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,rad,0,7);ctx.fill();};
  const cols=cfg.warmStars?['255,250,235','215,235,255','255,225,150','255,190,110','255,240,200']:['255,255,255','215,235,255','255,240,215','255,215,235','225,255,245'];
  const wts=cfg.warmStars?[.42,.06,.34,.14,.04]:[.55,.2,.12,.08,.05];
  const pick=()=>{let t=rnd(),c=0;for(let i=0;i<5;i++){c+=wts[i];if(t<=c)return cols[i];}return cols[0];};
  // sparse background + denser around galaxy
  for(let n=0;n<700;n++){
    const x=rnd()*N,y=rnd()*N; const d=Math.hypot(x/N-.5,y/N-.5);
    if(rnd()>1-d*0.9+0.25) continue;
    const big=rnd()<0.06;
    star(x,y,big?(2.5+rnd()*3.5):(0.7+rnd()*1.5),pick(),0.35+rnd()*0.65);
  }
  // galaxy field stars (inside disc ellipse)
  for(let n=0;n<420;n++){
    const rr=Math.sqrt(rnd())*cfg.R*0.95, an=rnd()*Math.PI*2;
    let ex=rr*Math.cos(an), ey=rr*Math.sin(an)*cfg.incl;
    const x0=ex*Math.cos(-pa)-ey*Math.sin(-pa), y0=ex*Math.sin(-pa)+ey*Math.cos(-pa);
    star((x0+1)/2*N,(y0+1)/2*N,0.6+rnd()*1.2,pick(),0.3+rnd()*0.6);
  }
  // few bright foreground stars with diffraction spikes
  for(let n=0;n<cfg.spikes;n++){
    const x=(0.12+rnd()*0.76)*N,y=(0.12+rnd()*0.76)*N;
    if(Math.hypot(x/N-.5,y/N-.5)<0.12){n--;continue;}
    const rad=5+rnd()*4;
    star(x,y,rad*2.2,'255,250,240',0.9);
    ctx.strokeStyle='rgba(255,250,240,0.35)';ctx.lineWidth=1.1;
    const L=rad*(4+rnd()*3);
    ctx.beginPath();ctx.moveTo(x-L,y);ctx.lineTo(x+L,y);ctx.moveTo(x,y-L);ctx.lineTo(x,y+L);ctx.stroke();
  }
  ctx.globalCompositeOperation='source-over';
  // final rounded + downscale
  const OUT=cfg.OUT||512;
  const out=document.createElement('canvas');out.width=OUT;out.height=OUT;
  const oc=out.getContext('2d');
  const rad=OUT*0.222;
  oc.beginPath();if(cfg.rounded===false){oc.rect(0,0,OUT,OUT);}else{oc.roundRect(0,0,OUT,OUT,rad);}oc.clip();
  oc.imageSmoothingEnabled=true;oc.imageSmoothingQuality='high';
  oc.drawImage(cv,0,0,OUT,OUT);
  return out.toDataURL('image/png');
}
"""

VARIANTS = {
 "A4_oro_teal": dict(seed=3, pa=-18, incl=0.66, R=1.0, m=2, k=2.1, sharp=2.2, fall=2.3, rb=0.17, dust=1.05, dustShift=0.30,
    hii=4.0, armGain=2.6, exposure=1.7, haloAmt=0.10, bulgeGain=2.8, nucGain=1.7, warmStars=True,
    bulgeCol=[1.0,0.88,0.50], arm1=[1.0,0.84,0.24], arm2=[0.30,0.62,0.78], hiiCol=[1.0,0.78,0.15],
    halo=[0.12,0.45,0.55], bg=[0.004,0.009,0.016], spikes=1),
 "A2_dorada_total": dict(seed=3, pa=-18, incl=0.66, R=1.0, m=2, k=2.1, sharp=2.2, fall=2.3, rb=0.17, dust=1.05, dustShift=0.30,
    hii=4.0, armGain=2.6, exposure=1.7, haloAmt=0.07, bulgeGain=2.8, nucGain=1.7, warmStars=True,
    bulgeCol=[1.0,0.88,0.50], arm1=[1.0,0.84,0.24], arm2=[1.0,0.52,0.10], hiiCol=[1.0,0.78,0.15],
    halo=[0.55,0.32,0.05], bg=[0.006,0.006,0.010], spikes=1),
 "A3_dorada_azul": dict(seed=3, pa=-18, incl=0.66, R=1.0, m=2, k=2.1, sharp=2.2, fall=2.3, rb=0.17, dust=1.05, dustShift=0.30,
    hii=4.0, armGain=2.4, exposure=1.6, haloAmt=0.12, bulgeGain=2.8, nucGain=1.7, warmStars=True,
    bulgeCol=[1.0,0.86,0.45], arm1=[1.0,0.80,0.28], arm2=[0.45,0.55,0.95], hiiCol=[1.0,0.72,0.18],
    halo=[0.45,0.40,0.35], bg=[0.008,0.008,0.014], spikes=1),

 "A_espiral_calida": dict(seed=3, pa=-18, incl=0.66, R=1.0, m=2, k=2.1, sharp=2.2, fall=2.3, rb=0.17, dust=1.05, dustShift=0.30,
    hii=3.5, armGain=2.2, exposure=1.55, haloAmt=0.10, bulgeGain=2.6, nucGain=1.6,
    bulgeCol=[1.0,0.80,0.52], arm1=[1.0,0.80,0.55], arm2=[0.38,0.58,1.0], hiiCol=[1.0,0.35,0.62],
    halo=[0.20,0.55,0.75], bg=[0.004,0.010,0.022], spikes=1),
 "B_frontal_azul": dict(seed=11, pa=24, incl=0.92, R=0.98, m=2, k=2.7, sharp=2.5, fall=2.1, rb=0.13, dust=1.2, dustShift=0.34,
    hii=4.5, armGain=2.3, exposure=1.55, haloAmt=0.09, bulgeGain=2.6, nucGain=1.6,
    bulgeCol=[1.0,0.86,0.62], arm1=[0.75,0.82,1.0], arm2=[0.30,0.48,1.0], hiiCol=[1.0,0.30,0.55],
    halo=[0.25,0.35,0.85], bg=[0.004,0.006,0.020], spikes=1),
 "C_dorada_referencia": dict(seed=21, pa=-32, incl=0.58, R=1.0, m=2, k=1.9, sharp=1.8, fall=1.8, rb=0.22, dust=1.2, dustShift=0.26,
    hii=2.5, armGain=2.2, exposure=1.55, haloAmt=0.14, bulgeGain=3.2, nucGain=1.8,
    bulgeCol=[1.0,0.84,0.60], arm1=[1.0,0.62,0.34], arm2=[0.22,0.62,0.95], hiiCol=[1.0,0.55,0.7],
    halo=[0.10,0.50,0.70], bg=[0.003,0.010,0.018], spikes=1),
}


async def main():
    import copy
    dest=sys.argv[1] if len(sys.argv)>1 else "."
    base=VARIANTS["B_frontal_azul"]
    jobs=[("icon-512.png",{"OUT":512}),("icon-192.png",{"OUT":192}),("icon-180.png",{"OUT":180}),
          ("icon-512-maskable.png",{"OUT":512,"rounded":False,"R":base["R"]*0.74})]
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(); await pg.set_content("<html><body></body></html>")
        for name,ov in jobs:
            cfg=copy.deepcopy(base); cfg.update(ov)
            data=await pg.evaluate(JS,cfg)
            open(f"{dest}/{name}","wb").write(base64.b64decode(data.split(",")[1])); print("wrote",name)
        await b.close()
asyncio.run(main())
