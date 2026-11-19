#!/usr/bin/env python3
"""Generates the animated SVG assets for the Saksham27 GitHub profile README.
Fonts (Inter Tight + JetBrains Mono, OFL) are subset and embedded so the SVGs
render identically everywhere GitHub shows them.  Run: python3 build.py"""
import base64, io, os, html
from fontTools.ttLib import TTFont
from fontTools import subset

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'repo', 'assets')
FONTS = os.environ.get('FONT_DIR', os.path.join(HERE, 'fonts'))
os.makedirs(OUT, exist_ok=True)

INK, CREAM, OR, LI, VI = '#0b0b0d', '#f1ede4', '#ff4f2b', '#c8f53a', '#7b5cff'
LINE, MUTED = '#26262b', '#8b8984'
E = html.escape

_used = {'sans': set(), 'mono': set()}
_pending = []  # (filename, svg body with font placeholder)


def t(kind, s):
    _used[kind].update(s)
    return E(s)


def font_css():
    css = []
    for kind, fname, fam in (('sans', 'inter.woff2', 'IT'), ('mono', 'mono.woff2', 'JB')):
        f = TTFont(os.path.join(FONTS, fname))
        opts = subset.Options(); opts.flavor = 'woff2'; opts.layout_features = ['kern', 'liga', 'tnum']
        sub = subset.Subsetter(opts); sub.populate(text=''.join(_used[kind]) + ' ')
        sub.subset(f)
        b = io.BytesIO(); f.flavor = 'woff2'; f.save(b)
        css.append("@font-face{font-family:%s;font-weight:100 900;src:url(data:font/woff2;base64,%s) format('woff2')}"
                   % (fam, base64.b64encode(b.getvalue()).decode()))
    return ''.join(css) + '.s{font-family:IT,Inter,system-ui,sans-serif}.m{font-family:JB,ui-monospace,monospace}'


def svg(name, w, h, body, extra_css='', label=''):
    _pending.append((name, (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{E(label)}">'
        f'<style>@@FONTS@@{extra_css}</style>{body}</svg>')))


def grid(w, h, step=40, op=.06):
    return (f'<defs><pattern id="g" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
            f'<path d="M{step} 0H0V{step}" fill="none" stroke="{CREAM}" stroke-opacity="{op}"/></pattern></defs>'
            f'<rect width="{w}" height="{h}" fill="url(#g)"/>')


