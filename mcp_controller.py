import os
import subprocess
import requests
import json
import shutil
import glob
import datetime
import pyautogui
import time

# Safety: don't let pyautogui move too fast
pyautogui.PAUSE = 0.3

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diana_memory.json")
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diana_history.json")

# ================================================================
# SYSTEM CONTROL TOOLS
# ================================================================

def open_application(app_name):
    try:
        os.startfile(app_name)
        return {"status": "success", "message": f"Opened {app_name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def close_application(app_name):
    try:
        result = subprocess.run(f"taskkill /IM {app_name} /F", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return {"status": "success", "message": f"Closed {app_name}"}
        else:
            return {"status": "error", "message": result.stderr.strip()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def run_system_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
        return {"status": "success", "output": result.stdout[:1000], "error": result.stderr[:500]}
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Command timed out after 15 seconds"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def simulate_typing(text):
    try:
        pyautogui.write(text, interval=0.02)
        return {"status": "success", "message": f"Typed: {text[:50]}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def simulate_hotkey(*keys):
    try:
        pyautogui.hotkey(*keys)
        return {"status": "success", "message": f"Pressed: {'+'.join(keys)}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def press_key(key):
    try:
        pyautogui.press(key)
        return {"status": "success", "message": f"Pressed: {key}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def simulate_click(x=None, y=None, button='left'):
    try:
        if x is not None and y is not None:
            pyautogui.click(x=int(x), y=int(y), button=button)
        else:
            pyautogui.click(button=button)
        return {"status": "success", "message": f"Clicked at ({x}, {y})"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def move_mouse(x, y):
    try:
        pyautogui.moveTo(int(x), int(y))
        return {"status": "success", "message": f"Mouse moved to ({x}, {y})"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_screen_size():
    try:
        w, h = pyautogui.size()
        return {"status": "success", "width": w, "height": h}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def focus_window(title):
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(title)
        if windows:
            win = windows[0]
            win.activate()
            return {"status": "success", "message": f"Focused window: {win.title}"}
        else:
            return {"status": "error", "message": f"No window found: {title}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def list_open_windows():
    try:
        import pygetwindow as gw
        windows = [w.title for w in gw.getAllWindows() if w.title.strip()]
        return {"status": "success", "windows": windows[:30]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def take_screenshot():
    try:
        import io
        import base64
        screenshot = pyautogui.screenshot()
        screenshot = screenshot.resize((1024, 576))
        buffer = io.BytesIO()
        screenshot.save(buffer, format="JPEG", quality=60)
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        screenshot.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_screenshot.jpg"))
        return {"status": "success", "message": "Screenshot captured.", "image_base64": img_base64}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def trigger_mobile_webhook(webhook_id, payload=None):
    try:
        base_url = os.environ.get("TASKER_WEBHOOK_URL")
        if not base_url:
            return {"status": "error", "message": "TASKER_WEBHOOK_URL not configured."}
        url = f"{base_url.rstrip('/')}/{webhook_id}"
        response = requests.post(url, json=payload or {})
        return {"status": "success", "status_code": response.status_code}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ================================================================
# WEB & INFORMATION TOOLS
# ================================================================

def web_search(query):
    """Searches the web and returns text results."""
    try:
        # Use DuckDuckGo Instant Answer API (free, no key needed)
        url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        results = []
        # Abstract (main answer)
        if data.get("Abstract"):
            results.append(f"Summary: {data['Abstract']}")
        # Related topics
        for topic in data.get("RelatedTopics", [])[:5]:
            if isinstance(topic, dict) and "Text" in topic:
                results.append(topic["Text"])

        if not results:
            # Fallback: just tell Diana to use the browser
            return {"status": "success", "message": f"No instant answer found for '{query}'. Try opening a browser search instead.", "results": []}

        return {"status": "success", "results": results[:5]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_weather(city):
    """Gets current weather using wttr.in (free, no API key)."""
    try:
        url = f"https://wttr.in/{city}?format=j1"
        r = requests.get(url, timeout=10)
        data = r.json()
        current = data["current_condition"][0]
        weather = {
            "temperature_c": current["temp_C"],
            "feels_like_c": current["FeelsLikeC"],
            "description": current["weatherDesc"][0]["value"],
            "humidity": current["humidity"],
            "wind_speed_kmph": current["windspeedKmph"],
            "city": city
        }
        return {"status": "success", "weather": weather}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def open_youtube(query):
    """Opens YouTube in the default browser with a search query."""
    try:
        import webbrowser
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        return {"status": "success", "message": f"Opened YouTube search for: {query}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def read_webpage(url):
    """Fetches and reads the text content of a webpage."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        # Basic text extraction (strip HTML tags)
        import re
        text = re.sub(r'<[^>]+>', ' ', r.text)
        text = re.sub(r'\s+', ' ', text).strip()
        return {"status": "success", "content": text[:2000]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ================================================================
# FILE MANAGEMENT TOOLS
# ================================================================

def find_files(directory, pattern):
    """Finds files matching a pattern in a directory."""
    try:
        search_path = os.path.join(directory, "**", pattern)
        files = glob.glob(search_path, recursive=True)
        return {"status": "success", "files": files[:30], "count": len(files)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def move_file(source, destination):
    """Moves a file from source to destination."""
    try:
        shutil.move(source, destination)
        return {"status": "success", "message": f"Moved {source} to {destination}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def copy_file(source, destination):
    """Copies a file from source to destination."""
    try:
        shutil.copy2(source, destination)
        return {"status": "success", "message": f"Copied {source} to {destination}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def delete_file(path):
    """Deletes a file or empty folder."""
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        return {"status": "success", "message": f"Deleted {path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def read_file_contents(path, num_lines=10):
    """Reads the first N lines of a text file."""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= num_lines:
                    break
                lines.append(line.rstrip())
        return {"status": "success", "content": "\n".join(lines), "lines_read": len(lines)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def create_folder(path):
    """Creates a new folder (and parent folders if needed)."""
    try:
        os.makedirs(path, exist_ok=True)
        return {"status": "success", "message": f"Created folder: {path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ================================================================
# MEMORY & CONTEXT TOOLS
# ================================================================

def _load_memory():
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {}

def _save_memory(data):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def remember(key, value):
    """Stores a piece of information in Diana's long-term memory."""
    try:
        mem = _load_memory()
        mem[key] = {"value": value, "saved_at": datetime.datetime.now().isoformat()}
        _save_memory(mem)
        return {"status": "success", "message": f"Remembered: {key} = {value}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def recall(key):
    """Retrieves a specific memory by key."""
    try:
        mem = _load_memory()
        if key in mem:
            return {"status": "success", "key": key, "value": mem[key]["value"], "saved_at": mem[key]["saved_at"]}
        # Fuzzy search
        matches = {k: v for k, v in mem.items() if key.lower() in k.lower()}
        if matches:
            return {"status": "success", "matches": {k: v["value"] for k, v in matches.items()}}
        return {"status": "not_found", "message": f"No memory found for: {key}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def recall_all():
    """Lists all stored memories."""
    try:
        mem = _load_memory()
        if not mem:
            return {"status": "success", "message": "No memories stored yet.", "memories": {}}
        summary = {k: v["value"] for k, v in mem.items()}
        return {"status": "success", "memories": summary, "count": len(summary)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def forget(key):
    """Removes a specific memory."""
    try:
        mem = _load_memory()
        if key in mem:
            del mem[key]
            _save_memory(mem)
            return {"status": "success", "message": f"Forgot: {key}"}
        return {"status": "not_found", "message": f"No memory found for: {key}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def save_conversation(user_said, diana_said):
    """Saves a conversation exchange to history."""
    try:
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        history.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "user": user_said,
            "diana": diana_said
        })
        # Keep last 100 conversations
        history = history[-100:]
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        return {"status": "success", "message": "Conversation saved."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_daily_briefing():
    """Gets a daily briefing with date, weather, and pending memories."""
    try:
        now = datetime.datetime.now()
        briefing = {
            "date": now.strftime("%A, %B %d, %Y"),
            "time": now.strftime("%I:%M %p"),
        }
        # Get weather
        try:
            weather_data = get_weather("auto")
            if weather_data["status"] == "success":
                briefing["weather"] = weather_data["weather"]
        except:
            briefing["weather"] = "Could not fetch weather"

        # Get memories
        mem = _load_memory()
        if mem:
            briefing["memories"] = {k: v["value"] for k, v in mem.items()}
            briefing["memory_count"] = len(mem)
        else:
            briefing["memories"] = "No saved memories"

        return {"status": "success", "briefing": briefing}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ================================================================
# EXPORT ALL TOOLS
# ================================================================
MCP_TOOLS = {
    # System
    "open_application": open_application,
    "close_application": close_application,
    "run_system_command": run_system_command,
    "simulate_typing": simulate_typing,
    "simulate_hotkey": simulate_hotkey,
    "press_key": press_key,
    "simulate_click": simulate_click,
    "move_mouse": move_mouse,
    "get_screen_size": get_screen_size,
    "focus_window": focus_window,
    "list_open_windows": list_open_windows,
    "take_screenshot": take_screenshot,
    "trigger_mobile_webhook": trigger_mobile_webhook,
    # Web
    "web_search": web_search,
    "get_weather": get_weather,
    "open_youtube": open_youtube,
    "read_webpage": read_webpage,
    # Files
    "find_files": find_files,
    "move_file": move_file,
    "copy_file": copy_file,
    "delete_file": delete_file,
    "read_file_contents": read_file_contents,
    "create_folder": create_folder,
    # Memory
    "remember": remember,
    "recall": recall,
    "recall_all": recall_all,
    "forget": forget,
    "save_conversation": save_conversation,
    "get_daily_briefing": get_daily_briefing,
}
