#!/usr/bin/env python3
"""
ROV Input Test Script
Test GPIO button inputs
"""

import time
import RPi.GPIO as GPIO
from config import BUTTON_PINS

def test_buttons():
    """Test button inputs"""
    print("ROV Input Test")
    print("=" * 50)
    print("Testing buttons...")
    print("Press each button (will timeout in 30 seconds):")
    print()

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
                    print(f"  {name}: DETECTED (GPIO {pin})")
                    tested_buttons.add(name)
                    time.sleep(0.5)  # Debounce

            time.sleep(0.1)

        print()
        print("=" * 50)
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
        print()
        return True
    except Exception as e:
        print(f"GPIO test: FAILED - {e}")
        print()
        return False

def main():
    """Run input tests"""
    print()

    tests = [
        ("GPIO Setup", test_gpio_setup),
        ("Button Inputs", test_buttons)
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
        print("All tests passed! Inputs are ready.")
    else:
        print("Some tests failed. Check connections and configuration.")

if __name__ == "__main__":
    main()
