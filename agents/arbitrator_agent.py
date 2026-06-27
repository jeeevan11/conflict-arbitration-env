"""
Arbitrator agent (Agent C). The agent being trained via GRPO.
"""
import json


class ArbitratorAgent:
    def __init__(self, model=None, tokenizer=None):
        self.model = model
        self.tokenizer = tokenizer

    def decide(self, observation: dict) -> dict:
        from training.prompt_templates import format_arbitrator_observation
        from training.rollout import generate_decision

        if self.model is None or self.tokenizer is None:
            return {
                "conflict_detected": False,
                "action": "nothing",
                "reason": "no model loaded",
                "correction_request": "",
            }

        messages = format_arbitrator_observation({"observation": observation})
        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        _, decision = generate_decision(self.model, self.tokenizer, prompt)
        if decision is None:
            return {
                "conflict_detected": False,
                "action": "nothing",
                "reason": "parse error",
                "correction_request": "",
            }
        return decision
