"""Session 1's first passing test: a full dry-run produces a valid batch
and — critically — publishes nothing.
"""
from __future__ import annotations

from content_agent.config import Config
from content_agent.graph import build_graph
from content_agent.models import Listing, PostStatus, RunState

LISTING = Listing(
    address="500 Test Ave, Minneapolis, MN",
    price=350000,
    beds=3,
    baths=2,
    sqft=1800,
    features=["updated kitchen", "big backyard"],
    photo_urls=["https://mock.media/test/1.jpg"],
)


def _run() -> RunState:
    app = build_graph()
    initial: RunState = {"listing": LISTING, "cost_usd": 0.0, "action_log": []}
    return app.invoke(initial)


def test_dry_run_produces_full_batch():
    final = _run()
    posts = final["posts"]
    # planner creates 3 items -> 3 posts
    assert len(posts) == 3
    # every post has copy and at least one media asset
    for post in posts:
        assert post.caption.strip()
        assert len(post.media) >= 1


def test_dry_run_never_publishes():
    final = _run()
    # default config is dry_run=True, so nothing may be marked published
    assert all(p.status != PostStatus.published for p in final["posts"])
    # and at least one post should be in the ready-dry-run state
    assert any(p.status == PostStatus.ready_dry_run for p in final["posts"])


def test_spend_stays_under_cap():
    final = _run()
    cfg = Config.from_env()
    assert final["cost_usd"] <= cfg.spend_cap_usd


def test_action_log_traces_every_stage():
    final = _run()
    log = " ".join(final["action_log"])
    for stage in ("planner", "copywriter", "media", "assembler", "critic", "publisher"):
        assert stage in log
