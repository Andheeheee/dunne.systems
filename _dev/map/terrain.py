import numpy as np
from PIL import Image, ImageDraw, ImageFilter
W,H=1600,1000
rng=np.random.default_rng(42)
def fbm(oct=(4,8,16,32,64,128,256),pers=0.55,seed=0):
    r=np.random.default_rng(seed);out=np.zeros((H,W));amp=1;tot=0
    for o in oct:
        g=r.random((max(2,H*o//W+2),o+2)).astype(np.float32)
        im=Image.fromarray((g*255).astype(np.uint8)).resize((W,H),Image.BICUBIC)
        out+=amp*(np.asarray(im,np.float32)/255);tot+=amp;amp*=pers
    return out/tot
# ---- land mask from polygons
m=Image.new('L',(W,H),0);d=ImageDraw.Draw(m)
east=[(640,0),(1600,0),(1600,1000),(260,1000),(300,900),(420,870),(560,860),(640,820),(700,760),(690,690),(720,600),(700,520),(735,450),(712,395),(760,350),(700,330),(690,290),(730,250),(700,180),(720,110),(680,40)]
d.polygon(east,fill=255)
kitsap=[(0,0),(450,0),(470,80),(430,160),(470,240),(420,330),(470,420),(430,520),(380,600),(400,700),(330,780),(250,820),(150,860),(0,870)]
d.polygon(kitsap,fill=255)
d.polygon([(500,470),(560,480),(585,560),(570,650),(540,720),(500,700),(490,610),(470,540)],fill=255)  # Vashon
d.polygon([(250,120),(300,110),(330,180),(290,230),(250,200)],fill=0) # little bay on kitsap
# Lake Washington
d.polygon([(880,190),(905,185),(925,260),(918,350),(935,430),(930,520),(905,560),(885,520),(892,430),(875,350),(882,260)],fill=0)
d.ellipse((935,260,975,330),fill=0)  # Lake Sammamish-ish? small
mask=np.asarray(m.filter(ImageFilter.GaussianBlur(9)),np.float32)/255
warp=fbm(seed=3)
land=(mask+ (warp-0.5)*0.35)>0.5
landf=np.asarray(Image.fromarray((land*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)),np.float32)/255
# distance-ish from coast (blur of land)
inland=np.asarray(Image.fromarray((land*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40)),np.float32)/255
# ---- height
n1=fbm(seed=7);n2=fbm((32,64,128,256,512),0.6,seed=9)
h=landf*(0.05+0.18*inland+0.22*(n1-0.3).clip(0)+0.05*n2)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
def peak(cx,cy,r,ht,rough=0.25,seed=11,ridges=0):
    dx,dy=xx-cx,(yy-cy)*1.25;dist=np.sqrt(dx**2+dy**2)/r
    rid=fbm((16,32,64,128,256),0.6,seed=seed)
    base=np.clip(1-dist,0,1)**2.1
    if ridges:
        ang=np.arctan2(dy,dx);rr=np.abs(np.sin(ang*ridges/2+rid*4))
        base=base*(0.78+0.32*rr*np.clip(dist*2,0,1))
    return ht*base*(1+rough*(rid-0.5)*2)
h+=peak(1450,840,360,1.25,0.3,ridges=11)*landf          # Rainier
h+=peak(120,150,260,0.4,0.5,seed=13)*landf     # Olympics foothills
h+=peak(1560,200,240,0.32,0.5,seed=15)*landf    # Cascades foothills
# ---- lighting (NW light)
gy,gx=np.gradient(h*420)
nx,ny,nz=-gx,-gy,np.ones_like(h);ln=np.sqrt(nx**2+ny**2+nz**2)
L=np.array([-0.6,-0.65,0.75]);L/=np.linalg.norm(L)
shade=np.clip((nx*L[0]+ny*L[1]+nz*L[2])/ln,0,1)
# ---- colors
def c(hexs):return np.array([int(hexs[i:i+2],16) for i in (1,3,5)],np.float32)
grass=c('#4fae2a');forest=c('#1f6a24');dark=c('#164d1c');beach=c('#d8c88a');rock=c('#7a6a5a');snow=c('#f6f8fb')
veg=fbm((64,128,256,512),0.6,seed=21)
col=grass[None,None,:]*(1-veg[...,None])+forest[None,None,:]*veg[...,None]
col=col*(1-np.clip((h-0.25)/0.25,0,1)[...,None])+dark*np.clip((h-0.25)/0.25,0,1)[...,None]
rk=np.clip((h-0.45)/0.15,0,1)[...,None];col=col*(1-rk)+rock*rk
sn=np.clip((h-0.55+0.12*(n2-0.5))/0.05,0,1)[...,None];col=col*(1-sn)+snow*sn
coast=np.clip(1-np.abs(landf-0.5)*6,0,1)[...,None]*0.0
bea=np.clip((0.75-landf)*4,0,1)[...,None]*land[...,None];col=col*(1-bea*0.7)+beach*bea*0.7
lit=(0.45+0.85*shade)[...,None]
col=col*lit
# water
depth=np.asarray(Image.fromarray((land*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(25)),np.float32)/255
wv=fbm((64,128,256,512,1024),0.7,seed=31)
deep=c('#1d4f9a');shal=c('#3fa0d8');foam=c('#bfe6f5')
wcol=deep*(1-depth[...,None]*1.6).clip(0,1)+shal*(depth[...,None]*1.6).clip(0,1)
wcol=wcol*(0.9+0.2*wv[...,None])
edge=np.clip((depth-0.45)*8,0,1)*(1-landf);wcol=wcol*(1-edge[...,None]*0.5)+foam*edge[...,None]*0.5
img=np.where(landf[...,None]>0.5,col,wcol)
# grain + slight vignette for the CD-ROM look
img+= (rng.random((H,W,1))-0.5)*14
vig=1-0.22*(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2)
img*=vig[...,None]
Image.fromarray(np.clip(img,0,255).astype(np.uint8)).save(__import__('pathlib').Path(__file__).resolve().parents[2]/'assets/images/map-terrain.jpg',quality=82,optimize=True,progressive=True)
import os;print(os.path.getsize(__import__('pathlib').Path(__file__).resolve().parents[2]/'assets/images/map-terrain.jpg')//1024,'KB')
