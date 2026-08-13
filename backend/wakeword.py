import openwakeword
from openwakeword.model import Model
import numpy as np

class WakeWordManager:
    def __init__(self, model_path=None):
        # Default wake word: "hey jarvis" or similar standard ones in openwakeword
        if model_path:
            self.model = Model(wakeword_models=model_path, inference_framework="onnx") 
        else:
            self.model = Model(inference_framework="onnx")
        print("Wake Word Engine Initialized.")

    def detect(self, audio_data: np.ndarray) -> bool:
        """
        Expects 16kHz, 16-bit mono PCM audio
        """
        prediction = self.model.predict(audio_data)
        for wakeword, score in self.model.prediction_buffer.items():
            if score[-1] > 0.5: # Threshold
                print(f"Wake word detected: {wakeword}")
                return True
        return False
