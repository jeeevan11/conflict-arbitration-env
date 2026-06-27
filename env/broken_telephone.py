import random

from env.reward import compute_reward
from env.merger import score_agent_alignment


class BrokenTelephoneGame:
    def __init__(self, spec_generator, conflict_injector, merger, curriculum, worker_agent=None):
        self.spec_generator = spec_generator
        self.conflict_injector = conflict_injector
        self.merger = merger
        self.curriculum = curriculum
        self.worker_agent = worker_agent
        self.current_episode = None

        if self.worker_agent is None:
            from agents.worker_agent import WorkerAgent
            self.worker_agent = WorkerAgent()

    def reset(self) -> dict:
        """
        Starts a new episode.
        Returns observation for Agent C.
        """
        spec = self.spec_generator.generate_spec(
            domain=self.curriculum.get_domain()
        )

        output_a = self.worker_agent.generate(spec, role="agent_a")
        output_b = self.worker_agent.generate(spec, role="agent_b")

        conflict_metadata = None
        if self.curriculum.should_inject_conflict():
            output_a, output_b, conflict_metadata = self.conflict_injector.inject(
                spec=spec,
                output_a=output_a,
                output_b=output_b,
                conflict_type=self.curriculum.get_conflict_type(),
                wrong_agent=random.randint(0, 1),
                obviousness=self.curriculum.get_obviousness()
            )

        self.current_episode = {
            "spec": spec,
            "output_a": output_a,
            "output_b": output_b,
            "conflict_metadata": conflict_metadata,
            "conflict_existed": conflict_metadata is not None,
            "wrong_agent": conflict_metadata["wrong_agent"] if conflict_metadata else None,
            "alignment_a": score_agent_alignment(output_a, spec),
            "alignment_b": score_agent_alignment(output_b, spec),
        }

        return {
            "spec": spec["task_description"],
            "agent_a_output": output_a,
            "agent_b_output": output_b,
        }

    def step(self, action: dict) -> dict:
        """
        Applies Agent C's decision.
        action = {
            "conflict_detected": bool,
            "action": "stop_a" | "stop_b" | "nothing",
            "reason": str,
            "correction_request": str
        }
        Returns reward + info.
        """
        agent_c_action = action.get("action", "nothing")
        correction_result = {"success": False}

        output_a = self.current_episode["output_a"]
        output_b = self.current_episode["output_b"]

        if agent_c_action == "stop_a":
            output_a = self.worker_agent.correct(
                output_a,
                action.get("correction_request", "")
            )
            correction_result = {"corrected_agent": 0, "new_output": output_a}
        elif agent_c_action == "stop_b":
            output_b = self.worker_agent.correct(
                output_b,
                action.get("correction_request", "")
            )
            correction_result = {"corrected_agent": 1, "new_output": output_b}

        merge_result = self.merger.merge_outputs(
            output_a, output_b, self.current_episode["spec"]
        )

        reward = compute_reward(
            conflict_existed=self.current_episode["conflict_existed"],
            agent_c_action=agent_c_action,
            wrong_agent_ground_truth=self.current_episode["wrong_agent"],
            merge_result=merge_result,
            correction_result=correction_result,
            agent_c_output_valid=True,
            timed_out=False,
            alignment_a=self.current_episode["alignment_a"],
            alignment_b=self.current_episode["alignment_b"],
        )

        return {
            "reward": reward,
            "merge_result": merge_result,
            "correction_result": correction_result,
            "done": True,
            "info": {
                "conflict_existed": self.current_episode["conflict_existed"],
                "agent_c_was_correct": self._was_correct(agent_c_action),
                "spec_satisfied": merge_result["spec_satisfied"],
            }
        }

    def _was_correct(self, agent_c_action: str) -> bool:
        conflict = self.current_episode["conflict_existed"]
        wrong = self.current_episode["wrong_agent"]
        if not conflict:
            return agent_c_action == "nothing"
        if agent_c_action == "nothing":
            return False
        stopped = 0 if agent_c_action == "stop_a" else 1
        return stopped == wrong
