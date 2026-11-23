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

GOV_CLIENTS = [
    "Crown Prince's Office – Fujairah",
    "Fujairah Government Excellence Program",
    "Fujairah Chamber of Commerce & Industry",
    "Fujairah Customs Department",
    "Fujairah Tourism & Antiquities Authority",
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
FONT = "'JF Flat','Adaa',-apple-system,BlinkMacSystemFont,'Segoe UI','Geeza Pro','Noto Naskh Arabic',Tahoma,Helvetica,Arial,sans-serif"
# Adaa brand, taken from adaaconsulting.ae: royal blue, sand-gold, charcoal, light grey + white cards
PAGE, CARD, BORDER, TEXT, MUTED = "#f5f5f5", "#ffffff", "#c9d6f2", "#333333", "#666666"
BLUE, GOLD, CHARCOAL = "#0047BB", "#B6B098", "#2f2f2f"
LOGO = base64.b64encode((Path(__file__).resolve().parent / "logo-white.png").read_bytes()).decode()


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


def chip(x, y, label, strong=False):
    w = int(len(label) * 6.6) + 20  # shortcut: width estimated from char count; fine for short Latin labels
    fill, stroke, color = ("#e8effb", BLUE, BLUE) if strong else (CARD, GOLD, MUTED)
    return w, (f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="11" fill="{fill}" stroke="{stroke}"/>'
               f'<text x="{x + w / 2}" y="{y + 15}" text-anchor="middle" font-size="12" fill="{color}">{esc(label)}</text>')


def chip_rows(x0, y, labels, max_x, strong=False):
    """Lay chips left-to-right, wrapping to a new row; returns (svg, bottom y)."""
    out, x = [], x0
    for label in labels:
        w, _ = chip(0, 0, label, strong)
        if x + w > max_x:
            x, y = x0, y + 30
        out.append(chip(x, y, label, strong)[1])
        x += w + 8
    return "".join(out), y + 22


def svg(h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{h}" '
            f'viewBox="0 0 {W} {h}" font-family="{FONT}">{body}</svg>')


def page(h):
    return f'<rect width="{W}" height="{h}" rx="12" fill="{PAGE}"/>'


def slashes(x, y):
    # the site's sand-gold slash marks
    return "".join(f'<path d="M{x} {y + i * 26} l18 -8" stroke="{GOLD}" stroke-width="4" stroke-linecap="round"/>' for i in range(4))


def banner():
    h = 240
    body = [
        f'<rect width="{W}" height="{h}" rx="14" fill="{CHARCOAL}"/>',
        f'<path d="M{W - 260} 0 H{W - 14} a14 14 0 0 1 14 14 V{h - 14} a14 14 0 0 1 -14 14 H{W - 420} Z" fill="{BLUE}"/>',
        f'<path d="M{W - 300} 0 L{W - 460} {h}" stroke="{GOLD}" stroke-width="3"/>',
        slashes(40, 84),
        f'<image x="{W - 230}" y="45" width="200" height="150" xlink:href="data:image/png;base64,{LOGO}" href="data:image/png;base64,{LOGO}"/>',
        f'<text x="90" y="98" font-size="40" font-weight="800" fill="#ffffff">Adaa Consulting</text>',
        f'<text x="90" y="138" font-size="24" font-weight="700" fill="{GOLD}">أداء للاستشارات</text>',
        f'<text x="90" y="176" font-size="16" fill="#e5e5e5">Institutional development starts from within</text>',
        f'<text x="90" y="202" font-size="15" fill="#bdbdbd">التطوير المؤسسي يبدأ من الداخل</text>',
    ]
    return svg(h, "".join(body))


def products():
    cols, gap, pad, ch = 2, 16, 20, 150
    cw = (W - pad * 2 - gap) // cols
    rows = (len(PRODUCTS) + 1) // cols
    h = pad * 2 + rows * ch + (rows - 1) * gap
    body = [page(h)]
    for i, (en, ar, desc, tech) in enumerate(PRODUCTS):
        x = pad + (i % cols) * (cw + gap)
        y = pad + (i // cols) * (ch + gap)
        body.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="10" fill="{CARD}" stroke="{BORDER}"/>')
        body.append(f'<rect x="{x + 18}" y="{y + 18}" width="26" height="26" rx="7" fill="{GOLD}"/>'
                    f'<text x="{x + 31}" y="{y + 36}" text-anchor="middle" font-size="13" font-weight="700" fill="#ffffff">{i + 1:02d}</text>')
        body.append(f'<text x="{x + 54}" y="{y + 37}" font-size="16" font-weight="700" fill="{TEXT}">{esc(en)}</text>')
        body.append(f'<text x="{x + cw - 18}" y="{y + 37}" text-anchor="end" font-size="14" font-weight="600" fill="{BLUE}">{esc(ar)}</text>')
        for j, line in enumerate(wrap(desc, 56)[:2]):
            body.append(f'<text x="{x + 18}" y="{y + 70 + j * 18}" font-size="13" fill="{MUTED}">{esc(line)}</text>')
        body.append(chip_rows(x + 18, y + ch - 34, tech, x + cw - 18)[0])
    return svg(h, "".join(body))


def clients():
    pad = 24
    body, y = [], pad
    for title, ar, names, strong in (("Digital solutions delivered for", "حلول رقمية لـ", GOV_CLIENTS, True),
                                     ("Consulting clients", "عملاء الاستشارات", CONSULTING_CLIENTS, False)):
        body.append(f'<text x="{pad}" y="{y + 14}" font-size="15" font-weight="700" fill="{BLUE}">{title}</text>')
        body.append(f'<text x="{W - pad}" y="{y + 14}" text-anchor="end" font-size="14" font-weight="600" fill="{BLUE}">{esc(ar)}</text>')
        s, y = chip_rows(pad, y + 28, names, W - pad, strong)
        body.append(s)
        y += 30
    h = y - 6
    return svg(h, page(h) + "".join(body))


def services():
    cols, gap, pad, rh = 2, 12, 20, 48
    cw = (W - pad * 2 - gap) // cols
    rows = (len(SERVICES) + 1) // cols
    h = pad * 2 + rows * rh + (rows - 1) * gap
    body = [page(h)]
    for i, (en, ar) in enumerate(SERVICES):
        x = pad + (i % cols) * (cw + gap)
        y = pad + (i // cols) * (rh + gap)
        body.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{rh}" rx="8" fill="{CARD}" stroke="{BORDER}"/>')
        body.append(f'<rect x="{x + 14}" y="{y + 14}" width="20" height="20" rx="5" fill="{GOLD}"/>'
                    f'<path d="M{x + 19} {y + 24} l4 4 l7 -8" stroke="#ffffff" stroke-width="2" fill="none" stroke-linecap="round"/>')
        body.append(f'<text x="{x + 44}" y="{y + 29}" font-size="14" font-weight="600" fill="{TEXT}">{esc(en)}</text>')
        body.append(f'<text x="{x + cw - 16}" y="{y + 29}" text-anchor="end" font-size="13" fill="{MUTED}">{esc(ar)}</text>')
    return svg(h, "".join(body))


def contact():
    h = 170
    body = [
        f'<rect width="{W}" height="{h}" rx="12" fill="{BLUE}"/>',
        f'<path d="M{W - 80} 0 L{W - 210} {h}" stroke="{GOLD}" stroke-width="3" opacity=".8"/>',
        f'<text x="{W / 2}" y="52" text-anchor="middle" font-size="22" font-weight="700" fill="#ffffff">Ready to transform your organization?</text>',
        f'<text x="{W / 2}" y="82" text-anchor="middle" font-size="16" fill="#dbe6fb">جاهزون لمرافقتكم في رحلة التحول المؤسسي والرقمي</text>',
        f'<text x="{W / 2}" y="108" text-anchor="middle" font-size="13" fill="{GOLD}">Abu Dhabi · Dubai · Fujairah · Riyadh</text>',
        f'<rect x="{W / 2 - 120}" y="122" width="240" height="34" rx="8" fill="#ffffff"/>',
        f'<text x="{W / 2}" y="144" text-anchor="middle" font-size="14" font-weight="700" fill="{BLUE}">info@adaaconsulting.ae  →</text>',
    ]
    return svg(h, "".join(body))


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "profile" / "assets"
    for name, content in (("banner.svg", banner()), ("products.svg", products()),
                          ("clients.svg", clients()), ("services.svg", services()), ("contact.svg", contact())):
        minidom.parseString(content)  # self-check: invalid XML (e.g. a bare &) silently breaks the image on GitHub
        (out / name).write_text(content, encoding="utf-8")
        print("wrote", out / name)
