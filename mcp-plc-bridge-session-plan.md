# Week 1: MCP Server for PLC — Claude Code Session Plan

**Goal:** Build an open-source MCP server that bridges an LLM to a simulated PLC
over Modbus TCP, using OpenPLC as the PLC runtime. Fully open-source, no
company/site-specific data anywhere.

**Machine:** Personal laptop (not AVL laptop — network restrictions block
Claude Code there).

**Total time:** ~3 hours, run as three checkpointed stages below. Paste each
prompt into Claude Code only after confirming the previous stage actually
works — don't chain them blind.

---

## Pre-session (tonight, ~10 min)

- [ ] Install Java (required for OpenPLC runtime)
- [ ] Download & install OpenPLC Editor from openplcproject.com
- [ ] Confirm Python 3.10+ is installed

---

## Global instruction to give Claude Code FIRST, before Stage 1

Paste this before anything else so it holds for the whole session:

```
This project will be published as a public open-source GitHub repo, so:
- No hardcoded IPs, site names, or company-specific naming anywhere —
  in code, comments, filenames, or commit messages
- Use only generic tag names (e.g. temp_1, motor_1, pressure_1)
- No references to any real company, client, or deployment site
- Assume this is a standalone demo project with no prior context
```

---

## Stage 1 — OpenPLC + Python Modbus client (Hour 1)

Manual step first (Claude Code can't drive the OpenPLC GUI):
- [ ] Open OpenPLC Editor, create a new project
- [ ] Build a simple ladder program: 2 digital inputs (start/stop), 1 digital
      output (motor), 1 analog input (temperature, simple counter for now)
- [ ] Compile and run in the built-in simulator
- [ ] Confirm Modbus TCP is live on localhost:502

Then prompt Claude Code:

```
Set up a Python project for an MCP-PLC bridge. Create a venv, install
pymodbus, and write plc_client.py with three functions: read_coil(address),
read_holding_register(address), and write_coil(address, value), targeting
a Modbus TCP server at localhost:502. Add a small __main__ block that reads
the temperature register and prints it, so I can test the connection
standalone before building anything else on top of it.
```

**Checkpoint:** running `python plc_client.py` prints a live value from
OpenPLC. Don't move on until this works.

---

## Stage 2 — MCP server wrapper (Hour 2)

```
Now wrap plc_client.py as an MCP server. Install the MCP Python SDK. Define
three MCP tools: get_sensor_reading(tag), set_actuator(tag, value), and
list_tags(). Use a simple in-code tag map (e.g. {"temp_1": holding register
0, "motor_1": coil 0}) so tags are named generically, not tied to any real
equipment. Make sure the server starts cleanly and the tools are registered
without errors.
```

**Checkpoint:** MCP server starts, no errors, tools show up when queried
locally (Claude Code should be able to verify this itself).

---

## Stage 3 — Connect to Claude + polish for showcase (Hour 3)

```
Help me configure Claude Desktop's MCP settings to point at this server, and
write a clean README.md explaining: what this project is, the architecture
(LLM <-> MCP server <-> Modbus TCP <-> OpenPLC), setup steps, and how to run
it. Also add an MIT license file, a requirements.txt, and a .gitignore
appropriate for a Python project with a venv. Do not include any real
sensor values, IPs, or site references anywhere — everything should read as
a generic open-source demo.
```

Then manually:
- [ ] Restart Claude Desktop, confirm the MCP tools appear
- [ ] Test: "What's the current temperature reading?" / "Turn on the motor"
- [ ] Screen-record ~20 seconds of that exchange for LinkedIn
- [ ] `git init`, commit, push to GitHub as `mcp-plc-bridge`

---

## If you run short on time

Cut the README/GitHub polish to a 15-minute follow-up the next morning.
Don't let it eat into the live demo in Hour 3 — a working, recordable demo
is the actual point of the session.
