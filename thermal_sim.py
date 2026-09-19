"""Digital-twin simulator standing in for a PID loop the ladder program doesn't have.

Continuously reads TempSetPoint (%MD0) and drives:
- Valve_position (%MD4): linear function of setpoint (100% at 20 deg, 10% at 40 deg)
- Actual_Temp (%MD8): drifts toward the setpoint with first-order lag, plus jitter

Run this alongside the OpenPLC runtime; it's pure Python, no ladder logic involved.
"""

import random
import time

from pymodbus.exceptions import ConnectionException

from plc_client import read_real, write_real

TEMP_SETPOINT_OFFSET = 0
VALVE_POSITION_OFFSET = 4
ACTUAL_TEMP_OFFSET = 8

VALVE_MIN_TEMP, VALVE_MAX_TEMP = 20.0, 40.0
VALVE_AT_MIN_TEMP, VALVE_AT_MAX_TEMP = 100.0, 10.0

LAG_TIME_CONSTANT_S = 20.0  # bigger = slower to reach setpoint
JITTER_STDDEV = 0.15  # degrees, applied once near the setpoint
TICK_SECONDS = 1.0


def valve_position_for_setpoint(setpoint: float) -> float:
    clamped = max(VALVE_MIN_TEMP, min(VALVE_MAX_TEMP, setpoint))
    span = VALVE_MAX_TEMP - VALVE_MIN_TEMP
    fraction = (clamped - VALVE_MIN_TEMP) / span
    return VALVE_AT_MIN_TEMP + fraction * (VALVE_AT_MAX_TEMP - VALVE_AT_MIN_TEMP)


def main() -> None:
    actual_temp = None
    while actual_temp is None:
        try:
            actual_temp = read_real(ACTUAL_TEMP_OFFSET)
        except ConnectionException:
            print("PLC not reachable yet, retrying...")
            time.sleep(TICK_SECONDS)
    print(f"Starting thermal sim. actual_temp={actual_temp:.2f}")

    while True:
        try:
            setpoint = read_real(TEMP_SETPOINT_OFFSET)

            valve_position = valve_position_for_setpoint(setpoint)
            write_real(VALVE_POSITION_OFFSET, valve_position)

            alpha = TICK_SECONDS / LAG_TIME_CONSTANT_S
            actual_temp += (setpoint - actual_temp) * alpha
            actual_temp += random.gauss(0, JITTER_STDDEV)
            write_real(ACTUAL_TEMP_OFFSET, actual_temp)

            print(
                f"setpoint={setpoint:.1f}  valve={valve_position:.1f}%  "
                f"actual_temp={actual_temp:.2f}"
            )
        except ConnectionException as exc:
            print(f"PLC connection blip, will retry next tick: {exc}")

        time.sleep(TICK_SECONDS)


if __name__ == "__main__":
    main()
