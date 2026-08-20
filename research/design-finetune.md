# Should we fine-tune a local model to fix the prose? A pre-registered design

Written 2026-08-20, before anything was trained. Every decision rule below was
fixed before the data it judges existed. Where I measured something in the course
of writing this, the measurement and its command are given, and it is marked
**verified**. Where I reasoned without checking, it is marked **assumed**.

## The verdict, first

**No-go.** Do not fine-tune. Not because a fine-tune would fail, but because we
cannot currently tell whether it succeeded, and building the thing before the
ruler is how you get a confident wrong answer.

Two measurements I ran while writing this are the reason. Both are new and both
undercut the target the fine-tune would chase.

**A forty-line script with no model in it moves the primary measure nine times
further than every intervention in the programme combined.** I took the five
GPT-5.6 specifications, the flattest prose measured anywhere in this project, and
joined groups of four adjacent sentences with ", and", ", but", ", so". No
rewriting. No model. Every word preserved, so fact retention is 1.00 by
construction and the existing gate does not fire. Median cv went from 0.293 to
0.702. That is +0.409, against the +0.045 the writing instruction bought and
against a 0.043 noise floor. Here is what it produced:

> This PEP proposes a standard-library interface for declaring one authoritative
> definition of a computed value, and the interface lets authors assign a stable
> identity to a derivation, but static analyzers then reject any second
> derivation that claims the same identity, so the proposal addresses values
> whose correctness depends on one canonical algorithm, policy, or source
> transformation.

Nobody would call that human writing. It is worse than the four flat sentences it
was made from. A measure that rewards it by +0.409 is not measuring what we want,
and a model trained to raise it will find this move, because it is the cheapest
move available.

**And a large share of the human reference band is document furniture, not
rhythm.** The 0.784 that the whole programme aims at comes from PEPs and RFCs.
When I looked at what the instrument counts as a sentence in those files, a third
of the segments are five words or fewer, and the ones I sampled were things like
`Hardt Standards Track [Page 26]`, `References ....................68`,
`4.1.2.1.`, `This is valid:` and `would look like:`. Those are page footers,
tables of contents, section numbers and lead-ins to code blocks. They are not
short sentences a person chose to write.

Drop segments under eight words and the separation between human technical prose
and Claude-written specifications falls from AUC 1.000 to 0.544, which is a coin
flip. Our own documents go from scoring below the human band to scoring above it.

I want to be careful here, because a blunt word floor also removes real short
sentences, and I checked that too. A targeted stripper that removes only page
footers, dot-leader contents lines and section titles leaves most of the gap
standing, at AUC 0.982. So the two reasonable ways of cleaning the corpus
disagree, and they disagree by more than the entire effect anyone is trying to
produce. **Which one is right has not been settled, and settling it costs a day.**

That is the whole argument. The target number is not yet established as a
property of prose rather than of formatting, and the measure that would judge the
fine-tune can be satisfied by a script. Spend the day on the ruler.

### The cost, so the trade is visible

| item | figure | how known |
| --- | ---: | --- |
| build the paired corpus | 6 to 10 h | assumed, by analogy with the E6 corpus build |
| download base weights, convert, quantise | 1 to 2 h | assumed; 309 GB free, HF reachable at 0.25 s |
| LoRA training runs, 3 to 5 configurations | 4 to 8 h | assumed; no timing measured, see below |
| evaluation and write-up | 4 to 6 h | assumed |
| **total** | **15 to 26 h** | |
| disk | 30 to 60 GB | assumed: 12B safetensors plus 4-bit copy plus adapters |
| the training-throughput number | **not measured** | `mlx_lm.lora --model <path> --train --data <dir> --iters 20 --steps-per-report 5` and read it/s |

Against that, my estimate that the adapter beats the +0.045 prompting already
delivers, on a measure that survives the two problems above: **I put it below
one in five, and I hold that as a judgement rather than a calculation.** The
reasoning is that all three revision arms in E3 had a negative median, both
families in E7 sit far below every human document, and the one lever that worked
worked weakly. There is no evidence in this programme that any model, prompted or
tuned, adds rhythm. The corruption operator moved text down reliably, which is
evidence that flattening is easy, not that un-flattening is learnable.

