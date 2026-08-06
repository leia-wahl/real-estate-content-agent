"""Run the agent on one listing and print the trace.

Usage:
    python -m content_agent.run

Defaults to dry-run (nothing publishes). Try flipping guardrails:
    AGENT_CONFIDENCE_THRESHOLD=0.99 python -m content_agent.run   # forces a HOLD
    AGENT_DRY_RUN=false python -m content_agent.run               # would go LIVE (mock)
"""
from __future__ import annotations

from .config import Config
from .graph import build_graph
from .models import Listing, RunState

SAMPLE = Listing(
    address="123 Lakeview Dr, Burnsville, MN",
    price=485000,
    beds=4,
    baths=2.5,
    sqft=2650,
    features=["a chef's kitchen", "walkout basement", "lake views"],
    photo_urls=["https://mock.media/123-lakeview/1.jpg"],
)


def main() -> RunState:
    cfg = Config.from_env()
    app = build_graph()
    initial: RunState = {"listing": SAMPLE, "cost_usd": 0.0, "action_log": []}
    final: RunState = app.invoke(initial)

    print("\n=== RUN CONFIG ===")
    print(f"dry_run={cfg.dry_run}  kill_switch={cfg.kill_switch}  "
          f"threshold={cfg.confidence_threshold}  spend_cap=${cfg.spend_cap_usd}")

    print("\n=== ACTION LOG ===")
    for line in final.get("action_log", []):
        print(" •", line)

    print("\n=== BATCH ===")
    for post in final.get("posts", []):
        print(f"[{post.platform.value}] status={post.status.value} "
              f"confidence={post.confidence} media={len(post.media)}")

    print(f"\nTotal cost: ${final.get('cost_usd', 0.0):.2f}")
    return final


if __name__ == "__main__":
    main()
