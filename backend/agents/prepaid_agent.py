"""
Prepaid Conversion Agent.
Negotiates with COD users to convert to Prepaid using dynamic, escalating discounts.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage, HumanMessage

from agents.state import MAVVEState
from agents.llm import get_llm
from agents.tools.payment_link import generate_payment_link, check_payment_status
from agents.tools.order_updater import confirm_prepaid_conversion
from config import settings

logger = structlog.get_logger()

# ── 1. LLM & Tools Setup ─────────────────────────────────

PREPAID_TOOLS = [generate_payment_link, check_payment_status, confirm_prepaid_conversion]

llm = get_llm()

llm_with_tools = llm.bind_tools(PREPAID_TOOLS)

# ── 2. System Prompts ────────────────────────────────────

PREPAID_SYSTEM_PROMPT = """
You are the MAVVE Prepaid Conversion Agent. 
Your goal is to gently persuade a user who opted for Cash on Delivery (COD) to convert to Prepaid via UPI (GPay/PhonePe).

You speak empathetically and respectfully in the customer's preferred language: {language}.
The total order value is ₹{total_amount}.

Instructions:
1. Negotiation Strategy (Escalating Discount):
   - First interaction: Offer a 5% discount (₹{discount_5}). "Pay via UPI now and save ₹{discount_5} instantly!"
   - If they refuse/hesitate due to trust: Escalate to 10% (₹{discount_10}) and emphasize the 30-day return policy and instant refunds.
   - If they refuse again: Offer the max 15% discount (₹{discount_15}) as a final offer.

2. Objection Handling:
   - "I don't use UPI": Suggest asking a family member or friend to scan the QR/link.
   - "Is this fraud?": Reassure them that MAVVE is verified and refunds are guaranteed.
   - "No, COD only": Respect their choice. Say "No problem, we will deliver as COD." and DO NOT push further.

3. Tools Usage:
   - Once they agree to an offer, use `generate_payment_link` to create a UPI link for the *discounted* amount. Send them the link.
   - If they say they paid, use `check_payment_status` to verify.
   - If payment is verified successful, use `confirm_prepaid_conversion` and conclude the conversation warmly.

Current discount offered: {discount_offered}%
Keep responses concise (1-2 sentences). Do not sound like a bot, sound like a helpful local assistant.
"""

# ── 3. Node Implementation ───────────────────────────────

def prepaid_agent_node(state: MAVVEState) -> MAVVEState:
    """
    Main entry for the Prepaid Conversion Agent.
    """
    logger.info("node_enter", node="prepaid_agent", order_id=state.get("order_id"))
    
    messages = state.get("messages", [])
    user_language = state.get("user_language", "hi")
    
    # Mock retrieving order total (in production, fetch from DB using order_id)
    total_amount = 500.0
    discount_offered = state.get("discount_offered", 0.0)
    
    # Calculate absolute discount amounts for the prompt
    d5 = int(total_amount * 0.05)
    d10 = int(total_amount * 0.10)
    d15 = int(total_amount * 0.15)
    
    sys_msg = SystemMessage(content=PREPAID_SYSTEM_PROMPT.format(
        language=user_language, 
        total_amount=total_amount,
        discount_5=d5,
        discount_10=d10,
        discount_15=d15,
        discount_offered=discount_offered
    ))
    
    llm_messages = [sys_msg] + messages
    
    response = llm_with_tools.invoke(llm_messages)
    
    # Determine next discount state if the agent is escalating
    if "10%" in response.content or str(d10) in response.content:
        discount_offered = 10.0
    elif "15%" in response.content or str(d15) in response.content:
        discount_offered = 15.0
    elif discount_offered == 0.0 and ("5%" in response.content or str(d5) in response.content):
        discount_offered = 5.0
    
    payment_status = state.get("payment_status", "COD")
    
    if response.tool_calls:
        logger.info("tool_calls_detected", calls=len(response.tool_calls))
        tool_messages = []
        for tool_call in response.tool_calls:
            if tool_call["name"] == "generate_payment_link":
                result = generate_payment_link.invoke(tool_call["args"])
                payment_status = "PREPAID_PENDING"
                tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
            elif tool_call["name"] == "check_payment_status":
                result = check_payment_status.invoke(tool_call["args"])
                if result == "success":
                    payment_status = "PREPAID_SUCCESS"
                tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
            elif tool_call["name"] == "confirm_prepaid_conversion":
                result = confirm_prepaid_conversion.invoke(tool_call["args"])
                tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
                
        final_messages = llm_messages + [response] + tool_messages
        final_response = llm_with_tools.invoke(final_messages)
        
        new_messages = [response] + tool_messages + [final_response]
    else:
        new_messages = [response]
        
    return {
        "messages": new_messages,
        "active_agent": "prepaid_agent",
        "payment_status": payment_status,
        "discount_offered": discount_offered,
        "interaction_count": state.get("interaction_count", 0) + 1
    }

# ── 4. Standalone Test ───────────────────────────────────
if __name__ == "__main__":
    print("--- Prepaid Conversion Agent Simulation ---")
    
    scenarios = [
        ("Successful Conversion", ["What is the offer?", "Okay, give me the link.", "I paid."]),
        ("Trust Hesitation (Partial Neg)", ["No, I will pay COD.", "I don't trust online payment.", "Okay, 10% is good, send link."]),
        ("Complete Decline", ["No, I only want COD.", "I don't have UPI at all."])
    ]
    
    for scenario_name, user_inputs in scenarios:
        print(f"\n\n{'='*40}")
        print(f"Scenario: {scenario_name}")
        print(f"{'='*40}")
        
        state: MAVVEState = {
            "order_id": "ORD-789",
            "user_id": "USR-1",
            "user_language": "English",
            "address_confidence": 0.9,
            "intent_verified": True,
            "payment_status": "COD",
            "active_agent": "prepaid_agent",
            "risk_factors": ["cod_payment"],
            "interaction_count": 0,
            "discount_offered": 0.0,
            "final_disposition": None,
            "messages": [AIMessage(content="Pay via UPI now and save ₹25 instantly!")]
        }
        
        for ui in user_inputs:
            print(f"\n[User]: {ui}")
            state["messages"].append(HumanMessage(content=ui))
            
            state = prepaid_agent_node(state)
            
            # Print only the latest agent outputs
            for msg in state["messages"][-3:]:
                if isinstance(msg, AIMessage):
                    if msg.tool_calls:
                        print("  Tool Calls:", [t["name"] for t in msg.tool_calls])
                    elif msg.content:
                        print("  [Agent]:", msg.content)
                elif isinstance(msg, ToolMessage):
                    print("  [Tool Result]:", msg.content)
            
            print(f"  [Discount State]: {state.get('discount_offered')}% | [Payment Status]: {state.get('payment_status')}")
