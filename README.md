<div align="center">

# 🌙 Project Diana

### Your Omnipotent Voice-Controlled AI Desktop Companion

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Google Gemini](https://img.shields.io/badge/Gemini_Live_Audio-WebSocket_API-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![Windows](https://img.shields.io/badge/Windows_11-0078D4?style=for-the-badge&logo=windows11&logoColor=white)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Diana is an always-on, voice-activated AI assistant that lives on your desktop.**  
She can hear you, talk back, think out loud, and control your entire computer with **67 powerful tools** — from opening apps and sending messages to searching the web, managing files, and remembering things across sessions.

> *"Hey Diana, open Chrome and search for the latest AI news"*  
> *"Hey Diana, what's the weather in New York?"*  
> *"Hey Diana, set a timer for 5 minutes"*  
> *"Hey Diana, remember that my exam is on May 5th"*

---

</div>

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🎙️ **Wake Word Detection** | Say **"Hey Diana"** to activate. She sleeps quietly until called. |
| 🗣️ **Real-Time Voice Chat** | Full-duplex bidirectional audio streaming via Google Gemini Multimodal Live API |
| 💭 **Floating Thought Bubbles** | See Diana's thinking process in real-time on your screen |
| 🖥️ **Full OS Control** | Open/close apps, type, click, keyboard shortcuts, screenshots |
| 🌐 **Web Intelligence** | Search the web, check weather, open YouTube, read webpages |
| 📁 **File Management** | Find, move, copy, delete, rename, zip/unzip files and folders |
| 🧠 **Persistent Memory** | Remembers things across sessions — meetings, preferences, facts |
| ⏰ **Timers & Notifications** | Set countdown timers with Windows toast notifications |
| 🔒 **System Power** | Volume, brightness, lock, sleep, shutdown, restart your PC |
| 📊 **System Monitoring** | CPU, RAM, battery, disk, IP address, running processes |
| 🌍 **Translation** | Translate text between languages instantly |
| 📱 **Mobile Control** | Trigger Android Tasker webhooks for cross-device automation |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    main.py                          │
│            (Orchestrator + Persona)                  │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Persona  │  │  67 Tool     │  │  Dispatcher  │  │
│  │  Config   │  │  Declarations│  │  Router      │  │
│  └──────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────┬───────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│voice_engine.py│ │diana_ui.py│ │mcp_controller│
│              │ │           │ │    .py       │
│ • Wake Word  │ │ • Avatar  │ │ • 67 Tools  │
│ • Audio I/O  │ │ • Thought │ │ • System    │
│ • WebSocket  │ │   Bubbles │ │ • Web       │
│ • Tool Exec  │ │ • Drag    │ │ • Files     │
│              │ │           │ │ • Memory    │
└──────┬───────┘ └───────────┘ └──────────────┘
       │
       ▼
┌──────────────────────┐
│  Google Gemini 2.0 / 2.5 Flash │
│  Live Audio API (WebSocket)   │
│  (WebSocket)         │
└──────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** installed
- **Windows 10/11**
- **Microphone** connected
- **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/apikey)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/VAIBHAV7848/Diana.git
cd Diana

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your .env file
echo GEMINI_API_KEY=your_api_key_here > .env

