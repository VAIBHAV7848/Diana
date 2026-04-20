import os
import subprocess
import requests
import json
import shutil
import glob
import datetime
import ctypes
import string
import random
import math
import zipfile
import webbrowser
import socket
import platform
import pyautogui
import time

pyautogui.PAUSE = 0.3

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diana_memory.json")
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diana_history.json")
NOTES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diana_notes.txt")

# ================================================================
# SYSTEM CONTROL
# ================================================================

def open_application(app_name):
    try:
        os.startfile(app_name)
        return {"status": "success", "message": f"Opened {app_name}"}
    except:
        try:
            subprocess.Popen(app_name, shell=True)
            return {"status": "success", "message": f"Opened {app_name}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

def close_application(app_name):
    try:
        if not app_name.lower().endswith(".exe"):
            app_name = app_name + ".exe"
        result = subprocess.run(f"taskkill /IM {app_name} /F", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return {"status": "success", "message": f"Closed {app_name}"}
        else:
            title = app_name.replace(".exe", "")
            try:
                import pygetwindow as gw
                windows = gw.getWindowsWithTitle(title)
                if windows:
                    windows[0].activate()
                    pyautogui.hotkey('alt', 'F4')
                    return {"status": "success", "message": f"Closed {title} via Alt+F4"}
            except:
                pass
            return {"status": "error", "message": result.stderr.strip()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def run_system_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
        return {"status": "success", "output": result.stdout[:1500], "error": result.stderr[:500]}
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Timed out"}
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
        return {"status": "success", "message": f"Clicked ({x},{y})"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def move_mouse(x, y):
    try:
        pyautogui.moveTo(int(x), int(y))
        return {"status": "success", "message": f"Mouse at ({x},{y})"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def scroll_mouse(clicks, direction="down"):
    try:
        amount = -int(clicks) if direction == "down" else int(clicks)
        pyautogui.scroll(amount)
        return {"status": "success", "message": f"Scrolled {direction} {clicks}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def drag_mouse(start_x, start_y, end_x, end_y):
    try:
        pyautogui.moveTo(int(start_x), int(start_y))
        pyautogui.drag(int(end_x)-int(start_x), int(end_y)-int(start_y), duration=0.5)
        return {"status": "success", "message": f"Dragged from ({start_x},{start_y}) to ({end_x},{end_y})"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def double_click(x=None, y=None):
    try:
        if x and y:
            pyautogui.doubleClick(int(x), int(y))
        else:
            pyautogui.doubleClick()
        return {"status": "success", "message": f"Double clicked ({x},{y})"}
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
            return {"status": "success", "message": f"Focused: {win.title}"}
        return {"status": "error", "message": f"No window: {title}"}
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
        import io, base64
        ss = pyautogui.screenshot()
        ss = ss.resize((1024, 576))
        buf = io.BytesIO()
        ss.save(buf, format="JPEG", quality=60)
        b64 = base64.b64encode(buf.getvalue()).decode()
        ss.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_screenshot.jpg"))
        return {"status": "success", "message": "Screenshot captured.", "image_base64": b64}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ================================================================
# SYSTEM POWER CONTROLS
# ================================================================

def set_volume(level):
    try:
        # Use PowerShell to set volume (0-100)
        level = max(0, min(100, int(level)))
        ps = f'''
        $wshShell = New-Object -ComObject WScript.Shell
        1..50 | ForEach-Object {{ $wshShell.SendKeys([char]174) }}
        $steps = [math]::Round({level}/2)
        1..$steps | ForEach-Object {{ $wshShell.SendKeys([char]175) }}
        '''
        subprocess.run(["powershell", "-Command", ps], capture_output=True)
        return {"status": "success", "message": f"Volume set to ~{level}%"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def mute_volume():
    try:
        pyautogui.press('volumemute')
        return {"status": "success", "message": "Toggled mute"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def set_brightness(level):
    try:
        level = max(0, min(100, int(level)))
        subprocess.run(f'powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})',
                       shell=True, capture_output=True)
        return {"status": "success", "message": f"Brightness set to {level}%"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def lock_pc():
    try:
        ctypes.windll.user32.LockWorkStation()
        return {"status": "success", "message": "PC locked"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def sleep_pc():
    try:
        subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
        return {"status": "success", "message": "PC going to sleep"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def shutdown_pc(delay=30):
    try:
        subprocess.run(f"shutdown /s /t {int(delay)}", shell=True)
        return {"status": "success", "message": f"Shutting down in {delay} seconds. Run 'shutdown /a' to cancel."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def restart_pc(delay=30):
    try:
        subprocess.run(f"shutdown /r /t {int(delay)}", shell=True)
        return {"status": "success", "message": f"Restarting in {delay} seconds. Run 'shutdown /a' to cancel."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def cancel_shutdown():
    try:
        subprocess.run("shutdown /a", shell=True)
        return {"status": "success", "message": "Shutdown cancelled"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_clipboard():
    try:
        import subprocess
        result = subprocess.run("powershell Get-Clipboard", shell=True, capture_output=True, text=True)
        return {"status": "success", "content": result.stdout.strip()[:1000]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def set_clipboard(text):
    try:
        subprocess.run(f'powershell "Set-Clipboard -Value \'{text}\'"', shell=True)
        return {"status": "success", "message": f"Copied to clipboard: {text[:50]}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def set_wallpaper(path):
    try:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)
        return {"status": "success", "message": f"Wallpaper set to: {path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def toggle_wifi(state):
    try:
        action = "enable" if state.lower() in ("on", "enable", "true") else "disable"
        subprocess.run(f'netsh interface set interface "Wi-Fi" {action}', shell=True, capture_output=True)
        return {"status": "success", "message": f"Wi-Fi {action}d"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ================================================================
# SYSTEM INFO & MONITORING
# ================================================================

def get_system_info():
    try:
        info = {
            "os": platform.platform(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "hostname": socket.gethostname(),
            "python": platform.python_version(),
        }
        # Get RAM and CPU via wmic
        ram = subprocess.run('wmic OS get TotalVisibleMemorySize /value', shell=True, capture_output=True, text=True)
        cpu = subprocess.run('wmic cpu get LoadPercentage /value', shell=True, capture_output=True, text=True)
        info["ram_info"] = ram.stdout.strip()
        info["cpu_load"] = cpu.stdout.strip()
        return {"status": "success", "info": info}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_battery_info():
    try:
        result = subprocess.run('WMIC Path Win32_Battery Get EstimatedChargeRemaining,BatteryStatus /format:list',
                               shell=True, capture_output=True, text=True)
        return {"status": "success", "battery": result.stdout.strip()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_ip_address():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        try:
            public_ip = requests.get("https://api.ipify.org", timeout=5).text
        except:
            public_ip = "Could not fetch"
        return {"status": "success", "hostname": hostname, "local_ip": local_ip, "public_ip": public_ip}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def list_processes():
    try:
        result = subprocess.run('tasklist /FO CSV /NH', shell=True, capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')[:20]
        return {"status": "success", "processes": lines}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def kill_process(pid):
    try:
        subprocess.run(f"taskkill /PID {pid} /F", shell=True)
        return {"status": "success", "message": f"Killed process {pid}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_disk_usage():
    try:
        result = subprocess.run('wmic logicaldisk get size,freespace,caption /format:list',
                               shell=True, capture_output=True, text=True)
        return {"status": "success", "disks": result.stdout.strip()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_date_time():
    try:
        now = datetime.datetime.now()
        return {
            "status": "success",
            "date": now.strftime("%A, %B %d, %Y"),
            "time": now.strftime("%I:%M:%S %p"),
            "timestamp": now.isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def send_notification(title, message):
    try:
        ps = f'''
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
        $template = @"
        <toast>
            <visual>
                <binding template="ToastText02">
                    <text id="1">{title}</text>
                    <text id="2">{message}</text>
                </binding>
            </visual>
        </toast>
"@
        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($template)
        $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Diana").Show($toast)
        '''
        subprocess.run(["powershell", "-Command", ps], capture_output=True)
        return {"status": "success", "message": f"Notification sent: {title}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ================================================================
# WEB & INFORMATION
# ================================================================

def web_search(query):
    try:
        url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        results = []
        if data.get("Abstract"):
            results.append(f"Summary: {data['Abstract']}")
        for topic in data.get("RelatedTopics", [])[:5]:
            if isinstance(topic, dict) and "Text" in topic:
                results.append(topic["Text"])
        if not results:
            return {"status": "success", "message": f"No instant answer for '{query}'. Try browser search.", "results": []}
        return {"status": "success", "results": results[:5]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_weather(city):
    try:
        r = requests.get(f"https://wttr.in/{city}?format=j1", timeout=10)
        c = r.json()["current_condition"][0]
        return {"status": "success", "weather": {
            "temp_c": c["temp_C"], "feels_like": c["FeelsLikeC"],
            "desc": c["weatherDesc"][0]["value"],
            "humidity": c["humidity"], "wind_kmph": c["windspeedKmph"], "city": city
        }}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def open_youtube(query):
    try:
        webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
        return {"status": "success", "message": f"YouTube: {query}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def open_url(url):
    try:
        webbrowser.open(url)
        return {"status": "success", "message": f"Opened: {url}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def read_webpage(url):
    try:
        import re
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        text = re.sub(r'<[^>]+>', ' ', r.text)
        text = re.sub(r'\s+', ' ', text).strip()
        return {"status": "success", "content": text[:2000]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def calculate(expression):
    try:
        allowed = set("0123456789+-*/().% ")
        if not all(c in allowed for c in expression):
            return {"status": "error", "message": "Invalid characters in expression"}
        result = eval(expression)
        return {"status": "success", "expression": expression, "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def translate_text(text, target_language):
    try:
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|{target_language}"
        r = requests.get(url, timeout=10)
        data = r.json()
        translated = data["responseData"]["translatedText"]
        return {"status": "success", "original": text, "translated": translated, "language": target_language}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def generate_password(length=16):
    try:
        length = max(8, min(64, int(length)))
        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.SystemRandom().choice(chars) for _ in range(length))
        return {"status": "success", "password": password, "length": length}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ================================================================
# FILE MANAGEMENT
# ================================================================

def find_files(directory, pattern):
    try:
        files = glob.glob(os.path.join(directory, "**", pattern), recursive=True)
        return {"status": "success", "files": files[:30], "count": len(files)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def move_file(source, destination):
    try:
        shutil.move(source, destination)
        return {"status": "success", "message": f"Moved to {destination}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def copy_file(source, destination):
    try:
        shutil.copy2(source, destination)
        return {"status": "success", "message": f"Copied to {destination}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def delete_file(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        return {"status": "success", "message": f"Deleted {path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def rename_file(old_path, new_path):
    try:
        os.rename(old_path, new_path)
        return {"status": "success", "message": f"Renamed to {new_path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def read_file_contents(path, num_lines=10):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [f.readline().rstrip() for _ in range(int(num_lines))]
        return {"status": "success", "content": "\n".join(lines)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def write_file_contents(path, content):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "success", "message": f"Written to {path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def append_to_file(path, content):
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content + "\n")
        return {"status": "success", "message": f"Appended to {path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def create_folder(path):
    try:
        os.makedirs(path, exist_ok=True)
        return {"status": "success", "message": f"Created: {path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_file_info(path):
    try:
        stat = os.stat(path)
        return {"status": "success", "info": {
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / 1024 / 1024, 2),
            "created": datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "is_file": os.path.isfile(path),
            "is_dir": os.path.isdir(path)
        }}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def list_directory(path):
    try:
        items = os.listdir(path)
        return {"status": "success", "items": items[:50], "count": len(items)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def zip_files(source_path, output_path):
    try:
        if os.path.isdir(source_path):
            shutil.make_archive(output_path.replace('.zip',''), 'zip', source_path)
        else:
            with zipfile.ZipFile(output_path, 'w') as z:
                z.write(source_path, os.path.basename(source_path))
        return {"status": "success", "message": f"Zipped to {output_path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def unzip_file(zip_path, destination):
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(destination)
        return {"status": "success", "message": f"Extracted to {destination}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ================================================================
# NOTES
# ================================================================

def take_note(note):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(NOTES_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {note}\n")
        return {"status": "success", "message": f"Note saved: {note[:50]}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def read_notes():
    try:
        if not os.path.exists(NOTES_FILE):
            return {"status": "success", "notes": "No notes yet."}
        with open(NOTES_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"status": "success", "notes": content[-2000:]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def clear_notes():
    try:
        if os.path.exists(NOTES_FILE):
            os.remove(NOTES_FILE)
        return {"status": "success", "message": "All notes cleared"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ================================================================
# MEMORY & CONTEXT
# ================================================================

def _load_memory():
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except: pass
    return {}

def _save_memory(data):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def remember(key, value):
    try:
        mem = _load_memory()
        mem[key] = {"value": value, "saved_at": datetime.datetime.now().isoformat()}
        _save_memory(mem)
        return {"status": "success", "message": f"Remembered: {key} = {value}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def recall(key):
    try:
        mem = _load_memory()
        if key in mem:
            return {"status": "success", "key": key, "value": mem[key]["value"]}
        matches = {k: v["value"] for k, v in mem.items() if key.lower() in k.lower()}
        if matches:
            return {"status": "success", "matches": matches}
        return {"status": "not_found", "message": f"No memory: {key}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def recall_all():
    try:
        mem = _load_memory()
        if not mem:
            return {"status": "success", "memories": {}, "message": "No memories yet."}
        return {"status": "success", "memories": {k: v["value"] for k, v in mem.items()}}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def forget(key):
    try:
        mem = _load_memory()
        if key in mem:
            del mem[key]
            _save_memory(mem)
            return {"status": "success", "message": f"Forgot: {key}"}
        return {"status": "not_found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def save_conversation(user_said, diana_said):
    try:
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        history.append({"time": datetime.datetime.now().isoformat(), "user": user_said, "diana": diana_said})
        history = history[-100:]
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_daily_briefing():
    try:
        now = datetime.datetime.now()
        briefing = {"date": now.strftime("%A, %B %d, %Y"), "time": now.strftime("%I:%M %p")}
        try:
            w = get_weather("auto")
            if w["status"] == "success": briefing["weather"] = w["weather"]
        except: briefing["weather"] = "unavailable"
        mem = _load_memory()
        briefing["memories"] = {k: v["value"] for k, v in mem.items()} if mem else "none"
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, 'r') as f:
                briefing["recent_notes"] = f.read()[-500:]
        return {"status": "success", "briefing": briefing}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def set_timer(seconds, message="Timer done!"):
    try:
        import threading
        def _timer():
            time.sleep(int(seconds))
            send_notification("Diana Timer", message)
            pyautogui.alert(message, "Diana Timer")
        t = threading.Thread(target=_timer, daemon=True)
        t.start()
        return {"status": "success", "message": f"Timer set for {seconds} seconds: {message}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def trigger_mobile_webhook(webhook_id, payload=None):
    try:
        base_url = os.environ.get("TASKER_WEBHOOK_URL")
        if not base_url:
            return {"status": "error", "message": "TASKER_WEBHOOK_URL not set"}
        r = requests.post(f"{base_url.rstrip('/')}/{webhook_id}", json=payload or {})
        return {"status": "success", "code": r.status_code}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ================================================================
# EXPORT ALL 50+ TOOLS
# ================================================================
MCP_TOOLS = {
    # System Control
    "open_application": open_application,
    "close_application": close_application,
    "run_system_command": run_system_command,
    "simulate_typing": simulate_typing,
    "simulate_hotkey": simulate_hotkey,
    "press_key": press_key,
    "simulate_click": simulate_click,
    "move_mouse": move_mouse,
    "scroll_mouse": scroll_mouse,
    "drag_mouse": drag_mouse,
    "double_click": double_click,
    "get_screen_size": get_screen_size,
    "focus_window": focus_window,
    "list_open_windows": list_open_windows,
    "take_screenshot": take_screenshot,
    # System Power
    "set_volume": set_volume,
    "mute_volume": mute_volume,
    "set_brightness": set_brightness,
    "lock_pc": lock_pc,
    "sleep_pc": sleep_pc,
    "shutdown_pc": shutdown_pc,
    "restart_pc": restart_pc,
    "cancel_shutdown": cancel_shutdown,
    "get_clipboard": get_clipboard,
    "set_clipboard": set_clipboard,
    "set_wallpaper": set_wallpaper,
    "toggle_wifi": toggle_wifi,
    "send_notification": send_notification,
    # System Info
    "get_system_info": get_system_info,
    "get_battery_info": get_battery_info,
    "get_ip_address": get_ip_address,
    "list_processes": list_processes,
    "kill_process": kill_process,
    "get_disk_usage": get_disk_usage,
    "get_date_time": get_date_time,
    # Web
    "web_search": web_search,
    "get_weather": get_weather,
    "open_youtube": open_youtube,
    "open_url": open_url,
    "read_webpage": read_webpage,
    "calculate": calculate,
    "translate_text": translate_text,
    "generate_password": generate_password,
    # Files
    "find_files": find_files,
    "move_file": move_file,
    "copy_file": copy_file,
    "delete_file": delete_file,
    "rename_file": rename_file,
    "read_file_contents": read_file_contents,
    "write_file_contents": write_file_contents,
    "append_to_file": append_to_file,
    "create_folder": create_folder,
    "get_file_info": get_file_info,
    "list_directory": list_directory,
    "zip_files": zip_files,
    "unzip_file": unzip_file,
    # Notes
    "take_note": take_note,
    "read_notes": read_notes,
    "clear_notes": clear_notes,
    # Memory
    "remember": remember,
    "recall": recall,
    "recall_all": recall_all,
    "forget": forget,
    "save_conversation": save_conversation,
    "get_daily_briefing": get_daily_briefing,
    "set_timer": set_timer,
    # Mobile
    "trigger_mobile_webhook": trigger_mobile_webhook,
}
