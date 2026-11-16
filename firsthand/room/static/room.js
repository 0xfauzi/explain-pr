/* The Room page, part one: helpers, the API, the frame of every page, routing and
   live updates. The screens are in room-views.js. It renders only the JSON the
   Firsthand engine returns and decides nothing about results: a result is drawn
   when the API gives one. Every string from the API is set with textContent. No
   markup is ever built from text. Nothing is loaded from anywhere but this server. */
(function () {
  'use strict';

  var D = document;
  var NS = 'http://www.w3.org/2000/svg';
  var NO_SESSION = 'This page needs a session. Run: firsthand room';
  var LOST = 'The Room cannot reach Firsthand on this computer. Start it with: firsthand room';
  var INTERNAL = 'Something went wrong inside Firsthand. Nothing was changed.';
  var DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  /* drawn: refs whose sheet has been drawn (the highlighter passes once).
     played: refs whose result has printed. tallies: skills whose track has filled. */
  var S = {
    token: null, inbox: null, view: null, viewJson: null, route: null, lost: false, es: null,
    draft: null, err: null, focus: null, settings: null, confirm: null, page: null,
    drawn: {}, played: {}, tallies: {}
  };

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
    if (kids === null || kids === undefined) return el;
    if (!Array.isArray(kids)) kids = [kids];
    kids.forEach(function (c) {
      if (c === null || c === undefined || c === false) return;
      el.appendChild(typeof c === 'string' ? D.createTextNode(c) : c);
    });
    return el;
  }

  function clear(el) { while (el.firstChild) el.removeChild(el.firstChild); }

  /* A custom property or a grid place, through the CSSOM: never a style attribute. */
  function prop(el, name, value) { el.style.setProperty(name, String(value)); return el; }

  function label(text, rest) { return h('span', { class: 'fh-label' }, [h('b', { text: text }), rest || null]); }

  function sec(text, right, rest) {
    return h('div', { class: 'fh-sec' }, [label(text, rest), right ? h('span', { class: 'fh-sec__n', text: right }) : null]);
  }

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

  /* ------------------------------------------------------------ two hands */

  /* Every occurrence of a name from `names` is set in the fact face, longest first. */
  function mixed(text, names) {
    var frag = D.createDocumentFragment();
    var list = (names || []).filter(function (n) { return n; }).slice().sort(function (a, b) { return b.length - a.length; });
    var i = 0;
    var start = 0;
    text = text || '';
    while (i < text.length) {
      var hit = null;
      for (var j = 0; j < list.length; j++) {
        if (text.substr(i, list[j].length) === list[j]) { hit = list[j]; break; }
      }
      if (!hit) { i += 1; continue; }
      if (i > start) frag.appendChild(D.createTextNode(text.slice(start, i)));
      frag.appendChild(h('span', { class: 'fh-fact', text: hit }));
      i += hit.length;
      start = i;
    }
    if (start < text.length) frag.appendChild(D.createTextNode(text.slice(start)));
    return frag;
  }

  /* Every "n of m" in the fact face. */
  function counts(text) {
    var frag = D.createDocumentFragment();
    var re = /\d+ of \d+/g;
    var last = 0;
    var m;
    text = text || '';
    while ((m = re.exec(text)) !== null) {
      if (m.index > last) frag.appendChild(D.createTextNode(text.slice(last, m.index)));
      frag.appendChild(h('span', { class: 'fh-fact', text: m[0] }));
      last = m.index + m[0].length;
    }
    if (last < text.length) frag.appendChild(D.createTextNode(text.slice(last)));
    return frag;
  }

  /* ------------------------------------------------------------ verdict marks */

  var MARKS = {
    match: { rect: [0, 0, 28, 28], bars: 'M8 11h12M8 17h12' },
    miss: { rect: [0.75, 0.75, 26.5, 26.5], bars: 'M8 11h12M8 17h12M17.5 6.5l-7 15' },
    none: { rect: [0.75, 0.75, 26.5, 26.5], bars: 'M8 11h12M8 17h12' }
  };
  var KINDS = { matched: 'match', did_not_match: 'miss', not_scored: 'none' };

  function mark(kind) {
    var d = MARKS[kind];
    var svg = D.createElementNS(NS, 'svg');
    svg.setAttribute('class', 'fh-m fh-m--' + kind);
    svg.setAttribute('viewBox', '0 0 28 28');
    svg.setAttribute('aria-hidden', 'true');
    var rect = D.createElementNS(NS, 'rect');
    rect.setAttribute('class', 'sq');
    ['x', 'y', 'width', 'height'].forEach(function (a, i) { rect.setAttribute(a, String(d.rect[i])); });
    var path = D.createElementNS(NS, 'path');
    path.setAttribute('class', 'bar');
    path.setAttribute('d', d.bars);
    svg.appendChild(rect);
    svg.appendChild(path);
    return svg;
  }

  function kindOf(chip) { return KINDS[chip] || null; }

  function verdict(kind, words) {
    return h('span', { class: 'fh-verdict fh-verdict--' + kind }, [mark(kind), words]);
  }

  /* ------------------------------------------------------------ numbers and times */

  function no(n) {
    if (n === null || n === undefined) return 'No. ----';
    var s = String(n);
    while (s.length < 4) s = '0' + s;
    return 'No. ' + s;
  }

  function two(n) { return n < 10 ? '0' + n : String(n); }

  function when(stamp) {
    if (!stamp) return null;
    var d = new Date(stamp);
    return isNaN(d.getTime()) ? null : d;
  }

  function hms(stamp) {
    var d = when(stamp);
    return d ? two(d.getHours()) + ':' + two(d.getMinutes()) + ':' + two(d.getSeconds()) : '';
  }

  function hm(stamp) {
    var d = when(stamp);
    return d ? two(d.getHours()) + ':' + two(d.getMinutes()) : '';
  }

  /* A margin time: HH:MM today, D Mon HH:MM on another day. */
  function marginTime(stamp) {
    var d = when(stamp);
    if (!d) return '';
    var now = new Date();
    if (d.toDateString() === now.toDateString()) return hm(stamp);
    return d.getDate() + ' ' + MONTHS[d.getMonth()] + ' ' + hm(stamp);
  }

  function folioDate() {
    var d = new Date();
    return DAYS[d.getDay()] + ' ' + d.getDate() + ' ' + MONTHS[d.getMonth()] + ' ' + d.getFullYear() + ' \u00b7 ' + location.host;
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
        if (r.ok) {
          if (S.lost) setLost(false);
          return data;
        }
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

  /* ------------------------------------------------------------ the frame */

  function route() {
    var p = location.pathname;
    var m = /^\/([qr])\/([A-Za-z0-9_-]{1,64})$/.exec(p);
    if (m) return { name: 'question', ref: m[2], tab: m[1] === 'q' ? 'inbox' : 'journal' };
    if (p === '/journal' || p === '/skills' || p === '/settings') return { name: p.slice(1), tab: p.slice(1) };
    return { name: 'inbox', tab: 'inbox' };
  }

  function markTabs(tab) {
    Array.prototype.forEach.call(D.querySelectorAll('[data-tab]'), function (a) {
      a.setAttribute('href', withProject(a.getAttribute('href').split('?')[0]));
      if (a.getAttribute('data-tab') === tab) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    });
    var word = D.querySelector('.fh-wordmark');
    if (word) word.setAttribute('href', withProject('/'));
  }

  /* A whole page in one blank ledger row: no session, not reachable, not found, an error. */
  function blankPage(margin, title, kids, heading) {
    var main = $('main');
    clear(main);
    S.view = null;
    S.viewJson = null;
    S.page = 'blank';
    add(main, [
      h('h1', { class: 'fh-vh', text: heading || 'The Room' }),
      h('ol', { class: 'fh-ledger' }, h('li', { class: 'fh-row fh-row--blank' }, [
        h('div', { class: 'fh-row__margin' }, h('b', { text: margin })),
        h('div', null, [h('h2', { class: 'fh-row__title', text: title })].concat(kids || []))
      ]))
    ]);
  }

  function noSession(message) {
    // The server's text names the command as it is typed on this computer.
    var text = message || NO_SESSION;
    var at = text.indexOf('Run in a terminal: ');
    var kids;
    if (at >= 0) {
      var cmd = text.slice(at + 'Run in a terminal: '.length).replace(/\.$/, '');
      kids = [h('p', { class: 'fh-text', text: 'Run in a terminal:' }), h('ol', { class: 'fh-cmds' }, h('li', { text: cmd }))];
    } else {
      kids = [h('p', { class: 'fh-text', text: text })];
    }
    $('tabs').hidden = true;
    $('notice').hidden = true;
    $('quiet').hidden = true;
    $('proj').textContent = ' / not signed in';
    $('asked').textContent = '';
    if (S.es) { S.es.close(); S.es = null; }
    S.noSession = true;
    blankPage('No session', 'This page needs a session.', kids);
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
      var sel = h('select', { class: 'fh-select', 'aria-label': 'Project', onchange: function () {
        location.search = '?project=' + encodeURIComponent(sel.value);
      } }, list.map(function (p) {
        return h('option', { value: p.id, text: p.name });
      }));
      sel.value = inbox.project.id;
      add(proj, [' / ', sel]);
    } else if (inbox.project) {
      proj.textContent = ' / ' + inbox.project.name;
    }
    var q = $('quiet');
    var quiet = inbox.state ? inbox.state.quiet : null;
    q.hidden = !inbox.project;
    q.querySelector('b').textContent = quiet ? 'on' : 'off';
    q.setAttribute('aria-pressed', quiet ? 'true' : 'false');
    q.disabled = quiet === 'session';
    var n = (inbox.now || []).length;
    $('count').textContent = n ? String(n) : '';
    $('count').hidden = !n;
    $('asked').textContent = inbox.closing || '';
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

  function notice(role, name, text, action) {
    return h('div', { class: 'fh-notice', role: role }, [label(name), h('p', { class: 'fh-notice__text' }, text), action || null]);
  }

  function drawNotice() {
    var box = $('notice');
    clear(box);
    var state = S.inbox && S.inbox.state ? S.inbox.state : {};
    var text = state.notice || '';
    var el = null;
    if (S.lost) {
      el = notice('alert', 'Not reachable', ['The Room cannot reach Firsthand on this computer. Start it with: ',
        h('span', { class: 'fh-fact', text: 'firsthand room' })]);
    } else if (state.dial === 'off' && text) {
      el = notice('status', 'Off', text.replace(/\s*Turn on$/, ''),
        h('a', { class: 'fh-btn fh-btn--quiet', href: withProject('/settings'), text: 'Turn on' }));
    } else if (state.quiet && text) {
      el = notice('status', 'Quiet', text.replace(/\s*Undo$/, ''), state.quiet === 'session' ? null
        : h('button', { type: 'button', class: 'fh-btn fh-btn--quiet', text: 'Undo', onclick: toggleQuiet }));
    }
    box.hidden = !el || S.noSession;
    if (el) box.appendChild(el);
  }

  function loadShell() {
    return api('GET', withProject('/api/inbox')).then(function (inbox) {
      shell(inbox);
      return inbox;
    });
  }

  /* ------------------------------------------------------------ errors and focus */

  /* The engine's message, shown under the control that was used. */
  function errLine() {
    if (!S.err) return null;
    return h('p', { class: 'fh-err', role: 'alert' }, [h('b', { text: 'Not taken' }), h('span', { text: S.err.message })]);
  }

  function setErr(err, where) {
    S.err = err ? { message: err.message, where: where || null } : null;
    if (err) say(err.message);
  }

  /* After a redraw, focus returns to the control that was pressed, else to the first
     control of what replaced it. */
  function restoreFocus(scope) {
    var key = S.focus;
    S.focus = null;
    if (!key) return;
    var el = D.querySelector('[data-k="' + key.replace(/["\\]/g, '') + '"]');
    if (el && !el.disabled) { el.focus({ preventScroll: true }); return; }
    var first = (scope || $('main')).querySelector('button:not([disabled]), input:not([disabled]), a[href], textarea');
    if (first) first.focus({ preventScroll: true });
  }

  /* ------------------------------------------------------------ routing and live updates */

  function render() {
    var r = S.route;
    var V = window.FH;
    if (r.name === 'question') return api('GET', '/api/q/' + encodeURIComponent(r.ref)).then(V.renderQuestion);
    if (r.name === 'journal') return api('GET', withProject('/api/journal')).then(V.renderJournal);
    if (r.name === 'skills') return api('GET', withProject('/api/skills')).then(V.renderSkills);
    if (r.name === 'settings') return api('GET', withProject('/api/settings')).then(V.renderSettings);
    return (S.inbox ? Promise.resolve(S.inbox) : loadShell()).then(V.renderInbox);
  }

  function typing() {
    var a = D.activeElement;
    return !!a && (a.tagName === 'TEXTAREA' || (a.tagName === 'INPUT' && a.type === 'text'));
  }

  function loadError(err) {
    if (err.code === 'no_session') return;
    if (err.code === 'unreachable') {
      if (S.page === 'blank' || !$('main').firstChild) firstLost();
      return;
    }
    if (err.code === 'not_found' && S.route.name === 'question') {
      blankPage('Not found', err.message, [h('p', { class: 'fh-acts' },
        h('a', { class: 'fh-btn fh-btn--second', href: withProject('/'), text: 'Back to the build' }))]);
      return;
    }
    blankPage('Error', err.message || INTERNAL);
  }

  function refresh() {
    if (typing() || S.noSession) return;
    if (S.route.name === 'inbox') S.inbox = null;
    render().catch(loadError);
  }

  function onNotice(n) {
    var r = S.route;
    if (S.noSession) return;
    if (n.topic === 'inbox' || n.topic === 'settings') {
      loadShell().then(function () { if (r.name === 'inbox') window.FH.renderInbox(S.inbox); }).catch(function () {});
    }
    if (r.name === 'question' && n.topic === 'question') {
      if (!n.id || !S.view || n.id === S.view.id) refresh();
      return;
    }
    if (r.name === 'settings' && n.topic === 'settings') refresh();
    if (r.name === 'journal' || r.name === 'skills') refresh();
  }

  function listen() {
    if (!window.EventSource || S.noSession) return;
    var es = new EventSource('/api/events');
    S.es = es;
    es.onopen = function () { setLost(false); };
    es.onmessage = function (ev) {
      var n;
      try { n = JSON.parse(ev.data); } catch (e) { return; }
      onNotice(n);
    };
    es.onerror = function () {
      if (S.noSession) return;
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

  function firstLost() {
    $('notice').hidden = true;
    blankPage('Not reachable', 'The Room cannot reach Firsthand on this computer.', [
      h('p', { class: 'fh-text', text: 'Start it with:' }), h('ol', { class: 'fh-cmds' }, h('li', { text: 'firsthand room' }))
    ]);
  }

  function boot() {
    S.route = route();
    markTabs(S.route.tab);
    $('folio').textContent = folioDate();
    $('quiet').addEventListener('click', toggleQuiet);
    api('GET', '/api/session').then(function (s) {
      S.token = s.token;
      return loadShell();
    }).then(function () {
      return render();
    }).then(function () {
      listen();
    }).catch(function (err) {
      if (err.code === 'unreachable') { S.lost = false; firstLost(); return; }
      loadError(err);
    });
  }

  window.FH = {
    S: S, $: $, h: h, add: add, clear: clear, prop: prop, label: label, sec: sec, say: say,
    withProject: withProject, mixed: mixed, counts: counts, mark: mark, kindOf: kindOf,
    verdict: verdict, no: no, hms: hms, hm: hm, marginTime: marginTime, api: api,
    loadShell: loadShell, refresh: refresh, errLine: errLine, setErr: setErr,
    restoreFocus: restoreFocus, blankPage: blankPage, loadError: loadError, INTERNAL: INTERNAL,
    start: function () {
      if (D.readyState === 'loading') D.addEventListener('DOMContentLoaded', boot);
      else boot();
    }
  };
}());
