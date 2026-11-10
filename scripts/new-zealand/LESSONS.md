# New Zealand build: what was hard, what we did, what to do next time

Written during the build (Nov 2026) so the next non-US / island-nation case starts faster.

## 1. Data access was the first wall
**Hard:** The sandbox shell could only reach GitHub and package registries. Government sites (elections.nz, Stats NZ, RNZ) returned proxy 403s and WebFetch failed on news and reference pages.
**What we did:** Boundaries came from a third-party GitHub copy of the Stats NZ 2025 files. Results were transcribed from the user's RNZ screenshots, then checked against the official seat totals (National 42, Labour 21, TPM 5, Greens 2, ACT 1). Populations were read from the Representation Commission PDF through the user's Chrome, using pdf.js injected into an elections.nz page.
**Next time:**
- Probe network reach in the first minute (GitHub, the official site, one news site) and plan the data route from the result.
- Ask for screenshots or files early, while building other parts.
- Keep a "source of each number" table from the start. It also feeds the credits line.
- Always reconcile totals against an official figure before building.

## 2. Names did not match across three datasets
**Hard:** Macrons (Ōtāhuhu, Te Tai Hauāuru), hyphens and "Mt"/"Mount" differed between boundaries, results and populations.
**What we did:** The join step fails loudly on any unmatched name or party. We fixed the sources, not the matcher.
**Next time:** Use a stable id (slug or official electorate id) in every file from the beginning.

## 3. Boundary files include sea, so the islands touched
**Hard:** Electoral boundaries run out to sea. North and South Island polygons merged across Cook Strait, and one Māori seat spans both islands. The engine would have drawn one bridged blob.
**What we did:** Clipped every electorate to Natural Earth 10m land (public domain) with a small buffer, with a fallback to the original shape if a seat lost all its land. Dropped Chatham Islands parts. Added a multi-landmass feature to the engine: `lens.landmasses: true` keeps every real landmass instead of only the largest, and `genall.py` takes the largest landmass for the legacy outline.
**Next time:**
- Check "does clipping to land split the map?" for any archipelago or island country (Japan, Philippines, Indonesia, Greece, Trinidad and Tobago).
- Keep `state_buffer` small (0.01 here) so water gaps stay open.
- Multi-part units (one seat on two islands) are still unsupported: the engine uses the largest part. This affects Te Tai Tonga on the Māori layer.

## 4. Extreme density made the warp very slow
**Hard:** The Auckland seats are about 0.05° wide and ~278× denser than the mean, while the South Island seats are huge. The density-equalizing flow takes a time step of roughly 0.3 × cell ÷ peak velocity. Each area-correction pass multiplies the density again, so passes got slower and slower (pass 4 ran over 10 minutes). We also launched several warpack runs at once on a 2-core machine, which hid the real cost.
**What we did:** Killed the stalled runs, measured one DCT (0.02 s, so steps were the cost, not grid size), then limited `hex.warp_passes` to 4 (max area error 14.5%, mean 1.6%). The exact hexagon assignment still gives every seat the right count, so this affects shape fidelity only. The clean single run took 71 s.
**Next time:**
- Run one job at a time, and log elapsed time per pass.
- Add a wall-clock budget and a step counter to `fit_areas`, and save the best result so far instead of returning only at the end.
- Estimate the density ratio (max G0 ÷ min) before building. Above ~100×, start with 3-4 passes and a coarser grid.
- Consider capping the per-seat density ratio, or building big cities in a nested higher-resolution pass.

## 5. The template assumed exactly two candidates
**Hard:** Colours, bars, cards, table and copy all used a blue/red pair.
**What we did:** `nz_patch.py` derives `nz.template.html` from `warp.template.html` using exact-match replacements that fail if the base template changes. The engine's `d` carries the winning margin and `r` the party index. Colour intensity is margin ÷ the 90th-percentile margin.
**Next time:** Promote this to a first-class "multi-party" mode in the base template, with a `parties` array, rather than a patch.