If the measure gets repaired and the gap survives the repair, come back to this
document. The design below is written so it can be picked up rather than
redone, and it is gated on that one condition.

## What I checked before forming a view

Everything under this heading is verified this session.

**The instrument reproduces its published number.** Running `ai_tells.measure`
over `corpus/dated-human/` gives a median cv of 0.784 across 20 documents, which
matches the 0.784 at n=18 in `results.md`. The two extra files are `pep-0020.md`
and one RFC that clear my five-sentence floor but not the earlier word floor. So
the harness below is measuring the same thing the programme measured.

**The gameability test.** Script at
`/private/tmp/claude-501/-Users-wumpinihussein-Documents-code-deckgen/545715f7-0ea6-413a-97b0-94f985f0f748/scratchpad/ft/gameable2.py`.
Fuse a run of `r` sentences into one every `e` sentences, leave the rest alone,
lowercase the joined initials, insert a connective from a fixed list.

| documents | cv before | cv after, r=4 e=8 | change |
| --- | ---: | ---: | ---: |
| GPT-5.6 specs, n=5 | 0.293 | 0.702 | +0.409 |
| Claude specs, n=5 | 0.504 | 0.567 | +0.063 |

The Claude documents move much less, because they already have long sentences and
the joiner has less room. That asymmetry matters: the flatter the input, the more
the script wins, and the flattest input is exactly what a fine-tune would be
pointed at.

**The prose-floor test.** Script at `.../scratchpad/ft/floor.py`. Recompute cv
using only sentences at or above a word floor.

| group | n | floor 1w | 4w | 6w | 8w |
| --- | ---: | ---: | ---: | ---: | ---: |
| human technical, PEP and RFC | 19 | 0.776 | 0.623 | 0.532 | 0.450 |
| human essay, Paul Graham | 8 | 0.632 | 0.593 | 0.540 | 0.498 |
| generated spec, Claude | 6 | 0.494 | 0.494 | 0.482 | 0.458 |
| generated spec, GPT-5.6 | 5 | 0.293 | 0.293 | 0.273 | 0.228 |
| our own documents | 3 | 0.632 | 0.582 | 0.537 | 0.489 |

And the separation those numbers produce:

| comparison | 1w | 4w | 6w | 8w |
| --- | ---: | ---: | ---: | ---: |
| human technical vs Claude specs | 1.000 | 1.000 | 0.851 | **0.544** |
| human technical vs GPT-5.6 specs | 1.000 | 1.000 | 1.000 | **1.000** |
| human technical vs our documents | 0.912 | 0.632 | 0.439 | **0.298** |
| human essay vs generated essay | 0.594 | 0.562 | 0.547 | 0.453 |

Three things fall out of that table.

The GPT-5.6 result is real and survives everything. That family genuinely writes
uniformly short sentences, and no floor rescues it. E7 stands.

The Claude result does not survive. Against date-proven human technical prose,
comparing sentences to sentences rather than sentences to page footers, there may
be no gap at all. AUC 0.544 is nothing.

Our own documents already sit above the human technical band once fragments are
removed, at AUC 0.298 in the direction that says we vary more than the PEPs do.

**The counter-test, which is why I say unsettled rather than refuted.** Script at
`.../scratchpad/ft/furniture.py`. Strip furniture by pattern instead of by
length: dot-leader contents lines, `[Page N]` footers, running headers, bare
section numbers, numbered section titles, reference entries. Human technical goes
0.776 to 0.722 and the AUC against Claude specs only falls from 1.000 to 0.982.

I do not trust that stripper either. It removed 4,666 lines it called bare titles,
and it pushed the human-essay separation from 0.594 up to 0.922, which is not
plausible and means it is eating real prose lines out of wrapped paragraphs. Both
strippers are wrong in opposite directions. That is precisely the state that
needs one careful pass rather than another argument.

## Hypothesis and null

Stated for completeness, and both are currently ill-posed for the reason above.
They become well-posed only after the measure is repaired.

