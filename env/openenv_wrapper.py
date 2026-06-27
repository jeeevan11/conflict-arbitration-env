import uuid

try:
    from openenv import Environment
except ImportError:
    class Environment:
        pass

from env.spec_generator import generate_spec
from env import spec_generator, conflict_injector, merger
from env.broken_telephone import BrokenTelephoneGame
from training.curriculum import CurriculumManager


class _CurriculumAdapter:
    def __init__(self):
        self.manager = CurriculumManager()

    def get_domain(self):
        from training.curriculum import CURRICULUM
        domains = CURRICULUM[self.manager.current_phase]["domains"]
        if "all" in domains:
            return None
        import random
        return random.choice(domains)

    def should_inject_conflict(self):
        from training.curriculum import CURRICULUM
        phase = CURRICULUM[self.manager.current_phase]
        if not phase["inject_conflicts"]:
            return False
        import random
        return random.random() < phase["conflict_rate"]

    def get_conflict_type(self):
        return conflict_injector.get_random_conflict_type(self.manager.current_phase)

    def get_obviousness(self):
        from training.curriculum import CURRICULUM
        return CURRICULUM[self.manager.current_phase].get("obviousness") or "medium"

    def record_episode(self, was_correct: bool):
        self.manager.record_episode(was_correct)


class ConflictArbitrationEnv(Environment):
    """
    OpenEnv-compatible wrapper.
    Follows standard reset/step/state interface.
    Client and server are separated. Client never imports server internals.
    """

    def __init__(self):
        self.curriculum = _CurriculumAdapter()
        self.game = BrokenTelephoneGame(
            spec_generator=spec_generator,
            conflict_injector=conflict_injector,
            merger=merger,
            curriculum=self.curriculum,
        )

    def reset(self) -> dict:
        obs = self.game.reset()
        return {
            "observation": obs,
            "current_agent": "arbitrator",
            "episode_id": str(uuid.uuid4())
        }

    def step(self, action: dict) -> dict:
        result = self.game.step(action)
        self.curriculum.record_episode(result["info"].get("agent_c_was_correct", False))
        return {
            "reward": result["reward"],
            "done": result["done"],
            "info": result["info"],
            "merge_result": result["merge_result"],
        }

    def state(self) -> dict:
        return self.game.current_episode
