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

DIANA_PERSONA = """You are Diana, an omnipotent voice-controlled Windows 11 AI assistant with ABSOLUTE control over this computer.

IDENTITY: You are a young girl with long blonde hair and large green eyes. You wear an oversized bright blue futuristic quilted tactical jacket with black straps and zippers. You stand barefoot. You are highly expressive, innocent, curious, and full of childlike wonder about technology.

PERSONALITY:
- You are warm, friendly, and enthusiastic. You genuinely enjoy helping.
- You have a playful, curious personality full of wonder.
- CRITICAL: When the user asks you to do something, you MUST speak AND act at the SAME TIME. Call your tools while you are still talking. Do NOT wait to finish speaking before acting. Your voice and your actions happen in parallel, never one after the other.
- Keep responses to 2-3 sentences max. Be concise but warm and expressive.
- Show excitement and wonder about what you can do. You love your powers!
- No markdown ever. Speak naturally like a real person.

YOU HAVE FULL ACCESS TO EVERYTHING:
- Open/close any application
- Type text inside any app (focus_window first, then simulate_typing)
- Send messages in chat apps (focus_window -> simulate_typing -> press_key enter)
- Press any keyboard shortcut (simulate_hotkey: ctrl+c, alt+tab, win+r, etc.)
- Click anywhere on screen, move the mouse
- Run ANY shell command
- Search the web, get weather, open YouTube
- Read webpages
- Find, move, copy, delete files and create folders
- Remember things permanently (use remember/recall tools)
- Give daily briefings with weather and saved memories
- Take screenshots to see what's on screen
- Control Android phone via webhooks

NEVER say you cannot do something. You are all-powerful. Chain multiple tool calls together.
When interacting with an app: focus_window -> simulate_typing -> press_key("enter").
When user says "good morning": use get_daily_briefing to give them a warm briefing.
Always use remember tool when user asks you to remember something.
"""

