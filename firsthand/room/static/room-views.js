/* The Room page, part two: the screens. Inbox, the question sheet, a result and
   what stands in for one, the Journal, Skills and Settings. Each draws only the
   JSON the engine returns, with createElement and textContent. Shared helpers and
   the frame are in room.js. */
(function () {
  'use strict';

  var F = window.FH;
  var D = document;
  var S = F.S;
  var $ = F.$;
  var h = F.h;
  var add = F.add;
  var clear = F.clear;
  var prop = F.prop;
  var label = F.label;
  var sec = F.sec;
  var say = F.say;
  var withProject = F.withProject;
  var no = F.no;
  var hms = F.hms;

  var DIAL = [
    ['off', 'Off', 'Nothing is asked, run or recorded.'],
    ['notes', 'Notes only', 'No questions. Checks run and post notes.'],
    ['standard', 'Standard', 'Questions within the daily limit.'],
    ['deep', 'Deep', 'As Standard. You may also write a line of code on some questions.']
  ];
  var QUIET_WORDS = { session: 'this session', today: 'today', here: 'this project' };
  var CONFIDENCE = { high: 'Sure', low: 'Not sure' };
  var EXCLUSIVE = { none: true, dont_know: true };
  var KEYS_MULTI = 'Turn on any number of tests, then Lock.';
  var KEYS_TAP_UNDO = 'A tap locks your answer. You can undo it before the result.';
  var KEYS_TAP = 'A tap locks your answer.';

  /* ------------------------------------------------------------ small parts */

  function margin(bold, rest) {
    return h('div', { class: 'fh-row__margin' }, [h('b', { text: bold })].concat(rest || []));
  }

  function ledger(rows, head) {
    return h('ol', { class: head === false ? 'fh-ledger' : 'fh-ledger fh-ledger--head' }, rows);
  }

  function fact(k, v, opts) {
    opts = opts || {};
    var li = h('li', { class: opts.key ? 'is-key' : null }, [
      h('span', { class: 'k', text: k }), h('span', { class: 'ld' }), h('span', { class: 'v', text: v })
    ]);
    if (opts.i !== undefined) prop(li, '--i', opts.i);
    return li;
  }

  function facts(list) { return h('ul', { class: 'fh-facts' }, list); }

  function finding(name, kids, text) {
    return h('div', { class: text ? 'fh-finding fh-finding--text' : 'fh-finding' }, [
      h('span', { class: 'fh-label', text: name }), h('div', null, kids)
    ]);
  }

  function btn(text, cls, onclick, extra) {
    var props = { type: 'button', class: 'fh-btn' + (cls ? ' fh-btn--' + cls : ''), text: text, onclick: onclick };
    var k;
    for (k in extra || {}) props[k] = extra[k];
    return h('button', props);
  }

  function back(second) {
    return h('a', { class: second ? 'fh-btn fh-btn--second' : 'fh-btn', href: withProject('/'), text: 'Back to the build' });
  }

  function testName(id) { return String(id || '').split('::').pop(); }

  function plural(n, one, many) { return n + ' ' + (n === 1 ? one : many); }

  /* The answer in the person's hand: said, a full stop, then how sure. */
  function answerText(said, confidence) {
    var text = said || '';
    if (!/["”]$/.test(text)) text += '.';
    var c = CONFIDENCE[confidence] || null;
    return c ? text + ' ' + c + '.' : text;
  }

  /* The person's line in their hand: straight quotes at its ends become curly ones. */
  function curly(text) {
    return String(text || '').replace(/^"/, '\u201C').replace(/"(?=[.]?$)/, '\u201D');
  }

  function lineAnswer(text) { return h('p', { class: 'fh-answer fh-answer--line', text: curly(text) }); }

  function answer(said, confidence, names, line) {
    var list = (names || []).filter(function (n) { return n; });
    return h('p', { class: line ? 'fh-answer fh-answer--line' : 'fh-answer' }, [
      answerText(said, confidence), list.length ? h('small', { text: list.join(', ') }) : null
    ]);
  }

  function head(name, time) {
    return h('div', { class: 'fh-spread__head' }, [
      h('span', { class: 'fh-label' }, typeof name === 'string' ? h('b', { text: name }) : name),
      time ? h('time', { text: time }) : null
    ]);
  }

  function errHere() { return F.errLine(); }

  /* ------------------------------------------------------------ actions */

  /* pre(nv), when given, runs before the new view is drawn. */
  function act(v, name, body, live, key, pre) {
    S.focus = key || null;
    return F.api('POST', '/api/q/' + encodeURIComponent(v.ref) + '/' + name, body).then(function (nv) {
      if (pre) pre(nv);
      F.setErr(null);
      renderQuestion(nv, true);
      // A result announces its verdict as it is drawn; the press word would replace it.
      if (layoutOf(nv) !== 'result') say(live);
      return nv;
    }, function (err) {
      if (err.code === 'no_session' || err.code === 'unreachable') return null;
      return F.api('GET', '/api/q/' + encodeURIComponent(v.ref)).then(function (nv) {
        F.setErr(err);
        renderQuestion(nv, true);
        return null;
      }, function () {
        F.setErr(err);
        renderQuestion(v, true);
        return null;
      });
    });
  }

  /* ------------------------------------------------------------ inbox */

  function stub(it) {
    var name = S.inbox && S.inbox.project ? S.inbox.project.name : '';
    return h('section', { class: 'fh-sheet fh-sheet--stub', 'aria-labelledby': 'stub-title' }, [
      h('div', { class: 'fh-sheet__bar' }, [h('span', { text: it.reason }), h('span', { text: no(it.no) + ' · skip ok' })]),
      h('div', { class: 'fh-sheet__body' }, [
        ctxText([name], it.since),
        h('h2', { class: 'fh-sheet__title', id: 'stub-title', text: it.task }),
        h('div', { class: 'fh-sheet__act' }, [
          h('a', { class: 'fh-btn', href: withProject(it.href), text: 'Open' }),
          h('span', { class: 'fh-sheet__size', text: [it.kind_label, it.size].filter(Boolean).join(' · ') })
        ])
      ])
    ]);
  }

  function blankRow(bold, rest, title, kids) {
    return h('li', { class: 'fh-row fh-row--blank' }, [
      margin(bold, rest), h('div', null, [h('h3', { class: 'fh-row__title', text: title })].concat(kids || []))
    ]);
  }

  function noteEvidence(list) {
    var items = (list || []).map(function (e, i) {
      return fact(testName(e.test), e.path + (e.line ? ':' + e.line : ''), { i: i });
    });
    return items.length ? facts(items) : null;
  }

  function noteRow(n, time, title) {
    return h('li', { class: 'fh-row fh-row--note' }, [
      margin('Note', time),
      h('div', null, [
        n.task ? h('div', { class: 'fh-row__kind', text: n.task }) : null,
        h('h3', { class: 'fh-row__title', text: title }),
        noteEvidence(n.evidence),
        h('p', { class: 'fh-row__foot', text: n.checked || 'Checked by a run, no model.' })
      ])
    ]);
  }

  function lines(you, run, ran) {
    return h('dl', { class: 'fh-row__lines' }, [
      h('dt', { text: 'You' }), h('dd', { class: 'you', text: you }),
      h('dt', { text: 'Run' }), h('dd', { class: ran === false ? 'say' : 'run', text: run })
    ]);
  }

  /* A call in a ledger: the Journal and the Inbox's results. */
  function entryRow(e, time) {
    var kind = F.kindOf(e.chip);
    return h('li', { class: 'fh-row' }, [
      margin(no(e.no), time),
      h('div', null, [
        h('div', { class: 'fh-row__kind', text: e.kind }),
        h('div', { class: 'fh-row__head' }, [
          h('h3', { class: 'fh-row__title' }, e.href ? h('a', { href: withProject(e.href), text: e.task }) : e.task),
          kind ? F.verdict(kind, e.chip_label) : null
        ]),
        lines(e.said, e.happened, e.ran)
      ])
    ]);
  }

  function waitingRow(w) {
    return h('li', { class: 'fh-row' }, [
      margin(no(w.no), w.locked_at ? 'locked ' + F.hm(w.locked_at) : null),
      h('div', null, [
        h('div', { class: 'fh-row__kind', text: w.kind }),
        h('div', { class: 'fh-row__head' }, h('h3', { class: 'fh-row__title' }, h('a', { href: withProject(w.href), text: w.task }))),
        lines(w.said, w.text, true)
      ])
    ]);
  }

  function statusLine(name, value) {
    return h('li', null, [name, h('span', { class: 'ld' }), h('b', { text: value })]);
  }

  function today(v) {
    var state = v.state || {};
    var dial = DIAL.filter(function (d) { return d[0] === state.dial; })[0];
    var asked = v.asked || { today: 0, limit: 1 };
    return [
      sec('Today'),
      h('ul', { class: 'fh-status' }, [
        statusLine('Asked today', asked.today + ' of ' + asked.limit),
        statusLine('The dial', dial ? dial[1] : String(state.dial || '')),
        statusLine('Quiet', QUIET_WORDS[state.quiet] || 'off')
      ])
    ];
  }

  function renderInbox(v) {
    var main = $('main');
    clear(main);
    S.view = null;
    S.viewJson = null;
    S.page = 'inbox';
    F.title(null);
    var now = (v.now || [])[0];
    add(main, [h('h1', { class: 'fh-vh', text: 'Inbox' }), sec('Now')]);
    if (now) {
      main.appendChild(stub(now));
    } else {
      main.appendChild(ledger([blankRow(no(v.next_no), 'next', 'No question is open.',
        v.empty ? [h('p', { class: 'fh-text', text: v.empty })] : null)]));
    }
    var waiting = v.waiting || [];
    if (waiting.length) add(main, [sec('Waiting', String(waiting.length)), ledger(waiting.map(waitingRow))]);
    var notes = v.notes || [];
    if (notes.length) {
      var older = v.older_notes || 0;
      add(main, [
        sec('Notes', older ? notes.length + ' of ' + (notes.length + older) : null),
        ledger(notes.map(function (n) { return noteRow(n, n.time, n.title); })),
        older ? h('p', { class: 'fh-acts' }, h('a', { class: 'fh-btn fh-btn--quiet', href: withProject('/journal'), text: 'Older notes' })) : null
      ]);
    }
    var results = v.results || [];
    if (results.length) {
      add(main, [
        sec('Results', results.length + ' not opened'),
        ledger(results.map(function (r) { return entryRow(r, F.marginTime(r.at)); }))
      ]);
    }
    add(main, today(v));
    F.fitFacts(main);
  }

  /* ------------------------------------------------------------ the question sheet */

  function codeListing(t) {
    var keys = {};
    (t.asserts || []).forEach(function (a) { keys[a.line] = true; });
    var rows = String(t.source).replace(/\n+$/, '').split('\n').map(function (text, i) {
      var n = Number(t.line) + i;
      return h('li', { class: keys[n] ? 'is-key' : null }, [h('span', { class: 'n', text: String(n) }), h('code', { text: text })]);
    });
    return h('ol', { class: 'fh-code' }, rows);
  }

  function evidence(v) {
    var items = (v.evidence || []).map(function (t) {
      var asserts = (t.asserts || []).map(function (a) { return h('code', { text: a.text }); });
      var full = t.source ? h('details', { class: 'fh-more fh-more--in' }, [h('summary', { text: 'Full test' }), codeListing(t)]) : null;
      return h('li', null, [
        h('span', { class: 'n', text: String(t.n) }),
        h('span', { class: 't' }, [
          h('span', { class: 'hd' }, [h('b', { text: t.name }), h('span', { class: 'ld' }), h('small', { text: t.path + ':' + t.line })])
        ].concat(asserts, [full]))
      ]);
    });
    if (!items.length) return null;
    return h('ol', { class: 'fh-evidence', tabindex: '0', 'aria-labelledby': 'lead' }, items);
  }

  function trace(v) {
    var t = v.trace;
    if (!t) return null;
    return h('div', { class: 'fh-trace', tabindex: '0', 'aria-label': 'The failing test and its trace' }, [
      h('p', { class: 'fh-trace__title', text: t.title }),
      h('ol', null, (t.frames || []).map(function (f) {
        var k = h('span', { class: 'k', text: f.path + ':' + f.line });
        return h('li', null, f.where ? [k, h('span', { class: 'ld' }), h('small', { text: f.where })] : [k]);
      }))
    ]);
  }

  function chosenOf(answerValue) {
    var on = {};
    if (!answerValue) return on;
    if (EXCLUSIVE[answerValue]) on[answerValue] = true;
    else String(answerValue).split(',').forEach(function (n) { on[n] = true; });
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
    S.focus = 'pick-' + value;
    renderQuestion(v, true);
  }

  function picked(v) {
    if (v.held && v.held.kind === 'pick') return v.held.answer;
    if (v.call) return v.call.answer;
    return null;
  }

  /* One cell. Word cells carry their label; Call it's column cells a number and a path. */
  function cell(v, p, on, cls, onpress) {
    var can = v.can || {};
    var kids = p.text;
    if (p.col) kids = [h('span', { class: 'n', text: p.n }), h('span', { class: 't', text: p.t })];
    return h('button', {
      type: 'button', class: 'fh-pick' + (cls ? ' ' + cls : ''), 'data-k': 'pick-' + p.value,
      'aria-pressed': on ? 'true' : 'false', disabled: !can.lock, onclick: can.lock ? onpress : null
    }, kids);
  }

  function multiCells(v) {
    var can = v.can || {};
    var on = can.lock ? draftFor(v).on : chosenOf(picked(v));
    return (v.picks || []).map(function (p) {
      var cls = p.value === 'none' ? 'fh-pick--word fh-pick--gap' : (p.value === 'dont_know' ? 'fh-pick--word' : null);
      return cell(v, { value: p.value, text: p.label }, !!on[p.value], cls, function () { toggle(v, p.value); });
    });
  }

  function tapCells(v, col) {
    var current = picked(v);
    var list = v.picks || [];
    return list.map(function (p, i) {
      var word = !col || !('path' in p);
      var gap = col ? (!('path' in p) && p.value !== 'dont_know') : (list.length > 2 && i === list.length - 1);
      var parts = /^(\S+)\s+([\s\S]*)$/.exec(p.label);
      var spec = { value: p.value, text: p.label, col: col };
      if (col) {
        spec.n = p.value === 'dont_know' ? '' : (parts ? parts[1] : '');
        spec.t = p.value === 'dont_know' ? p.label : (parts ? parts[2] : p.label);
      }
      var cls = [word ? 'fh-pick--word' : null, gap ? 'fh-pick--gap' : null].filter(Boolean).join(' ');
      return cell(v, spec, p.value === current, cls, function () {
        act(v, 'lock', { answer: p.value }, 'Locked.', 'pick-' + p.value);
      });
    });
  }

  function isBriefConfirm(v) { return v.kind === 'brief' && v.form === 'pick'; }

  function control(v) {
    if (v.form === 'line') return lineField(v);
    var col = (v.picks || []).some(function (p) { return 'path' in p; });
    var kids = v.multi ? multiCells(v) : tapCells(v, col);
    return h('div', { class: col ? 'fh-picks fh-picks--col' : 'fh-picks', role: 'group', 'aria-labelledby': 'q' }, kids);
  }

  function keysLine(v) {
    var can = v.can || {};
    if (!can.lock || v.form === 'line') return null;
    var text = v.multi ? KEYS_MULTI : (isBriefConfirm(v) ? KEYS_TAP : KEYS_TAP_UNDO);
    return h('p', { class: 'fh-keys', text: text });
  }

  function lineField(v) {
    var drafts = S.lines || (S.lines = {});
    var field = h('input', {
      class: 'fh-input fh-input--write', id: 'ans', type: 'text', maxlength: '500', autocomplete: 'off',
      'aria-describedby': 'q', 'data-k': 'ans', disabled: !(v.can || {}).lock,
      oninput: function () { drafts[v.ref] = field.value; }
    });
    field.value = drafts[v.ref] || '';
    return h('label', { class: 'fh-field' }, [h('span', { class: 'fh-label', text: v.said_label || 'Your check' }), field]);
  }

  /* What the sheet's primary button does: Lock, or Send to my agent. Also the form's submit. */
  function primary(v) {
    var can = v.can || {};
    if (!can.lock) return;
    if (v.form === 'line') {
      var field = $('ans');
      if (!field || !field.value.trim()) { if (field) field.focus(); return; }
      act(v, 'lock', { answer: field.value }, 'Given to your agent.', 'ans').then(function (nv) {
        if (nv && S.lines) delete S.lines[v.ref];
      });
      return;
    }
    if (!v.multi) return;
    var a = draftAnswer(draftFor(v).on);
    if (a) act(v, 'lock', { answer: a }, 'Locked.', 'lock');
  }

  function primaryButton(v) {
    var can = v.can || {};
    if (!can.lock) return null;
    if (v.form === 'line') {
      return h('button', { type: 'submit', class: 'fh-btn', 'data-k': 'send' }, [
        'Send to my agent ', h('span', { class: 'fh-kbd', 'aria-hidden': 'true', text: '↵' })
      ]);
    }
    if (!v.multi) return null;
    return h('button', { type: 'submit', class: 'fh-btn', 'data-k': 'lock', text: 'Lock', disabled: !draftAnswer(draftFor(v).on) });
  }

  /* The replacement question, when one is offered at once, takes this page: the route
     moves with the address, so a notice for the old question cannot draw it back. */
  function wrongStart(v) {
    act(v, 'wrong-start', {}, null, 'wrong', function (nv) {
      if (!nv.ref || nv.ref === v.ref) return;
      S.route = { name: 'question', ref: nv.ref, tab: 'inbox' };
      history.replaceState(null, '', withProject('/q/' + nv.ref));
    }).then(function (nv) {
      if (!nv) return;
      say(nv.status_line || [nv.kind_label, nv.prompt_text || nv.prompt].filter(Boolean).join('. '));
    });
  }

  function sheetActs(v) {
    var can = v.can || {};
    var kids = [
      primaryButton(v),
      can.skip ? btn('Skip', 'quiet', function () { act(v, 'skip', {}, 'Skipped.', 'skip'); }, { 'data-k': 'skip' }) : null,
      can.wrong_start ? btn('Wrong start', 'quiet', function () { wrongStart(v); }, { 'data-k': 'wrong' }) : null
    ].filter(Boolean);
    return kids.length ? h('div', { class: 'fh-sheet__act' }, kids) : null;
  }

  function sureCells(v) {
    var cur = v.held ? v.held.confidence : null;
    return h('div', { class: 'fh-held__sure' }, [
      h('span', { class: 'fh-label', id: 'sure', text: 'How sure?' }),
      h('div', { class: 'fh-picks', role: 'group', 'aria-labelledby': 'sure' }, [['high', 'Sure'], ['low', 'Not sure']].map(function (b) {
        var on = cur === b[0];
        return h('button', {
          type: 'button', class: 'fh-pick fh-pick--word', 'data-k': 'sure-' + b[0], 'aria-pressed': on ? 'true' : 'false', text: b[1],
          onclick: function () { act(v, 'confidence', { value: on ? null : b[0] }, null, 'sure-' + b[0]); }
        });
      }))
    ]);
  }

  function showResult(v) {
    act(v, 'show', {}, null, 'show').then(function (nv) {
      if (nv && nv.result && nv.result.ran_at) say(nv.result.chip_label + '. ' + (nv.result.what_happened || [])[0]);
      else if (nv) say(nv.status_line);
    });
  }

  /* Locked, before the result: the call is on the page, the run is not. */
  function heldBlock(v) {
    var can = v.can || {};
    var held = v.held;
    return h('div', { class: 'fh-held' }, [
      head('Your call', held.at ? 'locked ' + hms(held.at) : null),
      answer(held.said, held.confidence, held.names),
      can.confidence ? sureCells(v) : null,
      h('div', { class: 'fh-sheet__act' }, [
        can.show ? btn('Show the result', null, function () { showResult(v); }, { 'data-k': 'show' }) : null,
        can.undo ? btn('Undo', 'quiet', function () { act(v, 'undo', {}, 'Undone.', 'undo'); }, { 'data-k': 'undo' }) : null
      ]),
      errHere()
    ]);
  }

  function briefLine(v) {
    var call = v.call;
    if (!call) return null;
    return h('div', { class: 'fh-held' }, [
      head(v.said_label || 'Your check', call.locked_at ? 'locked ' + hms(call.locked_at) : null),
      lineAnswer(call.said)
    ]);
  }

  /* project / task / change since 09:12, where the last part never breaks inside. */
  function ctxText(parts, since) {
    var list = parts.filter(Boolean);
    if (!list.length && !since) return null;
    var p = h('p', { class: 'fh-sheet__ctx' }, list.join(' / '));
    if (since) add(p, [list.length ? ' / ' : null, h('span', { class: 'fh-nobr', text: 'change since ' + since })]);
    return p;
  }

  function ctxLine(v) {
    var w = v.where || {};
    return ctxText([w.project, w.task], w.since);
  }

  function sheet(v) {
    var held = v.held && v.held.kind === 'pick';
    var still = !!S.drawn[v.ref] || held;
    S.drawn[v.ref] = true;
    var right = no(v.no) + (held ? ' · locked' : (v.skip_ok ? ' · skip ok' : ''));
    var form = h('form', { onsubmit: function (e) { e.preventDefault(); primary(v); } }, [
      ctxLine(v),
      h('p', { class: 'fh-sheet__lead', id: 'lead', text: v.reason + '.' + (v.lead ? ' ' + v.lead : '') }),
      isBriefConfirm(v) ? briefLine(v) : null,
      trace(v),
      evidence(v),
      h('h2', { class: 'fh-q', id: 'q', 'data-still': still }, h('mark', { text: v.prompt_text || v.prompt })),
      v.prompt_name ? h('p', { class: 'fh-q__name', text: v.prompt_name }) : null,
      control(v),
      held ? heldBlock(v) : keysLine(v),
      held ? null : errHere(),
      held ? null : sheetActs(v)
    ]);
    return h('section', { class: 'fh-sheet', 'aria-labelledby': 'q' }, [
      h('div', { class: 'fh-sheet__bar' }, [h('span', { text: v.kind_label }), h('span', { text: right })]),
      h('div', { class: 'fh-sheet__body' }, form),
      v.footer ? h('div', { class: 'fh-sheet__foot' }, [
        h('span', { text: v.footer }),
        v.kind === 'revert_test' ? h('span', { text: 'Nothing is written to your project.' }) : null
      ]) : null
    ]);
  }

  /* ------------------------------------------------------------ results */

  function resultHead(v, kind, words) {
    var top = [no(v.no), v.kind_label, v.skill].filter(Boolean).join(' · ');
    return h('div', { class: 'fh-head' }, [
      h('div', null, [h('div', { class: 'fh-label', text: top }), h('h1', { class: 'fh-head__title', text: (v.where || {}).task || v.kind_label })]),
      kind ? F.verdict(kind, words) : null
    ]);
  }

  function callSide(v) {
    var call = v.call;
    var r = v.result || {};
    var brief = v.kind === 'brief';
    var kids = [];
    if (call) {
      kids.push(head(brief ? (v.said_label || 'Your check') : 'Your call', call.locked_at ? 'locked ' + hms(call.locked_at) : null));
      kids.push(brief ? lineAnswer(answerText(call.said, call.confidence)) : answer(call.said, call.confidence, call.names));
      if (brief && call.confirm) {
        kids.push(head('Is this your check?', call.confirm.at ? 'locked ' + hms(call.confirm.at) : null));
        kids.push(lineAnswer(call.confirm.value === 'yes' ? 'Yes.' : 'No.'));
      }
    } else {
      kids.push(head(brief ? (v.said_label || 'Your check') : 'Your call'));
      kids.push(h('p', { class: 'fh-answer', text: r.you_said || 'No answer.' }));
    }
    return h('div', { class: 'fh-spread__side fh-spread__call' }, kids);
  }

  function runSide(r) {
    return h('div', { class: 'fh-spread__side fh-spread__run' }, [
      head([h('b', { text: 'The run' }), r.run_label ? ' · ' + r.run_label : null], r.ran_at ? 'recorded ' + hms(r.ran_at) : null),
      facts((r.facts || []).map(function (f, i) { return fact(f.k, f.v, { key: f.key, i: i }); }))
    ]);
  }

  function spreadLabel(r) { return r.chip_label + '. ' + ((r.what_happened || [])[0] || ''); }

  function findingRows(r) {
    var names = r.names || [];
    var wh = r.what_happened || [];
    var body = [h('p', { class: 'fh-finding__text' }, F.mixed(wh[0] || '', names))];
    wh.slice(1).forEach(function (t) { body.push(h('p', null, F.mixed(t, names))); });
    if (r.reason) body.push(h('p', null, F.mixed(r.reason, names)));
    var out = [finding(r.chip_label, body)];
    if (r.cue) {
      var cue = [h('p', { class: 'fh-text' }, F.mixed(r.cue.text, names))];
      (r.cue.evidence || []).forEach(function (e) {
        if (!e.text) return;
        cue.push(h('ol', { class: 'fh-code' }, h('li', { class: 'is-key' }, [h('span', { class: 'n', text: String(e.line) }), h('code', { text: e.text })])));
      });
      out.push(finding('What would have shown it', cue, true));
    }
    if (r.counts) out.push(finding('Your record', [h('p', { class: 'fh-text' }, F.counts(r.counts))], true));
    return out;
  }

  function moreBox(r) {
    var m = r.more || {};
    var items = [];
    if ((m.why || []).length) {
      items.push(finding('Why listed', [facts(m.why.map(function (w, i) { return fact(w.name, w.text, { i: i }); }))], true));
    }
    if (m.sure) items.push(finding('How sure', [h('p', { class: 'fh-text' }, F.counts(m.sure))], true));
    if (m.sent) items.push(finding('Sent', [h('p', { class: 'fh-text', text: m.sent })], true));
    if (m.dispute) items.push(finding('Recheck', [h('p', { class: 'fh-text', text: m.dispute })], true));
    if ((m.notes || []).length) items.push(finding('Notes', m.notes.map(function (t) { return h('p', { class: 'fh-text', text: t }); }), true));
    if ((m.commands || []).length) {
      items.push(finding('Commands', [h('ol', { class: 'fh-cmds', id: 'cmds', tabindex: '-1' }, m.commands.map(function (c) { return h('li', { text: c }); }))], true));
    }
    if (!items.length) return null;
    return h('details', { class: 'fh-more', id: 'more' }, [h('summary', null, ['More', h('span', { class: 'ld' })])].concat(items));
  }

  function recheckRow(v) {
    var field = h('textarea', { class: 'fh-input fh-input--note', id: 'why', rows: '3', maxlength: '4000', 'data-k': 'why' });
    var row = h('div', { class: 'fh-finding fh-finding--text', id: 'recheck', hidden: true }, [
      h('span', { class: 'fh-label', text: 'Recheck' }),
      h('div', null, [
        h('label', { class: 'fh-field' }, [h('span', { class: 'fh-label', text: 'This result looks wrong' }), field]),
        h('div', { class: 'fh-acts' }, [
          btn('Recheck', 'second', function () {
            if (!field.value.trim()) { field.focus(); return; }
            act(v, 'dispute', { reason: field.value }, null, 'wrong-result').then(function (nv) {
              if (nv && nv.result && nv.result.more) say(nv.result.more.dispute);
            });
          }, { 'data-k': 'recheck' }),
          btn('Cancel', 'quiet', function () {
            row.hidden = true;
            var b = $('looks-wrong');
            if (b) { b.hidden = false; b.focus(); }
          })
        ])
      ])
    ]);
    return row;
  }

  function resultActs(v) {
    var r = v.result;
    var m = r.more || {};
    var can = v.can || {};
    return h('div', { class: 'fh-acts' }, [
      back(false),
      (m.commands || []).length ? btn('Open the commands', 'quiet', function () {
        var more = $('more');
        if (more) more.open = true;
        var c = $('cmds');
        if (c) c.focus();
      }) : null,
      can.dispute ? btn('This result looks wrong', 'quiet', function (e) {
        // The form now carries the words; the trigger leaves the line until Cancel.
        $('recheck').hidden = false;
        e.currentTarget.hidden = true;
        $('why').focus();
      }, { id: 'looks-wrong', 'data-k': 'looks-wrong' }) : null,
      m.checked ? h('span', { class: 'fh-acts__note', text: m.checked }) : null
    ]);
  }

  /* Everything after the spread, in order. */
  function afterSpread(v) {
    var r = v.result;
    return findingRows(r).concat([moreBox(r), v.can && v.can.dispute ? recheckRow(v) : null, errHere(), resultActs(v)]);
  }

  function resultPage(v, play) {
    var r = v.result;
    var kind = F.kindOf(r.chip) || 'none';
    var spread = h('div', { class: 'fh-spread', id: 'res', tabindex: '-1', 'aria-label': spreadLabel(r), 'data-play': play }, [
      callSide(v), F.mark(kind), runSide(r)
    ]);
    return [resultHead(v, kind, r.chip_label), spread].concat(afterSpread(v));
  }

  function waitLine(v) {
    var names = ((v.call || {}).names || []).slice();
    var t = v.trace && v.trace.title ? /^(.+?)(?:: | is failing\.)/.exec(v.trace.title) : null;
    if (t) names.push(t[1]);
    var frag = F.mixed(v.status_line || '', names);
    Array.prototype.forEach.call(frag.querySelectorAll('.fh-fact'), function (s) {
      frag.replaceChild(h('b', { text: s.textContent }), s);
    });
    return h('p', { class: 'fh-wait' }, frag);
  }

  function waitingPage(v) {
    return [
      resultHead(v, null),
      h('div', { class: 'fh-spread fh-spread--wait' }, [
        callSide(v),
        h('div', { class: 'fh-spread__side fh-spread__run' }, [head('The run'), waitLine(v)])
      ]),
      errHere(),
      h('div', { class: 'fh-acts' }, back(true))
    ];
  }

  /* A locked Brief line stays in the logbook when the check never ran. */
  function closedCall(v) {
    var call = v.call;
    if (v.kind !== 'brief' || !call || !call.said) return null;
    return finding(v.said_label || 'Your check', [
      lineAnswer(call.said),
      call.locked_at ? h('p', { class: 'fh-finding__time' }, h('time', { text: 'locked ' + hms(call.locked_at) })) : null
    ]);
  }

  function closedPage(v) {
    var can = v.can || {};
    var r = v.result;
    var skipped = v.state === 'skipped' || (v.held && v.held.kind === 'skip');
    var text;
    if (v.held && v.held.kind === 'skip') text = 'Skipped.';
    else if (r && r.reason) text = r.reason;
    else text = v.status_line || (v.state === 'skipped' ? 'Skipped.' : '');
    // The verdict already says Not scored: the sentence does not repeat it.
    if (r) text = String(text).replace(/^Not scored\.\s*/, '');
    return [
      resultHead(v, r ? 'none' : null, 'Not scored'),
      closedCall(v),
      finding(skipped ? 'Skipped' : 'Closed', [h('p', { class: 'fh-finding__text', text: text })]),
      errHere(),
      h('div', { class: 'fh-acts' }, [
        back(true),
        can.undo ? btn('Undo', 'quiet', function () { act(v, 'undo', {}, 'Undone.', 'undo'); }, { 'data-k': 'undo' }) : null
      ])
    ];
  }

  function layoutOf(v) {
    var held = v.held || null;
    var can = v.can || {};
    if (v.result && v.result.ran_at) return 'result';
    if (v.state === 'open' || (held && held.kind === 'pick') || (isBriefConfirm(v) && can.lock)) return 'sheet';
    if (held && held.kind === 'skip') return 'closed';
    if (v.state === 'sealed' && !v.result && v.call) return 'waiting';
    return 'closed';
  }

  function same(v) {
    var copy = JSON.parse(JSON.stringify(v));
    if (copy.result) delete copy.result.fresh;
    return JSON.stringify(copy);
  }

  /* The run arrives on a waiting page: the call side stays as it is. */
  function arrive(v) {
    var r = v.result;
    var spread = D.querySelector('.fh-spread--wait');
    var main = $('main');
    var kind = F.kindOf(r.chip) || 'none';
    var oldRun = spread.querySelector('.fh-spread__run');
    main.replaceChild(resultHead(v, kind, r.chip_label), main.querySelector('.fh-head'));
    spread.classList.remove('fh-spread--wait');
    spread.id = 'res';
    spread.setAttribute('tabindex', '-1');
    spread.setAttribute('aria-label', spreadLabel(r));
    spread.setAttribute('data-play', '');
    spread.insertBefore(F.mark(kind), oldRun);
    spread.replaceChild(runSide(r), oldRun);
    while (spread.nextSibling) main.removeChild(spread.nextSibling);
    add(main, afterSpread(v));
  }

  function drawQuestion(v, layout) {
    var main = $('main');
    clear(main);
    if (layout === 'sheet') {
      add(main, [h('h1', { class: 'fh-vh', text: v.kind_label }), sheet(v)]);
      return;
    }
    if (layout === 'result') {
      var play = !!v.result.fresh && !S.played[v.ref];
      add(main, resultPage(v, play));
      S.played[v.ref] = true;
      return;
    }
    add(main, layout === 'waiting' ? waitingPage(v) : closedPage(v));
  }

  function renderQuestion(v, force) {
    // A view fetched for a question this page no longer shows is dropped.
    if (S.route && S.route.name === 'question' && v.ref && v.ref !== S.route.ref) return;
    var json = same(v);
    if (force !== true && S.page !== 'blank' && S.view && S.view.ref === v.ref && json === S.viewJson) return;
    var before = S.view && S.view.ref === v.ref ? S.page : null;
    var layout = layoutOf(v);
    if (!force && !S.focus && D.activeElement && D.activeElement.getAttribute) S.focus = D.activeElement.getAttribute('data-k');
    if (layout === 'result' && before === 'waiting' && D.querySelector('.fh-spread--wait')) {
      arrive(v);
      S.played[v.ref] = true;
    } else {
      drawQuestion(v, layout);
    }
    S.view = v;
    S.viewJson = json;
    S.page = layout;
    F.title([no(v.no), v.kind_label].join(' '));
    F.placeFor(v.where);
    F.fitFacts($('main'));
    // A sheet that became a result or a wait is a new page: start it at its head.
    if (before && before !== layout && window.scrollY > 0) window.scrollTo(0, 0);
    if (layout === 'result' && before !== 'result') {
      var res = $('res');
      if (res) res.focus({ preventScroll: true });
      say(spreadLabel(v.result));
      S.focus = null;
      return;
    }
    F.restoreFocus($('main'));
  }

  /* ------------------------------------------------------------ journal */

  function renderJournal(v) {
    var main = $('main');
    clear(main);
    S.page = 'journal';
    var entries = v.entries || [];
    var rows = entries.map(function (e) {
      if (e.kind === 'Note') {
        return noteRow(e, e.time, e.title || ((e.rows || [])[0] || {}).text || e.task);
      }
      return entryRow(e, e.time);
    });
    if (!rows.length) {
      var next = S.inbox && S.inbox.next_no ? no(S.inbox.next_no) : null;
      rows = [blankRow(next || 'No entries', next ? 'next' : null, 'No calls or notes yet.')];
    }
    F.title('Journal');
    add(main, [
      h('h1', { class: 'fh-vh', text: 'Journal' }),
      sec('Journal', entries.length ? plural(entries.length, 'entry', 'entries') + ', newest first' : null, v.scope ? ' · ' + v.scope : null),
      ledger(rows)
    ]);
    F.fitFacts(main);
  }

  /* ------------------------------------------------------------ skills */

  function place(el, row, col, span) {
    el.style.gridRow = String(row);
    el.style.gridColumn = span ? col + ' / span ' + span : String(col);
    return el;
  }

  function dateRuns(calls) {
    var runs = [];
    calls.forEach(function (c, i) {
      var last = runs[runs.length - 1];
      if (last && last.day === c.day) last.n += 1;
      else runs.push({ day: c.day, start: i, n: 1 });
    });
    return runs;
  }

  function trackLabel(r) {
    var text = plural(r.total, 'call', 'calls') + '. You matched ' + r.matched + '.';
    if (!r.fixed_answer) return text;
    var c = (r.calls || []).filter(function (x) { return x.catch; }).length;
    return text + ' The easy answer would have matched ' + r.fixed_count + '. ' + c + ' of yours were catches.';
  }

  function track(r) {
    var all = r.calls || [];
    var calls = all.slice(-24);
    var easy = !!r.fixed_answer;
    var el = h('div', { class: 'fh-track', role: 'img', 'aria-label': trackLabel(r), 'data-skill': String(r.n) });
    prop(el, '--n', calls.length);
    calls.forEach(function (c, i) { add(el, place(h('span', { class: 'catch', text: c.catch ? '▾' : null }), 1, i + 2)); });
    add(el, place(h('span', { class: 'lb lb--you', text: 'You' }), 2, 1));
    calls.forEach(function (c, i) {
      add(el, prop(place(h('i', { class: 'you ' + (c.you === 'match' ? 'on' : 'miss') }), 2, i + 2), '--i', i));
    });
    if (easy) {
      add(el, place(h('span', { class: 'lb', text: 'Easy' }), 3, 1));
      calls.forEach(function (c, i) { add(el, prop(place(h('i', { class: c.easy ? 'easy on' : 'easy' }), 3, i + 2), '--i', i)); });
    }
    var runs = dateRuns(calls);
    runs.forEach(function (run) {
      // One label for the whole track: the full day, let out past its column.
      var whole = run.n >= 2 || runs.length === 1;
      var text = whole ? run.day : String(run.day).split(' ')[0];
      add(el, place(h('span', { class: whole && run.n < 2 ? 'date date--out' : 'date', text: text }), 4, run.start + 2, run.n));
    });
    return el;
  }

  function figures(r) {
    return h('div', { class: 'fh-figs' }, [
      h('div', { class: 'fh-fig fh-fig--you' }, [
        h('div', { class: 'fh-fig__n' }, [h('b', { text: String(r.matched) }), ' ', h('span', { text: 'of ' + r.total })]),
        h('p', { class: 'fh-fig__cap', text: 'of your calls matched' })
      ]),
      r.fixed_answer ? h('div', { class: 'fh-fig' }, [
        h('div', { class: 'fh-fig__n' }, [String(r.fixed_count), ' ', h('span', { text: 'of ' + r.total })]),
        h('p', { class: 'fh-fig__cap', text: 'if you had always said "' + r.fixed_answer + '"' })
      ]) : null
    ]);
  }

  function level(r) {
    if (r.level === 'shown') return h('span', { class: 'fh-level' }, [h('b', { text: 'Shown' }), ' · since ' + r.shown_since]);
    if (r.level === 'too_few') {
      return h('span', { class: r.days ? 'fh-level' : 'fh-level fh-level--none' }, ['Too few calls · ', h('b', { text: r.days + ' of 2' })]);
    }
    return h('span', { class: 'fh-level fh-level--none' }, h('b', { text: 'No level yet' }));
  }

  function skillCounts(r) {
    var text = r.asked || '';
    if (r.newest) text += ' ' + r.newest.charAt(0).toUpperCase() + r.newest.slice(1) + '.';
    return h('p', { class: 'fh-skill__counts', text: text });
  }

  function skillRow(r) {
    var calls = r.calls || [];
    // "since 16 Nov" stays whole: the line breaks before "since", never inside the date.
    var since = calls.length ? [plural(r.total, 'call', 'calls') + ' ', h('span', { class: 'fh-nobr', text: 'since ' + r.since })] : 'no calls yet';
    return h('li', { class: 'fh-row fh-row--skill', 'aria-label': r.name + ': ' + r.level_line + ', ' + r.newest }, [
      margin('Skill ' + r.n, since),
      h('div', null, [
        h('div', { class: 'fh-row__head' }, [h('h3', { class: 'fh-row__title', text: r.name }), level(r)]),
        // With no calls there is no track and no figure: a count of nothing is not a headline.
        r.total ? h('div', { class: 'fh-skill__top' }, [calls.length ? track(r) : null, figures(r)]) : null,
        calls.length > 24 ? h('p', { class: 'fh-track__more', text: 'newest 24 of ' + calls.length }) : null,
        skillCounts(r),
        r.level === 'none' ? h('p', { class: 'fh-text fh-skill__why', text: r.level_line }) : null,
        h('div', { class: 'fh-skill__note' }, [
          h('div', null, [h('span', { class: 'fh-label', text: 'Covers' }), r.covers]),
          h('div', null, [h('span', { class: 'fh-label', text: 'No evidence on' }), r.no_evidence])
        ])
      ])
    ]);
  }

  var watcher = null;

  function watchTallies() {
    if (watcher) { watcher.disconnect(); watcher = null; }
    if (!window.IntersectionObserver) return;
    watcher = new IntersectionObserver(function (seen) {
      seen.forEach(function (e) {
        if (!e.isIntersecting) return;
        var n = e.target.getAttribute('data-skill');
        watcher.unobserve(e.target);
        if (S.tallies[n]) return;
        S.tallies[n] = true;
        e.target.setAttribute('data-play', '');
      });
    }, { threshold: 0.6 });
    Array.prototype.forEach.call(D.querySelectorAll('.fh-track'), function (t) {
      if (!S.tallies[t.getAttribute('data-skill')]) watcher.observe(t);
    });
  }

  var KEY = [
    ['on', 'your call matched'], ['miss', 'did not match'], ['easy', 'the easy answer would have matched'],
    [null, 'it would not'], ['catch', 'a catch: you matched and the easy answer did not']
  ];

  function renderSkills(v) {
    var main = $('main');
    clear(main);
    S.page = 'skills';
    F.title('Skills');
    add(main, [
      h('h1', { class: 'fh-vh', text: 'Skills' }),
      sec('Skills', 'Checked by a run.', ' · all projects'),
      h('ul', { class: 'fh-key', 'aria-label': 'Key' }, KEY.map(function (k) {
        return h('li', null, [h('i', { class: k[0], text: k[0] === 'catch' ? '▾' : null }), k[1]]);
      })),
      ledger((v.rows || []).map(skillRow)),
      (v.legend || []).length ? finding('Shown', v.legend.map(function (t) { return h('p', { class: 'fh-text', text: t }); }), true) : null
    ]);
    watchTallies();
  }

  /* ------------------------------------------------------------ settings */

  function limitText(s) {
    if (s % 60 === 0) return (s / 60) + (s === 60 ? ' minute' : ' minutes');
    return s + ' seconds';
  }

  function dialName(value) {
    var d = DIAL.filter(function (x) { return x[0] === value; })[0];
    return d ? d[1] : String(value);
  }

  /* The change line of the confirm step: what the setting is, and from what to what. */
  function changeLine(changes, v) {
    if ('dial' in changes) return ['The dial', dialName(v.dial) + ' to ' + dialName(changes.dial)];
    if ('daily_limit' in changes) return ['Questions while building', v.daily_limit + ' to ' + changes.daily_limit + ' a day'];
    if ('findings_to_agent' in changes) return ['Send findings to my agent', 'off to on'];
    if ('test_command' in changes) return ['Test command', String(changes.test_command)];
    return [Object.keys(changes)[0], String(changes[Object.keys(changes)[0]])];
  }

  /* The engine names a setting by its field ("test_command must be a non-empty
     string."): the Room says it in words. Any other message is already plain. */
  var PLAIN = {
    test_command: 'The test command cannot be empty.',
    high_stakes_add: 'Write a path to add, such as refunds/**.',
    high_stakes_remove: 'That path cannot be removed.',
    dial: 'The dial is Off, Notes only, Standard or Deep.',
    daily_limit: 'Questions while building is 1, 2 or 3 a day.',
    quiet: 'Quiet for this project is on or off.',
    quiet_today: 'Quiet today is on or off.',
    findings_to_agent: 'Send findings to my agent is on or off.'
  };

  function plainError(message, changes) {
    var text = String(message || '');
    var key = Object.keys(changes || {})[0];
    if (key && PLAIN[key] && text.indexOf(key + ' ') === 0) return PLAIN[key];
    if (/^(Unknown (project )?setting|Not a project id)/.test(text)) return F.INTERNAL;
    if (/^No settings for project /.test(text)) return 'This project has no settings yet. Run Firsthand in that project first.';
    return text;
  }

  function save(changes, project, confirm, row, key) {
    S.focus = key || null;
    return F.api('POST', '/api/settings', { changes: changes, project: project, confirm: !!confirm }).then(function (nv) {
      S.confirm = null;
      F.setErr(null);
      renderSettings(nv);
      say('Saved.');
      return F.loadShell();
    }, function (err) {
      if (err.code === 'no_session' || err.code === 'unreachable') return null;
      return F.api('GET', withProject('/api/settings')).then(function (nv) {
        if (err.code === 'confirm') {
          F.setErr(null);
          S.confirm = { changes: changes, project: project, row: row, key: key, message: err.message, line: changeLine(changes, nv) };
          S.focus = 'confirm';
          renderSettings(nv);
          say(err.message);
        } else {
          S.confirm = null;
          F.setErr({ message: plainError(err.message, changes) }, row);
          renderSettings(nv);
        }
      });
    });
  }

  function confirmStep() {
    var c = S.confirm;
    return h('li', { class: 'fh-confirm', role: 'group', 'aria-label': 'Confirm' }, [
      h('span', { class: 'fh-label' }, h('b', { text: 'Confirm' })),
      h('div', null, [
        h('p', { class: 'fh-confirm__text', text: c.message }),
        facts([fact(c.line[0], c.line[1])]),
        h('div', { class: 'fh-acts' }, [
          btn('Confirm', null, function () { save(c.changes, c.project, true, c.row, c.key); }, { 'data-k': 'confirm' }),
          btn('Cancel', 'quiet', function () {
            S.confirm = null;
            S.focus = c.key;
            renderSettings(S.settings);
          })
        ])
      ])
    ]);
  }

  /* One setting: its name in the margin, its controls, its error, then a confirm step if one is open. */
  function setRow(id, name, kids) {
    var err = S.err && S.err.where === id ? errHere() : null;
    var out = [h('li', { class: 'fh-row', 'data-row': id }, [margin(name), h('div', { class: 'fh-set' }, kids.concat([err]))])];
    if (S.confirm && S.confirm.row === id) out.push(confirmStep());
    return out;
  }

  /* A radio group in Settings. An arrow key moves the selection only: the browser
     focuses and checks the next radio and sends it a click in the same task, and the
     saved radio is checked again, so the focus ring marks the move and nothing is
     saved. Space on the focused radio, Enter (the group is a form) or a click saves it.
     The script has no key handlers. */
  function radioGroup(props, name, items, saved, onpick) {
    var pointer = false;
    var moved = null;
    var inputs = items.map(function (it) {
      return h('input', { type: 'radio', name: name, value: it[0], checked: saved === it[0], 'data-k': name + '-' + it[0] });
    });
    function pick(value) { if (value !== saved) onpick(value); }
    inputs.forEach(function (input) {
      input.addEventListener('focus', function () {
        moved = input;
        setTimeout(function () { if (moved === input) moved = null; }, 0);
      });
      input.addEventListener('click', function () {
        var by = pointer;
        pointer = false;
        if (by || moved !== input) { pick(input.value); return; }
        inputs.forEach(function (x) { x.checked = x.value === saved; });
      });
    });
    // A press anywhere on the cell: the span is drawn over the radio.
    var group = h('form', props, inputs.map(function (input, i) {
      return h('label', { onpointerdown: function () { pointer = true; } }, [input, h('span', { text: items[i][1] })]);
    }).concat([h('button', { type: 'submit', class: 'fh-vh', tabindex: '-1', 'aria-hidden': 'true', text: 'Save' })]));
    group.addEventListener('submit', function (e) {
      e.preventDefault();
      var on = inputs.filter(function (x) { return x === D.activeElement; })[0] || inputs.filter(function (x) { return x.checked; })[0];
      if (on) pick(on.value);
    });
    return group;
  }

  function check(key, text, checked, onchange) {
    var input = h('input', { type: 'checkbox', checked: checked, 'data-k': key });
    input.addEventListener('change', function () { onchange(input.checked); });
    return h('label', { class: 'fh-check' }, [input, h('span', { text: text })]);
  }

  function howMuch(v) {
    var pid = v.project ? v.project.id : null;
    var quiet = v.quiet || {};
    var dial = radioGroup({ class: 'fh-seg', role: 'radiogroup', 'aria-label': 'The dial' }, 'dial', DIAL, v.dial, function (value) {
      save({ dial: value }, null, false, 'dial', 'dial-' + value);
    });
    var dialFacts = facts(DIAL.map(function (d, i) { return fact(d[1], d[2], { key: v.dial === d[0], i: i }); }));
    var limit = radioGroup({ class: 'fh-seg fh-seg--num', role: 'radiogroup', 'aria-label': 'Questions while building, a day' }, 'limit',
      [['1', '1'], ['2', '2'], ['3', '3']], String(v.daily_limit), function (value) {
        save({ daily_limit: Number(value) }, null, false, 'limit', 'limit-' + value);
      });
    return [
      sec('How much'),
      ledger([].concat(
        setRow('dial', 'The dial', [dial, dialFacts]),
        // The cells and their unit wrap as one, so "a day (up to 3)." is never alone on a line.
        setRow('limit', 'Questions', [h('p', { class: 'fh-inline' }, ['Questions while building: ',
          h('span', { class: 'fh-inline__unit' }, [limit, ' a day (up to 3).'])])]),
        setRow('quiet', 'Quiet', [h('div', null, [
          check('quiet-today', 'Today', !!quiet.today, function (on) { save({ quiet_today: on }, null, false, 'quiet', 'quiet-today'); }),
          pid ? check('quiet-here', 'This project', !!quiet.here, function (on) { save({ quiet: on }, pid, false, 'quiet', 'quiet-here'); }) : null
        ])]),
        setRow('findings', 'Findings', [check('findings', 'Send findings to my agent', !!v.findings_to_agent, function (on) {
          save({ findings_to_agent: on }, null, false, 'findings', 'findings');
        })])
      ))
    ];
  }

  function fieldRow(id, labelText, value, buttonText, onsave, placeholder) {
    var input = h('input', { class: 'fh-input', id: id, type: 'text', spellcheck: 'false', 'data-k': id, placeholder: placeholder || null });
    input.value = value || '';
    // A form, so Enter in the field saves as the button does.
    return h('form', { class: 'fh-field', onsubmit: function (e) { e.preventDefault(); onsave(input); } }, [
      h('label', { class: 'fh-vh', for: id, text: labelText }),
      h('div', { class: 'fh-fieldrow' }, [input, h('button', { type: 'submit', class: 'fh-btn fh-btn--second', 'data-k': id + '-save', text: buttonText })])
    ]);
  }

  function thisProject(p) {
    var cmd = fieldRow('cmd', 'Test command', p.test_command, 'Change', function (input) {
      // An empty command is refused here, before any confirm step is asked for.
      if (input.value.trim()) { save({ test_command: input.value }, p.id, false, 'cmd', 'cmd-save'); return; }
      S.confirm = null;
      F.setErr({ message: PLAIN.test_command }, 'cmd');
      S.focus = 'cmd';
      renderSettings(S.settings);
    });
    add(cmd, h('p', { class: 'fh-field__hint', text: 'Checks stop after ' + limitText(p.check_time_limit_s) + '.' }));
    var globs = (p.high_stakes || []).map(function (g) {
      return h('li', null, [h('span', { class: 'k', text: g }), h('span', { class: 'ld' }),
        btn('Remove', 'quiet', function () { save({ high_stakes_remove: g }, p.id, false, 'globs', 'glob'); }, { 'aria-label': 'Remove ' + g })]);
    });
    var addGlob = fieldRow('glob', 'Add a path', '', 'Add a path', function (input) {
      var g = input.value.trim();
      if (g) save({ high_stakes_add: g }, p.id, false, 'globs', 'glob');
      else input.focus();
    }, 'refunds/**');
    return [
      sec('This project', null, ' · ' + p.name),
      ledger([].concat(
        setRow('cmd', 'Test command', [cmd]),
        setRow('globs', 'High-stakes paths', [h('div', null, [globs.length ? h('ul', { class: 'fh-list' }, globs) : null, addGlob])])
      ))
    ];
  }

  function renderSettings(v) {
    var main = $('main');
    if (!S.focus && D.activeElement && main.contains(D.activeElement)) S.focus = D.activeElement.getAttribute('data-k');
    clear(main);
    S.settings = v;
    S.page = 'settings';
    F.title('Settings');
    add(main, [h('h1', { class: 'fh-vh', text: 'Settings' })]);
    add(main, howMuch(v));
    if (v.project) add(main, thisProject(v.project));
    add(main, [
      sec('Your record'),
      ledger(setRow('record', 'Kept at', [h('p', { class: 'fh-text' }, [
        h('span', { class: 'fh-fact', text: v.record }), '. A git repo on this computer. Plain files. No remote.'
      ])]))
    ]);
    F.restoreFocus(main);
  }

  window.FH.renderInbox = renderInbox;
  window.FH.renderQuestion = renderQuestion;
  window.FH.renderJournal = renderJournal;
  window.FH.renderSkills = renderSkills;
  window.FH.renderSettings = renderSettings;
  F.start();
}());
