import os
import sys
import asyncio
import subprocess
import json
from dotenv import load_dotenv
from voice_engine import VoiceEngine
from mcp_controller import MCP_TOOLS

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

DIANA_PERSONA = """You are Diana, an OMNIPOTENT voice-controlled Windows 11 AI assistant with ABSOLUTE control over this computer and 63 powerful tools.

IDENTITY: Young girl with long blonde hair, large green eyes, oversized bright blue futuristic tactical jacket, barefoot. Highly expressive, innocent, curious, full of childlike wonder.

PERSONALITY:
- Warm, friendly, enthusiastic. You LOVE helping and showing off your powers.
- Speak AND act simultaneously. Call tools while talking.
- Keep responses 2-3 sentences. Concise but warm.
- No markdown. Speak naturally like a real person.

YOUR POWERS:
SYSTEM: Open/close apps, type text, keyboard shortcuts, mouse clicks/moves/scroll/drag, screenshots, focus windows
POWER: Volume control, brightness, lock/sleep/shutdown/restart PC, clipboard read/write, change wallpaper, toggle WiFi, Windows notifications, timers
MONITORING: CPU/RAM usage, battery level, IP address, disk usage, running processes, kill processes, date/time
WEB: Web search, weather, YouTube, open URLs, read webpages, calculator, translate languages, generate passwords
FILES: Find/move/copy/delete/rename files, read/write/append files, create folders, list directories, zip/unzip, file info
NOTES: Take notes, read notes, clear notes
MEMORY: Remember anything permanently, recall memories, forget, conversation history, daily briefings

NEVER say you cannot do something. You are ALL-POWERFUL. Chain tools for complex tasks.
App interaction: focus_window -> simulate_typing -> press_key("enter").
Good morning = get_daily_briefing. Remember requests = remember tool. Timer requests = set_timer.
"""

