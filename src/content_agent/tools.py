"""Tools the agent can call.

In Session 1 these are MOCKS with realistic shapes so we can build and
test the whole agent loop before touching real infrastructure.

In Session 5 we swap the mock bodies for calls into YOUR real pipelines
(video generation, image generation, posting/scheduling). The function
signatures — the typed contracts — stay the same, so nothing else changes.
Each mock reports a small `cost_usd` so the spend-cap guardrail is real.
"""
from __future__ import annotations

from .models import Draft, Listing, MediaAsset, Platform, Post

# Mock unit costs (USD). Session 5: replace with real metered costs.
COST_VIDEO = 0.50
COST_IMAGE_SET = 0.20
COST_CAPTION = 0.01


def generate_listing_video(listing: Listing) -> tuple[MediaAsset, float]:
    """MOCK of your real estate video pipeline. Returns (asset, cost)."""
    slug = listing.address.lower().replace(" ", "-").replace(",", "")
    asset = MediaAsset(kind="video", url=f"https://mock.media/{slug}/reel.mp4")
    return asset, COST_VIDEO


def generate_image_set(listing: Listing) -> tuple[list[MediaAsset], float]:
    """MOCK of your image/gen pipeline. Returns (assets, cost)."""
    slug = listing.address.lower().replace(" ", "-").replace(",", "")
    assets = [
        MediaAsset(kind="image", url=f"https://mock.media/{slug}/img_{i}.jpg")
        for i in range(3)
    ]
    return assets, COST_IMAGE_SET


def write_captions(listing: Listing, platform: Platform) -> tuple[Draft, float]:
    """MOCK copywriter. Session 3: replace body with a Claude API call.

    Returns (draft, cost).
    """
    price = f"${listing.price:,}"
    feature = listing.features[0] if listing.features else "a must-see layout"
    hook = f"Just listed: {listing.beds}BD/{listing.baths}BA with {feature} 🏡"
    caption = (
        f"{listing.address} — {price}\n"
        f"{listing.beds} bed · {listing.baths} bath · {listing.sqft:,} sqft\n"
        f"Featuring {feature}. DM for a private tour."
    )
    hashtags = ["#realestate", "#justlisted", "#dreamhome"]
    draft = Draft(platform=platform, hook=hook, caption=caption, hashtags=hashtags)
    return draft, COST_CAPTION


def check_brand_guidelines(draft: Draft) -> tuple[bool, str]:
    """MOCK brand check. Session 4: expand into real rules / prompt check."""
    if len(draft.caption) < 20:
        return False, "Caption too short."
    if not draft.hashtags:
        return False, "No hashtags."
    return True, "OK"


def schedule_post(post: Post) -> str:
    """MOCK of your posting/scheduling layer.

    This is the ONLY tool that has real-world side effects, so it is
    guarded by dry_run / kill_switch in the publisher node — it is never
    called directly from anywhere else.
    """
    return f"scheduled:{post.platform.value}"
