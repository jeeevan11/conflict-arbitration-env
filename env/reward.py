REWARDS = {
    "merge_succeeded_after_correction": +10,
    "merge_succeeded_no_intervention_needed": +5,

    "correct_agent_identified": +10,
    "wrong_agent_stopped": -8,
    "conflict_missed": -10,
    "false_alarm_no_conflict": -3,

    "correction_accepted_merge_works": +5,
    "correction_failed_merge_still_broken": -5,

    "early_detection_bonus": +3,
    "invalid_json_output": -5,
    "timeout": -3,
}


def compute_reward(
    conflict_existed: bool,
    agent_c_action: str,
    wrong_agent_ground_truth: int,
    merge_result: dict,
    correction_result: dict,
    agent_c_output_valid: bool,
    timed_out: bool,
    alignment_a: dict = None,
    alignment_b: dict = None,
) -> float:
    """
    Computes total reward for one episode.
    All logic is here. Do not compute reward anywhere else.
    """
    if timed_out:
        return REWARDS["timeout"]

    if not agent_c_output_valid:
        return REWARDS["invalid_json_output"]

    if not conflict_existed:
        if agent_c_action == "nothing":
            return REWARDS["merge_succeeded_no_intervention_needed"]
        else:
            return REWARDS["false_alarm_no_conflict"]

    if agent_c_action == "nothing":
        return REWARDS["conflict_missed"]

    stopped_agent = 0 if agent_c_action == "stop_a" else 1

    contrast = 0.0
    if alignment_a and alignment_b:
        contrast = abs(
            alignment_a["alignment_score"] - alignment_b["alignment_score"]
        )

    if stopped_agent != wrong_agent_ground_truth:
        penalty = REWARDS["wrong_agent_stopped"] * (1 + contrast)
        return round(penalty, 2)

    base = REWARDS["correct_agent_identified"]

    difficulty_bonus = round((1 - contrast) * 5, 2)
    base += difficulty_bonus

    if merge_result["spec_satisfied"]:
        base += REWARDS["merge_succeeded_after_correction"]
        base += REWARDS["correction_accepted_merge_works"]
    else:
        base += REWARDS["correction_failed_merge_still_broken"]

    return round(base, 2)
