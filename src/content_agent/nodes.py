"""The agent's nodes. Each is a pure-ish function: state in, state update out.

Keeping nodes small and typed is what makes the graph readable and the
decision trace (action_log) meaningful.
"""
from __future__ import annotations

from . import tools
from .config import Config
from .models import (
    ContentPlan,
    CriticResult,
    Draft,
    Listing,
    PlanItem,
    Platform,
    Post,
    PostStatus,
    RunState,
)


def _log(state: RunState, msg: str) -> list[str]:
    log = list(state.get("action_log", []))
    log.append(msg)
    return log


def planner(state: RunState) -> RunState:
    """Decide what content to make. Session 3: let Claude choose angles."""
    listing: Listing = state["listing"]
    plan = ContentPlan(items=[
        PlanItem(platform=Platform.instagram, fmt="reel", angle="lifestyle walkthrough"),
        PlanItem(platform=Platform.tiktok, fmt="reel", angle="fast-cut highlight"),
        PlanItem(platform=Platform.facebook, fmt="single", angle="community + value"),
    ])
    return {
        "plan": plan,
        "action_log": _log(state, f"planner: {len(plan.items)} items for {listing.address}"),
    }


def copywriter(state: RunState) -> RunState:
    """Draft copy per planned item."""
    listing: Listing = state["listing"]
    plan: ContentPlan = state["plan"]
    cost = state.get("cost_usd", 0.0)
    drafts: list[Draft] = []
    for item in plan.items:
        draft, c = tools.write_captions(listing, item.platform)
        drafts.append(draft)
        cost += c
    return {
        "drafts": drafts,
        "cost_usd": cost,
        "action_log": _log(state, f"copywriter: {len(drafts)} drafts"),
    }


def media(state: RunState) -> RunState:
    """Generate media by calling the (mocked) pipelines. Honors spend cap."""
    listing: Listing = state["listing"]
    cost = state.get("cost_usd", 0.0)
    cfg = Config.from_env()

    video, cv = tools.generate_listing_video(listing)
    images, ci = tools.generate_image_set(listing)
    cost += cv + ci

    over_cap = cost > cfg.spend_cap_usd
    assets = [video, *images]
    log_msg = f"media: 1 video + {len(images)} images (cost ${cost:.2f})"
    if over_cap:
        log_msg += f" — WARNING over spend cap ${cfg.spend_cap_usd:.2f}"
    return {
        "media": assets,
        "cost_usd": cost,
        "action_log": _log(state, log_msg),
    }


def assembler(state: RunState) -> RunState:
    """Combine drafts + media into per-platform Post objects."""
    drafts: list[Draft] = state["drafts"]
    assets = state["media"]
    video = [a for a in assets if a.kind == "video"]
    images = [a for a in assets if a.kind == "image"]

    posts: list[Post] = []
    for d in drafts:
        media_for_post = video if d.platform in (Platform.instagram, Platform.tiktok) else images
        posts.append(Post(
            platform=d.platform,
            caption=f"{d.hook}\n\n{d.caption}\n\n{' '.join(d.hashtags)}",
            media=list(media_for_post),
        ))
    return {
        "posts": posts,
        "action_log": _log(state, f"assembler: {len(posts)} posts assembled"),
    }


def critic(state: RunState) -> RunState:
    """Self-evaluate quality + brand fit -> per-post confidence + batch score."""
    drafts: list[Draft] = state["drafts"]
    posts: list[Post] = state["posts"]

    per_post_scores: list[float] = []
    for post, draft in zip(posts, drafts):
        ok, _notes = tools.check_brand_guidelines(draft)
        has_media = len(post.media) > 0
        # Realistic-ish scoring so the confidence gate is actually meaningful:
        # brand compliance + media presence + a caption-quality proxy.
        # Session 3: replace this heuristic with a real Claude self-critique.
        brand = 0.45 if ok else 0.10
        media_score = 0.25 if has_media else 0.0
        target_len = 400
        caption_quality = 0.30 * min(1.0, len(post.caption) / target_len)
        score = round(brand + media_score + caption_quality, 2)
        post.confidence = score
        per_post_scores.append(score)

    batch_score = round(sum(per_post_scores) / len(per_post_scores), 2) if per_post_scores else 0.0
    cfg = Config.from_env()
    passed = batch_score >= cfg.confidence_threshold
    result = CriticResult(
        score=batch_score,
        passed=passed,
        notes=f"batch score {batch_score} vs threshold {cfg.confidence_threshold}",
    )
    return {
        "posts": posts,
        "critic": result,
        "action_log": _log(state, f"critic: score {batch_score}, passed={passed}"),
    }


def publisher(state: RunState) -> RunState:
    """The only node with real-world side effects. Fully guarded."""
    cfg = Config.from_env()
    posts: list[Post] = state["posts"]
    critic: CriticResult = state["critic"]

    for post in posts:
        if post.confidence < cfg.confidence_threshold:
            post.status = PostStatus.held
        elif cfg.dry_run or cfg.kill_switch:
            post.status = PostStatus.ready_dry_run
        else:
            tools.schedule_post(post)
            post.status = PostStatus.published

    mode = "DRY-RUN" if cfg.dry_run else ("KILL-SWITCH" if cfg.kill_switch else "LIVE")
    published = sum(1 for p in posts if p.status == PostStatus.published)
    return {
        "posts": posts,
        "action_log": _log(state, f"publisher [{mode}]: {published} published"),
    }


def hold(state: RunState) -> RunState:
    """Batch failed the confidence gate — nothing publishes."""
    posts: list[Post] = state["posts"]
    for post in posts:
        post.status = PostStatus.held
    return {
        "posts": posts,
        "action_log": _log(state, "hold: batch below confidence threshold — nothing published"),
    }


# --- Conditional edge -------------------------------------------------
def gate(state: RunState) -> str:
    """Route after the critic: publish the batch or hold it."""
    return "publisher" if state["critic"].passed else "hold"
