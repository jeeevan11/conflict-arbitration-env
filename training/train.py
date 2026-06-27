"""
End-to-end training driver for the Conflict Arbitration Agent.

Usage (from project root):
    python -m training.train

Requires CUDA GPU. Set ENV_URL to point at a running env server.
Defaults to http://localhost:8000 — start the server in another terminal:
    uvicorn server.app:app --host 127.0.0.1 --port 8000
"""
# Unsloth must be imported before trl/transformers for its patches to take effect.
# On non-CUDA hosts (e.g. macOS dev) this raises; ignore so the script still imports.
try:
    import unsloth  # noqa: F401
except Exception:
    pass

import os
import sys
import time
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=2000)
    parser.add_argument("--rollouts-per-step", type=int, default=8)
    parser.add_argument("--env-url", default=os.environ.get("ENV_URL", "http://localhost:8000"))
    parser.add_argument("--checkpoint-every", type=int, default=200)
    parser.add_argument("--eval-every", type=int, default=100)
    parser.add_argument("--output-dir", default="./checkpoints")
    parser.add_argument("--frozen-dir", default="./frozen_baseline")
    parser.add_argument("--curves-path", default="./training_curves.png")
    parser.add_argument("--metrics-json", default="./metrics.json")
    parser.add_argument("--model-name", default=None,
                        help="Override the default Qwen/Qwen2.5-1.5B-Instruct.")
    parser.add_argument("--resume-from", default=None,
                        help="Path to a checkpoint to resume training from.")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (also used as run tag in the HF model repo path).")
    parser.add_argument("--upload-repo", default=os.environ.get("UPLOAD_REPO"),
                        help="HF model repo (e.g. testingaccc/conflict-arbitrator-model) to upload outputs to.")
    args = parser.parse_args()

    import random as _random
    _random.seed(args.seed)
    try:
        import torch
        torch.manual_seed(args.seed)
    except ImportError:
        pass

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    from training.grpo_trainer import load_model, MODEL_NAME
    from training.rollout import collect_rollout
    from training.curriculum import CurriculumManager
    from training.metrics import TrainingMetrics
    from eval.frozen_baseline import save_frozen_checkpoint
    from server.client import EnvClient

    env_client = EnvClient(args.env_url)
    print(f"[env] checking {args.env_url} ...")
    print(f"[env] {env_client.health()}")

    model_name = args.model_name or MODEL_NAME
    print(f"[model] loading {model_name}")
    model, tokenizer = load_model(model_name)

    if args.resume_from:
        print(f"[resume] loading weights from {args.resume_from}")
        model.load_adapter(args.resume_from)
    else:
        print(f"[baseline] saving frozen checkpoint to {args.frozen_dir}")
        save_frozen_checkpoint(model, tokenizer, args.frozen_dir)

    curriculum = CurriculumManager()
    metrics = TrainingMetrics()

    print(f"[train] starting {args.steps} steps × {args.rollouts_per_step} rollouts")
    t0 = time.time()
    for step in range(args.steps):
        step_start = time.time()
        trajectories = collect_rollout(
            arbitrator_model=model,
            tokenizer=tokenizer,
            env_client=env_client,
            num_episodes=args.rollouts_per_step,
        )

        for t in trajectories:
            curriculum.record_episode(t["info"].get("agent_c_was_correct", False))

        metrics.log(step, trajectories, curriculum.current_phase)
        elapsed = time.time() - step_start

        if step % 10 == 0 or step < 5:
            avg_r = metrics.history["avg_reward"][-1]
            acc = metrics.history["arbitration_accuracy"][-1]
            print(f"[step {step:4d}] phase={curriculum.current_phase} "
                  f"reward={avg_r:+.2f} acc={acc:.2%} "
                  f"step_time={elapsed:.1f}s elapsed={(time.time()-t0)/60:.1f}min")

        if step % args.eval_every == 0 and step > 0:
            metrics.plot(args.curves_path)
            with open(args.metrics_json, "w") as f:
                json.dump(metrics.history, f, indent=2)
            # Incremental upload of curves + metrics so they survive cancellation
            if args.upload_repo:
                try:
                    from huggingface_hub import HfApi, create_repo
                    api = HfApi()
                    create_repo(args.upload_repo, repo_type="model", exist_ok=True)
                    prefix = f"seed-{args.seed}/"
                    for path in [args.curves_path, args.metrics_json]:
                        if Path(path).exists():
                            api.upload_file(path_or_fileobj=path, path_in_repo=prefix + Path(path).name,
                                            repo_id=args.upload_repo, repo_type="model")
                    print(f"[upload-incremental] curves+metrics pushed at step {step}")
                except Exception as e:
                    print(f"[upload-incremental] failed: {e}")

        if step % args.checkpoint_every == 0 and step > 0:
            ckpt = Path(args.output_dir) / f"step_{step}"
            print(f"[checkpoint] saving to {ckpt}")
            model.save_pretrained(str(ckpt))
            tokenizer.save_pretrained(str(ckpt))
            # Incremental upload of LoRA adapter so it survives cancellation
            if args.upload_repo:
                try:
                    from huggingface_hub import HfApi, create_repo
                    api = HfApi()
                    create_repo(args.upload_repo, repo_type="model", exist_ok=True)
                    api.upload_folder(folder_path=str(ckpt),
                                      path_in_repo=f"seed-{args.seed}/checkpoints/step_{step}",
                                      repo_id=args.upload_repo, repo_type="model")
                    print(f"[upload-incremental] checkpoint step_{step} pushed")
                except Exception as e:
                    print(f"[upload-incremental] checkpoint upload failed: {e}")

    print(f"[done] total time: {(time.time()-t0)/60:.1f}min")
    final = Path(args.output_dir) / "final"
    print(f"[save] final adapter -> {final}")
    model.save_pretrained(str(final))
    tokenizer.save_pretrained(str(final))

    merged = "conflict-arbitrator-trained"
    print(f"[save] merged 16-bit -> {merged}")
    try:
        model.save_pretrained_merged(merged, tokenizer, save_method="merged_16bit")
    except Exception as e:
        print(f"[save] merged save failed (continuing): {e}")

    metrics.plot(args.curves_path)
    with open(args.metrics_json, "w") as f:
        json.dump(metrics.history, f, indent=2)

    if args.upload_repo:
        print(f"[upload] pushing artifacts to {args.upload_repo} (seed={args.seed})")
        try:
            from huggingface_hub import HfApi, create_repo
            api = HfApi()
            try:
                create_repo(args.upload_repo, repo_type="model", exist_ok=True)
            except Exception as e:
                print(f"[upload] create_repo: {e}")
            prefix = f"seed-{args.seed}/"
            for path in [final, args.frozen_dir, args.curves_path, args.metrics_json, merged]:
                p = Path(path)
                if not p.exists():
                    continue
                if p.is_dir():
                    api.upload_folder(folder_path=str(p), path_in_repo=prefix + p.name,
                                      repo_id=args.upload_repo, repo_type="model")
                else:
                    api.upload_file(path_or_fileobj=str(p), path_in_repo=prefix + p.name,
                                    repo_id=args.upload_repo, repo_type="model")
                print(f"[upload]   uploaded {p}")
        except Exception as e:
            print(f"[upload] failed: {e}")


if __name__ == "__main__":
    main()
