# Doodle: Voice-Controlled AI Desktop Assistant

## 🧠 Overview
Doodle is a custom-built voice-controlled desktop assistant designed to help with everyday tasks using speech. It features:

- Wake-word detection ("Hey Doodle")
- Voice command interpretation
- Text-to-speech responses
- GUI chat interface
- Modes like Note Mode, Music Mode
- Calendar integration (reminders/events)
- Email reading
- Wikipedia search
- Memory module
- Weather updates

---

## 🌟 Key Features

### 🗣️ Wake Word Activation
- Wake word: **"Hey Doodle"**
- Powered by [Porcupine](https://picovoice.ai/platform/porcupine/)
- Listens continuously when `Start Listening` is active

### 📝 Note Mode (CRUD)
- **Create**: "Create a new note"
- **Read**: "Read note shopping"
- **Rename**: "Rename note shopping to groceries"
- **Delete**: "Delete note groceries"
- **Delete all**: "Delete all notes"
- **List**: "List my notes"
- Activated with: `Enter note mode`
- Exited with: `Exit note mode`

### 🎵 Music Mode (Spotify)
- Control music: Play, pause, next, previous, now playing
- Activated with: `Enter music mode`
- Exited with: `Exit music mode`

### 📅 Google Calendar Integration
- Add reminders: "Create a reminder tomorrow at 2:00 p.m."
- Delete reminders: "Delete reminder meeting"
- Event lookup: "What are my events tomorrow?"

### 📧 Email Reading
- "Read emails" or "Check my inbox"
- Reads latest Gmail messages via API

### 🔍 Internet Search
- Wikipedia queries: "What is quantum computing?"
- Personal memory: "Remember my birthday is June 29th"
- Recall: "What is my birthday?"
- Forget: "Forget my birthday"

### ☁️ Weather Updates
- Ask: "Will it rain today?", "What is the temperature?"

---

## 📊 Architecture

- `doodle.py`: GUI interface built with Tkinter
- `handle_user_input.py`: Routes commands to appropriate functions
- `main.py`: Console version for testing
- `utils/`
  - `voice_input.py`: Speech-to-text
  - `voice_engine.py`: Text-to-speech
  - `wake_word.py`: Wake word listening
  - `note_manager.py`: Local CRUD operations for notes
  - `google_calendar.py`: Calendar interaction
  - `email_manager.py`: Gmail reader
  - `web_search.py`: Wikipedia queries
  - `memory.py`: Persistent user facts
  - `weather.py`: Weather API wrapper

---

## 🛠️ Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```
- Libraries: `speechrecognition`, `pvporcupine`, `pyaudio`, `openai`, `google-api-python-client`, `tkinter`, `playsound`, etc.

### 2. Environment Variables
Create `config.env` and add:
```
OPENAI_API_KEY=your-openai-key
PORCUPINE_ACCESS_KEY=your-porcupine-key
```

### 3. Add Wake Word File
- Place `Hey-Doodle_en_windows_v3_0_0.ppn` at your desired path
- Update the path in `wake_word.py`

---

## 🚀 Launching the Assistant

### GUI Mode
```bash
python doodle.py
```

### Terminal Mode (for debugging)
```bash
python main.py
```

---

## ✨ Highlights
- Real-time speech interaction
- Multi-turn conversation support
- Friendly GUI with dark mode toggle
- Modular and extensible Python architecture
- Offline wake word support (no cloud latency)

---

## 📄 Credits
Created by **Satvik Jonnalagadda**, M.S. Computer Science @ University at Buffalo

With love for AI + UX + voice interfaces ✨

---

## 📲 Future Work
- Add language translation mode
- Add GUI note editor
- Add local file operations (File Mode)
- Add multi-lingual wake word support
- Push to cloud for multi-device sync

