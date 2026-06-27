import json
import time

try:
    import torch
except ImportError:
    torch = None

from training.prompt_templates import format_arbitrator_observation


def generate_decision(model, tokenizer, prompt: str, timeout: int = 30):
    """
    Generates Agent C's decision from the model.
    Returns (raw_text, parsed_json or None).
    """
    start = time.time()

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

    if time.time() - start > timeout:
        return "", None

    raw = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

    try:
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        parsed = json.loads(clean.strip())
        return raw, parsed
    except Exception:
        return raw, None


def collect_rollout(
    arbitrator_model,
    tokenizer,
    env_client,
    num_episodes: int = 8
) -> list:
    """
    Collects NUM_EPISODES of arbitration experience.
    Returns list of (prompt, response, reward) for GRPO.
    """
    trajectories = []

    for _ in range(num_episodes):
        obs = env_client.reset()

        messages = format_arbitrator_observation(obs)
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        decision_text, decision_json = generate_decision(
            arbitrator_model, tokenizer, prompt
        )

        timed_out = decision_json is None and decision_text == ""
        if decision_json is None:
            decision_json = {}

        # Normalize: server requires conflict_detected (bool), action (str), reason (str), correction_request (str)
        action_str = str(decision_json.get("action", "nothing")).lower().strip()
        if action_str not in ("stop_a", "stop_b", "nothing"):
            action_str = "nothing"
        clean_action = {
            "conflict_detected": bool(decision_json.get("conflict_detected", action_str != "nothing")),
            "action": action_str,
            "reason": str(decision_json.get("reason", "no reason given"))[:500],
            "correction_request": str(decision_json.get("correction_request", ""))[:1000],
        }

        try:
            result = env_client.step(clean_action)
        except Exception as e:
            print(f"[rollout] step failed: {e}; using safe fallback")
            clean_action = {"conflict_detected": False, "action": "nothing",
                            "reason": "client error", "correction_request": ""}
            result = env_client.step(clean_action)
        # Preserve scores from raw decision for trajectory logging
        decision_json = {**clean_action,
                         "agent_a_score": decision_json.get("agent_a_score"),
                         "agent_b_score": decision_json.get("agent_b_score")}
        reward = result["reward"]

        trajectories.append({
            "prompt": prompt,
            "response": decision_text,
            "reward": reward,
            "info": {
                **result.get("info", {}),
                "agent_c_score_a": decision_json.get("agent_a_score"),
                "agent_c_score_b": decision_json.get("agent_b_score"),
                "score_gap": abs(
                    (decision_json.get("agent_a_score") or 0) -
                    (decision_json.get("agent_b_score") or 0)
                ),
            }
        })

    return trajectories
