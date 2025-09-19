#!/usr/bin/env python3
"""
ROV Hardware Test Script
Test individual components before running main control system
"""

import time
import board
import busio
from adafruit_pca9685 import PCA9685
import RPi.GPIO as GPIO
from config import *

def test_pwm_hat():
    """Test Adafruit PWM hat communication"""
    print("Testing PWM hat...")
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        pca = PCA9685(i2c)
        pca.frequency = PWM_SETTINGS['frequency']

        # Test neutral signal on all thruster channels
        neutral_duty = int((PWM_SETTINGS['neutral'] / 20000.0) * 65535)

        for name, channel in THRUSTER_CHANNELS.items():
            pca.channels[channel].duty_cycle = neutral_duty
            print(f"  {name}: Channel {channel} - Neutral PWM sent")

        time.sleep(2)

        # Test forward pulse
        forward_duty = int((PWM_SETTINGS['max_pulse'] / 20000.0) * 65535)
        for name, channel in THRUSTER_CHANNELS.items():
            pca.channels[channel].duty_cycle = forward_duty
            print(f"  {name}: Channel {channel} - Forward PWM sent")
            time.sleep(1)
            pca.channels[channel].duty_cycle = neutral_duty

        pca.deinit()
        print("PWM hat test: PASSED")
        return True
    except Exception as e:
        print(f"PWM hat test: FAILED - {e}")
        return False

def test_buttons():
    """Test button inputs"""
    print("Testing buttons...")
    print("Press each button (will timeout in 30 seconds):")

    GPIO.setmode(GPIO.BCM)

    # Setup all button pins
    for name, pin in BUTTON_PINS.items():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    tested_buttons = set()
    start_time = time.time()

    try:
        while len(tested_buttons) < len(BUTTON_PINS) and (time.time() - start_time) < 30:
            for name, pin in BUTTON_PINS.items():
                if name not in tested_buttons and not GPIO.input(pin):  # Button pressed
                    print(f"  {name}: DETECTED")
                    tested_buttons.add(name)
                    time.sleep(0.5)  # Debounce

            time.sleep(0.1)

        if len(tested_buttons) == len(BUTTON_PINS):
            print("Button test: PASSED - All buttons detected")
            return True
        else:
            missing = set(BUTTON_PINS.keys()) - tested_buttons
            print(f"Button test: PARTIAL - Missing: {missing}")
            return False

    except Exception as e:
        print(f"Button test: FAILED - {e}")
        return False
    finally:
        GPIO.cleanup()

def test_i2c_devices():
    """Test I2C device detection"""
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
                return True
            else:
                print("PCA9685 PWM hat not found")
                return False
        else:
            print("I2C scan failed")
            return False
    except Exception as e:
        print(f"I2C test: FAILED - {e}")
        return False

def test_gpio_setup():
    """Test basic GPIO functionality"""
    print("Testing GPIO setup...")
    try:
        GPIO.setmode(GPIO.BCM)

        # Test setting up pins without errors
        test_pin = 18
        GPIO.setup(test_pin, GPIO.OUT)
        GPIO.output(test_pin, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(test_pin, GPIO.LOW)

        GPIO.cleanup()
        print("GPIO test: PASSED")
        return True
    except Exception as e:
        print(f"GPIO test: FAILED - {e}")
        return False

def main():
    """Run all hardware tests"""
    print("ROV Hardware Test Suite")
    print("=" * 40)

    tests = [
        ("GPIO Setup", test_gpio_setup),
        ("I2C Devices", test_i2c_devices),
        ("PWM Hat", test_pwm_hat),
        ("Button Inputs", test_buttons)
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 20)
        results[test_name] = test_func()

    print("\n" + "=" * 40)
    print("Test Results Summary:")

    all_passed = True
    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\nAll tests passed! ROV hardware is ready.")
    else:
        print("\nSome tests failed. Check connections and configuration.")

if __name__ == "__main__":
    main()