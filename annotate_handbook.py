"""
annotate_handbook.py
====================
Highlights every source passage of every rule in the handbook, using the rule's own colour,
and adds a colour tag (R01, R02 ...) in a side strip so each highlight can be traced to its rule.

Run:  python annotate_handbook.py  path/to/BU_handbook.pdf
Out:  outputs/handbook_pages/page_XX.png   and   outputs/Handbook_Annotated_Ch4_Ch5.pdf
"""
import sys, os
import fitz                                   # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import matplotlib
import handbook_data as H

OFFSET = 10          # PDF page = printed page + 10
DPI = 170
SCALE = DPI / 72.0
STRIP = 430          # width (px) of the side strip that holds the tags

SHORT = {
    "R01": "Programme minimum CGPA", "R02": "Low + None -> 1st Probation", "R03": "Low + One -> 2nd Probation",
    "R04": "Low + Two -> Dropped", "R05": "Safe -> Safe", "R06": "Borderline -> Watch",
    "R07": "Baseline broken -> Not eligible", "R08": "CGPA < 3.60 -> Not eligible", "R09": "Near-miss (just < 3.60)",
    "R10": "Cum Laude band", "R11": "Magna Cum Laude band", "R12": "Summa Cum Laude band",
    "R13": "Rector's List (>= 3.90)", "R14": "Advance Merit: min 3.50", "R15": "Merit non-eng: min 3.75",
    "R16": "Merit eng: min 3.60", "R17": "FAS: min 2.50", "R18": "Qarz-e-Hasna: min 2.75",
    "R19": "Below -> Suspended", "R20": "At-limit -> At-Risk", "R21": "Comfortable -> Continue",
    "R22": "Strong -> Secure", "R23": "Reduced load -> Suspended", "R24": "Slight reduce -> At-Risk",
}


def norm(w):
    return w.lower().strip(".,;:()'\"\u2019\u2018\u201c\u201d")


def tokens(text):
    return [t for t in (norm(w) for w in text.split()) if t]


def find_range(words, start, end):
    """Return the list of word-boxes from the first match of `start` to the end of the next match of `end`."""
    toks = [norm(w[4]) for w in words]
    s, e = tokens(start), tokens(end)

    def match(i, pat):
        return i + len(pat) <= len(toks) and toks[i:i + len(pat)] == pat

    for i in range(len(toks)):
        if match(i, s):
            for j in range(i, len(toks)):
                if match(j, e):
                    return words[i: j + len(e)]
    raise ValueError(f"Passage not found: {start!r} ... {end!r}")


def line_rects(word_boxes):
    lines = {}
    for w in word_boxes:
        lines.setdefault((w[5], w[6]), []).append(w)
    rects = []
    for ws in lines.values():
        rects.append(fitz.Rect(min(x[0] for x in ws), min(x[1] for x in ws),
                               max(x[2] for x in ws), max(x[3] for x in ws)))
    return sorted(rects, key=lambda r: (r.y0, r.x0))


def main(handbook_path, out_dir="outputs"):
    doc = fitz.open(handbook_path)
    os.makedirs(os.path.join(out_dir, "handbook_pages"), exist_ok=True)
    by_page = {}
    for r in H.RULES:
        for page, a, b in r["passages"]:
            by_page.setdefault(page, []).append((r["id"], a, b))

    fdir = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
    f_bold = ImageFont.truetype(os.path.join(fdir, "DejaVuSans-Bold.ttf"), 22)
    f_norm = ImageFont.truetype(os.path.join(fdir, "DejaVuSans.ttf"), 19)
    f_head = ImageFont.truetype(os.path.join(fdir, "DejaVuSans-Bold.ttf"), 20)

    pngs = []
    for printed in sorted(by_page):
        page = doc[printed + OFFSET - 1]
        words = page.get_text("words")
        marks = []                                   # (rid, [rects])
        for rid, a, b in by_page[printed]:
            rects = line_rects(find_range(words, a, b))
            rgb = H.rule_rgb(rid)
            annot = page.add_highlight_annot(quads=[r.quad for r in rects])
            annot.set_colors(stroke=rgb)
            annot.update()
            marks.append((rid, rects))
        pix = page.get_pixmap(dpi=DPI, annots=True)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

        canvas = Image.new("RGB", (img.width + STRIP, img.height), "white")
        canvas.paste(img, (0, 0))
        d = ImageDraw.Draw(canvas)
        d.line([(img.width, 0), (img.width, img.height)], fill=(190, 190, 190), width=2)

        # one tag per rule (grouped), placed at the first highlight; avoid overlaps
        first = {}
        for rid, rects in marks:
            first.setdefault(rid, []).extend(rects)
        order = sorted(first.items(), key=lambda kv: min(r.y0 for r in kv[1]))
        tag_h, prev_bottom = 38, 40
        for rid, rects in order:
            colour = tuple(round(c * 255) for c in H.rule_rgb(rid))
            for r in rects:                                   # bar next to every highlighted line
                d.rectangle([img.width + 6, r.y0 * SCALE, img.width + 14, r.y1 * SCALE], fill=colour)
            y = max(min(r.y0 for r in rects) * SCALE - 8, prev_bottom + 6)
            d.rounded_rectangle([img.width + 26, y, img.width + STRIP - 12, y + tag_h], radius=9,
                                fill=colour, outline=(70, 70, 70), width=1)
            d.text((img.width + 36, y + 7), rid, font=f_bold, fill=(20, 20, 20))
            d.text((img.width + 92, y + 9), SHORT[rid], font=f_norm, fill=(20, 20, 20))
            prev_bottom = y + tag_h
        d.text((img.width + 26, 8), "Rule tags", font=f_head, fill=(60, 60, 60))
        path = os.path.join(out_dir, "handbook_pages", f"page_{printed}.png")
        canvas.save(path)
        pngs.append(path)
        print("saved", path, "rules:", [m[0] for m in order] if False else sorted(first))

    # compile the annotated pages into one PDF
    imgs = [Image.open(p).convert("RGB") for p in pngs]
    pdf_path = os.path.join(out_dir, "Handbook_Annotated_Ch4_Ch5.pdf")
    imgs[0].save(pdf_path, save_all=True, append_images=imgs[1:], resolution=DPI)
    print("saved", pdf_path)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "BU_handbook.pdf")