**Hypothesis.** A LoRA adapter trained to invert a machine-flattening transform
raises the repaired rhythm measure on held-out, genuinely machine-written
technical prose by at least 0.05 more than prompting the same base model with the
same instruction, while retaining at least 0.98 of backticked identifiers and
while failing the anti-gaming gate on no more than 1 of 12 documents.

**Null.** The adapter matches or trails prompting on the repaired measure, or it
clears it only by the joining move the forty-line script already performs, in
which case it has learned nothing a `sed` script does not already do.

Both are falsifiable. Neither is testable today, because "the repaired measure"
does not exist yet.

## The training target, exactly

**A transform, not a voice.** Draft E4 got this right and I keep it. There is no
volume of the owner's prose in the target register (see the data section), so a
voice clone is not available. A transform can be trained from human prose that is
nobody's voice in particular.

**Which transform.** Input: machine-written technical prose. Output: the same
content with the sentence-length distribution of date-proven human technical
prose. Not "more human". Not "better". One distributional property, named, so
that failure is visible.

**Base model: Qwen3-8B, 4-bit, from Hugging Face safetensors.** Reasons, in order.

- **It must be safetensors, not GGUF.** Verified: `mlx_lm` has a `gguf.py`, but it
  is imported by `fuse.py` for export. There is no GGUF loader in `mlx_lm.utils`
  (`grep -i gguf` over the installed package returns only `gguf.py` and
  `fuse.py`). So every GGUF in `~/.cache/lm-studio/models/` and every ollama blob
  is unusable as a training base. Weights have to be downloaded fresh.
  `huggingface.co` answered 200 in 0.25 s and there are 309 GB free, so that is
  not a blocker, just a step.
- **It must be 4-bit at this size.** Verified: this machine has 32 GB of unified
  memory (`sysctl -n hw.memsize`), not more. A 12B model at bf16 is 24 GB of
  weights before activations, and the largest Metal allocation anyone has observed
  here is about 25 GB. That is not a margin. At 4-bit a 12B base is about 6.5 GB
  and an 8B about 4.5 GB, both comfortable. This is arithmetic on the parameter
  count, marked **assumed** until someone runs
  `mlx_lm.lora --model <path> --train --iters 20` and watches the memory.
- **Qwen3 over gemma3, against draft E4.** Three reasons. E3 measured gemma3:12b
  as the worst reviser tested, below the original on all three sources and failing
  the fact gate twice at 0.93 and 0.94. Training the worst writer to be the fixer
  needs an argument nobody has made. Second, the January llama.cpp checkout
  already refused ollama's repackaged gemma3 blobs, and a Qwen3 GGUF loaded
  cleanly, so Qwen3 is the family with a working path through both tools. Third,
  Qwen3-8B is already the perplexity scorer in this programme, so using it as the
  writer would make the surprisal measure circular. That third point is a reason
  to keep them separate if surprisal is ever used again, and since E2 rejected
  surprisal it costs nothing today.
- **MLX is available.** Verified: `uv pip install mlx-lm` into a clean 3.12 venv
  succeeded, giving `mlx 0.32.1` and `mlx-lm 0.31.3`, with
  `mx.metal.is_available()` true and `mlx_lm.lora`, `mlx_lm.fuse`,
  `mlx_lm.convert` on the path. `mlx_lm.lora` supports `lora`, `dora` and `full`,
  with `--num-layers`, `--grad-checkpoint` and `--mask-prompt`. `--mask-prompt`
  matters: for a transform task the loss belongs on the completion only.

## Data

Derived first, then surveyed, then judged. In that order, deliberately, because
the failure mode here is writing the requirement to match whatever is lying
around.

### 1. What this experiment requires, and why

**Kind.** Paired. Every training example is a source and a target of the same
content, differing only in the property being learned. Unpaired style transfer
exists but it needs orders of magnitude more data and a discriminator we do not
have. The pairing is what makes a few hundred examples plausible at all.

**Which half must be genuine.** The target half. The source half can be
synthesised, because the model is learning to produce targets, and a synthetic
source only shapes what it learns to condition on. This is why back-translation
works and it is the one structural idea in draft E4 that is sound.

