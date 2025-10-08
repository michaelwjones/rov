#!/usr/bin/env python3
"""
ROV Adafruit PWM Hat Test Script
Test PCA9685 PWM hat and ESC communication
"""

import time
import board
import busio
from adafruit_pca9685 import PCA9685
from config import THRUSTER_CHANNELS, PWM_SETTINGS

def test_i2c_devices():
    """Test I2C device detection"""
    print("ROV Adafruit PWM Hat Test")
    print("=" * 50)
    print("Testing I2C devices...")
    try:
        import subprocess
        result = subprocess.run(['i2cdetect', '-y', '1'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("I2C scan results:")
            print(result.stdout)
            if '40' in result.stdout:  # PCA9685 default address
                print("PCA9685 PWM hat detected at address 0x40")
                print()
                return True
            else:
                print("PCA9685 PWM hat not found")
                print()
                return False
        else:
            print("I2C scan failed")
            print()
            return False
    except Exception as e:
        print(f"I2C test: FAILED - {e}")
        print()
        return False

def test_pwm_hat():
    """Test Adafruit PWM hat communication and ESC control"""
    print("Testing PWM hat and ESCs...")
    print("-" * 50)
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        pca = PCA9685(i2c)
        pca.frequency = PWM_SETTINGS['frequency']

        # Test neutral signal on all thruster channels
        neutral_duty = int((PWM_SETTINGS['neutral'] / 20000.0) * 65535)

        print("Arming ESCs with neutral signal...")
        for name, channel in THRUSTER_CHANNELS.items():
            pca.channels[channel].duty_cycle = neutral_duty
            print(f"  {name}: Channel {channel} - Neutral PWM (1500µs)")

        print("  Waiting 3 seconds for ESC arming...")
        time.sleep(3)
        print()

        # Test forward, reverse, then neutral
        forward_duty = int((PWM_SETTINGS['max_pulse'] / 20000.0) * 65535)
        reverse_duty = int((PWM_SETTINGS['min_pulse'] / 20000.0) * 65535)

        print("Testing each thruster...")
        for name, channel in THRUSTER_CHANNELS.items():
            print(f"\n{name} (Channel {channel}):")

            # Forward
            pca.channels[channel].duty_cycle = forward_duty
            print(f"  Forward (2000µs)...")
            time.sleep(1)

            # Reverse
            pca.channels[channel].duty_cycle = reverse_duty
            print(f"  Reverse (1000µs)...")
            time.sleep(1)

            # Back to neutral
            pca.channels[channel].duty_cycle = neutral_duty
            print(f"  Neutral (1500µs)")
            time.sleep(0.5)

        pca.deinit()
        print()
        print("=" * 50)
        print("PWM hat test: PASSED")
        return True
    except Exception as e:
        print()
        print("=" * 50)
        print(f"PWM hat test: FAILED - {e}")
        return False

def main():
    """Run Adafruit PWM tests"""
    print()

    tests = [
        ("I2C Devices", test_i2c_devices),
        ("PWM Hat & ESCs", test_pwm_hat)
    ]

    results = {}

    for test_name, test_func in tests:
        results[test_name] = test_func()

    print("Test Results Summary:")
    print("-" * 50)

    all_passed = True
    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("All tests passed! Adafruit PWM hat is ready.")
    else:
        print("Some tests failed. Check connections and configuration.")

if __name__ == "__main__":
    main()
