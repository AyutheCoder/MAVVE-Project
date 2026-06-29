import pytest
from agents.orchestrator import app as mavve_graph, route_after_analyze, route_after_agent


# ── Test Routing from analyze_risk ────────────────────────

def test_routing_address_anomaly():
    """Address anomaly risk factor should route to address_agent."""
    state = {
        "messages": [],
        "order_id": "ORD-123",
        "user_id": "USR-123",
        "user_language": "hi",
        "address_confidence": 0.4,
        "intent_verified": False,
        "payment_status": "COD",
        "discount_offered": 0,
        "active_agent": "address_agent",   # set by analyze_risk node
        "risk_factors": ["address_anomaly"],
        "interaction_count": 0,
        "final_disposition": None,
    }
    next_node = route_after_analyze(state)
    assert next_node == "address_agent", f"Expected address_agent, got {next_node}"


def test_routing_cod_payment():
    """COD payment risk factor should route to prepaid_agent."""
    state = {
        "messages": [],
        "order_id": "ORD-456",
        "user_id": "USR-456",
        "user_language": "mr",
        "address_confidence": 0.9,
        "intent_verified": False,
        "payment_status": "COD",
        "discount_offered": 0,
        "active_agent": "prepaid_agent",
        "risk_factors": ["cod_payment"],
        "interaction_count": 0,
        "final_disposition": None,
    }
    next_node = route_after_analyze(state)
    assert next_node == "prepaid_agent", f"Expected prepaid_agent, got {next_node}"


def test_routing_high_historical_rto():
    """High historical RTO should route to intent_agent (not prepaid)."""
    state = {
        "messages": [],
        "order_id": "ORD-789",
        "user_id": "USR-789",
        "user_language": "en",
        "address_confidence": 0.9,
        "intent_verified": False,
        "payment_status": "COD",
        "discount_offered": 0,
        "active_agent": "intent_agent",
        "risk_factors": ["high_historical_rto"],
        "interaction_count": 0,
        "final_disposition": None,
    }
    next_node = route_after_analyze(state)
    assert next_node == "intent_agent", f"Expected intent_agent, got {next_node}"


def test_routing_default_fallback():
    """Empty risk factors should fall through to intent_agent (default)."""
    state = {
        "messages": [],
        "order_id": "ORD-000",
        "user_id": "USR-000",
        "user_language": "bn",
        "address_confidence": 0.5,
        "intent_verified": False,
        "payment_status": "COD",
        "discount_offered": 0,
        "active_agent": "intent_agent",
        "risk_factors": [],
        "interaction_count": 0,
        "final_disposition": None,
    }
    next_node = route_after_analyze(state)
    assert next_node == "intent_agent", f"Expected intent_agent, got {next_node}"


# ── Test Post-Agent Routing ───────────────────────────────

def test_routing_to_dispatch():
    """When intent is verified and address confidence is high, dispatch the order."""
    from langchain_core.messages import AIMessage
    state = {
        "messages": [AIMessage(content="Your order is confirmed!")],
        "order_id": "ORD-DISPATCH",
        "user_id": "USR-D",
        "user_language": "hi",
        "address_confidence": 0.9,
        "intent_verified": True,
        "payment_status": "PREPAID_SUCCESS",
        "discount_offered": 50,
        "active_agent": "intent_agent",
        "risk_factors": [],
        "interaction_count": 2,
        "final_disposition": None,
    }
    next_node = route_after_agent(state)
    assert next_node == "dispatch_order", f"Expected dispatch_order, got {next_node}"


def test_routing_to_cancel():
    """When message contains 'cancel', route to cancel_order."""
    from langchain_core.messages import AIMessage
    state = {
        "messages": [AIMessage(content="Order has been cancelled per user request.")],
        "order_id": "ORD-CANCEL",
        "user_id": "USR-C",
        "user_language": "hi",
        "address_confidence": 0.3,
        "intent_verified": False,
        "payment_status": "COD",
        "discount_offered": 0,
        "active_agent": "intent_agent",
        "risk_factors": ["high_historical_rto"],
        "interaction_count": 1,
        "final_disposition": None,
    }
    next_node = route_after_agent(state)
    assert next_node == "cancel_order", f"Expected cancel_order, got {next_node}"


def test_routing_to_human_input():
    """When intent not verified and address low, should wait for human input."""
    from langchain_core.messages import AIMessage
    state = {
        "messages": [AIMessage(content="Can you please confirm your landmark?")],
        "order_id": "ORD-WAIT",
        "user_id": "USR-W",
        "user_language": "hi",
        "address_confidence": 0.5,
        "intent_verified": False,
        "payment_status": "COD",
        "discount_offered": 0,
        "active_agent": "address_agent",
        "risk_factors": ["address_anomaly"],
        "interaction_count": 1,
        "final_disposition": None,
    }
    next_node = route_after_agent(state)
    assert next_node == "human_input", f"Expected human_input, got {next_node}"
