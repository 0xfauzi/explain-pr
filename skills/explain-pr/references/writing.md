# How to write the lesson

Read this before drafting prose for a lesson. Every rule below is here because a
draft failed without it, and the failure is printed beside the rule. A style rule
with no evidence is a preference, and preferences rot.

## Who you are writing for

Your reader built this system and knows it better than you do. What they do not
know is this change, and that is the whole gap you are closing.

Those two kinds of knowing feel similar and behave nothing alike. Write for the
expert they are, and you skip the connecting steps, because to an expert those
steps look obvious. The result is a document they cannot read, and they assume
the fault is theirs.

Write for the person meeting this change for the first time, and trust them to
skim what they already hold.

## Teach the idea, then name it

Give the reader the thing before the word for the thing.

Here is the sentence that worked, from a lesson about grouping shapes:

> A chart, its title and its source line are three shapes but one thing.

The word "component" arrived two paragraphs later. By then it was a label for
something the reader already held, and those are free.

Name it first and you have asked for trust instead. Some readers extend it. Most
stop following quietly, and you find out much later.

## Say why it matters in the first thirty seconds

Say what was wrong, or what was at stake. One line, before any file name.

Readers decide whether to skim in the first few seconds. A good middle section
does not win them back.

## Replace the jargon, rather than translating it

There is a tempting halfway house:

> the component gap threshold (that is, how close shapes must be)

Now the reader carries two names for one idea and holds the mapping for the rest
of the document. That costs more than the jargon did.

Pick the plain word. Put it in a small table near the top. Then use it
everywhere: in prose, in headings, in captions, inside the widgets.

One lesson said **clump** for component, and **look-alike font** for metric
substitution, and used those words from then on.

One idea, one word, the same word every time.

## Show the dead end

This is the most valuable thing you will write, and the thing authors leave out
most often.

The first approach tried is usually the approach your reader would pick, because
it was the obvious one. Say what was tried, and give the evidence that killed it
rather than the verdict.

A reader who sees only the surviving answer learns one fact. A reader who sees
the dead end learns how to judge the next case, which is what you wanted to give
them.

There is an honesty argument too. An approach abandoned in silence reads, later,
exactly like an approach nobody considered.

Where the change genuinely rejected nothing, say so. It was either trivial or
under-examined, and working out which is itself worth teaching.

## One real example, immediately

State a rule, then show one case of it, using real values from the actual change.

Where you cannot find a real case, stop and notice it. Usually the rule is not
doing the work you thought, and that is a finding worth more than the rule.

## Say how you know, every time

Confidence you do not have is a lie told in a calm voice. Mark every claim as one
of these, in your own words:

- I measured this, and here is the number and the command that produced it
- I reasoned this out and did not check it
- This is my judgement, and a reasonable person could differ
- I do not know

Where a number matters and nobody measured it, say so, and say what would measure
it. An estimate dressed as a finding is the worst thing a lesson can carry,
because it is the one error a reader cannot catch by reading.

When your confidence drops partway through, mark the seam out loud. "Now the
honest part" costs one line and buys more than the careful paragraph you were
about to write instead.

## Make every sentence do explanatory work

Some sentences explain nothing, and their real job is to sound careful. An early
draft said this:

> The rejected value is absent from the contract's `Literal`, so the state is
> unrepresentable by construction.

True, and it teaches nobody. The draft that worked put a button on the page. You
press it and it prints "no such value exists". Same fact, except the reader
watched it happen.

Hedging is the same failure wearing modesty. State the finding, then say how sure
you are, rather than softening it in advance to be safe from criticism.

## Give permission before instructions

A reader who does not know what is safe will touch nothing. Give them the blast
radius, then the move.

> Drag things. Nothing can break.

Then name two specific moves under each widget and say what each shows. "Try it"
is not an instruction. "Drag the right box left until the number turns red" is.

## Shape, and the rhythm that carries it

One idea per sentence. Simple tenses. Active voice. Name who does the thing. Cut
every word that does no work: "in order to" is "to", "the fact that" is nothing,
and a sentence that survives its own deletion should be deleted.

Then vary the length. This is the part that is easy to get wrong in a way that
looks like compliance, so it gets the rest of this section.

Aim most sentences short, and let a long one run when it carries a single
connected thought that does not survive being cut in half. What you are steering
is the spread, not the maximum. A page where every sentence lands between twelve
and twenty words reads like a machine even when each sentence is good, because
uniform sentence length is one of the few signatures of generated prose that word
choice cannot disguise.

### The measurement that changed this rule

