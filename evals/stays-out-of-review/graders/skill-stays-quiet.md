---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?explain-pr"'
min: 0
max: 0
arm: both
---

The description ends by saying not to use this for reviewing a PR for defects,
and this case checks that the sentence does any work. A description that fires on
everything PR-shaped is worse than none, because it drags a long teaching
procedure into a session that wanted a code review.

This is the harder half of discovery and the half descriptions usually get wrong.
Firing here counts as a failure, even though the skill would have produced
something that looked reasonable.

`arm: both` keeps it scored in the baseline too. The baseline passes trivially,
since a plugin that is not loaded cannot fire, so read the two arms together and
take information only from the with-plugin number.