## 6. Party colours versus colour-blind safety
**Hard:** National blue, Labour red, Greens green, ACT gold and TPM maroon-purple are conventional, but red and green fail deutan separation (ΔE 4.9), and ACT gold has contrast under 3:1 on light backgrounds.
**What we did:** Ran the validator, moved Greens to a teal-green and TPM to a violet. The light palette passes all checks except the gold contrast warning. In dark mode only the lightness-band check still fails (the gold and green steps sit just outside it). Secondary encoding is the key with seat counts, the card text, the table view, and per-segment tooltips.
**Next time:** Validate party colours on day one and negotiate the nearest passing hue, since voters recognise parties by colour.

## 7. Process lessons
- Ask the "how will this be shown" questions (winner colour? Māori seats? preliminary?) before building: we did, and it saved rework.
- A mid-build requirement change (two landmasses) is much cheaper when the pipeline has clear stages and loud failure checks.
- Send a short status line whenever a long job runs, and avoid blocking waits longer than the tool timeout (use background runs and poll).

## 8. Smaller bugs worth a checklist
- `fit_areas` returned the f from one update *after* the f that produced the hexagon layout. The next step (`build_warp_rings`) re-ran the flow with that denser f, which took over 10 minutes and did not match the layout. It now returns the f that produced the parts. **Check:** any stage that re-derives a result from saved parameters must use the same parameters that produced the saved output.
- The engine copy was missing `ed_layer.py`, found only at the last build step. **Check:** copy the whole `src/` tree, then run a smoke build on the reference election before adapting.
- A text-patch for the template swallowed a closing `uiMode(); }`, giving a JS syntax error that only showed in a browser. **Check:** always load the built page headless and fail on console errors, as part of the build.
- Wording that assumed one story (Labour "packed into cities") was wrong for the Māori layer, where the runner-up holds large rural seats. **Check:** make generated copy conditional on the data, and read the dek of every layer.
- Multi-layer elections (general plus Māori) need a layer switch and per-layer back links; decide this before the first build.

## 9. Adding the density-vs-vote and grow/shrink charts
- **Data:** the Electoral Commission preliminary site (electionresults.govt.nz/ge2026) has one page per electorate with candidate and party counts. It was reachable through the user's Chrome when the sandbox shell was blocked. All 71 margins matched our RNZ transcription exactly, which is a good cross-check. Saved as `data/electorate-votes.csv`.
- **Design decision:** the candidate table does not say which party each candidate belongs to (only the top two show up in the status table), so a per-party candidate share is not available. We used **party-vote share** for the vertical axis: it is complete for every party, it is what decides seats under MMP, and the dot colour still shows who won the electorate.
- **Small-n rule:** with 7 seats (Māori page) no fit line or r is drawn, and label placement tries eight positions.
- **Areas:** true km² come from an equal-area (sinusoidal) projection of the land-clipped geometry, not from the engine's projected degrees.
- **Next time:** ask early which vote measure a two-candidate chart should use, since MMP and preferential systems have no single "share of the vote".

## 10. Adding the briefing (intro) above the map

**Hard:** An intro with its own headings, tables, cards and buttons would collide with the map page's CSS (`.card`, `.note`, `.dot`, table rules). It also needed a seven-party palette, while the map config lists only five.
**What we did:** The intro lives in a shadow root (`<template id="intro-tpl">` cloned by `nz_intro.js`), so styles cannot leak either way. Party colours reach it through `--ip-*` variables defined by `nz_patch.py`, so the map config stays at five parties. Markup is generated by `nz_intro.py` from `nz_intro_body.html`. Images are files in `new-zealand/img/`. The Māori layer gets a "Read the briefing" link instead of the block.
**Bug worth remembering:** the new anchor reused `id="map"`, which the map SVG already owns. `getElementById` found the wrong element and the map drew nothing, with no console error. **Check:** grep the built page for duplicate ids before shipping any injected block.
**Check next time:** with all seven colours fixed by brand, red (Te Pāti Māori) next to green (Greens) fails the colour-blind check; keep direct labels and the legend filter.
