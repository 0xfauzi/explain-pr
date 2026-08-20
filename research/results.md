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

## E6: the measure works in one register and not in the other

Prompted by a challenge from the owner: a commercial detector reported both of
his published posts as fully machine-written. That forced an audit of what the
corpus had ever been calling human.

**The audit, and it failed on every count.**

- The `human` group was llama.cpp. That repository has **zero commits before
  ChatGPT**, its README carries 234 distinct authors, and it is an LLM project,
  so its contributors are the population most likely to write with assistance.
  It was labelled human because it was community open source, which is an
  assumption and not evidence.
- The `owner-human` group contained `AGENTS.md`, which is Claude-co-authored on
  **11 of the 11 commits** that touched it. The label was simply wrong.
- Which left the owner's session messages, 548 words, as the only text in the
  entire corpus defensible as human-written.

Every reference band reported before this point rested on those labels.

**The fix needs no detector.** Text published before ChatGPT is certainly human.
Text generated now is certainly not. Both ends are guaranteed, so provenance
stops being a judgement call.

Human side: 18 documents, PEPs and RFCs dated 1997 to 2018, plus 8 Paul Graham
essays, all pre-2022. Generated side: 16 explanations and 8 specifications
written for this experiment.

**The result, and the reason the first version of it was wrong.**

| register | author | n | median cv | IQR |
| --- | --- | ---: | ---: | :---: |
| technical | human | 18 | 0.784 | 0.729-0.827 |
| technical | generated | 5 | **0.491** | 0.413-0.504 |
| essay | human | 8 | 0.633 | 0.583-0.656 |
| essay | generated | 16 | 0.604 | 0.550-0.627 |

Comparing human technical prose against generated essays gives an AUC of 0.995,
which looks like a triumph and is an artefact. It compares two registers at once.
Within register:

| register | gap | AUC | verdict |
| --- | ---: | ---: | --- |
| technical | +0.293 | **1.000** | separates perfectly |
| essay | +0.029 | 0.664 | does not separate |

**What this means.** Rhythm separates human from generated writing only where
human writers actually vary. Specification authors vary enormously. Paul Graham
does not: he writes short, uniform, deliberate sentences, and on this measure he
scores 0.633 against a machine's 0.604.

So the target is register-specific and there is no single number:

- **Technical documentation and PR lessons: aim for 0.78.** We sit at 0.649, so
  the gap is real and worth closing. Generated spec prose at 0.491 is the flattest
  thing measured anywhere, so this is where the problem is worst.
- **Essays: do not chase this metric.** Our 0.649 already exceeds the human essay
  median of 0.633. Optimising further would push prose away from how good
  essayists actually write.

**Caveat.** Only 5 of 8 generated specifications cleared the 400-word floor, so
the perfect AUC rests on a small cell. The size of the gap is not in doubt; its
precision is.

## E3, completed: every reviser makes rhythm worse

The GPT-class arm ran once codex quota returned, so the three-way comparison the
design registered is now complete. Same instruction, byte-identical, four sources
of different kinds.

| source | original | Claude | Gemma | GPT-5.6 |
| --- | ---: | ---: | ---: | ---: |
| PR body | 0.730 | 0.899 | 0.516 | 0.706 |
| human OSS doc | 0.700 | 0.711 | 0.559 | 0.523 |
| our styled text | 0.606 | 0.556 | 0.604 | 0.569 |
| raw model output | 0.714 | 0.680 | 0.647 | 0.440 |
| **median change** | | **-0.011** | **-0.104** | **-0.107** |

Fact retention: Claude 1.00 on all four, GPT-5.6 1.00 on all four, Gemma between
0.93 and 1.00.

**Verdict: reject.** The rule required a cross-family reviser to beat same-family
by 0.05 in median change. GPT-5.6 trails it by 0.096.

The result is stronger than a rejection of one hypothesis. **All three revisers
have a negative median.** Across twelve revisions, three revisers and four kinds
of source, asking a model to rewrite prose so it reads more human made the rhythm
worse more often than better. Claude is closest to neutral, and neutral is the
ceiling.

