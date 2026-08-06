# Flagship 1 — Real Estate Content Ops Agent

**Working repo name:** `real-estate-content-agent`
**One-liner:** An autonomous agent that turns a property listing into a full, on-brand social content batch — planning, copywriting, and media generation end-to-end — with built-in safety guardrails and evaluation.

This doc is our build plan and doubles as the repo's `docs/SPEC.md`.

---

## 1. What it does (the demo story)

> Input: a listing (address, price, beds/baths, photos, key features).
> The agent autonomously: plans a content batch → writes captions/hooks per platform → calls your video/media pipeline → assembles the posts → self-checks quality → outputs a ready-to-publish batch (and can auto-publish once it clears its confidence + guardrail checks).

The "wow" in the demo: you paste one listing, walk away, and come back to a finished, on-brand content set with a trace showing every decision the agent made.

---

## 2. Architecture

Built as a **stateful agent graph** (LangGraph) so each step is a node with visible state — this is what lets you show an architecture diagram and a decision trace, which is exactly what reviewers want.

```
             ┌─────────────┐
  listing →  │   PLANNER   │  decides what content to make (which platforms, how many, angle)
             └──────┬──────┘
                    ▼
             ┌─────────────┐
             │  COPYWRITER │  drafts hooks + captions per platform (calls Claude)
             └──────┬──────┘
                    ▼
             ┌─────────────┐
             │ MEDIA TOOLS │  calls YOUR real estate video/image pipeline (tool calls)
             └──────┬──────┘
                    ▼
             ┌─────────────┐
             │  ASSEMBLER  │  combines media + copy into per-platform post objects
             └──────┬──────┘
                    ▼
             ┌─────────────┐
             │   CRITIC    │  self-evaluates quality + brand fit → confidence score
             └──────┬──────┘
                    ▼
         confidence ≥ threshold?  ──no──▶  HOLD (flag for review, do not publish)
                    │ yes
                    ▼
             ┌─────────────┐
             │  PUBLISHER  │  schedules/publishes (respects guardrails + kill switch)
             └─────────────┘
```

State carried through the graph: the listing, the plan, drafts, generated media refs, critic scores, cost so far, and a full action log.

---

## 3. The tools the agent calls (reusing your pipelines)

Each tool is a Python function with a typed schema (this *is* the "tool-calling with schemas" skill employers screen for). We wrap your existing pipelines behind clean interfaces:

| Tool | What it wraps | Input → Output |
|---|---|---|
| `generate_listing_video()` | your real estate video pipeline | listing + photos → video URL |
| `generate_image_set()` | your image/gen pipeline | listing → branded image variants |
| `write_captions()` | Claude API | listing + platform → caption/hook |
| `schedule_post()` | your posting/automation layer | post object → scheduled/published |
| `check_brand_guidelines()` | a rules/prompt check | draft → pass/fail + notes |

> **What I'll need from you:** a look at how your current real estate video pipeline is triggered (a function? an API call? a script?). Once I see the interface, we wrap it cleanly. Until then, I'll stub these with realistic mocks so we can build and test the whole agent loop, then swap in the real calls.

---

## 4. Autonomy + safety model (your differentiator)

Fully autonomous loop, made *credible* with guardrails:

- **Dry-run mode (default):** runs the entire loop but never publishes — outputs the batch for inspection. Perfect for demos + CI.
- **Confidence gate:** the CRITIC node scores each post; anything below threshold is held, not published.
- **Spend cap:** hard limit on generation/API cost per run; agent stops and reports if exceeded.
- **Kill switch:** an env flag / config that disables all publishing tools instantly.
- **Full action log:** every tool call, input, and decision is recorded (feeds observability later).

This section alone is worth a paragraph in your README — it shows you think about production risk, not just happy-path demos.

---

## 5. Stack

- **Python 3.11+** — core
- **LangGraph** — the agent state machine
- **Claude API** — planning, copywriting, self-critique
- **Pydantic** — typed tool schemas + validation
- **FastAPI** — a thin API to trigger runs (sets up Flagship 3 deployment story)
- **pytest** — tests, including a full dry-run test of the graph
- **Docker** — packaging (used again in the production-hardening flagship)

---

## 6. Evaluation plan (do NOT skip — most portfolios do)

We'll measure and report real numbers in the README:

- **Task success rate:** % of runs that produce a complete, valid batch (n ≥ 20 test listings).
- **Brand-guideline pass rate:** % of drafts passing `check_brand_guidelines()`.
- **Critic vs. human agreement:** on a sample, do the critic's scores match your judgment?
- **Cost per run:** average $ per completed batch.

A small `evals/` folder with test listings + a script that prints these = instant credibility.

---

## 7. Build milestones (our pair sessions)

Each is roughly one working session. We build together — I scaffold + explain, you drive and fill in.

1. **Repo skeleton + tool schemas** — project structure, typed tool stubs (mocked), one passing test.
2. **The graph** — wire PLANNER → COPYWRITER → ASSEMBLER with mocked tools; get a full dry-run producing a batch.
3. **Copywriting for real** — plug in Claude for planning + captions; make output genuinely good.
4. **CRITIC + guardrails** — confidence gate, spend cap, kill switch, action log.
5. **Wire in your real pipelines** — swap mocks for your actual video/media/posting tools.
6. **Evaluation + README + diagram + demo GIF** — package it to flagship standard.

---

## 8. What I need from you before session 5

- How your real estate video pipeline is invoked today (function/API/script + rough inputs & outputs).
- Whether you have a preferred posting/scheduling tool we should target.
- A couple of sample listings (real or fake) to test with.

Nothing blocks us from starting sessions 1–4 right now with mocks.
