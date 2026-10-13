#!/usr/bin/env python3
"""Builds the GitHub profile: animated SVGs (hero, stats, languages, activity)
in dark and light themes, plus README.md, from profile.json and live GitHub data.

Usage:
  python scripts/build.py            # live data (needs GITHUB_TOKEN)
  python scripts/build.py --sample   # offline preview with sample data
No third-party packages needed.
"""
import datetime as dt
import json
import os
import sys
import urllib.request

import fx
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "generated"
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Helvetica, Arial, sans-serif"
SERIF = "'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"

THEMES = {
    "dark": dict(bg1="#0f0e0c", bg2="#14120f", border="#2a261f", text="#ede6d6", muted="#8f8676",
                 a1="#f2a03d", a2="#e2553b", a3="#8fae7a", a4="#c9b48f", grid="#ede6d6", grid_o="0.05",
                 node="#17150f", chip="#17150f", empty="#211e18"),
    "light": dict(bg1="#f5f0e6", bg2="#efe8da", border="#ddd3c1", text="#1c1a16", muted="#6b6457",
                  a1="#b86a12", a2="#b33a22", a3="#4d7a3f", a4="#8a6a3e", grid="#1c1a16", grid_o="0.06",
                  node="#fbf8f1", chip="#fbf8f1", empty="#e6dfd0"),
}

REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def x(s):
    return escape(str(s), quote=True)


