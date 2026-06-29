"""
WhatsApp API Mock Server
Mimics the Meta WhatsApp Cloud API and provides a local UI to view messages.
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn
from datetime import datetime

app = FastAPI(title="WhatsApp Mock API")

# In-memory storage for messages sent by the backend
messages_db = []

@app.post("/v19.0/{phone_number_id}/messages")
async def send_message(phone_number_id: str, request: Request):
    """
    Mock endpoint that the backend calls to send a WhatsApp message.
    """
    data = await request.json()
    
    # Parse the message
    to = data.get("to")
    msg_type = data.get("type")
    
    content = "[Unsupported Type]"
    if msg_type == "text":
        content = data.get("text", {}).get("body", "")
    elif msg_type == "template":
        content = f"[Template: {data.get('template', {}).get('name')}]"
    elif msg_type == "interactive":
        content = f"[Interactive Button Menu]"
    elif msg_type == "audio":
        content = f"[Audio Voice Note]"
        
    messages_db.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "to": to,
        "type": msg_type,
        "content": content,
        "direction": "outbound"
    })
    
    return {
        "messaging_product": "whatsapp",
        "contacts": [{"input": to, "wa_id": to}],
        "messages": [{"id": f"wamid.{datetime.now().timestamp()}"}]
    }

@app.get("/", response_class=HTMLResponse)
async def view_messages():
    """
    Simple Web UI to view intercepted outbound messages.
    """
    html = """
    <html>
        <head>
            <title>WhatsApp Mock UI</title>
            <style>
                body { font-family: system-ui; background: #0f172a; color: #f8fafc; padding: 2rem; }
                .msg { background: #1e293b; padding: 1rem; margin-bottom: 1rem; border-radius: 8px; border-left: 4px solid #3b82f6;}
                .meta { font-size: 0.8rem; color: #94a3b8; margin-bottom: 0.5rem; }
            </style>
            <meta http-equiv="refresh" content="3">
        </head>
        <body>
            <h1>📱 WhatsApp Mock API (Outbox)</h1>
            <p>Messages sent by MAVVE Backend:</p>
            <div id="messages">
    """
    
    for msg in reversed(messages_db):
        html += f"""
        <div class="msg">
            <div class="meta">To: {msg['to']} | Type: {msg['type']} | {msg['timestamp']}</div>
            <div>{msg['content']}</div>
        </div>
        """
        
    html += """
            </div>
        </body>
    </html>
    """
    return html

if __name__ == "__main__":
    print("Starting WhatsApp Mock Server on port 8080...")
    print("View messages at: http://localhost:8080/")
    uvicorn.run(app, host="0.0.0.0", port=8080)
