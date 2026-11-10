  /* ---------- charts: density vs the vote, and who grows or shrinks ---------- */
  (function () {
    var V = META.votes, KM = META.km2, PK = META.pickers || [];
    if (!V || !PK.length) { var d0 = document.getElementById('chartsd'); if (d0) d0.hidden = true; return; }
    var small = C.length <= 12, NSVG = 'http://www.w3.org/2000/svg';
    C.forEach(function (c) { c.km2 = KM[c.name]; c.dens = c.pop / c.km2; c.gr = c.popS / c.landS; c.pv = V[c.name]; });
    var seats = function (p) { return p.pi == null ? -1 : tot.cnt[p.pi]; };
    var sel = PK.slice().sort(function (a, b) { return seats(b) - seats(a); })[0].k;
    var pkCol = function (p) { return p.pi == null ? 'var(--ink-3)' : 'var(--p' + p.pi + ')'; };
    var pkOf = function (k) { return PK.filter(function (p) { return p.k === k; })[0]; };
    var share = function (c) { return c.pv.p[sel] / c.pv.tv * 100; }, lx = function (c) { return Math.log10(c.dens); };
    var fmt1 = function (v) { return v >= 100 ? Math.round(v).toLocaleString('en-US') : v >= 10 ? v.toFixed(0) : v.toFixed(1); };
    var W = 360, H = 272, Lm = 38, Rm = 10, Tm = 10, Bm = 36, RAD = small ? 7 : 4.6;
    var xd, yd, sx, sy, fit = null;
    function scales() {
      var xs = C.map(lx), ys = C.map(share), xmin = Math.min.apply(null, xs), xmax = Math.max.apply(null, xs), ymin = Math.min.apply(null, ys), ymax = Math.max.apply(null, ys);
      xd = [Math.floor((xmin - .12) * 4) / 4, Math.ceil((xmax + .12) * 4) / 4];
      var st = (ymax - ymin) < 30 ? 5 : 10; yd = [Math.max(0, Math.floor((ymin - 2) / st) * st), Math.min(100, Math.ceil((ymax + 2) / st) * st)]; yd.step = st;
      sx = function (v) { return Lm + (v - xd[0]) / (xd[1] - xd[0]) * (W - Lm - Rm); }; sy = function (v) { return H - Bm - (v - yd[0]) / (yd[1] - yd[0]) * (H - Bm - Tm); };
      fit = null; if (!small) {
        var w = C.map(function (c) { return c.pv.tv; }), Wt = w.reduce(function (a, b) { return a + b; }, 0), mx = 0, my = 0, i;
        for (i = 0; i < C.length; i++) { mx += w[i] * xs[i]; my += w[i] * ys[i]; } mx /= Wt; my /= Wt;
        var sxx = 0, syy = 0, sxy = 0; for (i = 0; i < C.length; i++) { sxx += w[i] * (xs[i] - mx) * (xs[i] - mx); syy += w[i] * (ys[i] - my) * (ys[i] - my); sxy += w[i] * (xs[i] - mx) * (ys[i] - my); }
        fit = { b: sxy / sxx, a: my - sxy / sxx * mx, r: sxy / Math.sqrt(sxx * syy) };
      }
    }
    function labelSet() {
      var forced = selected != null ? [selected] : [], cand = C.map(function (c) { return c.i; });
      if (!small) { var rs = function (c) { return Math.abs(share(c) - (fit.a + fit.b * lx(c))); }; cand.sort(function (a, b) { return rs(C[b]) - rs(C[a]); }); }
      var order = forced.concat(cand.filter(function (i) { return forced.indexOf(i) < 0; })), placed = [], out = [], lim = small ? 99 : 12;
      var dots = C.map(function (c) { return { x: sx(lx(c)), y: sy(share(c)), r: RAD + 1, i: c.i }; });
      for (var n = 0; n < order.length; n++) {
        var i = order[n], c = C[i], isF = forced.indexOf(i) > -1; if (out.length >= lim && !isF) break;
        var cx = sx(lx(c)), cy = sy(share(c)), w = c.name.length * 6.2 + 3, opts = [[cx + RAD + 2, cy + 3.4, 'start'], [cx - RAD - 2, cy + 3.4, 'end'], [cx, cy - RAD - 3, 'middle'], [cx, cy + RAD + 10, 'middle'], [cx + RAD, cy - RAD - 2, 'start'], [cx - RAD, cy - RAD - 2, 'end'], [cx + RAD, cy + RAD + 10, 'start'], [cx - RAD, cy + RAD + 10, 'end']];
        for (var o = 0; o < opts.length; o++) {
          var x = opts[o][0], y = opts[o][1], an = opts[o][2], x0 = an === 'start' ? x : an === 'end' ? x - w : x - w / 2, bb = { x0: x0, x1: x0 + w, y0: y - 8.5, y1: y + 2 };
          if (bb.x0 < Lm - 4 || bb.x1 > W - 1 || bb.y0 < 0 || bb.y1 > H - Bm + 2) continue;
          if (placed.some(function (q) { return !(bb.x1 < q.x0 || bb.x0 > q.x1 || bb.y1 < q.y0 || bb.y0 > q.y1); })) continue;
          if (!isF && dots.some(function (d) { return d.i !== i && bb.x0 < d.x + d.r && bb.x1 > d.x - d.r && bb.y0 < d.y + d.r && bb.y1 > d.y - d.r; })) continue;
          placed.push(bb); out.push({ i: i, x: x, y: y, an: an }); break;
        }
      }
      return out;
    }
    function drawSc() {
      var el = document.getElementById('cSc'); scales();
      var xt = [.1, .3, 1, 3, 10, 30, 100, 300, 1000, 3000].filter(function (v) { var l = Math.log10(v); return l >= xd[0] && l <= xd[1] && (/^(1|3)/.test(String(v).replace('.', '')) && (String(v).replace('.', '')[0] === '1' || (xd[1] - xd[0]) < 3.2)); });
      var yt = []; for (var v = yd[0]; v <= yd[1] + .01; v += yd.step) yt.push(v);
      var g = xt.map(function (v) { var x = sx(Math.log10(v)); return '<line class="gl" x1="' + x + '" x2="' + x + '" y1="' + Tm + '" y2="' + (H - Bm) + '"/><text class="tk" x="' + x + '" y="' + (H - Bm + 13) + '" text-anchor="middle">' + (v >= 1000 ? (v / 1000) + 'k' : v) + '</text>'; }).join('') +
        yt.map(function (v) { return '<line class="gl" x1="' + Lm + '" x2="' + (W - Rm) + '" y1="' + sy(v) + '" y2="' + sy(v) + '"/><text class="tk" x="' + (Lm - 5) + '" y="' + (sy(v) + 3) + '" text-anchor="end">' + v + '</text>'; }).join('');
      var ord = C.slice().sort(function (a, b) { return b.pop - a.pop; });
      var dots = ord.map(function (c) { return '<circle class="dt" data-i="' + c.i + '" cx="' + sx(lx(c)).toFixed(1) + '" cy="' + sy(share(c)).toFixed(1) + '" r="' + RAD + '" style="fill:var(--p' + c.pi + ')"><title>' + esc(c.name) + ': ' + share(c).toFixed(1) + '% ' + esc(sel) + ', ' + fmt(Math.round(c.dens)) + ' people per km²</title></circle>'; }).join('');
      var hits = ord.map(function (c) { return '<circle class="hit" data-i="' + c.i + '" cx="' + sx(lx(c)).toFixed(1) + '" cy="' + sy(share(c)).toFixed(1) + '" r="' + Math.max(RAD, 9) + '"/>'; }).join('');
      var line = fit ? '<line class="fit" x1="' + sx(xd[0] + .04) + '" y1="' + sy(fit.a + fit.b * (xd[0] + .04)) + '" x2="' + sx(xd[1] - .04) + '" y2="' + sy(fit.a + fit.b * (xd[1] - .04)) + '"/>' : '';
      var note = small ? 'Seven seats are too few for a trend line, so none is drawn. Tap any dot to see which electorate it is.' : (Math.abs(fit.r) < .2 ? 'Density says little about ' + esc(sel) + ' support' : 'Denser electorates give <b>' + esc(sel) + '</b> ' + (fit.r > 0 ? 'more' : 'less') + ' of the party vote') + ' (<b>r = ' + (fit.r < 0 ? '−' : '') + Math.abs(fit.r).toFixed(2) + '</b>, weighted by party votes; the line shows the fit). This compares electorates, not individual voters.';
      el.innerHTML = '<h3>Density vs the vote</h3><p class="cs">Each dot is an electorate, coloured by who won it. Pick a party for the vertical axis: its share of the party vote, which decides seats under MMP.</p>' +
        '<div class="scp" role="group" aria-label="Party on the vertical axis">' + PK.map(function (p) { return '<button type="button" data-p="' + esc(p.k) + '" aria-pressed="' + (p.k === sel) + '"><i class="dot" style="background:' + pkCol(p) + '"></i>' + esc(p.s) + '</button>'; }).join('') + '</div>' +
        '<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="Scatter of people per square kilometre against ' + esc(sel) + ' share of the party vote, by electorate">' + g + line + dots + '<g id="scLb"></g>' + hits +
        '<text class="ax" x="' + (Lm + W - Rm) / 2 + '" y="' + (H - 5) + '" text-anchor="middle">People per km² · log scale</text><text class="ax" transform="translate(9 ' + (Tm + H - Bm) / 2 + ') rotate(-90)" text-anchor="middle">' + esc(sel) + ' % of party vote</text></svg>' +
        '<p class="nt">' + note + '</p>';
      el.querySelector('svg').addEventListener('click', function (e) { var h = e.target.closest('[data-i]'); if (h) act(+h.dataset.i, false); });
      el.querySelector('.scp').addEventListener('click', function (e) { var b = e.target.closest('button'); if (b && b.dataset.p !== sel) { sel = b.dataset.p; drawSc(); chartSel(selected); } });
    }
    var rk = C.slice().sort(function (a, b) { return b.gr - a.gr; }), lg = rk.map(function (c) { return Math.log2(c.gr); });
    var lo = Math.floor(Math.min.apply(null, lg) - .6), hi = Math.ceil(Math.max.apply(null, lg) + .6), span = hi - lo, cp = -lo / span * 100, pos = function (v) { return (Math.log2(v) - lo) / span * 100; };
    var rkTxt = function (r) { return r >= 1 ? 'grows ' + (r >= 10 ? r.toFixed(0) : r.toFixed(1)) + '×' : 'shrinks ' + (1 / r >= 10 ? (1 / r).toFixed(0) : (1 / r).toFixed(1)) + '×'; };
    function drawRk() {
      var el = document.getElementById('cRk'), tk = (span > 10 ? [[.001, '0.001×'], [.01, '0.01×'], [.1, '0.1×'], [1, '1×'], [10, '10×'], [100, '100×']] : [[.1, '0.1×'], [.25, '¼×'], [.5, '½×'], [1, '1×'], [2, '2×'], [4, '4×'], [10, '10×']]).filter(function (t) { return (pos(t[0]) > 4 && pos(t[0]) < 96) || t[0] === 1; });
      el.innerHTML = '<h3>All ' + C.length + ' ' + esc(META.unitsLabel) + ', ranked</h3><p class="cs">An electorate’s share of the people divided by its share of the land. Bars right of the line gain size when resized to its people; bars left shrink. ' + (small ? '' : 'General electorates are drawn with near-equal populations, so this ranking mostly reflects land area.') + '</p>' +
        '<div class="rk-h"><span>◀ shrinks</span><span>grows ▶</span></div><div class="rk-ax">' + tk.map(function (t) { return '<span style="left:' + pos(t[0]) + '%">' + t[1] + '</span>'; }).join('') + '</div>' +
        '<div class="rk" id="rk" style="--c:' + cp + '%">' + rk.map(function (c, n) { var l = lg[n], w = Math.abs(l) / span * 100, left = l >= 0 ? cp : cp - w;
          return '<button type="button" class="rk-row" data-i="' + c.i + '" aria-label="' + esc(c.name) + ', ' + rkTxt(c.gr) + ' when resized to its people"><span class="rn">' + esc(c.name) + '</span><span class="rt"><i class="br" style="left:' + left + '%;width:' + Math.max(w, .5) + '%;background:var(--p' + c.pi + ')"></i><span class="vl"></span></span></button>'; }).join('') + '</div>';
      el.querySelector('#rk').addEventListener('click', function (e) { var b = e.target.closest('.rk-row'); if (b) act(+b.dataset.i, false); });
    }
    function chartSel(i) {
      var sc = document.getElementById('cSc'); sc.classList.toggle('has', i != null);
      sc.querySelectorAll('.dt').forEach(function (d) { d.classList.toggle('on', +d.dataset.i === i); });
      var lb = sc.querySelector('#scLb'); if (lb) lb.innerHTML = labelSet().map(function (l) { return '<text class="lb" x="' + l.x.toFixed(1) + '" y="' + l.y.toFixed(1) + '" text-anchor="' + l.an + '">' + esc(C[l.i].name) + '</text>'; }).join('');
      var rows = document.getElementById('rk').children;
      rk.forEach(function (c, n) { var r = rows[n], on = c.i === i; r.setAttribute('aria-current', on); var v = r.querySelector('.vl');
        if (on) { var l = lg[n], w = Math.abs(l) / span * 100; v.textContent = '#' + (n + 1) + ' · ' + rkTxt(c.gr); v.style.left = v.style.right = ''; if (l >= 0 && cp + w > 58) { v.style.right = (100 - (cp - 1)) + '%'; v.style.left = 'auto'; } else if (l >= 0) { v.style.left = (cp + w + 1.5) + '%'; v.style.right = 'auto'; } else if (cp - w > 40) { v.style.right = (100 - (cp - w - 1.5)) + '%'; v.style.left = 'auto'; } else { v.style.left = (cp + 1.5) + '%'; v.style.right = 'auto'; } } else v.textContent = ''; });
    }
    drawSc(); drawRk(); chartSel(null); window.__chartSel = chartSel;
  })();
