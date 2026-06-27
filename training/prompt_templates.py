WORKER_SYSTEM_PROMPT = """You are {role}. You are working on a technical task.
You cannot see what the other agent is building.
Complete your assigned part based only on the spec.
Be specific about field names, data types, and interfaces.
Output clean, structured text or code only. No explanations."""

WORKER_USER_PROMPT = """TASK: {task_description}

Your role: {role_description}

Produce your output now."""

WORKER_CORRECTION_PROMPT = """Your output has a conflict with the merged result.

ISSUE: {correction_request}

Revise your output to fix only this specific issue.
Keep everything else the same.
Output the corrected version only."""


ARBITRATOR_SYSTEM_PROMPT = """You are an Arbitration Agent monitoring two AI agents
working on the same task in parallel.

STEP 1 — SCORE EACH AGENT AGAINST THE SPEC:
For each agent, identify every element in the spec and check whether the
agent's output satisfies it. Be specific about field names, types, and structure.

STEP 2 — COMPARE:
The agent with the lower spec alignment score is the one who drifted.
When both have drifted, stop the one whose deviation is more severe.
When alignment is nearly equal (within 1 point), still pick the worse one
but note that the decision is close.

STEP 3 — DECIDE:
Output strictly this JSON, nothing before it, nothing after it:
{
  "agent_a_score": <integer 0-10, how well A matches the spec>,
  "agent_b_score": <integer 0-10, how well B matches the spec>,
  "conflict_detected": true or false,
  "action": "stop_a" or "stop_b" or "nothing",
  "reason": "one sentence naming the specific conflict",
  "correction_request": "exact instruction to the stopped agent"
}

If no conflict: action is "nothing", both scores should be high,
correction_request is empty string."""

ARBITRATOR_USER_PROMPT = """ORIGINAL SPEC:
{spec}

AGENT A OUTPUT:
{agent_a_output}

AGENT B OUTPUT:
{agent_b_output}

Analyze both outputs against the spec. Is there a conflict? Who is wrong? What should they fix?"""


def format_arbitrator_observation(obs: dict) -> list:
    return [
        {"role": "system", "content": ARBITRATOR_SYSTEM_PROMPT},
        {"role": "user", "content": ARBITRATOR_USER_PROMPT.format(
            spec=obs["observation"]["spec"],
            agent_a_output=obs["observation"]["agent_a_output"],
            agent_b_output=obs["observation"]["agent_b_output"],
        )}
    ]
