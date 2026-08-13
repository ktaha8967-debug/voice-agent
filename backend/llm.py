
class LLMManager:
    def __init__(self, model_name=None):
        print("LLM Initialized (Placeholder Mode - Ollama Removed)")

    def generate_response(self, messages: list) -> str:
        user_query = messages[-1]['content'].lower()
        
        # Simple rule-based logic for testing
        if "hello" in user_query or "hi" in user_query:
            return "Hello! I am your local voice assistant. How can I help you today?"
        elif "time" in user_query:
            import datetime
            return f"The current time is {datetime.datetime.now().strftime('%H:%M:%S')}."
        elif "who are you" in user_query:
            return "I am a lightweight voice AI running on your computer."
        else:
            return f"You said: {messages[-1]['content']}. I have received your message, but my heavy brain (Ollama) has been removed to save your PC's resources."
