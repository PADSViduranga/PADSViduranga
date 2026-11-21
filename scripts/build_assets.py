#!/usr/bin/env python3
"""Generates the static SVG artwork for the profile README.

Run:  python scripts/build_assets.py
Edit the CONTENT section below to change text, then re-run.
"""
from pathlib import Path
from xml.sax.saxutils import escape as esc

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

# ───────────────────────── palette & type ─────────────────────────
BG0, BG1, BG2 = "#0c0408", "#1b0712", "#2b0a1d"
PINK, PINK2, ROSE = "#ff3d8b", "#ff7ab0", "#c2185b"
TEXT, MUTED, DIM, LINE = "#f7e8ef", "#c49aae", "#7d5167", "#5a1f3a"
PULSE = 'class="pulse"'
SERIF = "Georgia, 'Times New Roman', 'DejaVu Serif', serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', 'DejaVu Sans Mono', monospace"

STYLE = f"""
<style>
  .serif {{ font-family: {SERIF}; }}
  .mono  {{ font-family: {MONO}; }}
  .lbl   {{ font-family: {MONO}; font-size: 10.5px; letter-spacing: 2.2px; fill: {MUTED}; }}
  .num   {{ font-family: {MONO}; font-size: 10.5px; letter-spacing: 2px; fill: {PINK}; font-weight: 700; }}
  @keyframes blink {{ 0%,49% {{ opacity: 1 }} 50%,100% {{ opacity: 0 }} }}
  @keyframes pulse {{ 0%,100% {{ opacity: .35 }} 50% {{ opacity: 1 }} }}
  @keyframes glow  {{ 0%,100% {{ opacity: .55 }} 50% {{ opacity: .9 }} }}
  @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(8px) }} to {{ opacity: 1; transform: translateY(0) }} }}
  .cursor {{ animation: blink 1.1s step-end infinite; }}
  .pulse  {{ animation: pulse 2.4s ease-in-out infinite; }}
  .glow   {{ animation: glow 5s ease-in-out infinite; }}
  .rise   {{ animation: fadeUp .9s ease-out both; }}
</style>"""


def defs(w, h, uid):
    return f"""
<defs>
  <linearGradient id="bg{uid}" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{BG1}"/><stop offset=".55" stop-color="{BG0}"/><stop offset="1" stop-color="{BG2}"/>
  </linearGradient>
  <radialGradient id="halo{uid}" cx=".82" cy=".25" r=".7">
    <stop offset="0" stop-color="{PINK}" stop-opacity=".30"/><stop offset=".45" stop-color="{ROSE}" stop-opacity=".10"/><stop offset="1" stop-color="{BG0}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="edge{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{PINK}" stop-opacity="0"/><stop offset=".5" stop-color="{PINK}" stop-opacity=".9"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/>
  </linearGradient>
  <pattern id="grid{uid}" width="22" height="22" patternUnits="userSpaceOnUse">
    <path d="M22 0H0V22" fill="none" stroke="{PINK}" stroke-opacity=".05"/>
  </pattern>
</defs>"""


def frame(w, h, uid, x=0, y=0, rx=16, halo=True):
    """Card background: gradient, grid, glow, border, corner ticks, top edge highlight."""
    t = 10
    ticks = "".join(
        f'<path d="{d}" stroke="{PINK2}" stroke-opacity=".7" fill="none"/>'
        for d in (
            f"M{x+8} {y+8+t}V{y+8}H{x+8+t}",
            f"M{x+w-8-t} {y+8}H{x+w-8}V{y+8+t}",
            f"M{x+8} {y+h-8-t}V{y+h-8}H{x+8+t}",
            f"M{x+w-8-t} {y+h-8}H{x+w-8}V{y+h-8-t}",
        )
    )
    return f"""
<rect x="{x+.5}" y="{y+.5}" width="{w-1}" height="{h-1}" rx="{rx}" fill="url(#bg{uid})"/>
<rect x="{x+.5}" y="{y+.5}" width="{w-1}" height="{h-1}" rx="{rx}" fill="url(#grid{uid})"/>
{f'<rect class="glow" x="{x+.5}" y="{y+.5}" width="{w-1}" height="{h-1}" rx="{rx}" fill="url(#halo{uid})"/>' if halo else ''}
<rect x="{x+.5}" y="{y+.5}" width="{w-1}" height="{h-1}" rx="{rx}" fill="none" stroke="{LINE}"/>
<rect x="{x+w*.15}" y="{y}" width="{w*.7}" height="1.2" fill="url(#edge{uid})"/>
{ticks}"""


