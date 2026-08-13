from faster_whisper import WhisperModel
import tempfile
import os

class STTManager:
    def __init__(self, model_size="base.en"):
        print(f"Loading STT Model: {model_size} (faster-whisper)...")
        # CPU setup by default. In a real environment with CUDA, device="cuda"
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        print("STT Model loaded successfully.")

    def transcribe_audio_bytes(self, audio_bytes: bytes) -> str:
        # Frontend uses MediaRecorder which often produces webm
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_audio:
            temp_audio.write(audio_bytes)
            temp_path = temp_audio.name
            
        try:
            segments, info = self.model.transcribe(temp_path, beam_size=5)
            text = " ".join([segment.text for segment in segments])
            return text.strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
