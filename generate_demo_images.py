"""
generate_demo_images.py
Generates realistic, high-fidelity local product images for all demo items in EasyShare.
Saves images directly to app/static/uploads/items/.
"""
import os
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / 'app' / 'static' / 'uploads' / 'items'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Try loading Windows system fonts with safe fallbacks
def get_font(size=20, bold=False):
    font_names = [
        ('segoeuib.ttf' if bold else 'segoeui.ttf'),
        ('arialbd.ttf' if bold else 'arial.ttf'),
        ('calibrib.ttf' if bold else 'calibri.ttf'),
    ]
    for name in font_names:
        try:
            path = Path('C:/Windows/Fonts') / name
            if path.is_file():
                return ImageFont.truetype(str(path), size)
        except Exception:
            pass
    return ImageFont.load_default()


def create_studio_background(width=800, height=600, top_color=(245, 247, 250), bottom_color=(218, 225, 233)):
    """Create a clean studio gradient background with a soft floor shadow effect."""
    img = Image.new('RGB', (width, height), top_color)
    draw = ImageDraw.Draw(img)
    # Vertical gradient
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Soft circular highlight in the center
    center_x, center_y = width // 2, int(height * 0.45)
    halo = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    halo_draw = ImageDraw.Draw(halo)
    for rad in range(280, 0, -10):
        alpha = int(12 * (1 - rad / 280))
        halo_draw.ellipse(
            [center_x - rad, center_y - rad, center_x + rad, center_y + rad],
            fill=(255, 255, 255, alpha)
        )
    img.paste(Image.alpha_composite(img.convert('RGBA'), halo).convert('RGB'), (0, 0))
    return img


def draw_drop_shadow(draw, box, blur=20, shadow_color=(30, 41, 59, 45)):
    """Draw a soft ground shadow underneath a product."""
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    w = (x1 - x0) // 2 + 30
    h = 24
    for r in range(16, 0, -2):
        alpha = int(shadow_color[3] * (1 - r / 16))
        draw.ellipse([cx - w - r, y1 - h - r, cx + w + r, y1 + h + r], fill=(40, 50, 70, alpha))


# --------------------------------------------------------------------------
# 1. TI-84 Plus CE Graphing Calculator
# --------------------------------------------------------------------------
def gen_ti84_ce():
    img = create_studio_background()
    overlay = Image.new('RGBA', (800, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Ground shadow
    draw.ellipse([250, 500, 550, 550], fill=(20, 30, 45, 60))
    
    # Body
    bx0, by0, bx1, by1 = 280, 80, 520, 510
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=26, fill=(24, 28, 36, 255), outline=(55, 65, 81, 255), width=3)
    
    # Header bar
    draw.text((bx0 + 35, by0 + 16), "TEXAS INSTRUMENTS", font=get_font(12, True), fill=(156, 163, 175, 255))
    draw.text((bx0 + 35, by0 + 32), "TI-84 Plus CE", font=get_font(16, True), fill=(255, 255, 255, 255))
    
    # Color LCD Screen
    sx0, sy0, sx1, sy1 = bx0 + 25, by0 + 56, bx1 - 25, by0 + 200
    draw.rounded_rectangle([sx0, sy0, sx1, sy1], radius=6, fill=(15, 23, 42, 255), outline=(71, 85, 105, 255), width=2)
    # Graph grid & axes inside LCD
    cx, cy = (sx0 + sx1) // 2, (sy0 + sy1) // 2
    draw.line([(sx0 + 8, cy), (sx1 - 8, cy)], fill=(51, 65, 85, 255), width=1)
    draw.line([(cx, sy0 + 8), (cx, sy1 - 8)], fill=(51, 65, 85, 255), width=1)
    # Sine curve plot
    pts = []
    for x in range(sx0 + 12, sx1 - 12):
        rel_x = (x - cx) / 20.0
        y = cy - int(math.sin(rel_x) * 45)
        pts.append((x, y))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=(56, 189, 248, 255), width=2)
    draw.text((sx0 + 10, sy0 + 8), "Y1=sin(X)", font=get_font(11, True), fill=(56, 189, 248, 255))
    
    # Function keys (Y=, WINDOW, ZOOM, TRACE, GRAPH)
    fkeys = ["Y=", "WIND", "ZOOM", "TRCE", "GRPH"]
    for i, fk in enumerate(fkeys):
        kx = sx0 + i * 38
        draw.rounded_rectangle([kx, by0 + 212, kx + 32, by0 + 230], radius=4, fill=(55, 65, 81, 255))
        draw.text((kx + 3, by0 + 214), fk, font=get_font(9, True), fill=(209, 213, 219, 255))
    
    # Direction pad (circular diamond)
    draw.ellipse([bx1 - 85, by0 + 240, bx1 - 35, by0 + 290], fill=(55, 65, 81, 255), outline=(75, 85, 99, 255), width=2)
    
    # 2nd / Alpha keys
    draw.rounded_rectangle([bx0 + 25, by0 + 242, bx0 + 60, by0 + 264], radius=4, fill=(59, 130, 246, 255))  # 2nd blue
    draw.text((bx0 + 32, by0 + 246), "2nd", font=get_font(10, True), fill=(255, 255, 255, 255))
    draw.rounded_rectangle([bx0 + 68, by0 + 242, bx0 + 103, by0 + 264], radius=4, fill=(34, 197, 94, 255))  # alpha green
    draw.text((bx0 + 72, by0 + 246), "ALPHA", font=get_font(9, True), fill=(255, 255, 255, 255))
    
    # Numeric keypad
    rows = [
        ["7", "8", "9", "DEL"],
        ["4", "5", "6", "×"],
        ["1", "2", "3", "-"],
        ["0", ".", "(-)", "+"],
        ["ON", "STO", "LN", "ENTER"]
    ]
    start_y = by0 + 300
    for r_idx, row in enumerate(rows):
        for c_idx, label in enumerate(row):
            kx = bx0 + 26 + c_idx * 47
            ky = start_y + r_idx * 38
            btn_color = (75, 85, 99, 255) if label in ["DEL", "ENTER", "+", "-", "×"] else (45, 55, 72, 255)
            if label == "ENTER":
                btn_color = (30, 58, 138, 255)
            draw.rounded_rectangle([kx, ky, kx + 40, ky + 28], radius=6, fill=btn_color)
            draw.text((kx + 11, ky + 6), label, font=get_font(11, True), fill=(255, 255, 255, 255))
            
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img


