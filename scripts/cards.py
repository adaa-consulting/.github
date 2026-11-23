"""Generate the SVG images for profile/README.md. Edit the data below, then run: python3 scripts/cards.py"""
import base64
from pathlib import Path
from xml.dom import minidom
from xml.sax.saxutils import escape

PRODUCTS = [  # (English name, Arabic name, description, tech)
    ("Correspondence Management", "إدارة المراسلات",
     "Official incoming / outgoing mail, routing, approvals and archiving for government entities.",
     ["Django", "Next.js", "OnlyOffice"]),
    ("Single Sign-On & UAE Pass", "الدخول الموحد",
     "One secure login across every system, integrated with the UAE national digital identity.",
     ["OAuth2", "UAE Pass", "Multi-tenant"]),
    ("Strategy Management", "إدارة الاستراتيجية",
     "Strategic plans, KPIs, initiatives and performance dashboards for leadership.",
     ["KPIs", "Dashboards", "Reports"]),
    ("Meetings & AI Minutes", "الاجتماعات الذكية",
     "Meeting lifecycle, decisions and tasks, with Arabic speech-to-text and AI minutes.",
     ["Arabic STT", "AI Summaries"]),
    ("Complaints Management", "إدارة الشكاوى",
     "ISO 10002-compliant complaint handling, from intake to resolution and analysis.",
     ["ISO 10002", "SLA Tracking"]),
    ("Finance & Assets", "المالية وإدارة الأصول",
     "Budgets, financial workflows and asset registers for government programs.",
     ["Finance", "Assets", "Audit trail"]),
    ("Digital Portals & Media", "البوابات الرقمية والإعلام",
     "Bilingual public websites, admin dashboards and media-office systems.",
     ["Arabic RTL", "CMS", "SEO"]),
    ("Mobile Apps", "التطبيقات الذكية",
     "Companion mobile apps for officials and customers, on iOS and Android.",
     ["React Native", "Flutter"]),
]

IT_CLIENTS = [  # (key = logo file prefix in scripts/clients/, English, Arabic)
    ("1-cpo", "Crown Prince's Office – Fujairah", "مكتب سمو ولي عهد الفجيرة"),
    ("2-fgep", "Fujairah Government Excellence Program", "برنامج الفجيرة للتميز الحكومي"),
    ("3-fcci", "Fujairah Chamber of Commerce & Industry", "غرفة تجارة وصناعة الفجيرة"),
    ("4-customs", "Fujairah Customs Department", "دائرة جمارك الفجيرة"),
    ("5-tourism", "Fujairah Tourism & Antiquities Authority", "هيئة الفجيرة للسياحة والآثار"),
    ("6-ffrd", "Fujairah Foundation for Regions Development", "مؤسسة الفجيرة لتنمية المناطق"),
    ("7-hr", "Human Resources Department – Fujairah", "دائرة الموارد البشرية - الفجيرة"),
    ("8-albadr", "Al Badr Initiative", "مبادرة البدر"),
    ("9-equestrian", "Fujairah Equestrian Championships", "بطولات الفجيرة للفروسية"),
]
CONSULTING_CLIENTS = [
    "Dubai Electricity & Water Authority", "Dubai Municipality", "Ministry of Interior",
    "Dubai Police", "Abu Dhabi Police", "TDRA", "Etihad Water & Electricity",
]

SERVICES = [  # from adaaconsulting.ae
    ("Institutional Excellence", "التميز والريادة المؤسسية"),
    ("Strategic Planning", "التخطيط الاستراتيجي"),
    ("Human Resources", "الموارد البشرية"),
    ("Institutional Development", "التطوير المؤسسي"),
    ("Customer Experience", "تجربة المتعامل وخدمات المتعاملين"),
    ("Operational Efficiency", "إدارة العمليات والكفاءة التشغيلية"),
    ("Risk & Governance", "إدارة المخاطر والحوكمة المؤسسية"),
    ("Innovation", "الابتكار"),
    ("Standards & ISO Systems", "أنظمة المواصفات القياسية"),
    ("Digital Transformation & AI", "الرقمنة والذكاء الاصطناعي"),
]

