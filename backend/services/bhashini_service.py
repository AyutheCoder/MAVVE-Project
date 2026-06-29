"""
Bhashini Integration Service.
Handles ASR (Speech-to-Text), NMT (Machine Translation), and TTS (Text-to-Speech)
using the Bhashini API for vernacular Indian languages.
"""

import asyncio
import io
import os
import httpx
import base64
import structlog
from typing import Dict, Any, Optional
from pydub import AudioSegment

from config import settings

logger = structlog.get_logger()

# Supported Vernacular Languages
SUPPORTED_LANGUAGES = ["hi", "mr", "bn", "ta", "te", "kn", "gu", "en"]

class BhashiniService:
    def __init__(self, api_key: str = None, mock_mode: bool = True):
        self.api_key = api_key or os.getenv("BHASHINI_API_KEY", "dummy_key")
        self.mock_mode = mock_mode
        self.base_url = "https://dhruva-api.bhashini.gov.in/services/inference"
        
        # In a real setup, pipeline IDs are fetched via compute_pipeline
        self.pipeline_ids = {
            "asr": "asr-pipeline-id-mock",
            "nmt": "nmt-pipeline-id-mock",
            "tts": "tts-pipeline-id-mock"
        }
        
    async def compute_pipeline(self) -> Dict[str, str]:
        """
        Fetches the active pipeline IDs from Bhashini.
        Usually called once during startup and cached.
        """
        if self.mock_mode:
            logger.info("bhashini_mock_compute_pipeline")
            await asyncio.sleep(0.2)
            return self.pipeline_ids
            
        # Real implementation would call Bhashini catalog API here
        return self.pipeline_ids

    def _convert_audio_format(self, audio_bytes: bytes, from_format: str, to_format: str) -> bytes:
        """
        Converts audio format (e.g., OGG/Opus from WhatsApp to WAV for Bhashini).
        """
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=from_format)
            
            # Bhashini typically prefers 16kHz mono WAV
            if to_format == "wav":
                audio = audio.set_frame_rate(16000).set_channels(1)
                
            out_buffer = io.BytesIO()
            audio.export(out_buffer, format=to_format)
            return out_buffer.getvalue()
        except Exception as e:
            logger.error("audio_conversion_failed", error=str(e))
            # Return original if pydub fails (e.g., missing ffmpeg in local environment)
            return audio_bytes

    async def speech_to_text(self, audio_bytes: bytes, source_lang: str) -> str:
        """
        ASR: Converts voice audio (bytes) into vernacular text.
        """
        if source_lang not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Language {source_lang} not supported.")
            
        logger.info("bhashini_asr_start", lang=source_lang, size=len(audio_bytes))
        
        # Convert OGG from WhatsApp to WAV for Bhashini
        wav_bytes = self._convert_audio_format(audio_bytes, from_format="ogg", to_format="wav")
        audio_b64 = base64.b64encode(wav_bytes).decode('utf-8')
        
        if self.mock_mode:
            await asyncio.sleep(0.4) # Simulate latency
            mock_transcriptions = {
                "hi": "हाँ, मैं घर पर हूँ।",
                "mr": "हो, मी घरीच आहे.",
                "bn": "হ্যাঁ, আমি বাড়িতে আছি।"
            }
            result = mock_transcriptions.get(source_lang, "Yes, I am at home.")
            logger.info("bhashini_asr_success", result=result)
            return result
            
        # Real HTTPX Call Implementation
        headers = {"Authorization": self.api_key}
        payload = {
            "pipelineTasks": [{"taskType": "asr", "config": {"language": {"sourceLanguage": source_lang}}}],
            "inputData": {"audio": [{"audioContent": audio_b64}]}
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.base_url + "/pipeline", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["pipelineResponse"][0]["output"][0]["source"]

    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        NMT: Translates text from source language to target language.
        """
        logger.info("bhashini_nmt_start", source=source_lang, target=target_lang, text=text)
        
        if self.mock_mode:
            await asyncio.sleep(0.2)
            if target_lang == "en":
                result = "Yes, I am at home."
            else:
                # Mock translation back to vernacular
                result = f"[Translated to {target_lang}]: {text}"
            logger.info("bhashini_nmt_success", result=result)
            return result
            
        # Real HTTPX Call Implementation
        headers = {"Authorization": self.api_key}
        payload = {
            "pipelineTasks": [{"taskType": "translation", "config": {"language": {"sourceLanguage": source_lang, "targetLanguage": target_lang}}}],
            "inputData": {"input": [{"source": text}]}
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.base_url + "/pipeline", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["pipelineResponse"][0]["output"][0]["target"]

    async def text_to_speech(self, text: str, target_lang: str, gender: str = "female") -> bytes:
        """
        TTS: Converts vernacular text into audio bytes (WAV/Base64 -> OGG).
        """
        logger.info("bhashini_tts_start", lang=target_lang, gender=gender, text_length=len(text))
        
        if self.mock_mode:
            await asyncio.sleep(0.5)
            # Create a mock audio byte array (silent OGG or just random bytes for testing)
            mock_ogg_bytes = b"OggS\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00mock_audio_content"
            logger.info("bhashini_tts_success", size=len(mock_ogg_bytes))
            return mock_ogg_bytes
            
        # Real HTTPX Call Implementation
        headers = {"Authorization": self.api_key}
        payload = {
            "pipelineTasks": [{"taskType": "tts", "config": {"language": {"sourceLanguage": target_lang}, "gender": gender}}],
            "inputData": {"input": [{"source": text}]}
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.base_url + "/pipeline", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            audio_b64 = data["pipelineResponse"][0]["audio"][0]["audioContent"]
            wav_bytes = base64.b64decode(audio_b64)
            
            # Convert WAV back to OGG for WhatsApp
            ogg_bytes = self._convert_audio_format(wav_bytes, from_format="wav", to_format="ogg")
            return ogg_bytes


    async def run_multimodal_loop(self, user_audio_ogg: bytes, user_lang: str, llm_processor_func) -> bytes:
        """
        The complete Voice-to-Voice Multimodal Pipeline.
        1. ASR: User Voice -> Vernacular Text
        2. NMT: Vernacular Text -> English Text
        3. LLM: Process English Text (via provided function)
        4. NMT: English Agent Reply -> Vernacular Text
        5. TTS: Vernacular Text -> Agent Voice
        """
        logger.info("multimodal_loop_started", user_lang=user_lang)
        
        # 1. ASR
        vernacular_text = await self.speech_to_text(user_audio_ogg, source_lang=user_lang)
        
        # 2. Translate to English for LLM
        if user_lang != "en":
            english_input = await self.translate(vernacular_text, source_lang=user_lang, target_lang="en")
        else:
            english_input = vernacular_text
            
        # 3. LLM Processing (Assuming function returns an English string)
        english_reply = await llm_processor_func(english_input)
        
        # 4. Translate back to Vernacular
        if user_lang != "en":
            vernacular_reply = await self.translate(english_reply, source_lang="en", target_lang=user_lang)
        else:
            vernacular_reply = english_reply
            
        # 5. TTS
        agent_audio_ogg = await self.text_to_speech(vernacular_reply, target_lang=user_lang)
        
        logger.info("multimodal_loop_completed", user_lang=user_lang)
        return agent_audio_ogg

    @staticmethod
    def detect_language(user_profile_lang: Optional[str], default_lang: str = "hi") -> str:
        """
        Helper to determine the language to use.
        Can be expanded to use Bhashini's language detection API on the first audio.
        """
        if user_profile_lang and user_profile_lang in SUPPORTED_LANGUAGES:
            return user_profile_lang
        return default_lang


# ── Standalone Test ──────────────────────────────────────
if __name__ == "__main__":
    async def run_test():
        print("--- Bhashini Multimodal Pipeline Test ---")
        service = BhashiniService(mock_mode=True)
        
        # Mock LLM processor
        async def mock_llm(english_text: str) -> str:
            print(f"[LLM Received]: {english_text}")
            await asyncio.sleep(0.5)
            reply = "Great, I have confirmed your address. The package will arrive tomorrow."
            print(f"[LLM Replied]: {reply}")
            return reply
            
        # Mock incoming WhatsApp audio
        mock_in_audio = b"dummy_ogg_bytes_from_whatsapp"
        user_lang = "hi"
        
        print("\nStarting pipeline...")
        out_audio = await service.run_multimodal_loop(mock_in_audio, user_lang, mock_llm)
        
        print(f"\n[Final Output Audio Size]: {len(out_audio)} bytes")
        print("Pipeline executed successfully!")

    asyncio.run(run_test())
