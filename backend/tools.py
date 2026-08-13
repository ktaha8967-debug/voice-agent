import datetime

class Tools:
    @staticmethod
    def get_time():
        """Returns the current local time."""
        return f"The current time is {datetime.datetime.now().strftime('%H:%M:%S')}."

    @staticmethod
    def get_date():
        """Returns today's date."""
        return f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}."

    @staticmethod
    def weather_dummy(location: str):
        """Simulates a weather check."""
        return f"The weather in {location} is currently clear and 22 degrees Celsius (simulated)."

TOOL_MAP = {
    "get_time": Tools.get_time,
    "get_date": Tools.get_date,
    "get_weather": Tools.weather_dummy
}

TOOL_DEFINITIONS = [
    {
        "name": "get_time",
        "description": "Get the current time",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "get_date",
        "description": "Get today's date",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "The city name"}
            },
            "required": ["location"]
        }
    }
]
