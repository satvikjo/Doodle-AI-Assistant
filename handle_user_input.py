from main import (
    get_response,
    describe_desktop,
    add_reminder,
    delete_event_by_summary,
    interpret_day,
    parse_time_from_query,
    get_events_between,
    get_events_for_day,
    open_website,
    open_application,
    read_latest_emails,
    save_note,
    delete_note_by_name,
    rename_note,
    delete_all_notes,
    list_all_notes,
    read_note_by_name,
    search_wikipedia,
    give_daily_briefing,
    memory,
    weather,
    dt,
    timedelta,
    monthrange,
    listen,
    speak
)

from shared_state import app_state
from utils.voice_engine import speak
from utils.voice_input import listen

def handle_note_mode_command(user_input: str) -> str:
    """Handle all note-specific commands with continuous listening"""
    if "create" in user_input or "new" in user_input:
            speak("What would you like me to note down?")
            note_text = listen()
            if not note_text:
                return "No note content provided"
            
            speak("What should I name this note?")
            note_name = listen()
            filename = save_note(note_name, note_text)
            speak(f"Note saved as {filename}")
            return f"Note saved: {filename}"

    if "read" in user_input:
            speak("Which note would you like me to read?")
            note_name = listen()
            note_content = read_note_by_name(note_name)
            if note_content:
                speak(f"Here is the content of {note_name}")
                speak(note_content)
                return note_content
            return f"Note '{note_name}' not found"

    if "delete all" in user_input:
            speak("Are you sure? Say yes to confirm.")
            confirm = listen()
            if "yes" in confirm.lower():
                result = delete_all_notes()
                speak(result)
                return result
            return "Deletion cancelled"

    if "delete" in user_input:
            speak("Which note should I delete?")
            note_name = listen()
            result = delete_note_by_name(note_name)
            speak(result)
            return result

    if "rename" in user_input:
            speak("Current note name?")
            old_name = listen()
            speak("New name?")
            new_name = listen()
            result = rename_note(old_name, new_name)
            speak(result)
            return result

    if "list" in user_input:
            notes = list_all_notes()
            if notes:
                note_list = ", ".join(notes)
                speak(f"Your notes: {note_list}")
                return note_list
            speak("No notes found")
            return "No notes"

def handle_user_input(user_input: str) -> str:
    user_input = user_input.lower()

    if "enter note mode" in user_input:
        app_state.note_mode = True
        speak("You're now in note mode. What would you like to do?")
        return "📝 Note mode activated. You can say create, read, rename, delete, delete all, list, or exit."

    if "exit note mode" in user_input and app_state.note_mode:
        app_state.note_mode = False
        return "Exiting note mode. Back to normal commands."
    
    # System commands
    if 'stop' in user_input or 'exit' in user_input:
        speak("Shutting down. Goodbye!")
        return "Shutting down"

    # Note mode operations
    if app_state.note_mode:
        response = handle_note_mode_command(user_input)
        
        # After handling a note command, continue listening in note mode
        if app_state.note_mode:  # Check if we're still in note mode
            speak("What else would you like to do in note mode?")
            next_input = listen(timeout=5)  # Listen for next command
            if next_input:
                return handle_user_input(next_input)  # Recursively handle next command
        
        return response
        

    # Calendar and reminders
    if any(keyword in user_input for keyword in ["daily briefing", "my day", "what's my day"]):
        give_daily_briefing()
        return "Daily briefing completed"

    if any(keyword in user_input for keyword in ["create a reminder", "add a reminder", "set a reminder"]):
        add_reminder(user_input)
        return "Reminder set"

    if any(keyword in user_input for keyword in ["delete reminder", "remove reminder"]):
        speak("Reminder title to delete?")
        reminder_title = listen()
        today = dt.today().date()
        end = today + timedelta(days=7)
        result = delete_event_by_summary(reminder_title, today, end)
        speak(result)
        return result

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
        response = "\n".join(events) if events else "No events found"
        speak(response)
        return response

    # System controls
    if "desktop" in user_input:
        desktop_summary = describe_desktop()
        speak(desktop_summary)
        return desktop_summary

    if "open" in user_input:
        common_websites = ["youtube", "google", "facebook", "twitter", "instagram", "netflix"]
        if "website" in user_input:
            website = user_input.split("open website")[1].strip()
            open_website(website)
            return f"Opening {website}"
        else:
            for site in common_websites:
                if site in user_input:
                    open_website(f"www.{site}.com")
                    return f"Opening {site}"
            app_name = "vs code" if "vs code" in user_input else "chrome" if "chrome" in user_input else None
            if app_name:
                open_application(app_name)
                return f"Opening {app_name}"
            return "Please specify a website or app"

    # Information services
    if "check my inbox" in user_input or "read emails" in user_input:
        emails = read_latest_emails()
        for mail in emails:
            speak(mail)
        return "\n".join(emails) if emails else "No new emails"

    if "search" in user_input or "who is" in user_input or "what is" in user_input:
        query = user_input.replace("search", "").replace("who is", "").replace("what is", "").strip()
        result = search_wikipedia(query)
        speak(result)
        return result

    if "weather" in user_input or "temperature" in user_input:
        report = weather.get_weather()
        speak(report)
        return report

    if "will it rain" in user_input or "rain" in user_input:
        report = weather.will_it_rain()
        speak(report)
        return report

    # Memory system
    if "remember" in user_input and "is" in user_input:
        try:
            parts = user_input.split("remember")[1].strip().split(" is ")
            key = parts[0].strip()
            value = parts[1].strip()
            memory.remember(key, value)
            response = f"Remembered: {key} = {value}"
            speak(response)
            return response
        except:
            return "Failed to save memory"

    if "what is my" in user_input or "what's my" in user_input:
        key = user_input.replace("what is my", "").replace("what's my", "").strip()
        value = memory.recall(key)
        response = f"Your {key} is {value}" if value else f"I don't know your {key}"
        speak(response)
        return response

    if "forget my" in user_input:
        key = user_input.replace("forget my", "").strip()
        if memory.forget(key):
            response = f"Forgotten: {key}"
        else:
            response = f"Nothing found for: {key}"
        speak(response)
        return response

    if "what do you know about me" in user_input:
        facts = memory.load_memory()
        if not facts:
            return "I know nothing about you yet"
        summary = get_response(f"Summarize these facts about the user: {facts}")
        speak(summary)
        return summary

    # Default: General conversation
    response = get_response(user_input)
    speak(response)
    return response
