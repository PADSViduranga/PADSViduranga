#!/usr/bin/env python3
"""Draws assets/commit-log.svg from your real GitHub contribution calendar.

Runs daily in GitHub Actions (see .github/workflows/commit-log.yml).
Local run:  GITHUB_TOKEN=<token> python scripts/commit_log.py PADSviduranga
Demo run (fake data, for previewing the design only):  python scripts/commit_log.py --demo
"""
import json, os, sys, urllib.request, datetime as dt, random
from pathlib import Path
from xml.sax.saxutils import escape as esc

sys.path.insert(0, str(Path(__file__).parent))
from build_assets import defs, frame, STYLE, svg, BG0, PINK, PINK2, TEXT, MUTED, DIM, LINE  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "assets" / "commit-log.svg"
QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount}}}}}}"""


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "commit-log"},
    )
    data = json.load(urllib.request.urlopen(req))
    if "errors" in data:
        raise SystemExit(data["errors"])
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return [[(d["date"], d["contributionCount"]) for d in w["contributionDays"]] for w in cal["weeks"]]


def demo():
    start = dt.date.today() - dt.timedelta(days=364 + dt.date.today().isoweekday() % 7)
    r, weeks = random.Random(3), []
    for w in range(53):
        week = []
        for d in range(7):
            day = start + dt.timedelta(days=w * 7 + d)
            if day > dt.date.today():
                break
            act = r.random() < (0.25 + 0.6 * (w / 53))
            week.append((day.isoformat(), r.randint(1, 14) if act else 0))
        weeks.append(week)
    return weeks


def stats(weeks):
    days = [d for w in weeks for d in w]
    total = sum(c for _, c in days)
    active = sum(1 for _, c in days if c)
    best = run = 0
    best_end = run_start = best_start = None
    for date, c in days:
        if c:
            run_start = run_start if run else date
            run += 1
            if run > best:
                best, best_start, best_end = run, run_start, date
        else:
            run = 0
    busiest = max(days, key=lambda d: d[1]) if days else ("", 0)
    return total, active, len(days), best, best_start, best_end, busiest


def fmt(d):
    return dt.date.fromisoformat(d).strftime("%d %b %Y").upper() if d else "—"


def level(c, mx):
    if c == 0:
        return 0
    return min(4, 1 + int(3 * c / max(mx, 1)))


def draw(weeks, login):
    W, H, u = 880, 300, "c"
    total, active, ndays, best, bs, be, busiest = stats(weeks)
    mx = max((c for w in weeks for _, c in w), default=1)
    fills = [(PINK, .07), ("#7a1440", .9), ("#b8195e", .95), (PINK, 1), (PINK2, 1)]
    b = defs(W, H, u) + STYLE + frame(W, H, u)
    b += f'<text x="30" y="40" class="lbl"><tspan fill="{PINK}">COMMIT LOG</tspan> · REAL GITHUB ACTIVITY</text>'
    b += f'<text x="30" y="76" class="serif" font-size="22" fill="{TEXT}">A year of building, <tspan font-style="italic" fill="{PINK2}">one square at a time.</tspan></text>'
    cards = [(f"{total:,}", "CONTRIBUTIONS"), (str(active), "ACTIVE DAYS"), (str(best), "LONGEST STREAK"), (str(busiest[1]), "BUSIEST DAY")]
    for i, (v, lab) in enumerate(cards):
        x = 510 + i * 90
        b += f'<text x="{x}" y="38" class="mono" font-size="7.5" letter-spacing="1" fill="{MUTED}">{lab}</text>'
        b += f'<text x="{x}" y="70" class="serif" font-size="26" fill="{TEXT}">{v}</text>'
    # grid
    x0, y0, s, g = 64, 118, 11, 3
    last_month = None
    for wi, week in enumerate(weeks):
        for date, c in week:
            d = dt.date.fromisoformat(date)
            wd = (d.isoweekday() % 7)
            col, op = fills[level(c, mx)]
            x, y = x0 + wi * (s + g), y0 + wd * (s + g)
            delay = wi * 0.025
            b += (f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="2.5" fill="{col}" fill-opacity="{op}">'
                  f'<title>{c} on {date}</title>'
                  f'<animate attributeName="opacity" from="0" to="1" dur=".4s" begin="{delay:.2f}s" fill="freeze"/></rect>')
            if wd == 0 or (week and date == week[0][0]):
                if d.month != last_month and d.day <= 7:
                    b += f'<text x="{x}" y="{y0-10}" class="mono" font-size="9" fill="{MUTED}">{d.strftime("%b")}</text>'
                    last_month = d.month
    for wd, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        b += f'<text x="30" y="{y0 + wd*(s+g) + 9}" class="mono" font-size="9" fill="{DIM}">{name}</text>'
    yb = y0 + 7 * (s + g) + 26
    b += f'<line x1="30" y1="{yb-14}" x2="850" y2="{yb-14}" stroke="{LINE}"/>'
    b += f'<text x="30" y="{yb+4}" class="lbl" font-size="9">LONGEST STREAK · {best} DAYS · {fmt(bs)} → {fmt(be)}</text>'
    lx = 740
    b += f'<text x="{lx-10}" y="{yb+4}" text-anchor="end" class="mono" font-size="9" fill="{DIM}">less</text>'
    for i, (col, op) in enumerate(fills):
        b += f'<rect x="{lx + i*15}" y="{yb-6}" width="11" height="11" rx="2.5" fill="{col}" fill-opacity="{op}"/>'
    b += f'<text x="{lx + 80}" y="{yb+4}" class="mono" font-size="9" fill="{DIM}">more</text>'
    return svg(W, H, b, f"{total} contributions in the last year")


def placeholder():
    W, H, u = 880, 300, "c"
    b = defs(W, H, u) + STYLE + frame(W, H, u)
    b += f'<text x="30" y="40" class="lbl"><tspan fill="{PINK}">COMMIT LOG</tspan> · REAL GITHUB ACTIVITY</text>'
    b += f'<text x="440" y="150" text-anchor="middle" class="serif" font-size="26" fill="{TEXT}">Syncing contributions<tspan fill="{PINK}" class="cursor">…</tspan></text>'
    b += f'<text x="440" y="182" text-anchor="middle" class="mono" font-size="10.5" fill="{MUTED}">Run the “Commit log” workflow once in the Actions tab to draw this card.</text>'
    return svg(W, H, b, "Commit log syncing")


if __name__ == "__main__":
    if "--placeholder" in sys.argv:
        OUT.write_text(placeholder(), encoding="utf-8"); print("wrote placeholder"); sys.exit()
    if "--demo" in sys.argv:
        weeks, login, out = demo(), "PADSviduranga", OUT.with_name("commit-log-demo.svg")
    else:
        login = sys.argv[1] if len(sys.argv) > 1 else os.environ["GITHUB_REPOSITORY_OWNER"]
        weeks, out = fetch(login, os.environ["GITHUB_TOKEN"]), OUT
    out.write_text(draw(weeks, login), encoding="utf-8")
    print("wrote", out)
