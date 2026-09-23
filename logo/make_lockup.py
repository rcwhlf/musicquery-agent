# -*- coding: utf-8 -*-
"""合成横版 logo：图标 + MusicQuery Agent 字标 + 中文副标题（浅色/深色两版）。"""
import io, sys
from PIL import Image, ImageDraw, ImageFont

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

OUT = r"E:\musicquery-agent\logo"
ICON = OUT + r"\logo-icon-512.png"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT = r"C:\Windows\Fonts\msyh.ttc"

icon = Image.open(ICON).convert("RGBA")

def make(dark_bg=False, path=""):
    W, H = 2200, 640
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # 图标
    ic = icon.resize((520, 520), Image.LANCZOS)
    img.alpha_composite(ic, (50, 60))
    d = ImageDraw.Draw(img)
    text_main = (255, 255, 255, 255) if dark_bg else (36, 31, 53, 255)
    text_sub = (185, 179, 204, 255) if dark_bg else (111, 106, 128, 255)
    amber = (232, 163, 61, 255)
    f_main = ImageFont.truetype(FONT_BOLD, 170)
    f_sub = ImageFont.truetype(FONT, 54)
    x = 640
    # 主字标：MusicQuery（主色）+ Agent（琥珀）
    w1 = d.textbbox((x, 0), "MusicQuery", font=f_main)[2] - x
    d.text((x, 200), "MusicQuery", font=f_main, fill=text_main)
    d.text((x + w1 + 30, 200), "Agent", font=f_main, fill=amber)
    # 副标题
    d.text((x + 8, 430), "基于自然语言交互的音乐作品库智能查询系统", font=f_sub, fill=text_sub)
    img.save(path)
    print("SAVED:", path)

make(dark_bg=True, path=OUT + r"\logo-lockup-dark.png")
make(dark_bg=False, path=OUT + r"\logo-lockup-light.png")