**Register.** Technical prose that explains or specifies, matching what the
Human-Outward style is actually used to write: PR lessons, guides, procedures,
reference documents. Not essays. E6 established that rhythm does not separate
human from machine in the essay register at all, so essays cannot be targets for
a rhythm transform. This rules out the eight Paul Graham essays despite their
clean dates.

**Provenance, and how strong it has to be.** Published before 2022-11-30. Not
"looks human", not "community open source", not "no AI footer". A publication
date is the only evidence that costs nothing to check and cannot be argued with.
E6 records what happens otherwise: the `human` group was llama.cpp, a repository
with zero commits before ChatGPT whose contributors are the population most
likely to write with assistance, and the `owner-human` group contained a file
that is Claude-co-authored on 11 of the 11 commits touching it. Every band
reported before that audit was wrong. **A dated corpus is not a nicety here. It
is the only thing standing between this experiment and the last one.**

**Volume, and the justification.** I want three numbers to hold at once.

- *Passages.* Published LoRA style-transfer work operates in the hundreds to low
  thousands of paired examples, and MLX's own LoRA documentation ships examples on
  the order of a thousand training rows. I am treating **1,000 paired passages as
  the working floor and 3,000 as comfortable**, and I am marking this **assumed**,
  because I have not benchmarked it on this task and nobody should treat it as
  measured. The honest version of this line is: run the learning curve. Train at
  250, 500, 1,000 and 2,000 passages and plot the held-out score. If it is still
  climbing at 2,000, the corpus is the binding constraint and that is worth
  knowing before anything else is tuned.
- *Words.* At 150 to 400 words per passage, 1,000 passages is 150,000 to 400,000
  words of target text.
- *Documents.* The split must be by document, not by passage, because passages
  from one document share vocabulary and topic and would leak straight across.
  With held-out documents needing to be a fair sample of the register, **at least
  40 source documents** is the floor, and more is better. Twenty documents split
  80/20 gives four held-out documents, which is not a sample, it is an anecdote.

**One requirement draft E4 misses entirely.** The evaluation reference band and
the training targets must be disjoint sets of documents. If you train on the 18
PEPs and RFCs that define the 0.784 band, you have consumed the band, and there
is nothing independent left to score against. That alone means the existing
dated corpus cannot serve both roles.

### 2. What actually exists on this machine

Surveyed 2026-08-20. All verified, with the command that produced each figure.

**The assembled corpus**, at
`/private/tmp/claude-501/-Users-wumpinihussein-Documents-code-deckgen/545715f7-0ea6-413a-97b0-94f985f0f748/scratchpad/corpus/`.
Word counts via `wc -w`.

| group | files | words | provenance strength |
| --- | ---: | ---: | --- |
| `dated-human` | 20 | 178,462 | strong. PEPs and RFCs, dated 1997 to 2018 |
| `dated-essay` | 8 | 35,663 | strong by date, wrong register |
| `human` (llama.cpp) | 11 | 23,110 | **rejected by E6.** Zero commits pre-ChatGPT |
| `owner-edited` | 2 | 5,269 | weak. AI-drafted, hand-edited |
| `owner-human` | 2 | 2,294 | one file rejected by E6 as Claude-co-authored |
| `assisted` | 6 | 9,690 | known machine-assisted |
| `ours` | 4 | 14,046 | known generated |

So the clean, dated, right-register supply is exactly the 20 files in
`dated-human`, and those are the reference band.

**Claude session transcripts.** 208 project directories, 1,196 `.jsonl` files,
946 MB, spanning 2026-03-22 to 2026-08-20. Extraction script at
`.../scratchpad/ft/extract.py`.

| stage | messages | words |
| --- | ---: | ---: |
| records of type `user` | 48,998 | |
| of which tool results | 46,082 | |
| genuine authored text blocks | 2,321 | 788,387 |
| main conversation only, sidechain removed | 1,530 | 496,511 |
| after removing task notifications, headings, lists, code fences, path-dense text, session prompts | 882 | 47,386 |
| after also removing pasted grader and agent prompts | **795** | **20,450** |

