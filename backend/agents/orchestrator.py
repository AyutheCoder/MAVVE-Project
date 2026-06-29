"""
MAVVE Core LangGraph Orchestrator.
Determines routing between agents and manages state transitions.
"""

import structlog
from typing import Literal
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import AIMessage, HumanMessage

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.state import MAVVEState
from agents.llm import get_llm
from config import settings

logger = structlog.get_logger()

# ── 1. LLM Setup ─────────────────────────────────────────
llm = get_llm()

# ── 2. Nodes ─────────────────────────────────────────────

def analyze_risk(state: MAVVEState) -> MAVVEState:
    """Entry node: Examines risk factors and determines next step."""
    logger.info("node_enter", node="analyze_risk", order_id=state.get("order_id"))
    
    risk_factors = state.get("risk_factors", [])
    active_agent = "orchestrator"
    
    if "address_anomaly" in risk_factors or "missing_address" in risk_factors:
        active_agent = "address_agent"
    elif "cod_payment" in risk_factors:
        active_agent = "prepaid_agent"
    elif "high_historical_rto" in risk_factors or "late_night_impulse" in risk_factors or "first_time_user" in risk_factors:
        active_agent = "intent_agent"
    else:
        # Default fallback
        active_agent = "intent_agent"
        
    return {"active_agent": active_agent}

from agents.address_agent import address_agent_node

from agents.intent_agent import intent_agent_node

from agents.prepaid_agent import prepaid_agent_node

def human_input_node(state: MAVVEState) -> MAVVEState:
    """Wait for user response via WhatsApp."""
    logger.info("node_enter", node="human_input", order_id=state.get("order_id"))
    # In a real system, execution is paused here using `interrupt_before=["human_input"]`
    return {}

def dispatch_order(state: MAVVEState) -> MAVVEState:
    """Terminal node: Order is validated and ready for dispatch."""
    logger.info("node_enter", node="dispatch_order", order_id=state.get("order_id"), result="success")
    return {"final_disposition": "DISPATCH"}

def cancel_order(state: MAVVEState) -> MAVVEState:
    """Terminal node: Order is highly suspicious or user cancelled."""
    logger.info("node_enter", node="cancel_order", order_id=state.get("order_id"), result="failure")
    return {"final_disposition": "CANCEL"}


# ── 3. Edges & Routing ───────────────────────────────────

def route_after_analyze(state: MAVVEState) -> str:
    """Determine which agent gets control based on active_agent state."""
    logger.info("routing_decision", source="analyze_risk", target=state.get("active_agent"))
    return state.get("active_agent", "intent_agent")

def route_after_agent(state: MAVVEState) -> str:
    """
    Evaluate agent output and determine next step.
    If intent is verified and no address issues, dispatch.
    If user wants to cancel, cancel.
    Otherwise, wait for human input.
    """
    messages = state.get("messages", [])
    last_msg = messages[-1].content if messages else ""
    
    if state.get("intent_verified") and state.get("address_confidence", 0) > 0.8:
        target = "dispatch_order"
    elif "cancel" in str(last_msg).lower():
        target = "cancel_order"
    else:
        target = "human_input"
        
    logger.info("routing_decision", source=state.get("active_agent"), target=target)
    return target

def route_after_human(state: MAVVEState) -> str:
    """Route back to the active agent or orchestrator after human replies."""
    active = state.get("active_agent")
    
    if state.get("interaction_count", 0) >= 3:
        target = "cancel_order"
    elif active in ["address_agent", "intent_agent", "prepaid_agent"]:
        target = active
    else:
        target = "analyze_risk"
        
    logger.info("routing_decision", source="human_input", target=target)
    return target


# ── 4. Graph Construction ────────────────────────────────

workflow = StateGraph(MAVVEState)

workflow.add_node("analyze_risk", analyze_risk)
workflow.add_node("address_agent", address_agent_node)
workflow.add_node("intent_agent", intent_agent_node)
workflow.add_node("prepaid_agent", prepaid_agent_node)
workflow.add_node("human_input", human_input_node)
workflow.add_node("dispatch_order", dispatch_order)
workflow.add_node("cancel_order", cancel_order)

workflow.add_edge(START, "analyze_risk")

workflow.add_conditional_edges(
    "analyze_risk",
    route_after_analyze,
    {
        "address_agent": "address_agent",
        "intent_agent": "intent_agent",
        "prepaid_agent": "prepaid_agent"
    }
)

for agent in ["address_agent", "intent_agent", "prepaid_agent"]:
    workflow.add_conditional_edges(
        agent,
        route_after_agent,
        {
            "human_input": "human_input",
            "dispatch_order": "dispatch_order",
            "cancel_order": "cancel_order"
        }
    )

workflow.add_conditional_edges(
    "human_input",
    route_after_human,
    {
        "address_agent": "address_agent",
        "intent_agent": "intent_agent",
        "prepaid_agent": "prepaid_agent",
        "analyze_risk": "analyze_risk",
        "cancel_order": "cancel_order"
    }
)

workflow.add_edge("dispatch_order", END)
workflow.add_edge("cancel_order", END)

app = workflow.compile()


# ── 5. Test & Mermaid Export ─────────────────────────────
if __name__ == "__main__":
    print("--- LangGraph MAVVE Orchestrator ---")
    
    # Export Mermaid
    try:
        mermaid_md = app.get_graph().draw_mermaid()
        with open("mavve_graph.mmd", "w") as f:
            f.write(mermaid_md)
        print("Saved graph visualization to mavve_graph.mmd\n")
    except Exception as e:
        print("Failed to export Mermaid diagram:", e)
    
    # Test Run
    initial_state = {
        "order_id": "ORD-TEST-01",
        "user_id": "USR-99",
        "user_language": "hi",
        "risk_factors": ["address_anomaly"],
        "address_confidence": 0.4,
        "intent_verified": False,
        "payment_status": "COD",
        "active_agent": "orchestrator",
        "interaction_count": 0,
        "messages": []
    }
    
    print("Starting simulation for order:", initial_state["order_id"])
    print("Risk Factors:", initial_state["risk_factors"])
    print("-" * 40)
    
    # We use a custom limit so we don't loop endlessly in the test 
    # since we don't increment interaction_count yet
    step_count = 0
    for event in app.stream(initial_state):
        step_count += 1
        for key, value in event.items():
            print(f"Node [{key}] output:")
            if value and "messages" in value and value["messages"]:
                print(f"  Message: {value['messages'][-1].content}")
            if value and "active_agent" in value:
                print(f"  Active Agent: {value['active_agent']}")
            if value and "final_disposition" in value:
                print(f"  Outcome: {value['final_disposition']}")
            print("-" * 40)
            
        if step_count > 3:
            print("Stopping simulation (test limit reached).")
            break
