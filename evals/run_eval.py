"""Tiny evaluation harness. Session 6: expand into the real metrics table.

Runs the agent over every sample listing and prints aggregate numbers.
This is the seed of the "Evaluation" section that makes the repo credible.

Usage:
    python evals/run_eval.py
"""
from __future__ import annotations

import json
from pathlib import Path

from content_agent.graph import build_graph
from content_agent.models import Listing, PostStatus, RunState

HERE = Path(__file__).parent


def load_listings() -> list[Listing]:
    data = json.loads((HERE / "sample_listings.json").read_text())
    return [Listing(**d) for d in data]


def main() -> None:
    app = build_graph()
    listings = load_listings()

    total_posts = 0
    complete_batches = 0
    total_cost = 0.0
    confidences: list[float] = []

    for listing in listings:
        initial: RunState = {"listing": listing, "cost_usd": 0.0, "action_log": []}
        final: RunState = app.invoke(initial)
        posts = final.get("posts", [])
        total_posts += len(posts)
        total_cost += final.get("cost_usd", 0.0)
        confidences.extend(p.confidence for p in posts)
        # "complete" = every post has copy + media and nothing errored
        if posts and all(p.caption.strip() and p.media for p in posts):
            complete_batches += 1

    n = len(listings)
    avg_conf = round(sum(confidences) / len(confidences), 2) if confidences else 0.0
    print("=== EVAL RESULTS (mocked tools) ===")
    print(f"listings evaluated:      {n}")
    print(f"batch success rate:      {complete_batches}/{n} ({100*complete_batches//n}%)")
    print(f"posts produced:          {total_posts}")
    print(f"avg post confidence:     {avg_conf}")
    print(f"avg cost per listing:    ${total_cost / n:.2f}")


if __name__ == "__main__":
    main()
