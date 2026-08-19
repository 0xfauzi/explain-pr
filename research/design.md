# Can AI writing be made to read as human? A pre-registered design

Written before the experiments were run. The decision rules below are fixed in
advance, because a rule chosen after seeing results is not a rule.

## The question, and why the obvious answer is not available

We want prose that a person recognises as written by a person. The obvious
measurement is to ask people, and it is unavailable at the scale needed: one
reader, a handful of judgements, no way to run it on every draft.

So we measure two proxies drawn from published detection work, and we test
whether either separates text whose provenance we already know. A proxy that
cannot separate known classes cannot judge unknown ones, and that is the first
thing to establish rather than assume.

## Measures

**Rhythm (cv).** The coefficient of variation of sentence length in words:
standard deviation divided by the mean. Generated prose is uniform, human prose
alternates short and long. Reported instead of raw standard deviation so
documents with different average sentence length can be compared.

Computed by `skills/explain-pr/scripts/ai_tells.py`. Segments over 80 words are
dropped as non-prose and the count is reported, because unstripped code inflated
an earlier corpus median from 0.74 to 0.92.

**Surprisal (nll).** Mean per-token negative log-likelihood of a document under
`gemma3:12b`, computed with `llama-perplexity` over ollama's stored GGUF.

The scoring model must not be the writing model or the measure is circular: a
model finds its own output predictable by construction. Gemma is open-weights,
local, and from a different family to anything that wrote our corpus, which makes
it an independent reader rather than a mirror.

**Fact retention.** The share of backticked tokens in a source text that survive
verbatim into a rewrite of it. A style transform that loses an identifier or a
command has failed regardless of how it reads.

## Corpus

Twenty-five documents, grouped by how they were produced. Provenance is asserted
from evidence, not from impression.

| group | files | words | how provenance is known |
| --- | ---: | ---: | --- |
| `human` | 11 | 23,110 | llama.cpp docs, many contributors, community review |
| `owner-human` | 2 | 2,294 | written by the owner by hand: AGENTS.md, session messages |
| `owner-edited` | 2 | 5,269 | owner's published posts, AI-drafted then edited by hand |
| `assisted` | 6 | 9,690 | owner's PRs carrying a Claude Code footer |
| `ours` | 4 | 14,046 | this repository's own documents |

`owner-edited` is the most interesting group, because it is the condition we are
actually trying to reach: a model drafted it and a person improved it.

## Experiment 1: is there headroom in selection?

**Motivation.** Rewriting a draft to sound human failed on four of four sources
tested earlier: it improved one, was neutral on one, and made two worse. A
rewrite is another draw from the same distribution. Selection is different,
because it never destroys variation, it only picks among drafts that already
have it.

**Hypothesis.** Independent generations of one writing task differ enough in
rhythm that keeping the best of several raises cv materially.

**Null.** Draft-to-draft spread is small relative to the gap we need to close,
which is roughly 0.08 cv from our 0.649 to the owner's 0.726.

**Method.** One fixed writing task. Eight independent generations, same prompt,
same model, same settings, no seed control. Measure cv for each. Compute the
expected maximum of n for n = 1 to 8 by resampling without replacement.

**Primary measure.** Expected best-of-5 cv, minus the median single-draft cv.

**Decision rule, fixed in advance.** Selection is worth building if the expected
best-of-5 exceeds the median draft by at least 0.05 cv AND the expected best-of-5
reaches 0.726. Otherwise it is not, whatever the spread looks like.

**Guard.** cv can be inflated by one runaway sentence, so any draft whose longest
sentence exceeds 120 words is reported separately rather than counted as a win.

## Experiment 2: does surprisal separate provenance?

**Motivation.** The detection literature pairs burstiness with perplexity. We
have only ever measured burstiness. If surprisal separates classes we already
know, it earns a place; if it does not, everything built on it would rest on
nothing.

**Hypothesis.** Mean per-token surprisal under gemma3:12b is higher for
human-written prose than for model-generated prose of the same genre.

**Null.** The groups overlap, so surprisal carries no provenance signal at
document level.

