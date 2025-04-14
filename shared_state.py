# shared_state.py

class AppState:
    def __init__(self):
        self.note_mode = False
        self.music_mode = False
        self.session_memory = {
            "last_subject": None,
            "last_response": None
        }

# Create a single instance that will be shared across all modules
app_state = AppState()