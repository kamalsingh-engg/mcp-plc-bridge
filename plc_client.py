"""Modbus TCP client for talking to a simulated PLC (e.g. OpenPLC)."""

import struct

from pymodbus.client import ModbusTcpClient

PLC_HOST = "localhost"
PLC_PORT = 502

# %MD holding-register base on this runtime: qw_count (1024) + mw_count (1024).
# Each %MD value occupies 2 registers, high word first. The number in a
# variable's Location column (e.g. %MD4) IS the raw value index below -
# not a byte offset - confirmed empirically against the Editor's debugger.
# See modbus_slave.json on the OpenPLC Runtime install for the segment layout.
MD_BASE_ADDRESS = 2048


def _md_register_address(md_index: int) -> int:
    return MD_BASE_ADDRESS + md_index * 2


def read_coil(address: int) -> bool:
    with ModbusTcpClient(PLC_HOST, port=PLC_PORT) as client:
        result = client.read_coils(address, count=1)
        if result.isError():
            raise IOError(f"Failed to read coil at address {address}: {result}")
        return result.bits[0]


def read_holding_register(address: int) -> int:
    with ModbusTcpClient(PLC_HOST, port=PLC_PORT) as client:
        result = client.read_holding_registers(address, count=1)
        if result.isError():
            raise IOError(f"Failed to read holding register at address {address}: {result}")
        return result.registers[0]


def write_coil(address: int, value: bool) -> None:
    with ModbusTcpClient(PLC_HOST, port=PLC_PORT) as client:
        result = client.write_coil(address, value)
        if result.isError():
            raise IOError(f"Failed to write coil at address {address}: {result}")


def read_real(md_index: int) -> float:
    """Read a REAL value given its %MD index (e.g. 4 for %MD4)."""
    address = _md_register_address(md_index)
    with ModbusTcpClient(PLC_HOST, port=PLC_PORT) as client:
        result = client.read_holding_registers(address, count=2)
        if result.isError():
            raise IOError(f"Failed to read %MD{md_index}: {result}")
        raw = struct.pack(">HH", result.registers[0], result.registers[1])
        return struct.unpack(">f", raw)[0]


def write_real(md_index: int, value: float) -> None:
    """Write a REAL value given its %MD index (e.g. 4 for %MD4)."""
    address = _md_register_address(md_index)
    high, low = struct.unpack(">HH", struct.pack(">f", value))
    with ModbusTcpClient(PLC_HOST, port=PLC_PORT) as client:
        result = client.write_registers(address, [high, low])
        if result.isError():
            raise IOError(f"Failed to write %MD{md_index}: {result}")


if __name__ == "__main__":
    print(f"start_1 (coil 1): {read_coil(1)}")
    print(f"stop_1 (coil 2): {read_coil(2)}")
    print(f"motor_1 (coil 0): {read_coil(0)}")
