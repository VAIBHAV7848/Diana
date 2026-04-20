import asyncio
import websockets
import pyaudio
import json
import base64
import os
import concurrent.futures

THOUGHT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diana_thoughts.json")

def write_thought(thought, status=""):
    """Writes Diana's current thought to a shared file for the UI to display."""
    try:
        with open(THOUGHT_FILE, 'w', encoding='utf-8') as f:
            json.dump({"thought": thought, "status": status}, f, ensure_ascii=False)
    except:
        pass

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
INPUT_RATE = 16000
OUTPUT_RATE = 24000
CHUNK = 4096

class VoiceEngine:
    def __init__(self, endpoint_url, tool_handler=None):
        self.endpoint_url = endpoint_url
        self.p = pyaudio.PyAudio()
        self.tool_handler = tool_handler  # callback for executing tool calls

        # Open audio streams
        self.input_stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=INPUT_RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        self.output_stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=OUTPUT_RATE,
            output=True,
            frames_per_buffer=CHUNK
        )

        self.ws = None
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    async def connect(self):
        """Connects to the Analytics Engine Live API WebSocket endpoint."""
        print(f"Connecting to: {self.endpoint_url[:80]}...")
        self.ws = await websockets.connect(
            self.endpoint_url,
            max_size=None
        )
        print("WebSocket connected.")

    async def send_setup(self, setup_payload):
        """Sends the setup message and waits for the server's setupComplete response."""
        await self.ws.send(json.dumps(setup_payload))
        print("Setup payload sent. Waiting for server confirmation...")

        raw = await self.ws.recv()
        response = json.loads(raw)
        if "setupComplete" in response:
            print("Server confirmed setup. Diana is ready!")
        else:
            print(f"Unexpected setup response: {json.dumps(response)[:200]}")

    async def _audio_input_task(self):
        """Captures audio from microphone and sends it over WebSocket."""
        loop = asyncio.get_event_loop()
        try:
            while True:
                data = await loop.run_in_executor(
                    self._executor,
                    lambda: self.input_stream.read(CHUNK, exception_on_overflow=False)
                )

                payload = {
                    "realtimeInput": {
                        "mediaChunks": [{
                            "mimeType": f"audio/pcm;rate={INPUT_RATE}",
                            "data": base64.b64encode(data).decode("utf-8")
                        }]
                    }
                }
                await self.ws.send(json.dumps(payload))
                await asyncio.sleep(0.005)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Input Stream Error: {e}")

    async def _audio_output_task(self):
        """Receives messages from WebSocket, plays back audio, handles tool calls."""
        try:
            async for message in self.ws:
                try:
                    response = json.loads(message)
                except json.JSONDecodeError:
                    continue

                # --- Audio playback ---
                if "serverContent" in response:
                    server_content = response["serverContent"]
                    model_turn = server_content.get("modelTurn", {})
                    for part in model_turn.get("parts", []):
                        if "inlineData" in part:
                            audio_bytes = base64.b64decode(part["inlineData"]["data"])
                            self.output_stream.write(audio_bytes)
                        elif "text" in part:
                            # Diana's text thoughts - show on screen AND in cmd
                            thought_text = part['text']
                            print(f"\n[Diana]: {thought_text}")
                            write_thought(thought_text, "thinking...")

                    if server_content.get("turnComplete", False):
                        print("[Diana finished speaking]")
                        write_thought("", "")

                # --- Tool calls from Diana ---
                elif "toolCall" in response:
                    tool_call = response["toolCall"]
                    function_calls = tool_call.get("functionCalls", [])
                    function_responses = []

                    for fc in function_calls:
                        func_name = fc.get("name", "")
                        func_args = fc.get("args", {})
                        call_id = fc.get("id", "")

                        print(f"\n[TOOL] Diana wants to run: {func_name}({json.dumps(func_args)})")
                        write_thought(f"Running: {func_name}", "executing...")

                        # Execute the tool via the handler
                        if self.tool_handler:
                            result = self.tool_handler(func_name, func_args)
                        else:
                            result = {"status": "error", "message": "No tool handler registered"}

                        print(f"  [OK] Result: {json.dumps(result)[:200]}")

                        function_responses.append({
                            "id": call_id,
                            "name": func_name,
                            "response": result
                        })

                    # Send the tool results back to Analytics Engine so Diana can respond
                    tool_response_payload = {
                        "toolResponse": {
                            "functionResponses": function_responses
                        }
                    }
                    await self.ws.send(json.dumps(tool_response_payload))
                    print("  [SENT] Tool response sent back to Diana")

                # --- Other messages ---
                else:
                    keys = list(response.keys())
                    if keys and keys != ["setupComplete"]:
                        print(f"[Server]: {keys}")

        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Output Stream Error: {e}")

    async def start(self):
        """Starts both audio tasks concurrently."""
        print("Starting audio streams...")
        self.input_task = asyncio.create_task(self._audio_input_task())
        self.output_task = asyncio.create_task(self._audio_output_task())
        await asyncio.gather(self.input_task, self.output_task)

    def terminate(self):
        self.input_stream.stop_stream()
        self.input_stream.close()
        self.output_stream.stop_stream()
        self.output_stream.close()
        self.p.terminate()
        self._executor.shutdown(wait=False)
