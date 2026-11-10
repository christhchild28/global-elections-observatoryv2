/* Briefing: mounts into a shadow root so its styles cannot touch the map page. */
(function () {
  var host = document.getElementById('intro-host'), tpl = document.getElementById('intro-tpl');
  if (!host || !tpl) return;
  var R = host.attachShadow({ mode: 'open' }); R.appendChild(tpl.content.cloneNode(true)); host.hidden = false; host.style.display = 'block';
  var sk = R.getElementById('skip');
  if (sk) sk.addEventListener('click', function (e) { e.preventDefault(); var m = document.getElementById('mapstart'); if (m) m.scrollIntoView({ behavior: 'smooth' }); });
  var hw = R.getElementById('hw'); if (!hw) return;
  var seats = [].slice.call(hw.querySelectorAll('.s')), cn = R.getElementById('cn'), cl = R.getElementById('cl'), lgs = [].slice.call(R.querySelectorAll('.lg')), sel = -1;
  var total = seats.length;
  lgs.forEach(function (b, i) {
    b.setAttribute('aria-pressed', 'false');
    b.addEventListener('click', function () {
      sel = sel === i ? -1 : i;
      lgs.forEach(function (x, j) { x.setAttribute('aria-pressed', j === sel ? 'true' : 'false'); });
      hw.classList.toggle('f', sel > -1);
      var n = 0; seats.forEach(function (s) { var on = sel < 0 || +s.getAttribute('data-p') === sel; s.classList.toggle('on', on); if (on && sel > -1) n++; });
      cn.textContent = sel < 0 ? total : n; cl.textContent = sel < 0 ? 'seats' : 'seats · ' + lgs[sel].textContent.replace(/\s*\d+$/, '').trim();
    });
  });
})();