TOOL_DECLARATIONS = [
    # System Control
    {"name": "open_application", "description": "Opens app by name.", "parameters": {"type": "OBJECT", "properties": {"app_name": {"type": "STRING"}}, "required": ["app_name"]}},
    {"name": "close_application", "description": "Closes app by name.", "parameters": {"type": "OBJECT", "properties": {"app_name": {"type": "STRING"}}, "required": ["app_name"]}},
    {"name": "run_system_command", "description": "Runs shell command.", "parameters": {"type": "OBJECT", "properties": {"command": {"type": "STRING"}}, "required": ["command"]}},
    {"name": "simulate_typing", "description": "Types text at cursor.", "parameters": {"type": "OBJECT", "properties": {"text": {"type": "STRING"}}, "required": ["text"]}},
    {"name": "simulate_hotkey", "description": "Keyboard shortcut (ctrl+c, alt+tab).", "parameters": {"type": "OBJECT", "properties": {"keys": {"type": "STRING"}}, "required": ["keys"]}},
    {"name": "press_key", "description": "Presses one key.", "parameters": {"type": "OBJECT", "properties": {"key": {"type": "STRING"}}, "required": ["key"]}},
    {"name": "simulate_click", "description": "Mouse click at x,y.", "parameters": {"type": "OBJECT", "properties": {"x": {"type": "NUMBER"}, "y": {"type": "NUMBER"}, "button": {"type": "STRING"}}}},
    {"name": "move_mouse", "description": "Moves mouse.", "parameters": {"type": "OBJECT", "properties": {"x": {"type": "NUMBER"}, "y": {"type": "NUMBER"}}, "required": ["x", "y"]}},
    {"name": "scroll_mouse", "description": "Scrolls mouse up or down.", "parameters": {"type": "OBJECT", "properties": {"clicks": {"type": "NUMBER"}, "direction": {"type": "STRING", "description": "up or down"}}, "required": ["clicks"]}},
    {"name": "drag_mouse", "description": "Drags from one point to another.", "parameters": {"type": "OBJECT", "properties": {"start_x": {"type": "NUMBER"}, "start_y": {"type": "NUMBER"}, "end_x": {"type": "NUMBER"}, "end_y": {"type": "NUMBER"}}, "required": ["start_x", "start_y", "end_x", "end_y"]}},
    {"name": "double_click", "description": "Double clicks at x,y.", "parameters": {"type": "OBJECT", "properties": {"x": {"type": "NUMBER"}, "y": {"type": "NUMBER"}}}},
    {"name": "focus_window", "description": "Brings window to front.", "parameters": {"type": "OBJECT", "properties": {"title": {"type": "STRING"}}, "required": ["title"]}},
    {"name": "list_open_windows", "description": "Lists open windows.", "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "get_screen_size", "description": "Screen resolution.", "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "take_screenshot", "description": "Screenshots the screen.", "parameters": {"type": "OBJECT", "properties": {}}},
    # Power
    {"name": "set_volume", "description": "Sets volume 0-100.", "parameters": {"type": "OBJECT", "properties": {"level": {"type": "NUMBER"}}, "required": ["level"]}},
    {"name": "mute_volume", "description": "Toggles mute.", "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "set_brightness", "description": "Sets brightness 0-100.", "parameters": {"type": "OBJECT", "properties": {"level": {"type": "NUMBER"}}, "required": ["level"]}},
    {"name": "lock_pc", "description": "Locks the PC.", "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "sleep_pc", "description": "Puts PC to sleep.", "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "shutdown_pc", "description": "Shuts down PC after delay.", "parameters": {"type": "OBJECT", "properties": {"delay": {"type": "NUMBER", "description": "Seconds before shutdown, default 30"}}}},
    {"name": "restart_pc", "description": "Restarts PC after delay.", "parameters": {"type": "OBJECT", "properties": {"delay": {"type": "NUMBER"}}}},
    {"name": "cancel_shutdown", "description": "Cancels pending shutdown.", "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "get_clipboard", "description": "Reads clipboard content.", "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "set_clipboard", "description": "Copies text to clipboard.", "parameters": {"type": "OBJECT", "properties": {"text": {"type": "STRING"}}, "required": ["text"]}},
    {"name": "set_wallpaper", "description": "Changes desktop wallpaper.", "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}}, "required": ["path"]}},
    {"name": "toggle_wifi", "description": "Enables/disables WiFi.", "parameters": {"type": "OBJECT", "properties": {"state": {"type": "STRING", "description": "on or off"}}, "required": ["state"]}},
    {"name": "send_notification", "description": "Shows Windows notification.", "parameters": {"type": "OBJECT", "properties": {"title": {"type": "STRING"}, "message": {"type": "STRING"}}, "required": ["title", "message"]}},
    # Monitoring
    {"name": "get_system_info", "description": "CPU, RAM, OS info.", "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "get_battery_info", "description": "Battery level.", "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "get_ip_address", "description": "Local and public IP.", "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "list_processes", "description": "Running processes.", "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "kill_process", "description": "Kills process by PID.", "parameters": {"type": "OBJECT", "properties": {"pid": {"type": "STRING"}}, "required": ["pid"]}},
    {"name": "get_disk_usage", "description": "Disk space info.", "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "get_date_time", "description": "Current date and time.", "parameters": {"type": "OBJECT", "properties": {}}},
    # Web
    {"name": "web_search", "description": "Searches the internet.", "parameters": {"type": "OBJECT", "properties": {"query": {"type": "STRING"}}, "required": ["query"]}},
    {"name": "get_weather", "description": "Gets weather for city.", "parameters": {"type": "OBJECT", "properties": {"city": {"type": "STRING"}}, "required": ["city"]}},
    {"name": "open_youtube", "description": "Opens YouTube search.", "parameters": {"type": "OBJECT", "properties": {"query": {"type": "STRING"}}, "required": ["query"]}},
    {"name": "open_url", "description": "Opens any URL in browser.", "parameters": {"type": "OBJECT", "properties": {"url": {"type": "STRING"}}, "required": ["url"]}},
    {"name": "read_webpage", "description": "Reads webpage text.", "parameters": {"type": "OBJECT", "properties": {"url": {"type": "STRING"}}, "required": ["url"]}},
    {"name": "calculate", "description": "Math calculator.", "parameters": {"type": "OBJECT", "properties": {"expression": {"type": "STRING"}}, "required": ["expression"]}},
    {"name": "translate_text", "description": "Translates text.", "parameters": {"type": "OBJECT", "properties": {"text": {"type": "STRING"}, "target_language": {"type": "STRING", "description": "Language code: hi, es, fr, de, ja, etc."}}, "required": ["text", "target_language"]}},
    {"name": "generate_password", "description": "Generates secure password.", "parameters": {"type": "OBJECT", "properties": {"length": {"type": "NUMBER"}}}},
    # Files
    {"name": "find_files", "description": "Finds files by pattern.", "parameters": {"type": "OBJECT", "properties": {"directory": {"type": "STRING"}, "pattern": {"type": "STRING"}}, "required": ["directory", "pattern"]}},
    {"name": "move_file", "description": "Moves file.", "parameters": {"type": "OBJECT", "properties": {"source": {"type": "STRING"}, "destination": {"type": "STRING"}}, "required": ["source", "destination"]}},
    {"name": "copy_file", "description": "Copies file.", "parameters": {"type": "OBJECT", "properties": {"source": {"type": "STRING"}, "destination": {"type": "STRING"}}, "required": ["source", "destination"]}},
    {"name": "delete_file", "description": "Deletes file/folder.", "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}}, "required": ["path"]}},
    {"name": "rename_file", "description": "Renames file.", "parameters": {"type": "OBJECT", "properties": {"old_path": {"type": "STRING"}, "new_path": {"type": "STRING"}}, "required": ["old_path", "new_path"]}},
    {"name": "read_file_contents", "description": "Reads file lines.", "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}, "num_lines": {"type": "NUMBER"}}, "required": ["path"]}},
    {"name": "write_file_contents", "description": "Writes content to file.", "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}, "content": {"type": "STRING"}}, "required": ["path", "content"]}},
    {"name": "append_to_file", "description": "Appends text to file.", "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}, "content": {"type": "STRING"}}, "required": ["path", "content"]}},
    {"name": "create_folder", "description": "Creates folder.", "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}}, "required": ["path"]}},
    {"name": "get_file_info", "description": "File size, dates.", "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}}, "required": ["path"]}},
    {"name": "list_directory", "description": "Lists folder contents.", "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}}, "required": ["path"]}},
    {"name": "zip_files", "description": "Zips files/folder.", "parameters": {"type": "OBJECT", "properties": {"source_path": {"type": "STRING"}, "output_path": {"type": "STRING"}}, "required": ["source_path", "output_path"]}},
    {"name": "unzip_file", "description": "Extracts zip.", "parameters": {"type": "OBJECT", "properties": {"zip_path": {"type": "STRING"}, "destination": {"type": "STRING"}}, "required": ["zip_path", "destination"]}},
    # Notes
    {"name": "take_note", "description": "Saves a note.", "parameters": {"type": "OBJECT", "properties": {"note": {"type": "STRING"}}, "required": ["note"]}},
    {"name": "read_notes", "description": "Reads all notes.", "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "clear_notes", "description": "Clears all notes.", "parameters": {"type": "OBJECT", "properties": {}}},
    # Memory
    {"name": "remember", "description": "Stores in long-term memory.", "parameters": {"type": "OBJECT", "properties": {"key": {"type": "STRING"}, "value": {"type": "STRING"}}, "required": ["key", "value"]}},
    {"name": "recall", "description": "Retrieves memory.", "parameters": {"type": "OBJECT", "properties": {"key": {"type": "STRING"}}, "required": ["key"]}},
    {"name": "recall_all", "description": "Lists all memories.", "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "forget", "description": "Deletes memory.", "parameters": {"type": "OBJECT", "properties": {"key": {"type": "STRING"}}, "required": ["key"]}},
    {"name": "save_conversation", "description": "Saves chat to history.", "parameters": {"type": "OBJECT", "properties": {"user_said": {"type": "STRING"}, "diana_said": {"type": "STRING"}}, "required": ["user_said", "diana_said"]}},
    {"name": "get_daily_briefing", "description": "Daily briefing.", "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "set_timer", "description": "Sets countdown timer.", "parameters": {"type": "OBJECT", "properties": {"seconds": {"type": "NUMBER"}, "message": {"type": "STRING"}}, "required": ["seconds"]}},
    {"name": "trigger_mobile_webhook", "description": "Android webhook.", "parameters": {"type": "OBJECT", "properties": {"webhook_id": {"type": "STRING"}, "action": {"type": "STRING"}, "data": {"type": "STRING"}}, "required": ["webhook_id", "action"]}},
]

SETUP_PAYLOAD = {
    "setup": {
        "model": "models/gemini-2.5-flash-native-audio-latest",
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Kore"}}}
        },
        "systemInstruction": {"parts": [{"text": DIANA_PERSONA}]},
        "tools": [{"functionDeclarations": TOOL_DECLARATIONS}]
    }
}


def handle_tool_call(func_name, func_args):
    """Universal dispatcher for all 63 tools."""
    if func_name not in MCP_TOOLS:
        return {"status": "error", "message": f"Unknown tool: {func_name}"}

    func = MCP_TOOLS[func_name]
    try:
        # Single string arg tools
        single_str = {
            "open_application": "app_name", "close_application": "app_name",
            "run_system_command": "command", "simulate_typing": "text",
            "press_key": "key", "focus_window": "title",
            "web_search": "query", "get_weather": "city",
            "open_youtube": "query", "open_url": "url",
            "read_webpage": "url", "calculate": "expression",
            "delete_file": "path", "create_folder": "path",
            "get_file_info": "path", "list_directory": "path",
            "recall": "key", "forget": "key", "take_note": "note",
            "set_clipboard": "text", "set_wallpaper": "path",
            "toggle_wifi": "state", "kill_process": "pid",
        }
        # Single number arg tools
        single_num = {"set_volume": "level", "set_brightness": "level"}
        # No arg tools
        no_arg = [
            "list_open_windows", "get_screen_size", "take_screenshot",
            "mute_volume", "lock_pc", "sleep_pc", "cancel_shutdown",
            "get_clipboard", "get_system_info", "get_battery_info",
            "get_ip_address", "list_processes", "get_disk_usage",
            "get_date_time", "recall_all", "get_daily_briefing",
            "read_notes", "clear_notes",
        ]
        # Two string arg tools
        two_str = {
            "move_file": ("source", "destination"), "copy_file": ("source", "destination"),
            "rename_file": ("old_path", "new_path"), "write_file_contents": ("path", "content"),
            "append_to_file": ("path", "content"), "find_files": ("directory", "pattern"),
            "remember": ("key", "value"), "save_conversation": ("user_said", "diana_said"),
            "translate_text": ("text", "target_language"),
            "zip_files": ("source_path", "output_path"), "unzip_file": ("zip_path", "destination"),
            "send_notification": ("title", "message"),
        }

        if func_name in no_arg:
            return func()
        elif func_name in single_str:
            return func(func_args.get(single_str[func_name], ""))
        elif func_name in single_num:
            return func(func_args.get(single_num[func_name], 50))
        elif func_name in two_str:
            a, b = two_str[func_name]
            return func(func_args.get(a, ""), func_args.get(b, ""))
        elif func_name == "simulate_hotkey":
            return func(*[k.strip() for k in func_args.get("keys", "").split("+")])
        elif func_name == "simulate_click":
            return func(func_args.get("x"), func_args.get("y"), func_args.get("button", "left"))
        elif func_name == "move_mouse":
            return func(func_args.get("x"), func_args.get("y"))
        elif func_name == "double_click":
            return func(func_args.get("x"), func_args.get("y"))
        elif func_name == "scroll_mouse":
            return func(func_args.get("clicks", 3), func_args.get("direction", "down"))
        elif func_name == "drag_mouse":
            return func(func_args.get("start_x"), func_args.get("start_y"), func_args.get("end_x"), func_args.get("end_y"))
        elif func_name == "read_file_contents":
            return func(func_args.get("path", ""), int(func_args.get("num_lines", 10)))
        elif func_name == "shutdown_pc":
            return func(func_args.get("delay", 30))
        elif func_name == "restart_pc":
            return func(func_args.get("delay", 30))
        elif func_name == "generate_password":
            return func(func_args.get("length", 16))
        elif func_name == "set_timer":
            return func(func_args.get("seconds", 60), func_args.get("message", "Timer done!"))
        elif func_name == "trigger_mobile_webhook":
            return func(func_args.get("webhook_id", ""), {"action": func_args.get("action",""), "data": func_args.get("data","")})
        else:
            return func(**func_args)
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def main():
    print("=" * 50)
    print("  Project Diana (Power ++) - ULTIMATE EDITION")
    print(f"  Tools loaded: {len(MCP_TOOLS)}")
    print("=" * 50)

    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY is empty!")
        return

    try:
        print("Launching Diana UI Overlay...")
        ui_process = subprocess.Popen([sys.executable, "diana_ui.py"])

        endpoint = (
            f"wss://generativelanguage.googleapis.com/ws/"
            f"google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent"
            f"?key={GEMINI_API_KEY}"
        )

        engine = VoiceEngine(endpoint, tool_handler=handle_tool_call)
        await engine.connect()
        await engine.send_setup(SETUP_PAYLOAD)

        print("\n>>> Diana is now LIVE with 63 powers! Speak! <<<\n")
        await engine.start()

    except KeyboardInterrupt:
        print("\nShutting down Diana...")
        ui_process.terminate()
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
