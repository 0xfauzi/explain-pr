# What to draw, and how

Read this before building any visual for a lesson. It covers the three classes of
picture, the widget archetypes, and how to prove a widget teaches the truth.

## Why the ladder is ordered that way

A rule stated in a sentence asks the reader to believe you. Wire the same rule to
a control they can move, and they find out instead. Belief fades in a week.
Finding out does not.

So: a widget the reader can operate, then a figure, then a table, then prose.

Two drafts of one lesson stopped at figure and table. Both passed the checker,
both read well, and neither let the reader test a single rule. A picture of a
rule states the rule. Trying it and being surprised is a different event.

## When a picture is not the answer

Drawing costs something, and it earns that cost only sometimes. Prefer a sentence
when the idea is one fact with no moving parts, when a sentence genuinely says
the thing, or when you would be illustrating what the reader already believes.

A decorative figure teaches the reader that your figures are decoration. After
that they stop looking, including at the good ones.

## Class A: pictures of the system

These show where the change sits: the parts, and the flows between them.

**Generate them.** If the repository can emit a map of its own structure, run the
generator and paste in what it produces.

Draw one by hand and you have created a second definition of the topology. It
**drifts** the moment somebody moves a part, and nothing announces that it has.
The generated one cannot drift, because the next run replaces it.

This sounds like it contradicts the rule against restating things, so be precise.
Embedding a generated figure is **citation**. The restatement rule binds your
prose: a sentence repeating a computed count will eventually disagree with the
thing computing it. The figure will not. So paste the figure, and let it carry
its own numbers.

Read the map before writing about it. Where the picture and the PR title
disagree, teach the gap. A part the generator shows as unmapped is a fact about
the change, and it belongs in the lesson.

Mark generated figures `data-generated` so the checker leaves them alone. Their
labels answer to whatever produced them.

## Class B: pictures of a mechanism

A system map draws parts and flows, and stops. It cannot show a template
splitting at a sentinel, a retry loop draining its budget, or the field somebody
left out of a schema. Those you author yourself, inline, as SVG.

A mechanism figure earns its place when the reader needs to see an ordering, a
containment, or a path. When what you have is a set of pairs, use a table.

Hold every one to this:

- **One idea per figure.** If decoding it takes a paragraph, you have two.
- **Label every box and edge** in the exact words the glossary uses, so the
  figure reinforces the vocabulary instead of competing with it.
- **Let colour carry meaning**, and pair it with shape, position or a label, so
  the figure survives a greyscale print and both themes.
- **Keep everything inline**: plain SVG, system fonts, no fetches.

A useful test: cover the caption and look at the figure. If you cannot say what
it claims, it is not carrying its weight.

## Class C: widgets

The design fits in one sentence. **The reader moves the input the rule reads, and
the rule's answer changes in front of them.** Everything else is decoration.

Drag beats a slider, because the thing being dragged is the thing the rule
measures, so the reader feels the connection rather than inferring it. A slider
beats a still picture for the same reason, one rung down.

### Archetypes, and when to reach for each

- **Drag the thing.** Two boxes on a canvas and a rule about the gap between
  them. The reader drags one and watches the verdict flip. Reach for it when the
  rule is about geometry or distance.
- **Sweep one input.** A slider, one number out, one sentence out. Reach for it
  when the rule is arithmetic and the interest is where it crosses a threshold.
- **Press to reveal.** A button that answers a yes-or-no question about the
  system and prints the real answer. Reach for it when the fact is binary and the
  temptation is a careful paragraph instead.
- **Swap old for new.** One toggle between the rule before the change and the
  rule after, over the same input. Reach for it when the change replaced a rule
  rather than adding one.
- **The quiz.** For the Judge part at the end. Ask what would make this change
  wrong and let the reader commit before seeing your answer. Give each option its
  own `li`, since the checker treats a bare `div` as running on into what
  follows.

### Rules for all of them

- **One rule per widget.** Two rules means two widgets.
- **Put a "try this" line underneath**, naming two specific moves and what each
  one shows. A reader who knows what to touch will touch it.
- **Give the answer as a number and as a sentence.** A bare number leaves the
  reader to supply the meaning you owed them.
- **Make the reachable range contain the interesting cases.** See below. This is
  the failure that ships.
- **Label invented data as invented**, in the caption, beside the real numbers.
- **Keep it plain**: SVG and DOM, no libraries, no fetches, no fonts.

## Proving a widget teaches the truth

A widget carries more authority than any sentence you could write, because the
reader watched it happen. That cuts both ways. A wrong widget teaches a wrong
thing harder than a wrong sentence ever could.

Two false teachings shipped in one lesson. Both read well and parsed cleanly:

- a gutter demo placed its boxes thirty points apart, so the slider could never
  reach the case the prose promised
- a neighbour demo promised a wobble, on a crowd whose answer was flat from k=3
  upward

Neither was visible by reading the page. Both fell out in seconds once the
widget's own arithmetic ran outside the browser and printed.

So run it every time. Pull the rule into a standalone script and feed it the
widget's own data. Sweep the whole reachable range, printing the answer at each
step. It is usually about fifteen lines.

Then check the three things the prose is claiming:

1. Does the case you promised lie inside the reachable range?
2. Does the answer move across that range, or is it flat where you said it
   changes?
3. Does the boundary you named fall where the arithmetic puts it?

Worked shape, for a slider from 0 to 40 with a threshold at 12:

    for gap in range(0, 41):
        print(gap, verdict(gap))

Then read the output. A verdict that never changes means the slider is
decoration. A verdict that changes at 9 when your caption says 12 means one of
them is wrong, and now you know to find out which.

The checker parses your inline scripts, so a widget that cannot run gets caught
for you. A widget that runs perfectly and lies is caught only here.
