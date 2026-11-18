"""Native 2bpp course tiles. No sampled or borrowed game artwork."""
from PIL import Image, ImageDraw
from course_shapes import raster

PALETTES = [
    ('rough', ['548D42','437A3E','2B5C3A','173E35']),
    ('fairway', ['9AD65B','86C34F','437A3E','2B5C3A']),
    ('green', ['C8E581','B3D76A','9AD65B','437A3E']),
    ('sand', ['F4D48F','BE8C52','9AD65B','437A3E']),
    ('water', ['A5E8E0','5CC3CA','437A3E','275E83']),
    ('ink', ['9AD65B','FFE1A3','E45A55','173E35']),
    ('sprite', ['E8F8E0','FFF5D6','EF795E','173E35']),
    ('default-ui', ['173E35','326D48','BBD982','FFF0C9']),
    ('sky', ['C7EEED','87D6DF','4AAAC7','377B9C']),
]

def draw_course(h):
    terrain=raster(h); im=Image.new('L',(160,144),255); attrs=[]
    def at(x,y):return terrain.getpixel((max(0,min(159,x)),max(0,min(143,y))))
    for ty in range(18):
        for tx in range(20):
            cells={at(x,y) for y in range(ty*8,ty*8+8) for x in range(tx*8,tx*8+8)}
            pal=7 if ty<2 or ty>=16 else 4 if 4 in cells else 3 if 3 in cells else 2 if 2 in cells else 1 if 1 in cells else 0
            attrs.append(pal)
            if pal==7:continue
            for y in range(ty*8,ty*8+8):
                for x in range(tx*8,tx*8+8):
                    c=at(x,y);edge=any(at(x+dx,y+dy)!=c for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)])
                    rough=1 if pal==0 else 2 if pal in (1,4) else 3
                    if c in (0,5):
                        v=rough
                        if pal==0 and (x%8,y%8) in [(1,2),(5,6)]:v=2
                        if pal==0 and (x%16,y%16)==(8,11):v=0
                    elif c==1:
                        v=0 if pal==1 else 2 if pal in (2,3) else 2
                        if pal==1:
                            # Mown bands follow the diagonal rather than the tile grid.
                            v=1 if ((x+y//3)//6)%2 else 0
                            if edge:v=2
                    elif c==2:
                        v=0 if pal==2 else 2
                        if pal==2 and edge:v=1
                        if pal==2 and (x%8,y%8)==(2,2):v=1
                    elif c==3:
                        v=1 if edge or (x%8,y%8)==(3,5) else 0
                    else:
                        v=3 if edge else 1
                        if not edge and (y%6==2 and x%13 in (3,4,5,6)):v=0
                    im.putpixel((x,y),255-v*85)
    d=ImageDraw.Draw(im)
    # Sparse slope marks, clipped to the actual green interior.
    sx,sy=h['slope']
    for y in range(20,124,8):
        for x in range(4,156,8):
            if all(at(xx,yy)==2 for xx in range(x-2,x+3) for yy in range(y-2,y+3)):
                d.line((x-2*sx,y,x,y),fill=170);d.line((x,y-2*sy,x,y),fill=170)
    # Native conifers, with shadows and layered highlights over rough only.
    for y,row in enumerate(h['terrain']):
        for x,c in enumerate(row):
            if c!='t' or y<3 or y>15:continue
            cx=x*8+4;by=y*8+7
            if not all(at(xx,yy) in (0,5) for yy in range(by-17,by+1) for xx in range(max(0,cx-6),min(160,cx+7))):
                # A compact tree still makes the trunk collision visible beside a fairway.
                d.polygon([(cx,by-7),(cx+3,by-2),(cx-3,by-2)],fill=0)
                d.line((cx,by-6,cx-1,by-3),fill=255);d.line((cx,by-2,cx,by),fill=0)
                continue
            d.ellipse((cx-4,by-2,cx+6,by),fill=85)
            d.rectangle((cx-1,by-5,cx+1,by-1),fill=0)
            for top,width in [(by-17,4),(by-13,5),(by-9,6)]:
                d.polygon([(cx,top),(cx+width,top+7),(cx-width,top+7)],fill=0)
                d.polygon([(cx,top+1),(cx+2,top+5),(cx-width+2,top+5)],fill=170)
                d.line((cx-1,top+3,cx-2,top+5),fill=255)
    tx,ty=h['tee'];d.rectangle((tx*8,ty*8+4,tx*8+1,ty*8+6),fill=0);d.rectangle((tx*8+7,ty*8+4,tx*8+8,ty*8+6),fill=0)
    hx,hy=h['cup'];d.ellipse((hx*8+2,hy*8+3,hx*8+5,hy*8+5),fill=0)
    unique={im.crop((x,y,x+8,y+8)).tobytes() for y in range(0,144,8) for x in range(0,160,8)}
    assert len(unique)<=128, (h['hole'],len(unique),'would overlap the bank 0 HUD')
    print(f'Hole {h["hole"]}: {len(unique)}/128 course tiles')
    return im,attrs,terrain
