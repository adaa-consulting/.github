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
.photo{transform-origin:50% 50%;animation:zoom 24s ease-in-out infinite alternate}
@keyframes zoom{from{transform:scale(1)}to{transform:scale(1.07)}}
.in{animation:rise .9s cubic-bezier(.2,.7,.2,1) both}
.d1{animation-delay:.2s}.d2{animation-delay:.4s}.d3{animation-delay:.6s}.d4{animation-delay:.8s}.d5{animation-delay:1s}
@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
.slash{animation:slash .7s cubic-bezier(.2,.7,.2,1) both}
@keyframes slash{from{opacity:0;transform:translateX(-14px)}to{opacity:1;transform:none}}
.shine{animation:shine 5s 2s ease-in-out infinite}
@keyframes shine{0%{transform:translateX(-120px)}40%,100%{transform:translateX(320px)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""
PHOTO = base64.b64encode((HERE / "hero-photo.jpg").read_bytes()).decode()  # Adaa's own hero image from adaaconsulting.ae
ADAA_LOGO = base64.b64encode((HERE / "adaa-logo-color.png").read_bytes()).decode()  # official colour logo (training-platform repo), unaltered


def banner():
    """Mirrors the adaaconsulting.ae hero: team photo under a charcoal overlay, gold slash marks,
    white Arabic-first headline, royal-blue call-to-action. Brand colours only."""
    h = 300
    right = W - 44
    slashes = "".join(
        f'<path class="slash" style="animation-delay:{.15 + i * .12:.2f}s" d="M34 {124 + i * 28} l20 -9" '
        f'stroke="{GOLD}" stroke-width="5" stroke-linecap="round"/>' for i in range(4))
    btn_w, btn_x, btn_y = 214, right - 214, 222
    body = [
        f'<defs><style>{BANNER_CSS}</style>'
        f'<clipPath id="card"><rect width="{W}" height="{h}" rx="16"/></clipPath>'
        f'<clipPath id="btn"><rect x="{btn_x}" y="{btn_y}" width="{btn_w}" height="44" rx="8"/></clipPath>'
        f'<linearGradient id="shade" x1="0" x2="1"><stop offset="0" stop-color="{CHARCOAL}" stop-opacity=".5"/>'
        f'<stop offset=".42" stop-color="{CHARCOAL}" stop-opacity=".82"/><stop offset="1" stop-color="{CHARCOAL}" stop-opacity=".93"/></linearGradient>'
        f'<radialGradient id="corner" cx="0" cy="0" r="1"><stop offset="0" stop-color="{CHARCOAL}" stop-opacity=".9"/>'
        f'<stop offset="1" stop-color="{CHARCOAL}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="gloss" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="#fff" stop-opacity=".28"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>',
        '<g clip-path="url(#card)">',
        f'<rect width="{W}" height="{h}" fill="{CHARCOAL}"/>',
        f'<image class="photo" width="{W}" height="{h}" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{PHOTO}"/>',
        f'<rect width="{W}" height="{h}" fill="url(#shade)"/>',
        f'<rect width="420" height="230" fill="url(#corner)"/>',
        f'<rect y="{h - 4}" width="{W}" height="4" fill="{BLUE}"/>',
        '</g>',
        f'<image class="in d1" x="30" y="26" width="196" height="{196 * 225 / 760:.1f}" href="data:image/png;base64,{ADAA_LOGO}"/>',
        slashes,
        f'<text class="in d1" x="{right}" y="132" text-anchor="end" font-size="38" font-weight="700" fill="#ffffff">التطوير المؤسسي يبدأ من الداخل</text>',
        f'<text class="in d2" x="{right}" y="168" text-anchor="end" font-size="18" fill="#f5f5f5">حلول استشارية مبتكرة تعتمد على المعرفة والتجربة</text>',
        f'<text class="in d3" x="{right}" y="200" text-anchor="end" font-size="14" font-weight="600" fill="{GOLD}" letter-spacing=".4">'
        f'ADAA CONSULTING  ·  Institutional development starts from within</text>',
        f'<g class="in d4"><rect x="{btn_x}" y="{btn_y}" width="{btn_w}" height="44" rx="8" fill="{BLUE}"/>'
        f'<g clip-path="url(#btn)"><rect class="shine" x="{btn_x - 60}" y="{btn_y}" width="60" height="44" fill="url(#gloss)"/></g>'
        f'<text x="{btn_x + btn_w / 2}" y="{btn_y + 28}" text-anchor="middle" font-size="15" font-weight="700" fill="#ffffff">adaaconsulting.ae</text></g>',
        f'<text class="in d5" x="72" y="{h - 26}" font-size="12.5" fill="#f5f5f5" fill-opacity=".85">Abu Dhabi  ·  Dubai  ·  Fujairah  ·  Riyadh</text>',
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
    files = {"adaa-hero-v3.svg": banner(), "cta.svg": contact()}
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
