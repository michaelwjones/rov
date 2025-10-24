#!/usr/bin/env python3
"""
ROV Pololu Maestro PWM Test Script
Test Pololu Mini Maestro 12-channel servo controller and ESC communication via TTL serial
"""

import time
import sys
from maestro import Controller as MaestroController, microseconds_to_target
from config import THRUSTER_CHANNELS, PWM_SETTINGS, MAESTRO_CONFIG


def test_serial_connection():
    """Test TTL serial connection to Pololu Maestro"""
    print("ROV Pololu Maestro PWM Test")
    print("=" * 50)
    print("Testing TTL serial connection...")
    try:
        # Check for serial port
        import subprocess
        import os

        # Check if serial port exists
        if os.path.exists(MAESTRO_CONFIG['port']):
            print(f"Serial port found: {MAESTRO_CONFIG['port']}")
            print()
            return True
        else:
            print(f"Serial port NOT found: {MAESTRO_CONFIG['port']}")
            print()
            print("Troubleshooting:")
            print("  1. Check UART is enabled in /boot/firmware/config.txt")
            print("  2. Reboot after config changes")
            print("  3. Try: ls -la /dev/serial* /dev/ttyAMA*")
            print()
            return False
    except Exception as e:
        print(f"Serial port scan: FAILED - {e}")
        print()
        return False


def test_maestro_connection():
    """Test Pololu Maestro connection"""
    print("Testing Maestro connection...")
    print("-" * 50)
    try:
        maestro = MaestroController(
            port=MAESTRO_CONFIG['port'],
            baud_rate=MAESTRO_CONFIG['baud_rate']
        )
        print(f"Successfully connected to Maestro on {MAESTRO_CONFIG['port']}")
        maestro.close()
        print()
        return True
    except Exception as e:
        print(f"Maestro connection: FAILED - {e}")
        print()
        print("Troubleshooting tips:")
        print("  1. Check TTL serial wiring (TX, RX, GND)")
        print("  2. Verify correct port in config.py")
        print("  3. Check UART enabled: dtparam=uart0=on in /boot/firmware/config.txt")
        print("  4. Try: ls -la /dev/serial* /dev/ttyAMA*")
        print("  5. Check permissions: sudo usermod -a -G dialout $USER")
        print()
        return False


def test_pwm_maestro():
    """Test Pololu Maestro communication and ESC control"""
    print("Testing Maestro and ESCs...")
    print("-" * 50)
    try:
        maestro = MaestroController(
            port=MAESTRO_CONFIG['port'],
            baud_rate=MAESTRO_CONFIG['baud_rate']
        )

        # Calculate target values (in quarter-microseconds)
        neutral_target = microseconds_to_target(PWM_SETTINGS['neutral'])
        forward_target = microseconds_to_target(PWM_SETTINGS['max_pulse'])
        backward_target = microseconds_to_target(PWM_SETTINGS['min_pulse'])

        print("Arming ESCs with neutral signal (1500µs)...")
        for name, channel in THRUSTER_CHANNELS.items():
            maestro.setTarget(channel, neutral_target)
            print(f"  {name}: Channel {channel} - Neutral PWM (1500µs)")

        print("  Waiting 3 seconds for ESC arming...")
        time.sleep(3)
        print()

        print("Testing each thruster...")
        for name, channel in THRUSTER_CHANNELS.items():
            print(f"\n{name} (Channel {channel}):")

            # Forward for 5 seconds
            maestro.setTarget(channel, forward_target)
            print(f"  Forward ({PWM_SETTINGS['max_pulse']}µs)...")
            time.sleep(5)

            # Neutral
            maestro.setTarget(channel, neutral_target)
            print(f"  Neutral ({PWM_SETTINGS['neutral']}µs)")
            time.sleep(1)

            # Backward for 5 seconds
            maestro.setTarget(channel, backward_target)
            print(f"  Backward ({PWM_SETTINGS['min_pulse']}µs)...")
            time.sleep(5)

            # Back to neutral
            maestro.setTarget(channel, neutral_target)
            print(f"  Neutral ({PWM_SETTINGS['neutral']}µs)")
            time.sleep(0.5)

        maestro.close()
        print()
        print("=" * 50)
        print("Maestro test: PASSED")
        return True
    except Exception as e:
        print()
        print("=" * 50)
        print(f"Maestro test: FAILED - {e}")
        return False


def test_advanced_features():
    """Test advanced Maestro features"""
    print("\nTesting advanced Maestro features...")
    print("-" * 50)
    try:
        maestro = MaestroController(
            port=MAESTRO_CONFIG['port'],
            baud_rate=MAESTRO_CONFIG['baud_rate']
        )

        print("Testing channel 0 features:")

        # Test speed limiting
        print("  Setting speed limit (smooth movement)...")
        maestro.setSpeed(0, 50)  # Slow speed
        maestro.setTarget(0, microseconds_to_target(1700))
        time.sleep(2)
        maestro.setTarget(0, microseconds_to_target(1500))
        time.sleep(2)

        # Reset to unlimited speed
        maestro.setSpeed(0, 0)
        print("  Speed test complete")

        # Test acceleration
        print("  Setting acceleration limit...")
        maestro.setAcceleration(0, 10)
        maestro.setTarget(0, microseconds_to_target(1700))
        time.sleep(2)
        maestro.setTarget(0, microseconds_to_target(1500))
        time.sleep(2)

        # Reset to unlimited acceleration
        maestro.setAcceleration(0, 0)
        print("  Acceleration test complete")

        maestro.close()
        print()
        print("Advanced features test: PASSED")
        return True
    except Exception as e:
        print()
        print(f"Advanced features test: FAILED - {e}")
        return False


def main():
    """Run Pololu Maestro PWM tests"""
    print()

    tests = [
        ("Serial Connection", test_serial_connection),
        ("Maestro Connection", test_maestro_connection),
        ("Maestro & ESCs", test_pwm_maestro),
        ("Advanced Features", test_advanced_features)
    ]

    results = {}

    for test_name, test_func in tests:
        results[test_name] = test_func()

        # If a critical test fails, skip remaining tests
        if test_name in ["Serial Connection", "Maestro Connection"] and not results[test_name]:
            print("Critical test failed. Skipping remaining tests.")
            break

    print("\nTest Results Summary:")
    print("-" * 50)

    all_passed = True
    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("All tests passed! Pololu Maestro is ready.")
        print()
        print("Configuration:")
        print(f"  Port: {MAESTRO_CONFIG['port']}")
        print(f"  Channels: {len(THRUSTER_CHANNELS)} thrusters")
        print(f"  PWM Range: {PWM_SETTINGS['min_pulse']}-{PWM_SETTINGS['max_pulse']}µs")
    else:
        print("Some tests failed. Check connections and configuration.")
        print()
        print("Common issues:")
        print("  - TTL serial wiring incorrect (check TX/RX/GND)")
        print("  - UART not enabled in /boot/firmware/config.txt")
        print("  - Wrong port in config.py (try /dev/ttyAMA0)")
        print("  - Missing permissions: sudo usermod -a -G dialout $USER")
        print("  - Maestro not powered on")


if __name__ == "__main__":
    main()