def svg(w, h, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{esc(title)}"><title>{esc(title)}</title>{body}</svg>\n'
    )


def chip(x, y, text, solid=False):
    w = len(text) * 6.6 + 18
    fill = PINK if solid else "none"
    col = BG0 if solid else PINK2
    return (
        f'<rect x="{x}" y="{y}" width="{w:.0f}" height="20" rx="4" fill="{fill}" fill-opacity="{1 if solid else 0}" stroke="{PINK}" stroke-opacity=".55"/>'
        f'<text x="{x + w/2:.0f}" y="{y+13.5}" text-anchor="middle" class="mono" font-size="10" font-weight="700" letter-spacing="1" fill="{col}">{esc(text)}</text>',
        w,
    )


def chips(x, y, items, gap=8):
    out = []
    for i, t in enumerate(items):
        c, w = chip(x, y, t, solid=(i == 0))
        out.append(c)
        x += w + gap
    return "".join(out)


def title_text(x, y, plain, italic="", size=34, anchor="start", accent_dot=False):
    dot = f'<tspan fill="{PINK}">.</tspan>' if accent_dot else ""
    it = f'<tspan font-style="italic" fill="{PINK2}">{esc(italic)}</tspan>' if italic else ""
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="serif" font-size="{size}" fill="{TEXT}">{esc(plain)}{it}{dot}</text>'


# ───────────────────────── HERO ─────────────────────────
def hero():
    W, H, u = 880, 370, "h"
    cx, cy = 715, 190
    b = defs(W, H, u) + STYLE.replace("</style>", f"""
  @keyframes spin  {{ to {{ transform: rotate(360deg) }} }}
  @keyframes spinr {{ to {{ transform: rotate(-360deg) }} }}
  .spin  {{ transform-origin: {cx}px {cy}px; animation: spin 40s linear infinite; }}
  .spinr {{ transform-origin: {cx}px {cy}px; animation: spinr 26s linear infinite; }}
</style>""") + frame(W, H, u)
    b += f"""
<defs>
  <radialGradient id="orb" cx=".35" cy=".3" r=".8">
    <stop offset="0" stop-color="{PINK2}"/><stop offset=".55" stop-color="{ROSE}"/><stop offset="1" stop-color="#3a0a22"/>
  </radialGradient>
</defs>
<!-- prompt pill -->
<g class="rise">
  <rect x="36" y="30" width="292" height="26" rx="13" fill="{BG0}" stroke="{LINE}"/>
  <circle cx="52" cy="43" r="3.5" fill="{PINK}" class="pulse"/>
  <text x="64" y="47" class="mono" font-size="11" fill="{MUTED}">~/sachintha <tspan fill="{PINK}">›</tspan> build --scalable <tspan class="cursor" fill="{PINK}">▍</tspan></text>
</g>
<text x="36" y="96" class="lbl rise">— 01 · SOFTWARE ENGINEERING · FULL-STACK · CLOUD</text>
<g class="rise" style="animation-delay:.15s">
  {title_text(34, 168, "Sachintha", size=66)}
  {title_text(34, 238, "Viduranga", size=66, accent_dot=True)}
</g>
<text x="36" y="274" class="mono rise" font-size="11.5" letter-spacing="2" font-weight="700" fill="{PINK2}" style="animation-delay:.3s">CS UNDERGRADUATE · FULL-STACK DEVELOPER · BACKEND</text>
<text x="36" y="302" class="serif rise" font-size="17" font-style="italic" fill="{TEXT}" style="animation-delay:.4s">Building ideas into real-world solutions.</text>
<line x1="36" y1="322" x2="520" y2="322" stroke="{LINE}"/>
<text x="36" y="342" class="lbl" font-size="9.5">BSc (HONS) CS · NSBM GREEN UNIVERSITY · 2025 — PRESENT · SRI LANKA</text>

<!-- monogram orb -->
<g>
  <circle cx="{cx}" cy="{cy}" r="128" fill="{PINK}" fill-opacity=".05" class="pulse"/>
  <circle class="spin"  cx="{cx}" cy="{cy}" r="112" fill="none" stroke="{PINK}" stroke-opacity=".45" stroke-dasharray="2 7"/>
  <g class="spinr">
    <circle cx="{cx}" cy="{cy}" r="94" fill="none" stroke="{PINK2}" stroke-opacity=".35" stroke-dasharray="60 18 4 18"/>
    <circle cx="{cx+94}" cy="{cy}" r="4" fill="{PINK}"/>
  </g>
  <circle cx="{cx}" cy="{cy}" r="74" fill="url(#orb)"/>
  <circle cx="{cx}" cy="{cy}" r="74" fill="none" stroke="{PINK2}" stroke-opacity=".8"/>
  <text x="{cx}" y="{cy+19}" text-anchor="middle" class="serif" font-size="56" font-style="italic" fill="{TEXT}">SV</text>
  <path d="M{cx-150} {cy-118}h34M{cx-150} {cy-118}v10" stroke="{MUTED}" stroke-opacity=".6" fill="none"/>
  <text x="{cx-148}" y="{cy-124}" class="mono" font-size="9" letter-spacing="1.5" fill="{DIM}">FIG. 01</text>
  <text x="{cx+86}" y="{cy+128}" class="mono" font-size="9" letter-spacing="1.5" fill="{DIM}">LK · 6.9°N</text>
  <path d="M{cx+80} {cy+118}h34" stroke="{MUTED}" stroke-opacity=".6"/>
</g>"""
    return svg(W, H, b, "Sachintha Viduranga — CS undergraduate and full-stack developer")