# 4. Run Diana
python main.py
```

### First Run

1. Diana's avatar overlay will appear in the bottom-right corner of your screen
2. She'll calibrate your microphone (1 second)
3. You'll see: **"Say 'Hey Diana' to activate"**
4. Say **"Hey Diana"** → she wakes up and listens
5. Give her any command → she responds with voice and actions
6. After 6 seconds of silence → she goes back to sleep

---

## 🔧 Configuration

### Environment Variables (`.env`)

```env
GEMINI_API_KEY=your_gemini_api_key_here
TASKER_WEBHOOK_URL=http://your-phone-ip:port  # Optional: for Android control
```

### File Paths

Diana needs to know your actual file paths. Edit the `DIANA_PERSONA` section in `main.py`:

```python
IMPORTANT FILE PATHS ON THIS PC:
- Desktop: C:\\Users\\YOUR_USERNAME\\Desktop
- Documents: C:\\Users\\YOUR_USERNAME\\Documents
- Downloads: C:\\Users\\YOUR_USERNAME\\Downloads
```

> **Tip:** If you use OneDrive, your Desktop may be at `C:\Users\YOUR_USERNAME\OneDrive\Desktop`. Run this PowerShell command to check:
> ```powershell
> [Environment]::GetFolderPath('Desktop')
> ```

### Auto-Start on Boot

Run this to add Diana to Windows startup:
```powershell
Copy-Item "start_diana.bat" "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\"
```

---

## 🛠️ All 67 Tools

<details>
<summary><b>🖥️ System Control (15 tools)</b></summary>

| Tool | Description |
|------|-------------|
| `open_application` | Opens any app by name |
| `close_application` | Force-closes an app (auto-adds .exe) |
| `run_system_command` | Runs PowerShell commands |
| `simulate_typing` | Types text at cursor position |
| `simulate_hotkey` | Keyboard shortcuts (Ctrl+C, Alt+Tab, etc.) |
| `press_key` | Presses a single key |
| `simulate_click` | Mouse click at coordinates |
| `move_mouse` | Moves mouse cursor |
| `scroll_mouse` | Scrolls up/down |
| `drag_mouse` | Click and drag |
| `double_click` | Double-clicks at coordinates |
| `focus_window` | Brings a window to front |
| `list_open_windows` | Lists all open windows |
| `get_screen_size` | Returns screen resolution |
| `take_screenshot` | Captures the screen |

</details>

<details>
<summary><b>⚡ System Power (13 tools)</b></summary>

| Tool | Description |
|------|-------------|
| `set_volume` | Sets volume (0-100) |
| `mute_volume` | Toggles mute |
| `set_brightness` | Sets brightness (0-100) |
| `lock_pc` | Locks the computer |
| `sleep_pc` | Puts PC to sleep |
| `shutdown_pc` | Shuts down with delay |
| `restart_pc` | Restarts with delay |
| `cancel_shutdown` | Cancels pending shutdown |
| `get_clipboard` | Reads clipboard content |
| `set_clipboard` | Copies text to clipboard |
| `set_wallpaper` | Changes desktop wallpaper |
| `toggle_wifi` | Enables/disables WiFi |
| `send_notification` | Windows toast notification |

</details>

<details>
<summary><b>📊 System Monitoring (7 tools)</b></summary>

| Tool | Description |
|------|-------------|
| `get_system_info` | CPU, RAM, OS details |
| `get_battery_info` | Battery percentage |
| `get_ip_address` | Local and public IP |
| `list_processes` | Running processes |
| `kill_process` | Kills a process by PID |
| `get_disk_usage` | Disk space info |
| `get_date_time` | Current date and time |

</details>

<details>
<summary><b>🌐 Web & Intelligence (8 tools)</b></summary>

| Tool | Description |
|------|-------------|
| `web_search` | DuckDuckGo instant answers |
| `get_weather` | Weather via wttr.in (free) |
| `open_youtube` | Opens YouTube search |
| `open_url` | Opens any URL |
| `read_webpage` | Extracts text from URLs |
| `calculate` | Math calculator |
| `translate_text` | Language translation |
| `generate_password` | Secure password generator |

</details>

<details>
<summary><b>📁 File Management (13 tools)</b></summary>

| Tool | Description |
|------|-------------|
| `find_files` | Search files by pattern |
| `move_file` | Move files |
| `copy_file` | Copy files |
| `delete_file` | Delete files/folders |
| `rename_file` | Rename files |
| `read_file_contents` | Read file content |
| `write_file_contents` | Write to files |
| `append_to_file` | Append to files |
| `create_folder` | Create directories |
| `get_file_info` | File size, dates |
| `list_directory` | List folder contents |
| `zip_files` | Compress to ZIP |
| `unzip_file` | Extract ZIPs |

</details>

<details>
<summary><b>🧠 Memory & Notes (10 tools)</b></summary>

| Tool | Description |
|------|-------------|
| `remember` | Store in long-term memory |
| `recall` | Retrieve a memory |
| `recall_all` | List all memories |
| `forget` | Delete a memory |
| `save_conversation` | Save chat history |
| `get_daily_briefing` | Morning briefing |
| `set_timer` | Countdown timer |
| `take_note` | Quick notes |
| `read_notes` | Read all notes |
| `clear_notes` | Clear all notes |

</details>

<details>
<summary><b>📱 Mobile (1 tool)</b></summary>

| Tool | Description |
|------|-------------|
| `trigger_mobile_webhook` | Android Tasker webhook |

</details>

---

## 💡 Example Commands

```
"Hey Diana, open Notepad and type 'Hello World'"
"Hey Diana, what's the weather in Mumbai?"
"Hey Diana, play lofi music on YouTube"
"Hey Diana, find all PDF files on my Desktop"
"Hey Diana, create a folder called Projects on D drive"
"Hey Diana, remember that my meeting is at 3 PM tomorrow"
"Hey Diana, what do you remember?"
"Hey Diana, set volume to 40"
"Hey Diana, set a timer for 10 minutes"
"Hey Diana, translate 'good morning' to Japanese"
"Hey Diana, generate a secure password"
"Hey Diana, what's my battery level?"
"Hey Diana, what's my IP address?"
"Hey Diana, lock my PC"
"Good morning Diana!" → Full daily briefing
```

---

## 📂 Project Structure

```
Diana/
├── main.py              # Orchestrator, persona, tool declarations
├── voice_engine.py      # WebSocket audio streaming + wake word
├── mcp_controller.py    # All 67 tool implementations
├── diana_ui.py          # Floating avatar overlay + thought bubbles
├── start_diana.bat      # Auto-start script
├── requirements.txt     # Python dependencies
├── .env                 # API keys (not committed)
├── diana_memory.json    # Persistent memory (auto-created)
├── diana_notes.txt      # Notes storage (auto-created)
└── diana_history.json   # Conversation history (auto-created)
```

---

## 🔑 API Keys Required

| Service | Purpose | Free? | Get it at |
|---------|---------|-------|-----------|
| **Google Gemini API** | Live Audio & tool orchestration | ✅ Free tier | [aistudio.google.com](https://aistudio.google.com/apikey) |
| **Google Speech** | Wake word detection | ✅ Free | Built into `speech_recognition` |
| **DuckDuckGo** | Web search | ✅ Free | No key needed |
| **wttr.in** | Weather | ✅ Free | No key needed |
| **MyMemory** | Translation | ✅ Free | No key needed |

---

## ⚠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| `GEMINI_API_KEY is empty` | Create `.env` file with your key |
| `No module named 'pyaudio'` | `pip install pyaudio` — may need VS Build Tools on Windows |
| File paths fail | Check your real Desktop path with `[Environment]::GetFolderPath('Desktop')` in PowerShell |
| `notepad` won't close | Fixed: Diana auto-appends `.exe` now |
| Wake word not detecting | Speak clearly, check microphone permissions |
| Terminal encoding crash | Always run with `PYTHONIOENCODING=utf-8` |

---

## 🛣️ Roadmap

- [ ] 3D VRM Avatar with lip-sync animation
- [ ] Gmail API integration (read/send emails)
- [ ] Google Calendar integration
- [ ] Spotify playback control
- [ ] OCR (read text from screenshots)
- [ ] Screen recording
- [ ] Macro recording & playback
- [ ] Scheduled automation tasks
- [ ] Smart home integration (Home Assistant)
- [ ] Multi-language wake words

---

<div align="center">

**Built with ❤️ by [VAIBHAV7848](https://github.com/VAIBHAV7848)**

*Diana is named after the Roman goddess of the moon — always watching, always ready.*

</div>