W = 854
HERE = Path(__file__).resolve().parent
# Cairo (SIL OFL, see Cairo-OFL.txt), subset to Latin + Arabic and embedded: images on GitHub cannot load web fonts
CAIRO = base64.b64encode((HERE / "cairo.woff2").read_bytes()).decode()
FONT_CSS = (f"<style>@font-face{{font-family:'Cairo';font-weight:400 800;"
            f"src:url(data:font/woff2;base64,{CAIRO}) format('woff2')}}</style>")
FONT = "Cairo,'Segoe UI',Tahoma,sans-serif"
LOGO = (HERE / "logo.svg").read_text()  # traced from the official logo-white.png, so it stays sharp at any size

# Adaa brand, taken from adaaconsulting.ae: royal blue #0047BB, sand-gold #B6B098, charcoal
BLUE, GOLD, CHARCOAL = "#0047BB", "#B6B098", "#2f2f2f"
THEMES = {
    "light": dict(card="#ffffff", border="#c9d6f2", text="#333333", muted="#666666", blue=BLUE, gold=GOLD,
                  chip_strong="#e8effb", chip="#ffffff"),
    "dark": dict(card="#1b1f27", border="#2c3a57", text="#f0f0f0", muted="#a9adb4", blue="#6c9cff", gold=GOLD,
                 chip_strong="#10224a", chip="#1b1f27"),
}


def esc(s):
    return escape(s, {"'": "&#39;"})


def wrap(text, n):
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > n:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + [cur]


def chip(t, x, y, label, strong=False):
    w = int(len(label) * 6.4) + 22  # shortcut: width estimated from char count; fine for short Latin labels
    fill, stroke, color = (t["chip_strong"], t["blue"], t["blue"]) if strong else (t["chip"], t["gold"], t["muted"])
    return w, (f'<rect x="{x}" y="{y}" width="{w}" height="24" rx="12" fill="{fill}" stroke="{stroke}"/>'
               f'<text x="{x + w / 2}" y="{y + 16.5}" text-anchor="middle" font-size="12" font-weight="600" fill="{color}">{esc(label)}</text>')


def chip_rows(t, x0, y, labels, max_x, strong=False):
    """Lay chips left-to-right, wrapping to a new row; returns (svg, bottom y)."""
    out, x = [], x0
    for label in labels:
        w, _ = chip(t, 0, 0, label, strong)
        if x + w > max_x:
            x, y = x0, y + 32
        out.append(chip(t, x, y, label, strong)[1])
        x += w + 8
    return "".join(out), y + 24


def svg(h, body):
    # no page background: the image is transparent so it sits on GitHub's own light or dark page
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
            f'font-family="{FONT}"><defs>{FONT_CSS}</defs>{body}</svg>')


def logo(x, y, w, color):
    return f'<svg x="{x}" y="{y}" width="{w}" height="{w * .75}" viewBox="0 0 800 600" color="{color}">{LOGO}</svg>'


def banner():
    h = 240
    body = [
        f'<rect width="{W}" height="{h}" rx="14" fill="{CHARCOAL}"/>',
        f'<path d="M{W - 260} 0 H{W - 14} a14 14 0 0 1 14 14 V{h - 14} a14 14 0 0 1 -14 14 H{W - 420} Z" fill="{BLUE}"/>',
        f'<path d="M{W - 300} 0 L{W - 460} {h}" stroke="{GOLD}" stroke-width="3"/>',
        "".join(f'<path d="M40 {84 + i * 26} l18 -8" stroke="{GOLD}" stroke-width="4" stroke-linecap="round"/>' for i in range(4)),
        logo(W - 250, 30, 240, "#ffffff"),
        f'<text x="90" y="100" font-size="40" font-weight="800" fill="#ffffff">Adaa Consulting</text>',
        f'<text x="90" y="140" font-size="25" font-weight="700" fill="{GOLD}">أداء للاستشارات</text>',
        f'<text x="90" y="178" font-size="16" fill="#e5e5e5">Institutional development starts from within</text>',
        f'<text x="90" y="206" font-size="15" fill="#c4c4c4">التطوير المؤسسي يبدأ من الداخل</text>',
    ]
    return svg(h, "".join(body))