**Method.** Score every corpus document, plus the sixteen round-trip outputs
already on disk, which have known provenance because we generated them.

**Primary measure.** Median surprisal per group, with the range.

**Decision rule, fixed in advance.** Surprisal is usable if the `human` and
`ours` groups separate with non-overlapping interquartile ranges. Partial
separation counts as unusable at document level, and in that case the fallback
claim to test is the localisation one below, not the aggregate.

**Threat, stated in advance.** Genre and vocabulary drive surprisal at least as
hard as authorship. A document dense with rare identifiers scores high whoever
wrote it. Comparison is therefore only meaningful within genre, and every group
here is technical prose. Code is stripped before scoring.

**Second threat.** Low surprisal is not bad writing. Plain, conventional prose is
predictable by construction, and our own style rules ask for exactly that. So
surprisal is never a target to maximise. If it is useful it will be as a
locator: long flat runs, not low averages.

## Experiment 3: does a different model family revise better?

**Motivation.** Published work finds that structural habits learned in training
survive explicit instructions to write differently. If the flattening belongs to
the model rather than to the prompt, a different family should not share it.

**Hypothesis.** A revision pass by a different model family raises cv more than
the same family given the identical instruction.

**Null.** Revision quality is a property of the instruction, so family does not
matter.

**Method.** Four source drafts of different kinds. Each revised three ways with
byte-identical prompts: Claude (same family as the writer), a GPT-class model
through `codex`, and `gemma3:12b` locally. Measure cv delta against the source,
and fact retention.

**Primary measure.** Median cv delta per reviser, with fact retention as a gate.

**Decision rule, fixed in advance.** A cross-family reviser is worth the
dependency only if its median cv delta beats same-family by at least 0.05 AND its
fact retention is at least 0.98. A reviser that gains rhythm by dropping content
has not helped.

## What would falsify the whole programme

If E1 shows no selection headroom, E2 shows no separation, and E3 shows no family
effect, then none of the available levers move the measure, and the honest
conclusion is that rhythm has to come from the writing instruction at generation
time or not at all. That is a real result and it gets reported as one.

## Threats that apply to everything here

- **Single runs.** Each generation is one draw. Differences smaller than the
  draft-to-draft spread measured in E1 are not interpretable, and E1 is run first
  partly to establish that floor.
- **cv is a proxy.** It correlates with what we want; it is not the thing itself.
  A text can vary its sentence length and still read badly.
- **The human band is thin.** Two documents for `owner-human`, and the corpus is
  entirely technical. None of it transfers to essays without its own sample.
- **We built the meter.** It was fixed from published sources before our own
  prose was measured, and two artefacts in it have already been found and
  corrected by running it on outside text. More may remain.

## Experiment 4: can a local model be taught the transform?

Added after the first three were written, and gated behind them: if selection or
a cross-family reviser closes the gap, this is unnecessary work.

**The obvious version, and why it is wrong.** Fine-tune a small open-weights
model on the owner's writing so it writes in that voice. The data exists. A scan
of 1,215 session transcripts yields 735 authored messages and 67,964 words, once
pasted logs, code and file dumps are excluded, which is roughly 40% of the raw
total and the rest is material the owner pasted rather than wrote.

The problem is register. Those 735 messages are prompts: terse, imperative,
frequently annoyed, often mistyped, mean length 92 words. Training on them
produces a model that writes like the owner's prompts. Nobody wants an essay in
that register, including the owner.

**The better version: learn the transform, not the voice.** Style transfer has a
standard answer when you lack paired data, which is back-translation. Take real
human prose as the target. Corrupt it toward the machine attractor to synthesise
the source. Train the model to invert the corruption.

Only the input side is synthetic. Every target is genuine human writing, which is
the half that matters.

This is available to us because the corruption operator is already validated.
Pushing text toward the AI attractor lowered rhythm on four of four sources
tested, from four different starting points. It is the one operation in this
whole programme that has behaved reliably.

