import os
import uuid
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.db import init_db
from backend.session_manager import SessionManager
from backend.stt import STTManager
from backend.llm import LLMManager
from backend.tts import TTSManager
# from backend.wakeword import WakeWordManager

app = FastAPI(title="Advanced Local Voice AI Agent")

# Initialize managers globally
print("Initializing AI models...")
stt = STTManager(model_size="tiny.en")
llm = LLMManager() 
tts = TTSManager()
# ww = WakeWordManager()

# Global state to handle barge-in/interruptions
active_audio_tasks = {}

# Initialize Database
init_db()

# Mount Frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def get_index():
    return FileResponse("frontend/index.html")

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    session_manager = SessionManager(session_id=session_id)
    
    print(f"New WebSocket session started: {session_id}")
    
    try:
        while True:
            data = await websocket.receive_bytes()
            if not data:
                continue

            # BARGE-IN: If AI is talking and we get new audio, we could stop the current task
            if session_id in active_audio_tasks and not active_audio_tasks[session_id].done():
                print(f"[{session_id}] Barge-in detected! Stopping current AI response.")
                active_audio_tasks[session_id].cancel()

            # Process in background to allow continuous listening
            task = asyncio.create_task(process_voice_interaction(websocket, session_id, session_manager, data))
            active_audio_tasks[session_id] = task
                
    except WebSocketDisconnect:
        print(f"Client disconnected. Session: {session_id}")
    except Exception as e:
        print(f"WebSocket Error: {e}")

async def process_voice_interaction(websocket, session_id, session_manager, audio_data):
    import time
    try:
        # 1. STT
        start_stt = time.time()
        transcript = stt.transcribe_audio_bytes(audio_data)
        if not transcript:
            return
        
        print(f"[{session_id}] User: {transcript} (STT took {time.time()-start_stt:.2f}s)")
        session_manager.add_message("user", transcript)
        await websocket.send_text(json.dumps({"type": "transcript", "role": "user", "text": transcript}))

        # 2. LLM with Tools & RAG
        await websocket.send_text(json.dumps({"type": "processing_llm"}))
        start_llm = time.time()
        history = session_manager.get_history()
        ai_response = await asyncio.to_thread(llm.generate_response, history)
        
        if not ai_response:
            return

        print(f"[{session_id}] AI: {ai_response} (LLM took {time.time()-start_llm:.2f}s)")
        session_manager.add_message("assistant", ai_response)
        await websocket.send_text(json.dumps({"type": "transcript", "role": "assistant", "text": ai_response}))

        # 3. TTS
        start_tts = time.time()
        audio_response = await asyncio.to_thread(tts.text_to_audio_bytes, ai_response)
        
        if audio_response:
            print(f"[{session_id}] TTS completed in {time.time()-start_tts:.2f}s, sending {len(audio_response)} bytes")
            await websocket.send_text(json.dumps({"type": "audio_start"}))
            await websocket.send_bytes(audio_response)
        else:
            print(f"[{session_id}] TTS failed or returned no data.")

    except asyncio.CancelledError:
        print(f"[{session_id}] AI Task Cancelled (Barge-in).")
    except Exception as e:
        print(f"[{session_id}] Error in process_voice_interaction: {e}")