# --------------------------------------------------------------------------
# 2. Casio fx-991EX ClassWiz Scientific Calculator
# --------------------------------------------------------------------------
def gen_casio_classwiz():
    img = create_studio_background()
    overlay = Image.new('RGBA', (800, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Shadow
    draw.ellipse([260, 510, 540, 555], fill=(20, 30, 45, 60))
    
    # Body (Slim, curved modern scientific calculator)
    bx0, by0, bx1, by1 = 285, 75, 515, 515
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=22, fill=(240, 242, 245, 255), outline=(156, 163, 175, 255), width=2)
    
    # Dark carbon textured faceplate in the lower half
    draw.rounded_rectangle([bx0 + 8, by0 + 200, bx1 - 8, by1 - 8], radius=16, fill=(28, 32, 40, 255))
    
    # Branding & Solar panel
    draw.text((bx0 + 20, by0 + 16), "CASIO", font=get_font(15, True), fill=(17, 24, 39, 255))
    draw.text((bx0 + 20, by0 + 34), "fx-991EX CLASSWIZ", font=get_font(11, True), fill=(75, 85, 99, 255))
    
    # Solar cell
    draw.rounded_rectangle([bx1 - 80, by0 + 18, bx1 - 20, by0 + 38], radius=3, fill=(60, 40, 30, 255), outline=(180, 140, 100, 255), width=1)
    
    # High-res LCD Screen (White-dot matrix on silver grey)
    sx0, sy0, sx1, sy1 = bx0 + 16, by0 + 52, bx1 - 16, by0 + 140
    draw.rounded_rectangle([sx0, sy0, sx1, sy1], radius=6, fill=(226, 232, 240, 255), outline=(100, 116, 139, 255), width=2)
    draw.text((sx0 + 12, sy0 + 10), "√2 + ∫(x²+1)dx", font=get_font(16, True), fill=(15, 23, 42, 255))
    draw.text((sx1 - 95, sy1 - 28), "= 5.7475", font=get_font(18, True), fill=(15, 23, 42, 255))
    draw.text((sx0 + 12, sy1 - 22), "MATH [RAD] [D]", font=get_font(9, False), fill=(100, 116, 139, 255))
    
    # Circular dual-axis keypad
    cx = (bx0 + bx1) // 2
    draw.ellipse([cx - 30, by0 + 148, cx + 30, by0 + 196], fill=(203, 213, 225, 255), outline=(148, 163, 184, 255), width=2)
    draw.text((cx - 8, by0 + 164), "REPLAY", font=get_font(8, True), fill=(71, 85, 105, 255))
    
    # Silver function buttons
    draw.rounded_rectangle([bx0 + 16, by0 + 155, bx0 + 52, by0 + 175], radius=4, fill=(245, 158, 11, 255))  # SHIFT yellow
    draw.text((bx0 + 21, by0 + 158), "SHIFT", font=get_font(8, True), fill=(255, 255, 255, 255))
    draw.rounded_rectangle([bx0 + 60, by0 + 155, bx0 + 96, by0 + 175], radius=4, fill=(239, 68, 68, 255))  # ALPHA red
    draw.text((bx0 + 64, by0 + 158), "ALPHA", font=get_font(8, True), fill=(255, 255, 255, 255))
    
    # Dark keypad keys
    labels = [
        ["OPTN", "CALC", "∫dx", "x⁻¹", "log"],
        ["7", "8", "9", "DEL", "AC"],
        ["4", "5", "6", "×", "÷"],
        ["1", "2", "3", "+", "-"],
        ["0", ".", "x10ˣ", "Ans", "="]
    ]
    start_y = by0 + 220
    for r_idx, row in enumerate(labels):
        for c_idx, label in enumerate(row):
            kx = bx0 + 20 + c_idx * 40
            ky = start_y + r_idx * 54
            btn_bg = (55, 65, 81, 255)
            if label in ["DEL", "AC"]:
                btn_bg = (217, 119, 6, 255)  # Orange accent
            elif label == "=":
                btn_bg = (37, 99, 235, 255)
            draw.rounded_rectangle([kx, ky, kx + 34, ky + 34], radius=5, fill=btn_bg)
            draw.text((kx + 6, ky + 8), label, font=get_font(10, True), fill=(255, 255, 255, 255))
            
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img


# --------------------------------------------------------------------------
# 3. Higher Engineering Mathematics (B.S. Grewal)
# --------------------------------------------------------------------------
def gen_math_book():
    img = create_studio_background()
    overlay = Image.new('RGBA', (800, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Shadow
    draw.ellipse([240, 520, 580, 560], fill=(20, 30, 45, 60))
    
    # Book Cover (Deep Royal Blue)
    bx0, by0, bx1, by1 = 260, 70, 540, 530
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=8, fill=(15, 32, 67, 255), outline=(212, 175, 55, 255), width=3)
    
    # Book Spine 3D illusion
    draw.rectangle([bx0 - 15, by0 + 6, bx0, by1 - 6], fill=(10, 22, 48, 255))
    
    # Gold border styling
    draw.rectangle([bx0 + 16, by0 + 16, bx1 - 16, by1 - 16], outline=(212, 175, 55, 180), width=2)
    
    # Gold Badge: 44th Edition
    draw.rounded_rectangle([bx1 - 110, by0 + 26, bx1 - 26, by0 + 52], radius=4, fill=(212, 175, 55, 255))
    draw.text((bx1 - 104, by0 + 32), "44th EDITION", font=get_font(10, True), fill=(15, 32, 67, 255))
    
    # Titles
    draw.text((bx0 + 30, by0 + 80), "HIGHER", font=get_font(26, True), fill=(255, 255, 255, 255))
    draw.text((bx0 + 30, by0 + 115), "ENGINEERING", font=get_font(24, True), fill=(212, 175, 55, 255))
    draw.text((bx0 + 30, by0 + 148), "MATHEMATICS", font=get_font(22, True), fill=(255, 255, 255, 255))
    
    # Decorative Math formulas illustration
    draw.rectangle([bx0 + 30, by0 + 195, bx1 - 30, by0 + 360], fill=(20, 42, 85, 255), outline=(30, 58, 115, 255))
    draw.text((bx0 + 45, by0 + 210), "∇²u = ∂²u/∂x² + ∂²u/∂y²", font=get_font(13, True), fill=(147, 197, 253, 255))
    draw.text((bx0 + 45, by0 + 240), "L{f(t)} = ∫ e^(-st) f(t) dt", font=get_font(13, True), fill=(253, 224, 71, 255))
    draw.text((bx0 + 45, by0 + 270), "∮ F · dr = ∬ (∇ × F) · dS", font=get_font(13, True), fill=(147, 197, 253, 255))
    draw.text((bx0 + 45, by0 + 300), "λⁿ + c₁λⁿ⁻¹ + ... = 0", font=get_font(13, True), fill=(253, 224, 71, 255))
    
    # Author & Publisher
    draw.text((bx0 + 30, by0 + 410), "Dr. B.S. GREWAL", font=get_font(20, True), fill=(255, 255, 255, 255))
    draw.text((bx0 + 30, by0 + 440), "KHANNA PUBLISHERS", font=get_font(12, True), fill=(209, 213, 219, 255))
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img


# --------------------------------------------------------------------------
# 4. Organic Chemistry (Paula Bruice)
# --------------------------------------------------------------------------
def gen_organic_chem_book():
    img = create_studio_background()
    overlay = Image.new('RGBA', (800, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    draw.ellipse([240, 520, 580, 560], fill=(20, 30, 45, 60))
    
    # Emerald green cover
    bx0, by0, bx1, by1 = 260, 70, 540, 530
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=8, fill=(6, 78, 59, 255), outline=(16, 185, 129, 255), width=3)
    draw.rectangle([bx0 - 15, by0 + 6, bx0, by1 - 6], fill=(4, 47, 36, 255))
    
    # Title
    draw.text((bx0 + 30, by0 + 45), "GLOBAL EDITION", font=get_font(12, True), fill=(110, 231, 183, 255))
    draw.text((bx0 + 30, by0 + 80), "ORGANIC", font=get_font(30, True), fill=(255, 255, 255, 255))
    draw.text((bx0 + 30, by0 + 120), "CHEMISTRY", font=get_font(28, True), fill=(251, 191, 36, 255))
    draw.text((bx0 + 30, by0 + 160), "EIGHTH EDITION", font=get_font(13, True), fill=(209, 250, 229, 255))
    
    # Molecular benzene ring drawing
    cx, cy = (bx0 + bx1) // 2, by0 + 280
    r = 55
    pts = [(cx + int(r * math.cos(i * math.pi / 3)), cy + int(r * math.sin(i * math.pi / 3))) for i in range(6)]
    for i in range(6):
        draw.line([pts[i], pts[(i+1)%6]], fill=(255, 255, 255, 255), width=4)
        # Atoms (circles)
        draw.ellipse([pts[i][0]-8, pts[i][1]-8, pts[i][0]+8, pts[i][1]+8], fill=(245, 158, 11, 255))
    draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], outline=(110, 231, 183, 255), width=3)
    
    # Subtitle & Author
    draw.text((bx0 + 30, by0 + 410), "PAULA YURKANIS BRUICE", font=get_font(18, True), fill=(255, 255, 255, 255))
    draw.text((bx0 + 30, by0 + 440), "PEARSON", font=get_font(14, True), fill=(167, 243, 208, 255))
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img


# --------------------------------------------------------------------------
# 5. Concepts of Physics (H.C. Verma)
# --------------------------------------------------------------------------
def gen_physics_book():
    img = create_studio_background()
    overlay = Image.new('RGBA', (800, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    draw.ellipse([240, 520, 580, 560], fill=(20, 30, 45, 60))
    
    # Crimson/maroon cover
    bx0, by0, bx1, by1 = 260, 70, 540, 530
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=8, fill=(127, 29, 29, 255), outline=(239, 68, 68, 255), width=3)
    draw.rectangle([bx0 - 15, by0 + 6, bx0, by1 - 6], fill=(69, 10, 10, 255))
    
    # Titles
    draw.text((bx0 + 30, by0 + 75), "CONCEPTS OF", font=get_font(24, True), fill=(254, 202, 202, 255))
    draw.text((bx0 + 30, by0 + 110), "PHYSICS", font=get_font(34, True), fill=(255, 255, 255, 255))
    draw.text((bx0 + 30, by0 + 155), "VOLUME 1 & 2", font=get_font(16, True), fill=(252, 211, 77, 255))
    
    # Planetary orbits graphic
    cx, cy = (bx0 + bx1) // 2, by0 + 275
    draw.ellipse([cx - 80, cy - 35, cx + 80, cy + 35], outline=(252, 211, 77, 180), width=2)
    draw.ellipse([cx - 35, cy - 80, cx + 35, cy + 80], outline=(254, 202, 202, 180), width=2)
    draw.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=(245, 158, 11, 255))  # Nucleus / Sun
    draw.ellipse([cx + 65, cy - 10, cx + 80, cy + 5], fill=(56, 189, 248, 255))  # Electron
    
    # Author
    draw.text((bx0 + 30, by0 + 410), "H. C. VERMA", font=get_font(22, True), fill=(255, 255, 255, 255))
    draw.text((bx0 + 30, by0 + 445), "BHARATI BHAWAN", font=get_font(13, True), fill=(254, 202, 202, 255))
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img


# --------------------------------------------------------------------------
# 6. Cotton White Lab Coat & Safety Goggles
# --------------------------------------------------------------------------
def gen_lab_coat_goggles():
    img = create_studio_background()
    overlay = Image.new('RGBA', (800, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    draw.ellipse([220, 510, 580, 560], fill=(20, 30, 45, 60))
    
    # White Lab Coat folded body
    draw.rounded_rectangle([250, 150, 550, 520], radius=16, fill=(248, 250, 252, 255), outline=(203, 213, 225, 255), width=3)
    # Lapels & V-collar
    draw.polygon([(400, 150), (320, 250), (400, 340), (480, 250)], fill=(241, 245, 249, 255), outline=(203, 213, 225, 255))
    # Center seam & buttons
    draw.line([(400, 340), (400, 520)], fill=(203, 213, 225, 255), width=2)
    for by in [370, 420, 470]:
        draw.ellipse([395, by, 405, by + 10], fill=(226, 232, 240, 255), outline=(148, 163, 184, 255), width=1)
    # Left breast pocket
    draw.rectangle([290, 320, 350, 390], fill=(241, 245, 249, 255), outline=(203, 213, 225, 255), width=2)
    # Pen in pocket
    draw.rectangle([310, 305, 318, 330], fill=(37, 99, 235, 255))
    
    # UV Safety Goggles resting diagonally at the top
    # Blue rubber frame
    draw.rounded_rectangle([270, 90, 530, 180], radius=30, fill=(30, 58, 138, 240), outline=(59, 130, 246, 255), width=3)
    # Clear dual lenses with cyan reflection
    draw.rounded_rectangle([290, 105, 385, 165], radius=20, fill=(224, 242, 254, 210), outline=(186, 230, 253, 255), width=2)
    draw.rounded_rectangle([415, 105, 510, 165], radius=20, fill=(224, 242, 254, 210), outline=(186, 230, 253, 255), width=2)
    # Lens glare streaks
    draw.line([(310, 115), (340, 155)], fill=(255, 255, 255, 220), width=3)
    draw.line([(435, 115), (465, 155)], fill=(255, 255, 255, 220), width=3)
    # Elastic strap
    draw.line([(270, 135), (230, 140)], fill=(30, 58, 138, 255), width=8)
    draw.line([(530, 135), (570, 140)], fill=(30, 58, 138, 255), width=8)
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img


# --------------------------------------------------------------------------
# 7. Digital Multimeter with Test Probes
# --------------------------------------------------------------------------
def gen_multimeter():
    img = create_studio_background()
    overlay = Image.new('RGBA', (800, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    draw.ellipse([250, 510, 550, 555], fill=(20, 30, 45, 60))
    
    # Yellow rubber rugged case
    bx0, by0, bx1, by1 = 280, 80, 520, 510
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=24, fill=(245, 158, 11, 255), outline=(217, 119, 6, 255), width=4)
    # Dark grey inner chassis
    draw.rounded_rectangle([bx0 + 12, by0 + 12, bx1 - 12, by1 - 12], radius=18, fill=(31, 41, 55, 255))
    
    # Backlit LCD Screen
    draw.rounded_rectangle([bx0 + 26, by0 + 35, bx1 - 26, by0 + 130], radius=8, fill=(187, 247, 208, 255), outline=(134, 239, 172, 255), width=2)
    draw.text((bx0 + 40, by0 + 50), "230.4", font=get_font(42, True), fill=(20, 83, 45, 255))
    draw.text((bx1 - 70, by0 + 65), "V AC", font=get_font(18, True), fill=(20, 83, 45, 255))
    draw.text((bx0 + 40, by0 + 105), "AUTO RANGE  HOLD", font=get_font(10, True), fill=(22, 101, 52, 255))
    
    # Rotary Selector Dial
    cx, cy = (bx0 + bx1) // 2, by0 + 260
    draw.ellipse([cx - 65, cy - 65, cx + 65, cy + 65], fill=(55, 65, 81, 255), outline=(75, 85, 99, 255), width=2)
    draw.ellipse([cx - 45, cy - 45, cx + 45, cy + 45], fill=(17, 24, 39, 255))
    # Dial pointer knob
    draw.rectangle([cx - 6, cy - 42, cx + 6, cy], fill=(245, 158, 11, 255))
    # Markings around dial
    draw.text((cx - 15, cy - 80), "OFF", font=get_font(10, True), fill=(239, 68, 68, 255))
    draw.text((cx + 50, cy - 40), "V~", font=get_font(12, True), fill=(255, 255, 255, 255))
    draw.text((cx + 60, cy + 10), "V⎓", font=get_font(12, True), fill=(255, 255, 255, 255))
    draw.text((cx - 75, cy - 40), "Ω", font=get_font(14, True), fill=(255, 255, 255, 255))
    draw.text((cx - 70, cy + 10), "A⎓", font=get_font(12, True), fill=(255, 255, 255, 255))
    
    # 3 Probe Jacks at bottom
    jacks = [("10A", (239, 68, 68, 255)), ("COM", (17, 24, 39, 255)), ("VΩmA", (239, 68, 68, 255))]
    for i, (name, col) in enumerate(jacks):
        jx = bx0 + 50 + i * 70
        jy = by0 + 430
        draw.ellipse([jx - 12, jy - 12, jx + 12, jy + 12], fill=col, outline=(255, 255, 255, 255), width=2)
        draw.text((jx - 14, jy + 16), name, font=get_font(9, True), fill=(156, 163, 175, 255))
        
    # Red and Black test probes on side
    # Red lead
    draw.line([(bx1 - 5, by0 + 430), (bx1 + 60, by0 + 350)], fill=(220, 38, 38, 255), width=6)
    draw.rectangle([bx1 + 50, by0 + 200, bx1 + 65, by0 + 350], fill=(220, 38, 38, 255))
    draw.line([(bx1 + 57, by0 + 200), (bx1 + 57, by0 + 160)], fill=(203, 213, 225, 255), width=3)  # Metal tip
    
    # Black lead
    draw.line([(bx0 + 5, by0 + 430), (bx0 - 60, by0 + 350)], fill=(17, 24, 39, 255), width=6)
    draw.rectangle([bx0 - 65, by0 + 200, bx0 - 50, by0 + 350], fill=(17, 24, 39, 255))
    draw.line([(bx0 - 57, by0 + 200), (bx0 - 57, by0 + 160)], fill=(203, 213, 225, 255), width=3)
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img


# --------------------------------------------------------------------------
# 8. Yonex Nanoray Carbon Fiber Badminton Racket Pair
# --------------------------------------------------------------------------
def gen_badminton_racket():
    img = create_studio_background()
    overlay = Image.new('RGBA', (800, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    draw.ellipse([200, 510, 600, 560], fill=(20, 30, 45, 60))
    
    # Isometric Racket Head Oval
    cx, cy = 400, 200
    rx, ry = 110, 140
    # Outer Frame
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=(6, 182, 212, 255), width=7)
    draw.ellipse([cx - rx + 4, cy - ry + 4, cx + rx - 4, cy + ry - 4], outline=(15, 23, 42, 255), width=3)
    
    # Strings mesh
    for x in range(cx - rx + 20, cx + rx - 10, 14):
        draw.line([(x, cy - ry + 15), (x, cy + ry - 15)], fill=(255, 255, 255, 120), width=1)
    for y in range(cy - ry + 20, cy + ry - 10, 14):
        draw.line([(cx - rx + 15, y), (cx + rx - 15, y)], fill=(255, 255, 255, 120), width=1)
    
    # Shaft
    draw.line([(cx, cy + ry), (cx, cy + ry + 150)], fill=(15, 23, 42, 255), width=8)
    draw.line([(cx - 2, cy + ry), (cx - 2, cy + ry + 150)], fill=(6, 182, 212, 255), width=2)
    
    # Handle with red grip tape
    gx0, gy0, gx1, gy1 = cx - 12, cy + ry + 150, cx + 12, cy + ry + 240
    draw.rounded_rectangle([gx0, gy0, gx1, gy1], radius=4, fill=(220, 38, 38, 255))
    for step in range(gy0 + 10, gy1 - 5, 14):
        draw.line([(gx0, step), (gx1, step + 8)], fill=(185, 28, 28, 255), width=2)
    # Butt cap
    draw.rectangle([gx0 - 2, gy1 - 6, gx1 + 2, gy1], fill=(15, 23, 42, 255))
    
    # Shuttlecock beside racket
    sx, sy = 240, 420
    # Cork head
    draw.ellipse([sx - 16, sy + 30, sx + 16, sy + 60], fill=(255, 255, 255, 255), outline=(203, 213, 225, 255), width=2)
    # Feather skirt
    draw.polygon([(sx - 14, sy + 35), (sx + 14, sy + 35), (sx + 35, sy - 20), (sx - 35, sy - 20)], fill=(248, 250, 252, 230), outline=(203, 213, 225, 255))
    for fx in range(sx - 30, sx + 35, 10):
        draw.line([(fx, sy - 18), (sx, sy + 35)], fill=(148, 163, 184, 255), width=1)
        
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img


# --------------------------------------------------------------------------
# 9. Spalding NBA Official Grip Basketball
# --------------------------------------------------------------------------
def gen_basketball():
    img = create_studio_background()
    overlay = Image.new('RGBA', (800, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    cx, cy = 400, 300
    r = 180
    
    # Shadow
    draw.ellipse([cx - 190, cy + 170, cx + 190, cy + 225], fill=(20, 30, 45, 60))
    
    # Orange leather sphere
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(234, 88, 12, 255), outline=(194, 65, 12, 255), width=3)
    
    # Texture pebble dots simulation
    # Black seam channels
    draw.line([(cx - r, cy), (cx + r, cy)], fill=(15, 23, 42, 255), width=6)
    draw.line([(cx, cy - r), (cx, cy + r)], fill=(15, 23, 42, 255), width=6)
    
    # Curved ribs
    draw.arc([cx - r - 40, cy - r, cx + 40, cy + r], start=-90, end=90, fill=(15, 23, 42, 255), width=6)
    draw.arc([cx - 40, cy - r, cx + r + 40, cy + r], start=90, end=270, fill=(15, 23, 42, 255), width=6)
    
    # Spalding text
    draw.text((cx - 85, cy - 50), "SPALDING", font=get_font(28, True), fill=(15, 23, 42, 255))
    draw.text((cx - 75, cy + 15), "TF-1000 PRECISION", font=get_font(12, True), fill=(15, 23, 42, 255))
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img


# --------------------------------------------------------------------------
# 10. Logitech MX Master Wireless Mouse
# --------------------------------------------------------------------------
def gen_mouse():
    img = create_studio_background()
    overlay = Image.new('RGBA', (800, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Shadow
    draw.ellipse([260, 480, 540, 530], fill=(20, 30, 45, 60))
    
    # Sculpted dark graphite mouse body
    bx0, by0, bx1, by1 = 290, 120, 510, 490
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=70, fill=(30, 41, 59, 255), outline=(51, 65, 85, 255), width=3)
    
    # Left thumb rest wing
    draw.polygon([(bx0 + 20, by0 + 200), (bx0 - 35, by0 + 340), (bx0 + 20, by0 + 440)], fill=(15, 23, 42, 255))
    
    # Center seam dividing left and right click buttons
    cx = (bx0 + bx1) // 2
    draw.line([(cx, by0 + 10), (cx, by0 + 220)], fill=(71, 85, 105, 255), width=3)
    
    # Metallic hyper-fast scroll wheel
    draw.rounded_rectangle([cx - 10, by0 + 70, cx + 10, by0 + 140], radius=5, fill=(148, 163, 184, 255), outline=(203, 213, 225, 255), width=1)
    for ry in range(by0 + 78, by0 + 135, 8):
        draw.line([(cx - 10, ry), (cx + 10, ry)], fill=(71, 85, 105, 255), width=1)
        
    # Thumb wheel
    draw.rounded_rectangle([bx0 - 15, by0 + 230, bx0 + 5, by0 + 270], radius=3, fill=(148, 163, 184, 255))
    
    # Logi logo
    draw.text((cx - 24, by0 + 380), "logi", font=get_font(20, True), fill=(100, 116, 139, 255))
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img


# --------------------------------------------------------------------------
# 11. Foldable Aluminum Laptop Cooling Stand
# --------------------------------------------------------------------------
def gen_laptop_stand():
    img = create_studio_background()
    overlay = Image.new('RGBA', (800, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    draw.ellipse([200, 480, 600, 530], fill=(20, 30, 45, 60))
    
    # Brushed aluminum silver finish
    # Base legs
    draw.polygon([(260, 470), (540, 470), (500, 450), (290, 450)], fill=(203, 213, 225, 255), outline=(148, 163, 184, 255))
    
    # Twin angled riser arms
    draw.polygon([(290, 450), (320, 450), (390, 220), (360, 220)], fill=(148, 163, 184, 255))
    draw.polygon([(480, 450), (510, 450), (580, 220), (550, 220)], fill=(148, 163, 184, 255))
    
    # Top support plate (angled)
    draw.polygon([(240, 280), (560, 280), (510, 160), (290, 160)], fill=(226, 232, 240, 255), outline=(148, 163, 184, 255), width=2)
    # Airflow ventilation cutouts
    draw.polygon([(340, 260), (460, 260), (440, 190), (360, 190)], fill=(203, 213, 225, 255))
    
    # Front silicone protective hooks
    draw.rectangle([250, 270, 280, 305], fill=(71, 85, 105, 255))
    draw.rectangle([520, 270, 550, 305], fill=(71, 85, 105, 255))
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img


# --------------------------------------------------------------------------
# 12. Yamaha F280 Acoustic Folk Guitar
# --------------------------------------------------------------------------
def gen_acoustic_guitar():
    img = create_studio_background()
    overlay = Image.new('RGBA', (800, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    draw.ellipse([260, 520, 540, 560], fill=(20, 30, 45, 60))
    
    # Upper Bout & Lower Bout of guitar body (warm amber spruce)
    cx = 400
    # Lower bout
    draw.ellipse([cx - 120, 280, cx + 120, 520], fill=(217, 119, 6, 255), outline=(146, 64, 14, 255), width=3)
    # Upper bout
    draw.ellipse([cx - 95, 190, cx + 95, 360], fill=(217, 119, 6, 255), outline=(146, 64, 14, 255), width=3)
    
    # Soundhole (Deep black with ornate white/cream rosette rings)
    draw.ellipse([cx - 36, 270, cx + 36, 342], fill=(17, 24, 39, 255), outline=(254, 243, 199, 255), width=4)
    draw.ellipse([cx - 44, 262, cx + 44, 350], outline=(180, 83, 9, 255), width=2)
    
    # Black pickguard
    draw.ellipse([cx + 5, 300, cx + 55, 370], fill=(17, 24, 39, 255))
    
    # Wooden bridge
    draw.rectangle([cx - 40, 430, cx + 40, 455], fill=(120, 53, 15, 255), outline=(69, 26, 3, 255))
    # 6 Bridge pins
    for px in range(cx - 30, cx + 35, 12):
        draw.ellipse([px - 3, 440, px + 3, 446], fill=(255, 255, 255, 255))
        
    # Fretboard / Neck
    draw.rectangle([cx - 16, 60, cx + 16, 270], fill=(69, 26, 3, 255), outline=(45, 20, 5, 255))
    # Frets
    for fy in range(75, 270, 20):
        draw.line([(cx - 16, fy), (cx + 16, fy)], fill=(203, 213, 225, 255), width=1)
    # Fret dots
    for dy in [115, 155, 195]:
        draw.ellipse([cx - 2, dy, cx + 2, dy + 4], fill=(255, 255, 255, 255))
        
    # Headstock
    draw.polygon([(cx - 20, 60), (cx + 20, 60), (cx + 25, 15), (cx - 25, 15)], fill=(120, 53, 15, 255), outline=(69, 26, 3, 255))
    # Tuning pegs
    for py in [25, 40, 52]:
        draw.rectangle([cx - 38, py - 3, cx - 25, py + 3], fill=(203, 213, 225, 255))
        draw.rectangle([cx + 25, py - 3, cx + 38, py + 3], fill=(203, 213, 225, 255))
        
    # Strings (6 silver lines)
    for si, sx in enumerate([-10, -6, -2, 2, 6, 10]):
        draw.line([(cx + sx, 60), (cx + sx, 440)], fill=(226, 232, 240, 200), width=1)
        
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img


# --------------------------------------------------------------------------
# 13. Rotring Rapid Pro Technical Drafting Pen (0.5mm)
# --------------------------------------------------------------------------
def gen_drafting_pen():
    img = create_studio_background()
    overlay = Image.new('RGBA', (800, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Shadow
    draw.ellipse([200, 460, 600, 500], fill=(20, 30, 45, 60))
    
    # Diagonal drafting pencil
    # Main matte black hexagonal body
    p0 = (240, 420)
    p1 = (560, 160)
    draw.line([p0, p1], fill=(24, 28, 36, 255), width=22)
    
    # Signature Rotring Red Ring accent
    draw.line([(310, 363), (322, 353)], fill=(220, 38, 38, 255), width=24)
    
    # Knurled grip section (front)
    draw.line([(255, 408), (300, 372)], fill=(38, 44, 56, 255), width=20)
    for step in range(0, 40, 5):
        draw.line([(260 + step, 404 - int(step*0.8)), (264 + step, 400 - int(step*0.8))], fill=(71, 85, 105, 255), width=2)
        
    # Precision 0.5mm silver metal guide tube tip
    draw.line([(220, 436), (245, 416)], fill=(203, 213, 225, 255), width=8)
    draw.line([(210, 444), (222, 434)], fill=(148, 163, 184, 255), width=3)  # thin lead
    
    # Chrome pocket clip & push button cap
    draw.line([(535, 180), (565, 156)], fill=(203, 213, 225, 255), width=18)
    draw.line([(520, 200), (555, 172)], fill=(148, 163, 184, 255), width=6)  # clip
    
    # Branding text
    draw.text((360, 310), "rOtring 800 0.5", font=get_font(13, True), fill=(203, 213, 225, 255))
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img


# --------------------------------------------------------------------------
# 14. Anker 20000mAh PowerCore Fast Power Bank
# --------------------------------------------------------------------------
def gen_powerbank():
    img = create_studio_background()
    overlay = Image.new('RGBA', (800, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    draw.ellipse([240, 490, 560, 540], fill=(20, 30, 45, 60))
    
    # Matte Charcoal Power Bank Body
    bx0, by0, bx1, by1 = 280, 130, 520, 480
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=28, fill=(24, 28, 36, 255), outline=(55, 65, 81, 255), width=3)
    
    # Top port panel
    draw.rounded_rectangle([bx0 + 20, by0 + 20, bx1 - 20, by0 + 80], radius=10, fill=(15, 23, 42, 255))
    # USB-A ports (blue interior)
    draw.rectangle([bx0 + 45, by0 + 38, bx0 + 90, by0 + 62], fill=(14, 165, 233, 255), outline=(203, 213, 225, 255))
    draw.rectangle([bx1 - 90, by0 + 38, bx1 - 45, by0 + 62], fill=(14, 165, 233, 255), outline=(203, 213, 225, 255))
    # USB-C PD port in center
    draw.rounded_rectangle([(bx0 + bx1)//2 - 20, by0 + 44, (bx0 + bx1)//2 + 20, by0 + 56], radius=5, fill=(55, 65, 81, 255))
    
    # Anker Embossed Logo
    cx = (bx0 + bx1) // 2
    draw.text((cx - 50, by0 + 190), "ANKER", font=get_font(28, True), fill=(100, 116, 139, 255))
    draw.text((cx - 55, by0 + 230), "PowerCore 20K", font=get_font(14, True), fill=(71, 85, 105, 255))
    
    # Circular power button with 4 glowing blue LED indicator dots
    draw.ellipse([cx - 26, by0 + 340, cx + 26, by0 + 392], fill=(30, 41, 59, 255), outline=(71, 85, 105, 255), width=2)
    # 4 Blue LEDs
    for dot_idx in range(4):
        angle = dot_idx * (math.pi / 2) + math.pi / 4
        dx = cx + int(14 * math.cos(angle))
        dy = by0 + 366 + int(14 * math.sin(angle))
        draw.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=(56, 189, 248, 255))
        
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img


# --------------------------------------------------------------------------
# 15. Mobile Phone (Smartphone)
# --------------------------------------------------------------------------
def gen_mobile_phone():
    img = create_studio_background()
    overlay = Image.new('RGBA', (800, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    draw.ellipse([270, 520, 530, 560], fill=(20, 30, 45, 60))
    
    # Sleek Titanium Chassis
    bx0, by0, bx1, by1 = 290, 65, 510, 525
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=38, fill=(15, 23, 42, 255), outline=(148, 163, 184, 255), width=4)
    
    # AMOLED Screen with wallpaper
    sx0, sy0, sx1, sy1 = bx0 + 12, by0 + 12, bx1 - 12, by1 - 12
    draw.rounded_rectangle([sx0, sy0, sx1, sy1], radius=28, fill=(2, 6, 23, 255))
    
    # Vibrant wallpaper gradient inside screen
    for y in range(sy0, sy1):
        ratio = (y - sy0) / (sy1 - sy0)
        r = int(15 + 80 * ratio)
        g = int(23 + 120 * (1 - ratio))
        b = int(42 + 200 * ratio)
        draw.line([(sx0 + 4, y), (sx1 - 4, y)], fill=(r, g, b, 255))
        
    # Dynamic Island / Camera punch hole at top
    cx = (bx0 + bx1) // 2
    draw.rounded_rectangle([cx - 28, sy0 + 14, cx + 28, sy0 + 32], radius=9, fill=(0, 0, 0, 255))
    
    # Lock screen clock
    draw.text((cx - 52, sy0 + 65), "09:41", font=get_font(40, True), fill=(255, 255, 255, 255))
    draw.text((cx - 65, sy0 + 115), "Monday, October 31", font=get_font(12, True), fill=(226, 232, 240, 255))
    
    # App icons preview at bottom
    for i in range(4):
        ix = sx0 + 20 + i * 44
        iy = sy1 - 85
        draw.rounded_rectangle([ix, iy, ix + 34, iy + 34], radius=8, fill=(255, 255, 255, 230))
        
    # Bottom home indicator bar
    draw.rounded_rectangle([cx - 40, sy1 - 18, cx + 40, sy1 - 13], radius=3, fill=(255, 255, 255, 255))
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img


# --------------------------------------------------------------------------
# 16. Wireless Earbuds
# --------------------------------------------------------------------------
def gen_earbuds():
    img = create_studio_background()
    overlay = Image.new('RGBA', (800, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    draw.ellipse([220, 480, 580, 540], fill=(20, 30, 45, 60))
    
    # Open White Charging Case
    cx = 360
    # Bottom half of case
    draw.rounded_rectangle([cx - 90, 240, cx + 90, 460], radius=55, fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=2)
    # Open Lid behind
    draw.rounded_rectangle([cx - 86, 120, cx + 86, 250], radius=50, fill=(241, 245, 249, 255), outline=(203, 213, 225, 255), width=2)
    
    # Earbud magnetic slots interior
    draw.ellipse([cx - 60, 225, cx - 15, 280], fill=(203, 213, 225, 255))
    draw.ellipse([cx + 15, 225, cx + 60, 280], fill=(203, 213, 225, 255))
    
    # Status LED on case front (Green)
    draw.ellipse([cx - 4, 340, cx + 4, 348], fill=(34, 197, 94, 255))
    
    # Right Earbud resting beside case
    eb_x, eb_y = 540, 300
    # Earbud head with silicone tip
    draw.ellipse([eb_x - 30, eb_y - 30, eb_x + 30, eb_y + 30], fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=2)
    draw.ellipse([eb_x + 10, eb_y - 18, eb_x + 36, eb_y + 18], fill=(241, 245, 249, 255), outline=(203, 213, 225, 255))  # tip
    # Stem
    draw.rounded_rectangle([eb_x - 22, eb_y + 10, eb_x - 4, eb_y + 120], radius=8, fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=2)
    # Chrome charging tip
    draw.rounded_rectangle([eb_x - 20, eb_y + 110, eb_x - 6, eb_y + 120], radius=3, fill=(203, 213, 225, 255))
    # Black acoustic speaker grill dot
    draw.ellipse([eb_x - 10, eb_y - 8, eb_x - 2, eb_y], fill=(30, 41, 59, 255))
    
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img


# Mapping of product files to generator functions
GENERATORS = {
    'ti84_ce_calc.jpg': gen_ti84_ce,
    'casio_classwiz.jpg': gen_casio_classwiz,
    'math_grewal.jpg': gen_math_book,
    'bruice_organic_chem.jpg': gen_organic_chem_book,
    'hc_verma_physics.jpg': gen_physics_book,
    'lab_coat_goggles.jpg': gen_lab_coat_goggles,
    'multimeter.jpg': gen_multimeter,
    'badminton_racket.jpg': gen_badminton_racket,
    'basketball.jpg': gen_basketball,
    'mouse.jpg': gen_mouse,
    'laptop_stand.jpg': gen_laptop_stand,
    'acoustic_guitar.jpg': gen_acoustic_guitar,
    'drafting_pen.jpg': gen_drafting_pen,
    'powerbank.jpg': gen_powerbank,
    'mobile_phone.jpg': gen_mobile_phone,
    'earbuds.jpg': gen_earbuds
}


def generate_all_images():
    print(f"[*] Generating {len(GENERATORS)} high-fidelity demo product images...")
    for filename, gen_fn in GENERATORS.items():
        dest = OUTPUT_DIR / filename
        image = gen_fn()
        image.save(dest, format='JPEG', quality=90, optimize=True)
        print(f"   [+] Generated {filename} ({dest.stat().st_size // 1024} KB)")
    print("[OK] All demo product images created successfully in app/static/uploads/items/!")


if __name__ == '__main__':
    generate_all_images()
