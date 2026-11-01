# Explainer pages

An explainer is a self-contained HTML page that teaches one mechanism through
interactions the learner must answer before anything is revealed. It supplements
the conversation; it never replaces the learner's own attempt in chat.

## Contents

- When to build one, and when not to
- Workflow
- Page structure
- Interactions
- Diagrams
- Making simulations truthful
- Writing on the page
- Storing and delivering the page

## When to build one, and when not to

Build a page when the mechanism has a shape that text carries badly:

- state that changes over time (a request lifecycle, a retry, a migration)
- ordering or interleaving (two writers, a crash between two steps)
- a boundary or threshold (a timeout, a limit, a size where behaviour flips)
- topology (which component calls which, where a check sits)

Do not build one when:

- the idea is one fact, or one sentence says it
- the learner's attempt in chat was already correct; record it and move on
- the change is routine
- the page would only restate what the learner already explained

One page per topic, built after the learner's attempt in chat, aimed at the gaps
that attempt exposed. A page that tries to teach three mechanisms teaches none.

## Workflow

```
Explainer:
- [ ] 1. Collect the facts from code and commands
- [ ] 2. Choose the one mechanism and the learner's gaps
- [ ] 3. Copy the template and write the page
- [ ] 4. Sweep every simulation rule outside the browser
- [ ] 5. Run the checker; fix and re-run until OK
- [ ] 6. Look at the screenshots
- [ ] 7. Deliver, then import the results and follow up in chat
```

**1. Collect the facts.** Read the code that implements the mechanism and note
real names, values and `path:line` references. Run the tests that exercise it
and note the results. Every claim on the page comes from this list.

**2. Choose the mechanism and the gaps.** Name the one mechanism in a sentence.
List what the learner's chat answer missed or got wrong; each gap gets at least
one interaction.

**3. Write the page.** Copy `assets/explainer-template.html` to
`.learning/explainers/<topic-id>.html`. Keep the `<style>` and the
`<script id="ex-runtime">` block unchanged. Replace everything marked EXAMPLE,
set `<body data-topic>` to the topic id, and follow the structure below.

**4. Sweep the rules.** For each simulation:

    python3 ${CLAUDE_SKILL_DIR}/scripts/check_explainer.py PAGE --extract-rules /tmp/rules.cjs
    node -e "const R=require('/tmp/rules.cjs'); for (let v=MIN; v<=MAX; v+=STEP) console.log(v, R.NAME({param: v}).text)"

Sweep every control across its full range and in every combination of toggles.
Read the output against each claim the page makes:

1. Does the case the page promises fall inside the reachable range?
2. Does the output change where the page says it changes, and stay flat where it
   says it is flat?
3. Does the threshold sit exactly where the page and the code put it?
4. Does the prediction's marked answer match what the rule produces?

The checker cannot catch a simulation that runs and lies. This sweep is the only
thing that does.

**5. Run the checker.**

    python3 ${CLAUDE_SKILL_DIR}/scripts/check_explainer.py PAGE

It runs static checks, then drives the page in headless Chromium: no network
requests, no console errors, no sideways scroll on a phone, no answer visible
before a commit, steppers and simulations locked until their question is
answered, and one result line per answered interaction. Fix every problem and
run it again. If it reports that node or Playwright is missing, tell the learner
the browser checks did not run.

**6. Look at the screenshots.** Open `phone-before.png`, `phone-after.png` and
`desktop-before.png` from the shots folder the checker prints. Check that each
diagram can be read at phone width, that labels do not overlap, and that the
answered state shows the learner's choice and the correct one. Fix and repeat
from step 5.

**7. Deliver and follow up.** See "Storing and delivering the page".

## Page structure

In this order. Skip a part only when the mechanism genuinely lacks it.

1. **Stake.** One or two sentences: what goes wrong without this mechanism. Then
   one line saying nothing on the page changes any code.
2. **Predictions first.** One to three `ex-predict` blocks with `data-kind="attempt"`,
   before any explanation. Target the learner's gaps and the most common wrong
   model. Wrong answers here are expected; they make the explanation stick.
3. **Words used on this page.** A short table, only for terms the page needs and
   the learner may not hold. Use those exact words everywhere after, including
   inside diagrams.
4. **The mechanism, step by step.** An `ex-stepper` with one frame per state
   change. Put an `ex-predict` in the frame just before the decisive step, so the
   learner predicts the next state before seeing it.
5. **The boundary.** An `ex-sim` when the behaviour flips at a value, with a
   prediction inside it that locks the controls until answered.
6. **Explain it back.** One `ex-explain` asking why the mechanism works, or what
   must hold for it to keep working. The learner writes first, then compares.
7. **Build it.** One `ex-order` where the learner puts the real steps in order,
   when the order is the point.
8. **How each claim is known.** A table with one row per claim: observed (a test
   or command, named), implemented (in the code, `path:line`, not exercised),
   reasoned (inferred, not checked), or unknown.

The results box at the end is added by the runtime. Do not write one.

## Interactions

Every interaction is answered before it reveals anything, and asks for
confidence. Prefer the ones where the learner produces something.

**ex-predict**: multiple choice with an answer revealed on commit.

