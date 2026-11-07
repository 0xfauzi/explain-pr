# Spec: shared repos and the codebase guide

Part of `../PRODUCT.md` (section 10). Draws on `../concepts/teams.md`. Everything here is for a developer who works in a repo other people share.

---

## 1. Shared-repo rules

A repo is shared unless the user's own account owns the remote, or the user marked it as theirs. Unknown counts as shared. In a shared repo, teammates must not learn from the repo what the user is new to.

- No learning data in any branch, commit, trailer or PR body.
- Your-line markers are plain `TODO:` comments with the goal and the test, no product name, no user name. The engine finds them by location and region hash, not by text.
- Open markers are handed back before commit, so they are never committed.
- A cloud agent opening a PR keeps open lines only in its import blob, never in the PR.
- The optional merge check (`firsthand ci`) message is neutral: `Open TODO in retry.py:42.` It fails only on a TODO the engine recorded and nobody resolved. A hotfix branch skips it.
- Who wrote a line is never written to commits, trailers or PRs.
- Review-first findings are private. Posting one is the user's own plain review comment.
- Optional PR walkthrough: the author writes a walkthrough for reviewers. The engine gives private feedback on it. Reviewers see the text only.

---

## 2. The codebase guide

A shared repo holds knowledge no catalog has: which ideas matter here, where they live, how they break, and who knows them. Learning in the context where the skill is used transfers best (Arthur et al. 1998, research/learning-science.md D.3). The guide puts that knowledge in the repo, as plain files, so the loop can use it.

### 2.1 Files

```
.firsthand/guide/
  guide.toml            areas, owners willing to help, settings
  ideas/<idea>.md       one file per codebase idea
  lines.toml            nominated "lines worth writing by hand once"
  drills/<id>.md        rehearsals drafted from postmortems; keys not here
```

Each idea file: the idea in one sentence, where it lives, why it matters here, how it breaks, an optional owner "how I debug this" note, and who is willing to help. No personal data. Committed only if the team chooses, and reviewed in PRs like code.

### 2.2 Trust rules

- A guide is read only in repos the user marks as theirs or trusted, once per repo, confirmed in the pad.
- Guide text is shown quoted and attributed: `From this repo, written by contributors:`.
- Owner notes and drills have commands, URLs and code fences removed before display.
- Guide content can never change a setting, run a command, or widen anything.

### 2.3 Writing it

- `firsthand guide draft` proposes ideas with paths as a PR. Seniors edit and delete.
- `firsthand drill from <postmortem>` drafts a rehearsal with the real resolution sealed. Logs and text are scanned for secrets and personal data; the author sees each redaction and approves before save (`security.md` section 7).
- `firsthand handover <area>` drafts entries when someone rotates off an area.
- `firsthand guide check` lists ideas whose paths no longer exist.

### 2.4 How the guide feeds the loop

- Guide ideas are private catalog entries in the repo's namespace, shown on the map under "This codebase".
- Owner notes appear only after the learner's own attempt (L18).
- Nominated lines become your-line offers in that area when the idea is new to the learner.
- Postmortem drills become rehearsals: symptoms and logs first, the user's hypothesis and first safe action, then the real resolution (L16).
- Guide items ship without keys. The engine writes keys in a separate context.

---

## 3. What is not here

No admin console, no team reports, no usage counts, no single sign-on, no proctoring, and no way for anyone but the user to read their record. The record belongs to the person who owns it.
