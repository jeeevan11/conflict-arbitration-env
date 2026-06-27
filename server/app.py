from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from env.openenv_wrapper import ConflictArbitrationEnv
from pydantic import BaseModel

app = FastAPI(title="Conflict Arbitration Environment")
env = ConflictArbitrationEnv()


HOMEPAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Conflict Arbitration Environment</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 48px 24px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    background: radial-gradient(ellipse at top, #1a1a2e 0%, #0a0a14 100%);
    color: #e6e6f0; line-height: 1.6; min-height: 100vh;
  }
  .wrap { max-width: 880px; margin: 0 auto; }
  h1 { font-size: 2.4rem; margin: 0 0 8px; letter-spacing: -0.02em; }
  .sub { color: #8888a8; font-size: 1.05rem; margin-bottom: 32px; }
  .badge { display: inline-block; padding: 4px 10px; background: #2a2a4a;
           border-radius: 6px; font-size: 0.78rem; color: #b0b0d0;
           margin-right: 6px; }
  .card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
          border-radius: 12px; padding: 24px; margin: 16px 0; }
  h2 { font-size: 1.1rem; margin: 0 0 12px; color: #c8c8e8; }
  table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
  td { padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.06); vertical-align: top; }
  td:first-child { width: 130px; font-family: ui-monospace, monospace; color: #a0e0c0; }
  td:nth-child(2) { font-family: ui-monospace, monospace; color: #d0d0f0; }
  td:last-child { color: #8888a8; }
  pre { background: #0a0a18; border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px; padding: 14px; overflow-x: auto; font-size: 0.85rem;
        color: #c0c0e0; margin: 8px 0 0; }
  a { color: #8be9d6; }
  .pill { display: inline-block; padding: 3px 10px; background: #1a4d3a;
          color: #6fdd9e; border-radius: 20px; font-size: 0.8rem;
          font-weight: 600; }
  footer { margin-top: 48px; text-align: center; color: #555575; font-size: 0.85rem; }
</style>
</head>
<body>
<div class="wrap">
  <span class="pill">● running</span>
  <h1>Conflict Arbitration Environment</h1>
  <div class="sub">
    <span class="badge">OpenEnv</span>
    <span class="badge">FastAPI</span>
    <span class="badge">GRPO</span>
    <span class="badge">Team WooshiWooshi</span>
  </div>

  <div class="card">
    <h2>What this is</h2>
    Three agents, one task, one conflict, one arbitrator.
    Two frozen worker agents build the same spec in parallel.
    A third agent (Agent C) sees both outputs plus the original spec,
    decides who drifted, and stops the wrong one before merge fails.
    Agent C is trained via GRPO on programmatic, contrastive rewards —
    no LLM as judge, no hardcoded rules.
  </div>

  <div class="card">
    <h2>Endpoints</h2>
    <table>
      <tr><td>GET&nbsp;/health</td><td>liveness check</td><td>returns status + env name</td></tr>
      <tr><td>POST&nbsp;/reset</td><td>start a new episode</td><td>returns spec + Agent A/B outputs</td></tr>
      <tr><td>POST&nbsp;/step</td><td>submit Agent C decision</td><td>returns reward + merge result</td></tr>
      <tr><td>GET&nbsp;/state</td><td>full episode ground truth</td><td>logging/debug only</td></tr>
      <tr><td>GET&nbsp;/docs</td><td>interactive OpenAPI UI</td><td>try every endpoint live</td></tr>
    </table>
  </div>

  <div class="card">
    <h2>Quick test</h2>
<pre>curl https://testingaccc-conflict-arbitration-env.hf.space/health

curl -X POST https://testingaccc-conflict-arbitration-env.hf.space/reset

curl -X POST https://testingaccc-conflict-arbitration-env.hf.space/step \\
  -H "Content-Type: application/json" \\
  -d '{"conflict_detected": true, "action": "stop_a",
       "reason": "A drifted", "correction_request": "use canonical name"}'</pre>
  </div>

  <div class="card">
    <h2>Action schema</h2>
<pre>{
  "conflict_detected": true | false,
  "action": "stop_a" | "stop_b" | "nothing",
  "reason": "one sentence describing the conflict",
  "correction_request": "specific instruction to the stopped agent"
}</pre>
  </div>

  <footer>
    Meta PyTorch OpenEnv Hackathon · April 2026 ·
    <a href="/docs">/docs</a> ·
    <a href="/health">/health</a>
  </footer>
</div>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def homepage():
    return HOMEPAGE


class Action(BaseModel):
    conflict_detected: bool
    action: str
    reason: str
    correction_request: str = ""


@app.post("/reset")
def reset():
    return env.reset()


@app.post("/step")
def step(action: Action):
    return env.step(action.dict())


@app.get("/state")
def state():
    return env.state()


@app.get("/health")
def health():
    return {"status": "ok", "env": "ConflictArbitrationEnv"}
