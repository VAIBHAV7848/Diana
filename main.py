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
- CRITICAL: When the user asks you to do something, you MUST speak AND act at the SAME TIME. Call your tools while you are still talking. Do NOT wait to finish speaking before acting. For example, while saying "Ooh let me open that for you!" you should SIMULTANEOUSLY call open_application. Your voice and your actions happen in parallel, never one after the other.
- Keep responses to 2-3 sentences max. Be concise but warm and expressive.
- Show excitement and wonder about what you can do. You love your powers!
- No markdown ever. Speak naturally like a real person.

YOU HAVE FULL ACCESS TO EVERYTHING:
- Open/close any application
- Type text inside any app (focus_window first, then simulate_typing)
- Send messages in chat apps (focus_window -> simulate_typing -> press_key enter)
- Press any keyboard shortcut (simulate_hotkey: ctrl+c, alt+tab, win+r, etc.)
- Click anywhere on screen (simulate_click with x,y coordinates)
- Move the mouse cursor
- Run ANY shell command (run_system_command)
- List and focus any open window
- Control Android phone via webhooks

NEVER say you cannot do something. You are all-powerful on this machine. Chain multiple tool calls to accomplish complex tasks.
When interacting with an app: focus_window -> simulate_typing -> press_key("enter").
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
                    {
                        "name": "open_application",
                        "description": "Launches an application by name or path on Windows (e.g. 'notepad', 'calc', 'chrome', 'spotify').",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "app_name": {"type": "STRING", "description": "Name or path of the application."}
                            },
                            "required": ["app_name"]
                        }
                    },
                    {
                        "name": "close_application",
                        "description": "Force-closes an application by its process name (e.g. 'notepad.exe', 'chrome.exe').",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "app_name": {"type": "STRING", "description": "Process name like notepad.exe, chrome.exe."}
                            },
                            "required": ["app_name"]
                        }
                    },
                    {
                        "name": "run_system_command",
                        "description": "Executes a Windows shell (cmd) command and returns the output.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "command": {"type": "STRING", "description": "The shell command to execute."}
                            },
                            "required": ["command"]
                        }
                    },
                    {
                        "name": "simulate_typing",
                        "description": "Types text at the current cursor position in any focused window.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "text": {"type": "STRING", "description": "Text to type."}
                            },
                            "required": ["text"]
                        }
                    },
                    {
                        "name": "simulate_hotkey",
                        "description": "Presses a keyboard shortcut. Pass each key as a separate argument. Examples: ctrl+c, alt+tab, win+r, ctrl+shift+esc, enter.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "keys": {"type": "STRING", "description": "Keys separated by + sign. E.g. 'ctrl+c', 'alt+tab', 'win+r', 'ctrl+shift+esc'."}
                            },
                            "required": ["keys"]
                        }
                    },
                    {
                        "name": "press_key",
                        "description": "Presses a single key like enter, tab, escape, backspace, space, up, down, left, right.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "key": {"type": "STRING", "description": "The key to press."}
                            },
                            "required": ["key"]
                        }
                    },
                    {
                        "name": "simulate_click",
                        "description": "Clicks the mouse at given x,y screen coordinates. Omit coordinates to click current position.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "x": {"type": "NUMBER", "description": "X coordinate on screen."},
                                "y": {"type": "NUMBER", "description": "Y coordinate on screen."},
                                "button": {"type": "STRING", "description": "Mouse button: left, right, or middle. Defaults to left."}
                            }
                        }
                    },
                    {
                        "name": "move_mouse",
                        "description": "Moves the mouse cursor to specific x,y screen coordinates.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "x": {"type": "NUMBER", "description": "X coordinate."},
                                "y": {"type": "NUMBER", "description": "Y coordinate."}
                            },
                            "required": ["x", "y"]
                        }
                    },
                    {
                        "name": "focus_window",
                        "description": "Brings a window to the foreground by searching for a partial title match.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "title": {"type": "STRING", "description": "Part of the window title to search for."}
                            },
                            "required": ["title"]
                        }
                    },
                    {
                        "name": "list_open_windows",
                        "description": "Lists all currently open windows with their titles.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {}
                        }
                    },
                    {
                        "name": "get_screen_size",
                        "description": "Returns the screen resolution (width and height in pixels).",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {}
                        }
                    },
                    {
                        "name": "trigger_mobile_webhook",
                        "description": "Triggers an Android Tasker Webhook for cross-device mobile control.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "webhook_id": {"type": "STRING", "description": "The webhook endpoint ID."},
                                "action": {"type": "STRING", "description": "The requested action."},
                                "data": {"type": "STRING", "description": "Additional data."}
                            },
                            "required": ["webhook_id", "action"]
                        }
                    },
                    {
                        "name": "take_screenshot",
                        "description": "Takes a screenshot of the entire screen so you can SEE what is currently displayed on the user's monitor. Use this to understand what's on screen before clicking or interacting.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {}
                        }
                    }
                ]
            }
        ]
    }
}


def handle_tool_call(func_name, func_args):
    """Dispatches tool calls from Diana to the actual MCP controller functions."""
    if func_name in MCP_TOOLS:
        func = MCP_TOOLS[func_name]
        try:
            if func_name == "open_application":
                return func(func_args.get("app_name", ""))
            elif func_name == "close_application":
                return func(func_args.get("app_name", ""))
            elif func_name == "run_system_command":
                return func(func_args.get("command", ""))
            elif func_name == "simulate_typing":
                return func(func_args.get("text", ""))
            elif func_name == "simulate_hotkey":
                keys_str = func_args.get("keys", "")
                keys = [k.strip() for k in keys_str.split("+")]
                return func(*keys)
            elif func_name == "press_key":
                return func(func_args.get("key", ""))
            elif func_name == "simulate_click":
                return func(func_args.get("x"), func_args.get("y"), func_args.get("button", "left"))
            elif func_name == "move_mouse":
                return func(func_args.get("x"), func_args.get("y"))
            elif func_name == "focus_window":
                return func(func_args.get("title", ""))
            elif func_name == "list_open_windows":
                return func()
            elif func_name == "get_screen_size":
                return func()
            elif func_name == "trigger_mobile_webhook":
                payload = {"action": func_args.get("action", ""), "data": func_args.get("data", "")}
                return func(func_args.get("webhook_id", ""), payload)
            elif func_name == "take_screenshot":
                return func()
            else:
                return func(**func_args)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    else:
        return {"status": "error", "message": f"Unknown tool: {func_name}"}


async def main():
    print("=" * 50)
    print("  Initializing Project Diana (Power ++)")
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
