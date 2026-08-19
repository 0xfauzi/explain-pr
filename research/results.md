# Results

Run against `design.md`, whose decision rules were fixed before any data existed.
Deviations are recorded in that file.

## E1: selection has no headroom. Do not build it.

One writing task, eight independent generations, same prompt and model and
settings.

| | cv |
| --- | ---: |
| lowest draft | 0.514 |
| median draft | 0.574 |
| highest of all eight | 0.639 |
| standard deviation | 0.043 |
| spread | 0.125 |

Expected best-of-n, sampling without replacement:

| n | expected best | gain over median |
| ---: | ---: | ---: |
| 2 | 0.604 | +0.031 |
| 3 | 0.618 | +0.044 |
| 5 | 0.631 | +0.058 |
| 8 | 0.639 | +0.066 |

**Verdict: do not build.** The rule required best-of-5 to beat the median by 0.05
and to reach 0.726. It clears the first at +0.058 and fails the second at 0.631.

The failure is not marginal and no larger n rescues it. Taking the best of all
eight still lands at 0.639, short of the owner's 0.726 and well short of the 0.81
median for community technical documentation. The model's rhythm distribution is
narrow, so there is no lucky draft to find. Selection picks from a range that
does not contain the answer.

Note the curve flattens after n=3: the gain from 3 to 8 is 0.021 for five times
the cost. Even in a world where the level condition passed, best-of-3 would be
the whole prize.

## The noise floor, which was E1's other job

Standard deviation across identical repeats is **0.043 cv**. That is the
resolution of every other experiment here. Two conditions differing by less than
about 0.04 are indistinguishable from running the same condition twice.

Applying that retroactively to the round-trip results reported earlier:

| comparison | difference | interpretable? |
| --- | ---: | --- |
| one-step vs two-step, PR body | 0.135 | yes |
| one-step vs two-step, human doc | 0.102 | yes |
| one-step vs two-step, raw model output | 0.081 | yes |
| one-step vs two-step, our styled text | 0.051 | marginal |
| one-step vs original, raw model output | 0.034 | no |

So the claim that two-step loses to one-step holds on three of four sources. The
claim that one-step damaged the raw model output does not: that difference sits
below the floor and should not have been stated as a finding.

## E2: perplexity does not measure authorship here. Do not use it.

The pre-registered rule passed. A stronger test refuted it, and the refutation is
what gets reported.

**What the rule saw.** Median perplexity under Qwen3-8B, by group:

| group | n scored | median | IQR |
| --- | ---: | ---: | :---: |
| `human` (llama.cpp docs) | 7 | 11.1 | 8.2-13.2 |
| `owner-edited` (published posts) | 2 | 28.9 | 23.7-34.1 |
| `ours` | 4 | 40.3 | 36.2-44.6 |
| `assisted` (private PR bodies) | 3 | 66.3 | 61.8-76.2 |

The `human` and `ours` interquartile ranges do not overlap, which is what the
rule asked for. Taken at face value this says human prose is four times less
surprising than ours.

**Why that reading is wrong.** Two independent problems.

*The ordering tracks exposure, not authorship.* Read the groups again by how
likely the scoring model is to have seen the text: famous public OSS docs 11,
published blog posts 29, our week-old private documents 40, never-published
private PR bodies 66. That is a clean monotone relationship with web exposure and
it explains the whole table without reference to who wrote anything.

*The matched test refutes it directly.* Take one document and compare it against
machine rewrites of the same content, which hold genre and vocabulary fixed:

| | perplexity |
| --- | ---: |
| `llama-android.md`, human-written, public | 26.3 |
| the same content, machine rewrite (aimax) | 21.6 |
| the same content, machine rewrite (one-step) | 27.2 |
| the same content, machine rewrite (two-step) | 20.6 |

The human original sits in the middle of its own machine rewrites. On matched
content the signal disappears.

*And the decisive single case.* `AGENTS.md`, written by hand by the owner, scores
**133.3**, the highest of any document measured. Under the naive reading, the
most unambiguously human text in the corpus is the most machine-like. It is dense
with project-specific jargon and terse fragments, which an outside model cannot
predict whoever wrote them.

**Verdict: do not use.** Document-level perplexity here measures how ordinary and
how previously-seen a text is. Both are confounded with authorship in any corpus
assembled the obvious way.

**A flaw in my own design, worth recording.** The rule compared groups. Groups
differ in genre, vocabulary density and training exposure all at once, so a
between-group comparison could never have isolated authorship. The matched-content
test should have been the pre-registered rule, and it was added as a check.
Anyone repeating this should register the matched test as primary.

