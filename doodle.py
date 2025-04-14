import tkinter as tk
from tkinter import ttk, messagebox
import threading
from utils.voice_engine import speak
from utils.voice_input import listen
from handle_user_input import handle_user_input
from utils.wake_word import WakeWordDetector
from shared_state import app_state

class DoodleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Doodle AI Assistant")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        self.dark_mode = False
        self.listening = False

        # Style Configuration
        self.setup_styles()
        
        # Main Frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=5)
        
        self.title_label = ttk.Label(
            self.header_frame, 
            text="🤖 Doodle AI Assistant", 
            font=("Segoe UI", 16, "bold")
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Dark Mode Toggle
        self.mode_btn = ttk.Button(
            self.header_frame,
            text="🌙",
            command=self.toggle_dark_mode,
            width=3
        )
        self.mode_btn.pack(side=tk.RIGHT, padx=5)

        # Chat Area
        self.chat_frame = ttk.Frame(self.main_frame)
        self.chat_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chat_canvas = tk.Canvas(self.chat_frame, bg=self.bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.chat_frame, orient="vertical", command=self.chat_canvas.yview)
        self.chat_container = ttk.Frame(self.chat_canvas)
        
        self.chat_container.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(
                scrollregion=self.chat_canvas.bbox("all")
            )
        )
        
        self.chat_canvas.create_window((0, 0), window=self.chat_container, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Input Area
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(
            self.input_frame,
            text="🎤 Start Listening",
            command=self.start_listening,
            style="Accent.TButton"
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            self.input_frame,
            text="⏹ Stop Listening",
            command=self.stop_listening,
            style="Accent.TButton"
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("✅ Ready")
        self.status_bar = ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, ipady=5)

        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

    def setup_styles(self):
        self.bg_color = "#f0f0f0"
        self.user_bg = "#e3f2fd"
        self.ai_bg = "#f8f9fa"
        self.text_color = "#333333"
        
        style = ttk.Style()
        style.theme_use("clam")
        
        # Light mode styles
        style.configure(".", background=self.bg_color, foreground=self.text_color)
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color)
        style.configure("TButton", padding=5)
        style.configure("Accent.TButton", background="#4CAF50", foreground="white")
        style.configure("TEntry", fieldbackground="white")
        style.configure("TScrollbar", background="#dddddd")
        
        # Dark mode styles will be set in toggle_dark_mode()

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            self.bg_color = "#2d2d2d"
            self.user_bg = "#1e3a8a"
            self.ai_bg = "#374151"
            self.text_color = "#ffffff"
            self.mode_btn.config(text="☀️")
        else:
            self.bg_color = "#f0f0f0"
            self.user_bg = "#e3f2fd"
            self.ai_bg = "#f8f9fa"
            self.text_color = "#333333"
            self.mode_btn.config(text="🌙")
        
        self.update_colors()
        
    def update_colors(self):
        self.chat_canvas.config(bg=self.bg_color)
        self.status_bar.config(background="#333333" if self.dark_mode else "#dddddd",
                             foreground="white" if self.dark_mode else "black")
        
        for widget in self.chat_container.winfo_children():
            if isinstance(widget, tk.Frame):
                if "user" in widget.winfo_name():
                    widget.config(bg=self.user_bg)
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Label):
                            child.config(bg=self.user_bg, fg=self.text_color)
                else:
                    widget.config(bg=self.ai_bg)
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Label):
                            child.config(bg=self.ai_bg, fg=self.text_color)

    def create_chat_bubble(self, text, is_user=False):
        bubble_frame = tk.Frame(
            self.chat_container,
            bg=self.user_bg if is_user else self.ai_bg,
            padx=10,
            pady=5,
            name="user_bubble" if is_user else "ai_bubble"
        )
        bubble_frame.pack(fill=tk.X, padx=5, pady=2)
        
        emoji = "👤" if is_user else "🤖"
        prefix = f"{emoji} You: " if is_user else f"{emoji} Doodle: "
        
        bubble_label = tk.Label(
            bubble_frame,
            text=prefix + text,
            bg=self.user_bg if is_user else self.ai_bg,
            fg=self.text_color,
            font=("Segoe UI", 10),
            justify=tk.LEFT,
            wraplength=450,
            anchor="w"
        )
        bubble_label.pack(fill=tk.X)
        
        self.chat_canvas.yview_moveto(1.0)

    def start_listening(self):
        if not self.listening:
            self.listening = True
            self.status_var.set("🔊 Listening...")
            self.create_chat_bubble("Listening...", is_user=False)
            threading.Thread(target=self.listen_loop, daemon=True).start()

    def stop_listening(self):
        if self.listening:
            self.listening = False
            self.status_var.set("✅ Ready")
            speak("Listening stopped.")


    def listen_loop(self):
        wake_detector = WakeWordDetector()

        while self.listening:
            try:
                self.status_var.set("🔈 Say 'Hey Doodle'...")
                print("🔈 Say 'Hey Doodle'...")

                while self.listening:
                    if wake_detector.listen_for_wake_word(non_blocking=True):
                        break

                if not self.listening:
                    break

                self.status_var.set("🎤 Wake word detected! Speak now...")
                print("🎤 Wake word detected! Speak now...")

                user_input = listen()
                if user_input.strip():
                    self.create_chat_bubble(user_input, is_user=True)
                    response = handle_user_input(user_input)
                    self.create_chat_bubble(response, is_user=False)

                    if app_state.note_mode:
                        self.status_var.set("📝 Note Mode Active")
                    else:
                        self.status_var.set("✅ Ready")

            except Exception as e:
                self.create_chat_bubble(f"Error: {str(e)}", is_user=False)
                self.status_var.set("⚠️ Error occurred")
                self.listening = False




def run_gui():
    root = tk.Tk()
    
    # Set window icon and title
    try:
        root.iconbitmap("doodle_icon.ico")  # Add your icon file
    except:
        pass
        
    app = DoodleApp(root)
    
    # Center the window
    window_width = 600
    window_height = 500
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    root.mainloop()

if __name__ == "__main__":
    run_gui()