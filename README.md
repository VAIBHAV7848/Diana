# Project Diana (Power ++)

A continuous, low-latency, voice-controlled Windows 11 AI assistant running natively on the host OS with a real-time 3D visual avatar ("Diana").

## Architecture
- **VoiceEngine (`voice_engine.py`)**: Uses PyAudio to capture 16kHz microphone stream and playback 24kHz speaker stream over WebSockets.
- **Proxy**: The WebSockets connection is sent via a proxy provided by the Mascot Bot SDK, which natively handles mapping the audio back to Visemes (lip-syncing for VRM avatars).
- **MCP Controller (`mcp_controller.py`)**: Extends the agent's capabilities using native OS subprocess calls, `pyautogui` for mouse/keyboard control, and HTTP webhook `requests`.
- **Orchestrator (`main.py`)**: The master script setting up the environment, initializing the "Diana Persona", and invoking the `voice_engine`.

## Requirements
Ensure you have Python 3.9+ and have run:
```bash
pip install -r requirements.txt
```

> **Note**: For PyAudio on Windows, you might need extra build tools or a precompiled binary depending on your local Python distribution.

## Configuration
Before running, copy or configure your `.env` file in the root `Diana_Host_Assistant` directory:
- `GEMINI_API_KEY`: Your Analytics Engine API Developer Key.
- `MASCOT_PROXY_URL`: Base URL for the Mascot Bot SDK logic.
- `TASKER_WEBHOOK_URL`: Your Android webhook location.

## Execution
Run the system via:
```bash
python main.py
```

*Project developed leveraging Analytics Engine models and native integrations. Handle full system access parameters with extreme caution.*
