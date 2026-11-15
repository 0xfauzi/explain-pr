(function () {
  'use strict';

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function $(sel) { return document.querySelector(sel); }
  function $$(sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); }

  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- background field ---------- */

  // A field of faint cells. About one in six slowly lights up and fades, each on its own cycle.
  function renderField(host, n, seed) {
    if (!host) return;
    var frag = document.createDocumentFragment();
    for (var i = 0; i < n; i++) {
      var x = Math.sin((i + seed) * 12.9898) * 43758.5453, r = x - Math.floor(x);
      var y = Math.sin((i + seed) * 78.233) * 12345.678, q = y - Math.floor(y);
      var c = el('span', 'fc');
      if (r <= 0.17) {
        c.className = 'fc ' + (r < 0.06 ? 'g3' : (r < 0.11 ? 'g2' : 'g1'));
        c.style.setProperty('--d', (8 + q * 7).toFixed(1) + 's');
        c.style.animationDelay = (-q * 14).toFixed(1) + 's';
      }
      frag.appendChild(c);
    }
    host.appendChild(frag);
  }

  /* ---------- copy buttons ---------- */

  function copyText(text) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).catch(function () {});
        return;
      }
    } catch (e) { /* fall through */ }
    var area = el('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.style.position = 'fixed';
    area.style.opacity = '0';
    document.body.appendChild(area);
    area.select();
    try { document.execCommand('copy'); } catch (e) { /* nothing more to try */ }
    document.body.removeChild(area);
  }

  $$('[data-copy]').forEach(function (button) {
    var timer;
    button.addEventListener('click', function () {
      var from = button.getAttribute('data-copy-from');
      var pre = from ? $('[data-cmd="' + from + '"]') : button.parentNode.querySelector('pre');
      if (pre) copyText(pre.textContent);
      // Keep the width of the longer label, so the buttons next to it do not move.
      button.style.minWidth = button.offsetWidth + 'px';
      button.textContent = 'Copied';
      clearTimeout(timer);
      timer = setTimeout(function () {
        button.textContent = button.getAttribute('data-copy');
        button.style.minWidth = '';
      }, 2000);
    });
  });

  /* ---------- the Revert test card: ask, locked, skipped, result ---------- */

  var demo = $('#try');
  var live = $('#live');

  function say(text) {
    if (!live) return;
    live.textContent = '';
    setTimeout(function () { live.textContent = text; }, 40);
  }

  var TICK = '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2 6.5l2.6 2.6L10 3.4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var NAMES = {
    1: '1, test_same_key_refunds_once', 2: '2, test_refund_response_is_stable',
    3: '3, test_refund_amount_validated', none: 'None', dk: "Don't know"
  };
  var KEPT = 'test_refund_response_is_stable';
  var STILL = ' still passes with the change undone.';
  var EITHER = 'It would pass whether or not the change exists.';

  var pick = null, sure = null;

  // The picks are buttons, not radios: an arrow key in a radio group checks the
  // next radio, which would lock an answer the person did not choose.
  function picks() { return $$('#try .pk'); }
  function sures() { return $$('#try input[name="sure"]'); }

  function show(state) {
    demo.querySelectorAll('[data-v]').forEach(function (e) {
      e.hidden = e.getAttribute('data-v').split(' ').indexOf(state) < 0;
    });
  }

  function chipWord() {
    if (pick === '2') return 'Matched';
    return pick === 'dk' ? 'Not scored' : 'Did not match';
  }

  function fillResult() {
    var ok = pick === '2', dk = pick === 'dk', word = chipWord();
    var chip = $('#chip');
    chip.className = 'chip' + (ok ? '' : (dk ? ' dash' : ' miss'));
    chip.innerHTML = ok ? TICK : '';
    chip.appendChild(document.createTextNode(word));
    $('#res').setAttribute('aria-label', word + '. Revert test');
    $('#dkr').hidden = !dk;
    $('#said').textContent = NAMES[pick] + '.' + (sure && !dk ? ' ' + sure + '.' : '');
    var what = $('#what');
    what.textContent = '';
    if (ok) {
      what.textContent = 'It still passes with the change undone. ' + EITHER;
    } else {
      what.appendChild(el('span', 'mono', KEPT));
      what.appendChild(document.createTextNode(STILL + (dk ? ' ' + EITHER : '')));
    }
    $('#cuerow').hidden = ok;
  }

  function ask() {
    pick = null; sure = null;
    picks().forEach(function (b) { b.setAttribute('aria-pressed', 'false'); b.disabled = false; });
    sures().forEach(function (r) { r.checked = false; });
    show('ask');
  }

  function focusFirstPick() {
    var first = picks()[0];
    if (first) first.focus();
  }

  function lock(button) {
    pick = button.getAttribute('data-p'); sure = null;
    // The chosen pick stays enabled so focus stays on it. The others are disabled.
    picks().forEach(function (b) {
      var chosen = b === button;
      b.setAttribute('aria-pressed', chosen ? 'true' : 'false');
      b.disabled = !chosen;
    });
    sures().forEach(function (r) { r.checked = false; });
    var dk = pick === 'dk';
    $$('#surerow .sp, #sl').forEach(function (e) { e.hidden = dk; });
    show('locked');
    say('Locked.');
  }

  if (demo) {
    picks().forEach(function (b) {
      b.addEventListener('click', function () { if (pick === null) lock(b); });
    });
    sures().forEach(function (r) {
      r.addEventListener('change', function () { if (r.checked) sure = r.value; });
    });
    $('#undo').addEventListener('click', function () { ask(); focusFirstPick(); say('Undone.'); });
    $('#skip').addEventListener('click', function () {
      show('skipped');
      $('#unskip').focus();
      say('Skipped.');
    });
    $('#unskip').addEventListener('click', function () { ask(); focusFirstPick(); say('Undone.'); });
    $('#reveal').addEventListener('click', function () {
      fillResult();
      show('result');
      // Focus carries the result: the section's name starts with the chip word and
      // its rows are read from there, so the live region says nothing here.
      var res = $('#res');
      res.focus({ preventScroll: true });
      res.scrollIntoView({ block: 'nearest', behavior: still ? 'auto' : 'smooth' });
    });
    $('#again').addEventListener('click', function () {
      $('#res').querySelector('details').open = false;
      ask();
      focusFirstPick();
    });
    $('#card').addEventListener('submit', function (e) { e.preventDefault(); });
    ask();
  }

  /* ---------- background fields ---------- */

  renderField(document.getElementById('field'), 352, 3);
  renderField(document.getElementById('field2'), 112, 41);
})();
