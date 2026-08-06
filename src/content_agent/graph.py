"""Wire the nodes into a LangGraph state machine.

    planner -> copywriter -> media -> assembler -> critic --(gate)-->  publisher
                                                              \\--> hold

The conditional edge after `critic` is the confidence gate: it decides
whether the batch is good enough to publish.
"""
from __future__ import annotations

from langgraph.graph import END, StateGraph

from . import nodes
from .models import RunState


def build_graph():
    g = StateGraph(RunState)

    g.add_node("planner", nodes.planner)
    g.add_node("copywriter", nodes.copywriter)
    g.add_node("media", nodes.media)
    g.add_node("assembler", nodes.assembler)
    g.add_node("critic", nodes.critic)
    g.add_node("publisher", nodes.publisher)
    g.add_node("hold", nodes.hold)

    g.set_entry_point("planner")
    g.add_edge("planner", "copywriter")
    g.add_edge("copywriter", "media")
    g.add_edge("media", "assembler")
    g.add_edge("assembler", "critic")

    # Confidence gate: publish or hold.
    g.add_conditional_edges("critic", nodes.gate, {"publisher": "publisher", "hold": "hold"})

    g.add_edge("publisher", END)
    g.add_edge("hold", END)

    return g.compile()
