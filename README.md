# Real Estate Content Ops Agent

[![CI](https://github.com/leia-wahl/real-estate-content-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/leia-wahl/real-estate-content-agent/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)
![LangGraph](https://img.shields.io/badge/built%20with-LangGraph-purple)

> An autonomous agent that turns a single property listing into a full, on-brand
> social content batch — planning, copywriting, and media generation end-to-end —
> with built-in safety guardrails and evaluation.

**Status:** 🚧 in active development (Session 1 scaffold — mocked tools, full loop working)

<!-- Session 6: add a demo GIF here. It gets the most attention. -->

---

## What it does

Give it one listing. It autonomously:

1. **Plans** a content batch (which platforms, formats, angles)
2. **Writes** hooks + captions per platform
3. **Generates** media by calling the real estate video/image pipeline
4. **Assembles** per-platform posts
5. **Self-critiques** quality + brand fit → a confidence score
6. **Publishes** — but only if it clears the confidence gate and guardrails

```
planner → copywriter → media → assembler → critic ──gate──▶ publisher
                                                     └─────▶ hold
```

## Autonomy, made safe

It runs the entire loop with no human in the middle — and stays credible because of:

- **Dry-run mode** (default): runs everything, publishes nothing
- **Confidence gate**: low-scoring posts are held, not published
- **Spend cap**: hard cost ceiling per run
- **Kill switch**: instantly disables all publishing
- **Full action log**: every decision is traced

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

pytest                        # run the test suite
python -m content_agent.run   # run the agent on a sample listing (dry-run)
python evals/run_eval.py      # run the mini evaluation over sample listings
```

Try flipping a guardrail:

```bash
AGENT_CONFIDENCE_THRESHOLD=0.99 python -m content_agent.run   # forces a HOLD
```

## Project layout

```
src/content_agent/
  config.py    # guardrails: dry-run, spend cap, confidence gate, kill switch
  models.py    # typed Pydantic contracts (Listing, Post, ...)
  tools.py     # tools the agent calls — MOCKED now, real pipelines in Session 5
  nodes.py     # the agent's steps (planner, copywriter, critic, ...)
  graph.py     # LangGraph state machine wiring it together
  run.py       # entrypoint
evals/         # sample listings + a mini evaluation harness
tests/         # a full dry-run test that publishes nothing
docs/SPEC.md   # the full build plan
```

## Roadmap

- [x] **Session 1** — scaffold: structure, typed tools (mocked), working loop, tests
- [ ] **Session 2** — flesh out the graph + state handling
- [ ] **Session 3** — real Claude calls for planning + copywriting
- [ ] **Session 4** — critic + guardrails hardening
- [ ] **Session 5** — wire in the real video/image/posting pipelines
- [ ] **Session 6** — evaluation, diagram, demo GIF, polish

## Tech

Python · LangGraph · Claude API · Pydantic · FastAPI · pytest · Docker

---

Built by [Leia (leia-wahl)](https://github.com/leia-wahl)
