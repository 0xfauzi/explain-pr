# Learning Opportunities (Cat Hicks): direct read

Read on 16 November 2026 from a clone of https://github.com/DrCatHicks/learning-opportunities (last commit 19 August 2026, licence CC-BY-4.0). Files read: README.md, the core SKILL.md, the auto hook script and CHANGELOG.md. PRINCIPLES.md and MEASURE-THIS.md were not read.

## What it is

Three plugins for Claude Code and Codex:

- `learning-opportunities`: a skill. After "architectural work" (new files or modules, schema changes, refactors, unfamiliar patterns, or work where the user asked "why"), the agent offers an optional exercise of 10 to 15 minutes.
- `learning-opportunities-auto`: a PostToolUse hook on the Bash tool. When the command is a git commit, it adds a note that tells the agent to consider an offer. It stops after 2 offers in a session.
- `orient`: writes an orientation file for a new repository, with suggested lessons.

## Does it use prediction? Yes.

The README lists six exercise types. The first is "Prediction, Observation, Reflection": "What do you expect to happen? Now let's see. What surprised you?" Others are "Generation, Comparison" (sketch your approach before you see the implementation), "Trace the path" (predict each step of an execution), "Debug this", "Teach it back" and a "Retrieval check-in" at the start of a session. The skill tells the agent to stop its message after the question and wait, with no hints.

So the earlier finding "no tool asks for a prediction" is wrong for prediction as an exercise. The gap is narrower than the report says.

## How it differs from the product under design

| | Learning Opportunities | The product under design |
|---|---|---|
| When | After the work, and after a commit | Before the change happens |
| What is predicted | Behaviour of code already written ("what happens when X") | The effect of a change on the system |
| Level | Often code: "Open [file] and find [component]", "what does this line do" | Parts of the system, no lines |
| Who checks the answer | The agent, in the chat, from its own reading | A computed fact, with no model |
| Picture | None. All text in the chat | A drawn diagram of prediction and outcome |
| Record | None across sessions. A counter in a temp file per session | A record over months |
| Length | 10 to 15 minutes per exercise | One short act |
| Limit | 2 exercises per session | To be set. Evidence points to 0 to 2 a week |
| Where | Inside the agent's chat | Outside the chat, on a local page |

## What it shares

- The same learning science: generation, prediction, retrieval, spacing, metacognition.
- Optional, never blocks, always asks first.
- Agents: Claude Code and Codex.
- It is by a researcher with published work on developer learning, and it includes a measurement playbook (MEASURE-THIS.md) with survey items. It measures by survey, not by scored predictions.

## Consequences

1. "Prediction" alone does not set the product apart. Timing (before), the computed check, the picture and the record over time do.
2. Its design accepts the risk the report names: an answer judged by a model in the chat can be wrong, and the person can ask the model to answer for them.
3. It is the same shape as this repository's own earlier skill, learning-while-building.
4. Its author is a likely reviewer or collaborator for any measurement this product publishes.
