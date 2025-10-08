#!/usr/bin/env python3
"""
ROV Raspberry Pi Hardware PWM Test Script
Test native Pi 5 hardware PWM for ESC control

IMPORTANT: Raspberry Pi 5 hardware PWM limitations:
- Only 4 PWM channels available (GPIO 12, 13, 18, 19)
- Only 2 PWM channels can be active simultaneously
- This limits testing to 2 ESCs at a time

This test uses GPIO 12 and 13 (PWM channels 0 and 1).
Buttons have been moved to GPIO 5/6 to avoid conflicts.
"""

import time
try:
    from rpi_hardware_pwm import HardwarePWM
except ImportError:
    print("ERROR: rpi-hardware-pwm library not installed")
    print("Install with: sudo pip3 install rpi-hardware-pwm")
    exit(1)

from config import PWM_SETTINGS

# Raspberry Pi 5 PWM configuration
# Note: With custom pwm-pi5 overlay, the chip number is 0 (not 2 as in some docs)
PI5_PWM_CHIP = 0  # Using custom pwm-pi5 overlay

# PWM channels to test (limited to 2 on Pi 5)
# Channel mapping: 0=GPIO12, 1=GPIO13, 2=GPIO18, 3=GPIO19
# Using channels 0-1 (GPIO 12/13) - no button conflicts
PWM_TEST_CHANNELS = {
    'test_esc_1': {
        'channel': 0,      # GPIO 12
        'gpio': 12,
        'name': 'Test ESC 1'
    },
    'test_esc_2': {
        'channel': 1,      # GPIO 13
        'gpio': 13,
        'name': 'Test ESC 2'
    }
}

def pulse_to_duty_cycle(pulse_us, frequency=50):
    """
    Convert pulse width in microseconds to duty cycle percentage

    Args:
        pulse_us: Pulse width in microseconds
        frequency: PWM frequency in Hz

    Returns:
        Duty cycle as percentage (0-100)
    """
    period_us = 1_000_000 / frequency
    duty_cycle = (pulse_us / period_us) * 100
    return duty_cycle

def test_pwm_init():
    """Test PWM initialization and basic functionality"""
    print("ROV Raspberry Pi Hardware PWM Test")
    print("=" * 50)
    print()
    print("Raspberry Pi 5 PWM Configuration:")
    print("-" * 50)
    print("Using GPIO 12 and 13 (PWM channels 0 and 1)")
    print("Buttons moved to GPIO 5/6 - no conflicts")
    print("Using custom pwm-pi5 overlay")
    print()
    print("Raspberry Pi 5 PWM Limitations:")
    print("- Only 2 PWM channels active simultaneously")
    print("- Cannot test all 3 thrusters with native PWM")
    print("- Use Adafruit PWM hat for full 3-thruster operation")
    print()
    input("Press Enter to continue with PWM test...")
    print()

    print("Testing PWM initialization...")
    print("-" * 50)

    pwm_objects = {}

    try:
        # Check if PWM is available
        import os
        if not os.path.exists('/sys/class/pwm/pwmchip0'):
            raise Exception("PWM chip not found. Ensure dtoverlay=pwm-pi5 is in /boot/firmware/config.txt")

        # Initialize PWM channels - library may warn about config but will work
        for name, config in PWM_TEST_CHANNELS.items():
            try:
                pwm = HardwarePWM(
                    pwm_channel=config['channel'],
                    hz=PWM_SETTINGS['frequency'],
                    chip=PI5_PWM_CHIP
                )
                pwm_objects[name] = pwm
                print(f"  {config['name']}: Channel {config['channel']} (GPIO {config['gpio']}) - Initialized")
            except Exception as lib_error:
                # Library checks for pwm-2chan but pwm-pi5 works too
                error_msg = str(lib_error)
                if "dtoverlay=pwm-2chan" in error_msg:
                    print(f"\nNote: Library expects 'pwm-2chan' but 'pwm-pi5' overlay is active.")
                    print("The overlay IS working. Verify with:")
                    print("  ls /sys/class/pwm/pwmchip0")
                    print()
                raise

        print()
        print("PWM initialization: PASSED")
        print()
        return True, pwm_objects

    except Exception as e:
        print()
        print(f"PWM initialization: FAILED - {e}")
        print()
        print("Troubleshooting:")
        print("1. Ensure PWM is enabled in /boot/firmware/config.txt:")
        print("   dtoverlay=pwm-pi5")
        print("2. Reboot after changing config.txt")
        print("3. Verify PWM chip exists: ls /sys/class/pwm/")
        print("4. Install library: sudo pip3 install rpi-hardware-pwm")
        print()
        return False, pwm_objects