The median surviving message is 14 words. The mean is 26. Twenty-nine messages
reach 100 words, and together they hold 4,571 words. A fair sample:

> the many tiny squares is actually quite ugly and might trigger peoples'
> tryptophobia

> Okay, first of all, ensure you have the latest from main, and then ensure that
> it's not present under a different name.

> yoou're working on PR 41. Launch a monitor to wait for comments on the PR

Two things this proves. The register is dictated instructions, with typos, not
prose. And **the 491 sidechain messages holding 280,873 words are subagent
prompts that Claude wrote, not the owner**, which is the trap a naive scan falls
into and probably explains draft E4's inflated figure.

**Owner's git repositories** under `~/Documents/code/`. Checked every repo's
first commit date with `git log --reverse --format=%ad`. The earliest owner-authored
repository is `personal_website`, first commit 2025-09-01. `llama.cpp` starts
2023-03-10 and is not the owner's. `Aspose.Slides-API-References` starts
2022-04-05 and is vendor documentation. **No repository on this machine contains
owner-written prose from before ChatGPT.**

**Published posts.** Six, at `~/Documents/code/personal_website/content/`, dated
by path from 2025-09-09 to 2025-11-06. All post-ChatGPT. Nine of the site's 38
commits are authored by `v0`, which is Vercel's code generator. Two of these posts
are already in the corpus as `owner-edited`, and E6 records that a commercial
detector called both fully machine-written.

**Everything else.** `~/Library/Messages/chat.db` exists at 860 KB but reads are
refused without Full Disk Access, and 860 KB is a few thousand messages at most,
in the wrong register. There is no `~/Library/Mail`. `~/Documents/superwhisper`
holds 6 dictation recordings totalling 3.3 MB. None of these is a source of
technical prose.

### 3. Does the supply meet the requirement?

**No, and not narrowly.**

| requirement | supply | verdict |
| --- | --- | --- |
| targets published pre-2022 | 20 PEPs and RFCs | present, but they are the reference band |
| right register | those same 20 | present |
| at least 40 documents | 20, of which some must be held out | **fails** |
| 1,000 to 3,000 passages | maybe 500 to 900 from 178,462 words | **fails, and doubly so once the band is withheld** |
| targets disjoint from the evaluation band | impossible with one 20-file set | **fails** |
| owner voice in the target register | 20,450 words of imperative prompts | **fails, and the register is wrong anyway** |

The owner-voice route is dead and should be recorded as dead. Not because the
volume is small, though 20,450 words is small, but because every word of it is a
prompt. Training on it produces a model that writes instructions to itself.

**What would close the gap.** One thing, and it is cheap. PEPs and RFCs are
published in bulk, individually dated, and human by construction of their dates.
There are roughly 700 PEPs and several thousand RFCs numbered below 9000, all
pre-2022. Fetching 200 of them gives 40 for the evaluation band and 160 for
training targets, disjoint by document, with the volume requirement met several
times over. That is an afternoon of downloading, and it is the only data work
this experiment needs.

Two warnings on that corpus, both of which come straight out of the measurements
above. The RFC plain-text format carries page footers, running headers and
dot-leader contents lines, and those are what inflated the band in the first
place, so they must be stripped before anything is trained or scored. And PEPs
and RFCs are specifications, whereas the Human-Outward style is used to write
teaching prose. Nobody has checked whether specification rhythm is the right
target for a PR lesson. **That assumption is inherited, unexamined, and load-bearing
for the entire programme.**

## Sample size and power

The noise floor is a standard deviation of 0.043 cv across eight identical
repeats, from E1. Two conditions on the same task, n documents each:

    n per arm = 2 * (1.96 + 0.84)^2 * 0.043^2 / d^2 = 0.02899 / d^2

| effect I care about | documents per arm | total |
| ---: | ---: | ---: |
| 0.03 | 33 | 66 |
| 0.043, one noise floor | 16 | 32 |
| 0.05 | 12 | 24 |
| 0.10 | 3 | 6 |

