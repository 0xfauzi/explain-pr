# Critique: platform engineering

Reviewer lens: staff platform engineer (Claude Code, Codex, MCP, MCP Apps,
artifacts, hooks, web push). Date: 2026-11-07. No package files were edited.

Scope read: `architecture/recommended.md` (all), `experience.md` (sections 0,
2.a, 2.b, 3.0), `research/claude.md` and `research/codex-others.md` (claims
checked by grep), `index.html`, all eight prototypes, and the shipped code the
design builds on (`skills/learning-while-building/scripts/room.py`,
`assets/room.html`, `.mcp.json`).

Evidence sources I used in this session, beyond the package:

- The artifact runtime type definitions for contract 0.2.96
  (`room.d.ts`, `db.d.ts`) and the capability guidance served to this session.
- `https://code.claude.com/docs/en/hooks.md`, fetched now and grepped.
- This container's environment and tool list.
- Playwright screenshots at 1440 and 390 of `index.html` and all prototypes,
  in `/tmp/claude-0/-home-user-explain-pr/074e39f7-08cf-5ec8-b66b-62906beb6d01/scratchpad/le-shots/`.

## Verdict

The package is honest about most integrations. The tag system ([T], [D], [R],
[S]) and the dependency register (recommended.md section 12) are the right
discipline, and most tags hold up. The hook names are real. MCP Apps are kept
out of Claude Code. The Room is correctly chosen as the one designed surface
that works on both of the owner's devices.

The weak part is the data plane, not the doors. Three things in phase 1 do not
work as written: on-page grading needs a rubric that nothing can deliver after
the lock, the owner's main surface (a cloud session on a public repo) has no
durable home for the record, and the artifact db has no transactions, so two
writers on one doc can lose an answer. All three are fixable with small,
boring changes. The phase 2 "no extra turn" bell is also overstated, and there
is a better, documented path the package did not find.

## What I verified

| Claim | Where | Result |
|---|---|---|
| Hook events `MessageDisplay`, `PostToolUseFailure`, `PostToolBatch`, `FileChanged`, `PreCompact`, `Stop`, `idle_prompt`, handler option `asyncRewake` exist | research/claude.md lines 30, 66, 82 | Confirmed [D]: hooks.md has 22, 20, 17, 24, 17, 69, 5 and 4 matches. |
| `CLAUDE_CODE_MESSAGING_SOCKET` exists in this session | research/claude.md line 22 | Confirmed [T]: present in the environment, with `CLAUDE_CODE_MESSAGING_TOKEN`. Wire format still undocumented, correctly [S]. |
| A project stdio MCP server loads in this session | recommended.md register 1 | Confirmed [T]: `.mcp.json` registers `learning-question`, and `mcp__learning-question__learning_question` is in this session's tools. |
| `room.sendToClaudeSession` exists | register 8 | Exists [D], but its behaviour does not match the phase 2 claim. See M1. |
| Artifact db can hold a lock | recommended.md 4.2, 10 | No. `db.d.ts`: "Writes are last-writer-wins; there are no transactions." See B3. |
| No em dashes (U+2014) | whole package | Confirmed: zero matches. |
| No horizontal scroll at 390 | index and 8 prototypes | Confirmed: `scrollWidth` 390 on all nine pages. |
| No console errors | index and 8 prototypes | Fails on all 8 prototypes: one 404 each. See m1. |

## Blockers

### B1. On-page grading in phase 1 needs a rubric that nothing can deliver after the lock

- recommended.md 9.3: "In the Room db, the rubric is a separate doc that
  `room-push` writes only after the page reports a lock."
- experience.md 2.b step 5: "Then the page asks the server for the rubric doc
  (written only after a lock)." Step 6 grades on the phone in 1 to 4 s.
- prototypes/flow.html line 325: "rubric doc written after lock / sample:
  grading on the page".

There is no server. `room-push` is a session command, and in 2.b the session's
turn has ended and Sam is away from the laptop. Phase 1 has no bell (that is
E-SEND, phase 2), so no one can write the rubric doc after the lock. Either the
phone waits for Sam's next laptop message (which breaks step 6 and the phase 1
acceptance test, "reads the page's feedback on the phone"), or the rubric is in
the db before the lock.

