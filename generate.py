import os, json, datetime, urllib.request
from xml.sax.saxutils import escape
from ascii_art import ART, ART_FONT, ART_LINE, SPIN, SPIN_SECONDS, MODE_3D, FRAMES_3D
if MODE_3D:
    import lotus3d

USER = "nicoleespinosa"
INICIO = datetime.date(2024, 3, 1)
WIDTH = 60

def uptime():
    hoje = datetime.date.today()
    a = hoje.year - INICIO.year; m = hoje.month - INICIO.month; d = hoje.day - INICIO.day
    if d < 0:
        m -= 1
        prev = (hoje.replace(day=1) - datetime.timedelta(days=1))
        d += prev.day
    if m < 0: a -= 1; m += 12
    p = lambda n, s: f"{n} {s if n == 1 else s + 's'}"
    return f"{p(a,'year')}, {p(m,'month')}, {p(d,'day')}"

def github_stats():
    token = os.getenv("ACCESS_TOKEN") or os.getenv("GITHUB_TOKEN")
    zero = dict(repos=0, contrib=0, stars=0, followers=0, commits=0)
    if not token: return zero
    q = """query($login:String!){ user(login:$login){
      followers{totalCount}
      repositoriesContributedTo(contributionTypes:[COMMIT,PULL_REQUEST,REPOSITORY]){totalCount}
      repositories(ownerAffiliations:OWNER, first:100, isFork:false){totalCount nodes{stargazerCount}}
      contributionsCollection{totalCommitContributions restrictedContributionsCount}
    }}"""
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": q, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    try:
        u = json.load(urllib.request.urlopen(req, timeout=30))["data"]["user"]
    except Exception as e:
        print("Falha ao buscar stats:", e); return zero
    cc = u["contributionsCollection"]
    return dict(repos=u["repositories"]["totalCount"],
                contrib=u["repositoriesContributedTo"]["totalCount"],
                stars=sum(n["stargazerCount"] for n in u["repositories"]["nodes"]),
                followers=u["followers"]["totalCount"],
                commits=cc["totalCommitContributions"] + cc["restrictedContributionsCount"])


def linhas(s):
    return [
        ("title", "nicole@espinosa"),
        ("kv", "OS", "Windows, Salesforce Platform"),
        ("kv", "Uptime", uptime()),
        ("kv", "Host", "AI/R Everymind"),
        ("kv", "Role", "Mid-level Salesforce Developer"),
        ("kv", "Kernel", "Apex, LWC, Flows, SOQL/SOSL"),
        ("kv", "IDE", "VS Code + Salesforce CLI"),
        ("blank",),
        ("kv", "Languages.Programming", "Apex, JavaScript, Java"),
        ("kv", "Languages.Computer", "HTML, CSS, JSON, XML"),
        ("kv", "Languages.Real", "Portuguese, English"),
        ("blank",),
        ("kv", "Clouds", "Sales, Service, Agentforce"),
        ("kv", "Certs", "Agentforce Specialist, AI Associate"),
        ("kv", "DevOps", "Git, Flosum, DevOps Center, Azure"),
        ("kv", "Hobbies", "ASCII art, Sudoku, Pokémon TCG, Music"),
        ("blank",),
        ("section", "Contact"),
        ("kv", "Email", "nicoleespinosactt@gmail.com"),
        ("kv", "LinkedIn", "nicolespinosa"),
        ("kv", "GitHub", USER),
        ("blank",),
        ("section", "GitHub Stats"),
        ("stats1", s), ("stats2", s),
    ]


def t(cls, txt): return f'<tspan class="{cls}">{escape(str(txt))}</tspan>'

def render_line(l):
    k = l[0]
    if k == "title":
        return t("key", l[1]) + " " + t("cc", "—" * (WIDTH - len(l[1]) - 1))
    if k == "section":
        return t("cc", "- ") + t("key", l[1]) + " " + t("cc", "—" * (WIDTH - len(l[1]) - 3))
    if k == "blank":
        return t("cc", ". ")
    if k == "kv":
        key, val = l[1], l[2]
        dots = WIDTH - 2 - len(key) - 2 - len(val) - 1
        return t("cc", ". ") + t("key", key) + ":" + t("cc", " " + "." * max(dots, 1) + " ") + t("value", val)
    s = l[1]
    if k == "stats1":
        return two("Repos", f"{s['repos']} {{Contributed: {s['contrib']}}}", "Stars", s["stars"])
    if k == "stats2":
        return two("Commits (year)", s["commits"], "Followers", s["followers"])

def seg(key, val, w):
    val = str(val); dots = w - len(key) - 3 - len(val)
    return t("key", key) + ":" + t("cc", " " + "." * max(dots, 1) + " ") + t("value", val)