An earlier version of this file set a hard twenty-word cap. It was measured and
it was wrong.

Two explanations of the same pull request, same prompt and same model, differing
only in whether the teaching style was active:

| | mean words | longest | coefficient of variation |
| --- | ---: | ---: | ---: |
| style off | 26.2 | 114 | 0.874 |
| style on | 26.4 | 64 | **0.606** |
| the repository owner's own writing | 20 to 22 | 78 to 129 | 0.76 to 0.81 |

The cap did not shorten the average sentence at all. What it did was clip the
long tail, and the long tail is what makes prose read like a person. Comprehension,
measured separately on the same two documents, showed no detectable difference.

So the cap cost the thing it was supposed to protect and bought nothing that
could be measured. Steer the distribution instead, and check it with
`scripts/ai_tells.py`, which reports the coefficient of variation alongside the
other signatures.

### The move that keeps a short sentence honest

If you find yourself splitting a sentence at its comma to meet a limit, stop.
That keeps every word and throws away the join, which was carrying the argument.
An earlier draft of the widgets file did exactly this:

> A hand-drawn topology is a rival definition of the topology. It starts
> drifting the moment a part moves. Nothing tells the reader it has drifted.

Three legal sentences, and nothing says why the second follows from the first.
Put the connective at the front of the next sentence instead:

> Draw the topology by hand and you have two definitions of it. So they disagree
> the moment somebody moves a part. Nothing tells you they have.

It costs one word and the reasoning survives. The words doing this work are all
small: so, but, then, because, which is why.

Reach for a short sentence because the thought is finished.

## The habits that survive a style instruction

Published work on generated prose finds two classes of tell, and they behave
differently.

**Vocabulary washes out.** The words people learned to spot in 2023, like "delve"
and "tapestry", have largely gone, partly because writers avoid them and partly
because humans have adopted them from reading model output. A word blocklist has
a shelf life measured in months, so do not spend much attention on one.

**Structure persists.** These habits come from markdown-heavy training and survive
being told to write differently, which makes them the honest test of whether a
style instruction changed anything:

- **Reaching for a heading, a bullet or a bold run** where a sentence would do.
  Structure earns its place when the content is genuinely parallel; scaffolding
  applied to one argument fragments it.
- **Paragraphs of uniform length**, for the same reason as uniform sentences.
- **Negative parallelism**: "it is not just X, it is Y", a modest claim followed
  by a grander restatement of the same claim. This is the most reliable current
  tell, because it is a shape rather than a word. Say the claim once, at its real
  size.
- **The rule of three**, used because three sounds complete rather than because
  there are three things. Two is allowed, and so is four.
- **Participial tails** asserting significance without evidence: ", highlighting
  the importance of", ", underscoring its role in". Real significance deserves
  its own sentence with a reason attached.
- **Significance inflation**: "plays a crucial role", "stands as a testament to",
  "a turning point". Show the thing and let the reader judge its size.

`scripts/ai_tells.py` counts all of these and names its sources. Read its output
against a sample of writing you know a person produced, because a count with no
human reference tells you the prose changed rather than improved.

## Two habits that protect the reader

**Let the widget speak for itself.** The reader watched it happen, so saying it
again in prose tells them you did not trust what you built.

**Say the surprising thing plainly, in its own sentence.** The figure to avoid is
the paraprosdokian, whose ending forces a re-read of its start. Here is the
classic:

> I have had a wonderful evening, but this was not it.

The re-read is the entire effect, and a lesson spends re-reads on content only.
No checker catches this. Reading your own draft again does.

## Mechanics that cost time to rediscover

- The checker strips `script`, `style`, `svg` and `code` before judging prose, so
  text in there is never checked. Your reader still reads it, so it still gets
  the same care.
- Tick and cross glyphs sit inside the emoji range and get rejected. Use words.
- The checker cannot split a sentence ending inside a quotation mark. It reads
  `it." The` as one sentence, so a quoted line merges with the next and gets
  flagged as long. Put quotations on their own line as a blockquote.
- Only certain tags close a block. Text in a bare `div` runs on into whatever
  follows, so quiz options each need their own `li`.
- Browser extensions refuse `file://`. Serve the folder with
  `python -m http.server` to drive the page.

## What the checker cannot do

It counts sentences. It does not read for meaning, and it never asks whether
anybody learned anything. Two drafts of one lesson passed it cleanly and taught
nothing.

Its passive-voice finding over-reports, matching things like "is complete", so
treat that one as advisory.

Where it flags something wrongly, reword the prose. The rule is the only part of
this that does not rot.
