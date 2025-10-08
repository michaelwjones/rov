#!/usr/bin/env python3
"""
ESC Calibration Script for Apisqueen U2 Thrusters
Run this ONCE when setting up new ESCs to calibrate throttle range
"""

import time
import board
import busio
from adafruit_pca9685 import PCA9685
from config import THRUSTER_CHANNELS, PWM_SETTINGS

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
        i2c = busio.I2C(board.SCL, board.SDA)
        pca = PCA9685(i2c)
        pca.frequency = PWM_SETTINGS['frequency']

        # Calculate duty cycles
        max_duty = int((PWM_SETTINGS['max_pulse'] / 20000.0) * 65535)
        min_duty = int((PWM_SETTINGS['min_pulse'] / 20000.0) * 65535)
        neutral_duty = int((PWM_SETTINGS['neutral'] / 20000.0) * 65535)

        print("\nCalibrating each thruster...")
        print("-" * 60)

        for name, channel in THRUSTER_CHANNELS.items():
            print(f"\n>>> Calibrating: {name} (Channel {channel})")

            # Step 1: Set max throttle BEFORE powering ESC
            print("  Step 1: Setting MAX throttle (2000µs)")
            pca.channels[channel].duty_cycle = max_duty

            print("\n  >>> DISCONNECT POWER to the ESC now!")
            input("  >>> Press ENTER when power is disconnected...")

            print("\n  >>> RECONNECT POWER to the ESC now!")
            input("  >>> Press ENTER when power is connected...")
            print("  >>> You should hear beeps indicating max throttle detected")
            time.sleep(2)

            # Step 2: Set min throttle
            print("\n  Step 2: Setting MIN throttle (1000µs)")
            pca.channels[channel].duty_cycle = min_duty
            print("  >>> You should hear beeps indicating min throttle detected")
            time.sleep(3)

            # Step 3: Set neutral
            print("\n  Step 3: Setting NEUTRAL (1500µs)")
            pca.channels[channel].duty_cycle = neutral_duty
            print("  >>> You should hear a confirmation beep")
            time.sleep(2)

            print(f"\n  ✓ {name} calibration complete!")
            print("-" * 60)

        # Test all thrusters
        print("\n\nCalibration complete! Testing all thrusters...")
        input("Press ENTER to test forward direction...")

        for name, channel in THRUSTER_CHANNELS.items():
            pca.channels[channel].duty_cycle = max_duty
        print("All thrusters: FORWARD (2 seconds)")
        time.sleep(2)

        # Back to neutral
        for name, channel in THRUSTER_CHANNELS.items():
            pca.channels[channel].duty_cycle = neutral_duty
        print("All thrusters: NEUTRAL (1 second)")
        time.sleep(1)

        input("Press ENTER to test reverse direction...")

        for name, channel in THRUSTER_CHANNELS.items():
            pca.channels[channel].duty_cycle = min_duty
        print("All thrusters: REVERSE (2 seconds)")
        time.sleep(2)

        # Back to neutral
        for name, channel in THRUSTER_CHANNELS.items():
            pca.channels[channel].duty_cycle = neutral_duty
        print("All thrusters: NEUTRAL")
        time.sleep(1)

        pca.deinit()

        print("\n" + "=" * 60)
        print("ESC CALIBRATION AND TEST COMPLETE!")
        print("=" * 60)
        print("\nYour ESCs are now calibrated and ready to use.")
        print("You can now run test_hardware.py for normal testing.\n")

    except Exception as e:
        print(f"\nCalibration FAILED: {e}")
        return False

    return True

if __name__ == "__main__":
    calibrate_esc()
