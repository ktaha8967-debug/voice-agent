# Local Voice AI Agent

A 100% free, self-hosted, offline Voice AI Agent built from scratch. This project uses open-source tools exclusively and requires absolutely no paid services, no API keys, and no cloud providers.

## Architecture

```text
[ User Microphone ] 
        | (WebSocket Streaming)
        v
[ FastAPI Backend ]
        | 
        |-- 1. STT: faster-whisper (Whisper.cpp optimized for Python) -> Converts speech to text.
        | 
        |-- 2. DB: SQLite (Local) -> Stores conversation history and manages session memory.
        |
        |-- 3. LLM: Ollama (Llama 3 / Mistral / Gemma) -> Generates response based on transcript and history.
        |
        |-- 4. TTS: Piper TTS -> Synthesizes natural-sounding voice from LLM text.
        v
[ User Speaker ] (Real-time Audio playback)
```

### Components Explanation

1. **Frontend (`frontend/`)**: 
   - A simple web interface using vanilla HTML, CSS, and JS. 
   - Captures microphone audio via `MediaRecorder` API and streams it over WebSockets.
   - Plays back incoming audio buffers from the server.
   - Maintains a push-to-talk or toggle-to-talk interface and displays live transcripts.

2. **Backend (`main.py` & `backend/`)**: 
   - **FastAPI**: Manages WebSocket connections and serves the frontend. Handles asynchronous streams.
   - **STT (`backend/stt.py`)**: Uses `faster-whisper` for fast local inference of Whisper models. Processes incoming audio chunks and returns text.
   - **LLM (`backend/llm.py`)**: Connects to a locally running `Ollama` instance. Sends system prompts, chat history, and the new user transcript to generate intelligent text responses.
   - **TTS (`backend/tts.py`)**: Uses `piper-tts`, an extremely fast, high-quality local text-to-speech engine. Converts the LLM's text into raw audio streams.
   - **Database & Session (`backend/db.py`, `backend/session_manager.py`)**: SQLite tracks session IDs, messages, and handles memory so the LLM remembers previous turns.

### Installation Guide

#### Prerequisites
1. **Python 3.10+** installed.
2. **Ollama** installed on your system (Download from https://ollama.com).
3. (Optional but recommended) Build tools / C++ compiler for certain python dependencies.

#### Step-by-Step Setup

1. **Install Ollama Model**:
   Open a terminal and download your preferred model:
   ```bash
   ollama run llama3
   ```
   *(Ensure Ollama is running in the background).*

2. **Setup Python Virtual Environment**:
   ```bash
   cd "C:\Users\IC\Desktop\Voice agent"
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download Piper TTS Voice Model**:
   By default, the code will attempt to download a small English model (e.g., `en_US-lessac-medium`).

#### Running the Project
1. Start Ollama (if not already running as a service).
2. Activate your virtual environment.
3. Run the backend server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
4. Open your browser and navigate to `http://localhost:8000`.

#### Testing the Project
1. Allow microphone access in your browser.
2. Click "Start Conversation".
3. Speak into your microphone.
4. The UI will show your transcribed text, and you will hear the AI's response shortly after.

### Optimization Methods
- **Quantization**: Models for STT and LLM are quantized (e.g., INT8/INT4) for faster inference on CPUs and lower VRAM usage on GPUs.
- **Streaming**: Future iterations can implement token-by-token streaming from the LLM directly into the TTS engine to lower Time-to-First-Byte (TTFB).
- **VAD (Voice Activity Detection)**: Implementing a VAD like Silero-VAD before STT can significantly reduce empty audio processing.

### Deployment Guide (Local Network)
To access this from another device on your local network:
1. Run uvicorn bound to `0.0.0.0` (done by default in the run command above).
2. Access the site via `http://<your-local-ip>:8000`. 
*(Note: Browsers require HTTPS for microphone access on non-localhost IPs. For local network mobile testing, you will need to set up a local SSL certificate or use tools like ngrok/localtunnel for a secure tunnel, though that technically uses an external service).*

### Future Improvements
1. Implement real-time barge-in (interruption handling) by aborting LLM/TTS generation when the WebSocket receives new high-volume audio.
2. Add Silero VAD to locally detect speech vs. silence.
3. Support continuous streaming STT rather than chunked STT.