# ───────────────────────── SECTION HEADERS ─────────────────────────
def section(num, label, plain, italic, tag):
    W, H, u = 880, 104, "s"
    b = STYLE + f"""
<defs><linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{PINK}"/><stop offset=".35" stop-color="{PINK}" stop-opacity=".35"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></linearGradient></defs>
<text x="4" y="30"><tspan class="num">{num}</tspan><tspan class="lbl" dx="10">{esc(label)}</tspan></text>
<text x="876" y="30" text-anchor="end" class="lbl" font-size="9.5" fill="{DIM}">{esc(tag)}</text>
{title_text(2, 74, plain, italic, size=36)}
<rect x="2" y="90" width="876" height="1.4" fill="url(#ln)"/>
<circle cy="90.7" r="3" fill="{PINK2}"><animate attributeName="cx" values="4;600;4" dur="9s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;.2;1" dur="9s" repeatCount="indefinite"/></circle>"""
    return svg(W, H, b, f"{label}: {plain}{italic}")


# ───────────────────────── ABOUT ─────────────────────────
def about():
    W, H, u = 880, 300, "a"
    b = defs(W, H, u) + STYLE + frame(570, H, u)
    b += f"""
<circle cx="28" cy="26" r="5" fill="{PINK}"/><circle cx="46" cy="26" r="5" fill="{PINK2}" fill-opacity=".6"/><circle cx="64" cy="26" r="5" fill="{DIM}"/>
<text x="285" y="30" text-anchor="middle" class="mono" font-size="10.5" fill="{DIM}">sachintha@profile: ~</text>
<line x1="16" y1="44" x2="554" y2="44" stroke="{LINE}"/>"""
    rows = [
        ("whoami", "Sachintha Viduranga — CS undergraduate, full-stack dev"),
        ("cat education.txt", "BSc (Hons) Computer Science · NSBM Green University"),
        ("cat focus.txt", "Backend & enterprise apps · Cloud · DevOps · Microservices"),
        ("cat now.txt", "Exploring AI-powered software systems"),
        ("cat goal.txt", "Keep learning, build meaningful things, grow as an engineer."),
    ]
    y = 70
    for i, (cmd, out) in enumerate(rows):
        d = f'style="animation-delay:{.15*i:.2f}s"'
        b += f'<text x="28" y="{y}" class="mono rise" font-size="11.5" fill="{TEXT}" {d}><tspan fill="{PINK}">$</tspan> {esc(cmd)}</text>'
        b += f'<text x="28" y="{y+18}" class="mono rise" font-size="11" fill="{MUTED}" {d}><tspan fill="{PINK2}">→</tspan> {esc(out)}</text>'
        y += 42
    b += f'<text x="28" y="{y-6}" class="mono" font-size="12" fill="{PINK}">$ <tspan class="cursor">▍</tspan></text>'

    side = [
        ("PRIMARY STACK", "Java · Spring Boot", "backend services · REST APIs"),
        ("ALSO SHIPPING", "React · ASP.NET Core", "full-stack web apps"),
        ("EXPLORING", "Cloud · AI systems", "DevOps · microservices"),
    ]
    for i, (lab, val, sub) in enumerate(side):
        y0 = i * 102
        b += frame(296, 92, f"a{i}", x=584, y=y0, rx=12, halo=(i == 0))
        b += defs(296, 92, f"a{i}")
        b += f'<text x="604" y="{y0+28}" class="lbl" font-size="9.5"><tspan fill="{PINK}">0{i+1}</tspan>  {esc(lab)}</text>'
        b += f'<text x="604" y="{y0+58}" class="serif" font-size="21" fill="{TEXT}">{esc(val)}</text>'
        b += f'<text x="604" y="{y0+78}" class="mono" font-size="10" fill="{DIM}">{esc(sub)}</text>'
    return svg(W, H, b, "About Sachintha")


