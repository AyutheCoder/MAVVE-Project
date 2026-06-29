"""
WhatsApp Integration Service.
Handles sending and receiving messages via WhatsApp Cloud API.
"""

import httpx
import structlog
import os
from typing import List, Dict, Any, Optional
from config import settings

logger = structlog.get_logger()

class WhatsAppService:
    def __init__(self):
        self.access_token = os.getenv("WHATSAPP_TOKEN", "dummy_whatsapp_token")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_ID", "dummy_phone_id")
        self.base_url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}/messages"
        self.media_url = "https://graph.facebook.com/v17.0/"
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        self.is_mock = self.access_token == "dummy_whatsapp_token"

    async def _send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to send POST request to WhatsApp API."""
        if self.is_mock:
            logger.info("whatsapp_mock_send", payload=payload)
            # In mock mode, we could broadcast this to a WebSocket for the simulator UI
            return {"messages": [{"id": "mock_msg_id_123"}]}
            
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.base_url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def send_text_message(self, phone: str, text: str) -> Dict[str, Any]:
        """Send a plain text message."""
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"body": text}
        }
        return await self._send_request(payload)

    async def send_template_message(self, phone: str, template_name: str, params: List[Dict[str, str]]) -> Dict[str, Any]:
        """Send a template message (useful for 24h window re-engagement)."""
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "body",
                        "parameters": params
                    }
                ]
            }
        }
        return await self._send_request(payload)

    async def send_interactive_message(self, phone: str, body: str, buttons: List[Dict[str, str]]) -> Dict[str, Any]:
        """Send an interactive message with Quick Reply buttons (up to 3)."""
        formatted_buttons = [
            {"type": "reply", "reply": {"id": btn["id"], "title": btn["title"][:20]}}
            for btn in buttons[:3]
        ]
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body},
                "action": {"buttons": formatted_buttons}
            }
        }
        return await self._send_request(payload)

    async def send_audio_message(self, phone: str, audio_link_or_id: str, is_id: bool = False) -> Dict[str, Any]:
        """Send a voice note (audio message)."""
        audio_payload = {"id": audio_link_or_id} if is_id else {"link": audio_link_or_id}
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "audio",
            "audio": audio_payload
        }
        return await self._send_request(payload)

    async def download_media(self, media_id: str) -> bytes:
        """Download incoming voice notes or images using media_id."""
        if self.is_mock:
            logger.info("whatsapp_mock_download_media", media_id=media_id)
            return b"mock_media_bytes"
            
        async with httpx.AsyncClient() as client:
            # 1. Get Media URL
            resp = await client.get(f"{self.media_url}{media_id}", headers=self.headers)
            resp.raise_for_status()
            url = resp.json().get("url")
            
            # 2. Download Media bytes
            media_resp = await client.get(url, headers=self.headers)
            media_resp.raise_for_status()
            return media_resp.content

# Singleton instance
whatsapp = WhatsAppService()
