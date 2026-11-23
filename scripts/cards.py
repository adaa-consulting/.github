"""Generate the SVG images for profile/README.md. Edit the data below, then run: python3 scripts/cards.py"""
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
    ("Meetings & AI Minutes", "الاجتماعات والمحاضر الذكية",
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
    ("Digital Transformation & AI", "التحول الرقمي والذكاء الاصطناعي"),
]

W = 854
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Geeza Pro','Noto Naskh Arabic',Tahoma,Helvetica,Arial,sans-serif"
BG, CARD, BORDER, TEXT, MUTED = "#0d1117", "#161b22", "#30363d", "#e6edf3", "#8b949e"
ACCENT, ACCENT2 = "#2dd4bf", "#0e7490"  # teal brand-neutral accent; swap for Adaa's official colors if available


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
    fill, stroke, color = ("#0b3b3a", ACCENT, ACCENT) if strong else (BG, BORDER, MUTED)
    return w, (f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="11" fill="{fill}" stroke="{stroke}"/>'
               f'<text x="{x + w / 2}" y="{y + 15}" text-anchor="middle" font-size="12" fill="{color}">{esc(label)}</text>')


def chip_rows(x0, y, labels, max_x, strong=False):
    """Lay chips left-to-right, wrapping to a new row; returns (svg, bottom y)."""
    out, x = [], x0
    for label in labels:
        w, s = chip(0, 0, label, strong)
        if x + w > max_x:
            x, y = x0, y + 30
        out.append(chip(x, y, label, strong)[1])
        x += w + 8
    return "".join(out), y + 22


def svg(h, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" font-family="{FONT}">'
            f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#042f2e"/>'
            f'<stop offset=".55" stop-color="#0f3d45"/><stop offset="1" stop-color="{ACCENT2}"/></linearGradient>{defs}</defs>'
            f'{body}</svg>')


def banner():
    h = 230
    body = [
        f'<rect width="{W}" height="{h}" rx="14" fill="url(#g)"/>',
        f'<circle cx="{W - 70}" cy="40" r="120" fill="{ACCENT}" fill-opacity=".07"/>',
        f'<circle cx="{W - 30}" cy="200" r="70" fill="{ACCENT}" fill-opacity=".06"/>',
        f'<text x="{W / 2}" y="82" text-anchor="middle" font-size="44" font-weight="800" fill="#ffffff">Adaa Consulting</text>',
        f'<text x="{W / 2}" y="124" text-anchor="middle" direction="rtl" font-size="28" font-weight="700" fill="{ACCENT}">أداء للاستشارات</text>',
        f'<line x1="{W / 2 - 60}" y1="146" x2="{W / 2 + 60}" y2="146" stroke="{ACCENT}" stroke-opacity=".6" stroke-width="2"/>',
        f'<text x="{W / 2}" y="176" text-anchor="middle" font-size="17" fill="#d1fae5">Institutional development starts from within</text>',
        f'<text x="{W / 2}" y="204" text-anchor="middle" direction="rtl" font-size="16" fill="#99f6e4">التطوير المؤسسي يبدأ من الداخل</text>',
    ]
    return svg(h, "".join(body))