```html
<section class="ex-predict" data-id="p1" data-kind="attempt" data-answer="b">
  <p class="ex-q">Question stating a concrete situation.</p>
  <ol class="ex-options">
    <li data-value="a">A plausible wrong model</li>
    <li data-value="b">The right answer</li>
    <li data-value="c">Another plausible wrong model</li>
  </ol>
  <div class="ex-reveal" hidden>
    <p data-for="a">Shown only to someone who chose a: why that model fails.</p>
    <p>Explanation for everyone, with path:line.</p>
  </div>
</section>
```

Write every wrong option as a belief a capable engineer could hold, ideally one
the learner showed in chat. Give each wrong option its own `data-for` feedback
naming the belief and the evidence against it. Options of similar length; the
right answer must not be the longest or the most hedged.

**ex-explain**: free text, then the model answer, then an honest self-grade.

```html
<section class="ex-explain" data-id="e1" data-kind="explain-back">
  <p class="ex-q">Why does X hold, and what would break it?</p>
  <div class="ex-reveal" hidden><p>Model answer with path:line.</p></div>
</section>
```

**ex-order**: write the steps in the correct order; the page shuffles them.

```html
<section class="ex-order" data-id="o1" data-kind="attempt">
  <p class="ex-q">Put the steps in the order the code runs them.</p>
  <ol class="ex-items"><li>First</li><li>Second</li><li>Third</li></ol>
  <div class="ex-reveal" hidden><p>Which step's position matters, and why.</p></div>
</section>
```

**ex-stepper**: learner-paced frames; Next stays locked while the current frame
has an unanswered interaction.

```html
<section class="ex-stepper">
  <figure class="ex-frame"><svg>...</svg><figcaption>Step 1. ...</figcaption></figure>
  <figure class="ex-frame"><svg>...</svg><figcaption>Step 2. ...</figcaption>
    <section class="ex-predict" ...>...</section></figure>
</section>
```

**ex-sim**: controls feed a pure rule in `<script id="ex-rules">`; a prediction
inside locks the controls until committed.

```html
<section class="ex-sim" data-rule="name">
  <section class="ex-predict" ...>...</section>
  <div class="ex-controls">
    <label>Label: <b class="ex-val" data-for="x"></b>
      <input type="range" data-param="x" min="0" max="100" step="5" value="20"></label>
    <label><input type="checkbox" data-param="flag"> Toggle</label>
  </div>
  <output class="ex-out"></output>
  <p class="ex-label">Which values are real (path:line) and which are illustrative.</p>
</section>
```

```js
const RULES = {
  name({ x, flag }) {
    return { text: "Outcome as a sentence, with the number", state: "good" /* or "bad" */ };
  },
};
```

A rule takes the control values and returns `{text, state}`. No DOM access, so it
can be swept in node. Mirror the real code's logic and constants, and cite them.

## Diagrams

- **One idea per figure.** If a figure needs a paragraph to decode, split it
  into frames.
- **Discrete frames, not animation.** Show each state as its own frame, which the
  learner steps through at their own pace. Do not animate continuously.
- **Keep the layout fixed across frames.** Same component, same position, same
  size in every frame. Only what changed between frames should differ, marked
  with the `changed` class (or `fault` for the failure).
- **Labels on the parts, not in a legend.** Put each label next to the thing it
  names, in the glossary's words.
- **Colour plus another cue.** Pair colour with a dash pattern, weight or a text
  label, so the figure works for colour-blind readers and in both themes.
- **No decoration.** No icons, gradients, shadows or illustrative clip-art.
  Every mark carries information.
- **Readable at 375 px.** Keep `viewBox` widths near 360 units with 13 px text,
  and no more than four or five boxes per row.
- **Use the template's classes** (`box`, `edge`, `changed`, `fault`, `arrowhead`)
  so dark mode works. Keep shared `<defs>` in the hidden block at the top.
- **Generated over hand-drawn for system maps.** If the repository can emit its
  own architecture diagram, embed that output. A hand-drawn map goes stale
  silently when the code moves.
- **Diagrams state a model; they prove nothing.** Never present a diagram as
  evidence that a boundary or guarantee holds. That evidence goes in the claims
  table, from tests.

## Making simulations truthful

- Take constants from the code and cite them. Label every illustrative value as
  illustrative, in the `ex-label` line beside the controls.
- Make the reachable range include the case the page talks about, and both sides
  of every threshold.
- Model the rule the code implements, not a cleaner rule you would prefer. Where
  you simplified, say what was simplified.
- If the simulation and the code could disagree (the code has paths the rule
  ignores), say which paths are not modelled.

## Writing on the page

Short sentences, plain words, the idea before its name. Every claim carries its
evidence or says it is unverified. Write for a capable engineer who has not seen
this code. Do not restate in prose what a diagram or interaction already showed.

## Storing and delivering the page

1. Save it as `.learning/explainers/<topic-id>.html`, so it is committed with
   the record.
2. If the session has a tool for publishing an HTML page the learner can open on
   any device, publish it there. Otherwise give the file path.
3. Tell the learner: work through it, then press "Copy for Claude" at the bottom
   and paste the result into the chat.
4. Import what they paste:

       python3 ${CLAUDE_SKILL_DIR}/scripts/learning.py import --file RESULTS.jsonl

   (Write the pasted text to a file first, or pipe it with `--file -`.)
5. Discuss every misconception the import prints. Then ask one question in chat,
   graded by Claude against a fixed rubric, that the page did not ask. Page
   results are recognition and self-assessment; only a produced answer in chat
   moves the topic's level.

A page records what was true on the day it was built. When the code changes
underneath it, add a short note at the top saying what changed, or retire the
topic.
