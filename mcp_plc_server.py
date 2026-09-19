"""MCP server exposing the PLC bridge as tools for an LLM.

See mcp-plc-bridge-session-plan.md for the ladder logic and thermal_sim.py
for the digital-twin process backing the analog tags.
"""

from mcp.server.mcpserver import MCPServer

from plc_client import read_coil, read_real, write_coil, write_real

mcp = MCPServer("plc-bridge")

# kind "coil": boolean, address is a Modbus coil number
# kind "real": float, address is the %MD byte offset
# Tag names match the ladder program's variable names exactly.
TAG_MAP = {
    "motor": {"kind": "coil", "address": 0, "writable": True},
    "input1": {"kind": "coil", "address": 1, "writable": True},
    "input2": {"kind": "coil", "address": 2, "writable": True},
    "TempsetPoint": {"kind": "real", "address": 0, "writable": True},
    "Valve_position": {"kind": "real", "address": 4, "writable": False},
    "Actual_Temp": {"kind": "real", "address": 8, "writable": False},
}


def _tag_info(tag: str) -> dict:
    if tag not in TAG_MAP:
        raise ValueError(f"Unknown tag: {tag}. Known tags: {list(TAG_MAP)}")
    return TAG_MAP[tag]


@mcp.tool()
def list_tags() -> list[str]:
    """List the available PLC tag names."""
    return list(TAG_MAP)


@mcp.tool()
def get_sensor_reading(tag: str) -> bool | float:
    """Read the current value of a PLC tag (boolean for coils, float for analog tags)."""
    info = _tag_info(tag)
    if info["kind"] == "coil":
        return read_coil(info["address"])
    return read_real(info["address"])


@mcp.tool()
def set_actuator(tag: str, value: bool | float) -> str:
    """Set a writable PLC tag. Boolean for coils, float for %MD analog tags
    (the address is that variable's %MD index, e.g. 4 for %MD4).

    Valve_position and Actual_Temp are computed automatically by thermal_sim.py
    from TempsetPoint and are not directly writable.
    """
    info = _tag_info(tag)
    if not info["writable"]:
        raise ValueError(f"{tag} is read-only (computed automatically), cannot set it")
    if info["kind"] == "coil":
        write_coil(info["address"], bool(value))
    else:
        write_real(info["address"], float(value))
    return f"{tag} set to {value}"


if __name__ == "__main__":
    mcp.run()
