#!/usr/bin/env python3
"""
Generiert index.html (Hyperframes) für den STRAIGHT-Testballon:
beat-synchrone B-Roll-Cuts + Typo-Beats + Phonk-Musik. Dark anti-Trinity Look.
Liest selects/selects.json, kopiert genutzte Clips nach assets/broll/.
"""
import os, json, shutil, argparse

PROJ = os.path.expanduser("~/Studio/active/edits/2026-05-31_straight-testballon")
SELECTS_JSON = os.path.expanduser("~/Studio/active/edits/2026-05-30_straight-exclusive-sommeraktion/selects/selects.json")
SELECTS_DIR = os.path.expanduser("~/Studio/active/edits/2026-05-30_straight-exclusive-sommeraktion/selects")
BEAT = 0.496  # 121 BPM
MUSIC_OFFSET = 8.30  # Downbeat ~9.29s − 2 Beats → Beat liegt auf Spot-t=0 (Cut-Grid sitzt auf dem Beat)

# kuratierte Reihenfolge (Kategorie-Arc); fällt auf vorhandene zurück
ARC = ["entrance","action","equipment","atmosphere","action","equipment","action","atmosphere","action","equipment","action","warmth","action","equipment","atmosphere","action","equipment","action","entrance","equipment","action","atmosphere"]

import re
def _cnum(s):
    m = re.search(r'(C\d{3,4})', s.get("clip", s.get("file",""))); return m.group(1) if m else s["file"]

def pick_clips(n):
    data = json.load(open(SELECTS_JSON))["selects"]
    by = {}
    for s in data: by.setdefault(s["cat"], []).append(s)
    for k in by: by[k].sort(key=lambda x:-x["score"])
    ptr = {k:0 for k in by}
    seq, used_src = [], set()
    # Round-Robin entlang ARC, dedupe nach Quell-Clip (C-Nummer)
    def take(cat):
        pool = by.get(cat)
        if not pool: return None
        while ptr[cat] < len(pool):
            c = pool[ptr[cat]]; ptr[cat]+=1
            if _cnum(c) not in used_src:
                used_src.add(_cnum(c)); return c
        return None
    order = ARC[:]
    # falls ARC erschöpft: weiter im Round-Robin über alle Kategorien (nach Häufigkeit)
    cats_by_size = sorted(by, key=lambda k:-len(by[k]))
    i=0
    while len(seq) < n:
        cat = order[i] if i < len(order) else cats_by_size[(i-len(order)) % len(cats_by_size)]
        c = take(cat)
        if c: seq.append(c)
        i+=1
        if i > len(order) + 4*sum(len(v) for v in by.values()): break
    return seq[:n]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--secs", type=float, default=35.0)
    ap.add_argument("--clips", type=int, default=24)
    ap.add_argument("--test", action="store_true", help="kurzer Verify-Modus (6s, 5 cuts, 1 typo)")
    args = ap.parse_args()

    if args.test: args.secs=6.0; args.clips=5

    seq = pick_clips(args.clips)
    os.makedirs(f"{PROJ}/assets/broll", exist_ok=True)
    # genutzte Clips kopieren
    for s in seq:
        src=os.path.join(SELECTS_DIR, s["file"]); dst=f"{PROJ}/assets/broll/{s['file']}"
        if not os.path.exists(dst): shutil.copy(src, dst)

    # Cut-Timeline auf Beat-Grid: Rhythmus-Muster (in Beats) zyklisch
    rhythm = [2,2,1,1,2,4,2,1,1,2,2,4] if not args.test else [2,2,2,2,4]
    cuts=[]; t=0.0; ri=0
    for s in seq:
        beats = rhythm[ri % len(rhythm)]; ri+=1
        dur = round(beats*BEAT,3)
        if t+dur > args.secs: dur = round(args.secs-t,3)
        if dur < 0.2: break
        cuts.append({"file":s["file"],"start":round(t,3),"dur":dur,"cat":s["cat"],"what":s.get("what","")})
        t=round(t+dur,3)
        if t>=args.secs: break
    total = round(min(args.secs, t),3)

    # Typo-Beats (30er-Aktion) — auf Cut-Grenzen gelegt, anti-Trinity
    typo_all = [
        ("30","JAHRE STRAIGHT", "gold"),
        ("30 €","FÜR 30 WOCHEN","white"),
        ("ALL-","INCLUSIVE","gold"),
        ("50%","RABATT","white"),
        ("NUR","30 PLÄTZE","gold"),
        ("JETZT","SICHERN","white"),
    ]
    if args.test: typo_all = [("30","JAHRE STRAIGHT","gold")]
    # gleichmäßig über die Timeline verteilen, auf nächste Cut-Grenze snappen
    typo=[]
    if cuts:
        slots = len(typo_all)
        for i,(big,small,col) in enumerate(typo_all):
            target = total*(i+0.6)/slots
            cut = min(cuts, key=lambda c: abs(c["start"]-target))
            typo.append({"big":big,"small":small,"col":col,"start":cut["start"],"dur":min(1.6, max(1.0, cut["dur"]+0.6))})

    html = build_html(cuts, typo, total)
    open(f"{PROJ}/index.html","w").write(html)
    print(f"index.html: {len(cuts)} cuts, {len(typo)} typo-beats, {total}s")
    for c in cuts: print(f"  {c['start']:5.2f}s +{c['dur']:.2f}  {c['cat']:11} {c['file']}")

