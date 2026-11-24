#!/usr/bin/env python3
"""Generates the animated, transparent-background WhatsApp sticker pack.
Usage: python3 tools/make_stickers.py   (needs: pip install pillow, a bold Arabic-capable font)
Output: 512x512 animated WebP (<500KB each), tray.png, pack.json, launcher icon."""
import math, json, os, sys
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "app/src/main/assets")
ICON = os.path.join(ROOT, "app/src/main/res/mipmap-xxxhdpi/ic_launcher.png")
FONT = os.environ.get("STICKER_FONT", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
W, CX, CY, R, N, DUR, TAU = 1024, 512, 430, 290, 18, 55, 2 * math.pi
INK = (59, 36, 16, 255); FACE = (255, 205, 64, 255); EDGE = (222, 152, 24, 255)
WHITE = (255, 255, 255, 255); PINK = (255, 120, 140, 255); RED = (235, 60, 70, 255)
SKIN = (255, 190, 45, 255)

@lru_cache(None)
def F(n): return ImageFont.truetype(FONT, int(n))
def fade(p): return int(255 * math.sin(math.pi * p))
def tear(p, c=(90, 190, 255)): return c + (fade(p),)

def ln(d, pts, w=26, c=INK):
    d.line(pts, fill=c, width=w, joint="curve")
    for x, y in (pts[0], pts[-1]): d.ellipse([x-w/2, y-w/2, x+w/2, y+w/2], fill=c)
def eye(d, x, y, r=50, px=0, py=0, pr=24):
    d.ellipse([x-r, y-r, x+r, y+r], fill=WHITE, outline=INK, width=8)
    d.ellipse([x+px-pr, y+py-pr, x+px+pr, y+py+pr], fill=INK)
    d.ellipse([x+px-pr*.1, y+py-pr*.7, x+px+pr*.5, y+py-pr*.1], fill=WHITE)
def happy(d, x, y, w=62, h=44): d.arc([x-w, y-h, x+w, y+h], 200, 340, fill=INK, width=26)
def sleepy(d, x, y, w=62, h=34): d.arc([x-w, y-h, x+w, y+h], 20, 160, fill=INK, width=26)
def smile(d, cx, cy, w=120, h=80, wd=26, c=INK): d.arc([cx-w, cy-h, cx+w, cy+h], 25, 155, fill=c, width=wd)
def frown(d, cx, cy, w=110, h=70, wd=26): d.arc([cx-w, cy-h, cx+w, cy+h], 205, 335, fill=INK, width=wd)
def mouth(d, cx, yt, w, h, tongue=True):
    d.chord([cx-w, yt-h, cx+w, yt+h], 0, 180, fill=INK)
    d.rectangle([cx-w*.82, yt, cx+w*.82, yt+h*.2], fill=WHITE)
    if tongue: d.ellipse([cx-w*.5, yt+h*.55, cx+w*.5, yt+h*.93], fill=PINK)
def blush(d, y, dx=175):
    for s in (-1, 1): d.ellipse([CX+s*dx-48, y-28, CX+s*dx+48, y+28], fill=(255, 110, 130, 150))
def base(d, col=FACE): d.ellipse([CX-R, CY-R, CX+R, CY+R], fill=col, outline=EDGE, width=16)
def heart(d, cx, cy, s, col=RED):
    pts = [(cx + s*16*math.sin(a)**3/34, cy - s*(13*math.cos(a) - 5*math.cos(2*a) - 2*math.cos(3*a) - math.cos(4*a))/34)
           for a in [i*TAU/60 for i in range(60)]]
    d.polygon(pts, fill=col)
def drop(d, x, y, s=34, col=(90, 190, 255, 255)):
    d.polygon([(x, y-s*1.6), (x-s*.9, y-s*.2), (x+s*.9, y-s*.2)], fill=col); d.ellipse([x-s, y-s, x+s, y+s], fill=col)
def sparkle(d, x, y, s, col):
    d.polygon([(x, y-s), (x+s*.25, y-s*.25), (x+s, y), (x+s*.25, y+s*.25), (x, y+s), (x-s*.25, y+s*.25), (x-s, y), (x-s*.25, y-s*.25)], fill=col)
def flame(d, cx, by, h, w, sway):
    o, y = (255, 110, 20, 255), (255, 210, 60, 255)
    d.ellipse([cx-w, by-w*1.6, cx+w, by+w*.4], fill=o); d.polygon([(cx-w, by-w*.6), (cx+sway, by-h), (cx+w, by-w*.6)], fill=o)
    d.ellipse([cx-w*.55, by-w, cx+w*.55, by+w*.3], fill=y); d.polygon([(cx-w*.55, by-w*.4), (cx+sway*.6, by-h*.7), (cx+w*.55, by-w*.4)], fill=y)

def s_laugh(d, t):
    base(d); happy(d, CX-115, CY-70); happy(d, CX+115, CY-70); mouth(d, CX, CY+15, 165, 165)
    for s in (-1, 1):
        for ph in (0, .5):
            p = (t+ph) % 1; drop(d, CX+s*(160+p*60), CY-20+p*140, 28-p*10, tear(p))
def s_ok(d, t):
    base(d); eye(d, CX-115, CY-60); happy(d, CX+115, CY-55, 52, 32); mouth(d, CX-10, CY+50, 130, 110, False)
    up = -22*abs(math.sin(math.pi*t))
    d.rounded_rectangle([CX+205, CY+95+up, CX+265, CY+235], radius=30, fill=SKIN, outline=EDGE, width=10)
    d.rounded_rectangle([CX+120, CY+200, CX+320, CY+345], radius=42, fill=SKIN, outline=EDGE, width=10)
    for y in (240, 275, 310): ln(d, [(CX+150, CY+y), (CX+215, CY+y)], 9, EDGE)
def s_shock(d, t):
    base(d); j = math.sin(t*TAU*3)*5
    eye(d, CX-105, CY-50, 64, j, 0, 15); eye(d, CX+105, CY-50, 64, j, 0, 15)
    ln(d, [(CX-180, CY-160), (CX-105, CY-195), (CX-30, CY-160)], 22); ln(d, [(CX+30, CY-160), (CX+105, CY-195), (CX+180, CY-160)], 22)
    d.ellipse([CX-58, CY+70, CX+58, CY+200], fill=INK); d.ellipse([CX-34, CY+140, CX+34, CY+195], fill=PINK)
    for a in (-155, -135, -45, -25):
        r = math.radians(a); l = 40 + 20*abs(math.sin(math.pi*t))
        ln(d, [(CX+(R+25)*math.cos(r), CY+(R+25)*math.sin(r)), (CX+(R+25+l)*math.cos(r), CY+(R+25+l)*math.sin(r))], 18, (255, 150, 30, 255))
def s_thanks(d, t):
    base(d); happy(d, CX-115, CY-60); happy(d, CX+115, CY-60); smile(d, CX, CY+30, 105, 85); blush(d, CY+30)
    d.polygon([(CX, CY+175), (CX-75, CY+265), (CX-65, CY+345), (CX+65, CY+345), (CX+75, CY+265)], fill=SKIN, outline=EDGE, width=10)
    ln(d, [(CX, CY+200), (CX, CY+340)], 9, EDGE)
    for i in range(3):
        p = (t+i/3) % 1; heart(d, CX+150+p*120, CY-20-p*150, 70-p*30, RED[:3]+(fade(p),))
def s_morning(d, t):
    for i in range(14):
        a = (i+t)*TAU/14; r0, r1 = R-10, R+62
        d.polygon([(CX+r0*math.cos(a-.1), CY+r0*math.sin(a-.1)), (CX+r1*math.cos(a), CY+r1*math.sin(a)), (CX+r0*math.cos(a+.1), CY+r0*math.sin(a+.1))], fill=(255, 150, 25, 255))
    base(d, (255, 218, 80, 255)); happy(d, CX-115, CY-60); happy(d, CX+115, CY-60); mouth(d, CX, CY+35, 140, 115); blush(d, CY+30, 190)
def s_cool(d, t):
    base(d); K = (25, 25, 35, 255)
    for s in (-1, 1): d.rounded_rectangle([CX+s*115-95, CY-125, CX+s*115+95, CY+5], radius=40, fill=K)
    d.rectangle([CX-25, CY-105, CX+25, CY-85], fill=K)
    for s in (-1, 1):
        x = CX+s*115-60+t*120; d.polygon([(x, CY-110), (x+26, CY-110), (x+8, CY-10), (x-18, CY-10)], fill=(255, 255, 255, 150))
    ln(d, [(CX-100, CY+110), (CX+10, CY+150), (CX+120, CY+85)], 26)
def s_yasater(d, t):
    base(d); eye(d, CX-105, CY-45, 52, -14, -16, 22); eye(d, CX+105, CY-45, 52, -14, -16, 22)
    ln(d, [(CX-175, CY-120), (CX-60, CY-165)], 22); ln(d, [(CX+60, CY-165), (CX+175, CY-120)], 22)
    ln(d, [(CX-110+i*22, CY+140+14*math.sin(i*1.3)) for i in range(11)], 22)
    drop(d, CX+185, CY-190+t*90, 30, tear(t)); q = (t+.5) % 1; drop(d, CX-195, CY-130+q*90, 22, tear(q))
def s_sleep(d, t):
    base(d, (250, 200, 80, 255)); sleepy(d, CX-115, CY-55); sleepy(d, CX+115, CY-55)
    d.ellipse([CX-34, CY+105, CX+34, CY+175], fill=INK); drop(d, CX+30, CY+200+t*70, 24, tear(t, (150, 210, 255)))
    for i in range(3):
        p = (t+i/3) % 1
        d.text((CX+170+p*100, CY-170-p*130), "Z", font=F(70+60*p), fill=(70, 110, 220, fade(p)), anchor="mm")
def s_fire(d, t):
    for i, a in enumerate((-150, -120, -90, -60, -30)):
        r = math.radians(a); bx, by = CX+(R-20)*math.cos(r), CY+(R-20)*math.sin(r)
        flame(d, bx, by, 95+18*math.sin(TAU*t+i*1.7), 52, (bx-CX)*.18+20*math.sin(TAU*t+i))
    base(d); eye(d, CX-105, CY-40); eye(d, CX+105, CY-40)
    ln(d, [(CX-175, CY-135), (CX-60, CY-100)], 26); ln(d, [(CX+60, CY-100), (CX+175, CY-135)], 26)
    mouth(d, CX, CY+50, 140, 120, False)
def s_angry(d, t):
    base(d, (245, 105, 65, 255)); eye(d, CX-100, CY-30, 44, 10, 8, 20); eye(d, CX+100, CY-30, 44, -10, 8, 20)
    ln(d, [(CX-175, CY-125), (CX-45, CY-75)], 30); ln(d, [(CX+45, CY-75), (CX+175, CY-125)], 30)
    d.rounded_rectangle([CX-110, CY+110, CX+110, CY+175], radius=20, fill=WHITE, outline=INK, width=10)
    for x in (-55, 0, 55): ln(d, [(CX+x, CY+115), (CX+x, CY+170)], 8)
    k = 1+.2*math.sin(TAU*t); cx, cy = CX+190, CY-190
    for a in (45, 135, 225, 315): d.arc([cx-45*k, cy-45*k, cx+45*k, cy+45*k], a-35, a+35, fill=(190, 20, 30, 255), width=16)
def s_love(d, t):
    base(d); k = 1+.15*math.sin(TAU*t*2); heart(d, CX-110, CY-45, 130*k); heart(d, CX+110, CY-45, 130*k)
    smile(d, CX, CY+40, 120, 100); blush(d, CY+60, 190)
    for i in range(3):
        p = (t+i/3) % 1; heart(d, CX+100+p*170+(i-1)*25, CY+100-p*260, 60-20*p, PINK[:3]+(fade(p),))
def s_think(d, t):
    base(d); eye(d, CX-105, CY-45, 52, 20, -18, 22); eye(d, CX+105, CY-45, 52, 20, -18, 22)
    ln(d, [(CX-175, CY-125), (CX-60, CY-160)], 22); ln(d, [(CX+60, CY-125), (CX+175, CY-120)], 22)
    ln(d, [(CX-90, CY+140), (CX+10, CY+120), (CX+100, CY+145)], 24)
    d.text((CX+235, CY-215+12*math.sin(TAU*t)), "؟", font=F(170), fill=(60, 110, 220, 255), anchor="mm")
def s_broke(d, t):
    base(d); eye(d, CX-105, CY-40, 52, 0, 22, 22); eye(d, CX+105, CY-40, 52, 0, 22, 22)
    ln(d, [(CX-175, CY-120), (CX-60, CY-160)], 22); ln(d, [(CX+60, CY-160), (CX+175, CY-120)], 22)
    frown(d, CX, CY+170, 100, 70)
    for s in (-1, 1): drop(d, CX+s*135, CY+30+t*120, 26, tear(t))
    for i in range(3):
        p = (t+i/3) % 1; x, y, a = CX+60+p*250, CY+140-p*170, fade(p)
        d.rounded_rectangle([x-55, y-32, x+55, y+32], radius=10, fill=(110, 200, 120, a), outline=(40, 130, 60, a), width=6)
        d.text((x, y), "$", font=F(60), fill=(30, 110, 50, a), anchor="mm")
def s_nazar(d, t):
    for r, c in ((270, (20, 70, 160, 255)), (205, WHITE), (140, (70, 170, 245, 255)), (72, (15, 15, 25, 255))):
        d.ellipse([CX-r, CY-r, CX+r, CY+r], fill=c)
    d.ellipse([CX-40, CY-42, CX-8, CY-14], fill=WHITE); d.arc([CX-250, CY-250, CX+250, CY+250], 200, 250, fill=(255, 255, 255, 140), width=14)
    d.ellipse([CX-40, CY-335, CX+40, CY-255], outline=(230, 170, 40, 255), width=18)
    for x, y, ph in ((CX-300, CY-120, 0), (CX+310, CY+60, .4), (CX+250, CY-240, .7)):
        sparkle(d, x, y, 30+30*abs(math.sin(math.pi*(t+ph))), (255, 215, 60, 255))
def s_tea(d, t):
    d.ellipse([CX-210, CY+170, CX+210, CY+250], fill=(245, 245, 245, 255), outline=(190, 190, 200, 255), width=10)
    d.polygon([(CX-115, CY-110), (CX+115, CY-110), (CX+88, CY+190), (CX-88, CY+190)], fill=(235, 245, 255, 255), outline=(150, 170, 200, 255), width=12)
    d.polygon([(CX-108, CY-60), (CX+108, CY-60), (CX+88, CY+185), (CX-88, CY+185)], fill=(175, 95, 25, 255))
    d.ellipse([CX-108, CY-80, CX+108, CY-40], fill=(205, 125, 40, 255))
    eye(d, CX-45, CY+35, 26, 0, 4, 12); eye(d, CX+45, CY+35, 26, 0, 4, 12); smile(d, CX, CY+70, 38, 28, 12, WHITE)
    for i, x in enumerate((-50, 0, 50)):
        ln(d, [(CX+x+22*math.sin(TAU*(t+j/6)+i*2), CY-130-j*34) for j in range(6)], 14, (165, 165, 185, 200))
def s_usta(d, t):
    base(d); w = 8*math.sin(TAU*t)
    eye(d, CX-100, CY-10, 44, 0, 4, 20); eye(d, CX+100, CY-10, 44, 0, 4, 20)
    ln(d, [(CX-165, CY-70), (CX-50, CY-62)], 26); ln(d, [(CX+50, CY-62), (CX+165, CY-70)], 26)
    d.ellipse([CX-135+w, CY+55, CX+4+w, CY+125], fill=INK); d.ellipse([CX-4-w, CY+55, CX+135-w, CY+125], fill=INK)
    smile(d, CX, CY+110, 70, 55, 22)
    d.pieslice([CX-235, CY-280, CX+235, CY+60], 180, 360, fill=(45, 95, 175, 255), outline=(25, 60, 120, 255), width=10)
    d.rounded_rectangle([CX-285, CY-135, CX+285, CY-95], radius=20, fill=(30, 70, 140, 255)); d.ellipse([CX-20, CY-300, CX+20, CY-262], fill=(30, 70, 140, 255))

SPECS = [  # file, text, whatsapp emojis, draw fn, motion, pivot
    ("s01", "هموت من الضحك", ["😂", "🤣"], s_laugh, "bounce", (CX, CY)),
    ("s02", "تمام يا باشا", ["👍", "😉"], s_ok, "pulse", (CX, CY)),
    ("s03", "إيه ده يا عم!", ["😳", "😱"], s_shock, "shake", (CX, CY)),
    ("s04", "على راسي", ["🙏", "😊"], s_thanks, "bounce", (CX, CY)),
    ("s05", "صباح الفل", ["☀️", "🌼"], s_morning, "wobble", (CX, CY)),
    ("s06", "أنا كده", ["😎", "😏"], s_cool, "bounce", (CX, CY)),
    ("s07", "يا ساتر", ["😅", "🤦"], s_yasater, "shake", (CX, CY)),
    ("s08", "نايم ع الواقف", ["😴", "💤"], s_sleep, "wobble", (CX, CY)),
    ("s09", "عاش يا وحش", ["🔥", "💪"], s_fire, "shake", (CX, CY)),
    ("s10", "مش فاضي", ["😡", "😤"], s_angry, "shake", (CX, CY)),
    ("s11", "يا قمر", ["😍", "🥰"], s_love, "pulse", (CX, CY)),
    ("s12", "طب وبعدين؟", ["🤔", "❓"], s_think, "wobble", (CX, CY)),
    ("s13", "الجيب فاضي", ["💸", "😭"], s_broke, "shake", (CX, CY)),
    ("s14", "عين وصابتك", ["🧿", "🙏"], s_nazar, "wobble", (CX, CY-300)),
    ("s15", "شاي بقى", ["🍵", "☕"], s_tea, "bounce", (CX, CY)),
    ("s16", "على طول يا أسطى", ["🚖", "😁"], s_usta, "wobble", (CX, CY)),
]

def pose(m, t):
    s = math.sin(TAU*t)
    return {"bounce": (-abs(math.sin(math.pi*t))*55, 0, 1), "wobble": (0, s*.14, 1),
            "pulse": (0, 0, 1+.06*s), "shake": (0, math.sin(TAU*t*3)*.06, 1)}[m]
def xform(img, dy, rot, sc, pv):
    if rot: img = img.rotate(math.degrees(rot), resample=Image.BICUBIC, center=pv)
    if sc != 1 or dy:
        r = img.resize((int(W*sc), int(W*sc)), Image.BICUBIC); out = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        out.paste(r, (int(pv[0]-pv[0]*sc), int(pv[1]-pv[1]*sc+dy))); img = out
    return img
def render(spec, t):
    _, text, _, fn, motion, pv = spec
    art = Image.new("RGBA", (W, W), (0, 0, 0, 0)); fn(ImageDraw.Draw(art, "RGBA"), t)
    dy, rot, sc = pose(motion, t); art = xform(art, dy, rot, sc, pv)
    d = ImageDraw.Draw(art, "RGBA"); size = 165
    while size > 60 and d.textlength(text, font=F(size), direction="rtl", language="ar") > 850: size -= 6
    d.text((512, 855), text, font=F(size), fill=INK, anchor="mm", direction="rtl", language="ar", stroke_width=5, stroke_fill=INK)
    mask = art.getchannel("A").filter(ImageFilter.GaussianBlur(14)).point(lambda v: 255 if v > 6 else 0).filter(ImageFilter.GaussianBlur(2))
    out = Image.new("RGBA", (W, W), (255, 255, 255, 0)); out.putalpha(mask)
    return Image.alpha_composite(out, art).resize((512, 512), Image.LANCZOS)

if __name__ == "__main__":
    os.makedirs(f"{ASSETS}/stickers", exist_ok=True); os.makedirs(os.path.dirname(ICON), exist_ok=True); entries = []; sheet = Image.new("RGBA", (1024, 1024), (235, 235, 240, 255))
    for i, sp in enumerate(SPECS):
        frames = [render(sp, k/N) for k in range(N)]; path = f"{ASSETS}/stickers/{sp[0]}.webp"
        for q in (80, 70, 60, 50, 40, 30):
            frames[0].save(path, save_all=True, append_images=frames[1:], duration=DUR, loop=0, quality=q, method=4, lossless=False)
            if os.path.getsize(path) <= 500*1024: break
        print(sp[0], sp[1], os.path.getsize(path)//1024, "KB q", q)
        entries.append({"file": sp[0]+".webp", "emojis": sp[2], "label": sp[1]})
        f = render(sp, .25).resize((256, 256), Image.LANCZOS); sheet.alpha_composite(f, ((i % 4)*256, (i//4)*256))
        if i == 0:
            frames[0].resize((96, 96), Image.LANCZOS).save(f"{ASSETS}/tray.png")
            ic = Image.new("RGBA", (192, 192), (0, 0, 0, 0)); ImageDraw.Draw(ic).rounded_rectangle([0, 0, 191, 191], 44, fill=(255, 244, 222, 255))
            ic.alpha_composite(render(sp, .25).resize((176, 176), Image.LANCZOS), (8, 8)); ic.save(ICON)
    json.dump({"id": "egy_animated_1", "name": "ستيكرز مصرية متحركة", "publisher": "Egy Stickers", "tray": "tray.png", "stickers": entries},
              open(f"{ASSETS}/pack.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    sheet.save("/home/claude/preview.png")
