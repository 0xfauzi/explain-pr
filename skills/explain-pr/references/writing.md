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

## Shape

Two limits, both from ASD-STE100, the controlled-English standard for technical
writing. **Twenty words per sentence.** **Six sentences per paragraph.** Two to
four sentences usually reads better than six.

Four habits underneath them, from Zinsser:

- **Simplicity.** One idea per sentence. Simple tenses. Active voice. Name who
  does the thing.
- **Brevity.** Cut every word that does no work. "In order to" is "to". "The
  fact that" is nothing. If a sentence survives its own deletion, delete it.
- **Clarity.** The same word for the same idea, always, and jargon only where
  the glossary defines it.
- **Humanity.** Write to a person. Say plainly when something is wrong, unproven
  or unknown.

## The trap inside the limits, and the way out

This section is worth more than the limits themselves.

The limits are pacing, not compliance. Take a twenty-six word sentence, split it
at the comma, and you keep every word while throwing away the join, which was
carrying your argument. The result passes the checker and reads like a wall of
commandments.

This document did it to itself. An earlier draft of the widgets file read:

> A hand-drawn topology is a rival definition of the topology. It starts
> drifting the moment a part moves. Nothing tells the reader it has drifted.

Three legal sentences, and nothing says why the second follows from the first.

**Put the join at the front of the next sentence.** That is the whole technique,
and it costs one word:

> Draw the topology by hand and you have two definitions of it. So they disagree
> the moment somebody moves a part. Nothing tells you they have.

Same limit, and the reasoning survived. The words doing this work are all small:
so, but, and, then, because, which is why, that is.

Reach for a short sentence because the thought is finished.

## Rhythm

Ten sentences of the same length read like a machine, even when each one is good.
Vary them.

The basic move is a longer sentence that unfolds an argument, then a short one
that lands it. Then let the next paragraph breathe differently, or the reader
starts hearing the pattern instead of the content.

Read the draft aloud. Anywhere you would not say a sentence to a colleague
standing at your desk, rewrite it.

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