def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def build_html(cuts, typo, total):
    GOLD="#C9A24B"
    # Video-Clips
    vids=[]
    for i,c in enumerate(cuts):
        vids.append(
            f'      <video id="v{i}" class="clip broll" src="assets/broll/{c["file"]}" muted playsinline preload="auto" '
            f'data-start="{c["start"]}" data-duration="{c["dur"]}" data-media-start="0" data-track-index="{10+i}"></video>')
    vids="\n".join(vids)
    # Typo-Beats
    typo_html=[]; typo_tl=[]
    for i,tb in enumerate(typo):
        ti=300+i
        colcss = GOLD if tb["col"]=="gold" else "#ffffff"
        typo_html.append(
            f'      <div class="clip typo" id="typo{i}" data-start="{tb["start"]}" data-duration="{tb["dur"]}" data-track-index="{ti}" data-layout-allow-overflow="true">'
            f'<span class="t-big" style="color:{colcss}">{esc(tb["big"])}</span>'
            f'<span class="t-small">{esc(tb["small"])}</span></div>')
        s=tb["start"]
        typo_tl.append(
            f'      tl.fromTo("#typo{i} .t-big", {{opacity:0,y:80,scale:1.3}}, {{opacity:1,y:0,scale:1,duration:0.32,ease:"back.out(2)"}}, {s});\n'
            f'      tl.fromTo("#typo{i} .t-small", {{opacity:0,y:30}}, {{opacity:1,y:0,duration:0.3,ease:"power2.out"}}, {round(s+0.08,3)});\n'
            f'      tl.to("#typo{i}", {{opacity:0,duration:0.2,ease:"power2.in"}}, {round(tb["start"]+tb["dur"]-0.2,3)});')
    typo_html="\n".join(typo_html); typo_tl="\n".join(typo_tl)
    # leichte Ken-Burns/Punch pro Cut
    cut_tl=[]
    for i,c in enumerate(cuts):
        cut_tl.append(f'      tl.fromTo("#v{i}", {{scale:1.08}}, {{scale:1.0,duration:{c["dur"]},ease:"none"}}, {c["start"]});')
    cut_tl="\n".join(cut_tl)
    # End-Logo-Card
    end_start = round(max(0, total-2.8),3)
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@600;800;900&display=swap" rel="stylesheet" />
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html,body {{ width:1080px; height:1920px; overflow:hidden; background:#000; font-family:"Inter",sans-serif; color:#fff; -webkit-font-smoothing:antialiased; }}
  #root {{ position:relative; width:1080px; height:1920px; background:#0A0A0A; overflow:hidden; }}
  .broll {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; will-change:transform; filter:contrast(1.04) saturate(1.02) brightness(0.96); }}
  /* dunkle Vignette + leichtes Gold-Rim, KEIN amber-wash */
  .scrim {{ position:absolute; inset:0; pointer-events:none; background:radial-gradient(ellipse at center, transparent 45%, rgba(0,0,0,0.72) 100%); z-index:80; }}
  .typo {{ position:absolute; left:0; right:0; bottom:360px; text-align:center; z-index:120; }}
  .t-big {{ display:block; font-family:"Anton",sans-serif; font-size:300px; line-height:0.86; letter-spacing:-4px; text-transform:uppercase; text-shadow:0 8px 60px rgba(0,0,0,0.7); }}
  .t-small {{ display:block; font-family:"Anton",sans-serif; font-size:92px; letter-spacing:2px; text-transform:uppercase; color:#fff; margin-top:6px; text-shadow:0 4px 30px rgba(0,0,0,0.8); }}
  .end-card {{ position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; background:#0A0A0A; z-index:200; }}
  .end-logo {{ font-family:"Anton",sans-serif; font-size:150px; letter-spacing:2px; text-transform:uppercase; color:#fff; }}
  .end-logo b {{ color:{GOLD}; }}
  .end-sub {{ font-family:"Anton",sans-serif; font-size:64px; letter-spacing:8px; color:{GOLD}; margin-top:18px; text-transform:uppercase; }}
  .grain {{ position:absolute; inset:0; pointer-events:none; z-index:150; opacity:0.10; background:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.7' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E"); }}
  .flash {{ position:absolute; inset:0; background:#fff; z-index:140; pointer-events:none; opacity:0; }}
</style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920">
{vids}
      <div class="scrim clip" id="scrim" data-start="0" data-duration="{total}" data-track-index="90"></div>
{typo_html}
      <div class="flash clip" id="flash" data-start="0" data-duration="{total}" data-track-index="140"></div>
      <div class="grain clip" id="grain" data-start="0" data-duration="{total}" data-track-index="150"></div>
      <div class="end-card clip" id="end-card" data-start="{end_start}" data-duration="{round(total-end_start,3)}" data-track-index="260" style="opacity:0">
        <div class="end-logo">STR<b>AI</b>GHT</div>
        <div class="end-sub">JETZT SICHERN</div>
      </div>
      <audio class="clip" id="music" src="assets/music/phonk.mp3" data-start="0" data-duration="{total}" data-media-start="{MUSIC_OFFSET}" data-volume="0.9" data-track-index="250"></audio>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
{cut_tl}
{typo_tl}
    // End-Card Reveal + Logo-Pop
    tl.to("#end-card", {{opacity:1, duration:0.25, ease:"power2.out"}}, {end_start});
    tl.fromTo("#end-card .end-logo", {{scale:1.25, opacity:0}}, {{scale:1, opacity:1, duration:0.5, ease:"back.out(1.8)"}}, {round(end_start+0.05,3)});
    tl.fromTo("#end-card .end-sub", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.4, ease:"power2.out"}}, {round(end_start+0.4,3)});
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