# ---------------------------------------------------------------- header
def header():
    W, H = 1200, 440
    lines = ['building tools people actually search for',
             'shipping data tools on the Apify Store',
             'making Chrome extensions & Notion systems',
             '.NET  ·  Node  ·  React  ·  Rust  ·  Python']
    n = len(lines); per = 3.2; total = per * n
    rot = ''
    css = ''
    for i, s in enumerate(lines):
        a, b = i / n * 100, (i + 1) / n * 100
        css += (f'@keyframes r{i}{{0%,{max(a-0.01,0):.2f}%{{opacity:0;transform:translateY(14px)}}'
                f'{a+2.5:.2f}%,{b-3:.2f}%{{opacity:1;transform:translateY(0)}}'
                f'{b-0.5:.2f}%,100%{{opacity:0;transform:translateY(-14px)}}}}'
                f'.r{i}{{opacity:0;animation:r{i} {total}s cubic-bezier(.2,.7,.2,1) infinite}}')
        rot += f'<text class="m r{i}" x="0" y="0" font-size="22" fill="{CREAM}" fill-opacity=".86">{t("mono", s)}</text>'
    css += (f'@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}.pd{{animation:pulse 1.6s ease-in-out infinite}}'
            f'@keyframes caret{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}.ca{{animation:caret 1s steps(1) infinite}}'
            f'@keyframes drift{{0%,100%{{transform:translate(0,0) scale(1)}}50%{{transform:translate(-40px,18px) scale(1.08)}}}}'
            f'.bl{{transform-box:fill-box;transform-origin:center;animation:drift 14s ease-in-out infinite}}'
            f'@keyframes drift2{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(30px,-16px)}}}}'
            f'.bl2{{transform-box:fill-box;transform-origin:center;animation:drift2 18s ease-in-out infinite}}'
            f'@keyframes rise{{from{{opacity:0;transform:translateY(18px)}}to{{opacity:1;transform:none}}}}'
            f'.in{{animation:rise .9s cubic-bezier(.2,.7,.2,1) both}}.in2{{animation-delay:.12s}}.in3{{animation-delay:.24s}}'
            f'@keyframes spin{{to{{transform:rotate(360deg)}}}}.sp{{transform-box:fill-box;transform-origin:center;animation:spin 40s linear infinite}}')
    body = f'''
<defs>
 <clipPath id="c"><rect width="{W}" height="{H}" rx="28"/></clipPath>
 <radialGradient id="o" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{OR}" stop-opacity=".55"/><stop offset="1" stop-color="{OR}" stop-opacity="0"/></radialGradient>
 <radialGradient id="v" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{VI}" stop-opacity=".35"/><stop offset="1" stop-color="{VI}" stop-opacity="0"/></radialGradient>
 <linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{INK}"/><stop offset=".55" stop-color="{INK}" stop-opacity=".6"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></linearGradient>
</defs>
<g clip-path="url(#c)">
 <rect width="{W}" height="{H}" fill="{INK}"/>
 {grid(W, H)}
 <ellipse class="bl" cx="980" cy="120" rx="360" ry="300" fill="url(#o)"/>
 <ellipse class="bl2" cx="760" cy="420" rx="320" ry="220" fill="url(#v)"/>
 <rect width="{W}" height="{H}" fill="url(#fade)"/>
 <!-- S² mark -->
 <g transform="translate(1000 176)">
  <circle class="sp" r="118" fill="none" stroke="{CREAM}" stroke-opacity=".18" stroke-dasharray="2 9"/>
  <rect x="-70" y="-70" width="140" height="140" rx="36" fill="{OR}"/>
  <text class="s" x="-40" y="34" font-size="96" font-weight="900" fill="{INK}">{t("sans","S")}</text>
  <text class="s" x="18" y="-6" font-size="46" font-weight="900" fill="{INK}">{t("sans","2")}</text>
 </g>
 <g transform="translate(64 0)">
  <g class="in"><rect y="62" width="292" height="36" rx="18" fill="{CREAM}" fill-opacity=".06" stroke="{CREAM}" stroke-opacity=".14"/>
   <circle class="pd" cx="22" cy="80" r="5" fill="{LI}"/>
   <text class="m" x="38" y="85.5" font-size="15" fill="{CREAM}" fill-opacity=".8">{t("mono","now building SSquared Labs")}</text></g>
  <text class="s in in2" x="-4" y="198" font-size="104" font-weight="800" letter-spacing="-4" fill="{CREAM}">{t("sans","Saksham Singh")}<tspan fill="{OR}">{t("sans",".")}</tspan></text>
  <text class="s in in3" x="0" y="248" font-size="27" font-weight="500" fill="{CREAM}" fill-opacity=".62">{t("sans","Software engineer · indie product builder · India")}</text>
  <g transform="translate(0 316)"><text class="m" x="0" y="0" font-size="22" fill="{OR}">{t("mono","~$")}</text>
   <g transform="translate(40 0)">{rot}</g></g>
  <line x1="0" y1="372" x2="1072" y2="372" stroke="{CREAM}" stroke-opacity=".1"/>
  <text class="m" x="0" y="404" font-size="14" letter-spacing="2" fill="{CREAM}" fill-opacity=".45">{t("mono","SSQUAREDLABS.DEV")}</text>
  <text class="m" x="1072" y="404" text-anchor="end" font-size="14" letter-spacing="2" fill="{CREAM}" fill-opacity=".45">{t("mono","APIFY · CHROME · NOTION")}</text>
 </g>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="27.5" fill="none" stroke="{CREAM}" stroke-opacity=".1"/>'''
    svg('header.svg', W, H, body, css, 'Saksham Singh: software engineer and indie product builder')