**Hypothesis.** A LoRA adapter on gemma3:12b, trained on synthetic pairs whose
targets are real human prose, raises cv on held-out machine-written text more
than prompting the same base model to do the same job.

**Null.** The adapter matches or trails prompting, so the transform is not
learnable from this quantity of data.

**Method.**

1. Targets: human prose only. The 11 llama.cpp documents, the owner's two edited
   posts, AGENTS.md, and the authored session messages, segmented into passages
   of 150 to 400 words. Estimated 300 to 600 passages.
2. Sources: each target corrupted by the AI-max operator, one pass, meaning
   preserved.
3. Split by document, never by passage, so no document appears on both sides.
   Passages from one document share vocabulary and would leak.
4. Train a LoRA with MLX on Apple Silicon. MLX is not currently installed.
5. Evaluate on held-out machine-written text the adapter has never seen.

**Primary measure.** Median cv delta on held-out inputs, adapter against the same
base model prompted rather than trained.

**Decision rule, fixed in advance.** The adapter earns its cost if it beats
prompting by at least 0.05 median cv delta with fact retention at least 0.98.

**Threats, stated in advance.**

- **The corruption is not the real distribution.** We synthesise "AI-flavoured"
  text by instructing a model to write badly. That is not the same distribution
  as text a model produced while trying to write well, and an adapter may learn
  to undo our instruction rather than the genuine habit. This is the central
  risk, and the held-out set must be real generated prose, never corrupted prose.
- **Quantity.** A few hundred passages is at the low end even for style work.
- **Target contamination.** The owner's edited posts were AI-drafted, so they are
  not clean human targets. They are labelled `owner-edited` and reported apart
  from `human` for exactly this reason.
- **The measure can be gamed.** A model can raise cv by inserting one long
  sentence per paragraph. Fact retention does not catch that; reading does.

## Design review

Reviewed against the design after writing it, before running anything.

**What holds.** Every experiment has a null, a primary measure and a numeric
decision rule fixed before data. Each proxy is validated against known classes
before being trusted on unknown ones, which is the ordering that matters. E1 runs
first and establishes the draft-to-draft floor, so later experiments have a
threshold below which differences are not interpretable.

**Weaknesses I can name, in order of severity.**

1. **cv is one number and it is a proxy.** Everything here optimises it. It
   correlates with what we want, and it is not the thing itself. Mitigation: the
   owner reads the winning output and says whether it reads better. No measure
   here replaces that, and none is claimed to.
2. **Group sizes are small and unequal.** Eleven human documents against two
   owner-written ones. Medians and ranges are reported rather than means and
   confidence intervals, because the samples do not support the latter.
3. **One genre.** All technical prose. Nothing here transfers to essays, which is
   the stated target, without a separate essay corpus.
4. **Single generations in E3.** Only E1 repeats a condition. E3's differences
   are only interpretable against the spread E1 measures, which is why E1 is
   first.
5. **We wrote the meter.** Two artefacts in it have already been found by running
   it on outside text and both changed the answer materially. That is evidence
   the process works, and also evidence that more may remain.

**What would make me distrust a positive result.** A win that appears only on our
own documents and not on the outside corpus. A cv gain accompanied by fact
retention below 0.98. Any decision rule I am tempted to adjust after seeing the
number.

## Deviations from this design, recorded as they happened

**Scoring model changed from gemma3:12b to Qwen3-8B (bf16).** Recorded before E2
was run, not after seeing any result.

Two candidates failed to load. Ollama repackages GGUF metadata and its gemma3
blob is missing `gemma3.attention.layer_norm_rms_epsilon`, which this llama.cpp
build requires. LM Studio's `gemma-4-12B-it-QAT` is a clean GGUF but declares
architecture `gemma4`, which postdates the checkout.

Qwen3-8B loads and scores at 8.8 seconds per pass. It satisfies the property the
design actually requires, which is that the scoring model comes from a different
family than anything that wrote the corpus. It is smaller than intended, so
absolute perplexity values are not comparable to any published figure. Only the
comparison between groups is used, and that comparison is internally consistent
because every document is scored by the same model.
