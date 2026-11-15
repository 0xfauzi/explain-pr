/* The Room page. It renders only the JSON the Firsthand engine returns (the Room
   HTTP API) and decides nothing about results: a result is drawn when the API
   gives one. Every string from the API is set with textContent. No markup is
   ever built from text. Nothing is loaded from anywhere but this server. */
(function () {
  'use strict';

  var D = document;
  var NO_SESSION = 'This page needs a session. Run: firsthand room';
  var LOST = 'The Room cannot reach Firsthand on this computer. Start it with: firsthand room';
  var INTERNAL = 'Something went wrong inside Firsthand. Nothing was changed.';
  var DIAL = [
    ['off', 'Off', 'Nothing is asked, run or recorded.'],
    ['notes', 'Notes only', 'No questions. Checks run and post notes.'],
    ['standard', 'Standard', 'Questions within the daily limit.'],
    ['deep', 'Deep', 'As Standard. You may also write a line of code on some questions.']
  ];

  var S = { token: null, inbox: null, view: null, route: null, lost: false, es: null, draft: null };

  /* ------------------------------------------------------------ small helpers */

  function $(id) { return D.getElementById(id); }

  function h(tag, props, kids) {
    var el = D.createElement(tag);
    var k;
    props = props || {};
    for (k in props) {
      if (!Object.prototype.hasOwnProperty.call(props, k)) continue;
      var v = props[k];
      if (v === null || v === undefined || v === false) continue;
      if (k === 'class') el.className = v;
      else if (k === 'text') el.textContent = v;
      else if (k.slice(0, 2) === 'on') el.addEventListener(k.slice(2), v);
      else if (k === 'checked' || k === 'disabled' || k === 'open' || k === 'value') el[k] = v;
      else el.setAttribute(k, v === true ? '' : String(v));
    }
    add(el, kids);
    return el;
  }

  function add(el, kids) {
    if (kids === null || kids === undefined) return;
    if (!Array.isArray(kids)) kids = [kids];
    kids.forEach(function (c) {
      if (c === null || c === undefined || c === false) return;
      el.appendChild(typeof c === 'string' ? D.createTextNode(c) : c);
    });
  }

  function clear(el) { while (el.firstChild) el.removeChild(el.firstChild); }

  function say(text) {
    var live = $('live');
    if (!live || !text) return;
    live.textContent = '';
    setTimeout(function () { live.textContent = text; }, 40);
  }

  function projectParam() {
    var p = new URLSearchParams(location.search).get('project');
    return p || null;
  }

  function withProject(path) {
    var p = projectParam();
    if (!p) return path;
    return path + (path.indexOf('?') < 0 ? '?' : '&') + 'project=' + encodeURIComponent(p);
  }

  function chip(code, label) {
    var cls = 'chip';
    if (code === 'matched') cls += ' ok';
    else if (code === 'did_not_match') cls += ' miss';
    else cls += ' dash';
    return h('span', { class: cls, text: label });
  }

  function rows(pairs) {
    var dl = h('dl', { class: 'rw' });
    pairs.forEach(function (p) {
      if (p[1] === null || p[1] === undefined || p[1] === '') return;
      dl.appendChild(h('div', null, [h('dt', { text: p[0] }), h('dd', null, p[1])]));
    });
    return dl;
  }

  /* ------------------------------------------------------------ the API */

  function api(method, path, body) {
    var opts = { method: method, credentials: 'same-origin', headers: {} };
    if (method === 'POST') {
      opts.headers['Content-Type'] = 'application/json';
      opts.headers['X-Firsthand-Token'] = S.token || '';
      opts.body = JSON.stringify(body || {});
    }
    return fetch(path, opts).then(function (r) {
      return r.json().catch(function () { return null; }).then(function (data) {
        if (r.ok) return data;
        var e = (data && data.error) || { code: 'internal', message: INTERNAL };
        var err = new Error(e.message);
        err.code = e.code;
        err.status = r.status;
        if (e.code === 'no_session') noSession(e.message);
        throw err;
      });
    }, function () {
      var err = new Error(LOST);
      err.code = 'unreachable';
      setLost(true);
      throw err;
    });
  }

  /* ------------------------------------------------------------ shell */

  function route() {
    var p = location.pathname;
    var m = /^\/([qr])\/([A-Za-z0-9_-]{1,64})$/.exec(p);
    if (m) return { name: 'question', ref: m[2] };
    if (p === '/journal' || p === '/skills' || p === '/settings') return { name: p.slice(1) };
    return { name: 'inbox' };
  }

  function markTabs(name) {
    Array.prototype.forEach.call(D.querySelectorAll('[data-tab]'), function (a) {
      a.setAttribute('href', withProject(a.getAttribute('href').split('?')[0]));
      if (a.getAttribute('data-tab') === name) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    });
  }

  function noSession(message) {
    // The server's text names the command as it is typed on this computer.
    var text = message || NO_SESSION;
    var main = $('main');
    clear(main);
    main.appendChild(h('p', { class: 'sub', text: text }));
    $('quiet').hidden = true;
    say(text);
  }

  function setLost(on) {
    if (S.lost === on) return;
    S.lost = on;
    drawNotice();
    if (on) say(LOST);
  }

  function shell(inbox) {
    S.inbox = inbox;
    var proj = $('proj');
    clear(proj);
    var list = inbox.projects || [];
    if (list.length > 1 && inbox.project) {
      var sel = h('select', { 'aria-label': 'Project', onchange: function () {
        location.search = '?project=' + encodeURIComponent(sel.value);
      } }, list.map(function (p) {
        return h('option', { value: p.id, text: p.name });
      }));
      sel.value = inbox.project.id;
      proj.appendChild(sel);
    } else if (inbox.project) {
      proj.textContent = inbox.project.name;
    }
    var q = $('quiet');
    var quiet = inbox.state ? inbox.state.quiet : null;
    q.hidden = !inbox.project;
    q.textContent = 'Quiet: ' + (quiet ? 'on' : 'off');
    q.setAttribute('aria-pressed', quiet ? 'true' : 'false');
    q.disabled = quiet === 'session';
    drawNotice();
  }

  function quietOff(quiet) {
    var project = S.inbox && S.inbox.project ? S.inbox.project.id : null;
    if (quiet === 'here') return { changes: { quiet: false }, project: project };
    return { changes: { quiet_today: false }, project: null };
  }

  function toggleQuiet() {
    var quiet = S.inbox && S.inbox.state ? S.inbox.state.quiet : null;
    if (quiet === 'session') return;
    var body = quiet ? quietOff(quiet) : { changes: { quiet_today: true }, project: null };
    api('POST', '/api/settings', { changes: body.changes, project: body.project, confirm: false })
      .then(function () { return loadShell(); })
      .then(function () {
        var n = S.inbox && S.inbox.state ? S.inbox.state.notice : null;
        say(quiet ? 'Quiet is off.' : n);
        refresh();
      })
      .catch(function (err) { say(err.message); });
  }

  function drawNotice() {
    var bar = $('notice');
    clear(bar);
    var text = S.lost ? LOST : (S.inbox && S.inbox.state ? S.inbox.state.notice : null);
    bar.hidden = !text;
    if (!text) return;
    var p = h('p');
    var quiet = S.inbox && S.inbox.state ? S.inbox.state.quiet : null;
    if (!S.lost && /\sTurn on$/.test(text)) {
      add(p, [text.replace(/\sTurn on$/, ''), h('a', { class: 'tbtn', href: withProject('/settings'), text: 'Turn on' })]);
    } else if (!S.lost && /\sUndo$/.test(text)) {
      add(p, text.replace(/\sUndo$/, ''));
      if (quiet && quiet !== 'session') add(p, h('button', { type: 'button', class: 'tbtn', text: 'Undo', onclick: toggleQuiet }));
    } else {
      add(p, text);
    }
    bar.appendChild(p);
  }

  function loadShell() {
    return api('GET', withProject('/api/inbox')).then(function (inbox) {
      shell(inbox);
      return inbox;
    });
  }

  /* ------------------------------------------------------------ inbox */

  function group(title, items) {
    if (!items.length) return null;
    var id = 'g-' + title.toLowerCase();
    return h('section', { class: 'grp', 'aria-labelledby': id }, [h('h2', { id: id, text: title })].concat(items));
  }

  function nowItem(it) {
    return h('a', { class: 'it now', href: it.href }, [
      h('span', { class: 'k', text: it.reason }), h('span', { class: 'w', text: it.task }),
      h('span', { class: 'z', text: it.size }), h('span', { class: 'go', text: 'Open' })
    ]);
  }

  function noteItem(n) {
    var ev = (n.evidence || []).map(function (e) {
      return h('li', { text: e.path + ':' + e.line });
    });
    return h('details', { class: 'note' }, [
      h('summary', null, [h('span', { class: 'k', text: n.title }), h('span', { class: 'z', text: n.time })]),
      h('div', { class: 'nb' }, [
        h('p', { class: 'nt', text: n.text }),
        ev.length ? h('ul', null, ev) : null,
        h('p', { class: 'nt', text: n.checked })
      ])
    ]);
  }

  function waitingItem(w) {
    return h('a', { class: 'it', href: w.href }, [
      h('span', { class: 'k', text: w.kind }), h('span', { class: 'w', text: w.text })
    ]);
  }

  function resultItem(r) {
    return h('a', { class: 'it', href: r.href, 'aria-label': r.chip_label + '. ' + r.kind + ', ' + r.task }, [
      h('span', { class: 'k', text: r.kind }), h('span', { class: 'w', text: r.task }),
      h('span', { class: 'z' }), chip(r.chip, r.chip_label)
    ]);
  }

  function waitingGroup(list) {
    var items = list.map(waitingItem);
    if (items.length <= 3) return items;
    var rest = h('details', { class: 'more' }, [h('summary', { text: (items.length - 3) + ' more' })].concat(items.slice(3)));
    return items.slice(0, 3).concat([rest]);
  }

  function renderInbox(v) {
    var main = $('main');
    clear(main);
    main.appendChild(h('h1', { class: 'pg', text: 'Inbox' }));
    if (v.empty) main.appendChild(h('p', { class: 'hint', text: v.empty }));
    var notes = (v.notes || []).map(noteItem);
    if (notes.length && v.older_notes > 0) {
      notes.push(h('p', { class: 'close' }, h('a', { href: withProject('/journal'), text: 'Older notes' })));
    }
    add(main, [
      group('NOW', (v.now || []).map(nowItem)),
      group('WAITING', waitingGroup(v.waiting || [])),
      group('NOTES', notes),
      group('RESULTS', (v.results || []).map(resultItem))
    ]);
    if (v.closing) main.appendChild(h('p', { class: 'close', text: v.closing }));
  }

  /* ------------------------------------------------------------ question card */

  function evidence(v) {
    var items = (v.evidence || []).map(function (t) {
      var asserts = (t.asserts || []).map(function (a) { return h('span', { class: 'a', text: a.text }); });
      var src = t.source ? h('details', null, [
        h('summary', { text: 'Full test' }), h('pre', { text: t.source })
      ]) : null;
      return h('li', null, [
        h('span', { class: 'n', text: String(t.n) }),
        h('span', null, [t.name].concat(asserts, [h('span', { class: 'a nt', text: t.path + ':' + t.line }), src]))
      ]);
    });
    if (!items.length) return null;
    return h('ol', { class: 'ev', tabindex: '0', 'aria-label': v.lead || 'Tests' }, items);
  }

  function trace(v) {
    var t = v.trace;
    if (!t) return null;
    var kids = [h('span', { class: 't', text: t.title })];
    (t.frames || []).forEach(function (f) {
      kids.push(h('span', { class: 'a', text: '  ' + f.path + ':' + f.line + (f.where ? '   ' + f.where : '') }));
    });
    return h('div', { class: 'ev tr', tabindex: '0', 'aria-label': 'The failing test and its trace' }, kids);
  }

  function picked(v) {
    if (v.held && v.held.kind === 'pick') return v.held.answer;
    if (v.call) return v.call.answer;
    return null;
  }

  function pill(name, value, label, checked, disabled, onpick, note) {
    var input = h('input', { type: 'radio', name: name, value: value, checked: checked, disabled: disabled });
    input.addEventListener('change', function () { if (input.checked) onpick(value); });
    input.addEventListener('click', function () { if (checked) onpick(value, true); });
    var face = note === undefined ? h('span', { text: label }) : h('span', null, [h('b', { class: 'm', text: label }), note ? h('small', { text: note }) : null]);
    return h('label', { class: 'pill' }, [input, face]);
  }

  function picks(v) {
    if (v.multi) return togglePicks(v);
    var current = picked(v);
    var can = v.can || {};
    var col = (v.picks || []).some(function (p) { return 'path' in p; });
    return h('fieldset', null, [
      h('legend', { class: 'q', id: 'q', text: v.prompt }),
      h('div', { class: col ? 'picks col' : 'picks' }, (v.picks || []).map(function (p) {
        var on = p.value === current;
        return pill('pick', p.value, p.label, on, !can.lock && !on, function (value, again) {
          if (!again && can.lock) act(v, 'lock', { answer: value }, 'Locked.');
        }, col ? null : undefined);
      }))
    ]);
  }

  /* Several tests: the numbers are toggles, None and Don't know are exclusive, and
     only the Lock button sends. A toggle never locks, so no key press can. */

  var EXCLUSIVE = { none: true, dont_know: true };

  function chosenOf(answer) {
    var on = {};
    if (!answer) return on;
    if (EXCLUSIVE[answer]) on[answer] = true;
    else answer.split(',').forEach(function (n) { on[n] = true; });
    return on;
  }

  function draftFor(v) {
    if (!S.draft || S.draft.ref !== v.ref) S.draft = { ref: v.ref, on: {} };
    return S.draft;
  }

  function draftAnswer(on) {
    var keys = Object.keys(on).filter(function (k) { return on[k]; });
    var only = keys.filter(function (k) { return EXCLUSIVE[k]; });
    if (only.length) return only[0];
    return keys.map(Number).sort(function (a, b) { return a - b; }).join(',');
  }

  function toggle(v, value) {
    var d = draftFor(v);
    var was = !!d.on[value];
    if (EXCLUSIVE[value] || Object.keys(d.on).some(function (k) { return EXCLUSIVE[k] && d.on[k]; })) d.on = {};
    d.on[value] = !was;
    renderQuestion(v);
    var again = D.querySelector('[data-pick="' + value + '"]');
    if (again) again.focus();
  }

  function togglePicks(v) {
    var can = v.can || {};
    var current = picked(v);
    var on = can.lock ? draftFor(v).on : chosenOf(current);
    var answer = draftAnswer(on);
    var kids = (v.picks || []).map(function (p) {
      var pressed = !!on[p.value];
      return h('button', {
        type: 'button', class: 'pill tg' + (EXCLUSIVE[p.value] ? ' ex' : ''), 'data-pick': p.value,
        'aria-pressed': pressed ? 'true' : 'false', disabled: !can.lock,
        onclick: function () { if (can.lock) toggle(v, p.value); }
      }, h('span', { text: p.label }));
    });
    var lock = can.lock ? h('p', { class: 'acts send' }, h('button', {
      type: 'button', class: 'btn sm', text: 'Lock', disabled: !answer,
      onclick: function () {
        if (!answer) return;
        act(v, 'lock', { answer: answer }, 'Locked.');
      }
    })) : null;
    return h('fieldset', null, [
      h('legend', { class: 'q', id: 'q', text: v.prompt }),
      h('div', { class: 'picks', role: 'group', 'aria-labelledby': 'q' }, kids),
      lock
    ]);
  }

  function sureRow(v) {
    var can = v.can || {};
    var row = h('div', { class: 'sure' });
    if (can.confidence) {
      var cur = v.held ? v.held.confidence : null;
      add(row, h('span', { class: 'lb', id: 'sl', text: 'How sure?' }));
      [['high', 'Sure'], ['low', 'Not sure']].forEach(function (b) {
        add(row, pill('sure', b[0], b[1], cur === b[0], false, function (value, again) {
          act(v, 'confidence', { value: again ? null : value }, null);
        }));
      });
    }
    if (can.show) {
      add(row, h('button', { type: 'button', class: 'btn sm', text: 'Show the result', onclick: function () {
        act(v, 'show', {}, null).then(function (nv) {
          if (nv && nv.result) say(nv.result.chip_label + '. ' + (nv.result.what_happened || [])[0]);
        });
      } }));
    }
    return row.childNodes.length ? row : null;
  }

  function lockRow(v) {
    var can = v.can || {};
    if (v.held && v.held.kind === 'pick') {
      return h('div', { class: 'lock' }, [
        h('p', { class: 'st' }, ['Locked.', can.undo ? h('button', { type: 'button', class: 'tbtn', text: 'Undo', onclick: function () {
          act(v, 'undo', {}, 'Undone.');
        } }) : null]),
        sureRow(v)
      ]);
    }
    if (v.status_line || v.call) {
      return h('div', { class: 'lock' }, [
        v.call ? rows([[v.said_label || 'You said', v.call.label + (v.call.confidence_label ? '. ' + v.call.confidence_label + '.' : (/["]$/.test(v.call.label) ? '' : '.'))]]) : null,
        v.status_line ? h('p', { class: 'st', text: v.status_line }) : null,
        sureRow(v)
      ]);
    }
    return null;
  }

  function quietActs(v) {
    var can = v.can || {};
    var acts = [];
    if (can.skip) acts.push(h('button', { type: 'button', class: 'tbtn', text: 'Skip', onclick: function () { act(v, 'skip', {}, 'Skipped.'); } }));
    if (can.wrong_start) {
      acts.push(h('button', { type: 'button', class: 'tbtn', text: 'Wrong start', onclick: function () {
        act(v, 'wrong-start', {}, null).then(function (nv) {
          if (!nv) return;
          // The replacement question, when one was offered at once, takes this page.
          if (nv.ref && nv.ref !== v.ref) history.replaceState(null, '', withProject('/q/' + nv.ref));
          say(nv.status_line);
        });
      } }));
    }
    return acts.length ? h('div', { class: 'acts quiet' }, acts) : null;
  }

  function renderSkipped(v) {
    var can = v.can || {};
    return h('p', { class: 'card' }, ['Skipped. ', can.undo ? h('button', { type: 'button', class: 'tbtn', text: 'Undo', onclick: function () {
      act(v, 'undo', {}, 'Undone.');
    } }) : null]);
  }

  function lineField(v) {
    var can = v.can || {};
    if (!can.lock) return null;
    var field = h('input', { id: 'ans', type: 'text', autocomplete: 'off', maxlength: '500', 'aria-labelledby': 'q' });
    var send = function () {
      if (!field.value.trim()) { field.focus(); return; }
      act(v, 'lock', { answer: field.value }, 'Given to your agent.');
    };
    return h('div', null, [
      h('p', { class: 'q', id: 'q', text: v.prompt }),
      h('label', { class: 'fld' }, [h('b', { text: v.said_label || 'Your answer' }), field]),
      h('p', { class: 'acts send' }, h('button', { type: 'button', id: 'send', class: 'btn sm', text: 'Send to my agent', onclick: send }))
    ]);
  }

  function renderCard(v) {
    if ((v.held && v.held.kind === 'skip') || v.state === 'skipped') return renderSkipped(v);
    var open = v.state === 'open' || v.state === 'held';
    return h('form', { class: 'card' + (open ? ' open' : ''), 'aria-labelledby': 'q', onsubmit: function (e) {
      e.preventDefault();
      var send = $('send');  /* Enter in the Brief's one-line field sends it */
      if (v.form === 'line' && send) send.click();
    } }, [
      h('p', { class: 'eb' }, [h('span', { text: v.reason }), v.skip_ok ? h('span', { class: 'sk', text: 'skip ok' }) : null]),
      h('p', { class: 'ctx', text: v.context }),
      v.lead ? h('p', { class: 'lead', text: v.lead }) : null,
      trace(v),
      evidence(v),
      v.form === 'line' ? lineField(v) : picks(v),
      lockRow(v),
      quietActs(v),
      h('p', { class: 'err', id: 'err', hidden: true }),
      open ? h('p', { class: 'foot', text: v.footer }) : null  /* says what happens next: only while open */
    ]);
  }

  /* ------------------------------------------------------------ result */

  function cueRow(cue) {
    if (!cue) return null;
    var dd = [cue.text];
    (cue.evidence || []).forEach(function (e) {
      dd.push(h('span', { class: 'mono s', text: ' ' + e.path + ':' + e.line + (e.text ? '  ' + e.text : '') }));
    });
    return dd;
  }

  function disputeBox(v) {
    var box = h('div', { hidden: true });
    var field = h('textarea', { rows: '3', maxlength: '4000', 'aria-label': 'This result looks wrong' });
    add(box, [h('label', { class: 'fld' }, field), h('p', { class: 'acts' }, h('button', { type: 'button', class: 'btn sm', text: 'Recheck', onclick: function () {
      if (!field.value.trim()) { field.focus(); return; }
      act(v, 'dispute', { reason: field.value }, null).then(function (nv) {
        if (nv && nv.result && nv.result.more) say(nv.result.more.dispute);
      });
    } }))]);
    var open = h('button', { type: 'button', class: 'tbtn', text: 'This result looks wrong', onclick: function () {
      box.hidden = false;
      open.hidden = true;
      field.focus();
    } });
    return h('div', null, [open, box]);
  }

  function more(v, r) {
    var m = r.more || {};
    var cmds = h('pre', { hidden: true, text: (m.commands || []).join('\n') });
    var cmdBtn = (m.commands || []).length ? h('button', { type: 'button', class: 'tbtn', text: 'Open the commands', onclick: function () {
      cmds.hidden = !cmds.hidden;
    } }) : null;
    var list = (m.rows || []).map(function (row) {
      return h('li', null, [h('span', { class: 'mono', text: row.name }), h('span', { text: row.text })]);
    });
    return h('details', { class: 'more' }, [
      h('summary', { text: 'More' }),
      h('div', { class: 'mb' }, [
        list.length ? h('ul', null, list) : null,
        h('p', null, [m.checked || '', ' ', cmdBtn]),
        cmds,
        m.counts ? h('p', { text: m.counts }) : null,
        m.sure ? h('p', { text: m.sure }) : null,
        m.sent ? h('p', { text: m.sent }) : null,
        m.dispute ? h('p', { text: m.dispute }) : null,
        (m.notes || []).length ? h('div', { class: 'notes' }, m.notes.map(function (t) { return h('p', { text: t }); })) : null,
        (v.can || {}).dispute ? disputeBox(v) : null
      ])
    ]);
  }

  function renderResult(v) {
    var r = v.result;
    var label = r.chip_label + '. ' + r.headline;
    return h('section', { class: 'card', id: 'res', tabindex: '-1', 'aria-label': label }, [
      h('div', { class: 'rh' }, [h('h1', { class: 'rt', text: r.headline }), chip(r.chip, r.chip_label)]),
      h('p', { class: 'ctx', text: v.context }),
      r.reason ? h('p', { class: 'sub', text: r.reason }) : null,
      rows([
        [r.said_label || 'You said', r.you_said],
        ['What happened', (r.what_happened || []).join(' ')],
        ['What would have shown it', cueRow(r.cue)]
      ]),
      h('div', { class: 'cue' }, [h('a', { class: 'btn', href: withProject('/'), text: 'Back to the build' }), h('p', { text: r.back })]),
      quietActs(v),
      h('p', { class: 'err', id: 'err', hidden: true }),
      more(v, r)
    ]);
  }

  function renderQuestion(v) {
    S.view = v;
    var main = $('main');
    var focusResult = v.result && !D.getElementById('res');
    clear(main);
    main.appendChild(h('a', { class: 'crumb', href: withProject('/'), text: 'Inbox' }));
    main.appendChild(v.result ? renderResult(v) : renderCard(v));
    if (focusResult) {
      var res = $('res');
      if (res) res.focus({ preventScroll: true });
    }
  }

  function showError(err) {
    var el = $('err');
    if (el) {
      el.textContent = err.message;
      el.hidden = false;
    }
    say(err.message);
  }

  function act(v, name, body, live) {
    return api('POST', '/api/q/' + encodeURIComponent(v.ref) + '/' + name, body).then(function (nv) {
      renderQuestion(nv);
      say(live);
      return nv;
    }, function (err) {
      if (err.code === 'no_session' || err.code === 'unreachable') return null;
      return api('GET', '/api/q/' + encodeURIComponent(v.ref)).then(function (nv) {
        renderQuestion(nv);
        showError(err);
        return null;
      }, function () { showError(err); return null; });
    });
  }

  /* ------------------------------------------------------------ journal, skills */

  function renderJournal(v) {
    var main = $('main');
    clear(main);
    main.appendChild(h('h1', { class: 'pg', text: 'Journal' }));
    if (v.scope) main.appendChild(h('p', { class: 'sub', text: v.scope }));
    var entries = v.entries || [];
    if (!entries.length) {
      main.appendChild(h('p', { class: 'hint', text: 'No calls or notes yet.' }));
      return;
    }
    main.appendChild(h('div', { class: 'jl' }, entries.map(function (e) {
      var title = [h('span', { class: 'd', text: e.date }), e.task + ' | ' + e.kind];
      return h('article', { class: 'je' }, [
        h('div', { class: 'jh' }, [
          e.href ? h('a', { class: 'jt', href: e.href }, title) : h('span', { class: 'jt' }, title),
          e.chip ? chip(e.chip, e.chip_label) : null
        ]),
        rows((e.rows || []).map(function (r) { return [r.label, r.text]; }))
      ]);
    })));
  }

  function renderSkills(v) {
    var main = $('main');
    clear(main);
    main.appendChild(h('h1', { class: 'pg', text: 'Skills' }));
    (v.legend || []).forEach(function (line) { main.appendChild(h('p', { class: 'sub', text: line })); });
    main.appendChild(h('ul', { class: 'sl' }, (v.rows || []).map(function (r) {
      return h('li', { class: 'sr', 'aria-label': r.name + ': ' + r.level_line + ', ' + r.newest }, [
        h('div', { class: 'sh' }, [
          h('span', { class: 'sn' }, [h('span', { class: 'n', text: String(r.n) }), r.name]),
          h('span', { class: 'lv', text: r.level_line }),
          h('span', { class: 'nw', text: r.newest })
        ]),
        h('div', { class: 'mb' }, [
          h('p', { text: r.counts }), r.fixed ? h('p', { text: r.fixed }) : null, h('p', { text: r.asked })
        ]),
        rows([['Evidence covers', r.covers], ['No evidence on', r.no_evidence]]),
        h('p', { class: 'foot', text: r.checked })
      ]);
    })));
  }

  /* ------------------------------------------------------------ settings */

  function save(changes, project, confirm) {
    return api('POST', '/api/settings', { changes: changes, project: project, confirm: !!confirm }).then(function (nv) {
      renderSettings(nv);
      say('Saved.');
      return loadShell();
    }, function (err) {
      if (err.code === 'no_session' || err.code === 'unreachable') return null;
      return api('GET', withProject('/api/settings')).then(function (nv) {
        renderSettings(nv);
        if (err.code === 'confirm') askConfirm(err.message, changes, project);
        else showError(err);
      });
    });
  }

  function askConfirm(message, changes, project) {
    var box = $('confirm');
    clear(box);
    box.hidden = false;
    add(box, [h('p', { text: message }), h('div', { class: 'acts' }, [
      h('button', { type: 'button', class: 'btn sm', text: 'Confirm', onclick: function () { save(changes, project, true); } }),
      h('button', { type: 'button', class: 'tbtn', text: 'Cancel', onclick: function () { box.hidden = true; } })
    ])]);
    say(message);
    var b = box.querySelector('button');
    if (b) b.focus();
  }

  function option(type, name, value, label, note, checked, onpick) {
    var input = h('input', { type: type, name: name, value: value, checked: checked });
    input.addEventListener('change', function () { onpick(input); });
    return h('label', { class: 'opt' }, [input, h('span', null, [label, note ? h('small', { text: note }) : null])]);
  }

  function howMuch(v) {
    var dial = h('fieldset', null, [h('legend', { text: 'The dial' })].concat(DIAL.map(function (d) {
      return option('radio', 'dial', d[0], d[1], d[2], v.dial === d[0], function () { save({ dial: d[0] }, null); });
    })));
    var limit = h('select', { 'aria-label': 'Questions while building, a day', onchange: function () {
      save({ daily_limit: Number(limit.value) }, null);
    } }, [1, 2, 3].map(function (n) { return h('option', { value: String(n), text: String(n) }); }));
    limit.value = String(v.daily_limit);
    var quiet = v.quiet || {};
    var pid = v.project ? v.project.id : null;
    var quietSet = h('fieldset', null, [
      h('legend', { text: 'Quiet' }),
      option('checkbox', 'qt', 'today', 'Today', null, !!quiet.today, function (i) { save({ quiet_today: i.checked }, null); }),
      pid ? option('checkbox', 'qh', 'here', 'This project', null, !!quiet.here, function (i) { save({ quiet: i.checked }, pid); }) : null
    ]);
    return h('section', { class: 'sg', 'aria-labelledby': 's-how' }, [
      h('h2', { id: 's-how', text: 'HOW MUCH' }),
      h('div', { class: 'card' }, [
        dial,
        h('p', { class: 'row' }, ['Questions while building: ', limit, ' a day (up to 3).']),
        quietSet,
        option('checkbox', 'fa', 'on', 'Send findings to my agent', null, !!v.findings_to_agent, function (i) {
          save({ findings_to_agent: i.checked }, null);
        })
      ])
    ]);
  }

  function limitText(s) {
    if (s % 60 === 0) return (s / 60) + (s === 60 ? ' minute' : ' minutes');
    return s + ' seconds';
  }

  function thisProject(p) {
    var cmd = h('input', { type: 'text', value: p.test_command || '', 'aria-label': 'Test command', spellcheck: 'false' });
    var glob = h('input', { type: 'text', 'aria-label': 'Add a path', spellcheck: 'false' });
    var globs = (p.high_stakes || []).map(function (g) {
      return h('li', null, [g, h('button', { type: 'button', class: 'tbtn', text: 'Remove', 'aria-label': 'Remove ' + g, onclick: function () {
        save({ high_stakes_remove: g }, p.id);
      } })]);
    });
    return h('section', { class: 'sg', 'aria-labelledby': 's-proj' }, [
      h('h2', { id: 's-proj', text: 'THIS PROJECT' }),
      h('div', { class: 'card' }, [
        h('p', { class: 'mono', text: p.name }),
        h('div', null, [h('b', { text: 'Test command' }), h('p', { class: 'row' }, [cmd, h('button', { type: 'button', class: 'btn sm ghost', text: 'Change', onclick: function () {
          save({ test_command: cmd.value }, p.id);
        } })])]),
        h('p', { class: 'sub', text: 'Checks stop after ' + limitText(p.check_time_limit_s) + '.' }),
        h('div', null, [h('b', { text: 'High-stakes paths' }), globs.length ? h('ul', { class: 'globs' }, globs) : null,
          h('p', { class: 'row' }, [glob, h('button', { type: 'button', class: 'btn sm ghost', text: 'Add a path', onclick: function () {
            if (glob.value.trim()) save({ high_stakes_add: glob.value.trim() }, p.id);
          } })])])
      ])
    ]);
  }

  function renderSettings(v) {
    var main = $('main');
    clear(main);
    main.appendChild(h('h1', { class: 'pg', text: 'Settings' }));
    main.appendChild(h('div', { class: 'confirm', id: 'confirm', role: 'group', hidden: true }));
    main.appendChild(h('p', { class: 'err', id: 'err', hidden: true }));
    main.appendChild(howMuch(v));
    if (v.project) main.appendChild(thisProject(v.project));
    main.appendChild(h('section', { class: 'sg', 'aria-labelledby': 's-rec' }, [
      h('h2', { id: 's-rec', text: 'YOUR RECORD' }),
      h('div', { class: 'card' }, h('p', { text: v.record + '. A git repo on this computer. Plain files. No remote.' }))
    ]));
  }

  /* ------------------------------------------------------------ routing and live updates */

  function render() {
    var r = S.route;
    if (r.name === 'question') return api('GET', '/api/q/' + encodeURIComponent(r.ref)).then(renderQuestion);
    if (r.name === 'journal') return api('GET', withProject('/api/journal')).then(renderJournal);
    if (r.name === 'skills') return api('GET', withProject('/api/skills')).then(renderSkills);
    if (r.name === 'settings') return api('GET', withProject('/api/settings')).then(renderSettings);
    return (S.inbox ? Promise.resolve(S.inbox) : loadShell()).then(renderInbox);
  }

  function typing() {
    var a = D.activeElement;
    return !!a && (a.tagName === 'TEXTAREA' || (a.tagName === 'INPUT' && a.type === 'text'));
  }

  function refresh() {
    if (typing()) return;
    if (S.route.name === 'inbox') S.inbox = null;
    render().catch(function (err) { if (err.code !== 'no_session') showError(err); });
  }

  function onNotice(n) {
    var r = S.route;
    if (n.topic === 'inbox' || n.topic === 'settings') {
      loadShell().then(function () { if (r.name === 'inbox') renderInbox(S.inbox); }).catch(function () {});
    }
    if (r.name === 'question' && n.topic === 'question') {
      if (!n.id || !S.view || n.id === S.view.id) refresh();
      return;
    }
    if (r.name === 'settings' && n.topic === 'settings') refresh();
    if (r.name === 'journal' || r.name === 'skills') refresh();
  }

  function listen() {
    if (!window.EventSource) return;
    var es = new EventSource('/api/events');
    S.es = es;
    es.onopen = function () { setLost(false); };
    es.onmessage = function (ev) {
      var n;
      try { n = JSON.parse(ev.data); } catch (e) { return; }
      onNotice(n);
    };
    es.onerror = function () {
      setLost(true);
      if (es.readyState !== 2) return;
      setTimeout(function () {
        api('GET', '/api/session').then(function (s) {
          S.token = s.token;
          setLost(false);
          listen();
        }).catch(function () {});
      }, 5000);
    };
  }

  function boot() {
    S.route = route();
    markTabs(S.route.name);
    $('quiet').addEventListener('click', toggleQuiet);
    api('GET', '/api/session').then(function (s) {
      S.token = s.token;
      return loadShell();
    }).then(function () {
      return render();
    }).then(function () {
      listen();
    }).catch(function (err) {
      if (err.code === 'no_session') return;
      var main = $('main');
      clear(main);
      main.appendChild(h('p', { class: 'sub', text: err.code === 'unreachable' ? LOST : err.message }));
    });
  }

  if (D.readyState === 'loading') D.addEventListener('DOMContentLoaded', boot);
  else boot();
}());
