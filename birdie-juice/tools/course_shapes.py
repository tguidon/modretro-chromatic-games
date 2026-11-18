"""Rasterize authored course contours at two-pixel terrain resolution."""
from PIL import Image, ImageDraw

def spline(points, closed=False):
    points=[tuple(p) for p in points]
    p=([points[-1]]+points+[points[0],points[1]]) if closed else [points[0]]+points+[points[-1]]
    out=[]
    for i in range(1,len(p)-2):
        a,b,c,d=p[i-1:i+3]
        for k in range(16):
            t=k/16
            out.append(tuple(.5*((2*b[j])+(-a[j]+c[j])*t+(2*a[j]-5*b[j]+4*c[j]-d[j])*t*t+(-a[j]+3*b[j]-3*c[j]+d[j])*t*t*t) for j in range(len(b))))
    return out

def raster(h):
    # Author at native pixels, then classify two-pixel cells for both art and ROM.
    im=Image.new('L',(160,144),0);d=ImageDraw.Draw(im);shapes=h['contours']
    points=spline(shapes['fairway'])
    for x,y,r in points:d.ellipse((round(x-r),round(y-r),round(x+r),round(y+r)),fill=1)
    for poly in shapes['water']:d.polygon(spline(poly,True),fill=4)
    d.polygon(spline(shapes['green'],True),fill=2)
    for poly in shapes['bunkers']:d.polygon(spline(poly,True),fill=3)
    # Preserve tree trunks as physical obstacles, not the decorative canopy.
    for y,row in enumerate(h['terrain']):
        for x,c in enumerate(row):
            if c=='t':d.rectangle((x*8,y*8,x*8+7,y*8+7),fill=5)
    # A small tee patch always remains playable.
    x,y=h['tee'];d.ellipse((x*8-2,y*8,x*8+10,y*8+8),fill=1)
    d.rectangle((0,0,159,15),fill=0);d.rectangle((0,128,159,143),fill=0)
    return im.resize((80,72),Image.Resampling.NEAREST).resize((160,144),Image.Resampling.NEAREST)
