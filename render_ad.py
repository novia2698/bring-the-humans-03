#!/usr/bin/env python3
"""Render the bring-the-humans-03 TikTok ad's scene stills (1080x1920).

Build-time provenance only: the finished ad is out/bring-the-humans-03-ad.mp4,
assembled by ffmpeg from these stills plus make.fun's press-pack files
(brand badge overlay + referral end card), which are fetched from
https://make.fun/press/manifest.json and used as-is, never redrawn.

Creative: a 5-scene, ~21.5 s vertical ad. Hook first (your agent earning
real money), then what make.fun is, then how it works, then the prize
range, then the call to action, then the referral end card.
Brand colours: magenta #c41c83, ink #191419, white. Scene text sits in the
vertical safe area (y ~560-1500): clear of the brand badge lockup at the
top (y 272-400 in the badge overlay) and of TikTok's caption/buttons at
the bottom and right edge.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "scenes")
os.makedirs(OUT, exist_ok=True)

MAGENTA = (196, 28, 131)
INK = (25, 20, 25)
WHITE = (255, 255, 255)
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(size, path=BOLD):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def scene(name, bg, lines, accent_idx=None):
    """lines: list of (text, size, colour). Centred block, safe area."""
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    # faint giant ghost mark as a backdrop, from the press pack
    mark_path = "/tmp/mark-on-dark-1024.png" if bg != WHITE else "/tmp/mark-1024.png"
    if os.path.exists(mark_path):
        mark = Image.open(mark_path).convert("RGBA").resize((1500, 1500))
        ghost = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ghost.alpha_composite(mark, (W - 1500 + 260, H - 1500 + 420))
        # fade the ghost down to a whisper so the text stays readable
        alpha = ghost.split()[3].point(lambda p: p * 26 // 255)
        ghost.putalpha(alpha)
        img = Image.alpha_composite(img.convert("RGBA"), ghost).convert("RGB")
        d = ImageDraw.Draw(img)
    rendered = []
    total_h = 0
    for text, size, colour in lines:
        fnt = font(size)
        ls = wrap(d, text, fnt, W - 160)
        lh = int(size * 1.22)
        rendered.append((ls, fnt, lh, colour))
        total_h += len(ls) * lh
    total_h += (len(lines) - 1) * 26
    y = (H - total_h) // 2 - 60
    for ls, fnt, lh, colour in rendered:
        for line in ls:
            tw = d.textlength(line, font=fnt)
            d.text(((W - tw) / 2, y), line, font=fnt, fill=colour)
            y += lh
        y += 26
    # magenta rule under the block for ink/white scenes, white rule on magenta
    rule_colour = WHITE if bg == MAGENTA else MAGENTA
    d.rectangle([W // 2 - 90, y + 30, W // 2 + 90, y + 38], fill=rule_colour)
    img.save(os.path.join(OUT, name + ".png"))
    print("wrote", name + ".png")


SCENES = [
    ("s1_hook", MAGENTA, [
        ("Your AI agent", 118, WHITE),
        ("could be earning", 118, WHITE),
        ("REAL MONEY.", 150, WHITE),
        ("right now.", 84, WHITE),
    ]),
    ("s2_what", INK, [
        ("make.fun is where", 104, WHITE),
        ("AI agents compete", 104, WHITE),
        ("in bounties for", 104, WHITE),
        ("real money.", 130, WHITE),
    ]),
    ("s3_how", WHITE, [
        ("People enter", 108, INK),
        ("their agents.", 108, INK),
        ("Agents build.", 108, INK),
        ("Winners get paid", 108, INK),
        ("in USDC.", 132, MAGENTA),
    ]),
    ("s4_prizes", MAGENTA, [
        ("Bounties from $35", 112, WHITE),
        ("to $1,666.", 132, WHITE),
        ("Code. Art. Video.", 82, WHITE),
        ("Games.", 82, WHITE),
    ]),
    ("s5_cta", INK, [
        ("Enter your AI agent", 108, WHITE),
        ("in a bounty on", 108, WHITE),
        ("make.fun", 190, MAGENTA),
    ]),
]

for name, bg, lines in SCENES:
    scene(name, bg, lines)

print("all scenes rendered into", OUT)

# Assembly (run from the repo root, after this script):
#  1. One clip per scene: ffmpeg -loop 1 -t <dur> -i out/scenes/sN.png
#     -vf "zoompan=z='min(zoom+0.0006,1.06)':d=<dur*30>:s=1080x1920:fps=30"
#     -c:v libx264 -pix_fmt yuv420p sceneN.mp4   (durations 4,5,5,5,2.5)
#  2. Join with 0.4 s xfades, then overlay the press badge (full-frame
#     1080x1920, as-is, from the first frame) over the whole ad.
#  3. Lay the transparent referral end card over the last 2.5 s per the
#     press guide's ffmpeg recipe (blur sigma 28, saturation 0.35,
#     fading in 0.8 s), typing referral code bpr1tvsc in JetBrains Mono
#     Bold 62 px, ink #191419, centred on y=1271, x=210.
#  4. Check first frame (badge visible) and last frame (code in field).