def test_esc_arming(pwm_objects):
    """Test ESC arming sequence"""
    print("Testing ESC arming sequence...")
    print("-" * 50)

    try:
        neutral_duty = pulse_to_duty_cycle(PWM_SETTINGS['neutral'])

        print("Sending neutral signal (1500µs, 7.5% duty)...")
        for name, pwm in pwm_objects.items():
            config = PWM_TEST_CHANNELS[name]
            pwm.start(neutral_duty)
            print(f"  {config['name']}: Neutral signal sent")

        print("  Waiting 3 seconds for ESC arming...")
        time.sleep(3)
        print()
        print("ESC arming: PASSED")
        print()
        return True

    except Exception as e:
        print()
        print(f"ESC arming: FAILED - {e}")
        print()
        return False

def test_esc_control(pwm_objects):
    """Test ESC control (forward, reverse, neutral)"""
    print("Testing ESC control...")
    print("-" * 50)

    try:
        forward_duty = pulse_to_duty_cycle(PWM_SETTINGS['max_pulse'])
        reverse_duty = pulse_to_duty_cycle(PWM_SETTINGS['min_pulse'])
        neutral_duty = pulse_to_duty_cycle(PWM_SETTINGS['neutral'])

        for name, pwm in pwm_objects.items():
            config = PWM_TEST_CHANNELS[name]
            print(f"\n{config['name']} (GPIO {config['gpio']}):")

            # Forward
            pwm.change_duty_cycle(forward_duty)
            print(f"  Forward (2000µs, 10% duty)...")
            time.sleep(1)

            # Neutral
            pwm.change_duty_cycle(neutral_duty)
            print(f"  Neutral (1500µs, 7.5% duty)...")
            time.sleep(0.5)

            # Reverse
            pwm.change_duty_cycle(reverse_duty)
            print(f"  Reverse (1000µs, 5% duty)...")
            time.sleep(1)

            # Back to neutral
            pwm.change_duty_cycle(neutral_duty)
            print(f"  Neutral (1500µs, 7.5% duty)")
            time.sleep(0.5)

        print()
        print("ESC control: PASSED")
        print()
        return True

    except Exception as e:
        print()
        print(f"ESC control: FAILED - {e}")
        print()
        return False

def cleanup_pwm(pwm_objects):
    """Safely stop all PWM outputs"""
    print("Stopping PWM outputs...")
    neutral_duty = pulse_to_duty_cycle(PWM_SETTINGS['neutral'])

    for name, pwm in pwm_objects.items():
        try:
            pwm.change_duty_cycle(neutral_duty)
            time.sleep(0.1)
            pwm.stop()
            config = PWM_TEST_CHANNELS[name]
            print(f"  {config['name']}: Stopped")
        except Exception as e:
            print(f"  {name}: Error during cleanup - {e}")
    print()

def main():
    """Run Raspberry Pi PWM tests"""
    print()

    pwm_objects = {}

    try:
        tests = []

        # Initialize PWM
        init_passed, pwm_objects = test_pwm_init()
        results = {"PWM Initialization": init_passed}

        if init_passed:
            # Run ESC tests
            arm_passed = test_esc_arming(pwm_objects)
            results["ESC Arming"] = arm_passed

            if arm_passed:
                control_passed = test_esc_control(pwm_objects)
                results["ESC Control"] = control_passed

        print("=" * 50)
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
            print("All tests passed! Raspberry Pi PWM is working.")
            print()
            print("Note: Only 2 ESCs can be controlled simultaneously")
            print("with native Pi 5 PWM. For 3-thruster operation,")
            print("use the Adafruit PCA9685 PWM hat instead.")
        else:
            print("Some tests failed. Check configuration and connections.")

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user!")

    finally:
        # Always cleanup PWM
        if pwm_objects:
            cleanup_pwm(pwm_objects)

if __name__ == "__main__":
    main()
