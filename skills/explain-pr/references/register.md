# The register

Read this when the repository keeps a register of lessons, or when you are
creating one. It covers the entry format, the glossary rule, and supersession.

The register is one file kept beside the lessons, doing two jobs. It holds the
agreed vocabulary, and it logs what each lesson taught.

Without it you have a folder of files. With it, the set reads three ways:

- by the parts of the system a change touched
- by the rules a change tested
- straight through, by date

The third reading is the one people expect. The first two are why the register
earns its small cost.

## Log entries

Newest last. A heading per lesson, then a block of fields, then the prose.

    ### PR 52: the plan/write split on text

    - file: pr-52.html
    - range: <base sha>..<head sha>
    - parts: <the parts of the system the change reaches>
    - rules: <the repository invariants it serves, by number or name>
    - reverses: <an earlier entry, or (none)>

    Then the prose. Say what the lesson taught, not what the PR did.

The fields exist to be checked. A checker reading them catches three things:

- a range that no longer resolves
- a part that does not exist
- a rule number the repository never defined

Each means the entry has gone stale, and none of them is visible by reading.

## Glossary entries

A term goes in once a lesson has taught it. Define what the term **is**, in a
sentence or two, rather than how to use it.

Prefer the repository's own words wherever they exist. A conventions file or a
specification outranks anything invented while writing a lesson, since those are
what the code was built against.

**Revise a wrong entry where it stands.** A glossary is a definition, and one
term with two definitions is worse than none. This is the one place the
immutability rule below does not apply, precisely because a definition is not a
record.

## Supersession

A lesson says what a change taught **on the day it landed**, and stays that way.
The reason is the one that keeps old measurements unedited: rewriting one
destroys the history that made the set worth keeping.

This is not a hypothetical worry. One lesson taught a constant, and taught that a
value was deliberately absent from a type. Sixteen commits later the constant was
gone and the value was back.

Leave that lesson unmarked and a reader learns two false things. The file still
looks entirely current.

So when a later change reverses a lesson, three things happen together:

1. The new entry names what it reverses, in its `reverses:` field.
2. The old entry gains a `superseded-by:` field.
3. The old lesson gains a banner at the top of its body, naming the lesson that
   replaced it and saying what was overturned. Nothing else in that file changes.

That banner is the one edit a shipped lesson takes.

Have the checker fail when any one of the three is missing. Two out of three is
worse than none, because from the outside it looks handled.

## What the register still will not tell you

It records what was taught, not what anyone retained, and tidying the log will
not change that.

Slicing by part also inherits the system map's blind spots. A part the map does
not attribute gets named in no entry, so a slice by it comes back empty rather
than wrong. Empty is much harder to notice.

Both gaps have the same fix, and it is not a tool. Ask your reader.
