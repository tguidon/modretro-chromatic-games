"""Native 2bpp course tiles. No sampled or borrowed game artwork."""
from PIL import Image, ImageDraw

PALETTES = [
    ('rough', ['548D42','437A3E','2B5C3A','173E35']),
    ('fairway', ['9AD65B','86C34F','70AB43','326D3F']),
    ('green', ['C8E581','B3D76A','94C453','548D42']),
    ('sand', ['F4D48F','DDB56C','BE8C52','805F3C']),
    ('water', ['A5E8E0','5CC3CA','328FAF','275E83']),
    ('ink', ['9AD65B','FFE1A3','E45A55','173E35']),
    ('sprite', ['E8F8E0','FFF5D6','EF795E','173E35']),
    ('default-ui', ['173E35','326D48','BBD982','FFF0C9']),
    ('sky', ['C7EEED','87D6DF','4AAAC7','377B9C']),
]

def slope(h, x, y):
    """A gentle, readable cross slope, alternating with each green."""
    return h.get('slope', [1 if h['hole'] % 2 else -1, 1])

def draw_course(h):
    rows=h['terrain']; im=Image.new('L',(160,144),255); d=ImageDraw.Draw(im)
    attrs=[]
    codes={'r':0,'f':1,'g':2,'s':3,'w':4,'t':0}
    for y in range(18):
        for x in range(20):
            c=rows[y][x]; px=x*8; py=y*8
            attrs.append(7 if y<2 or y>=16 else codes[c])
            if y<2 or y>=16: continue
            if c=='r':
                d.rectangle((px,py,px+7,py+7),fill=170)
                for dx,dy in [(1,2),(5,0),(3,6),(7,4)]:
                    d.point((px+dx,py+dy),fill=85)
                    d.point((px+dx-1,py+dy+1),fill=255)
            elif c=='f':
                d.rectangle((px,py,px+7,py+7),fill=255 if x%3 else 170)
                d.point((px+2,py+5),fill=170 if x%3 else 255)
            elif c=='g':
                d.rectangle((px,py,px+7,py+7),fill=255)
                d.point((px+1,py+1),fill=170)
                # Chevron heads show downhill direction; actual physics uses this same slope.
                sx,sy=slope(h,x,y)
                if (x+y)%2==0:
                    xx=px+(5 if sx>0 else 2); yy=py+(5 if sy>0 else 2)
                    d.line((xx-2*sx,yy,xx,yy),fill=85)
                    d.line((xx,yy-2*sy,xx,yy),fill=85)
            elif c=='s':
                d.point((px+2,py+2),fill=85);d.point((px+6,py+5),fill=170)
                d.line((px+1,py+6,px+3,py+6),fill=170)
            elif c=='w':
                d.rectangle((px,py,px+7,py+7),fill=85)
                d.line((px+1,py+2,px+4,py+2),fill=170)
                d.line((px+3,py+6,px+6,py+6),fill=255)
            else:
                d.rectangle((px,py,px+7,py+7),fill=170)
                d.line((px+4,py+5,px+4,py+7),fill=0)
                d.polygon([(px+3,py),(px+7,py+5),(px+6,py+6),(px,py+6)],fill=0)
                d.polygon([(px+3,py),(px+5,py+4),(px+1,py+4)],fill=85)
                d.line((px+3,py+1,px+2,py+3),fill=255)
            # Inset lips join terrain tiles into connected banks and fairway contours.
            if c in 'fgsw':
                for dx,dy,edge in [(0,-1,(px,py,px+7,py)),(0,1,(px,py+7,px+7,py+7)),(-1,0,(px,py,px,py+7)),(1,0,(px+7,py,px+7,py+7))]:
                    if 0<=x+dx<20 and 0<=y+dy<18 and rows[y+dy][x+dx]!=c:
                        d.line(edge,fill=0 if c in 'sw' else 85)
                # Bevel exposed corners so fairways and hazard banks read as contours.
                for sx,sy in [(-1,-1),(1,-1),(-1,1),(1,1)]:
                    if 0<=x+sx<20 and 0<=y+sy<18 and rows[y][x+sx]!=c and rows[y+sy][x]!=c:
                        xx=px+(7 if sx>0 else 0); yy=py+(7 if sy>0 else 0)
                        d.polygon([(xx,yy),(xx-sx*3,yy),(xx,yy-sy*3)],fill=0 if c in 'sw' else 85)
    # Taller original conifers sit over matching rough tiles. The trunk tile remains
    # the collision footprint; keep every canopy out of the HUD and neighboring fairway.
    for y in range(3,16):
        for x in range(1,19):
            if rows[y][x]!='t':continue
            if not all(rows[yy][xx] in 'rt' for yy in [y-1,y] for xx in [x-1,x,x+1]):continue
            cx=x*8+4;by=y*8+7
            d.ellipse((cx-4,by-2,cx+7,by),fill=85)
            d.rectangle((cx-1,by-5,cx+1,by-1),fill=0)
            for top,width in [(by-17,4),(by-13,5),(by-9,6)]:
                d.polygon([(cx,top),(cx+width,top+7),(cx-width,top+7)],fill=0)
                d.polygon([(cx,top+1),(cx+2,top+5),(cx-width+2,top+5)],fill=170)
                d.line((cx-1,top+3,cx-2,top+5),fill=255)
    tx,ty=h['tee']; d.rectangle((tx*8+1,ty*8+5,tx*8+6,ty*8+6),fill=0)
    hx,hy=h['cup']; d.ellipse((hx*8+2,hy*8+3,hx*8+5,hy*8+5),fill=0)
    unique={im.crop((x,y,x+8,y+8)).tobytes() for y in range(0,144,8) for x in range(0,160,8)}
    assert len(unique)<=128, (h['hole'],len(unique),'would overwrite HUD font')
    print(f'Hole {h["hole"]}: {len(unique)}/128 course tiles')
    return im,attrs
