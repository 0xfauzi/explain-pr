---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?explain-pr"'
min: 1
---

The prompt asks for the two things the description promises: understanding rather
than defects, and where the change sits in the system. If the skill does not fire
on that, the description is not doing its job, and no amount of care inside
`SKILL.md` ever reaches a user.

Under `--ablation with-without` this grader is reported rather than scored, since
the baseline arm has no skill available to fire.
