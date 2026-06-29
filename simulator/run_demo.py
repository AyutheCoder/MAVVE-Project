"""
MAVVE End-to-End Demo Runner
1. Generates mock orders
2. Intercepts high-risk ones
3. Uses ConsumerSimulator to reply to MAVVE agents on WhatsApp
"""
import sys
import os
import asyncio
import time
import httpx
from colorama import init, Fore, Style

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from order_generator import generate_orders
from consumer_simulator import ConsumerSimulator
from db.database import SessionLocal
from api.orders import intercept_order, InterceptRequest
from services.session_manager import SessionManager

init(autoreset=True)

async def process_order(order, user, db):
    print(f"\n{Fore.CYAN}==================================================")
    print(f"Processing Order: {order.order_id} | User: {user.name} ({user.phone_number})")
    
    # 1. Intercept Order
    req = InterceptRequest(order_id=order.order_id)
    res = await intercept_order(req, db)
    
    if res.get("status") == "ignored":
        print(f"{Fore.GREEN}Low Risk Order. No MAVVE intervention required.")
        return
        
    print(f"{Fore.YELLOW}High Risk Detected! {res.get('message')}")
    print(f"Initializing MAVVE WhatsApp Session...")
    
    # Wait for session to initialize in background
    await asyncio.sleep(2)
    session = SessionManager.get_session(user.phone_number)
    
    if not session:
        print(f"{Fore.RED}Failed to initialize session.")
        return
        
    # 2. Simulate Consumer
    print(f"{Fore.MAGENTA}--- Simulation Started ---")
    simulator = ConsumerSimulator(persona="random", language=user.preferred_language)
    print(f"Assigned Persona: {simulator.persona.upper()}")
    
    # We will poll the session manager for new messages addressed to the user
    # In a real flow, WhatsApp would push webhooks. Here we simulate the webhook directly.
    
    max_rounds = 10
    round_count = 0
    last_msg_count = 0
    
    while round_count < max_rounds:
        # Check if session is closed
        if session['state'].get('final_disposition'):
            print(f"\n{Fore.GREEN}Session Finalized: {session['state']['final_disposition']}")
            break
            
        current_msgs = session['state'].get('messages', [])
        
        # If there are new messages from the agent
        if len(current_msgs) > last_msg_count:
            # Print all new messages
            new_msgs = current_msgs[last_msg_count:]
            for msg in new_msgs:
                if msg.type == "ai":
                    print(f"{Fore.BLUE}MAVVE Agent: {msg.content}")
                    
                    # Generate response
                    print(f"{Fore.LIGHTBLACK_EX}Consumer is typing...")
                    await asyncio.sleep(2) # simulate typing
                    reply = simulator.generate_response(msg.content)
                    
                    if reply:
                        print(f"{Fore.GREEN}Consumer: {reply}")
                        # Send reply to backend via webhook
                        webhook_payload = {
                            "object": "whatsapp_business_account",
                            "entry": [{"changes": [{"value": {
                                "messages": [{"from": user.phone_number.replace("+",""), "type": "text", "text": {"body": reply}}]
                            }}]}]
                        }
                        
                        try:
                            # Send via HTTP to the running backend (assuming it's on 8000)
                            async with httpx.AsyncClient() as client:
                                await client.post("http://localhost:8000/api/webhooks/whatsapp", json=webhook_payload)
                        except Exception as e:
                            print(f"{Fore.RED}Failed to send webhook. Ensure backend is running on port 8000.")
                            return
                    else:
                        print(f"{Fore.RED}Consumer went silent (Unavailable persona).")
                        return
                        
            last_msg_count = len(current_msgs)
            
        await asyncio.sleep(3) # Polling interval
        round_count += 1
        
    if round_count >= max_rounds:
        print(f"{Fore.RED}Simulation timed out.")

async def run_demo():
    print(f"{Fore.GREEN}Starting MAVVE E2E Simulator...")
    
    # Generate a few orders (force high high_risk ratio for demo)
    orders = await generate_orders(count=3, high_risk_ratio=0.8)
    
    async with SessionLocal() as db:
        for order, user in orders:
            await process_order(order, user, db)

if __name__ == "__main__":
    asyncio.run(run_demo())