Today's code already chooses the second, without saying so: `room.py`
`cmd_room_push` calls `room_rows(root, with_rubric=True)` and writes the rubric
into the same `questions/<id>` doc that `room.html` `hostedStore.subscribe`
streams to the browser with `onSnapshot`. The rubric is in page memory before
the learner answers.

Fix (simple and robust for the stated threat model, "an accidental glance"):
write the rubric at post time to a separate doc, `keys/<id>`. The page never
subscribes to `keys/`. It calls `db.doc("keys/" + id).get()` once, after the
answer doc is written. The card keeps `rubric_commit`, and `learning.py check`
verifies it on import. State the residual risk in Settings, as section 9.3
already plans. Remove "written only after a lock" from all three files.

### B2. The owner's main surface has no durable home for the record in phase 1

- The owner works in cloud sessions, and `origin` is the public
  `github.com/0xfauzi/explain-pr`.
- recommended.md P1.5: until E-REPO passes (phase 2), "a public project keeps
  the record in a Room db mirror and in local files only".
- recommended.md 4.3: in a cloud session the sealed root is "a `sealed/` folder
  in the private record repo". That repo is E-REPO, phase 2.
- recommended.md 10: the Room db is an inbox, "not replicas".
- Neither document says when the record is committed and pushed.

A cloud container is ephemeral. Local files, `~/.lwb/sealed/`, `events.jsonl`
and the schedule are lost when the container is replaced. In phase 1 the
owner's own project therefore has no system of record. The Room db is the only
thing that survives, and the architecture says it is not the record.

Fix: run E-REPO in phase 1 (under an hour, and `add_repo` exists in this
session). Add one explicit persistence step: after every grade, `lwb` commits
and pushes the record repo (`git pull --rebase`, then retry once). If E-REPO
fails, declare the Room db the system of record for public projects. Store one
doc per event, and add `learning.py export` to rebuild the files from it. Do
not ship a phase in which the store is undefined.

### B3. The db is last-writer-wins, and two writers share one doc

`db.d.ts` (DocumentReference.set): "Write the WHOLE document ... Writes are
last-writer-wins; there are no transactions." The design has two writers on
`questions/<id>`: the agent (`room-push` writes whole docs through
ArtifactData) and the page (`answer: ref(id).update({status: "answered",
answer, ...})` in room.html).

Failure case: Sam locks on the phone at 14:02. At 14:03 the laptop session
re-pushes open cards, because its local copy still says "open". The `set`
replaces the doc, and the answer is gone. recommended.md 4.2 says "the earliest
`locked_at` wins". The db cannot enforce that, and the chat lock time is when
the agent calls `lwb_lock` at a turn boundary, not when Sam typed.

Fix: one writer per doc.

- `cards/<id>`: written only by the agent.
- `answers/<id>/<attempt uuid>`: created only by the page, and never updated.
- `grades/<id>`: written by the page after `sample`.

Import takes the earliest answer doc and keeps the others as `also_answered`.
For chat locks, use the timestamp of the learner's message, not the time of
the tool call. In code review, enforce that the agent never writes `answers/`.

## Major

### M1. The phase 2 bell does not give "no extra turn", and a better path exists

`room.d.ts` says `sendToClaudeSession` defaults to `deliver: "stage"`.
"Nothing reaches Claude until the viewer sends their own message with it."
With `deliver: "send"`, "the platform shows the viewer what this page is about
to send and asks them, in its own dialog". With nothing open beside the page,
"the browser leaves this page". The "session" route goes to "a Claude session
of this viewer's it already knows has the artifact". The type file does not say
that a Claude Code cloud session can be that target. Also, the room's agent
peer is "flag-gated, off by default" (room.d.ts line 53).

So the phase 2 acceptance test ("rings the session ... with no extra turn",
recommended.md section 2; index.html "How it ships") is at best one
confirmation tap. On the phone Room, the tap may also take the learner away
from the page.