# ───────────────────────── PROJECTS ─────────────────────────
def art_pipeline(x, y):  # ApexHire
    stages = ["APPLIED", "SCREEN", "INTERVIEW", "OFFER"]
    out = f'<path id="pp" d="M{x} {y+60} C{x+60} {y+60},{x+60} {y+20},{x+110} {y+20} S{x+170} {y+90},{x+230} {y+50}" fill="none" stroke="{PINK}" stroke-opacity=".5" stroke-dasharray="3 4"/>'
    pts = [(x, y + 60), (x + 75, y + 30), (x + 160, y + 62), (x + 230, y + 50)]
    for i, ((px, py), s) in enumerate(zip(pts, stages)):
        out += f'<circle cx="{px}" cy="{py}" r="{6 if i < 3 else 9}" fill="{BG0}" stroke="{PINK2}"/>'
        out += f'<text x="{px}" y="{py+(26 if i%2==0 else -16)}" text-anchor="middle" class="mono" font-size="8.5" letter-spacing="1.2" fill="{MUTED}">{s}</text>'
    out += f'<circle cx="{x+230}" cy="{y+50}" r="3.5" fill="{PINK}" class="pulse"/>'
    out += f'<circle r="4" fill="{PINK}"><animateMotion dur="4s" repeatCount="indefinite"><mpath href="#pp"/></animateMotion></circle>'
    return out


def art_grid(x, y):  # ResQGrid
    out = ""
    nodes = [(0, 0), (2, 1), (4, 0), (1, 3), (3, 3), (5, 2), (6, 4), (0, 5), (4, 5)]
    edges = [(0, 1), (1, 2), (1, 3), (1, 4), (2, 5), (4, 5), (5, 6), (3, 7), (4, 8), (6, 8)]
    s = 36
    for i in range(7):
        for j in range(6):
            out += f'<circle cx="{x+i*s}" cy="{y+j*22}" r="1" fill="{PINK}" fill-opacity=".3"/>'
    P = [(x + a * s, y + b_ * 22) for a, b_ in nodes]
    for a, c in edges:
        out += f'<line x1="{P[a][0]}" y1="{P[a][1]}" x2="{P[c][0]}" y2="{P[c][1]}" stroke="{PINK}" stroke-opacity=".45"/>'
    for k, (px, py) in enumerate(P):
        hub = k in (1, 5)
        out += f'<circle cx="{px}" cy="{py}" r="{5 if hub else 3}" fill="{PINK if hub else PINK2}" {PULSE if hub else ""}/>'
        if hub:
            out += f'<circle cx="{px}" cy="{py}" r="5" fill="none" stroke="{PINK}"><animate attributeName="r" values="5;16" dur="2.2s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;0" dur="2.2s" repeatCount="indefinite"/></circle>'
    out += f'<text x="{x}" y="{y+132}" class="mono" font-size="8.5" letter-spacing="1.2" fill="{DIM}">SUPPLY HUBS · ROUTES · DEMAND ZONES</text>'
    return out