Worth noting separately: GPT-5.6 kept every identifier in every source, matching
Claude and beating the local model. It is a careful reviser. It is just a flatter
writer, which is what the next section measures.

## E7, at full sample: the other family is flatter still

| writer | n | median cv | range |
| --- | ---: | ---: | :---: |
| human, published pre-2022 | 18 | **0.784** | 0.676-1.151 |
| Claude | 6 | 0.493 | 0.405-0.553 |
| GPT-5.6 | 5 | **0.293** | 0.248-0.308 |

The three cells do not overlap anywhere. GPT-5.6's range is the tightest of the
three and sits entirely below Claude's.

The two families reach flatness from opposite directions. Claude writes long
sentences of similar length. GPT-5.6 writes short ones of similar length, and in
five documents no sentence exceeded 21 words.

**So flatness is not a Claude quirk and no vendor has fixed it.** Two families
trained separately converge on uniform sentence length by opposite routes, and
both sit far below every human document measured. That also explains E3: there is
no reviser to borrow, because the obvious candidate writes flatter than the
writer, and a flatter reviser cannot add variation.

## A methodology error, recorded because it changed what I reported

I claimed in an earlier draft of this file that codex runs took about ten minutes
each, that concurrent runs collided, and that the sample was small because
generation was expensive. All three were wrong.

`codex exec` blocks indefinitely reading standard input unless it is redirected.
Every hang was that. Measured on the same trivial prompt: without a redirect it
ran to the timeout, and with `< /dev/null` it finished in 10.6 seconds. Once the
redirect was added, four revisions and three specifications completed in a single
pass.

The lesson generalises past this tool. I diagnosed a slow model from a hanging
process without checking why it hung, then wrote the diagnosis into a results
file as though it were an observation. It was an assumption wearing a number.

## Two findings from an independent review, which qualify everything above

A fresh-context agent was asked to design the fine-tuning experiment and to
verify rather than inherit any claim in this file. It returned a no-go, and two
of its reasons undercut the measure itself. Both were reproduced independently
before being recorded here.

### The measure is trivially gameable

A short script with no model in it, joining runs of sentences with ", and",
", but" and ", so", raises cv on the five GPT-5.6 specifications from 0.293 to
0.441 in my reproduction and to 0.702 in the reviewer's fuller version.

That is a gain of between +0.148 and +0.409, against the +0.045 that the writing
instruction bought and a noise floor of 0.043. Every word is preserved, so fact
retention is 1.00 and the existing gate never fires. The output is a run-on, and
plainly worse prose than its input.

**So cv is a diagnostic and can never be a target.** Any process that optimises
it, including a fine-tune, will find this move before it finds good writing. This
is the strongest argument against the fine-tune, and it is not about cost.

### The separation depends on a preprocessing choice we never disclosed

Thirty percent of what the instrument counts as a sentence in the human corpus is
five words or fewer, and the samples are document furniture: "Table of Contents",
"Tabs or Spaces?", "Maximum Line Length", RFC page footers, dotted contents lines.

Two defensible cleanings disagree, and they disagree by more than the effect
anyone is chasing:

| cleaning | human median | AUC human vs Claude |
| --- | ---: | ---: |
| none, as published | 0.785 | 1.000 |
| strip headings and page furniture | 0.741 | 1.000 |
| drop every sentence under 8 words | 0.450 | **0.489** |
| drop every sentence under 10 words | 0.420 | 0.391 |

A targeted furniture stripper leaves the finding intact. A blunt short-sentence
floor destroys it, and at a floor of 10 reverses it.

**The honest status is unsettled, not refuted.** Which cleaning is correct is a
real question about what a sentence is, and this file previously reported the
uncleaned number as though no choice had been made. GPT-5.6 is the exception: its
separation holds at every floor tested, so E7 stands.

### A data error of mine, corrected

Draft E4 claimed 67,964 words of the owner's own writing in session transcripts.
Measured again with the sidechain flag checked, 639 messages and 33,621 words
were typed by the owner and 121 messages and 34,924 words were prompts Claude
wrote to its own subagents. The original figure was about half somebody else's
writing, and I never inspected what was inside it.
