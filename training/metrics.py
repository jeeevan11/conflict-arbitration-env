try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


class TrainingMetrics:
    def __init__(self):
        self.history = {
            "step": [],
            "arbitration_accuracy": [],
            "conflict_detection_rate": [],
            "false_alarm_rate": [],
            "merge_success_rate": [],
            "wrong_agent_rate": [],
            "avg_reward": [],
            "curriculum_phase": [],
        }

    def log(self, step: int, trajectories: list, curriculum_phase: int):
        correct = sum(1 for t in trajectories if t["info"].get("agent_c_was_correct"))
        merged = sum(1 for t in trajectories if t["info"].get("spec_satisfied"))
        rewards = [t["reward"] for t in trajectories]

        self.history["step"].append(step)
        self.history["arbitration_accuracy"].append(correct / len(trajectories))
        self.history["merge_success_rate"].append(merged / len(trajectories))
        self.history["avg_reward"].append(sum(rewards) / len(rewards))
        self.history["curriculum_phase"].append(curriculum_phase)

    def plot(self, save_path: str = "./training_curves.png"):
        if plt is None:
            print("matplotlib not installed; skipping plot")
            return
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle("Conflict Arbitration Agent — Training Progress")

        metrics = [
            ("arbitration_accuracy", "Arbitration Accuracy", "green"),
            ("conflict_detection_rate", "Conflict Detection Rate", "blue"),
            ("false_alarm_rate", "False Alarm Rate", "red"),
            ("merge_success_rate", "Merge Success Rate", "purple"),
            ("wrong_agent_rate", "Wrong Agent Rate", "orange"),
            ("avg_reward", "Average Reward", "black"),
        ]

        for ax, (key, title, color) in zip(axes.flatten(), metrics):
            if self.history[key]:
                ax.plot(self.history["step"], self.history[key], color=color)
                ax.set_title(title)
                ax.set_xlabel("Training Step")
                ax.set_ylabel(key.replace("_", " ").title())
                ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved training curves to {save_path}")
