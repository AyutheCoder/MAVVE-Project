"""
WhatsApp Simulator API & Web UI.
A local mock interface for testing the MAVVE multimodal agent loop without Meta API.
"""

from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
import structlog
from typing import Dict, List, Any
from datetime import datetime

from api.webhooks import process_incoming_message

logger = structlog.get_logger()
router = APIRouter()

# In-memory store for simulator chat history
_SIMULATOR_CHATS: Dict[str, List[Dict[str, Any]]] = {}

# We patch the WhatsApp service to route mock messages to our simulator UI
from services.whatsapp_service import whatsapp

original_send_request = whatsapp._send_request

async def mock_send_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Intercepts WhatsApp outbound messages and routes them to the simulator."""
    phone = payload.get("to")
    if phone not in _SIMULATOR_CHATS:
        _SIMULATOR_CHATS[phone] = []
        
    msg_type = payload.get("type", "text")
    content = ""
    
    if msg_type == "text":
        content = payload["text"]["body"]
    elif msg_type == "interactive":
        content = payload["interactive"]["body"]["text"] + "\n[Buttons: " + ", ".join([b["reply"]["title"] for b in payload["interactive"]["action"]["buttons"]]) + "]"
        
    _SIMULATOR_CHATS[phone].append({
        "sender": "agent",
        "text": content,
        "type": msg_type,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    logger.info("simulator_intercepted_outbound", phone=phone, text=content)
    return {"messages": [{"id": "mock_msg_id_123"}]}

# Apply the patch if we are in mock mode
if whatsapp.is_mock:
    whatsapp._send_request = mock_send_request


@router.get("/", response_class=HTMLResponse)
async def get_simulator_ui():
    """Returns the Simulator Web UI."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MAVVE WhatsApp Simulator</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #e5ddd5; margin: 0; padding: 20px; display: flex; justify-content: center; }
            .chat-container { width: 400px; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); display: flex; flex-direction: column; height: 80vh; }
            .header { background: #075e54; color: white; padding: 15px; font-weight: bold; text-align: center; }
            .chat-box { flex: 1; padding: 15px; overflow-y: auto; background-image: url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png'); display: flex; flex-direction: column; gap: 10px; }
            .msg { max-width: 80%; padding: 8px 12px; border-radius: 8px; font-size: 14px; line-height: 1.4; position: relative; }
            .msg.user { background: #dcf8c6; align-self: flex-end; border-top-right-radius: 0; }
            .msg.agent { background: #ffffff; align-self: flex-start; border-top-left-radius: 0; box-shadow: 0 1px 1px rgba(0,0,0,0.1); }
            .msg-time { font-size: 10px; color: #999; text-align: right; margin-top: 4px; }
            .input-area { display: flex; padding: 10px; background: #f0f0f0; }
            input[type="text"] { flex: 1; padding: 10px; border: none; border-radius: 20px; outline: none; }
            button { background: #128c7e; color: white; border: none; border-radius: 50%; width: 40px; height: 40px; margin-left: 10px; cursor: pointer; }
            .phone-selector { padding: 10px; background: #eee; text-align: center; border-bottom: 1px solid #ddd; }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="header">MAVVE Simulator</div>
            <div class="phone-selector">
                <input type="text" id="phoneInput" value="+919876543210" style="text-align:center; padding:5px; border-radius:5px; border:1px solid #ccc;">
            </div>
            <div class="chat-box" id="chatBox"></div>
            <div class="input-area">
                <input type="text" id="msgInput" placeholder="Type a message or /voice [text]" autocomplete="off" onkeypress="handleEnter(event)">
                <button onclick="sendMessage()">▶</button>
            </div>
        </div>
        
        <script>
            let currentPhone = document.getElementById("phoneInput").value;
            
            document.getElementById("phoneInput").addEventListener("change", (e) => {
                currentPhone = e.target.value;
                document.getElementById("chatBox").innerHTML = "";
            });
            
            function addMessageToUI(text, sender, time) {
                const chatBox = document.getElementById("chatBox");
                const msgDiv = document.createElement("div");
                msgDiv.className = "msg " + sender;
                msgDiv.innerHTML = text + `<div class="msg-time">${time}</div>`;
                chatBox.appendChild(msgDiv);
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            async function sendMessage() {
                const input = document.getElementById("msgInput");
                const text = input.value.trim();
                if (!text) return;
                
                let isVoice = false;
                let actualText = text;
                if(text.startsWith("/voice ")) {
                    isVoice = true;
                    actualText = text.replace("/voice ", "");
                }
                
                input.value = "";
                const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                addMessageToUI(isVoice ? "🎤 " + actualText : actualText, "user", time);
                
                await fetch("/api/simulator/send", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        phone: currentPhone,
                        text: actualText,
                        type: isVoice ? "audio" : "text"
                    })
                });
            }
            
            function handleEnter(e) {
                if (e.key === "Enter") sendMessage();
            }
            
            // Poll for agent messages
            setInterval(async () => {
                const resp = await fetch(`/api/simulator/poll?phone=${encodeURIComponent(currentPhone)}`);
                const data = await resp.json();
                if (data.messages) {
                    data.messages.forEach(msg => {
                        addMessageToUI(msg.text, "agent", msg.timestamp);
                    });
                }
            }, 2000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.post("/send")
async def simulator_send_message(data: dict, background_tasks: BackgroundTasks):
    """Receives a message from the simulator UI and pushes it to webhooks logic."""
    phone = data.get("phone")
    text = data.get("text")
    msg_type = data.get("type", "text")
    
    logger.info("simulator_inbound", phone=phone, text=text, type=msg_type)
    
    mock_payload = {
        "from": phone,
        "type": msg_type
    }
    
    if msg_type == "text":
        mock_payload["text"] = {"body": text}
    elif msg_type == "audio":
        # Simulating audio processing bypassing Bhashini transcription logic for UI simplicity
        # We just act like Bhashini transcribed it to 'text'
        mock_payload["audio"] = {"id": "mock_audio_id"}
        # We override the webhook audio behavior to just use the text we passed
        mock_payload["type"] = "text"
        mock_payload["text"] = {"body": text}
        
    # Dispatch to webhook logic in background
    background_tasks.add_task(process_incoming_message, phone, mock_payload)
    return {"status": "ok"}

@router.get("/poll")
async def simulator_poll(phone: str):
    """Simulator UI polls this to get agent replies."""
    if phone in _SIMULATOR_CHATS and len(_SIMULATOR_CHATS[phone]) > 0:
        msgs = _SIMULATOR_CHATS[phone]
        _SIMULATOR_CHATS[phone] = [] # Clear after fetching
        return {"messages": msgs}
    return {"messages": []}
