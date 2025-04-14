import openai
from dotenv import load_dotenv
import os
import re
import webbrowser
from utils.voice_engine import speak
from datetime import datetime as dt, timedelta
from calendar import monthrange
from utils.voice_input import listen
from utils.google_calendar import get_events_between, add_event_to_calendar, delete_event_by_summary, get_events_for_day
from utils.email_manager import read_latest_emails
from utils.note_manager import save_note, delete_note_by_name, rename_note, delete_all_notes, list_all_notes, read_note_by_name
from utils.web_search import search_wikipedia
from utils import spotify_control
from utils import memory
from utils import weather
from utils.wake_word import WakeWordDetector
from shared_state import app_state

# Remove these lines from main.py:
# note_mode = False
# music_mode = False
# session_memory = {...}

# Then anywhere you used these variables, replace with:
# app_state.note_mode
# app_state.music_mode
# app_state.session_memory

load_dotenv("config.env")
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

'''note_mode = False
music_mode = False

session_memory = {
    "last_subject": None,
    "last_response": None
}'''

def get_response(prompt):
    if app_state.session_memory["last_subject"] and any(x in prompt.lower() for x in ["he", "she", "they", "it", "that", "this"]):
        full_prompt = f"Continue based on: {app_state.session_memory['last_subject']}. {prompt}"
    else:
        full_prompt = prompt
        app_state.session_memory["last_subject"] = prompt

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": full_prompt}]
    )
    reply = response.choices[0].message.content

    app_state.session_memory["last_response"] = reply

    if not any(x in prompt.lower() for x in ["he", "she", "they", "it", "that", "this"]):
        app_state.session_memory["last_subject"] = None
        app_state.session_memory["last_response"] = None

    return reply

def describe_desktop():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    files = os.listdir(desktop_path)
    if not files:
        return "Your Desktop is empty."

    descriptions = []
    for f in files[:10]:
        full_path = os.path.join(desktop_path, f)
        if os.path.isfile(full_path):
            modified_time = dt.fromtimestamp(os.path.getmtime(full_path))
            descriptions.append(f"{f} (last modified: {modified_time.strftime('%Y-%m-%d %H:%M')})")
        else:
            descriptions.append(f"{f} (folder)")

    return "Here's what I found on your Desktop:\n" + "\n".join(descriptions)

def parse_time_from_query(query):
    time_regex = r'(\d{1,2})(?::(\d{2}))?\s*(A\.M\.|P\.M\.|a\.m\.|p\.m\.)?'
    time_match = re.search(time_regex, query)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        am_pm = time_match.group(3)
        am_pm = am_pm.upper() if am_pm and am_pm.strip() else None
        return hour, minute, am_pm
    return None, None, None

def interpret_day(query):
    today = dt.today().date()
    if "tomorrow" in query:
        return today + timedelta(days=1)
    elif "today" in query:
        return today
    else:
        return today

def add_reminder(user_input):
    today = dt.today()
    hour, minute, am_pm = parse_time_from_query(user_input)
    if hour is None:
        speak("Sorry, I couldn't find a valid time in your request.")
        return
    if not am_pm:
        speak("Please say the full time including AM or PM.")
        return
    if am_pm == "P.M." and hour != 12:
        hour += 12
    elif am_pm == "A.M." and hour == 12:
        hour = 0
    date = interpret_day(user_input)
    target_time = dt.combine(date, dt.min.time()).replace(hour=hour, minute=minute)
    speak("What would you like me to remind you about?")
    task_description = listen()
    if not task_description or "sorry" in task_description.lower():
        speak("I didn't catch that. Reminder not added.")
        return
    add_event_to_calendar(task_description, target_time)
    speak(f"Your reminder for '{task_description}' has been set for {target_time.strftime('%Y-%m-%d %I:%M %p')}.")

def open_website(website_url):
    if not website_url.startswith("http"):
        website_url = "https://" + website_url
    try:
        webbrowser.open(website_url)
        speak(f"Opening {website_url}")
    except Exception as e:
        speak(f"Sorry, I couldn't open {website_url}. Error: {e}")

