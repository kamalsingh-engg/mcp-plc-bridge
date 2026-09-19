"""Live-print all PLC tags every second, independent of the Editor's debugger UI."""

import time

from plc_client import read_coil, read_real

while True:
    print(
        f"motor={read_coil(0)}  input1={read_coil(1)}  input2={read_coil(2)}  |  "
        f"TempsetPoint={read_real(0):.2f}  Valve_position={read_real(4):.2f}  "
        f"Actual_Temp={read_real(8):.2f}"
    )
    time.sleep(1)