# ---------------------------------------------------------------- section titles
def title(name, num, label):
    W, H = 1200, 84
    body = (f'<text class="m" x="2" y="52" font-size="17" letter-spacing="2" fill="{OR}">{t("mono", num)}</text>'
            f'<text class="s" x="64" y="56" font-size="40" font-weight="800" letter-spacing="-1.2" fill="#8b8984">{t("sans", label)}</text>'
            f'<line x1="64" y1="78" x2="{W}" y2="78" stroke="#8b8984" stroke-opacity=".35"/>'
            f'<rect class="ul" x="64" y="76.5" width="120" height="3" rx="1.5" fill="{OR}"/>')
    css = '@keyframes ul{0%{transform:translateX(0)}50%{transform:translateX(80px)}100%{transform:translateX(0)}}.ul{animation:ul 6s ease-in-out infinite}'
    svg(name, W, H, body, css, label)


# ---------------------------------------------------------------- project cards
ICONS = {
    'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/>',
    'db': '<ellipse cx="12" cy="5.5" rx="8" ry="2.8"/><path d="M4 5.5v13c0 1.6 3.6 2.8 8 2.8s8-1.2 8-2.8v-13M4 12c0 1.6 3.6 2.8 8 2.8s8-1.2 8-2.8"/>',
    'puzzle': '<path d="M9 3.5a2 2 0 0 1 4 0V5h4a1 1 0 0 1 1 1v4h-1.5a2 2 0 0 0 0 4H18v4a1 1 0 0 1-1 1h-4v-1.5a2 2 0 0 0-4 0V19H5a1 1 0 0 1-1-1v-4h1.5a2 2 0 0 0 0-4H4V6a1 1 0 0 1 1-1h4z"/>',
    'grid': '<rect x="3.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.5"/><path d="M14 17h6M17 14v6"/>',
}


def card(name, acc, icon, kicker, head, desc, chips, status, status_live=True):
    W, H = 580, 300
    chip_svg, x = '', 0
    for c in chips:
        w = len(c) * 8.4 + 26
        chip_svg += (f'<rect x="{x}" y="0" width="{w:.0f}" height="30" rx="15" fill="{CREAM}" fill-opacity=".05" stroke="{CREAM}" stroke-opacity=".14"/>'
                     f'<text class="m" x="{x + 13}" y="20" font-size="13" fill="{CREAM}" fill-opacity=".75">{t("mono", c)}</text>')
        x += w + 8
    sw = len(status) * 7.9 + 40
    dlines = ''.join(f'<tspan x="0" dy="{0 if i == 0 else 27}">{t("sans", l)}</tspan>' for i, l in enumerate(desc))
    css = ('@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}.pd{animation:pulse 1.6s ease-in-out infinite}'
           '@keyframes sh{0%{transform:translateX(-200px)}60%,100%{transform:translateX(800px)}}.sh{animation:sh 6s ease-in-out infinite}')
    body = f'''
<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="24"/></clipPath>
<radialGradient id="o" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{acc}" stop-opacity=".32"/><stop offset="1" stop-color="{acc}" stop-opacity="0"/></radialGradient>
<linearGradient id="s" x1="0" x2="1"><stop offset="0" stop-color="{CREAM}" stop-opacity="0"/><stop offset=".5" stop-color="{CREAM}" stop-opacity=".06"/><stop offset="1" stop-color="{CREAM}" stop-opacity="0"/></linearGradient></defs>
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{INK}"/>{grid(W, H, 32, .045)}
<ellipse cx="{W - 40}" cy="20" rx="230" ry="170" fill="url(#o)"/>
<rect class="sh" x="0" y="0" width="160" height="{H}" fill="url(#s)" transform="skewX(-20)"/>
<rect x="0" y="0" width="{W}" height="4" fill="{acc}"/></g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="23.5" fill="none" stroke="{CREAM}" stroke-opacity=".12"/>
<g transform="translate(36 38)">
 <rect width="52" height="52" rx="14" fill="{acc}"/>
 <g transform="translate(14 14)" fill="none" stroke="{INK}" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">{ICONS[icon]}</g>
 <text class="m" x="70" y="20" font-size="13" letter-spacing="1.6" fill="{CREAM}" fill-opacity=".5">{t("mono", kicker)}</text>
 <text class="s" x="69" y="46" font-size="27" font-weight="800" letter-spacing="-.6" fill="{CREAM}">{t("sans", head)}</text>
 <g transform="translate({W - 72 - sw} 6)"><rect width="{sw:.0f}" height="28" rx="14" fill="{acc if status_live else 'none'}" fill-opacity="{.14 if status_live else 0}" stroke="{acc}" stroke-opacity=".55"/>
  <circle class="{'pd' if status_live else ''}" cx="15" cy="14" r="4" fill="{acc}"/>
  <text class="m" x="27" y="18.5" font-size="12.5" fill="{acc}">{t("mono", status)}</text></g>
 <text class="s" x="0" y="112" font-size="18.5" font-weight="500" fill="{CREAM}" fill-opacity=".72">{dlines}</text>
 <g transform="translate(0 196)">{chip_svg}</g>
 <g transform="translate({W - 104} 196)"><circle cx="15" cy="15" r="15" fill="{CREAM}" fill-opacity=".06" stroke="{CREAM}" stroke-opacity=".18"/>
  <path d="M9 15h12M16 10l5 5-5 5" fill="none" stroke="{CREAM}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></g>
</g>'''
    svg(name, W, H, body, css, head)


