"""
Worker agent (Agent A and Agent B). Frozen, same model.
Uses templated outputs by default for deterministic environment behavior.
Can be swapped for an LLM-backed implementation.
"""
import json


class WorkerAgent:
    def __init__(self, model=None, tokenizer=None):
        self.model = model
        self.tokenizer = tokenizer

    def generate(self, spec: dict, role: str = "agent_a") -> str:
        if self.model is not None and self.tokenizer is not None:
            return self._generate_llm(spec, role)
        return self._generate_template(spec, role)

    def correct(self, output: str, correction_request: str) -> str:
        if self.model is not None and self.tokenizer is not None:
            return self._correct_llm(output, correction_request)
        return self._correct_template(output, correction_request)

    def _generate_template(self, spec: dict, role: str) -> str:
        ground_truth = spec.get("ground_truth", {})
        return json.dumps(ground_truth, indent=2)

    def _correct_template(self, output: str, correction_request: str) -> str:
        return output + f"\n# corrected: {correction_request}"

    def _generate_llm(self, spec: dict, role: str) -> str:
        from training.prompt_templates import (
            WORKER_SYSTEM_PROMPT,
            WORKER_USER_PROMPT,
        )
        messages = [
            {"role": "system", "content": WORKER_SYSTEM_PROMPT.format(role=role)},
            {"role": "user", "content": WORKER_USER_PROMPT.format(
                task_description=spec["task_description"],
                role_description=role,
            )},
        ]
        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        import torch
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        return self.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True,
        )

    def _correct_llm(self, output: str, correction_request: str) -> str:
        from training.prompt_templates import WORKER_CORRECTION_PROMPT
        messages = [
            {"role": "user", "content": WORKER_CORRECTION_PROMPT.format(
                correction_request=correction_request
            ) + "\n\nORIGINAL OUTPUT:\n" + output},
        ]
        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        import torch
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        return self.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True,
        )
