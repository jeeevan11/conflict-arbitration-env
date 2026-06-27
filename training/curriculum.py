CURRICULUM = {
    1: {
        "name": "Obvious conflicts, API domain",
        "inject_conflicts": True,
        "conflict_rate": 0.8,
        "obviousness": "high",
        "domains": ["api"],
        "conflict_types": ["naming"],
        "advance_threshold": 0.70,
        "min_steps": 200,
    },
    2: {
        "name": "Subtle conflicts, two domains",
        "inject_conflicts": True,
        "conflict_rate": 0.7,
        "obviousness": "medium",
        "domains": ["api", "database"],
        "conflict_types": ["naming", "format", "spelling"],
        "advance_threshold": 0.70,
        "min_steps": 300,
    },
    3: {
        "name": "Mixed conflicts, all domains",
        "inject_conflicts": True,
        "conflict_rate": 0.6,
        "obviousness": "low",
        "domains": ["api", "database", "config", "data_format",
                    "graphql", "event", "cli", "error_response"],
        "conflict_types": ["naming", "format", "assumption", "missing_field",
                           "spelling", "casing", "logic", "value_drift"],
        "advance_threshold": 0.65,
        "min_steps": 400,
    },
    4: {
        "name": "Natural conflicts, full generalization",
        "inject_conflicts": False,
        "conflict_rate": None,
        "obviousness": None,
        "domains": ["all"],
        "conflict_types": ["all"],
        "advance_threshold": None,
        "min_steps": 1000,
    },
}


class CurriculumManager:
    def __init__(self):
        self.current_phase = 1
        self.steps_in_phase = 0
        self.accuracy_window = []

    def record_episode(self, was_correct: bool):
        self.accuracy_window.append(int(was_correct))
        if len(self.accuracy_window) > 100:
            self.accuracy_window.pop(0)
        self.steps_in_phase += 1
        self._check_advance()

    def _check_advance(self):
        phase = CURRICULUM[self.current_phase]
        if len(self.accuracy_window) < 100:
            return
        if self.steps_in_phase < phase["min_steps"]:
            return
        if phase["advance_threshold"] is None:
            return
        accuracy = sum(self.accuracy_window) / len(self.accuracy_window)
        if accuracy >= phase["advance_threshold"]:
            if self.current_phase < 4:
                self.current_phase += 1
                self.steps_in_phase = 0
                self.accuracy_window = []
                print(f"Advanced to Phase {self.current_phase}")
