import os
import json

try:
    import gradio as gr
except ImportError:
    gr = None

from env.openenv_wrapper import ConflictArbitrationEnv


_env = ConflictArbitrationEnv()


def load_before_transcript() -> str:
    path = "./transcripts/before.json"
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return "No before transcript available yet."


def load_after_transcript() -> str:
    path = "./transcripts/after.json"
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return "No after transcript available yet."


def run_live_episode(spec_text: str):
    obs = _env.reset()
    agent_a = obs["observation"]["agent_a_output"]
    agent_b = obs["observation"]["agent_b_output"]
    decision = {
        "conflict_detected": False,
        "action": "nothing",
        "reason": "no model loaded",
        "correction_request": "",
    }
    result = _env.step(decision)
    return agent_a, agent_b, decision, result


def run_transfer_test(domain: str):
    obs = _env.reset()
    return {
        "domain": domain,
        "observation": obs,
        "note": "Domain transfer test stub. Requires a trained model.",
    }


def build_demo():
    if gr is None:
        raise ImportError("gradio is required to build the demo UI.")

    with gr.Blocks(title="Conflict Arbitration Agent") as demo:
        gr.Markdown("# Conflict Arbitration Agent")
        gr.Markdown(
            "Two AI agents build the same thing in parallel. "
            "A third agent monitors both and stops conflicts before they happen."
        )

        with gr.Tab("Live Arbitration"):
            gr.Markdown("### Watch Agent C make a decision in real time")
            spec_input = gr.Textbox(
                label="Task Spec",
                value="Build a user authentication endpoint",
                lines=2
            )
            run_btn = gr.Button("Run Episode", variant="primary")

            with gr.Row():
                agent_a_out = gr.Textbox(label="Agent A Output", lines=8)
                agent_b_out = gr.Textbox(label="Agent B Output", lines=8)

            arbitrator_out = gr.JSON(label="Agent C Decision")
            merge_out = gr.JSON(label="Merge Result + Reward")

            run_btn.click(
                fn=run_live_episode,
                inputs=[spec_input],
                outputs=[agent_a_out, agent_b_out, arbitrator_out, merge_out]
            )

        with gr.Tab("Before vs After"):
            gr.Markdown("### Same episode. Untrained vs trained Agent C.")
            with gr.Row():
                gr.Textbox(label="Untrained Agent C (Step 0)", lines=20, value=load_before_transcript())
                gr.Textbox(label="Trained Agent C (Final)", lines=20, value=load_after_transcript())

        with gr.Tab("Training Curves"):
            gr.Markdown("### Evidence of learning across 2000 training steps")
            gr.Image(value="./training_curves.png", label="Training Progress")

        with gr.Tab("Domain Transfer"):
            gr.Markdown("### Trained on coding. Watch it catch a conflict in a domain it never saw.")
            domain_select = gr.Dropdown(
                choices=["legal", "medical", "financial"],
                label="Select Unseen Domain",
                value="legal"
            )
            transfer_btn = gr.Button("Run Transfer Test")
            transfer_result = gr.JSON(label="Transfer Result")
            transfer_btn.click(fn=run_transfer_test, inputs=[domain_select], outputs=[transfer_result])

    return demo


if __name__ == "__main__":
    demo = build_demo()
    demo.launch()
