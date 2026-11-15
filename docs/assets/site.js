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
  var TESTS = { 1: 'test_same_key_refunds_once', 2: 'test_refund_response_is_stable', 3: 'test_refund_amount_validated' };
  var KEPT = 'test_refund_response_is_stable';
  var STILL = ' still passes with the change undone.';
  var EITHER = 'It would pass whether or not the change exists.';
  // In the example only test 2 still passes. A miss cue is about test 2 when it was
  // left out, else about the first picked test that does not still pass.
  var CUES = {
    2: ['Its only assertion is at ', 'tests/test_refunds.py:41', '.'],
    1: ['It fails at ', 'tests/test_refunds.py:29', '.'],
    3: ['With the change undone it stops at ', 'tests/test_refunds.py:52', ' with an error, not on an assertion.']
  };

  // The chosen answer: ['none'], ['dk'], or test numbers, ascending.
  var chosen = [], locked = false, sure = null;

  // The picks are buttons, not radios: an arrow key in a radio group checks the
  // next radio, which would lock an answer the person did not choose. The numbers
  // toggle, None and Don't know clear them, and only Lock locks.
  function picks() { return $$('#try .pk'); }
  function sures() { return $$('#try input[name="sure"]'); }
  function exclusive(p) { return p === 'none' || p === 'dk'; }
  function only() { return chosen.length === 1 && exclusive(chosen[0]) ? chosen[0] : null; }

  function show(state) {
    demo.querySelectorAll('[data-v]').forEach(function (e) {
      e.hidden = e.getAttribute('data-v').split(' ').indexOf(state) < 0;
    });
  }

  function matched() { return chosen.length === 1 && chosen[0] === '2'; }

  function chipWord() {
    if (matched()) return 'Matched';
    return only() === 'dk' ? 'Not scored' : 'Did not match';
  }

  function and(items) {
    if (items.length < 2) return items.join('');
    return items.slice(0, -1).join(', ') + ' and ' + items[items.length - 1];
  }

  function saidText() {
    if (only() === 'dk') return "Don't know.";
    if (only() === 'none') return 'None.';
    return and(chosen) + ', ' + and(chosen.map(function (n) { return TESTS[n]; })) + '.';
  }

  function fillCue() {
    var wrong = chosen.filter(function (n) { return n !== '2' && !exclusive(n); });
    var c = CUES[chosen.indexOf('2') < 0 ? 2 : wrong[0]];
    var dd = $('#cue');
    dd.textContent = '';
    dd.appendChild(document.createTextNode(c[0]));
    dd.appendChild(el('span', 'mono', c[1]));
    dd.appendChild(document.createTextNode(c[2]));
  }

  function fillResult() {
    var ok = matched(), dk = only() === 'dk', word = chipWord();
    var chip = $('#chip');
    chip.className = 'chip' + (ok ? '' : (dk ? ' dash' : ' miss'));
    chip.innerHTML = ok ? TICK : '';
    chip.appendChild(document.createTextNode(word));
    $('#res').setAttribute('aria-label', word + '. Revert test');
    $('#dkr').hidden = !dk;
    $('#said').textContent = saidText() + (sure && !dk ? ' ' + sure + '.' : '');
    var what = $('#what');
    what.textContent = '';
    if (ok) {
      what.textContent = 'It still passes with the change undone. ' + EITHER;
    } else {
      what.appendChild(el('span', 'mono', KEPT));
      what.appendChild(document.createTextNode(STILL + (dk ? ' ' + EITHER : '')));
    }
    $('#cuerow').hidden = ok;
    if (!ok) fillCue();
  }

  function draw() {
    picks().forEach(function (b) {
      b.setAttribute('aria-pressed', chosen.indexOf(b.getAttribute('data-p')) < 0 ? 'false' : 'true');
      b.disabled = locked;
    });
    $('#lockbtn').disabled = locked || !chosen.length;
  }

  function ask() {
    chosen = []; locked = false; sure = null;
    sures().forEach(function (r) { r.checked = false; });
    draw();
    show('ask');
  }

  function focusFirstPick() {
    var first = picks()[0];
    if (first) first.focus();
  }

  function toggle(button) {
    var p = button.getAttribute('data-p');
    var was = chosen.indexOf(p) >= 0;
    if (exclusive(p) || only()) chosen = [];
    else chosen = chosen.filter(function (n) { return n !== p; });
    if (!was) chosen.push(p);
    chosen.sort();
    draw();
  }

  function lock() {
    if (!chosen.length || locked) return;
    locked = true; sure = null;
    draw();
    sures().forEach(function (r) { r.checked = false; });
    var dk = only() === 'dk';
    $$('#surerow .sp, #sl').forEach(function (e) { e.hidden = dk; });
    show('locked');
    $('#undo').focus();
    say('Locked.');
  }

  if (demo) {
    picks().forEach(function (b) {
      b.addEventListener('click', function () { if (!locked) toggle(b); });
    });
    $('#lockbtn').addEventListener('click', lock);
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