**The effect I would care about is 0.05, so 12 documents per arm.** Defence, in
two parts.

Anything below 0.043 is one noise floor and cannot be told from running the same
condition twice. That sets the hard bottom. Above that, the number has to be
worth the cost: prompting already delivers +0.045 for the price of editing a
markdown file, and an adapter that adds another 0.02 on top would not survive
first contact with the question "is this worth maintaining a local model for". So
0.05 is the smallest gain that changes a decision, and it is exactly the bar E1
and E3 used, which keeps this programme's rules consistent rather than tuned
per experiment.

Two corrections to that arithmetic, both of which make the real requirement
larger.

The 0.043 was measured across repeats of **one** task. Across different documents
the spread is far wider: the dated-human corpus runs 0.631 to 1.151. So the arms
must be **paired**, the same source document through both conditions, and the
statistic must be the paired difference. Unpaired, with between-document variance
in the mix, the sample needed is several times larger and the experiment is not
affordable.

Twelve per arm is the floor for the primary comparison alone. The design below
carries an anti-gaming gate and a fact-retention gate, and those need their own
documents, so **budget 12 paired evaluation documents plus 12 more held in
reserve for the gates**, drawn from held-out source documents.

## Primary measure and the decision rule

The owner's objection is right and I am building the design around it: cv alone
cannot tell you what is machine-written. E6 already showed it fails completely in
the essay register at AUC 0.664, and the gaming test above shows it can be
satisfied without changing a single word of the content. A single moment of a
single distribution is not enough.

So the primary measure is a **triple**, and all three parts must pass. Any one
failing is a failure.

**1. Rhythm, on repaired prose.** cv of sentence length, computed after the
furniture stripper agreed in the prerequisite work below, on documents of at
least 400 words. Reported as the paired difference, adapter minus prompted base,
on the same source documents.

**2. The anti-gaming gate.** The joining move raises cv by consuming short
sentences. Human technical prose has many: the dated corpus has a median 30% of
segments at five words or fewer, whereas the gamed documents have essentially
none. So the gate is on **the share of sentences of ten words or fewer**, which
in the feature scan separated human from generated at AUC 0.852 and separated
human from *gamed* at AUC 1.000. It is the one feature the joiner cannot fake,
because the joiner destroys exactly what it measures. **A document whose
short-sentence share falls below its own source's share fails, whatever its cv
did.** The exact threshold has to be set from the repaired corpus and not from
this document.

**3. Fact retention.** Share of backticked tokens surviving verbatim, at least
0.98, unchanged from E3. Note that this gate is blind to the gaming move, since
the joiner preserves every token, which is why gate 2 exists separately.

**The decision rule, fixed now.** The adapter is worth its cost if, on 12 paired
held-out documents:

- median paired cv difference against the prompted base is **at least +0.05**, and
- short-sentence share does not fall on more than **1 of the 12**, and
- fact retention is **at least 0.98 on every document**, and
- the same three hold on the real-generated held-out set, not only the synthetic
  one.

Anything less and the adapter is not built into anything. No partial credit, and
no adjusting these four lines after seeing a number. If I am tempted to, that
temptation is the finding.

## Held-out evaluation, and the inversion trap

**The trap.** We synthesise training sources by instructing a model to flatten
human prose. An adapter can learn to undo *that instruction* rather than the
genuine habit. It would then score beautifully on synthetic inputs and do nothing
whatever on real machine output. Draft E4 names this risk and names it as central,
which is correct, and then does not defend against it, which is not.

**The defence, in three parts.**

*The primary held-out set is real generated prose and contains no corrupted text
at all.* Twelve documents written by the model while trying to write well, in the
target register. The e6 and e7 specification sets are the model for how to
produce these. Any number quoted from corrupted inputs is a secondary diagnostic
and never a decision input.

*Two held-out sets, and the difference between them is itself a reported number.*
Set A is real generated prose. Set B is human prose put through the corruption
operator. If the adapter gains materially more on B than on A, it learned the
inversion rather than the habit, and the size of that difference is the evidence.
**Pre-registered: if the median gain on B exceeds the median gain on A by more
than 0.05, the result is reported as inversion-learning and the adapter is
rejected regardless of what set A did.** This is the one check that makes the
central risk falsifiable rather than merely acknowledged.