Better candidate (documented in this session's capability guidance): a page
can call this session's `mcp__claude-code-remote__*` tools through the
built-in claude.ai connector "Claude Code Remote". `send_message` takes an
explicit `session_id`, and the card already has `return.claude_session`. Add
E-CCR-SEND: declare `mcp: {servers: [{server: "Claude Code Remote", tools:
["send_message"]}]}`, call `listTools()` first (viewers may have fewer tools),
and send only `{card: id, event: "locked"}`, never the answer. Keep
`sendToClaudeSession({deliver: "send"})` as the second rung and the pull rule
as the floor. Change the acceptance wording to match what passes.

### M2. "Phase 1 tested" claims more than was tested

index.html "How it ships" says "Phase 1 uses only what we tested", and
recommended.md 11 says "Everything here is [T]". But:

- `lwb` is not built.
- Rubric privacy through an MCP tool input is [S] (register 10), and P1.2
  depends on it.
- B1 is a contradiction, not a test.
- The offline queue (M3) is untested.
- The pull rule's ArtifactData reads and the `lwb` tools may raise permission
  prompts (M6).

Relabel as "built only on tested parts", and list the experiments that must
pass before phase 1 can claim the acceptance test: E-SEAL, E-REPO, E-OFFLINE
(new), E-PERM (new) and E-CCR-SEND (new). Each takes under an hour.

### M3. Offline answers are promised with no tested mechanism

- experience.md 2.b offline branch: "saved on this phone and sent when you are
  back online".
- card.html line 371 and flow.html line 330: "queue in page storage, retry on
  online".

The artifact contract says browser storage "can come back empty, or the
accessor can throw", in private windows, previews and with cleared data.
`db.d.ts` says that pending writes show with `hasPendingWrites`, but it does
not say that they survive closing the page. An iOS webview that is suspended
in the background is the normal case. The Room also cannot load from claude.ai
when the phone is offline, and `sample` cannot grade offline.

Fix: until E-OFFLINE passes (airplane mode, lock, close the Claude app,
reopen, go online, check the db), the copy says "Not sent yet. Keep this page
open until it says Sent." The page watches `hasPendingWrites` and shows "Sent"
only on a confirmed snapshot. "Saved here" is a promise that the platform does
not make.

### M4. The learner's answer travels through the model before it reaches the record

`lwb` is a stdio MCP server. It cannot call ArtifactData, which is a harness
tool. So "import" (recommended.md 8, rank 2; experience.md 2.b step 8) means
that the agent reads the db rows inline and then passes the text to
`learning.py import`. The model transcribes the learner's answer, and the
rubric passes through its context again. A long answer can be truncated or
paraphrased with no one noticing.

Fix: the page stores `sha256(answer)` next to the answer. `learning.py import`
reads JSON on stdin, recomputes the hash, and rejects a mismatch with "Answer
changed in transit. Not imported." This uses only the standard library and
makes "lost or altered answers" detectable.

### M5. Git sync is conflict-free only for the append-only files

recommended.md 10 says sessions and scheduled-task branches "merge with no
conflicts [T]". That holds for one file per attempt and for union-merged
`*.jsonl`. It does not hold for `open.json`, `map.json`, `config.json`,
`dimensions.json` and `topics/*`. These are rewritten JSON files, and parallel
cloud sessions write them. Fresh-session scheduled tasks (E-SCHED) push to
their own branches, and nothing merges those branches back.

Union merge also duplicates lines after a rebase or cherry-pick.

Fix:

- Do not commit derived files. `map.json` and `open.json` are rebuilt from the
  events.
- Only the learner's Settings writes `config.json`.
- Scheduled tasks write to the Room db only, never to git.
- Every event line carries a uuid, and the reader removes duplicates.
- The record repo uses one branch, with pull, rebase and retry.

### M6. Permission prompts break "No stall"

recommended.md section 2 tests "Time from 'Not now' to the next tool call:
under 5 s". In default permission mode, the first call to each `lwb` tool, and
the ArtifactData read on every turn while a Room card is open, can each stop
for approval. A project MCP server from `.mcp.json` can also need a one-time
approval. Ship a `.claude/settings.json` allow list for `mcp__lwb__*` and the
ArtifactData read, and add E-PERM: a fresh cloud session in default mode runs
the whole 2.a journey and counts the prompts. The target is 0 after the first
approval.

## Minor

- **m1. Grain 404 on every prototype.** All eight prototypes load
  `url(../../../docs/assets/grain.png)`. It resolves only when the repo root is
  served. Served from the package folder (as this review was told to do), on
  Pages (which publishes `docs/`), or as an artifact, it is a 404. There is one
  console error per page at both widths. index.html has none. Inline the grain
  as a small data URI, or copy it into the package.
- **m2. Register 38 (artifact `mcp` to a local server) is not [S].** It is
  documented as impossible for cloud sessions. `host:` servers "only answer
  when the viewer opens the page in a Claude app that has that same local
  server connected". A cloud session's `lwb` runs in the container. Mark it
  local-desktop only.
- **m3. Sealing default.** The subagent path (a subagent writes the rubric
  from the code and calls `lwb_seal`, and the main transcript sees only the
  hash) is listed as the E-SEAL fallback. Make it the default. It works
  whatever the app shows for tool inputs, and it keeps the rubric out of the
  main agent's context, which also lowers the risk that a hint gives the
  answer away.
- **m4. The sealed-root read guard is a string match.** A `PreToolUse` deny on
  paths is bypassed by `python -c`, `git show` or `grep -r`. That is acceptable
  for the accidental-glance model, but say so in section 9, and keep plaintext
  rubrics out of any path that a normal project search touches.
- **m5. Capability minimalism.** The Room declares `db`, `sample`, `room`,
  `user` and `mcp` (register 4). Each grant can ask the viewer for consent on
  the phone, which is friction at the worst moment. Phase 1 needs `db` and
  `sample` only. Add `mcp` with exactly one tool when E-CCR-SEND passes.
- **m6. Codex async input is gated.** `request_user_input_async` is "when
  enabled by the model catalog" (codex-others.md line 22). The skill cannot
  turn it on. Keep it as [D], but make the door choice depend on whether the
  tool is present, not on the harness name.
- **m7. Visual: phone action bar.** card.html at 390: the sticky bar (Not now,
  I do not know, Lock my answer) takes about 170 of the 844 px. The answer
  field and confidence are below the fold on first view. With the iOS keyboard
  open, the field and the bar compete. Test with `visualViewport`, and hide the
  secondary row while the field has focus.
- **m8. Visual: two left edges on wide Room pages.** map.html at 1440: the Room
  shell ("Room orbit-pay" and the tabs) starts at about x=162, and the content
  column starts at about x=272. Align them to one edge.
- **m9. Copy conflicts with behaviour.** The index hero says "it stops and asks
  you one question: before it builds". The flow and 2.a step 3 say "It does not
  wait." Use "asks" without "stops", so the front page matches the no-stall
  design.

## The three changes that would most improve the product

1. **Make the data plane single-writer, hash-verified and durable from day
   one.** Use separate `cards/`, `answers/` (create once), `keys/` (read once
   after the lock) and `grades/` docs. Add `sha256` on answers and verify it at
   import. Run E-REPO now, and commit and push the private record after every
   grade. This removes B1, B2, B3 and M4, and it is about one day of work in
   `room.py` and `record.py`.
2. **Replace the speculative bell with a tested ladder.** The page calls
   "Claude Code Remote" `send_message(return.claude_session, {card, event})`
   (E-CCR-SEND). The next rung is `sendToClaudeSession({deliver: "send"})`,
   with one confirmation tap stated honestly. The floor is the pull rule. This
   is the real path to "the grade is in chat when you come back" on the
   owner's surface, and it needs no daemon and no tunnel.
3. **Before writing `lwb`, spend one afternoon on five one-hour experiments:**
   E-SEAL (with the subagent path as default), E-REPO, E-OFFLINE, E-PERM and
   E-CCR-SEND. Then change "Phase 1 tested" and the copy ("Saved here", "rings
   the session") to say only what passed. The product feels seamless only if
   it never promises a state that the platform did not deliver.
