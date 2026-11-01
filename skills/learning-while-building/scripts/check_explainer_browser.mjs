// Drive an explainer in headless Chromium and report what a learner would hit.
//
// Usage: node check_explainer_browser.mjs <page.html> <screenshot-dir>
//
// Checks, in order:
//   - the page makes no network request (every non-file request is blocked and listed)
//   - no console errors or uncaught exceptions
//   - no horizontal scroll at phone width (375 px)
//   - every answer is hidden on load, and stays hidden if Commit is pressed early
//   - a stepper will not advance past a frame whose question is unanswered
//   - a gated simulation keeps its controls disabled until the prediction is committed
//   - committing each interaction reveals its answer and adds one result line
// Screenshots at 375 px and 1100 px, before and after answering, go to the
// screenshot dir so the page can be looked at, not just tested.
//
// Exit 0 when clean, 1 with each problem listed, 2 when Playwright is missing.

import path from "node:path";
import fs from "node:fs";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
let chromium;
try {
  ({ chromium } = require("playwright"));
} catch {
  console.log("SKIPPED: Playwright is not installed for node (npm i -g playwright), so the page was not run in a browser.");
  process.exit(2);
}

const [file, outDir] = process.argv.slice(2);
if (!file || !outDir) {
  console.log("usage: node check_explainer_browser.mjs <page.html> <screenshot-dir>");
  process.exit(2);
}
fs.mkdirSync(outDir, { recursive: true });
const url = "file://" + path.resolve(file);
const problems = [];
const notes = [];

const launchOptions = fs.existsSync("/opt/pw-browsers/chromium") ? {} : {};
const browser = await chromium.launch(launchOptions);
const context = await browser.newContext({ viewport: { width: 375, height: 800 } });
const blocked = [];
await context.route("**/*", (route) => {
  const u = route.request().url();
  if (u.startsWith("file:") || u.startsWith("data:") || u.startsWith("blob:")) return route.continue();
  blocked.push(u);
  return route.abort();
});
const page = await context.newPage();
page.on("console", (m) => m.type() === "error" && problems.push("console error: " + m.text()));
page.on("pageerror", (e) => problems.push("uncaught exception: " + e.message));
await page.goto(url);
await page.waitForLoadState("load");

const shot = async (name, width) => {
  await page.setViewportSize({ width, height: 800 });
  await page.screenshot({ path: path.join(outDir, name), fullPage: true });
};

const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
if (overflow > 1) problems.push(`page scrolls sideways by ${overflow}px at 375px width`);
await shot("phone-before.png", 375);
await shot("desktop-before.png", 1100);
await page.setViewportSize({ width: 375, height: 800 });