*Vary the corruption at training time so there is no single instruction to
invert.* At least three flattening operators with different prompts, plus a
purely mechanical splitter with no model in it. An adapter that inverts one
prompt cannot invert all four, so the shared structure is the only learnable
signal.

**Splitting.** By document, never by passage, and the evaluation reference band
comes from documents that appear in no training pair. With the 200-document
corpus described above: 40 for the band, 140 for training targets, 20 for
validation during training.

## Threats to validity, worst first

1. **The measure does not measure what we want, and a script beats every model on
   it.** Verified above, +0.409 from forty lines of Python. *Mitigation:* the
   three-part gate, and specifically gate 2, which the script fails by
   construction. *Residual:* a trained model may find a move that raises cv and
   preserves short sentences and is still not human writing. Nobody has enumerated
   those moves. There is no mitigation for the ones we have not thought of, and
   the only real defence is the owner reading the output blind.

2. **The target band may be an artefact of RFC formatting.** Verified above: a
   word floor destroys the gap, a pattern stripper mostly preserves it, and the two
   disagree by more than the effect size. *Mitigation:* the prerequisite work
   below, which must complete before anything else. *No mitigation exists for
   proceeding without it.*

3. **Specification rhythm may be the wrong target for teaching prose.** The
   0.784 comes from PEPs and RFCs. The style is used to write PR lessons. Nobody
   has measured whether a good human PR explanation looks like RFC 7231. *No
   mitigation, and no data on this machine that would provide one*, because
   date-proven human PR explanations from before 2022 are not a thing that exists
   in quantity. This is an admission, not a plan.

4. **The corpus cannot serve as both training target and reference band.** Verified:
   20 dated files is all there is. *Mitigation:* fetch 200. Cheap and certain.

5. **Register mismatch in the only owner data.** Verified: 20,450 words of
   imperative prompts, median 14 words. *Mitigation:* none. Drop the voice-clone
   idea entirely.

6. **A 12B model may not fit alongside training state in 32 GB.** Assumed from
   parameter arithmetic, not measured. *Mitigation:* 4-bit base, 8B rather than
   12B, `--grad-checkpoint`. *Measure it* with a 20-iteration run before
   committing to a size.

7. **Single generations.** Every source document is one draw. *Mitigation:*
   pairing, so the same source goes through both conditions, and the E1 floor of
   0.043 is the threshold below which nothing is read as a difference.

8. **We built the meter and we are now also building the thing it grades.** Two
   artefacts have already been found in it by running it on outside text, and this
   document found two more. *Mitigation:* mutation-test the repaired stripper.
   Feed it text where the right answer is known by construction, including the
   gamed documents, and check it gives the answer that was fixed in advance.

## The kill criterion

Stop, at the first of these that fires.

- **Stage 0, the prerequisite.** If the two furniture strippers still disagree by
  more than 0.05 in median human-technical cv after one careful pass, stop.
  The band is not knowable to the precision this programme needs, and nothing
  downstream of it means anything.
- **Stage 0, second gate.** If, on the repaired measure, the AUC separating
  date-proven human technical prose from Claude-written technical prose is below
  **0.75**, stop and report that there is no gap to close in this register.
  Publish it: it is the most useful thing in the programme, and it would mean the
  writing instruction is already doing everything available.
- **Stage 1, the learning curve.** If the held-out gain at 1,000 passages is
  under **0.02**, stop. Do not scale to 3,000 hoping. E1's flattening curve is the
  precedent for how that ends.
- **Stage 2, the inversion check.** If the gain on corrupted inputs exceeds the
  gain on real generated inputs by more than **0.05**, stop and report
  inversion-learning.
- **Stage 3, the gates.** If short-sentence share falls on more than 1 of 12, or
  fact retention drops below 0.98 anywhere, stop. A cv gain bought either way is
  not a gain.
