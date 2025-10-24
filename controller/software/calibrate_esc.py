#!/usr/bin/env python3
"""
ESC Calibration Script for Apisqueen U2 Thrusters
Run this ONCE when setting up new ESCs to calibrate throttle range
"""

import time
from maestro import Controller as MaestroController, microseconds_to_target
from config import THRUSTER_CHANNELS, PWM_SETTINGS, MAESTRO_CONFIG

def calibrate_esc():
    """
    ESC Calibration Procedure:
    1. Set max throttle
    2. Power on ESC (you'll do this manually)
    3. ESC detects max point
    4. Set min throttle
    5. ESC detects min point
    6. Set neutral
    7. ESC is calibrated
    """
    print("=" * 60)
    print("ESC CALIBRATION PROCEDURE")
    print("=" * 60)
    print("\nWARNING: Remove propellers before calibration!")
    print("The motor will spin during this process.\n")

    input("Press ENTER when propellers are removed and you're ready...")

    try:
        maestro = MaestroController(
            port=MAESTRO_CONFIG['port'],
            baud_rate=MAESTRO_CONFIG['baud_rate']
        )

        # Calculate target values (in quarter-microseconds)
        max_target = microseconds_to_target(PWM_SETTINGS['max_pulse'])
        min_target = microseconds_to_target(PWM_SETTINGS['min_pulse'])
        neutral_target = microseconds_to_target(PWM_SETTINGS['neutral'])

        print("\nCalibrating each thruster...")
        print("-" * 60)

        for name, channel in THRUSTER_CHANNELS.items():
            print(f"\n>>> Calibrating: {name} (Channel {channel})")

            # Step 1: Set max throttle BEFORE powering ESC
            print("  Step 1: Setting MAX throttle (2000µs)")
            maestro.setTarget(channel, max_target)

            print("\n  >>> DISCONNECT POWER to the ESC now!")
            input("  >>> Press ENTER when power is disconnected...")

            print("\n  >>> RECONNECT POWER to the ESC now!")
            input("  >>> Press ENTER when power is connected...")
            print("  >>> You should hear beeps indicating max throttle detected")
            time.sleep(2)

            # Step 2: Set min throttle
            print("\n  Step 2: Setting MIN throttle (1000µs)")
            maestro.setTarget(channel, min_target)
            print("  >>> You should hear beeps indicating min throttle detected")
            time.sleep(3)

            # Step 3: Set neutral
            print("\n  Step 3: Setting NEUTRAL (1500µs)")
            maestro.setTarget(channel, neutral_target)
            print("  >>> You should hear a confirmation beep")
            time.sleep(2)

            print(f"\n  ✓ {name} calibration complete!")
            print("-" * 60)

        # Test all thrusters
        print("\n\nCalibration complete! Testing all thrusters...")
        input("Press ENTER to test forward direction...")

        for name, channel in THRUSTER_CHANNELS.items():
            maestro.setTarget(channel, max_target)
        print("All thrusters: FORWARD (2 seconds)")
        time.sleep(2)

        # Back to neutral
        for name, channel in THRUSTER_CHANNELS.items():
            maestro.setTarget(channel, neutral_target)
        print("All thrusters: NEUTRAL (1 second)")
        time.sleep(1)

        input("Press ENTER to test reverse direction...")

        for name, channel in THRUSTER_CHANNELS.items():
            maestro.setTarget(channel, min_target)
        print("All thrusters: REVERSE (2 seconds)")
        time.sleep(2)

        # Back to neutral
        for name, channel in THRUSTER_CHANNELS.items():
            maestro.setTarget(channel, neutral_target)
        print("All thrusters: NEUTRAL")
        time.sleep(1)

        maestro.close()

        print("\n" + "=" * 60)
        print("ESC CALIBRATION AND TEST COMPLETE!")
        print("=" * 60)
        print("\nYour ESCs are now calibrated and ready to use.")
        print("You can now run test_pololu_pwm.py for normal testing.\n")

    except Exception as e:
        print(f"\nCalibration FAILED: {e}")
        return False

    return True

if __name__ == "__main__":
    calibrate_esc()