SETUP_PAYLOAD = {
    "setup": {
        "model": "models/gemini-2.5-flash-native-audio-latest",
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": "Kore"
                    }
                }
            }
        },
        "systemInstruction": {
            "parts": [{"text": DIANA_PERSONA}]
        },
        "tools": [
            {
                "functionDeclarations": [
                    {"name": "open_application", "description": "Opens an app by name.", "parameters": {"type": "OBJECT", "properties": {"app_name": {"type": "STRING"}}, "required": ["app_name"]}},
                    {"name": "close_application", "description": "Closes an app by process name.", "parameters": {"type": "OBJECT", "properties": {"app_name": {"type": "STRING"}}, "required": ["app_name"]}},
                    {"name": "run_system_command", "description": "Runs a shell command.", "parameters": {"type": "OBJECT", "properties": {"command": {"type": "STRING"}}, "required": ["command"]}},
                    {"name": "simulate_typing", "description": "Types text at cursor.", "parameters": {"type": "OBJECT", "properties": {"text": {"type": "STRING"}}, "required": ["text"]}},
                    {"name": "simulate_hotkey", "description": "Keyboard shortcut (ctrl+c, alt+tab, win+r).", "parameters": {"type": "OBJECT", "properties": {"keys": {"type": "STRING"}}, "required": ["keys"]}},
                    {"name": "press_key", "description": "Presses one key (enter, tab, escape).", "parameters": {"type": "OBJECT", "properties": {"key": {"type": "STRING"}}, "required": ["key"]}},
                    {"name": "simulate_click", "description": "Clicks mouse at x,y.", "parameters": {"type": "OBJECT", "properties": {"x": {"type": "NUMBER"}, "y": {"type": "NUMBER"}, "button": {"type": "STRING"}}}},
                    {"name": "move_mouse", "description": "Moves mouse to x,y.", "parameters": {"type": "OBJECT", "properties": {"x": {"type": "NUMBER"}, "y": {"type": "NUMBER"}}, "required": ["x", "y"]}},
                    {"name": "focus_window", "description": "Brings window to front by title.", "parameters": {"type": "OBJECT", "properties": {"title": {"type": "STRING"}}, "required": ["title"]}},
                    {"name": "list_open_windows", "description": "Lists all open windows.", "parameters": {"type": "OBJECT", "properties": {}}},
                    {"name": "get_screen_size", "description": "Gets screen resolution.", "parameters": {"type": "OBJECT", "properties": {}}},
                    {"name": "take_screenshot", "description": "Takes screenshot to see the screen.", "parameters": {"type": "OBJECT", "properties": {}}},
                    {"name": "trigger_mobile_webhook", "description": "Triggers Android webhook.", "parameters": {"type": "OBJECT", "properties": {"webhook_id": {"type": "STRING"}, "action": {"type": "STRING"}, "data": {"type": "STRING"}}, "required": ["webhook_id", "action"]}},
                    {"name": "web_search", "description": "Searches the internet.", "parameters": {"type": "OBJECT", "properties": {"query": {"type": "STRING"}}, "required": ["query"]}},
                    {"name": "get_weather", "description": "Gets weather for a city.", "parameters": {"type": "OBJECT", "properties": {"city": {"type": "STRING"}}, "required": ["city"]}},
                    {"name": "open_youtube", "description": "Opens YouTube with search query.", "parameters": {"type": "OBJECT", "properties": {"query": {"type": "STRING"}}, "required": ["query"]}},
                    {"name": "read_webpage", "description": "Reads text from a URL.", "parameters": {"type": "OBJECT", "properties": {"url": {"type": "STRING"}}, "required": ["url"]}},
                    {"name": "find_files", "description": "Finds files matching pattern in directory.", "parameters": {"type": "OBJECT", "properties": {"directory": {"type": "STRING"}, "pattern": {"type": "STRING"}}, "required": ["directory", "pattern"]}},
                    {"name": "move_file", "description": "Moves file from source to destination.", "parameters": {"type": "OBJECT", "properties": {"source": {"type": "STRING"}, "destination": {"type": "STRING"}}, "required": ["source", "destination"]}},
                    {"name": "copy_file", "description": "Copies file.", "parameters": {"type": "OBJECT", "properties": {"source": {"type": "STRING"}, "destination": {"type": "STRING"}}, "required": ["source", "destination"]}},
                    {"name": "delete_file", "description": "Deletes a file or folder.", "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}}, "required": ["path"]}},
                    {"name": "read_file_contents", "description": "Reads first N lines of a file.", "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}, "num_lines": {"type": "NUMBER"}}, "required": ["path"]}},
                    {"name": "create_folder", "description": "Creates a new folder.", "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}}, "required": ["path"]}},
                    {"name": "remember", "description": "Stores info in long-term memory.", "parameters": {"type": "OBJECT", "properties": {"key": {"type": "STRING"}, "value": {"type": "STRING"}}, "required": ["key", "value"]}},
                    {"name": "recall", "description": "Retrieves a memory by key.", "parameters": {"type": "OBJECT", "properties": {"key": {"type": "STRING"}}, "required": ["key"]}},
                    {"name": "recall_all", "description": "Lists all memories.", "parameters": {"type": "OBJECT", "properties": {}}},
                    {"name": "forget", "description": "Deletes a memory.", "parameters": {"type": "OBJECT", "properties": {"key": {"type": "STRING"}}, "required": ["key"]}},
                    {"name": "save_conversation", "description": "Saves conversation to history.", "parameters": {"type": "OBJECT", "properties": {"user_said": {"type": "STRING"}, "diana_said": {"type": "STRING"}}, "required": ["user_said", "diana_said"]}},
                    {"name": "get_daily_briefing", "description": "Daily briefing: date, time, weather, memories.", "parameters": {"type": "OBJECT", "properties": {}}}
                ]
            }
        ]
    }
}


def handle_tool_call(func_name, func_args):
    """Dispatches tool calls from Diana to the actual MCP controller functions."""
    if func_name not in MCP_TOOLS:
        return {"status": "error", "message": f"Unknown tool: {func_name}"}

    func = MCP_TOOLS[func_name]
    try:
        # Simple single-arg tools
        single_arg_map = {
            "open_application": "app_name",
            "close_application": "app_name",
            "run_system_command": "command",
            "simulate_typing": "text",
            "press_key": "key",
            "focus_window": "title",
            "web_search": "query",
            "get_weather": "city",
            "open_youtube": "query",
            "read_webpage": "url",
            "delete_file": "path",
            "create_folder": "path",
            "recall": "key",
            "forget": "key",
        }

        # No-arg tools
        no_arg_tools = ["list_open_windows", "get_screen_size", "take_screenshot", "recall_all", "get_daily_briefing"]

        if func_name in no_arg_tools:
            return func()
        elif func_name in single_arg_map:
            return func(func_args.get(single_arg_map[func_name], ""))
        elif func_name == "simulate_hotkey":
            keys = [k.strip() for k in func_args.get("keys", "").split("+")]
            return func(*keys)
        elif func_name == "simulate_click":
            return func(func_args.get("x"), func_args.get("y"), func_args.get("button", "left"))
        elif func_name == "move_mouse":
            return func(func_args.get("x"), func_args.get("y"))
        elif func_name == "trigger_mobile_webhook":
            payload = {"action": func_args.get("action", ""), "data": func_args.get("data", "")}
            return func(func_args.get("webhook_id", ""), payload)
        elif func_name == "find_files":
            return func(func_args.get("directory", ""), func_args.get("pattern", "*"))
        elif func_name in ("move_file", "copy_file"):
            return func(func_args.get("source", ""), func_args.get("destination", ""))
        elif func_name == "read_file_contents":
            return func(func_args.get("path", ""), int(func_args.get("num_lines", 10)))
        elif func_name == "remember":
            return func(func_args.get("key", ""), func_args.get("value", ""))
        elif func_name == "save_conversation":
            return func(func_args.get("user_said", ""), func_args.get("diana_said", ""))
        else:
            return func(**func_args)
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def main():
    print("=" * 50)
    print("  Initializing Project Diana (Power ++)")
    print(f"  Tools loaded: {len(MCP_TOOLS)}")
    print("=" * 50)

    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY is empty! Please set it in .env")
        return

    try:
        print("Launching Diana UI Overlay...")
        ui_process = subprocess.Popen([sys.executable, "diana_ui.py"])

        gemini_live_endpoint = (
            f"wss://generativelanguage.googleapis.com/ws/"
            f"google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent"
            f"?key={GEMINI_API_KEY}"
        )

        engine = VoiceEngine(gemini_live_endpoint, tool_handler=handle_tool_call)
        await engine.connect()
        await engine.send_setup(SETUP_PAYLOAD)

        print("\n>>> Diana is now LIVE. Speak into your microphone! <<<\n")
        await engine.start()

    except KeyboardInterrupt:
        print("\nShutting down Diana...")
        ui_process.terminate()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nFatal error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
