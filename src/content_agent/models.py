"""Typed domain models (Pydantic v2).

These are the contracts every tool and node speaks in. Clean, typed
schemas like these ARE the "tool-calling with validation" skill that
hiring managers screen for.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional, TypedDict

from pydantic import BaseModel, Field


class Platform(str, Enum):
    instagram = "instagram"
    tiktok = "tiktok"
    facebook = "facebook"


class Listing(BaseModel):
    """The single input to the agent."""
    address: str
    price: int
    beds: int
    baths: float
    sqft: int
    features: list[str] = Field(default_factory=list)
    photo_urls: list[str] = Field(default_factory=list)


class PlanItem(BaseModel):
    platform: Platform
    fmt: str                 # e.g. "reel", "carousel", "single"
    angle: str               # the creative angle the planner chose


class ContentPlan(BaseModel):
    items: list[PlanItem] = Field(default_factory=list)


class Draft(BaseModel):
    platform: Platform
    hook: str
    caption: str
    hashtags: list[str] = Field(default_factory=list)


class MediaAsset(BaseModel):
    kind: str                # "video" | "image"
    url: str


class PostStatus(str, Enum):
    draft = "draft"
    held = "held"                     # failed the confidence gate
    ready_dry_run = "ready_dry_run"   # would publish, but dry-run/kill-switch on
    published = "published"


class Post(BaseModel):
    platform: Platform
    caption: str
    media: list[MediaAsset] = Field(default_factory=list)
    confidence: float = 0.0
    status: PostStatus = PostStatus.draft


class CriticResult(BaseModel):
    score: float                      # 0..1 overall batch confidence
    notes: str = ""
    passed: bool = False


# --- Graph state ------------------------------------------------------
# LangGraph passes this dict between nodes. Keys are filled progressively.
class RunState(TypedDict, total=False):
    listing: Listing
    plan: ContentPlan
    drafts: list[Draft]
    media: list[MediaAsset]
    posts: list[Post]
    critic: CriticResult
    cost_usd: float
    action_log: list[str]
