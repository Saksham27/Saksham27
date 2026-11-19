#!/usr/bin/env python3
"""Renders branded stats SVGs (activity heatmap + language bar) for the profile README.
Runs daily in GitHub Actions. Usage: GITHUB_TOKEN=... python3 stats.py <user> <out_dir>
With STATS_FAKE=1 it renders sample data (for local design checks)."""
import base64, io, json, os, sys, random, datetime as dt, urllib.request, html
from fontTools.ttLib import TTFont
from fontTools import subset

INK, CREAM, OR, LI, VI, MUTED = '#0b0b0d', '#f1ede4', '#ff4f2b', '#c8f53a', '#7b5cff', '#8b8984'
HEAT = ['#17171b', '#4a1d14', '#8a2c18', '#d23d1f', '#ff4f2b']
LANG_COLORS = [OR, LI, VI, '#f1ede4', '#3ec7ff', '#ffb02b', MUTED]
HERE = os.path.dirname(os.path.abspath(__file__))
E = html.escape

Q = '''query($login:String!){user(login:$login){
 followers{totalCount}
 repositories(ownerAffiliations:OWNER,isFork:false,first:100,privacy:PUBLIC){totalCount
  nodes{stargazerCount languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}
 contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}'''


def fetch(user):
    if os.environ.get('STATS_FAKE'):
        random.seed(7); today = dt.date.today(); start = today - dt.timedelta(days=370 + today.weekday())
        days = [{'date': str(start + dt.timedelta(d)), 'contributionCount': random.choice([0, 0, 0, 1, 2, 3, 5, 8, 12])} for d in range(371)]
        weeks = [{'contributionDays': days[i:i + 7]} for i in range(0, 371, 7)]
        return {'followers': {'totalCount': 4}, 'repositories': {'totalCount': 46, 'nodes': [
            {'stargazerCount': 2, 'languages': {'edges': [{'size': s, 'node': {'name': n}}]}} for n, s in
            [('C#', 900), ('JavaScript', 700), ('TypeScript', 300), ('Python', 200), ('Rust', 120), ('HTML', 100), ('CSS', 80), ('Java', 30)]]},
            'contributionsCollection': {'contributionCalendar': {'totalContributions': 1234, 'weeks': weeks}}}
    req = urllib.request.Request('https://api.github.com/graphql', method='POST',
                                 data=json.dumps({'query': Q, 'variables': {'login': user}}).encode(),
                                 headers={'Authorization': 'bearer ' + os.environ['GITHUB_TOKEN'], 'User-Agent': 'profile-stats'})
    d = json.load(urllib.request.urlopen(req))
    if 'errors' in d: sys.exit(d['errors'])
    return d['data']['user']


class Fonts:
    def __init__(self): self.used = {'sans': set(), 'mono': set()}
    def t(self, kind, s): self.used[kind].update(str(s)); return E(str(s))
    def css(self):
        out = []
        for kind, fn, fam in (('sans', 'inter.woff2', 'IT'), ('mono', 'mono.woff2', 'JB')):
            f = TTFont(os.path.join(HERE, 'fonts', fn)); o = subset.Options(); o.flavor = 'woff2'
            s = subset.Subsetter(o); s.populate(text=''.join(self.used[kind]) + ' '); s.subset(f)
            b = io.BytesIO(); f.flavor = 'woff2'; f.save(b)
            out.append("@font-face{font-family:%s;font-weight:100 900;src:url(data:font/woff2;base64,%s) format('woff2')}" % (fam, base64.b64encode(b.getvalue()).decode()))
        return ''.join(out) + '.s{font-family:IT,Inter,system-ui,sans-serif}.m{font-family:JB,ui-monospace,monospace}'


_HM = None
def text_width(txt, size):
    global _HM
    if _HM is None:
        f = TTFont(os.path.join(HERE, 'fonts', 'inter.woff2')); _HM = (f['hmtx'].metrics, f.getBestCmap(), f['head'].unitsPerEm)
    m, cmap, upm = _HM
    return sum(m.get(cmap.get(ord(ch), ''), (550, 0))[0] for ch in txt) * size / upm * 1.04