def open_application(app_name):
    try:
        if app_name.lower() == "vs code":
            os.system("code")
            speak("Opening Visual Studio Code")
        elif app_name.lower() == "chrome":
            os.system("start chrome")
            speak("Opening Google Chrome")
        else:
            speak(f"I don't know how to open {app_name}.")
    except Exception as e:
        speak(f"Sorry, I couldn't open {app_name}. Error: {e}")

def give_daily_briefing():
    speak("Here's your daily briefing:")
    today = dt.today().date()
    events = get_events_for_day(today)
    if events:
        speak("Here are your events for today.")
        for event in events:
            speak(event)
    else:
        speak("You have no events scheduled for today.")
    speak("Now checking your unread emails.")
    emails = read_latest_emails(max_results=3)
    if emails and "No new messages" not in emails[0]:
        for mail in emails:
            speak(mail)
    else:
        speak("You have no unread emails.")

def main():
    global note_mode, music_mode
    print("\U0001F399️Doodle is listening... Say 'stop' to quit.")
    while True:
        WakeWordDetector.listen_for_wake_word()
        print("🎤 Wake word detected!")
        user_input = listen(timeout=None)
        if not user_input:
            speak("I didn't hear anything. Please try again.")
            continue
        '''if "enter note mode" in user_input:
            note_mode = True
            speak("You're now in note mode. You can say create, read, rename, delete, delete all, list, or exit.")
            continue
        if "exit note mode" in user_input and note_mode:
            note_mode = False
            speak("Exiting note mode. Back to normal commands.")
            continue'''
        if "enter music mode" in user_input:
            music_mode = True
            speak("You're now in Music Mode. You can say play, pause, next, previous, or what's playing.")
            continue
        if "exit music mode" in user_input and music_mode:
            music_mode = False
            speak("Exiting Music Mode. Back to normal commands.")
            continue
        if 'stop' in user_input or 'exit' in user_input:
            speak("Shutting down. Goodbye!")
            break
        if any(keyword in user_input for keyword in ["daily briefing", "my day", "what's my day"]):
            give_daily_briefing()
            continue
        if any(keyword in user_input for keyword in ["create a reminder", "add a reminder", "set a remainder"]):
            add_reminder(user_input)
            continue
        if any(keyword in user_input for keyword in ["delete reminder", "remove reminder"]):
            speak("What is the title of the reminder you'd like to delete?")
            reminder_title = listen()
            today = dt.today().date()
            end = today + timedelta(days=7)
            result = delete_event_by_summary(reminder_title, today, end)
            speak(result)
            continue
        if "desktop" in user_input:
            desktop_summary = describe_desktop()
            print("Doodle:", desktop_summary)
            speak(desktop_summary)
            continue
        if "event" in user_input:
            today = dt.today().date()
            if "tomorrow" in user_input:
                start = today + timedelta(days=1)
                end = start + timedelta(days=1)
            elif "next week" in user_input:
                start = today
                end = today + timedelta(days=7)
            elif "next month" in user_input:
                next_month = today.replace(day=1) + timedelta(days=32)
                start = next_month.replace(day=1)
                end = start.replace(day=monthrange(start.year, start.month)[1])
            else:
                start = today
                end = today + timedelta(days=1)
            events = get_events_between(start, end)
            response = "\n".join(events)
            print(f"Doodle: {response}")
            speak(response)
            continue
        if "open" in user_input:
            common_websites = ["youtube", "google", "facebook", "twitter", "instagram", "netflix"]
            if "website" in user_input:
                website = user_input.split("open website")[1].strip()
                open_website(website)
            else:
                for site in common_websites:
                    if site in user_input:
                        open_website(f"www.{site}.com")
                        break
                else:
                    app_name = "vs code" if "vs code" in user_input else "chrome" if "chrome" in user_input else None
                    if app_name:
                        open_application(app_name)
                    else:
                        speak("Sorry, I didn’t understand what to open. Please specify a website or app.")
            continue
        if "check my inbox" in user_input or "read emails" in user_input:
            emails = read_latest_emails()
            for mail in emails:
                speak(mail)
            continue
        if "search" in user_input or "who is" in user_input or "what is" in user_input:
            query = user_input.replace("search", "").replace("who is", "").replace("what is", "").strip()
            speak(f"Searching for {query} on Wikipedia...")
            result = search_wikipedia(query)
            speak(result)
            continue
        if app_state.note_mode:
            if "create" in user_input or "new" in user_input:
                speak("What would you like me to note down?")
                note_text = listen()
                if "sorry" in note_text.lower():
                    speak("I didn't catch that. Please try again.")
                    continue
                speak("What should I name this note?")
                note_name = listen()
                if "sorry" in note_name.lower():
                    speak("I didn't catch that either. Let's try again later.")
                    continue
                filename = save_note(note_name, note_text)
                speak(f"Note saved as {filename}")
                continue
            if "read" in user_input:
                speak("Which note would you like me to read?")
                note_name = listen()
                note_content = read_note_by_name(note_name)
                if note_content:
                    speak(f"Here is the content of {note_name}")
                    speak(note_content)
                else:
                    speak(f"I couldn't find a note named '{note_name}'.")
                continue
            if "delete all" in user_input:
                speak("Are you sure you want to delete all notes? Say yes to confirm.")
                confirm = listen()
                if "yes" in confirm.lower():
                    result = delete_all_notes()
                    speak(result)
                else:
                    speak("Cancelled deleting notes.")
                continue
            if "delete" in user_input:
                speak("What is the name of the note you want to delete?")
                note_name = listen()
                result = delete_note_by_name(note_name)
                speak(result)
                continue
            if "rename" in user_input:
                speak("What is the current name of the note?")
                old_name = listen()
                speak("What should I rename it to?")
                new_name = listen()
                result = rename_note(old_name, new_name)
                speak(result)
                continue
            if "list" in user_input:
                notes = list_all_notes()
                if notes:
                    note_list = ", ".join(notes)
                    speak(f"You have the following notes: {note_list}")
                else:
                    speak("You don't have any notes.")
                continue
        if music_mode:
            if "play" in user_input:
                spotify_control.play()
                speak("Playing music.")
                continue
            if "pause" in user_input:
                spotify_control.pause()
                speak("Music paused.")
                continue
            if "next" in user_input:
                spotify_control.next_track()
                speak("Skipping to next song.")
                continue
            if "previous" in user_input:
                spotify_control.previous_track()
                speak("Going back to previous song.")
                continue
            if "what's playing" in user_input or "now playing" in user_input:
                song = spotify_control.current_song()
                speak(song)
                continue
        if "remember" in user_input and "is" in user_input:
            try:
                parts = user_input.split("remember")[1].strip().split(" is ")
                key = parts[0].strip()
                value = parts[1].strip()
                memory.remember(key, value)
                speak(f"Got it! I'll remember that your {key} is {value}.")
            except:
                speak("Sorry, I didn't catch what to remember.")
            continue
        if "what is my" in user_input or "what's my" in user_input:
            key = user_input.replace("what is my", "").replace("what's my", "").strip()
            value = memory.recall(key)
            if value:
                speak(f"Your {key} is {value}.")
            else:
                speak(f"I don't remember your {key}. You can tell me by saying, remember my {key} is ...")
            continue
        if "forget my" in user_input:
            key = user_input.replace("forget my", "").strip()
            if memory.forget(key):
                speak(f"I've forgotten your {key}.")
            else:
                speak(f"I couldn't find that in my memory.")
            continue
        if "what do you know about me" in user_input or "what do you remember about me" in user_input:
            personal_facts = memory.load_memory()
            if not personal_facts:
                speak("I don't know anything about you yet. You can tell me by saying, for example, 'remember my birthday is June 10th'.")
                continue
            facts_prompt = "\n".join([f"{key}: {value}" for key, value in personal_facts.items()])
            prompt = f"Based on the following information, summarize what you know about the user:\n{facts_prompt}"
            summary = get_response(prompt)
            speak(summary)
            continue
        if "weather" in user_input or "temperature" in user_input:
            report = weather.get_weather()
            speak(report)
            continue
        if "will it rain" in user_input or "rain" in user_input:
            rain_report = weather.will_it_rain()
            speak(rain_report)
            continue
        response = get_response(user_input)
        print("Doodle:", response)
        speak(response)

if __name__ == "__main__":
    main()
