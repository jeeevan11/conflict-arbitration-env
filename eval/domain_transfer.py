from training.prompt_templates import format_arbitrator_observation
from training.rollout import generate_decision


def evaluate_domain_transfer(
    trained_model,
    env_client,
    tokenizer,
    unseen_domain: str,
    num_episodes: int = 50
) -> dict:
    """
    Tests Agent C on a domain it was never trained on.
    If accuracy stays high: it learned the abstract pattern.
    If accuracy drops: it memorized the training domain.

    This is your wow demonstration on stage.
    Run this live. Show it works on a domain it never saw.
    """
    results = []
    for _ in range(num_episodes):
        obs = env_client.reset()
        messages = format_arbitrator_observation(obs)
        prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        _, decision = generate_decision(trained_model, tokenizer, prompt)
        if decision is None:
            decision = {
                "conflict_detected": False,
                "action": "nothing",
                "reason": "parse error",
                "correction_request": "",
            }
        result = env_client.step(decision)
        results.append(result)

    correct = sum(r["info"].get("agent_c_was_correct", False) for r in results)
    satisfied = sum(r["info"].get("spec_satisfied", False) for r in results)

    return {
        "domain": unseen_domain,
        "accuracy": correct / num_episodes if num_episodes else 0.0,
        "merge_rate": satisfied / num_episodes if num_episodes else 0.0,
        "episodes": num_episodes,
    }