def frame(w, h, inner, css, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{E(label)}"><style>{css}</style>'
            f'<defs><clipPath id="c"><rect width="{w}" height="{h}" rx="24"/></clipPath>'
            f'<pattern id="g" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="{CREAM}" stroke-opacity=".045"/></pattern>'
            f'<radialGradient id="o" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{OR}" stop-opacity=".22"/><stop offset="1" stop-color="{OR}" stop-opacity="0"/></radialGradient></defs>'
            f'<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="{INK}"/><rect width="{w}" height="{h}" fill="url(#g)"/>'
            f'<ellipse cx="{w - 60}" cy="0" rx="320" ry="200" fill="url(#o)"/></g>'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="23.5" fill="none" stroke="{CREAM}" stroke-opacity=".12"/>{inner}</svg>')


def streaks(days):
    cur = best = run = 0
    for d in days:
        run = run + 1 if d['contributionCount'] else 0
        best = max(best, run)
    # current streak: today may still be empty, so start from yesterday in that case
    seq = days[:-1] if days and not days[-1]['contributionCount'] else days
    for d in reversed(seq):
        if not d['contributionCount']: break
        cur += 1
    return cur, best


def activity(u):
    F = Fonts(); W, H = 1200, 400
    cal = u['contributionsCollection']['contributionCalendar']
    days = [d for w in cal['weeks'] for d in w['contributionDays']]
    cur, best = streaks(days)
    stars = sum(n['stargazerCount'] for n in u['repositories']['nodes'])
    nums = [(f"{cal['totalContributions']:,}", 'contributions · 12 months'), (str(cur), 'current streak'),
            (str(best), 'longest streak'), (str(u['repositories']['totalCount']), 'public repos'), (str(stars), 'stars earned')]
    inner, x = '', 48
    for i, (n, lab) in enumerate(nums):
        col = OR if i == 0 else CREAM
        inner += (f'<g class="in" style="animation-delay:{i * .08:.2f}s"><text class="s" x="{x}" y="96" font-size="50" font-weight="800" letter-spacing="-1.5" fill="{col}">{F.t("sans", n)}</text>'
                  f'<text class="m" x="{x + 2}" y="126" font-size="12.5" letter-spacing=".5" fill="{CREAM}" fill-opacity=".55">{F.t("mono", lab)}</text></g>')
        x += 224
    # heatmap
    weeks = cal['weeks'][-53:]
    mx = max([d['contributionCount'] for d in days] + [1])
    cell, gap, ox, oy = 17, 4, 48, 176
    css_anim = ''
    for wi, w in enumerate(weeks):
        for d in w['contributionDays']:
            wd = dt.date.fromisoformat(d['date']).weekday()  # Mon=0
            row = (wd + 1) % 7  # Sunday first like GitHub
            c = d['contributionCount']
            lvl = 0 if c == 0 else min(4, 1 + int(3 * c / mx + .0001)) if mx > 1 else 4
            inner += (f'<rect class="hc" style="animation-delay:{wi * .018:.3f}s" x="{ox + wi * (cell + gap)}" y="{oy + row * (cell + gap)}" '
                      f'width="{cell}" height="{cell}" rx="4.5" fill="{HEAT[lvl]}"><title>{E(d["date"])}: {c}</title></rect>')
    months, last = '', None
    for wi, w in enumerate(weeks):
        m = dt.date.fromisoformat(w['contributionDays'][0]['date']).strftime('%b')
        if m != last and wi < len(weeks) - 2:
            months += f'<text class="m" x="{ox + wi * (cell + gap)}" y="{oy - 12}" font-size="11.5" fill="{CREAM}" fill-opacity=".45">{F.t("mono", m.upper())}</text>'
        last = m
    legend = f'<g transform="translate({W - 48 - 5 * 18 - 110} {H - 30})"><text class="m" x="0" y="11" font-size="11.5" fill="{CREAM}" fill-opacity=".45">{F.t("mono", "LESS")}</text>'
    for i, c in enumerate(HEAT):
        legend += f'<rect x="{44 + i * 18}" y="0" width="13" height="13" rx="3.5" fill="{c}"/>'
    legend += f'<text class="m" x="{44 + 5 * 18 + 6}" y="11" font-size="11.5" fill="{CREAM}" fill-opacity=".45">{F.t("mono", "MORE")}</text></g>'
    stamp = f'<text class="m" x="48" y="{H - 19}" font-size="11.5" fill="{CREAM}" fill-opacity=".35">{F.t("mono", "UPDATED " + dt.date.today().strftime("%d %b %Y").upper())}</text>'
    anim = ('@keyframes in{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}.in{animation:in .8s cubic-bezier(.2,.7,.2,1) both}'
            '@keyframes hc{from{opacity:0}to{opacity:1}}.hc{animation:hc .5s ease-out both}')
    body = inner + months + legend + stamp
    return frame(W, H, body, F.css() + anim, 'GitHub activity')


def languages(u):
    F = Fonts(); W, H = 1200, 180
    tot = {}
    for n in u['repositories']['nodes']:
        for e in n['languages']['edges']:
            tot[e['node']['name']] = tot.get(e['node']['name'], 0) + e['size']
    top = sorted(tot.items(), key=lambda kv: -kv[1])
    s = sum(v for _, v in top) or 1
    items = top[:6]
    rest = s - sum(v for _, v in items)
    if rest > 0: items.append(('Other', rest))
    inner = f'<text class="m" x="48" y="54" font-size="13" letter-spacing="2" fill="{CREAM}" fill-opacity=".5">{F.t("mono", "LANGUAGES ACROSS PUBLIC REPOS")}</text>'
    x, bw = 48, W - 96
    inner += f'<clipPath id="bar"><rect x="48" y="76" width="{bw}" height="14" rx="7"/></clipPath><g clip-path="url(#bar)">'
    for i, (n, v) in enumerate(items):
        w = bw * v / s
        inner += f'<rect class="gr" x="{x:.1f}" y="76" width="{w + .5:.1f}" height="14" fill="{LANG_COLORS[i % len(LANG_COLORS)]}"/>'
        x += w
    inner += '</g>'
    lx = 48
    for i, (n, v) in enumerate(items):
        pct = f'{100 * v / s:.1f}%'
        nw = text_width(n, 17)
        inner += (f'<circle cx="{lx + 6}" cy="132" r="6" fill="{LANG_COLORS[i % len(LANG_COLORS)]}"/>'
                  f'<text class="s" x="{lx + 20}" y="138" font-size="17" font-weight="600" fill="{CREAM}">{F.t("sans", n)}'
                  f'<tspan class="m" dx="8" font-size="13" font-weight="400" fill-opacity=".5">{F.t("mono", pct)}</tspan></text>')
        lx += 20 + nw + 8 + len(pct) * 7.8 + 30
    anim = '@keyframes gr{from{transform:scaleX(0)}to{transform:scaleX(1)}}.gr{transform-origin:48px 0;animation:gr 1.2s cubic-bezier(.2,.7,.2,1) both}'
    return frame(W, H, inner, F.css() + anim, 'Top languages')


if __name__ == '__main__':
    user, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    u = fetch(user)
    open(os.path.join(out, 'activity.svg'), 'w').write(activity(u))
    open(os.path.join(out, 'languages.svg'), 'w').write(languages(u))
    print('ok')
