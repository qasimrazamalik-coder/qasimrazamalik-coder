"""Extra animated SVGs for the profile: game preview, stickers, terminal, divider.
All original artwork, pure SVG + CSS/SMIL (GitHub renders these inside <img>)."""
import math
import random
from html import escape

SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"
REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def x(s):
    return escape(str(s), quote=True)


def _open(W, H, t, title, css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{x(title)}">'
            f'<title>{x(title)}</title>'
            f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["bg1"]}"/><stop offset="1" stop-color="{t["bg2"]}"/></linearGradient>'
            f'<filter id="gl" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
            f'<style>text{{font-family:{SANS};fill:{t["text"]}}}{css}{REDUCED}</style>'
            f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18" fill="url(#bg)" stroke="{t["border"]}"/>')


# ----------------------------------------------------------------- game preview
def game_preview(d, t):
    """A self-playing loop of Contribution Breakout, bricks from real contribution data."""
    W, H, T = 1200, 300, 7.0
    cols, rows = 40, 7
    counts = [c for _, c in d["days"]][-cols * rows:]
    nz = sorted(c for c in counts if c > 0)
    def rank(c):
        if not c:
            return 0
        i = sum(1 for v in nz if v < c)
        return 1 + min(3, 4 * i // max(1, len(nz)))
    pal = ["#1e6f8f", "#14b8a6", t["a1"], t["a2"], t["a4"]]
    gx, gy, bw, bh, g = 120, 46, 21, 13, 3
    bricks = {}
    for i, c in enumerate(counts):
        col, row = i // 7, i % 7
        if c == 0 and (i * 7919) % 10 < 4:
            continue
        lvl = rank(c)
        bricks[(col, row)] = (gx + col * (bw + g), gy + row * (bh + g), pal[lvl])
    # ball path: alternating bounces between paddle and chosen bricks
    rnd = random.Random(4)
    targets = [k for k in sorted(bricks, key=lambda k: (k[1], k[0]), reverse=True)]
    picks, used = [], set()
    for frac in (0.12, 0.3, 0.52, 0.7, 0.88, 0.4):
        want = int(frac * cols)
        best = min((k for k in targets if k not in used), key=lambda k: abs(k[0] - want) + (6 - k[1]) * 0.6, default=None)
        if best:
            used.add(best)
            picks.append(best)
    paddle_y = H - 34
    pts, times, hits = [(W / 2, paddle_y - 8)], [0.0], []
    seg = T / (len(picks) * 2)
    tt = 0.0
    for k in picks:
        bx, by, _ = bricks[k]
        tt += seg
        pts.append((bx + bw / 2, by + bh + 5))
        times.append(tt)
        hits.append((k, tt))
        tt += seg
        px = 220 + rnd.random() * 760
        pts.append((px, paddle_y - 8))
        times.append(tt)
    pts[-1] = pts[0]
    kt = ";".join(f"{v / T:.4f}" for v in times)
    path = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    body = []
    hit_set = {k: tm for k, tm in hits}
    for k, (bx, by, col) in bricks.items():
        if k in hit_set:
            tm = hit_set[k] / T
            body.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="3" fill="{col}">'
                        f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" '
                        f'values="1;0;1" keyTimes="0;{tm:.4f};0.985"/></rect>')
            cx_, cy_ = bx + bw / 2, by + bh / 2
            for j in range(10):
                a = j / 10 * math.tau
                dx, dy = math.cos(a) * 34, math.sin(a) * 26
                body.append(f'<circle cx="{cx_}" cy="{cy_}" r="2.4" fill="{col}" opacity="0">'
                            f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" values="0;0;1;0;0" keyTimes="0;{tm:.4f};{tm + .005:.4f};{min(tm + .09, .98):.4f};1"/>'
                            f'<animateTransform attributeName="transform" type="translate" dur="{T}s" repeatCount="indefinite" values="0 0;0 0;{dx:.1f} {dy:.1f};{dx:.1f} {dy:.1f}" keyTimes="0;{tm:.4f};{min(tm + .09, .98):.4f};1"/></circle>')
            body.append(f'<circle cx="{cx_}" cy="{cy_}" r="4" fill="none" stroke="{col}" stroke-width="2" opacity="0">'
                        f'<animate attributeName="r" dur="{T}s" repeatCount="indefinite" values="4;4;30;30" keyTimes="0;{tm:.4f};{min(tm + .08, .98):.4f};1"/>'
                        f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" values="0;0;1;0;0" keyTimes="0;{tm:.4f};{tm + .004:.4f};{min(tm + .08, .98):.4f};1"/></circle>')
        else:
            body.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="3" fill="{col}" opacity=".9"/>')
    # paddle follows the bottom touch points
    pxs = []
    for (a, b), tm in zip(pts, times):
        pxs.append(a - 65)
    pv = ";".join(f"{v:.1f}" for v in pxs)
    css = (f".lbl{{font:800 15px {MONO};fill:{t['text']}}}.cta{{animation:pul 1.6s ease-in-out infinite}}"
           f"@keyframes pul{{50%{{opacity:.55}}}}")
    svg = _open(W, H, t, "Contribution Breakout: a playable arcade game built from Qasim Raza Malik's GitHub contributions", css)
    svg += f'<path id="bp" d="{path}" fill="none"/>'
    svg += "".join(body)
    svg += (f'<rect y="{paddle_y}" width="130" height="10" rx="5" fill="{t["a1"]}" filter="url(#gl)">'
            f'<animate attributeName="x" dur="{T}s" repeatCount="indefinite" values="{pv}" keyTimes="{kt}"/></rect>')
    for k, op in ((0, 1), (1, .5), (2, .25)):
        svg += (f'<circle r="{7 - k}" fill="{"#ffffff" if t["bg1"].startswith("#07") else t["a2"]}" opacity="{op}" filter="url(#gl)">'
                f'<animateMotion dur="{T}s" repeatCount="indefinite" begin="-{k * .04:.2f}s" keyPoints="{";".join(f"{i / (len(pts) - 1):.4f}" for i in range(len(pts)))}" keyTimes="{kt}" calcMode="linear"><mpath href="#bp"/></animateMotion></circle>')
    svg += (f'<text class="lbl" x="28" y="30">CONTRIBUTION BREAKOUT</text>'
            f'<text x="{W - 28}" y="30" text-anchor="end" style="font:600 13px {MONO};fill:{t["muted"]}">bricks = my real commits · sound on</text>'
            f'<g class="cta"><rect x="{W / 2 - 120}" y="{H / 2 + 10}" width="240" height="44" rx="12" fill="{t["a2"]}" opacity=".18" stroke="{t["a2"]}"/>'
            f'<text x="{W / 2}" y="{H / 2 + 39}" text-anchor="middle" style="font:800 18px {SANS}">▶ CLICK TO PLAY</text></g></svg>')
    return svg


# ----------------------------------------------------------------- stickers
def _sticker(t, title, inner, css=""):
    W = H = 220
    return _open(W, H, t, title, css) + inner + "</svg>"


def sticker_rocket(t):
    css = (".rk{animation:fly 3s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
           "@keyframes fly{0%,100%{transform:translateY(6px)}50%{transform:translateY(-10px)}}"
           ".fl{animation:fl .14s steps(2) infinite;transform-box:fill-box;transform-origin:top center}"
           "@keyframes fl{50%{transform:scaleY(.6)}}"
           ".st{animation:st 1.2s linear infinite}@keyframes st{from{transform:translateY(-40px)}to{transform:translateY(240px)}}")
    stars = "".join(f'<circle class="st" cx="{25 + i * 23 % 170}" cy="{(i * 47) % 220}" r="{1 + i % 2}" fill="{t["muted"]}" style="animation-delay:-{i * .17:.2f}s"/>' for i in range(10))
    rk = (f'<g class="rk"><path d="M110 40 C130 60 134 100 128 132 L92 132 C86 100 90 60 110 40Z" fill="{t["text"]}"/>'
          f'<circle cx="110" cy="84" r="11" fill="{t["a1"]}" stroke="{t["bg1"]}" stroke-width="4"/>'
          f'<path d="M92 112 L72 140 L94 134Z" fill="{t["a2"]}"/><path d="M128 112 L148 140 L126 134Z" fill="{t["a2"]}"/>'
          f'<g class="fl"><path d="M96 132 L110 178 L124 132Z" fill="#fb923c"/><path d="M102 132 L110 160 L118 132Z" fill="#fde68a"/></g></g>')
    lbl = f'<text x="110" y="205" text-anchor="middle" style="font:700 13px {MONO};fill:{t["muted"]}">shipping</text>'
    return _sticker(t, "Animated rocket sticker: shipping", stars + rk + lbl, css)


def sticker_robot(t):
    css = (".eye{animation:bl 3.4s infinite;transform-box:fill-box;transform-origin:center}"
           "@keyframes bl{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.1)}}"
           ".ant{animation:an 1s ease-in-out infinite alternate}@keyframes an{to{opacity:.25}}"
           ".hd{animation:tilt 4s ease-in-out infinite;transform-box:fill-box;transform-origin:center bottom}"
           "@keyframes tilt{0%,100%{transform:rotate(-5deg)}50%{transform:rotate(5deg)}}")
    inner = (f'<g class="hd"><line x1="110" y1="38" x2="110" y2="58" stroke="{t["muted"]}" stroke-width="4"/>'
             f'<circle class="ant" cx="110" cy="34" r="7" fill="{t["a4"]}" filter="url(#gl)"/>'
             f'<rect x="58" y="58" width="104" height="84" rx="22" fill="{t["node"]}" stroke="{t["a2"]}" stroke-width="3"/>'
             f'<ellipse class="eye" cx="88" cy="96" rx="10" ry="12" fill="{t["a1"]}" filter="url(#gl)"/>'
             f'<ellipse class="eye" cx="132" cy="96" rx="10" ry="12" fill="{t["a1"]}" filter="url(#gl)"/>'
             f'<path d="M92 122 Q110 134 128 122" stroke="{t["a3"]}" stroke-width="4" fill="none" stroke-linecap="round"/>'
             f'<rect x="48" y="86" width="10" height="24" rx="4" fill="{t["a2"]}"/><rect x="162" y="86" width="10" height="24" rx="4" fill="{t["a2"]}"/></g>'
             f'<text x="110" y="180" text-anchor="middle" style="font:700 13px {MONO};fill:{t["muted"]}">training models</text>')
    return _sticker(t, "Animated robot sticker: AI and machine learning", inner, css)


def sticker_chai(t):
    css = (".sm{animation:sm 2.4s ease-in-out infinite;transform-box:fill-box;transform-origin:bottom}"
           "@keyframes sm{0%{opacity:0;transform:translateY(10px) scaleY(.8)}40%{opacity:.9}100%{opacity:0;transform:translateY(-26px) scaleY(1.2)}}")
    smoke = "".join(f'<path class="sm" style="animation-delay:{i * .8:.1f}s" d="M{86 + i * 20} 92 q-10 -14 0 -28 q10 -14 0 -28" stroke="{t["muted"]}" stroke-width="4" fill="none" stroke-linecap="round"/>' for i in range(3))
    cup = (f'<path d="M62 100 H150 V140 Q150 172 106 172 Q62 172 62 140Z" fill="{t["a4"]}"/>'
           f'<path d="M150 112 Q176 112 176 132 Q176 150 150 150" stroke="{t["a4"]}" stroke-width="8" fill="none"/>'
           f'<rect x="62" y="100" width="88" height="10" fill="#fde68a" opacity=".8"/>'
           f'<text x="110" y="205" text-anchor="middle" style="font:700 13px {MONO};fill:{t["muted"]}">chai → code</text>')
    return _sticker(t, "Animated chai cup sticker: chai into code", smoke + cup, css)


def sticker_radar(t):
    css = (".sw{animation:rot 2.6s linear infinite;transform-origin:110px 100px}@keyframes rot{to{transform:rotate(360deg)}}"
           ".bl{animation:bp 2.6s ease-out infinite}@keyframes bp{0%,30%{opacity:0}35%{opacity:1}100%{opacity:0}}")
    inner = "".join(f'<circle cx="110" cy="100" r="{r}" fill="none" stroke="{t["a3"]}" stroke-opacity=".35"/>' for r in (24, 48, 72))
    inner += (f'<g class="sw"><path d="M110 100 L182 100 A72 72 0 0 0 161 49Z" fill="{t["a3"]}" opacity=".35"/>'
              f'<line x1="110" y1="100" x2="182" y2="100" stroke="{t["a3"]}" stroke-width="2"/></g>'
              f'<circle class="bl" cx="150" cy="62" r="6" fill="{t["a3"]}" filter="url(#gl)"/>'
              f'<circle class="bl" cx="76" cy="130" r="5" fill="{t["a3"]}" filter="url(#gl)" style="animation-delay:1.1s"/>'
              f'<text x="110" y="205" text-anchor="middle" style="font:700 13px {MONO};fill:{t["a3"]}">open to work</text>')
    return _sticker(t, "Animated radar sticker: open to work", inner, css)


# ----------------------------------------------------------------- terminal
def terminal(p, t):
    W, H = 1200, 250
    lines = [("$", "whoami", t["a3"]),
             ("›", f'{p["name"]} · Abbottabad, Pakistan', t["text"]),
             ("$", "ls ~/projects --latest | head -3", t["a3"]),
             ("›", "voice-cloner      free Urdu + English voice cloning on Colab", t["text"]),
             ("›", "encore-booking    seat-booking API that never double-sells", t["text"]),
             ("›", "motion-forge      AI motion graphics that check their own frames", t["text"])]
    css = (f".ln{{font:500 16px {MONO};white-space:pre}}.cur{{animation:bk 1s steps(1) infinite}}@keyframes bk{{50%{{opacity:0}}}}"
           "@keyframes ty{from{clip-path:inset(-20% 100% -20% 0)}to{clip-path:inset(-20% 0 -20% 0)}}")
    out = _open(W, H, t, "Terminal card: what Qasim Raza Malik is building now", css)
    out += (f'<rect x=".5" y=".5" width="{W - 1}" height="34" rx="18" fill="{t["node"]}"/>'
            f'<rect x=".5" y="18" width="{W - 1}" height="17" fill="{t["node"]}"/>'
            + "".join(f'<circle cx="{26 + i * 20}" cy="17" r="6" fill="{c}"/>' for i, c in enumerate(("#f87171", "#fbbf24", "#34d399")))
            + f'<text x="{W / 2}" y="22" text-anchor="middle" style="font:600 13px {MONO};fill:{t["muted"]}">~/now-building</text>')
    delay = .3
    for i, (pr, txt, col) in enumerate(lines):
        y = 70 + i * 30
        n = len(txt)
        dur = max(.5, n * .03)
        out += (f'<text class="ln" x="30" y="{y}" style="fill:{t["a2"]}">{x(pr)}</text>'
                f'<text class="ln" x="54" y="{y}" style="fill:{col};animation:ty {dur:.2f}s {delay:.2f}s steps({n},end) both">{x(txt)}</text>')
        delay += dur + .25
    out += f'<rect class="cur" x="54" y="{70 + len(lines) * 30 - 15}" width="10" height="18" fill="{t["a1"]}"/></svg>'
    return out


# ----------------------------------------------------------------- divider
def divider(t):
    W, H = 1200, 36
    css = ".wv{animation:wv 6s linear infinite}@keyframes wv{to{transform:translateX(-200px)}}"
    pts = " ".join(f"L{i * 10},{18 + math.sin(i / 20 * math.tau) * 8:.1f}" for i in range(0, 161))
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="section divider">'
           f'<defs><linearGradient id="lg" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1200" y2="0"><stop offset="0" stop-color="{t["a1"]}" stop-opacity="0"/><stop offset=".2" stop-color="{t["a1"]}"/>'
           f'<stop offset=".5" stop-color="{t["a2"]}"/><stop offset=".8" stop-color="{t["a4"]}"/><stop offset="1" stop-color="{t["a4"]}" stop-opacity="0"/></linearGradient></defs>'
           f'<style>{css}{REDUCED}</style>'
           f'<g class="wv"><path d="M0,18 {pts}" fill="none" stroke="url(#lg)" stroke-width="2.5"/></g></svg>')
    return out