# ---------------------------------------------------------------- footer
def footer():
    W, H = 1200, 120
    css = '@keyframes m{to{transform:translateX(-600px)}}.mq{animation:m 22s linear infinite}'
    words = ['SHIP SMALL', 'SHIP OFTEN', 'BUILD WHAT PEOPLE SEARCH FOR', 'AUTOMATE THE BORING PARTS']
    seq, x = '', 0
    for k in range(4):
        for wd in words:
            seq += f'<text class="m" x="{x}" y="0" font-size="15" letter-spacing="3" fill="{CREAM}" fill-opacity=".55">{t("mono", wd)}</text>'
            x += len(wd) * 12 + 44
            seq += f'<text class="s" x="{x - 30}" y="1" font-size="16" fill="{OR}">{t("sans", "✦")}</text>'
    body = f'''<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="24"/></clipPath>
<linearGradient id="f" x1="0" x2="1"><stop offset="0" stop-color="{INK}"/><stop offset=".1" stop-color="{INK}" stop-opacity="0"/><stop offset=".9" stop-color="{INK}" stop-opacity="0"/><stop offset="1" stop-color="{INK}"/></linearGradient></defs>
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{INK}"/>{grid(W, H, 30, .04)}
<g transform="translate(0 66)"><g class="mq">{seq}</g></g><rect width="{W}" height="{H}" fill="url(#f)"/></g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="23.5" fill="none" stroke="{CREAM}" stroke-opacity=".1"/>'''
    svg('footer.svg', W, H, body, css, 'Ship small, ship often')


header()
title('t-about.svg', '01', 'About')
title('t-building.svg', '02', 'What I’m building')
title('t-stack.svg', '03', 'Toolbox')
title('t-stats.svg', '04', 'Activity')
card('card-labs.svg', OR, 'globe', 'THE STUDIO', 'SSquared Labs',
     ['A one-person software studio shipping small,', 'sharp tools that people already search for.', 'Everything automated, end to end.'],
     ['Python', 'Cloudflare', 'Static site'], 'LIVE')
card('card-apify.svg', LI, 'db', 'APIFY STORE', 'Data tools',
     ['Contact finder, PDF to text & AI chunks,', 'domain email & DNS checker, and bank', 'statement / invoice PDF to CSV.'],
     ['Node.js', 'Apify SDK', 'Pay per event'], '4 LIVE')
card('card-chrome.svg', VI, 'puzzle', 'CHROME WEB STORE', 'Browser extensions',
     ['Contact Finder pulls emails & socials from', 'any page. E-Invoice Viewer opens XRechnung,', 'ZUGFeRD, Peppol & KSeF invoices.'],
     ['Manifest V3', 'JavaScript', 'i18n'], 'IN REVIEW', False)
card('card-notion.svg', OR, 'grid', 'NOTION TEMPLATES', 'Life & money systems',
     ['Budget & finance trackers for India and', 'global users, plus a life goals planner', 'built to top-seller standards.'],
     ['Notion', 'Formulas', 'Dashboards'], 'DEC 2026', False)
footer()

fonts = font_css()
for name, s in _pending:
    with open(os.path.join(OUT, name), 'w') as fh:
        fh.write(s.replace('@@FONTS@@', fonts))
    print(name, os.path.getsize(os.path.join(OUT, name)) // 1024, 'KB')
