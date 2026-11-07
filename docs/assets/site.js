(function () {
  'use strict';

  var CMD = '/plugin marketplace add 0xfauzi/explain-pr\n/plugin install learning-while-building@learning-while-building';
  var FILLS = ['f1', 'f2', 'f3'];
  var LEVEL_NAMES = ['not yet', 'with help', 'without help', 'new situation'];

  var CODE = ['def backoff(attempt):', '    return 0.5 * 2 ** attempt', '', 'def charge(order):', '    for attempt in range(3):', '        try:',
    '            return gateway.charge(', '                order.card,', '                order.amount,', '                timeout=0.8,', '            )',
    '        except gateway.Timeout:', '            sleep(backoff(attempt))', '    raise ChargeFailed(order.id)'];

  var EXAMPLES = {
    comp: {
      opts: ['No order and no email', 'An order, but no confirmation email', 'An order and two emails'], right: 1,
      why: 'The save is complete, so the order exists. The message was not sent, so the worker does not send an email. To prevent this, save the order and the message in one database transaction. Then a separate process sends the message. Engineers call this an outbox.',
      area: 'Architecture and design'
    },
    code: {
      opts: ['About 2.4 seconds', 'About 5.9 seconds', 'It tries again until it works'], right: 1,
      why: 'Three attempts of 0.8 seconds take 2.4 seconds. The code also waits after each attempt, and after the last attempt too: 0.5 + 1 + 2 seconds. The total is 5.9 seconds. The last wait of 2 seconds has no purpose. See lines 10 and 13.',
      area: 'Reliability and operations'
    }
  };

  // Example levels on the skill's scale: 0 not yet, 1 with help, 2 without help (recalls), 3 new situation (transfers).
  var DIMS = [
    ['Architecture and design', 0, 2], ['Domain model', 1, 3], ['Correctness and testing', 0, 2], ['Debugging and diagnosis', 0, 2],
    ['Performance', 0, 1], ['Reliability and operations', 0, 2], ['Security', 0, 0], ['Data and storage', 1, 3],
    ['Concurrency', 1, 3], ['Reading code', 0, 2]
  ];

  var SVG_RIGHT = '<svg role="img" aria-label="Correct" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#16161A" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 12.5l5 5L19.5 7"></path></svg>';
  var SVG_WRONG = '<svg role="img" aria-label="Your answer, wrong" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#C2410C" stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"></path></svg>';

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

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

  /* ---------- record rows ---------- */

  function setRow(row, lv) {
    var segs = row.querySelectorAll('.seg');
    for (var j = 0; j < 3; j++) segs[j].className = lv >= j + 1 ? 'seg lit ' + FILLS[j] : 'seg';
    var label = row.querySelector('.lv');
    label.className = 'mono lv' + (lv === 0 ? ' ink0' : (lv === 3 ? ' ink3' : ''));
    label.textContent = LEVEL_NAMES[lv];
  }

  function buildRow(name, lv, delay) {
    var row = el('div', 'row');
    row.appendChild(el('span', 'nm', name));
    var segs = el('div', 'segs');
    segs.setAttribute('aria-hidden', 'true');
    for (var j = 0; j < 3; j++) {
      var s = el('span', 'seg');
      if (delay != null) s.style.transitionDelay = (delay + j * 0.12).toFixed(2) + 's';
      segs.appendChild(s);
    }
    row.appendChild(segs);
    row.appendChild(el('span', 'mono lv'));
    setRow(row, lv);
    return row;
  }

  var dimsHost = document.getElementById('dims');
  var wk = document.getElementById('wk'), mo = document.getElementById('mo');
  var alone = document.getElementById('alone');
  var growTimer;

  function showRecord(later) {
    var rows = dimsHost.children, n = 0;
    DIMS.forEach(function (d, i) {
      var lv = later ? d[2] : d[1];
      if (lv >= 2) n++;
      setRow(rows[i], lv);
    });
    alone.textContent = String(n);
    wk.className = later ? 'tg' : 'tg on';
    mo.className = later ? 'tg on' : 'tg';
    wk.setAttribute('aria-pressed', String(!later));
    mo.setAttribute('aria-pressed', String(later));
  }

  if (dimsHost) {
    dimsHost.textContent = '';
    DIMS.forEach(function (d, i) { dimsHost.appendChild(buildRow(d[0], d[1], i * 0.07)); });
    showRecord(false);
    growTimer = setTimeout(function () { showRecord(true); }, 1400);
    wk.addEventListener('click', function () { clearTimeout(growTimer); showRecord(false); });
    mo.addEventListener('click', function () { clearTimeout(growTimer); showRecord(true); });
  }

  /* ---------- copy buttons ---------- */

  var copyButtons = document.querySelectorAll('[data-copy]');
  var copyTimer;
  function setCopied(on) {
    for (var i = 0; i < copyButtons.length; i++) {
      // Keep the width of the longer label, so the buttons next to it do not move.
      copyButtons[i].style.minWidth = on ? copyButtons[i].offsetWidth + 'px' : '';
      copyButtons[i].textContent = on ? 'Copied' : copyButtons[i].getAttribute('data-copy');
    }
  }
  for (var ci = 0; ci < copyButtons.length; ci++) {
    copyButtons[ci].addEventListener('click', function () {
      try { if (navigator.clipboard) navigator.clipboard.writeText(CMD).catch(function () {}); } catch (e) {}
      setCopied(true);
      clearTimeout(copyTimer);
      copyTimer = setTimeout(function () { setCopied(false); }, 2000);
    });
  }

  /* ---------- question ---------- */

  var tabs = document.querySelectorAll('[role="tab"]');
  var panels = {};
  var state = { ex: 'comp', choice: null, conf: null, locked: false, grown: false, status: '' };
  var deltaTimer;

  function renderCode(pre) {
    pre.setAttribute('aria-label', CODE.join('\n'));
    pre.textContent = '';
    CODE.forEach(function (text, i) {
      var line = el('div', 'ln');
      line.setAttribute('aria-hidden', 'true');
      line.appendChild(el('i', null, String(i + 1)));
      line.appendChild(document.createTextNode(text));
      pre.appendChild(line);
    });
  }

  function renderOpts(host, ex) {
    host.textContent = '';
    ex.opts.forEach(function (text, i) {
      var b = el('button', 'opt');
      b.type = 'button';
      b.appendChild(el('span', 'k', 'ABC'[i]));
      b.firstChild.appendChild(el('span', 'vh', ', '));
      b.appendChild(el('span', null, text));
      b.appendChild(el('span', 'mk'));
      b.addEventListener('click', function () {
        if (!state.locked) { state.choice = i; state.status = ''; render(); }
      });
      host.appendChild(b);
    });
  }

  function setupPanel(panel) {
    var key = panel.getAttribute('data-ex'), ex = EXAMPLES[key];
    var side = panel.querySelector('.qside');
    renderOpts(side.querySelector('.opts'), ex);
    side.appendChild(document.getElementById('tpl-controls').content.cloneNode(true));
    var code = panel.querySelector('.code');
    if (code) renderCode(code);
    side.querySelectorAll('[data-conf]').forEach(function (b) {
      b.addEventListener('click', function () {
        if (!state.locked) { state.conf = b.getAttribute('data-conf'); state.status = ''; render(); }
      });
    });
    side.querySelector('[data-act="lock"]').addEventListener('click', lock);
    side.querySelector('[data-act="reset"]').addEventListener('click', function () {
      clearTimeout(deltaTimer);
      fresh();
      render();
      var first = panels[state.ex].querySelector('.opt');
      if (first) first.focus();
    });
    panels[key] = panel;
  }

  function fresh() {
    state.choice = null; state.conf = null; state.locked = false; state.grown = false; state.status = '';
  }

  function lock() {
    if (state.conf !== 'dk' && (state.choice === null || state.conf === null)) {
      state.status = 'Select an answer and how sure you are.';
      render();
      return;
    }
    state.locked = true; state.grown = false;
    render();
    var result = panels[state.ex].querySelector('.result');
    result.querySelector('.verdict').focus({ preventScroll: true });
    var still = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    result.scrollIntoView({ block: 'nearest', behavior: still ? 'auto' : 'smooth' });
    clearTimeout(deltaTimer);
    deltaTimer = setTimeout(function () { state.grown = true; render(); }, 900);
  }

  function render() {
    var s = state, ex = EXAMPLES[s.ex], panel = panels[s.ex], dk = s.conf === 'dk';
    var correct = !dk && s.choice === ex.right;

    Object.keys(panels).forEach(function (k) { panels[k].hidden = k !== s.ex; });
    for (var t = 0; t < tabs.length; t++) {
      var on = tabs[t].getAttribute('data-ex') === s.ex;
      tabs[t].className = on ? 'tab on' : 'tab';
      tabs[t].setAttribute('aria-selected', String(on));
      tabs[t].tabIndex = on ? 0 : -1;
    }

    panel.querySelectorAll('.opt').forEach(function (b, i) {
      var cls = 'opt';
      if (s.locked) cls += i === ex.right ? ' right' : (i === s.choice ? ' wrong' : ' dim');
      else if (s.choice === i) cls += ' on';
      b.className = cls;
      b.disabled = s.locked;
      b.setAttribute('aria-pressed', String(s.choice === i));
      var right = s.locked && i === ex.right, wrong = s.locked && i === s.choice && i !== ex.right;
      b.querySelector('.mk').innerHTML = right ? SVG_RIGHT : (wrong ? SVG_WRONG : '');
    });
    panel.querySelectorAll('.sure').forEach(function (b) {
      var picked = s.conf === b.getAttribute('data-conf');
      b.className = picked ? 'sure on' : 'sure';
      b.setAttribute('aria-pressed', String(picked));
      b.disabled = s.locked;
    });
    panel.querySelector('.lockrow').hidden = s.locked;
    panel.querySelector('.status').textContent = s.status;

    var flow = panel.querySelector('.flow');
    if (flow) {
      flow.className = s.locked ? 'flow stop' : 'flow';
      flow.querySelector('.cut').hidden = !s.locked;
      panel.querySelector('.flownote').textContent = s.locked
        ? 'The API stops here, after step 1 and before step 2.'
        : 'The orange dot shows the normal path of one order.';
    }
    var marked = s.locked && s.ex === 'code' ? [2, 10, 13] : [];
    panel.querySelectorAll('.ln').forEach(function (line, i) {
      line.className = marked.indexOf(i + 1) >= 0 ? 'ln hl' : 'ln';
    });

    var result = panel.querySelector('.result');
    result.hidden = !s.locked;
    if (!s.locked) return;
    var verdict = result.querySelector('.verdict');
    if (dk) { verdict.textContent = 'That is OK. This is the answer.'; verdict.className = 'verdict ok'; }
    else if (correct) { verdict.textContent = 'Correct.'; verdict.className = 'verdict ok'; }
    else { verdict.textContent = 'No.'; verdict.className = 'verdict'; }
    result.querySelector('.why').textContent = ex.why;
    result.querySelector('.belief').hidden = !(!dk && !correct && s.conf === 'high');
    var row = result.querySelector('.delta .row');
    row.querySelector('.nm').textContent = ex.area;
    setRow(row, s.grown ? (correct ? 2 : 1) : 1);
    result.querySelector('.dnote').textContent = correct
      ? 'Without help for the first time. The next question about this idea comes in 3 days.'
      : 'No change. The question comes back tomorrow.';
  }

  function pick(key) {
    clearTimeout(deltaTimer);
    state.ex = key;
    fresh();
    render();
  }

  document.querySelectorAll('.qpanel').forEach(setupPanel);
  if (panels.comp) {
    Object.keys(panels).forEach(function (k) {
      panels[k].setAttribute('role', 'tabpanel');
      panels[k].setAttribute('aria-labelledby', 'tab-' + k);
    });
    for (var ti = 0; ti < tabs.length; ti++) {
      tabs[ti].addEventListener('click', function () { pick(this.getAttribute('data-ex')); });
      tabs[ti].addEventListener('keydown', function (e) {
        var next = { Home: 'comp', End: 'code' }[e.key];
        if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') next = this.getAttribute('data-ex') === 'comp' ? 'code' : 'comp';
        if (!next) return;
        pick(next);
        document.getElementById('tab-' + next).focus();
        e.preventDefault();
      });
    }
    render();
  }

  /* ---------- background fields ---------- */

  renderField(document.getElementById('field'), 352, 3);
  renderField(document.getElementById('field2'), 112, 41);
})();
