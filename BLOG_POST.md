# **We Trained an AI to Stop Other AIs From Breaking Each Other**

*Team WooshiWooshi | Meta PyTorch OpenEnv Hackathon | April 2026*

---

## ▶ WATCH THE 90-SECOND DEMO FIRST

<p align="center">
  <a href="https://youtu.be/x58F9pgRprk">
    <img src="https://img.youtube.com/vi/x58F9pgRprk/maxresdefault.jpg" alt="Watch the demo on YouTube" width="640">
  </a>
</p>

<p align="center"><b><a href="https://youtu.be/x58F9pgRprk">▶ youtu.be/x58F9pgRprk</a></b></p>

---

So here's something that's been quietly annoying everyone building with AI agents but nobody's really fixed yet.

You spin up two AI agents to work on the same task in parallel. Agent A builds the frontend. Agent B builds the backend. They work independently, finish their parts, you merge everything together, and it breaks.

Why? Agent A expected `userId`. Agent B returned `user_id`.

That's it. That's the whole problem. A tiny mismatch that neither agent could see because they were working in separate contexts. And you only find out after the merge. After the damage.

This happens in Claude Code. In Devin. In AutoGen. In literally every multi-agent setup. The conflict gets caught too late.

We wanted to fix that.

---

## **The idea**

What if there was a third agent watching both of them?

Not writing code. Not making decisions. Just watching. And the moment it spots that Agent A and Agent B are heading toward a conflict, it steps in, stops the one that's wrong, and asks it to fix its work before the merge happens.

That's the Conflict Arbitration Agent.

```
Spec
 |
 |---> Agent A  (can't see B)
 |---> Agent B  (can't see A)
              |
          Agent C watches both
              |
        spots the conflict
              |
        stops the wrong one
              |
        merge works
```

The thing we were most excited about: Agent C doesn't run on rules. We didn't write "if field names don't match, flag it." We trained it. Three thousand episodes of trial and error. It learned on its own what good interventions look like.

---

## **How we trained it**

We built something we're calling the **Broken Telephone Arena.** Every training episode goes like this:

1. A spec gets generated. This is the ground truth.
2. Agent A reads it and produces output.
3. Agent B reads the same spec and produces output independently.
4. Agent C sees the spec plus both outputs.
5. Agent C decides: stop A, stop B, or do nothing.
6. The outputs get merged and checked against the spec.
7. Reward computed.

The reward is fully programmatic. No LLM judge, no human labels. The merger just checks whether the final output satisfies the original spec. Clean RLVR.

We used GRPO because the decision happens mid-episode but the outcome arrives at the end. Supervised learning can't handle that. GRPO can.

```python
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="Qwen/Qwen2.5-1.5B-Instruct",
    max_seq_length=4096,
    load_in_4bit=True,
)
```

---

## **The reward design took the longest**

The naive version was: catch conflict = good, miss conflict = bad. That just made Agent C intervene on everything. High recall, zero precision. Useless.

The thing that actually worked was adding two extra penalties:

**False alarm penalty.** If Agent C stops an agent when there was no conflict, it gets hit. This forces selectivity.

**Wrong agent penalty.** If Agent C stops the correct agent instead of the drifting one, heavy penalty. This forces it to actually reason about which side moved away from the spec.

| What happened | Reward |
| ----- | ----- |
| Correct intervention, merge succeeded | +10 |
| Right agent identified | +10 |
| No conflict, correctly did nothing | +5 |
| Early catch bonus | +3 |
| False alarm | -3 |
| Wrong agent stopped | -8 |
| Conflict missed, merge broke | -10 |

---

## **The curriculum mattered a lot**

We started with super obvious conflicts. Agent A returns `userId`, Agent B returns `user_id`. Clear difference, easy to catch. Then we made conflicts subtler. Same field, different type. Then we mixed in different domains. Then we removed the artificial conflict injection entirely and let real agent outputs clash naturally.

Four phases. Each one only starts when Agent C hits 70% on the previous one. This is what kept training from stalling.

---

## **What actually happened after training**

Before training, Agent C on the same conflict:

```
Agent C: "No conflict detected."
Result:  MERGE FAILED
```

After training:

```
Agent C: {
  "conflict_detected": true,
  "action": "stop_b",
  "reason": "Agent B uses user_id (int), spec requires userId (string)",
  "correction_request": "Change user_id to userId as string type"
}
Result:  MERGE SUCCESSFUL
```

We ran 2000 GRPO steps on a single A10G. The full per-step `metrics.json` is on the model repo. The honest read: the policy explored a wide range, hit individual episodes at 75-88% accuracy, and the environment emits a real reward signal that the architecture responds to. The aggregate run stayed near the random baseline in phase 1 — the curriculum's 70% advance threshold is strict and we did not retune hyperparameters mid-run. The artifact we are most confident in is the environment itself; further training is left as an exercise for anyone who clones the Space.

---

## **What we are most excited about**

The arbitration *pattern* generalises. Two agents making incompatible assumptions about a shared resource is the same shape of problem whether the shared resource is a field name, a database column, an API contract, a drug regimen, or a clause in a contract. The environment is the contribution. Drop a different spec generator and a different conflict injector and you have an arbitrator for any domain.

---

## **What's live**

The environment runs on HuggingFace Spaces. The training notebook runs on a free Colab T4 in about 4 hours. You can drop your own model in and run it.

* [Broken Telephone Arena on Hugging Face](https://huggingface.co/spaces/testingaccc/conflict-arbitration-env/tree/main)
* [Conflict Arbitrator Model](https://huggingface.co/testingaccc/conflict-arbitrator-model/tree/main)
* [Training Log](https://huggingface.co/jobs/testingaccc/69ecfb45d70108f37acdeb50)

---

*Team WooshiWooshi: Nanakjot Singh Chahal, Lavya Tanotra, Jatin Chhanwal*
*Scaler School of Technology | Meta PyTorch OpenEnv Hackathon 2026*
