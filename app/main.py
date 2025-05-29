from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .services.voice_chat import VoiceChat
import json
import base64
import os
import asyncio
import logging

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Store active voice chat sessions
active_sessions = {}

# Configure logging (prints to stdout)
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
)

@app.get("/")
async def root():
    return FileResponse("app/static/index.html")

@app.websocket("/ws/voice-chat/{client_id}")
async def voice_chat_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    logging.info(f"[BotWot][Session:{client_id}] WebSocket connection opened")
    loop = asyncio.get_event_loop()

    try:
        # Initialize voice chat
        voice_chat = VoiceChat()
        active_sessions[client_id] = voice_chat

        # --- SAFE CALLBACKS FOR ELEVENLABS ---
        def on_agent_response(response):
            logging.info(f"[BotWot][Session:{client_id}] Agent response: {response}")
            asyncio.run_coroutine_threadsafe(
                websocket.send_json({
                    "type": "agent_response",
                    "text": response
                }),
                loop
            )

        def on_user_transcript(transcript):
            logging.info(f"[BotWot][Session:{client_id}] User transcript: {transcript}")
            asyncio.run_coroutine_threadsafe(
                websocket.send_json({
                    "type": "user_transcript",
                    "text": transcript
                }),
                loop
            )

        # Start conversation
        conversation = voice_chat.start_conversation(
            on_agent_response=on_agent_response,
            on_user_transcript=on_user_transcript
        )

        # Main WebSocket loop
        while True:
            data = await websocket.receive_json()
            logging.debug(f"[BotWot][Session:{client_id}] Received data: {data}")

            if data["type"] == "audio":
                # Only log if needed, since audio is handled by DefaultAudioInterface
                pass
            elif data["type"] == "stop":
                logging.info(f"[BotWot][Session:{client_id}] Stop received, ending session")
                voice_chat.stop_conversation()
                break

    except WebSocketDisconnect:
        logging.warning(f"[BotWot][Session:{client_id}] WebSocket disconnected by client")
        if client_id in active_sessions:
            active_sessions[client_id].stop_conversation()
            del active_sessions[client_id]
    except Exception as e:
        logging.error(f"[BotWot][Session:{client_id}] ERROR: {str(e)}", exc_info=True)
        if client_id in active_sessions:
            active_sessions[client_id].stop_conversation()
            del active_sessions[client_id]
    finally:
        logging.info(f"[BotWot][Session:{client_id}] Session cleanup complete")

