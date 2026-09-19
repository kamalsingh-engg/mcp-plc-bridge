# mcp-plc-bridge

An open-source MCP (Model Context Protocol) server that lets an LLM read
sensors and control actuators on a PLC over Modbus TCP. Built against
[OpenPLC](https://autonomylogic.com/) as the PLC runtime, but the bridge
itself only depends on standard Modbus TCP, so it works with any Modbus
TCP-capable PLC or simulator.

## Architecture

```
LLM (e.g. Claude) <--MCP--> mcp_plc_server.py <--Modbus TCP--> PLC runtime
                                    ^
                                    |
                       plc_client.py (Modbus helper)
                                    ^
                                    |
                         thermal_sim.py (optional digital twin
                         for analog tags, see below)
```

- **plc_client.py** — thin Modbus TCP client (coils and 32-bit REAL values).
- **mcp_plc_server.py** — MCP server exposing `list_tags`, `get_sensor_reading`,
  and `set_actuator` tools, backed by a small tag map.
- **thermal_sim.py** — standalone digital-twin process for a simulated
  analog control loop (a setpoint, a valve position derived from it, and a
  temperature that drifts toward the setpoint over time). This is pure
  Python, not PLC ladder logic — a stand-in for a real PID loop so the demo
  has a live analog signal to show off. Skip it if you only care about the
  boolean tags.
- **mock_plc_server.py** — a plain Python Modbus TCP server you can run
  instead of a real PLC runtime, useful for trying the bridge without
  installing OpenPLC at all.

## Tags

| Tag             | Type  | Writable | Notes                                   |
|-----------------|-------|----------|------------------------------------------|
| `motor`         | bool  | yes      | Digital output                          |
| `input1`        | bool  | yes      | Digital input                           |
| `input2`        | bool  | yes      | Digital input                           |
| `TempsetPoint`  | float | yes      | Temperature setpoint                    |
| `Valve_position`| float | no       | Computed from `TempsetPoint`            |
| `Actual_Temp`   | float | no       | Drifts toward `TempsetPoint` over time  |

## Setup

1. Install Java (required by OpenPLC) and Python 3.10+.
2. Install [OpenPLC Editor](https://autonomylogic.com/download) and set up a
   PLC runtime (native install or Docker) — see OpenPLC's own docs for this
   part, since it depends on your OS and OpenPLC version.
3. Create a venv and install dependencies:

   ```bash
   python -m venv venv
   venv/Scripts/activate   # or `source venv/bin/activate` on Linux/macOS
   pip install -r requirements.txt
   ```

4. In OpenPLC Editor, build a program with the tags above (or edit the tag
   map in `mcp_plc_server.py` to match your own I/O layout), deploy it, and
   start the PLC.

## Running

```bash
# Optional: only if you're using the analog tags
python thermal_sim.py

# The MCP server itself (this is what a Claude client connects to)
python mcp_plc_server.py
```

To try the bridge without any PLC at all:

```bash
python mock_plc_server.py   # in one terminal
python plc_client.py        # in another, to sanity-check the connection
```

## Connecting to Claude

Point your MCP client at:

- **Command**: path to your venv's `python` (or `python.exe` on Windows)
- **Args**: path to `mcp_plc_server.py`

Where exactly to configure this depends on which Claude client you're using
— check its settings for an "Extensions," "Connectors," or "MCP servers"
section, or its `claude_desktop_config.json` if it uses the classic
`mcpServers` format.

Once connected, you can ask things like "What's the current temperature
reading?" or "Turn on the motor."

## License

MIT — see [LICENSE](LICENSE).