def two(k1, v1, k2, v2, L=33):
    return t("cc", ". ") + seg(k1, v1, L) + t("cc", " | ") + seg(k2, v2, WIDTH - 2 - L - 3)

THEMES = {
    "dark":  dict(bg="#161b22", border="#30363d", text="#c9d1d9", key="#ffa657", value="#a5d6ff", cc="#616e7f", art="#f778ba"),
    "light": dict(bg="#f6f8fa", border="#d0d7de", text="#24292f", key="#953800", value="#0a3069", cc="#8c959f", art="#bf3989"),
}
DOTS = ["#8b949e", "#f0f6fc", "#39c5cf", "#db61a2", "#58a6ff", "#e3b341", "#3fb950", "#f85149"]

def svg(theme, s):
    c = THEMES[theme]; LH = 20; FS = 16; X_INFO = 500
    if MODE_3D:
        frames = [f.split("\n") for f in lotus3d.frames(FRAMES_3D)]
    else:
        frames = [ART.split("\n")]
    art = max(frames, key=len); info = [render_line(l) for l in linhas(s)]
    h = max(len(info) * LH + 60, int(len(art) * ART_LINE) + 50)
    out = [f'<?xml version="1.0" encoding="utf-8"?>',
           f'<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,\'Courier New\',monospace" width="1105px" height="{h}px" font-size="{FS}px">',
           "<style>", f".key{{fill:{c['key']};}} .value{{fill:{c['value']};}} .cc{{fill:{c['cc']};}} .art{{fill:{c["art"]};font-weight:bold;}}",
           "text,tspan{white-space:pre;}",
           "</style>",
           f'<rect width="1105px" height="{h}px" fill="{c["bg"]}" rx="15" stroke="{c["border"]}"/>']
    art_h = len(art) * ART_LINE
    y0 = 20 + max(0, (len(info) * LH - art_h) / 2) + ART_LINE

    nrows = max(len(f) for f in frames)
    wmax = max(len(l) for f in frames for l in f)
    cx = 20 + wmax * ART_FONT * 0.6 / 2
    out.append(f'<g transform="translate({cx:.1f},0)"><g>')
    if SPIN and not MODE_3D:
        S = SPIN_SECONDS
        out.append(f'<animateTransform attributeName="transform" type="scale" values="1 1;-1 1;1 1" '
                   f'keyTimes="0;0.5;1" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1" dur="{S}s" repeatCount="indefinite"/>')
        out.append(f'<animate attributeName="opacity" values="1;.55;1;.55;1" keyTimes="0;.25;.5;.75;1" dur="{S}s" repeatCount="indefinite"/>')
    N = len(frames) if (MODE_3D and SPIN) else 1
    dur = SPIN_SECONDS / 2
    for fi, f in enumerate(frames[:N]):
        f = f + [""] * (nrows - len(f))
        if N > 1:
            if fi == 0:
                anim = f'<animate attributeName="opacity" values="1;0" keyTimes="0;{1/N:.4f}" calcMode="discrete" dur="{dur}s" repeatCount="indefinite"/>'
            else:
                anim = (f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{fi/N:.4f};{(fi+1)/N:.4f}" '
                        f'calcMode="discrete" dur="{dur}s" repeatCount="indefinite"/>' if fi < N-1 else
                        f'<animate attributeName="opacity" values="0;1" keyTimes="0;{fi/N:.4f}" calcMode="discrete" dur="{dur}s" repeatCount="indefinite"/>')
            out.append(f'<g opacity="{1 if fi == 0 else 0}">{anim}')
        out.append(f'<text x="0" y="{y0:.1f}" class="art" font-size="{ART_FONT}px" text-anchor="middle" xml:space="preserve">')
        for i, l in enumerate(f):
            if l.strip():
                out.append(f'<tspan x="0" y="{y0 + i*ART_LINE:.1f}">{escape(l.ljust(wmax))}</tspan>')
        out.append("</text>")
        if N > 1: out.append("</g>")
    out.append("</g></g>")
    out.append(f'<text x="{X_INFO}" y="30" fill="{c["text"]}" xml:space="preserve">')
    for i, l in enumerate(info):
        out.append(f'<tspan x="{X_INFO}" y="{30 + i*LH}">{l}</tspan>')
    out.append("</text>")
    yd = 30 + len(info) * LH + 6
    dots = DOTS if theme == "dark" else [d if d != "#f0f6fc" else "#24292f" for d in DOTS]
    for i, col in enumerate(dots):
        out.append(f'<circle cx="{X_INFO + 6 + i*22}" cy="{yd}" r="6" fill="{col}"/>')
    out.append("</svg>")
    return "\n".join(out)

if __name__ == "__main__":
    s = github_stats()
    for th in THEMES:
        open(f"{th}_mode.svg", "w", encoding="utf-8").write(svg(th, s))
    print("ok", s)
