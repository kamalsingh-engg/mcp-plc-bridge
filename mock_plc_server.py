"""Standalone mock Modbus TCP server standing in for OpenPLC during development.

Mirrors the tag layout in mcp-plc-bridge-session-plan.md: coil 0 = motor,
holding register 0 = temperature (a free-running counter here). Swap this
out for a real OpenPLC runtime later without changing plc_client.py.
"""

import logging

from pymodbus.datastore import (
    ModbusDeviceContext,
    ModbusSequentialDataBlock,
    ModbusServerContext,
)
from pymodbus.server import StartTcpServer

logging.basicConfig(level=logging.INFO)

HOST = "localhost"
PORT = 502


def build_context() -> ModbusServerContext:
    device = ModbusDeviceContext(
        di=ModbusSequentialDataBlock(1, [0] * 10),   # digital inputs (start/stop)
        co=ModbusSequentialDataBlock(1, [0] * 10),   # coils (motor output)
        hr=ModbusSequentialDataBlock(1, list(range(10))),  # holding registers (temperature)
        ir=ModbusSequentialDataBlock(1, [0] * 10),
    )
    return ModbusServerContext(devices=device, single=True)


if __name__ == "__main__":
    print(f"Starting mock Modbus TCP server on {HOST}:{PORT} ...")
    StartTcpServer(context=build_context(), address=(HOST, PORT))