def products(t):
    cols, gap, ch = 2, 16, 152
    cw = (W - gap) // cols
    rows = (len(PRODUCTS) + 1) // cols
    h = rows * ch + (rows - 1) * gap + 2
    body = []
    for i, (en, ar, desc, tech) in enumerate(PRODUCTS):
        x = 1 + (i % cols) * (cw + gap)
        y = 1 + (i // cols) * (ch + gap)
        body.append(f'<rect x="{x}" y="{y}" width="{cw - 2}" height="{ch}" rx="10" fill="{t["card"]}" stroke="{t["border"]}"/>')
        body.append(f'<rect x="{x + 18}" y="{y + 18}" width="28" height="28" rx="7" fill="{t["gold"]}"/>'
                    f'<text x="{x + 32}" y="{y + 37}" text-anchor="middle" font-size="13" font-weight="700" fill="#ffffff">{i + 1:02d}</text>')
        body.append(f'<text x="{x + 56}" y="{y + 38}" font-size="16" font-weight="700" fill="{t["text"]}">{esc(en)}</text>')
        body.append(f'<text x="{x + cw - 20}" y="{y + 38}" text-anchor="end" font-size="14" font-weight="700" fill="{t["blue"]}">{esc(ar)}</text>')
        for j, line in enumerate(wrap(desc, 56)[:2]):
            body.append(f'<text x="{x + 18}" y="{y + 72 + j * 19}" font-size="13" fill="{t["muted"]}">{esc(line)}</text>')
        body.append(chip_rows(t, x + 18, y + ch - 38, tech, x + cw - 20)[0])
    return svg(h, "".join(body))


MIME = {".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}


def logo_data(key):
    files = [f for f in (HERE / "clients").glob(key + ".*") if f.suffix.lower() in MIME]
    if not files:
        return None
    f = files[0]
    return f"data:{MIME[f.suffix.lower()]};base64," + base64.b64encode(f.read_bytes()).decode()


def it_clients(t):
    cols, gap, th = 3, 14, 168
    cw = (W - gap * (cols - 1)) // cols
    rows = -(-len(IT_CLIENTS) // cols)
    h = rows * th + (rows - 1) * gap + 2
    body = []
    for i, (key, en, ar) in enumerate(IT_CLIENTS):
        x = 1 + (i % cols) * (cw + gap)
        y = 1 + (i // cols) * (th + gap)
        # logo tiles stay white in both themes: client logos are designed for a light background
        body.append(f'<rect x="{x}" y="{y}" width="{cw - 2}" height="{th}" rx="12" fill="#ffffff" stroke="{t["border"]}"/>')
        data = logo_data(key)
        if data:
            body.append(f'<image x="{x + 20}" y="{y + 14}" width="{cw - 42}" height="84" preserveAspectRatio="xMidYMid meet" href="{data}"/>')
        else:  # shortcut: text fallback when a logo file is missing; add scripts/clients/<key>.png to fix
            body.append(f'<text x="{x + cw / 2}" y="{y + 64}" text-anchor="middle" font-size="17" font-weight="800" fill="{BLUE}">{esc(ar)}</text>')
        body.append(f'<line x1="{x + 24}" y1="{y + 110}" x2="{x + cw - 26}" y2="{y + 110}" stroke="#ececec"/>')
        body.append(f'<text x="{x + cw / 2}" y="{y + 132}" text-anchor="middle" font-size="12" font-weight="700" fill="#333333">{esc(en)}</text>')
        body.append(f'<text x="{x + cw / 2}" y="{y + 153}" text-anchor="middle" font-size="12" font-weight="600" fill="{BLUE}">{esc(ar)}</text>')
    return svg(h, "".join(body))


def clients(t):
    body = [f'<text x="2" y="16" font-size="15" font-weight="700" fill="{t["blue"]}">Consulting clients</text>',
            f'<text x="{W - 2}" y="16" text-anchor="end" font-size="15" font-weight="700" fill="{t["blue"]}">عملاء الاستشارات</text>']
    s, y = chip_rows(t, 1, 30, CONSULTING_CLIENTS, W - 1)
    body.append(s)
    return svg(y + 2, "".join(body))


def services(t):
    cols, gap, rh = 2, 12, 50
    cw = (W - gap) // cols
    rows = (len(SERVICES) + 1) // cols
    h = rows * rh + (rows - 1) * gap + 2
    body = []
    for i, (en, ar) in enumerate(SERVICES):
        x = 1 + (i % cols) * (cw + gap)
        y = 1 + (i // cols) * (rh + gap)
        body.append(f'<rect x="{x}" y="{y}" width="{cw - 2}" height="{rh}" rx="8" fill="{t["card"]}" stroke="{t["border"]}"/>')
        body.append(f'<rect x="{x + 14}" y="{y + 15}" width="20" height="20" rx="5" fill="{t["gold"]}"/>'
                    f'<path d="M{x + 19} {y + 25} l4 4 l7 -8" stroke="#ffffff" stroke-width="2" fill="none" stroke-linecap="round"/>')
        body.append(f'<text x="{x + 44}" y="{y + 31}" font-size="14" font-weight="700" fill="{t["text"]}">{esc(en)}</text>')
        body.append(f'<text x="{x + cw - 18}" y="{y + 31}" text-anchor="end" font-size="13" fill="{t["muted"]}">{esc(ar)}</text>')
    return svg(h, "".join(body))


def contact():
    h = 170
    body = [
        f'<rect width="{W}" height="{h}" rx="12" fill="{BLUE}"/>',
        f'<path d="M{W - 80} 0 L{W - 210} {h}" stroke="{GOLD}" stroke-width="3" opacity=".8"/>',
        f'<text x="{W / 2}" y="52" text-anchor="middle" font-size="23" font-weight="700" fill="#ffffff">Ready to transform your organization?</text>',
        f'<text x="{W / 2}" y="82" text-anchor="middle" font-size="16" fill="#dbe6fb">جاهزون لمرافقتكم في رحلة التحول المؤسسي والرقمي</text>',
        f'<text x="{W / 2}" y="108" text-anchor="middle" font-size="13" fill="{GOLD}">Abu Dhabi · Dubai · Fujairah · Riyadh</text>',
        f'<rect x="{W / 2 - 125}" y="120" width="250" height="36" rx="8" fill="#ffffff"/>',
        f'<text x="{W / 2}" y="143" text-anchor="middle" font-size="14" font-weight="700" fill="{BLUE}">info@adaaconsulting.ae  →</text>',
    ]
    return svg(h, "".join(body))


if __name__ == "__main__":
    out = HERE.parent / "profile" / "brand"
    files = {"hero.svg": banner(), "cta.svg": contact()}
    for theme, t in THEMES.items():
        files[f"products-{theme}.svg"] = products(t)
        files[f"consulting-{theme}.svg"] = clients(t)
        files[f"client-logos-{theme}.svg"] = it_clients(t)
        files[f"services-{theme}.svg"] = services(t)
    for old in out.glob("*.svg"):
        old.unlink()
    for name, content in files.items():
        minidom.parseString(content)  # self-check: invalid XML (e.g. a bare &) silently breaks the image on GitHub
        (out / name).write_text(content, encoding="utf-8")
        print("wrote", out / name)