def products():
    cols, gap, pad, ch = 2, 16, 20, 150
    cw = (W - pad * 2 - gap) // cols
    rows = (len(PRODUCTS) + 1) // cols
    h = pad * 2 + rows * ch + (rows - 1) * gap
    body = [f'<rect width="{W}" height="{h}" rx="12" fill="{BG}"/>']
    for i, (en, ar, desc, tech) in enumerate(PRODUCTS):
        x = pad + (i % cols) * (cw + gap)
        y = pad + (i // cols) * (ch + gap)
        body.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="10" fill="{CARD}" stroke="{BORDER}"/>')
        body.append(f'<rect x="{x}" y="{y + 18}" width="3" height="40" rx="1.5" fill="{ACCENT}"/>')
        body.append(f'<text x="{x + 18}" y="{y + 36}" font-size="16" font-weight="700" fill="{TEXT}">{esc(en)}</text>')
        body.append(f'<text x="{x + cw - 18}" y="{y + 36}" text-anchor="end" font-size="14" font-weight="600" fill="{ACCENT}">{esc(ar)}</text>')
        for j, line in enumerate(wrap(desc, 56)[:2]):
            body.append(f'<text x="{x + 18}" y="{y + 64 + j * 18}" font-size="13" fill="{MUTED}">{esc(line)}</text>')
        body.append(chip_rows(x + 18, y + ch - 36, tech, x + cw - 18)[0])
    return svg(h, "".join(body))


def clients():
    pad = 24
    body = []
    y = pad
    for title, ar, names, strong in (("DIGITAL SOLUTIONS DELIVERED FOR", "حلول رقمية لـ", GOV_CLIENTS, True),
                                     ("CONSULTING CLIENTS", "عملاء الاستشارات", CONSULTING_CLIENTS, False)):
        body.append(f'<text x="{pad}" y="{y + 12}" font-size="11" font-weight="700" letter-spacing="1" fill="{ACCENT}">{title}</text>')
        body.append(f'<text x="{W - pad}" y="{y + 12}" text-anchor="end" font-size="13" font-weight="600" fill="{ACCENT}">{esc(ar)}</text>')
        s, y = chip_rows(pad, y + 26, names, W - pad, strong)
        body.append(s)
        y += 30
    h = y - 6
    return svg(h, f'<rect width="{W}" height="{h}" rx="12" fill="{BG}"/>' + "".join(body))


def services():
    cols, gap, pad, rh = 2, 12, 20, 46
    cw = (W - pad * 2 - gap) // cols
    rows = (len(SERVICES) + 1) // cols
    h = pad * 2 + rows * rh + (rows - 1) * gap
    body = [f'<rect width="{W}" height="{h}" rx="12" fill="{BG}"/>']
    for i, (en, ar) in enumerate(SERVICES):
        x = pad + (i % cols) * (cw + gap)
        y = pad + (i // cols) * (rh + gap)
        body.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{rh}" rx="10" fill="{CARD}" stroke="{BORDER}"/>')
        body.append(f'<circle cx="{x + 20}" cy="{y + rh / 2}" r="4" fill="{ACCENT}"/>')
        body.append(f'<text x="{x + 34}" y="{y + 28}" font-size="14" font-weight="600" fill="{TEXT}">{esc(en)}</text>')
        body.append(f'<text x="{x + cw - 16}" y="{y + 28}" text-anchor="end" font-size="13" fill="{MUTED}">{esc(ar)}</text>')
    return svg(h, "".join(body))


def contact():
    h = 160
    body = [
        f'<rect x="1" y="1" width="{W - 2}" height="{h - 2}" rx="12" fill="url(#g)" stroke="{ACCENT}" stroke-opacity=".5"/>',
        f'<text x="{W / 2}" y="50" text-anchor="middle" font-size="22" font-weight="700" fill="#ffffff">Ready to transform your organization?</text>',
        f'<text x="{W / 2}" y="78" text-anchor="middle" direction="rtl" font-size="16" fill="#99f6e4">جاهزون لمرافقتكم في رحلة التحول المؤسسي والرقمي</text>',
        f'<text x="{W / 2}" y="104" text-anchor="middle" font-size="13" fill="#c9d1d9">Abu Dhabi · Dubai · Fujairah · Riyadh</text>',
        f'<rect x="{W / 2 - 120}" y="116" width="240" height="32" rx="16" fill="{ACCENT}"/>',
        f'<text x="{W / 2}" y="137" text-anchor="middle" font-size="14" font-weight="700" fill="#042f2e">info@adaaconsulting.ae  →</text>',
    ]
    return svg(h, "".join(body))


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "profile" / "assets"
    for name, content in (("banner.svg", banner()), ("products.svg", products()),
                          ("clients.svg", clients()), ("services.svg", services()), ("contact.svg", contact())):
        minidom.parseString(content)  # self-check: invalid XML (e.g. a bare &) silently breaks the image on GitHub
        (out / name).write_text(content, encoding="utf-8")
        print("wrote", out / name)
