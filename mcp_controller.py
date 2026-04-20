import os
import subprocess
import requests
import json
import pyautogui
import time

# Safety: don't let pyautogui move too fast
pyautogui.PAUSE = 0.3

def open_application(app_name):
    """Launches an application by name or path."""
    try:
        os.startfile(app_name)
        return {"status": "success", "message": f"Opened {app_name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def close_application(app_name):
    """Closes an application by process name."""
    try:
        result = subprocess.run(f"taskkill /IM {app_name} /F", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return {"status": "success", "message": f"Closed {app_name}"}
        else:
            return {"status": "error", "message": result.stderr.strip()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def run_system_command(command):
    """Executes a system shell command."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
        return {
            "status": "success",
            "output": result.stdout[:1000],
            "error": result.stderr[:500]
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Command timed out after 15 seconds"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def simulate_typing(text):
    """Types out a string of text at the current cursor position."""
    try:
        pyautogui.write(text, interval=0.02)
        return {"status": "success", "message": f"Typed: {text[:50]}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def simulate_hotkey(*keys):
    """Presses a keyboard shortcut like ctrl+c, alt+tab, win+r, etc."""
    try:
        pyautogui.hotkey(*keys)
        return {"status": "success", "message": f"Pressed: {'+'.join(keys)}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def press_key(key):
    """Presses a single key like enter, tab, escape, backspace, etc."""
    try:
        pyautogui.press(key)
        return {"status": "success", "message": f"Pressed: {key}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def simulate_click(x=None, y=None, button='left'):
    """Simulates a mouse click at coordinates. If no coords given, clicks current position."""
    try:
        if x is not None and y is not None:
            pyautogui.click(x=int(x), y=int(y), button=button)
        else:
            pyautogui.click(button=button)
        return {"status": "success", "message": f"Clicked at ({x}, {y})"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def move_mouse(x, y):
    """Moves the mouse to specific screen coordinates."""
    try:
        pyautogui.moveTo(int(x), int(y))
        return {"status": "success", "message": f"Mouse moved to ({x}, {y})"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_screen_size():
    """Returns the screen resolution."""
    try:
        w, h = pyautogui.size()
        return {"status": "success", "width": w, "height": h}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def focus_window(title):
    """Brings a window to the foreground by its title."""
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(title)
        if windows:
            win = windows[0]
            win.activate()
            return {"status": "success", "message": f"Focused window: {win.title}"}
        else:
            return {"status": "error", "message": f"No window found with title containing: {title}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def list_open_windows():
    """Lists all currently open windows with their titles."""
    try:
        import pygetwindow as gw
        windows = [w.title for w in gw.getAllWindows() if w.title.strip()]
        return {"status": "success", "windows": windows[:30]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def trigger_mobile_webhook(webhook_id, payload=None):
    """Triggers an Android Tasker Webhook."""
    try:
        base_url = os.environ.get("TASKER_WEBHOOK_URL")
        if not base_url:
            return {"status": "error", "message": "TASKER_WEBHOOK_URL not configured."}
        url = f"{base_url.rstrip('/')}/{webhook_id}"
        response = requests.post(url, json=payload or {})
        return {"status": "success", "status_code": response.status_code}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def take_screenshot():
    """Takes a screenshot of the entire screen and returns a description of what's visible."""
    try:
        import io
        import base64
        screenshot = pyautogui.screenshot()
        # Resize to reduce size for the API
        screenshot = screenshot.resize((1024, 576))
        buffer = io.BytesIO()
        screenshot.save(buffer, format="JPEG", quality=60)
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        # Save locally too for reference
        screenshot.save("d:\\Diana\\Diana_Host_Assistant\\last_screenshot.jpg")
        return {
            "status": "success",
            "message": "Screenshot captured. Image data is attached.",
            "image_base64": img_base64
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Export mapping for MCP/Analytics Engine Tools
MCP_TOOLS = {
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
    "trigger_mobile_webhook": trigger_mobile_webhook,
    "take_screenshot": take_screenshot
}

