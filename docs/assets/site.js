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

  var picks = [].slice.call($("path").querySelectorAll("[data-p]"));
  var sures = [].slice.call($("sure").children);
  // In the example the fix landed in pricing/rates.py.
  var SAID = {
    order: "checkout/order.py.",
    totals: "pricing/totals.py.",
    rates: "pricing/rates.py.",
    "else": "Somewhere else.",
    dk: "Don't know."
  };
  var MORE = {
    match: "Your answer and the fix are the same file.",
    miss: "The fix is in pricing/rates.py, a file that the failing trace does not name.",
    none: "\"Don't know\" is not counted as a miss."
  };
  var BARS = { match: "M8 11h12M8 17h12", miss: "M8 11h12M8 17h12M17.5 6.5l-7 15", none: "M8 11h12M8 17h12" };
  var WORDS = { match: "Matched", miss: "Did not match", none: "Not scored" };
  var chosen = null, sure = null;

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

  function draw() {
    var open = state() === "ask";
    picks.forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-p") === chosen ? "true" : "false");
      b.disabled = !open;
    });
    sures.forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-s") === sure ? "true" : "false");
    });
  }

  function write() {
    var said = SAID[chosen];
    if (sure && chosen !== "dk") said += " " + sure + ".";
    ["held", "answer", "waitcall", "rec-said"].forEach(function (id) { $(id).textContent = said; });
  }

  // A tap on a part locks the answer. Undo opens it again.
  function lock(p) {
    if (state() !== "ask") return;
    chosen = p;
    sure = null;
    go("locked");
    draw();
    write();
    $("surerow").hidden = chosen === "dk";
    $("show").focus();
    say("Locked.");
  }

  function verdict() {
    return chosen === "dk" ? "none" : chosen === "rates" ? "match" : "miss";
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
    // The verdict words, the margin label, the entry's name and the marks change together.
    mark($("stamp"), v);
    mark($("rec-mark"), v);
    mark($("verdict").querySelector("svg"), v);
    $("verdict").className = "fh-verdict fh-verdict--" + v;
    $("verdict").lastChild.nodeValue = WORDS[v];
    $("entry").setAttribute("aria-label", WORDS[v] + ". Call it, No. 0042");
    $("f-label").textContent = WORDS[v];
    $("f-more").textContent = MORE[v];
    $("rpath").setAttribute("data-said", chosen);
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

  function reset() {
    var back = chosen;
    chosen = null;
    sure = null;
    go("ask");
    draw();
    var first = picks.filter(function (b) { return b.getAttribute("data-p") === back; })[0] || picks[0];
    first.focus();
  }

  picks.forEach(function (b) {
    b.addEventListener("click", function () { lock(b.getAttribute("data-p")); });
  });
  sures.forEach(function (b) {
    b.addEventListener("click", function () {
      var s = b.getAttribute("data-s");
      sure = sure === s ? null : s;
      draw();
      write();
    });
  });
  $("show").addEventListener("click", show);
  $("undo").addEventListener("click", function () { reset(); say("Undone."); });
  $("unskip").addEventListener("click", function () { reset(); say("Undone."); });
  $("skip").addEventListener("click", function () {
    chosen = null;
    go("skipped");
    draw();
    $("unskip").focus();
    say("Skipped.");
  });
  $("again").addEventListener("click", function () { reset(); });

  draw();
})();