**Missing data.** Thirteen of 41 documents failed to score, systematically at
around 650 words, because `llama-perplexity` needs more than two chunks. Every
`owner-human` document failed at the registered context size and had to be
rescored at `-c 256`. Group medians therefore rest on the longer documents in
each group, which is its own bias.

## E3: a small local model cannot do the revision. The family question is unanswered.

**Deviation.** The GPT-class arm could not run. `codex` reported the account had
hit its usage limit until the following morning. So the design's three-way
comparison became two-way, and what was tested is not the hypothesis that was
registered.

Same instruction, byte-identical, applied by Claude and by `gemma3:12b` locally:

| source | original cv | Claude cv | Gemma cv | Claude facts | Gemma facts |
| --- | ---: | ---: | ---: | ---: | ---: |
| PR body | 0.730 | 0.899 | 0.516 | 1.00 | 0.93 |
| human OSS doc | 0.700 | 0.711 | 0.559 | 1.00 | 1.00 |
| our styled text | 0.606 | 0.556 | 0.604 | 1.00 | 0.94 |

**Verdict: reject, with a caveat that matters.** Gemma lands below the original
on all three sources and below Claude on two. It also fails the fact gate twice,
at 0.93 and 0.94 against a required 0.98, dropping identifiers the instruction
told it to keep.

The caveat is that this tests a *small* model, not a *different family*. Gemma at
12B quantised is not comparable in capability to the model it is being compared
against, so a loss here is as easily explained by size as by family. The
registered hypothesis, that a different family does not share the same
structural habit, remains untested. Anyone repeating this needs a cross-family
model of comparable capability, which is what the codex arm was for.

## Where three negatives leave the programme

The design named this outcome in advance: if selection, surprisal and
cross-family revision all fail, then rhythm has to come from the writing
instruction at generation time or not at all.

That is where we are, and it points at something uncomfortable. The instruction
we have makes rhythm *worse*. Measured on the same task, the Teacher style
produced cv 0.606 where the default produced 0.714, because its hard twenty-word
sentence cap removed the long tail that carries variation.

That cap has since been removed and replaced with a distribution target. The
change was made on the strength of the diagnosis and was never itself tested,
which is the same error this whole exercise exists to catch. E5 tests it.

## E5: the instruction lever works, weakly

Added after E1 to E3 came back negative, because the writing instruction was the
only lever left and it had been changed without being tested.

Same task as E1, eight drafts per condition, differing only in whether the
revised Teacher style was active.

| condition | n | median cv | mean | sd | range |
| --- | ---: | ---: | ---: | ---: | :---: |
| default style | 8 | 0.574 | 0.578 | 0.043 | 0.514-0.639 |
| revised Teacher | 8 | **0.619** | 0.606 | 0.057 | 0.506-0.681 |

Median difference **+0.045**, against a noise floor of 0.043 established by E1.
Revised beats default in 6 of 8 rank-for-rank positions.

**Verdict: real but marginal.** The difference clears the floor by 0.002, which
is not a margin anybody should lean on. Two runs of eight are enough to say the
sign is probably right and not enough to say the size is.

What it does establish is that the direction of the earlier change was correct.
The old Teacher style, with its hard twenty-word cap, produced 0.606 on this task
family and sat *below* the unstyled default. The revised style, targeting the
distribution instead of the maximum, now sits above it. Removing the cap stopped
the style working against itself.

## The state of the programme

| lever | result |
| --- | --- |
| best-of-n selection | rejected. Best of eight reaches 0.639; the target is 0.726 |
| document perplexity | rejected. Measures exposure and ordinariness, not authorship |
| small local model revision | rejected. Worse rhythm, and fails the fact gate |
| different family revision | **untested**. The GPT-class arm was out of quota |
| the writing instruction | +0.045, marginal, direction confirmed |
| fine-tuning | not run. Gated behind the family question |

Current position: **0.619**, against 0.726 for the owner's own writing and 0.810
for community technical documentation. Roughly a third of the gap closed, by the
only lever that survived, and no available mechanism closes the rest.

The honest summary is that the measurement works and the interventions mostly do
not. That is worth publishing as it stands, because the failed levers are the
expensive ones and somebody else would otherwise build them.

**The two things still worth trying**, in order:

1. The family question, properly. A cross-family model of comparable capability,
   not a small local one. Everything is in place to run it the moment quota
   allows.
2. The back-translation fine-tune of E4, whose corruption operator is the one
   thing in this programme that behaved reliably: pushing text toward the machine
   attractor lowered rhythm on four of four sources.
