from datetime import datetime
from tzlocal import get_localzone


def greetings():
    """Greet a user or doctor based on the current time in the system's local timezone."""
    local_tz = get_localzone()
    
    local_time = datetime.now(local_tz)
    hour = local_time.hour

    if 5 <= hour < 12:
        return "Good Morning!"
    elif 12 <= hour < 16:
        return "Good Afternoon!"
    elif 16 <= hour < 22:
        return "Good Evening!"
    else:
        return "Good Night!"
    

def profile_completion(data):
    """Calculate profile completion percentage"""
    total_fields = 0
    filled_fields = 0

    def count_fields(obj):
        nonlocal total_fields, filled_fields
        if isinstance(obj, dict):
            for value in obj.values():
                count_fields(value)
        elif isinstance(obj, list):
            for item in obj:
                count_fields(item)
        else:
            total_fields += 1
            if obj is not None and obj != "":
                filled_fields += 1

    count_fields(data)
    
    if total_fields == 0:
        return 0
    
    completion_percentage = (filled_fields / total_fields) * 100
    return round(completion_percentage, 2)