const report = await page.evaluate(() => {
  const out = { problems: [], notes: [] };
  const P = (m) => out.problems.push(m);
  const visible = (el) => !!el && !el.closest("[hidden]");
  const reveals = [...document.querySelectorAll(".ex-reveal")];
  reveals.forEach((r, i) => visible(r) && P(`answer ${i + 1} is visible before any commit`));

  // Stepper gating, before anything is answered.
  document.querySelectorAll(".ex-stepper").forEach((stepper, s) => {
    const next = [...stepper.querySelectorAll(".ex-nav button")].find((b) => b.textContent === "Next step");
    const frames = [...stepper.querySelectorAll(":scope > .ex-frame")];
    let guard = 0;
    const isOpen = (f) => [...f.querySelectorAll(".ex-predict, .ex-explain, .ex-order")].some((g) => g.dataset.committed !== "true");
    while (next && !next.disabled && guard++ < 50) {
      const here = frames.findIndex((f) => !f.hidden);
      if (isOpen(frames[here])) P(`stepper ${s + 1}: moved past frame ${here + 1} while its question was unanswered`);
      next.click();
    }
    const at = frames.findIndex((f) => !f.hidden);
    const gate = frames[at] && frames[at].querySelector(".ex-predict, .ex-explain, .ex-order");
    if (at < frames.length - 1 && !gate) P(`stepper ${s + 1}: stuck at frame ${at + 1} with no question`);
    if (gate) out.notes.push(`stepper ${s + 1}: correctly stops at frame ${at + 1} until its question is answered`);
  });

  // Simulations stay locked until their prediction is committed.
  document.querySelectorAll(".ex-sim").forEach((sim, i) => {
    const gate = sim.querySelector(".ex-predict");
    const inputs = [...sim.querySelectorAll("[data-param]")];
    if (gate && inputs.some((x) => !x.disabled)) P(`simulation ${i + 1}: controls usable before the prediction is committed`);
    if (!gate) out.notes.push(`simulation ${i + 1} has no prediction gate: the learner can play without committing`);
  });

  const count = () => document.getElementById("ex-results-text").value.split("\n").filter(Boolean).length;
  const commit = (root) => root.querySelector(".ex-commit").click();
  const pickConf = (root, level) => {
    const c = root.querySelector(`.ex-conf input[value=${level}]`);
    if (c) c.checked = true;
  };

  for (const root of document.querySelectorAll(".ex-predict")) {
    const id = root.dataset.id;
    const reveal = root.querySelector(".ex-reveal");
    commit(root);
    if (!reveal.hidden) P(`${id}: answer revealed by pressing Commit with nothing chosen`);
    const options = [...root.querySelectorAll(".ex-options input")];
    if (!options.some((o) => o.value === root.dataset.answer)) P(`${id}: data-answer matches no option`);
    const wrong = options.find((o) => o.value !== root.dataset.answer) || options[0];
    wrong.checked = true;
    commit(root);
    if (!reveal.hidden) P(`${id}: answer revealed without a confidence rating`);
    pickConf(root, "high");
    const before = count();
    commit(root);
    if (reveal.hidden) P(`${id}: answer still hidden after a full commit`);
    if (count() !== before + 1) P(`${id}: commit did not add a result line`);
    const ownFeedback = reveal.querySelector(`[data-for="${wrong.value}"]`);
    if (ownFeedback && ownFeedback.hidden) P(`${id}: feedback for the chosen option stayed hidden`);
    // Fire a change on a sim this unlocks.
    const sim = root.closest(".ex-sim");
    if (sim) {
      const inputs = [...sim.querySelectorAll("[data-param]")];
      if (inputs.some((x) => x.disabled)) P(`${id}: simulation controls still disabled after commit`);
      const out = sim.querySelector(".ex-out");
      const seen = new Set();
      for (const input of inputs.filter((x) => x.type === "range")) {
        for (const v of [input.min, input.max]) {
          input.value = v;
          input.dispatchEvent(new Event("input"));
          seen.add(out.textContent);
        }
      }
      if (inputs.some((x) => x.type === "range") && seen.size < 2) P(`${id}: simulation output is the same at both ends of every slider`);
      if (/Missing rule/.test(out.textContent)) P(`${id}: ${out.textContent}`);
    }
  }

  for (const root of document.querySelectorAll(".ex-order")) {
    const reveal = root.querySelector(".ex-reveal");
    commit(root);
    if (!reveal.hidden) P(`${root.dataset.id}: order revealed without a confidence rating`);
    pickConf(root, "medium");
    const before = count();
    commit(root);
    if (reveal.hidden) P(`${root.dataset.id}: correct order still hidden after commit`);
    if (count() !== before + 1) P(`${root.dataset.id}: commit did not add a result line`);
  }

  for (const root of document.querySelectorAll(".ex-explain")) {
    const reveal = root.querySelector(".ex-reveal");
    pickConf(root, "low");
    commit(root);
    if (!reveal.hidden) P(`${root.dataset.id}: model answer revealed with an empty answer`);
    root.querySelector("textarea").value = "Because the gateway remembers the key and returns the first result.";
    const before = count();
    commit(root);
    if (reveal.hidden) P(`${root.dataset.id}: model answer still hidden after commit`);
    const partly = [...root.querySelectorAll("button")].find((b) => b.textContent === "I had part");
    if (!partly) P(`${root.dataset.id}: no self-grade buttons after commit`);
    else partly.click();
    if (count() !== before + 1) P(`${root.dataset.id}: self-grade did not add a result line`);
  }

  // Every result line must carry what learning.py import needs.
  const need = ["topic", "id", "kind", "grader", "question", "rubric", "answer", "outcome", "confidence", "hint"];
  for (const line of document.getElementById("ex-results-text").value.split("\n").filter(Boolean)) {
    const r = JSON.parse(line);
    const missing = need.filter((k) => !(k in r));
    if (missing.length) P(`result ${r.id} lacks ${missing.join(", ")}`);
  }
  out.notes.push(`${count()} result line(s) produced`);
  return out;
});

problems.push(...report.problems);
notes.push(...report.notes);
await page.evaluate(() => document.querySelectorAll(".ex-stepper .ex-frame").forEach((f) => (f.hidden = false)));
await shot("phone-after.png", 375);
await browser.close();

if (blocked.length) problems.push("network requests (blocked): " + [...new Set(blocked)].join(", "));
for (const n of notes) console.log("NOTE: " + n);
for (const p of problems) console.log("PROBLEM: " + p);
console.log(`Screenshots: ${path.resolve(outDir)}/{phone,desktop}-before.png, phone-after.png`);
console.log(problems.length ? `FAILED: ${problems.length} problem(s)` : "OK: browser checks passed");
process.exit(problems.length ? 1 : 0);
