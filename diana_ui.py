import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk
import json
import os
import sys
import textwrap

THOUGHT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diana_thoughts.json")

class DianaOverlay:
    def __init__(self, root, image_path):
        self.root = root
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-transparentcolor', '#010101')
        self.root.configure(bg='#010101')

        # --- Main Frame ---
        self.main_frame = tk.Frame(root, bg='#010101')
        self.main_frame.pack()

        # --- Thought Bubble (above avatar) ---
        self.bubble_frame = tk.Frame(self.main_frame, bg='#010101')
        self.bubble_frame.pack(side=tk.TOP, pady=(0, 5))

        self.bubble_bg = '#1a1a2e'
        self.bubble_fg = '#e0e0ff'
        self.bubble_border = '#4a4aff'

        self.thought_label = tk.Label(
            self.bubble_frame,
            text="",
            bg=self.bubble_bg,
            fg=self.bubble_fg,
            wraplength=320,
            justify=tk.LEFT,
            padx=12,
            pady=8,
            relief=tk.FLAT,
            bd=0,
            highlightbackground=self.bubble_border,
            highlightthickness=2,
            highlightcolor=self.bubble_border
        )
        # Hidden by default until Diana starts thinking
        self.thought_label.pack_forget()

        # --- Status indicator ---
        self.status_label = tk.Label(
            self.bubble_frame,
            text="",
            bg='#010101',
            fg='#7070ff',
            padx=4,
            pady=2
        )
        self.status_label.pack_forget()

        # --- Avatar Image ---
        self.avatar_frame = tk.Frame(self.main_frame, bg='#010101')
        self.avatar_frame.pack(side=tk.BOTTOM)

        try:
            img = Image.open(image_path)
            img = img.resize((280, 280), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image: {e}")
            root.destroy()
            return

        self.avatar_label = tk.Label(self.avatar_frame, image=self.photo, bg='#010101', cursor="fleur")
        self.avatar_label.pack()

        # Position bottom-right
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        x = ws - 360
        y = hs - 520
        root.geometry(f'+{x}+{y}')

        # Drag bindings
        self.avatar_label.bind('<ButtonPress-1>', self.on_drag_start)
        self.avatar_label.bind('<B1-Motion>', self.on_drag_motion)
        self.avatar_label.bind('<Button-3>', lambda e: root.destroy())

        # Set up fonts
        try:
            self.thought_font = tkfont.Font(family="Segoe UI", size=9)
            self.status_font = tkfont.Font(family="Segoe UI", size=8, slant="italic")
        except:
            self.thought_font = tkfont.Font(size=9)
            self.status_font = tkfont.Font(size=8, slant="italic")

        self.thought_label.configure(font=self.thought_font)
        self.status_label.configure(font=self.status_font)

        # Track last thought to avoid flicker
        self.last_thought = ""
        self.last_status = ""
        self.hide_timer = None

        # Start polling for thoughts
        self.poll_thoughts()

    def on_drag_start(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def on_drag_motion(self, event):
        x = self.root.winfo_x() - self._drag_start_x + event.x
        y = self.root.winfo_y() - self._drag_start_y + event.y
        self.root.geometry(f"+{x}+{y}")

    def show_thought(self, text, status=""):
        if text and text != self.last_thought:
            self.last_thought = text
            # Truncate long thoughts
            display_text = text[:200] + "..." if len(text) > 200 else text
            self.thought_label.configure(text=display_text)
            self.thought_label.pack(side=tk.TOP)

            if status:
                self.status_label.configure(text=status)
                self.status_label.pack(side=tk.BOTTOM)
            else:
                self.status_label.pack_forget()

            # Auto-hide after 8 seconds
            if self.hide_timer:
                self.root.after_cancel(self.hide_timer)
            self.hide_timer = self.root.after(8000, self.hide_thought)

    def hide_thought(self):
        self.thought_label.pack_forget()
        self.status_label.pack_forget()
        self.last_thought = ""

    def poll_thoughts(self):
        """Reads the shared thought file written by voice_engine."""
        try:
            if os.path.exists(THOUGHT_FILE):
                with open(THOUGHT_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                thought = data.get("thought", "")
                status = data.get("status", "")
                if thought:
                    self.show_thought(thought, status)
        except (json.JSONDecodeError, IOError):
            pass
        # Poll every 300ms
        self.root.after(300, self.poll_thoughts)


def main():
    image_path = r"C:\Users\jayas\.gemini\antigravity\brain\f28282d1-e0ef-479f-ba6f-1715c06c95bb\diana_visual_matrix_1776683599821.png"
    root = tk.Tk()
    root.title("Diana")

    app = DianaOverlay(root, image_path)
    root.mainloop()

if __name__ == '__main__':
    main()