def art_eq(x, y):  # SonicFlow
    out = ""
    for i in range(22):
        h1, h2 = 14 + (i * 37) % 70, 10 + (i * 53) % 80
        dur = 0.8 + (i % 5) * 0.17
        out += (f'<rect x="{x+i*10}" width="6" rx="2" fill="{PINK if i%4 else PINK2}" fill-opacity="{.5+ (i%3)*.2:.1f}">'
                f'<animate attributeName="height" values="{h1};{h2};{h1}" dur="{dur:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="y" values="{y+100-h1};{y+100-h2};{y+100-h1}" dur="{dur:.2f}s" repeatCount="indefinite"/></rect>')
    out += f'<line x1="{x}" y1="{y+112}" x2="{x+216}" y2="{y+112}" stroke="{LINE}"/>'
    out += f'<rect x="{x}" y="{y+110}" width="86" height="4" rx="2" fill="{PINK}"/><circle cx="{x+86}" cy="{y+112}" r="5" fill="{TEXT}"/>'
    out += f'<text x="{x}" y="{y+132}" class="mono" font-size="8.5" letter-spacing="1.2" fill="{DIM}">01:24</text><text x="{x+216}" y="{y+132}" text-anchor="end" class="mono" font-size="8.5" fill="{DIM}">03:47</text>'
    return out


def art_risk(x, y):  # FraudShield
    pts = [8, 12, 9, 14, 11, 10, 15, 12, 13, 58, 18, 12, 14, 11, 16, 13]
    d = " ".join(f"{'M' if i==0 else 'L'}{x+i*14.5:.1f} {y+100-v}" for i, v in enumerate(pts))
    out = f'<line x1="{x}" y1="{y+60}" x2="{x+218}" y2="{y+60}" stroke="{PINK}" stroke-opacity=".5" stroke-dasharray="4 4"/>'
    out += f'<text x="{x}" y="{y+54}" class="mono" font-size="8.5" fill="{PINK2}">THRESHOLD</text>'
    out += f'<path d="{d}" fill="none" stroke="{PINK}" stroke-opacity=".45" stroke-width="1.4"/>'
    out += f'<path d="{d}" fill="none" stroke="{PINK2}" stroke-width="1.8" stroke-dasharray="400" stroke-dashoffset="400"><animate attributeName="stroke-dashoffset" values="400;0;0" keyTimes="0;.6;1" dur="5s" repeatCount="indefinite"/></path>'
    ax, ay = x + 9 * 14.5, y + 100 - 58
    out += f'<circle cx="{ax}" cy="{ay}" r="5" fill="{PINK}" class="pulse"/>'
    out += f'<rect x="{ax+10}" y="{ay-16}" width="62" height="18" rx="3" fill="{PINK}"/><text x="{ax+41}" y="{ay-4}" text-anchor="middle" class="mono" font-size="9" font-weight="700" fill="{BG0}">ALERT ↑</text>'
    out += f'<text x="{x}" y="{y+132}" class="mono" font-size="8.5" letter-spacing="1.2" fill="{DIM}">TRANSACTION RISK SCORE · REAL-TIME</text>'
    return out


def art_code(x, y):  # CodeQuest
    out = f'<text x="{x}" y="{y+56}" class="mono" font-size="54" fill="{PINK}" fill-opacity=".85">{{ }}</text>'
    for i in range(5):
        done = i < 3
        out += f'<circle cx="{x+8+i*26}" cy="{y+86}" r="7" fill="{PINK if done else "none"}" stroke="{PINK2}" {PULSE if i==3 else ""}/>'
        if i < 4:
            out += f'<line x1="{x+15+i*26}" y1="{y+86}" x2="{x+27+i*26}" y2="{y+86}" stroke="{LINE}"/>'
    out += f'<text x="{x}" y="{y+112}" class="mono" font-size="8.5" letter-spacing="1.2" fill="{DIM}">LEVEL 04 / 05</text>'
    return out


def art_scan(x, y):  # PixelProof
    out = f'<rect x="{x}" y="{y}" width="120" height="92" rx="6" fill="{BG0}" stroke="{PINK2}" stroke-opacity=".7"/>'
    for i in range(6):
        for j in range(4):
            op = .08 + ((i * 7 + j * 3) % 5) * .07
            out += f'<rect x="{x+8+i*18}" y="{y+8+j*19}" width="14" height="15" rx="2" fill="{PINK}" fill-opacity="{op:.2f}"/>'
    out += f'<rect x="{x+2}" width="116" height="2" fill="{PINK}"><animate attributeName="y" values="{y+4};{y+86};{y+4}" dur="3.2s" repeatCount="indefinite"/></rect>'
    out += f'<text x="{x}" y="{y+112}" class="mono" font-size="8.5" letter-spacing="1.2" fill="{DIM}">SCANNING…</text>'
    return out


