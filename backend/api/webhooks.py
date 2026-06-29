"""
WhatsApp Webhook Handlers.
Receives incoming messages and handles Meta webhook verification.
"""

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
import structlog
import os
from langchain_core.messages import HumanMessage
from sqlalchemy import update

from services.whatsapp_service import whatsapp
from services.session_manager import SessionManager
from agents.orchestrator import app as langgraph_app
from services.bhashini_service import BhashiniService
from db.database import AsyncSessionLocal
from models.order import Order

logger = structlog.get_logger()
router = APIRouter()

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "mavve_webhook_secret")
bhashini = BhashiniService(mock_mode=True)

@router.get("/whatsapp")
async def verify_webhook(request: Request):
    """Handles Meta's webhook verification challenge."""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info("webhook_verified")
            return int(challenge)
        else:
            raise HTTPException(status_code=403, detail="Verification failed")
    raise HTTPException(status_code=400, detail="Missing parameters")


async def process_incoming_message(phone: str, message_data: dict):
    """
    Background task to process an incoming WhatsApp message through LangGraph.
    Includes Bhashini voice support and terminal state DB updating.
    """
    logger.info("processing_incoming_message", phone=phone)
    
    session = SessionManager.get_session(phone)
    if not session:
        logger.warning("no_active_session", phone=phone)
        return

    msg_type = message_data.get("type")
    user_input = ""
    is_voice = False
    
    if msg_type == "text":
        user_input = message_data["text"]["body"]
    elif msg_type == "interactive":
        interactive = message_data["interactive"]
        if interactive["type"] == "button_reply":
            user_input = interactive["button_reply"]["title"]
    elif msg_type == "audio":
        audio_id = message_data["audio"]["id"]
        logger.info("received_audio", audio_id=audio_id)
        
        # 1. Download audio from WhatsApp
        audio_bytes = await whatsapp.download_media(audio_id)
        
        # 2. Use Bhashini to transcribe
        user_lang = session["state"].get("user_language", "hi")
        user_input = await bhashini.speech_to_text(audio_bytes, source_lang=user_lang)
        is_voice = True
    else:
        logger.info("unsupported_message_type", type=msg_type)
        return

    # Update LangGraph state with new Human message
    state = session["state"]
    state["messages"].append(HumanMessage(content=user_input))
    
    try:
        logger.info("resuming_langgraph", phone=phone)
        for event in langgraph_app.stream(state):
            for key, value in event.items():
                if value and "messages" in value and value["messages"]:
                    latest_msg = str(value["messages"][-1].content)
                    
                    if is_voice:
                        # Convert agent reply to voice using Bhashini TTS
                        user_lang = session["state"].get("user_language", "hi")
                        if user_lang != "en":
                            latest_msg = await bhashini.translate(latest_msg, source_lang="en", target_lang=user_lang)
                        audio_ogg_bytes = await bhashini.text_to_speech(latest_msg, target_lang=user_lang)
                        mock_link = "https://mock.cdn/agent_reply.ogg"
                        await whatsapp.send_audio_message(phone, mock_link)
                    else:
                        await whatsapp.send_text_message(phone, latest_msg)
                    
                state.update(value)
                
        # Save updated state
        SessionManager.update_session_state(phone, state)
        
        # Handle Terminal State
        if state.get("final_disposition"):
            logger.info("session_terminal", phone=phone, disposition=state["final_disposition"])
            
            # Update Database
            async with AsyncSessionLocal() as db:
                order_id = state["order_id"]
                new_status = "VALIDATED" if state["final_disposition"] == "DISPATCH" else "CANCELLED"
                
                stmt = update(Order).where(Order.order_id == order_id).values(status=new_status)
                await db.execute(stmt)
                await db.commit()
                logger.info("order_status_updated", order_id=order_id, new_status=new_status)
            
            # Clear session
            SessionManager.clear_session(phone)
            
    except Exception as e:
        logger.error("langgraph_execution_failed", error=str(e))
        await whatsapp.send_text_message(phone, "Sorry, I encountered an error processing that.")


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """Receives incoming messages and status updates from WhatsApp."""
    data = await request.json()
    logger.info("webhook_received", data=data)

    if data.get("object") == "whatsapp_business_account":
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                
                # Handle status updates (sent, delivered, read)
                if "statuses" in value:
                    for status in value["statuses"]:
                        logger.info("message_status_update", status=status["status"], recipient=status["recipient_id"])
                
                # Handle incoming messages
                if "messages" in value:
                    for message in value["messages"]:
                        phone = message["from"]
                        background_tasks.add_task(process_incoming_message, phone, message)
                        
        return {"status": "ok"}
        
    raise HTTPException(status_code=404)
