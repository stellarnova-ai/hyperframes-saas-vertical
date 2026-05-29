# hyperframes-saas-vertical — Template

Basis: erster Hyperframes-Build (10s 9:16 SaaS-Explainer „KI überflügelt uns", 2026-05-10).
Stand: getestet, lint+inspect 0 errors, gerendert.

## Was drin ist
- 1080×1920, 10s @ 30fps
- Beat-Struktur: (1) Year-Counter-Klimax → Hero-Typo-Stack mit Shimmer → (2) White-Flash → Card-Stack (Chart + Stat-Card + Pill, 2.5D-Parallax) → Punchline mit Shimmer
- Components: shimmer-sweep, grain-overlay (in `compositions/components/`)
- Atmosphäre: receding 2.5D-Grid (CSS perspective), 2 glow-blobs drift, vignette, filmgrain
- Palette: cyan `#5ee7df`/`#6ef0e8`, magenta `#ff4d8b`, bg `#050507`. Fonts: Inter (900/800) + JetBrains Mono.

## Neues Projekt draus machen
```bash
cp -r ~/Studio/dev/templates/hyperframes-saas-vertical ~/Studio/active/edits/$(date +%F)_<slug>
cd ~/Studio/active/edits/$(date +%F)_<slug>
# index.html: Text/Farben/Timings ändern, Beat-Inhalt austauschen
npx hyperframes lint && npx hyperframes inspect   # MUSS 0 errors
npx hyperframes preview                            # Studio auf localhost:30xx
npx hyperframes render -o ../<name>.mp4
```

## Lint/Inspect-Traps (immer beachten)
- Jedes timed Element = eigener `data-track-index` (gleichzeitig + gleicher Track = Error)
- CSS `transform: translateX(-50%)` ↔ GSAP-Tween-Konflikt → `gsap.set(el,{xPercent:-50})` + in fromTo mitführen
- Absichtlich überragende Kinder / off-canvas Animation-Entry → `data-layout-allow-overflow="true"` aufs Parent/Stage
- Überlappende Tweens auf gleicher Property → `overwrite:"auto"` oder späterer Start
- GSAP-Properties NUR: opacity/x/y/scale/scaleX/scaleY/rotation/width/height/visibility (+ CSS-Custom-Props). 3D nur via statisches CSS perspective + Layer-Parallax simulieren.
- Vor Arbeit: `/hyperframes` Skill invoken (encodet die Patterns).

## Decision-Kontext
Siehe Memory `architecture_decision_hyperframes_remotion_hybrid.md` — Hybrid-Strategie: Hyperframes für <30s 9:16-Spots, Remotion für alles Größere/KIBA/ProRes-Alpha.
