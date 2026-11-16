/* Firsthand site: the example question and the Copy buttons. No library.
   The state is data-demo on .fh-site. An element that belongs to some states
   lists them in data-v, and the stylesheet hides it in the others. This script
   changes the attribute and writes the words of the answer and the verdict. */
(function () {
  "use strict";

  var page = document.querySelector("[data-demo]");
  var $ = function (id) { return document.getElementById(id); };

  /* ---------- Copy buttons ---------- */

  function copyText(text) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).catch(function () {});
        return;
      }
    } catch (e) { /* fall through to the old way */ }
    var area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    try { document.execCommand("copy"); } catch (e) { /* nothing more to try */ }
    document.body.removeChild(area);
  }

  [].forEach.call(document.querySelectorAll("[data-copy]"), function (button) {
    var label = button.textContent, timer;
    button.addEventListener("click", function () {
      var from = button.getAttribute("data-copy-from");
      var src = from
        ? document.querySelector('[data-cmd="' + from + '"]')
        : button.parentNode.querySelector("code");
      if (src) copyText(src.textContent);
      // Hold the width of the longer label, so nothing beside it moves.
      button.style.minWidth = button.offsetWidth + "px";
      button.textContent = "Copied";
      clearTimeout(timer);
      timer = setTimeout(function () {
        button.textContent = label;
        button.style.minWidth = "";
      }, 2000);
    });
  });

  /* ---------- The example: ask, locked, skipped, result ---------- */

  var sheet = $("sheet");
  if (!page || !sheet) return;

  var picks = [].slice.call($("picks").children);
  var sures = [].slice.call($("sure").children);
  var NAMES = {
    1: "test_same_key_refunds_once",
    2: "test_refund_response_is_stable",
    3: "test_refund_amount_validated"
  };
  // In the example only test 2 still passes. Each cue is [before, path, after].
  var MORE = {
    match: "It would pass whether or not the change exists.",
    only: ["Its only assertion is at ", "tests/test_refunds.py:41", "."],
    1: ["Test 1 fails at ", "tests/test_refunds.py:29", " with the change undone."],
    3: ["With the change undone test 3 stops at ", "tests/test_refunds.py:52", " with an error, not on an assertion."]
  };
  var BARS = { match: "M8 11h12M8 17h12", miss: "M8 11h12M8 17h12M17.5 6.5l-7 15", none: "M8 11h12M8 17h12" };
  var WORDS = { match: "Matched", miss: "Did not match", none: "Not scored" };
  var chosen = [], sure = null;

  function state() { return page.getAttribute("data-demo"); }

  function go(s) {
    page.setAttribute("data-demo", s);
    // The highlighter passes once: it does not pass again on a return to ask.
    if (s !== "ask") $("q").setAttribute("data-still", "");
  }

  function say(text) {
    var live = $("live");
    live.textContent = "";
    setTimeout(function () { live.textContent = text; }, 40);
  }

  function isWord(p) { return p === "none" || p === "dk"; }
  function nums() { return chosen.filter(function (p) { return !isWord(p); }); }

  function draw() {
    var open = state() === "ask";
    picks.forEach(function (b) {
      b.setAttribute("aria-pressed", chosen.indexOf(b.getAttribute("data-p")) < 0 ? "false" : "true");
      b.disabled = !open;
    });
    sures.forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-s") === sure ? "true" : "false");
    });
    $("lock").disabled = !chosen.length;
  }

  function toggle(p) {
    if (state() !== "ask") return;
    var was = chosen.indexOf(p) >= 0;
    // None and Don't know each clear everything else; a number clears them.
    var clear = isWord(p) || (chosen.length && isWord(chosen[0]));
    chosen = clear ? [] : chosen.filter(function (n) { return n !== p; });
    if (!was) chosen.push(p);
    chosen.sort();
    draw();
  }

  function join(a) {
    return a.length < 2 ? a.join("") : a.slice(0, -1).join(", ") + " and " + a[a.length - 1];
  }

  function write() {
    var n = nums();
    var said = chosen[0] === "dk" ? "Don't know." : chosen[0] === "none" ? "None." : join(n) + ".";
    if (sure && chosen[0] !== "dk") said += " " + sure + ".";
    $("rec-said").textContent = said;
    ["held", "answer", "waitcall"].forEach(function (id) {
      var line = $(id);
      line.textContent = said;
      if (!n.length) return;
      var names = document.createElement("small");
      names.textContent = n.map(function (x) { return NAMES[x]; }).join(", ");
      line.appendChild(names);
    });
  }

  function lock() {
    if (state() !== "ask" || !chosen.length) return;
    sure = null;
    go("locked");
    draw();
    write();
    $("surerow").hidden = chosen[0] === "dk";
    $("show").focus();
    say("Locked.");
  }

  function verdict() {
    if (chosen[0] === "dk") return "none";
    return chosen.join() === "2" ? "match" : "miss";
  }

  function mark(svg, v) {
    svg.setAttribute("class", "fh-m fh-m--" + v);
    svg.querySelector("path").setAttribute("d", BARS[v]);
    var sq = svg.querySelector("rect"), inset = v === "match" ? 0 : 0.75;
    sq.setAttribute("x", inset);
    sq.setAttribute("y", inset);
    sq.setAttribute("width", 28 - inset * 2);
    sq.setAttribute("height", 28 - inset * 2);
  }

  function fill() {
    var v = verdict();
    write();
    // The verdict words, the margin label, the entry's name and both marks change together.
    mark($("stamp"), v);
    mark($("rec-mark"), v);
    mark($("verdict").querySelector("svg"), v);
    $("verdict").className = "fh-verdict fh-verdict--" + v;
    $("verdict").lastChild.nodeValue = WORDS[v];
    $("entry").setAttribute("aria-label", WORDS[v] + ". Revert test, No. 0042");
    $("f-label").textContent = WORDS[v];
    var more = $("f-more");
    more.textContent = "";
    if (v === "match") { more.textContent = MORE.match; return; }
    // If 2 is not picked, the sentence is about test 2; else about the lowest other pick.
    var other = nums().filter(function (x) { return x !== "2"; })[0];
    var cue = nums().indexOf("2") < 0 ? MORE.only : MORE[other];
    var lead = v === "none" ? "\"Don't know\" is not counted as a miss. " : "";
    more.appendChild(document.createTextNode(lead + cue[0]));
    var path = document.createElement("span");
    path.className = "fh-fact";
    path.textContent = cue[1];
    more.appendChild(path);
    more.appendChild(document.createTextNode(cue[2]));
  }

  function show() {
    if (state() !== "locked") return;
    fill();
    go("result");
    draw();
    // Play the print once: drop the attribute, force a reflow, set it again.
    [$("spread"), $("entry"), $("rec")].forEach(function (el) {
      el.removeAttribute("data-play");
      void el.offsetWidth;
      el.setAttribute("data-play", "");
    });
    $("entry").focus({ preventScroll: true });
    $("result").scrollIntoView({ block: "start" });
  }

  function reset(keep) {
    if (!keep) chosen = [];
    sure = null;
    go("ask");
    draw();
    var first = picks.filter(function (b) { return b.getAttribute("aria-pressed") === "true"; })[0] || picks[0];
    first.focus();
  }

  picks.forEach(function (b) {
    b.addEventListener("click", function () { toggle(b.getAttribute("data-p")); });
  });
  sures.forEach(function (b) {
    b.addEventListener("click", function () {
      var s = b.getAttribute("data-s");
      sure = sure === s ? null : s;
      draw();
      write();
    });
  });
  $("lock").addEventListener("click", lock);
  $("show").addEventListener("click", show);
  $("undo").addEventListener("click", function () { reset(true); say("Undone."); });
  $("unskip").addEventListener("click", function () { reset(true); say("Undone."); });
  $("skip").addEventListener("click", function () {
    chosen = [];
    go("skipped");
    draw();
    $("unskip").focus();
    say("Skipped.");
  });
  $("again").addEventListener("click", function () { reset(false); });

  sheet.addEventListener("keydown", function (e) {
    if (state() !== "ask" || e.ctrlKey || e.metaKey || e.altKey) return;
    var k = e.key;
    var p = k === "1" || k === "2" || k === "3" ? k : (k === "n" || k === "N") ? "none" : k === "?" ? "dk" : null;
    if (p) { e.preventDefault(); toggle(p); return; }
    // Enter locks from the sheet or a cell once a cell is on. Lock, Skip and links keep their own Enter.
    if (k !== "Enter" || e.repeat || !chosen.length) return;
    var t = e.target;
    if (t === sheet || t.classList.contains("fh-pick")) { e.preventDefault(); lock(); }
  });

  chosen = [];
  draw();
})();
