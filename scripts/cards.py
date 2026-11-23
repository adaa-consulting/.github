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
    ("9-equestrian", "Fujairah Arabian Horse Championship", "بطولة الفجيرة الدولية للخيل العربي"),
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
                  chip_strong="#e8effb", chip="#ffffff", chip_soft="#eef2f9"),
    "dark": dict(card="#1b1f27", border="#2c3a57", text="#f0f0f0", muted="#a9adb4", blue="#6c9cff", gold=GOLD,
                 chip_strong="#10224a", chip="#1b1f27", chip_soft="#242b38"),
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


BANNER_CSS = """
.in{animation:rise .9s cubic-bezier(.2,.7,.2,1) both}
.d1{animation-delay:.15s}.d2{animation-delay:.35s}.d3{animation-delay:.55s}.d4{animation-delay:.75s}.d5{animation-delay:.95s}
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
.line{stroke-dasharray:120;animation:draw 1.1s .6s cubic-bezier(.6,0,.2,1) both}
@keyframes draw{from{stroke-dashoffset:120}to{stroke-dashoffset:0}}
.spin,.spin-r,.pulse,.logo{transform-box:fill-box;transform-origin:center}
.spin{animation:spin 48s linear infinite}.spin-r{animation:spin 70s linear infinite reverse}
@keyframes spin{to{transform:rotate(360deg)}}
.pulse{animation:pulse 4.5s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:.55;transform:scale(.94)}50%{opacity:.95;transform:scale(1.04)}}
.logo{animation:pop 1.2s .4s cubic-bezier(.2,.8,.2,1) both}
@keyframes pop{from{opacity:0;transform:scale(.85)}to{opacity:1;transform:none}}
.sweep{animation:sweep 9s 1.5s ease-in-out infinite}
@keyframes sweep{0%{transform:translateX(-420px)}45%,100%{transform:translateX(1100px)}}
.p{animation:float 9s ease-in-out infinite}
@keyframes float{0%{opacity:0;transform:translateY(0)}25%{opacity:.9}100%{opacity:0;transform:translateY(-70px)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def banner():
    h, cx, cy = 280, 690, 140
    # logo glyphs occupy x 152-652, y 192-404 of the traced 800x600 canvas: crop to them
    logo_w = 118
    logo_h = logo_w * 212 / 500
    particles = "".join(
        f'<circle class="p" cx="{px}" cy="{py}" r="{r}" fill="{c}" style="animation-delay:{dl}s;animation-duration:{du}s"/>'
        for px, py, r, c, dl, du in [(470, 250, 1.6, GOLD, 0, 9), (540, 230, 1.2, "#7aa2ff", 2.5, 11), (610, 260, 1.8, GOLD, 4, 10),
                                     (780, 240, 1.3, "#7aa2ff", 1.2, 12), (820, 200, 1.5, GOLD, 6, 9), (430, 180, 1.1, "#7aa2ff", 3.5, 13),
                                     (360, 255, 1.4, GOLD, 7, 11), (760, 70, 1.2, GOLD, 5, 10)])
    orbit = lambda r, n, col, cls: (f'<g class="{cls}"><circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" '
                                    f'stroke-opacity=".45" stroke-width="1" stroke-dasharray="2 7"/>'
                                    + "".join(f'<circle cx="{cx + r * c}" cy="{cy + r * s}" r="2.6" fill="{col}"/>'
                                              for c, s in n) + "</g>")
    body = [
        f'<defs><style>{BANNER_CSS}</style>'
        f'<clipPath id="card"><rect width="{W}" height="{h}" rx="18"/></clipPath>'
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#070d1a"/>'
        f'<stop offset=".55" stop-color="#0b1a38"/><stop offset="1" stop-color="#0a2a6b"/></linearGradient>'
        f'<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#2f6bff" stop-opacity=".75"/>'
        f'<stop offset=".6" stop-color="{BLUE}" stop-opacity=".18"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="shine" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="goldtext" x1="0" x2="1"><stop offset="0" stop-color="#e9e2c6"/><stop offset="1" stop-color="{GOLD}"/></linearGradient>'
        f'<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#9db4ff" fill-opacity=".16"/></pattern>'
        f'<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset=".45" stop-color="#fff" stop-opacity=".1"/><stop offset="1" stop-color="#fff" stop-opacity="1"/></linearGradient>'
        f'<mask id="dotmask"><rect width="{W}" height="{h}" fill="url(#fade)"/></mask></defs>',
        '<g clip-path="url(#card)">',
        f'<rect width="{W}" height="{h}" fill="url(#bg)"/>',
        f'<rect width="{W}" height="{h}" fill="url(#dots)" mask="url(#dotmask)"/>',
        f'<circle class="pulse" cx="{cx}" cy="{cy}" r="170" fill="url(#glow)"/>',
        f'<g class="sweep"><rect x="-200" y="-40" width="160" height="{h + 80}" fill="url(#shine)" transform="skewX(-18)"/></g>',
        particles,
        # thin gold frame line along the bottom
        f'<rect x="0" y="{h - 3}" width="{W}" height="3" fill="url(#goldtext)" opacity=".9"/>',
        '</g>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="18" fill="none" stroke="#ffffff" stroke-opacity=".08"/>',
        # logo emblem: glass disc, rotating rings with orbiting dots, crisp vector logo
        orbit(112, [(1, 0), (-.5, .866), (-.5, -.866)], GOLD, "spin"),
        orbit(90, [(0, 1), (0, -1)], "#7aa2ff", "spin-r"),
        f'<circle cx="{cx}" cy="{cy}" r="70" fill="#ffffff" fill-opacity=".06" stroke="#ffffff" stroke-opacity=".18"/>',
        f'<g class="logo"><svg x="{cx - logo_w / 2}" y="{cy - logo_h / 2}" width="{logo_w}" height="{logo_h}" '
        f'viewBox="152 192 500 212" color="#ffffff">{LOGO}</svg></g>',
        # text block
        f'<text class="in d1" x="48" y="72" font-size="11.5" font-weight="700" letter-spacing="2.6" fill="{GOLD}">'
        f'INSTITUTIONAL DEVELOPMENT  ·  DIGITAL SOLUTIONS</text>',
        f'<text class="in d2" x="46" y="124" font-size="46" font-weight="800" fill="#ffffff">Adaa Consulting</text>',
        f'<text class="in d3" x="48" y="164" font-size="27" font-weight="700" fill="url(#goldtext)">أداء للاستشارات</text>',
        f'<line class="line" x1="48" y1="182" x2="168" y2="182" stroke="{GOLD}" stroke-width="2.5" stroke-linecap="round"/>',
        f'<text class="in d4" x="48" y="212" font-size="16" fill="#d3dcf0">Institutional development starts from within</text>',
        f'<text class="in d5" x="48" y="240" font-size="15" fill="#9fb0d4">التطوير المؤسسي يبدأ من الداخل</text>',
    ]
    return svg(h, "".join(body))


ICONS = [  # 24x24 line icons, one per product (same order as PRODUCTS)
    '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    '<path d="M3 21h18"/><rect x="5" y="11" width="3" height="7"/><rect x="10.5" y="5" width="3" height="13"/><rect x="16" y="13" width="3" height="5"/>',
    '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3M8 21h8"/>',
    '<path d="M4 5h16v11H9l-5 4z"/><path d="M12 8v4M12 14.5v.01"/>',
    '<rect x="3" y="6" width="18" height="13" rx="2"/><path d="M3 10h18M16 14.5h2"/>',
    '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3z"/>',
    '<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/>',
]
assert len(ICONS) == len(PRODUCTS)

GRADIENTS = (f'<linearGradient id="tile" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BLUE}"/>'
             f'<stop offset="1" stop-color="#3b7cf0"/></linearGradient>'
             f'<linearGradient id="accent" x1="0" x2="1"><stop offset="0" stop-color="{BLUE}"/>'
             f'<stop offset="1" stop-color="{GOLD}"/></linearGradient>')


def soft_chips(t, x, y, labels):
    out = []
    for label in labels:
        w = int(len(label) * 6.3) + 20  # shortcut: width estimated from char count; fine for short Latin labels
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="6" fill="{t["chip_soft"]}"/>'
                   f'<text x="{x + w / 2}" y="{y + 15}" text-anchor="middle" font-size="11.5" font-weight="600" fill="{t["muted"]}">{esc(label)}</text>')
        x += w + 6
    return "".join(out)


def products(t):
    cols, gap, ch = 2, 16, 182
    cw = (W - gap) // cols
    rows = (len(PRODUCTS) + 1) // cols
    h = rows * ch + (rows - 1) * gap + 2
    body = [f'<defs>{GRADIENTS}</defs>']
    for i, (en, ar, desc, tech) in enumerate(PRODUCTS):
        x = 1 + (i % cols) * (cw + gap)
        y = 1 + (i // cols) * (ch + gap)
        body.append(f'<rect x="{x}" y="{y}" width="{cw - 2}" height="{ch}" rx="14" fill="{t["card"]}" stroke="{t["border"]}"/>')
        body.append(f'<rect x="{x + 20}" y="{y}" width="{cw - 42}" height="3" rx="1.5" fill="url(#accent)"/>')
        body.append(f'<text x="{x + cw - 22}" y="{y + 52}" text-anchor="end" font-size="34" font-weight="800" fill="{t["muted"]}" fill-opacity=".16">{i + 1:02d}</text>')
        body.append(f'<rect x="{x + 20}" y="{y + 24}" width="48" height="48" rx="12" fill="url(#tile)"/>'
                    f'<g transform="translate({x + 32} {y + 36})" fill="none" stroke="#ffffff" stroke-width="1.8" '
                    f'stroke-linecap="round" stroke-linejoin="round">{ICONS[i]}</g>')
        body.append(f'<text x="{x + 84}" y="{y + 45}" font-size="17" font-weight="700" fill="{t["text"]}">{esc(en)}</text>')
        body.append(f'<text x="{x + 84}" y="{y + 68}" font-size="14" font-weight="600" fill="{t["blue"]}">{esc(ar)}</text>')
        for j, line in enumerate(wrap(desc, 58)[:2]):
            body.append(f'<text x="{x + 20}" y="{y + 104 + j * 19}" font-size="13" fill="{t["muted"]}">{esc(line)}</text>')
        body.append(f'<line x1="{x + 20}" y1="{y + ch - 46}" x2="{x + cw - 22}" y2="{y + ch - 46}" stroke="{t["border"]}" stroke-opacity=".6"/>')
        body.append(soft_chips(t, x + 20, y + ch - 34, tech))
    return svg(h, "".join(body))


MIME = {".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}


def logo_data(key):
    """Client logos are embedded exactly as published by the client: never recolour or edit them."""
    files = sorted(f for f in (HERE / "clients").glob(key + ".*") if f.suffix.lower() in MIME)
    if not files:
        return None
    f = files[0]
    return f"data:{MIME[f.suffix.lower()]};base64," + base64.b64encode(f.read_bytes()).decode()


def it_clients(t, dark):
    cols, gap, th = 3, 14, 168
    cw = (W - gap * (cols - 1)) // cols
    rows = -(-len(IT_CLIENTS) // cols)
    h = rows * th + (rows - 1) * gap + 2
    body = []
    for i, (key, en, ar) in enumerate(IT_CLIENTS):
        x = 1 + (i % cols) * (cw + gap)
        y = 1 + (i // cols) * (th + gap)
        body.append(f'<rect x="{x}" y="{y}" width="{cw - 2}" height="{th}" rx="14" fill="{t["card"]}" stroke="{t["border"]}"/>')
        data = logo_data(key)
        if dark:  # soft light plate behind the untouched logo so dark ink in logos stays readable
            body.append(f'<rect x="{x + 12}" y="{y + 10}" width="{cw - 26}" height="92" rx="10" fill="#ffffff"/>')
        if data:
            body.append(f'<image x="{x + 22}" y="{y + 16}" width="{cw - 46}" height="80" preserveAspectRatio="xMidYMid meet" href="{data}"/>')
        else:  # shortcut: text fallback when a logo file is missing; add scripts/clients/<key>.png to fix
            body.append(f'<text x="{x + cw / 2}" y="{y + 64}" text-anchor="middle" font-size="17" font-weight="800" fill="{t["blue"]}">{esc(ar)}</text>')
        body.append(f'<line x1="{x + 24}" y1="{y + 110}" x2="{x + cw - 26}" y2="{y + 110}" stroke="{t["border"]}" stroke-opacity=".7"/>')
        body.append(f'<text x="{x + cw / 2}" y="{y + 132}" text-anchor="middle" font-size="12" font-weight="700" fill="{t["text"]}">{esc(en)}</text>')
        body.append(f'<text x="{x + cw / 2}" y="{y + 153}" text-anchor="middle" font-size="12" font-weight="600" fill="{t["blue"]}">{esc(ar)}</text>')
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
    files = {"banner-animated.svg": banner(), "cta.svg": contact()}
    for theme, t in THEMES.items():
        files[f"solutions-{theme}.svg"] = products(t)
        files[f"consulting-{theme}.svg"] = clients(t)
        files[f"client-tiles-{theme}.svg"] = it_clients(t, theme == "dark")
        files[f"services-{theme}.svg"] = services(t)
    for old in out.glob("*.svg"):
        old.unlink()
    for name, content in files.items():
        minidom.parseString(content)  # self-check: invalid XML (e.g. a bare &) silently breaks the image on GitHub
        (out / name).write_text(content, encoding="utf-8")
        print("wrote", out / name)
