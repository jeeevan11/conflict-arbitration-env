from training.prompt_templates import format_arbitrator_observation
from training.rollout import generate_decision


def save_frozen_checkpoint(model, tokenizer, path: str = "./frozen_baseline"):
    """
    Call this at step 0 before any training.
    This is your primary proof of learning.
    Non-negotiable.
    """
    model.save_pretrained(path)
    tokenizer.save_pretrained(path)
    print(f"Frozen baseline saved to {path}")


def load_frozen(path: str):
    try:
        from unsloth import FastLanguageModel
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=path,
            max_seq_length=4096,
            load_in_4bit=True,
            fast_inference=True,
        )
        return model
    except ImportError:
        from transformers import AutoModelForCausalLM
        return AutoModelForCausalLM.from_pretrained(path)


def evaluate_vs_frozen(
    trained_model,
    frozen_checkpoint_path: str,
    env_client,
    tokenizer,
    num_episodes: int = 100
) -> dict:
    """
    Runs trained Agent C against frozen Agent C baseline.
    Both face the same episodes.
    Returns comparative metrics.
    """
    frozen_model = load_frozen(frozen_checkpoint_path)

    trained_results = []
    frozen_results = []

    for _ in range(num_episodes):
        obs = env_client.reset()

        messages = format_arbitrator_observation(obs)
        prompt = tokenizer.apply_chat_template(messages, tokenize=False)
        _, trained_decision = generate_decision(trained_model, tokenizer, prompt)
        trained_result = env_client.step(trained_decision or {"action": "nothing"})
        trained_results.append(trained_result)

        obs_reset = env_client.reset()
        _, frozen_decision = generate_decision(frozen_model, tokenizer, prompt)
        frozen_result = env_client.step(frozen_decision or {"action": "nothing"})
        frozen_results.append(frozen_result)

    return {
        "trained_accuracy": sum(r["info"]["agent_c_was_correct"] for r in trained_results) / num_episodes,
        "frozen_accuracy": sum(r["info"]["agent_c_was_correct"] for r in frozen_results) / num_episodes,
        "trained_merge_rate": sum(r["info"]["spec_satisfied"] for r in trained_results) / num_episodes,
        "frozen_merge_rate": sum(r["info"]["spec_satisfied"] for r in frozen_results) / num_episodes,
    }
