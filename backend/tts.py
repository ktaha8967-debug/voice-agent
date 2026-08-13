import os
import tempfile
import subprocess
import urllib.request

class TTSManager:
    def __init__(self, model_name="en_US-lessac-medium"):
        self.models_dir = os.path.join(os.getcwd(), "models")
        self.model_path = os.path.join(self.models_dir, f"{model_name}.onnx")
        self.config_path = f"{self.model_path}.json"
        self._ensure_model_exists(model_name)

    def _ensure_model_exists(self, model_name):
        os.makedirs(self.models_dir, exist_ok=True)
        if not os.path.exists(self.model_path):
            print(f"Downloading Piper TTS model '{model_name}' to {self.model_path}...")
            # For simplicity, hardcoded to download lessac medium if missing.
            url_onnx = f"https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/{model_name}.onnx?download=true"
            url_json = f"https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/{model_name}.onnx.json?download=true"
            urllib.request.urlretrieve(url_onnx, self.model_path)
            urllib.request.urlretrieve(url_json, self.config_path)
            print("TTS Model download complete.")
        else:
            print("TTS Model already exists.")

    def text_to_audio_bytes(self, text: str) -> bytes:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_wav_path = temp_audio.name
            
        command = [
            "python", "-m", "piper",
            "--model", self.model_path,
            "--output_file", temp_wav_path
        ]
        
        try:
            # We pass text via standard input
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            process.communicate(input=text.encode("utf-8"))
            
            with open(temp_wav_path, "rb") as f:
                audio_data = f.read()
            return audio_data
        except Exception as e:
            print(f"TTS Error: {e}")
            return b""
        finally:
            if os.path.exists(temp_wav_path):
                os.remove(temp_wav_path)