# --------------------------------------------------------------------------- hero
def hero(p, t):
    W, H = 1200, 420
    roles = p["roles"]
    n = len(roles)
    cyc = 4 * n
    role_css, role_svg = [], []
    for i, r in enumerate(roles):
        role_css.append(f".r{i}{{animation:type {cyc}s {i*4}s infinite both}}")
        role_svg.append(f'<text class="role r{i}" x="84" y="214">{x(r)}</text>')
    # typing keyframes expressed as a fraction of one role window (4s of cyc)
    w = 100 / n
    kf = (f"@keyframes type{{0%{{clip-path:inset(-20% 100% -20% 0);opacity:1;animation-timing-function:steps(22,end)}}"
          f"{w*0.32:.2f}%{{clip-path:inset(-20% 0 -20% 0);opacity:1}}"
          f"{w*0.80:.2f}%{{clip-path:inset(-20% 0 -20% 0);opacity:1;animation-timing-function:steps(14,end)}}"
          f"{w*0.97:.2f}%{{clip-path:inset(-20% 100% -20% 0);opacity:1}}"
          f"{w:.2f}%,100%{{clip-path:inset(-20% 100% -20% 0);opacity:0}}}}")

    chips, cx = [], 56
    for i, c in enumerate(p["chips"]):
        cw = int(len(c) * 7.6 + 30)
        if cx + cw > 660:
            break
        chips.append(
            f'<g class="chip" style="animation-delay:{1.2 + i*0.12:.2f}s">'
            f'<rect x="{cx}" y="300" width="{cw}" height="30" rx="15" fill="{t["chip"]}" stroke="{t["border"]}"/>'
            f'<circle cx="{cx+14}" cy="315" r="3.5" fill="{[t["a1"], t["a2"], t["a3"], t["a4"]][i % 4]}"/>'
            f'<text x="{cx+24}" y="320" class="chipt">{x(c)}</text></g>')
        cx += cw + 10

    # data flywheel: 4 nodes around a hub
    nodes = [(760, 92, "Interface", "React · TS · UI", t["a1"]),
             (968, 92, "API", "Node · Express", t["a2"]),
             (968, 262, "Data", "SQL · dashboards", t["a3"]),
             (760, 262, "AI", "Python · voice", t["a4"])]
    NW, NH = 168, 58
    centers = [(nx + NW / 2, ny + NH / 2) for nx, ny, *_ in nodes]
    paths = []
    for i in range(4):
        (x1, y1), (x2, y2) = centers[i], centers[(i + 1) % 4]
        if i == 0:
            d = f"M{x1+NW/2-4},{y1} L{x2-NW/2+4},{y2}"
        elif i == 1:
            d = f"M{x1},{y1+NH/2-2} L{x2},{y2-NH/2+2}"
        elif i == 2:
            d = f"M{x1-NW/2+4},{y1} L{x2+NW/2-4},{y2}"
        else:
            d = f"M{x1},{y1-NH/2+2} L{x2},{y2+NH/2-2}"
        paths.append(d)
    hubx, huby = (centers[0][0] + centers[1][0]) / 2, (centers[0][1] + centers[2][1]) / 2
    spokes = [f"M{cx_},{cy_} L{hubx},{huby}" for cx_, cy_ in centers]

    flow = []
    for i, d in enumerate(paths):
        flow.append(f'<path id="p{i}" d="{d}" class="wire"/>')
        flow.append(f'<path d="{d}" class="wire-glow" stroke="{nodes[i][4]}"/>')
        for k in range(3):
            flow.append(f'<circle r="3.2" fill="{nodes[i][4]}" filter="url(#glow)">'
                        f'<animateMotion dur="2.4s" begin="{k*0.8 + i*0.3:.1f}s" repeatCount="indefinite">'
                        f'<mpath href="#p{i}"/></animateMotion></circle>')
    for i, d in enumerate(spokes):
        flow.append(f'<path id="s{i}" d="{d}" class="spoke"/>')
        flow.append(f'<circle r="2.4" fill="{nodes[i][4]}" opacity=".9">'
                    f'<animateMotion dur="3.2s" begin="{i*0.8:.1f}s" repeatCount="indefinite" keyPoints="0;1" keyTimes="0;1">'
                    f'<mpath href="#s{i}"/></animateMotion></circle>')
    boxes = []
    for i, (nx, ny, title, sub, col) in enumerate(nodes):
        boxes.append(
            f'<g class="node" style="animation-delay:{0.5 + i*0.15:.2f}s">'
            f'<rect x="{nx}" y="{ny}" width="{NW}" height="{NH}" rx="14" fill="{t["node"]}" stroke="{col}" stroke-opacity=".55"/>'
            f'<rect x="{nx+12}" y="{ny+17}" width="24" height="24" rx="7" fill="{col}" fill-opacity=".16"/>'
            f'<circle cx="{nx+24}" cy="{ny+29}" r="5" fill="{col}"><animate attributeName="r" values="4;6;4" dur="2s" begin="{i*0.5}s" repeatCount="indefinite"/></circle>'
            f'<text x="{nx+46}" y="{ny+26}" class="nt">{x(title)}</text>'
            f'<text x="{nx+46}" y="{ny+44}" class="ns">{x(sub)}</text></g>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="ttl dsc">
<title id="ttl">{x(p["name"])}: {x(p["headline"])}</title>
<desc id="dsc">{x(p["tagline"])} Skills: {x(", ".join(p["chips"]))}.</desc>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["bg1"]}"/><stop offset="1" stop-color="{t["bg2"]}"/></linearGradient>
<linearGradient id="name" x1="0" x2="1"><stop offset="0" stop-color="{t["a1"]}"/><stop offset=".5" stop-color="{t["a2"]}"/><stop offset="1" stop-color="{t["a4"]}"/>
<animateTransform attributeName="gradientTransform" type="translate" values="-0.4 0;0.4 0;-0.4 0" dur="8s" repeatCount="indefinite"/></linearGradient>
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="{t["grid"]}" stroke-opacity="{t["grid_o"]}"/></pattern>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="70"/></filter>
<filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<style>
text{{font-family:{SANS}}}
.mono{{font-family:{MONO}}}
.prompt{{font:500 15px {MONO};fill:{t["a3"]};animation:type1 1.6s .1s steps(32,end) both}}
@keyframes type1{{from{{clip-path:inset(-20% 100% -20% 0)}}to{{clip-path:inset(-20% 0 -20% 0)}}}}
.name{{font:700 60px {SERIF};fill:{t["text"]};letter-spacing:-1px;animation:up .9s .35s cubic-bezier(.2,.8,.2,1) both}}
.role{{font:600 25px {MONO};fill:{t["text"]}}}
.caret{{font:600 25px {MONO};fill:{t["a1"]};animation:blink 1s steps(1) infinite}}
.tag{{font:400 17.5px {SANS};fill:{t["muted"]};animation:up .9s .8s cubic-bezier(.2,.8,.2,1) both}}
.chip{{animation:pop .5s cubic-bezier(.2,1.4,.4,1) both;transform-box:fill-box;transform-origin:center}}
.chipt{{font:600 13px {SANS};fill:{t["text"]}}}
.status{{font:600 13px {SANS};fill:{t["a3"]}}}
.node{{animation:pop .6s cubic-bezier(.2,1.3,.4,1) both;transform-box:fill-box;transform-origin:center}}
.nt{{font:700 15px {SANS};fill:{t["text"]}}}
.ns{{font:500 11.5px {MONO};fill:{t["muted"]}}}
.wire{{fill:none;stroke:{t["muted"]};stroke-opacity:.35;stroke-width:1.5;stroke-dasharray:5 6;animation:dash 1.2s linear infinite}}
.wire-glow{{fill:none;stroke-width:2;stroke-opacity:.0}}
.spoke{{fill:none;stroke:{t["muted"]};stroke-opacity:.18;stroke-width:1}}
.blob{{animation:drift 14s ease-in-out infinite alternate}}
.ring{{fill:none;stroke:{t["a2"]};stroke-width:2;transform-box:fill-box;transform-origin:center;animation:ring 2.4s ease-out infinite}}
@keyframes dash{{to{{stroke-dashoffset:-11}}}}
@keyframes up{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
@keyframes pop{{from{{opacity:0;transform:scale(.6)}}to{{opacity:1;transform:none}}}}
@keyframes blink{{50%{{opacity:0}}}}
@keyframes drift{{from{{transform:translate(0,0)}}to{{transform:translate(60px,30px)}}}}
@keyframes ring{{from{{transform:scale(.6);opacity:.9}}to{{transform:scale(2.2);opacity:0}}}}
{kf}
{"".join(role_css)}
{REDUCED}
@media (prefers-reduced-motion: reduce){{.r0{{clip-path:none;opacity:1}}}}
</style>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#grid)"/>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="22" fill="none" stroke="{t["border"]}"/>
<text class="prompt" x="56" y="78">~/{x(p["login"])} $ whoami</text>
<text class="name" x="54" y="150">{x(p["name"])}</text>
<rect x="56" y="166" width="0" height="3" fill="{t["a1"]}"><animate attributeName="width" from="0" to="96" dur=".9s" begin=".6s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/></rect>
<text class="caret" x="56" y="214">&gt;</text>
{"".join(role_svg)}
<text class="tag" x="56" y="262">{x(p.get("hero_tagline", p["tagline"]))}</text>
{"".join(chips)}
<g style="animation:up .8s 2s both"><circle cx="62" cy="370" r="5" fill="{t["a3"]}"/><circle cx="62" cy="370" r="5" class="ring" style="stroke:{t["a3"]}"/>
<text class="status" x="76" y="375">{x(p["status"])}  ·  {x(p["location"])}</text></g>
{"".join(flow)}
<circle cx="{hubx}" cy="{huby}" r="20" class="ring"/>
<circle cx="{hubx}" cy="{huby}" r="20" fill="{t["node"]}" stroke="{t["a2"]}" stroke-width="2"/>
<text x="{hubx}" y="{huby+5}" text-anchor="middle" class="nt" style="font-size:13px">ship</text>
{"".join(boxes)}
<text x="{(centers[0][0]+centers[1][0])/2}" y="{H-28}" text-anchor="middle" class="ns">UI → API → data → AI, shipped end to end</text>
</svg>'''
    return svg


# --------------------------------------------------------------------------- data
QUERY = """query($login:String!){user(login:$login){
 name followers{totalCount}
 repositories(ownerAffiliations:OWNER,privacy:PUBLIC,isFork:false,first:100){totalCount nodes{stargazerCount
   languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name color}}}}}
 contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{contributionCount date}}}}
}}"""


def fetch(login):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set (use --sample for an offline preview)")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-builder"})
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.load(r)
    if "errors" in res:
        sys.exit(f"GitHub API error: {res['errors']}")
    u = res["data"]["user"]
    langs = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            n = e["node"]["name"]
            langs.setdefault(n, [0, e["node"]["color"] or "#8b949e"])
            langs[n][0] += e["size"]
    days = [d for w in u["contributionsCollection"]["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    return dict(repos=u["repositories"]["totalCount"],
                stars=sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
                followers=u["followers"]["totalCount"],
                total=u["contributionsCollection"]["contributionCalendar"]["totalContributions"],
                langs=langs, days=[(d["date"], d["contributionCount"]) for d in days])


def sample():
    import random
    random.seed(7)
    start = dt.date.today() - dt.timedelta(days=364)
    days = []
    for i in range(365):
        d = start + dt.timedelta(days=i)
        base = 0 if random.random() < 0.35 else random.randint(1, 9)
        days.append((d.isoformat(), base))
    return dict(repos=49, stars=12, followers=1, total=sum(c for _, c in days),
                langs={"TypeScript": [52000, "#3178c6"], "Python": [41000, "#3572A5"], "Go": [18000, "#00ADD8"],
                       "C++": [16000, "#f34b7d"], "JavaScript": [12000, "#f1e05a"], "HTML": [6000, "#e34c26"]},
                days=days)


def streaks(days):
    counts = [c for _, c in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    cur, i = 0, len(counts) - 1
    if i >= 0 and counts[i] == 0:
        i -= 1  # today may not have activity yet
    while i >= 0 and counts[i]:
        cur += 1
        i -= 1
    return cur, longest


def frame(W, H, t, body, title, extra_css=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{x(title)}">
<title>{x(title)}</title>
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["bg1"]}"/><stop offset="1" stop-color="{t["bg2"]}"/></linearGradient></defs>
<style>
text{{font-family:{SANS};fill:{t["text"]}}}
.h{{font:700 17px {SANS}}}
.m{{font:500 12.5px {SANS};fill:{t["muted"]}}}
.v{{font:800 28px {SANS}}}
.in{{animation:up .7s cubic-bezier(.2,.8,.2,1) both}}
@keyframes up{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
{extra_css}
{REDUCED}
</style>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="url(#bg)" stroke="{t["border"]}"/>
{body}
</svg>'''


def stats_card(d, t):
    W, H = 590, 210
    cur, longest = streaks(d["days"])
    items = [("Contributions · 12 mo", d["total"], t["a1"]), ("Public repos", d["repos"], t["a2"]),
             ("Current streak", f'{cur}d', t["a3"]), ("Longest streak", f'{longest}d', t["a4"]),
             ("Stars earned", d["stars"], t["a1"]), ("Followers", d["followers"], t["a2"])]
    body = [f'<text class="h in" x="28" y="40">GitHub at a glance</text>',
            f'<text class="m in" x="{W-28}" y="40" text-anchor="end">updated {dt.date.today():%d %b %Y}</text>']
    for i, (label, val, col) in enumerate(items):
        cx, cy = 28 + (i % 3) * 186, 80 + (i // 3) * 64
        body.append(f'<g class="in" style="animation-delay:{0.15 + i*0.1:.2f}s">'
                    f'<rect x="{cx}" y="{cy}" width="4" height="44" rx="2" fill="{col}"/>'
                    f'<text class="v" x="{cx+16}" y="{cy+28}">{x(val)}</text>'
                    f'<text class="m" x="{cx+16}" y="{cy+46}">{x(label)}</text></g>')
    return frame(W, H, t, "".join(body), "GitHub stats for Qasim Raza Malik")


def langs_card(d, t):
    W, H = 590, 210
    items = sorted(d["langs"].items(), key=lambda kv: -kv[1][0])[:6]
    total = sum(v[0] for _, v in items) or 1
    body = ['<text class="h in" x="28" y="40">Languages I ship in</text>']
    # stacked bar
    bx, bw = 28, W - 56
    acc = 0
    for i, (n, (sz, col)) in enumerate(items):
        w = bw * sz / total
        body.append(f'<rect x="{bx+acc:.1f}" y="58" width="{max(w-2,1):.1f}" height="12" rx="3" fill="{col}" class="grow" style="animation-delay:{0.2+i*0.12:.2f}s"/>')
        acc += w
    for i, (n, (sz, col)) in enumerate(items):
        cx, cy = 28 + (i % 2) * 280, 104 + (i // 2) * 36
        pct = 100 * sz / total
        body.append(f'<g class="in" style="animation-delay:{0.4+i*0.08:.2f}s"><circle cx="{cx+6}" cy="{cy-5}" r="6" fill="{col}"/>'
                    f'<text x="{cx+20}" y="{cy}" style="font:600 14px {SANS}">{x(n)}</text>'
                    f'<text class="m" x="{cx+250}" y="{cy}" text-anchor="end">{pct:.1f}%</text></g>')
    css = ".grow{animation:grow .9s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box;transform-origin:left}@keyframes grow{from{transform:scaleX(0)}to{transform:none}}"
    return frame(W, H, t, "".join(body), "Top languages by code size", css)


def activity_card(d, t):
    days = d["days"][-364:]
    W, H = 1200, 250
    cell, gap, x0, y0 = 17, 4, 40, 72
    mx = max([c for _, c in days] + [1])
    levels = [t["empty"]] + [t["a1"]] * 4
    first = dt.date.fromisoformat(days[0][0])
    offset = (first.weekday() + 1) % 7  # Sunday-first rows like GitHub
    body = [f'<text class="h in" x="40" y="42">{d["total"]} contributions in the last year</text>',
            '<text class="m in" x="1160" y="42" text-anchor="end">every square is a day</text>']
    months = {}
    for i, (ds, c) in enumerate(days):
        k = i + offset
        col, row = k // 7, k % 7
        lvl = 0 if c == 0 else 1 + min(3, int(4 * c / (mx + 1)))
        op = [1, .35, .55, .78, 1][lvl]
        px, py = x0 + col * (cell + gap), y0 + row * (cell + gap)
        delay = 0.15 + col * 0.018 + row * 0.01
        body.append(f'<rect x="{px}" y="{py}" width="{cell}" height="{cell}" rx="3.5" fill="{levels[lvl]}" fill-opacity="{op}" '
                    f'class="c" style="animation-delay:{delay:.2f}s"><title>{ds}: {c}</title></rect>')
        dd = dt.date.fromisoformat(ds)
        if dd.day <= 7 and row == 0 and dd.strftime("%b") not in months:
            months[dd.strftime("%b")] = px
    for m, px in months.items():
        body.append(f'<text class="m" x="{px}" y="{y0-10}">{m}</text>')
    css = (".c{animation:pop .5s cubic-bezier(.2,1.4,.4,1) both;transform-box:fill-box;transform-origin:center}"
           "@keyframes pop{from{opacity:0;transform:scale(.2)}to{opacity:1;transform:none}}")
    return frame(W, H, t, "".join(body), f'{d["total"]} GitHub contributions in the last year', css)


# --------------------------------------------------------------------------- readme
def pic(name, alt, width=None):
    w = f' width="{width}"' if width else ""
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/generated/{name}-dark.svg"/>'
            f'<source media="(prefers-color-scheme: light)" srcset="assets/generated/{name}-light.svg"/>'
            f'<img alt="{x(alt)}" src="assets/generated/{name}-dark.svg"{w}/></picture>')


def badge(label, msg, color, logo, url):
    from urllib.parse import quote
    src = f"https://img.shields.io/badge/{quote(label)}-{quote(msg.replace('-', '--'))}-{color}?style=for-the-badge&logo={logo}&logoColor=white"
    return f'<a href="{url}"><img alt="{x(label)}: {x(msg)}" src="{src}"/></a>'


def readme(p):
    L, login = p["links"], p["login"]
    badges = []
    if L.get("linkedin"):
        badges.append(badge("LinkedIn", p["name"], "2a261f", "linkedin", L["linkedin"]))
    if L.get("website"):
        badges.append(badge("Website", L["website"].split("//")[-1], "b86a12", "googlechrome", L["website"]))
    if L.get("email"):
        badges.append(badge("Email", "Say hello", "2a261f", "gmail", f"mailto:{L['email']}"))
    rows = []
    for pr in p["projects"]:
        nm = f'[**{pr["name"]}**](https://github.com/{login}/{pr["repo"]})' if pr["repo"] else f'**{pr["name"]}**'
        rows.append(f'| {nm} | {pr["desc"]} | {pr["stack"]} |')
    focus = "\n".join(f"- **{a}:** {b}" for a, b in p["focus"])
    tools = " · ".join(f"`{t}`" for t in p["toolbox"])
    game_url = f"https://{login}.github.io/{login}/game/"
    div = pic("divider", "")
    stick = " ".join(pic(f"sticker-{s}", a, "23%") for s, a in (("rocket", "Rocket sticker: shipping"), ("robot", "Robot sticker: training AI models"), ("chai", "Chai sticker: chai into code"), ("radar", "Radar sticker: open to work")))
    return f'''<!-- Generated by scripts/build.py from profile.json. Edit profile.json, not this file. -->
<p align="center">
  {pic("hero", f'{p["name"]}: {p["headline"]}. {p["tagline"]}')}
</p>

<h1 align="center">{p["name"]}</h1>
<p align="center"><b>{p["headline"]}</b><br/>{p["location"]} · {p["status"]}</p>

<p align="center">
  {" ".join(badges)}
</p>

<p align="center">{stick}</p>

<p align="center">{div}</p>

## About me

{" ".join(p["about"])}

<p align="center">
  {pic("terminal", "Terminal card listing what Qasim Raza Malik is building now")}
</p>

## What I work on

{focus}

## Featured projects

| Project | What it does | Built with |
|---|---|---|
{chr(10).join(rows)}

<p align="center">{div}</p>

## Play my contribution graph

Every brick in this arcade game is a real day from my GitHub contribution graph. Busier days are brighter and take more hits. It has particles, combos, power-ups and synthesized sound effects, and runs in the browser with no libraries.

<p align="center">
  <a href="{game_url}">{pic("game", "Contribution Breakout, a playable arcade game built from Qasim Raza Malik's GitHub contributions. Click to play.")}</a>
</p>
<p align="center"><a href="{game_url}"><b>▶ Play Contribution Breakout</b></a> (sound on 🔊)</p>

<p align="center">{div}</p>

## GitHub at a glance

<p align="center">
  {pic("stats", f"GitHub stats for {p['name']}", "49%")}
  {pic("langs", f"Top programming languages used by {p['name']}", "49%")}
</p>
<p align="center">
  {pic("activity", f"{p['name']} GitHub contribution activity over the last year")}
</p>
<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/{login}/{login}/output/snake-dark.svg"/>
  <img alt="Animation of a snake eating {p['name']}'s GitHub contribution graph" src="https://raw.githubusercontent.com/{login}/{login}/output/snake.svg"/></picture>
</p>

## Toolbox

{tools}

## Let's work together

Hiring an **AI & Backend Engineer**, or need an AI feature, API, data pipeline or full-stack app built? {"Email me at **" + L["email"] + "**" if L.get("email") else "Reach out"}{" or message me on [LinkedIn](" + L["linkedin"] + ")" if L.get("linkedin") else ""}.

<sub>Cards on this page are drawn by my own GitHub Action from live GitHub data, refreshed daily. No third-party stats services.</sub>
'''


def main():
    p = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
    d = sample() if "--sample" in sys.argv else fetch(p["login"])
    OUT.mkdir(parents=True, exist_ok=True)
    for name, t in THEMES.items():
        (OUT / f"hero-{name}.svg").write_text(hero(p, t), encoding="utf-8")
        (OUT / f"stats-{name}.svg").write_text(stats_card(d, t), encoding="utf-8")
        (OUT / f"langs-{name}.svg").write_text(langs_card(d, t), encoding="utf-8")
        (OUT / f"activity-{name}.svg").write_text(activity_card(d, t), encoding="utf-8")
        (OUT / f"game-{name}.svg").write_text(fx.game_preview(d, t), encoding="utf-8")
        (OUT / f"terminal-{name}.svg").write_text(fx.terminal(p, t), encoding="utf-8")
        (OUT / f"divider-{name}.svg").write_text(fx.divider(t), encoding="utf-8")
        for st in ("rocket", "robot", "chai", "radar"):
            (OUT / f"sticker-{st}-{name}.svg").write_text(getattr(fx, f"sticker_{st}")(t), encoding="utf-8")
    game = ROOT / "game"
    game.mkdir(exist_ok=True)
    (game / "data.json").write_text(json.dumps({"login": p["login"], "updated": dt.date.today().isoformat(),
                                                "days": [c for _, c in d["days"]][-364:]}), encoding="utf-8")
    (ROOT / "README.md").write_text(readme(p), encoding="utf-8")
    print("built", sorted(f.name for f in OUT.iterdir()))


if __name__ == "__main__":
    main()