PROJECTS = [
    dict(slug="apexhire", n="01", cat="FULL-STACK · RECRUITMENT", name="ApexHire", sub="Full-stack recruitment platform",
         desc=["A modern recruitment platform that takes a candidate from", "application to offer, built with React and ASP.NET Core."],
         stack=["REACT", ".NET", "SQL SERVER"], art=art_pipeline),
    dict(slug="resqgrid", n="02", cat="LOGISTICS · OPTIMISATION", name="ResQGrid", sub="Disaster logistics & resource optimisation",
         desc=["A disaster logistics system that helps get the right", "resources to the right place when it matters most."],
         stack=["SPRING BOOT", "REACT", "MYSQL"], art=art_grid),
    dict(slug="sonicflow", n="03", cat="FRONTEND · MEDIA", name="SonicFlow", sub="Online music player",
         desc=["A modern music player built with React, Vite and the", "HTML5 Audio API."],
         stack=["REACT", "VITE", "JAVASCRIPT"], art=art_eq),
    dict(slug="fraudshield", n="04", cat="SECURITY · FINTECH", name="FraudShield", sub="Financial fraud detection system",
         desc=["Fraud detection and investigation system with risk", "scoring and alert management."],
         stack=["PHP", "MYSQL"], art=art_risk),
]
SMALL = [
    dict(slug="codequest", n="05", cat="MOBILE · GAME", name="CodeQuest", sub="Interactive coding puzzle game",
         desc=["Mobile game with coding challenges", "and interactive gameplay."], stack=["FLUTTER", "DART", "FIREBASE"], art=art_code),
    dict(slug="pixelproof", n="06", cat="AI · VISION", name="PixelProof AI", sub="AI-powered image analysis",
         desc=["Full-stack image analysis project", "combining React and ASP.NET Core."], stack=["REACT", "ASP.NET CORE"], art=art_scan),
]


def project_card(p):
    W, H, u = 880, 236, p["slug"]
    b = defs(W, H, u) + STYLE + frame(W, H, u)
    b += f'<text x="32" y="40"><tspan class="num">{p["n"]}</tspan><tspan class="lbl" dx="10">{p["cat"]}</tspan></text>'
    b += title_text(30, 92, p["name"], size=42)
    b += f'<text x="32" y="116" class="mono" font-size="11" letter-spacing="1.5" font-weight="700" fill="{PINK2}">{esc(p["sub"].upper())}</text>'
    for i, line in enumerate(p["desc"]):
        b += f'<text x="32" y="{146+i*20}" class="serif" font-size="15" fill="{MUTED}">{esc(line)}</text>'
    b += f'<text x="32" y="{196}" class="lbl" font-size="9"><tspan fill="{PINK}">BUILT</tspan> ·</text>'
    b += chips(92, 183, p["stack"])
    b += f'<line x1="582" y1="30" x2="582" y2="206" stroke="{LINE}"/>'
    b += p["art"](614, 58)
    return svg(W, H, b, f'{p["name"]} — {p["sub"]}')


def small_card(p):
    W, H, u = 430, 250, p["slug"]
    b = defs(W, H, u) + STYLE + frame(W, H, u)
    b += f'<text x="26" y="38"><tspan class="num">{p["n"]}</tspan><tspan class="lbl" dx="10">{p["cat"]}</tspan></text>'
    b += title_text(24, 84, p["name"], size=32)
    b += f'<text x="26" y="106" class="mono" font-size="9.5" letter-spacing="1.2" font-weight="700" fill="{PINK2}">{esc(p["sub"].upper())}</text>'
    for i, line in enumerate(p["desc"]):
        b += f'<text x="26" y="{136+i*19}" class="serif" font-size="14" fill="{MUTED}">{esc(line)}</text>'
    b += chips(26, 200, p["stack"], gap=6)
    b += p["art"](290, 34)
    return svg(W, H, b, f'{p["name"]} — {p["sub"]}')


# ───────────────────────── TOOLKIT ─────────────────────────
TOOLS = [
    ("LANGUAGES", "Java · C#", "Python · JavaScript", "PHP · Dart · TypeScript", "PRIMARY"),
    ("FRONTEND & MOBILE", "React · Next.js", "Flutter", "HTML · CSS · Vite", ""),
    ("BACKEND & APIS", "Spring Boot", "ASP.NET Core · Node.js", "REST APIs", ""),
    ("DATA", "MySQL · PostgreSQL", "MongoDB · SQL Server", "Firebase", ""),
    ("CLOUD & TOOLING", "Git · GitHub", "Docker · AWS", "Vercel · VS Code", ""),
    ("EXPLORING", "Microservices", "DevOps · CI/CD", "AI-powered systems", "NOW"),
]