- **At any stage.** If the owner reads the winning output blind against the
  prompted baseline and does not prefer it, stop. No number here outranks that,
  and none is claimed to.

## What to do instead, and it is one day of work

**Repair the measure. Nothing else, until that is done.**

1. Build one furniture stripper and settle it. Take the 20 dated documents, strip
   page footers, running headers, dot-leader contents lines, bare section numbers
   and reference entries, and then hand-check 100 randomly drawn segments against
   the question "is this a sentence somebody wrote". Fix the stripper until the
   answer is yes for at least 95 of them. Command:
   `python3 .../scratchpad/ft/short.py` prints the segments to check.
2. Re-derive the band on the repaired corpus and report it with the same instrument
   at every prose floor from 1 to 8 words, so the number's dependence on the floor
   is visible rather than hidden in a default.
3. Re-run the human-versus-generated AUC on the repaired measure, per register and
   per model family. That is the number that decides whether any of this has a
   target.
4. Add the anti-gaming gate to `ai_tells.py` and mutation-test it against
   `.../scratchpad/ft/gameable2.py`. A meter that a forty-line script defeats is
   not finished.

If step 3 comes back above 0.75 for Claude prose, this document is live and the
design above is what to run. If it comes back at 0.544, the programme has its
answer already, and the answer is that the gap it has been chasing in the
technical register was mostly punctuation in old RFCs.

## What in draft E4 is wrong

I improved it rather than discarding it. The back-translation idea is sound and
survives. Six specific things do not.

**The data claim is not reproducible, and it is wrong in the flattering
direction.** E4 says "a scan of 1,215 session transcripts yields 735 authored
messages and 67,964 words, once pasted logs, code and file dumps are excluded".
I measure 1,196 transcripts and, applying that same exclusion honestly, 795
messages and 20,450 words. The loosest defensible filter reaches 47,386 and still
falls short. The likely cause is that the scan counted sidechain messages, which
are subagent prompts Claude wrote, and there are 491 of those holding 280,873
words. E4's own conclusion from the number happens to be right, and it was right
by luck.

**The requirement was derived from the supply.** E4 estimates "300 to 600
passages" from the documents it already had. That is the failure mode this
document was asked to avoid. The requirement is 1,000 to 3,000 passages across at
least 40 documents, and the supply on hand does not meet it, which is a finding
rather than a reason to lower the requirement.

**The targets include material E6 later rejected.** E4 names "the 11 llama.cpp
documents, the owner's two edited posts, AGENTS.md, and the authored session
messages". E6 disqualified llama.cpp entirely, and disqualified AGENTS.md
specifically as Claude-co-authored on 11 of 11 commits. Roughly two thirds of
E4's target pile is contaminated. Only the dated corpus survives, and E4 predates
it.

**Training targets and the evaluation band are the same documents.** E4 splits by
document, which is right, but never notices that the documents it trains on are
the documents that define the band it will be scored against. Consume the band
and there is nothing independent to score with.

**gemma3:12b is the wrong base and E3 said so.** E4 picks it before E3 ran. E3
then measured it as the worst reviser tested, worse than the original on all
three sources, failing the fact gate at 0.93 and 0.94. E4 was never updated. On
top of that, `mlx_lm` cannot train from the GGUF that ollama holds, so "a LoRA on
gemma3:12b" understates the work by a download and a conversion. E4 says "MLX is
not currently installed", which was true and is a smaller obstacle than it looks:
verified today, it installs clean in about a minute.

**The central risk is named and not defended.** E4 says the corruption may not be
the real distribution, calls it the central risk, and then offers only "the
held-out set must be real generated prose". That is necessary and it is not
sufficient, because it gives no way to detect inversion-learning when it happens.
The two-set comparison and the 0.05 divergence rule above are what turn the
warning into a test.

**And the thing E4 could not have known.** Its primary measure is cv alone, with
one line admitting the measure can be gamed by "inserting one long sentence per
paragraph" and the observation that "reading" catches it. Reading does not scale
to a training loop, and the gaming is worth +0.409, which is larger than any
effect this programme has ever measured. That is not a caveat. It is the reason
the experiment is on hold.
