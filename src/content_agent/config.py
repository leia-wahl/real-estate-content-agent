"""Runtime configuration + safety guardrails.

Everything here is what keeps a *fully autonomous* agent credible:
a dry-run default, a spend cap, a confidence gate, and a kill switch.
Values can be overridden with environment variables.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


def _env_float(name: str, default: float) -> float:
    val = os.getenv(name)
    return float(val) if val is not None else default


@dataclass(frozen=True)
class Config:
    # SAFETY -----------------------------------------------------------
    dry_run: bool = True          # default: run the whole loop but never publish
    kill_switch: bool = False     # if True, publishing tools are hard-disabled
    spend_cap_usd: float = 5.0    # stop the run if projected cost exceeds this
    confidence_threshold: float = 0.7  # posts below this are held, not published

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            dry_run=_env_bool("AGENT_DRY_RUN", True),
            kill_switch=_env_bool("AGENT_KILL_SWITCH", False),
            spend_cap_usd=_env_float("AGENT_SPEND_CAP_USD", 5.0),
            confidence_threshold=_env_float("AGENT_CONFIDENCE_THRESHOLD", 0.7),
        )