def toolkit():
    W, H = 880, 336
    cw, ch, g = 284, 160, 14
    b = STYLE
    for i, (lab, l1, l2, l3, tag) in enumerate(TOOLS):
        x, y = (i % 3) * (cw + g), (i // 3) * (ch + g)
        u = f"t{i}"
        b += defs(cw, ch, u) + frame(cw, ch, u, x=x, y=y, rx=12, halo=(i in (0, 5)))
        b += f'<text x="{x+22}" y="{y+32}" class="lbl" font-size="9.5"><tspan fill="{PINK}">0{i+1}</tspan>  {esc(lab)}</text>'
        if tag:
            b += f'<text x="{x+cw-20}" y="{y+32}" text-anchor="end" class="mono" font-size="8.5" letter-spacing="1.5" fill="{PINK2}">● {tag}</text>'
        b += f'<text x="{x+22}" y="{y+72}" class="serif" font-size="23" fill="{TEXT}">{esc(l1)}</text>'
        b += f'<text x="{x+22}" y="{y+100}" class="serif" font-size="17" fill="{TEXT}" fill-opacity=".85">{esc(l2)}</text>'
        b += f'<text x="{x+22}" y="{y+132}" class="mono" font-size="10.5" letter-spacing=".5" fill="{MUTED}">{esc(l3)}</text>'
    return svg(W, H, b, "Toolkit")


# ───────────────────────── FOOTER ─────────────────────────
def footer():
    W, H, u = 880, 230, "f"
    b = defs(W, H, u) + STYLE + frame(W, H, u)
    b += f"""
<radialGradient id="fh" cx=".5" cy="1" r=".7"><stop offset="0" stop-color="{PINK}" stop-opacity=".35"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></radialGradient>
<rect x="1" y="1" width="878" height="228" rx="16" fill="url(#fh)" class="glow"/>"""
    import random
    r = random.Random(7)
    for _ in range(26):
        x, y, d = r.randint(30, 850), r.randint(20, 210), r.uniform(2, 6)
        b += f'<circle cx="{x}" cy="{y}" r="{r.choice([1,1,1.5,2])}" fill="{PINK2}"><animate attributeName="opacity" values="0;.9;0" dur="{d:.1f}s" begin="{r.uniform(0,4):.1f}s" repeatCount="indefinite"/></circle>'
    b += f'<text x="440" y="112" text-anchor="middle" class="serif" font-size="58" font-style="italic" fill="{TEXT}">Sachintha<tspan fill="{PINK}">.</tspan></text>'
    b += f'<text x="440" y="150" text-anchor="middle" class="serif" font-size="17" font-style="italic" fill="{PINK2}">Code today. Build tomorrow.</text>'
    b += f'<text x="440" y="186" text-anchor="middle" class="lbl" font-size="9.5">ALWAYS LEARNING · ALWAYS BUILDING · TURNING IDEAS INTO REALITY</text>'
    return svg(W, H, b, "Code today. Build tomorrow.")


if __name__ == "__main__":
    files = {
        "hero.svg": hero(),
        "about.svg": about(),
        "toolkit.svg": toolkit(),
        "footer.svg": footer(),
        "sec-about.svg": section("01", "ABOUT", "Hello, I'm ", "Sachintha.", "WHO · WHAT · WHY"),
        "sec-work.svg": section("02", "SELECTED WORK", "Projects, not ", "assignments.", "SIX BUILDS · FULL-STACK"),
        "sec-tools.svg": section("03", "TOOLKIT", "The tools I ", "reach for.", "LANGUAGES · FRAMEWORKS · CLOUD"),
        "sec-log.svg": section("04", "COMMIT LOG", "A year of ", "building.", "REAL DATA · UPDATED DAILY"),
        "sec-stats.svg": section("05", "GITHUB AT A GLANCE", "Numbers, ", "honestly.", "LIVE STATS"),
        "sec-connect.svg": section("06", "CONNECT", "Let's build something ", "worth shipping.", "EMAIL · LINKEDIN · GITHUB"),
    }
    for p in PROJECTS:
        files[f"project-{p['slug']}.svg"] = project_card(p)
    for p in SMALL:
        files[f"project-{p['slug']}.svg"] = small_card(p)
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
    print(f"wrote {len(files)} files to {OUT}")
