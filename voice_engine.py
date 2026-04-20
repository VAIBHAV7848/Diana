import asyncio
import websockets
import pyaudio
import json
import base64
import os
import threading
import concurrent.futures
import speech_recognition as sr

THOUGHT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diana_thoughts.json")

def write_thought(thought, status=""):
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
        self.tool_handler = tool_handler

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
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        
        # Wake word state
        self._active = False  # Whether Diana is actively listening
        self._wake_lock = threading.Lock()
        self._idle_timer = None

    async def connect(self):
        print(f"Connecting to: {self.endpoint_url[:80]}...")
        self.ws = await websockets.connect(
            self.endpoint_url,
            max_size=None
        )
        print("WebSocket connected.")

    async def send_setup(self, setup_payload):
        await self.ws.send(json.dumps(setup_payload))
        print("Setup payload sent. Waiting for server confirmation...")
        raw = await self.ws.recv()
        response = json.loads(raw)
        if "setupComplete" in response:
            print("Server confirmed setup. Diana is ready!")
        else:
            print(f"Unexpected: {json.dumps(response)[:200]}")

    def _wake_up(self):
        """Activates Diana - starts sending audio to Analytics Engine."""
        with self._wake_lock:
            if not self._active:
                self._active = True
                print("\n[WAKE] Hey Diana detected! Listening...")
                write_thought("I'm listening!", "awake")

    def _go_to_sleep(self):
        """Puts Diana back to sleep - stops sending audio."""
        with self._wake_lock:
            if self._active:
                self._active = False
                print("[SLEEP] Diana going back to sleep. Say 'Hey Diana' to wake.")
                write_thought("Say 'Hey Diana' to wake me!", "sleeping")

    def _start_idle_timer(self, seconds=6):
        """After Diana finishes speaking, wait N seconds then sleep."""
        if self._idle_timer:
            self._idle_timer.cancel()
        self._idle_timer = threading.Timer(seconds, self._go_to_sleep)
        self._idle_timer.daemon = True
        self._idle_timer.start()

    def _cancel_idle_timer(self):
        if self._idle_timer:
            self._idle_timer.cancel()
            self._idle_timer = None

    def _wake_word_listener(self):
        """Runs in a background thread. Uses speech_recognition to detect 'diana'."""
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.8

        # Use the default microphone
        mic = sr.Microphone(sample_rate=16000)
        
        print("[WAKE WORD] Calibrating microphone...")
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        print("[WAKE WORD] Ready! Say 'Hey Diana' to activate.")
        write_thought("Say 'Hey Diana' to wake me!", "sleeping")

        while True:
            try:
                # Only listen for wake word when Diana is asleep
                if self._active:
                    import time
                    time.sleep(0.5)
                    continue

                with mic as source:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)

                try:
                    text = recognizer.recognize_google(audio).lower()
                    print(f"[WAKE WORD] Heard: '{text}'")
                    
                    if "diana" in text or "dianna" in text or "deana" in text or "dina" in text:
                        self._wake_up()
                        self._cancel_idle_timer()
                except sr.UnknownValueError:
                    pass  # Could not understand audio
                except sr.RequestError:
                    pass  # Google API error, silently continue

            except sr.WaitTimeoutError:
                pass  # No speech detected, loop again
            except Exception as e:
                print(f"[WAKE WORD] Error: {e}")
                import time
                time.sleep(1)

    async def _audio_input_task(self):
        """Captures audio and sends to Analytics Engine only when Diana is active."""
        loop = asyncio.get_event_loop()
        try:
            while True:
                data = await loop.run_in_executor(
                    self._executor,
                    lambda: self.input_stream.read(CHUNK, exception_on_overflow=False)
                )

                # Only send audio when Diana is awake
                if self._active:
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
        """Receives messages from WebSocket, plays audio, handles tools."""
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
                            # Diana is speaking - cancel idle timer
                            self._cancel_idle_timer()
                            audio_bytes = base64.b64decode(part["inlineData"]["data"])
                            self.output_stream.write(audio_bytes)
                        elif "text" in part:
                            thought_text = part['text']
                            print(f"\n[Diana]: {thought_text}")
                            write_thought(thought_text, "thinking...")

                    if server_content.get("turnComplete", False):
                        print("[Diana finished speaking]")
                        write_thought("", "")
                        # Start idle timer - go back to sleep after 6 seconds of silence
                        self._start_idle_timer(6)

                # --- Tool calls ---
                elif "toolCall" in response:
                    self._cancel_idle_timer()  # Stay awake during tool execution
                    tool_call = response["toolCall"]
                    function_calls = tool_call.get("functionCalls", [])
                    function_responses = []

                    for fc in function_calls:
                        func_name = fc.get("name", "")
                        func_args = fc.get("args", {})
                        call_id = fc.get("id", "")

                        print(f"\n[TOOL] Diana wants to run: {func_name}({json.dumps(func_args)})")
                        write_thought(f"Running: {func_name}", "executing...")

                        if self.tool_handler:
                            result = self.tool_handler(func_name, func_args)
                        else:
                            result = {"status": "error", "message": "No tool handler"}

                        print(f"  [OK] Result: {json.dumps(result)[:200]}")

                        function_responses.append({
                            "id": call_id,
                            "name": func_name,
                            "response": result
                        })

                    tool_response_payload = {
                        "toolResponse": {
                            "functionResponses": function_responses
                        }
                    }
                    await self.ws.send(json.dumps(tool_response_payload))
                    print("  [SENT] Tool response sent back to Diana")

                else:
                    keys = list(response.keys())
                    if keys and keys != ["setupComplete"]:
                        print(f"[Server]: {keys}")

        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Output Stream Error: {e}")

    async def start(self):
        """Starts wake word listener + audio streaming tasks."""
        print("Starting wake word listener...")
        
        # Start wake word detection in background thread
        wake_thread = threading.Thread(target=self._wake_word_listener, daemon=True)
        wake_thread.start()

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
