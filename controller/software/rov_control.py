#!/usr/bin/env python3
"""
ROV Control System
Main control script for underwater ROV with 3 thrusters
"""

import time
import board
import busio
from adafruit_pca9685 import PCA9685
import RPi.GPIO as GPIO
from typing import Dict, Tuple
import signal
import sys

class ROVController:
    def __init__(self):
        # PWM setup for thrusters
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = 50  # 50Hz for ESCs

        # Thruster PWM channels (0-15 available)
        self.THRUSTER_HORIZONTAL_1 = 0
        self.THRUSTER_HORIZONTAL_2 = 1
        self.THRUSTER_VERTICAL = 2

        # GPIO setup for buttons (BCM numbering)
        GPIO.setmode(GPIO.BCM)

        # Button pins - 6 buttons total (2 per thruster)
        self.BUTTONS = {
            'h1_forward': 17,   # Horizontal thruster 1 forward
            'h1_back': 18,      # Horizontal thruster 1 back
            'h2_forward': 19,   # Horizontal thruster 2 forward
            'h2_back': 20,      # Horizontal thruster 2 back
            'v_up': 21,         # Vertical thruster up
            'v_down': 22        # Vertical thruster down
        }


        # Setup GPIO pins
        for pin in self.BUTTONS.values():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # PWM neutral and range values (typical ESC values)
        self.PWM_NEUTRAL = 1500  # microseconds (stopped)
        self.PWM_MIN = 1100      # microseconds (full reverse)
        self.PWM_MAX = 1900      # microseconds (full forward)

        # Current thruster states
        self.thruster_states = {
            'h1': 0.0,  # -1.0 to 1.0 (reverse to forward)
            'h2': 0.0,
            'v': 0.0
        }

        # Safety flag
        self.emergency_stop = False

        print("ROV Controller initialized")

    def microseconds_to_duty_cycle(self, microseconds: int) -> int:
        """Convert microseconds to 16-bit duty cycle value for PCA9685"""
        # PCA9685 is 12-bit (0-4095), but we use 16-bit values
        # 50Hz = 20ms period, so 1500us = 7.5% duty cycle
        duty_cycle = int((microseconds / 20000.0) * 65535)
        return min(65535, max(0, duty_cycle))

    def set_thruster_pwm(self, channel: int, power: float):
        """Set thruster power (-1.0 to 1.0)"""
        if self.emergency_stop:
            power = 0.0

        # Clamp power to safe range
        power = max(-1.0, min(1.0, power))

        # Convert power to microseconds
        if power == 0:
            microseconds = self.PWM_NEUTRAL
        elif power > 0:
            # Forward: 1500 to 1900
            microseconds = int(self.PWM_NEUTRAL + (power * (self.PWM_MAX - self.PWM_NEUTRAL)))
        else:
            # Reverse: 1500 to 1100
            microseconds = int(self.PWM_NEUTRAL + (power * (self.PWM_NEUTRAL - self.PWM_MIN)))

        duty_cycle = self.microseconds_to_duty_cycle(microseconds)
        self.pca.channels[channel].duty_cycle = duty_cycle

    def read_buttons(self) -> Dict[str, bool]:
        """Read all button states"""
        button_states = {}
        for name, pin in self.BUTTONS.items():
            # Buttons are pulled up, so pressed = False
            button_states[name] = not GPIO.input(pin)
        return button_states


    def update_thrusters(self):
        """Main control loop - read inputs and update thrusters"""
        buttons = self.read_buttons()

        # Horizontal thruster 1 control
        h1_power = 0.0
        if buttons['h1_forward']:
            h1_power = 1.0
        elif buttons['h1_back']:
            h1_power = -1.0

        # Horizontal thruster 2 control
        h2_power = 0.0
        if buttons['h2_forward']:
            h2_power = 1.0
        elif buttons['h2_back']:
            h2_power = -1.0

        # Vertical thruster control
        v_power = 0.0
        if buttons['v_up']:
            v_power = 1.0
        elif buttons['v_down']:
            v_power = -1.0

        # Update thruster states
        self.thruster_states['h1'] = h1_power
        self.thruster_states['h2'] = h2_power
        self.thruster_states['v'] = v_power

        # Send PWM signals
        self.set_thruster_pwm(self.THRUSTER_HORIZONTAL_1, h1_power)
        self.set_thruster_pwm(self.THRUSTER_HORIZONTAL_2, h2_power)
        self.set_thruster_pwm(self.THRUSTER_VERTICAL, v_power)

    def emergency_stop_all(self):
        """Emergency stop - immediately stop all thrusters"""
        self.emergency_stop = True
        self.set_thruster_pwm(self.THRUSTER_HORIZONTAL_1, 0.0)
        self.set_thruster_pwm(self.THRUSTER_HORIZONTAL_2, 0.0)
        self.set_thruster_pwm(self.THRUSTER_VERTICAL, 0.0)
        print("EMERGENCY STOP ACTIVATED")

    def cleanup(self):
        """Clean shutdown"""
        print("Shutting down ROV controller...")
        self.emergency_stop_all()
        time.sleep(0.1)  # Brief pause to ensure PWM signals are sent
        self.pca.deinit()
        GPIO.cleanup()
        print("Cleanup complete")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutdown signal received")
    if 'rov' in globals():
        rov.cleanup()
    sys.exit(0)

def main():
    global rov

    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        rov = ROVController()

        print("ROV Control System started")
        print("Use Ctrl+C to stop")
        print("Button layout:")
        print("  H1: GPIO 17 (fwd), GPIO 18 (back)")
        print("  H2: GPIO 19 (fwd), GPIO 20 (back)")
        print("  V:  GPIO 21 (up),  GPIO 22 (down)")

        # Main control loop
        while True:
            rov.update_thrusters()

            # Debug output every second
            if int(time.time()) % 1 == 0:
                states = rov.thruster_states
                print(f"Thrusters - H1: {states['h1']:+.2f}, H2: {states['h2']:+.2f}, V: {states['v']:+.2f}")
                time.sleep(0.05)  # Prevent rapid printing

            time.sleep(0.05)  # 20Hz update rate

    except Exception as e:
        print(f"Error: {e}")
        if 'rov' in locals():
            rov.cleanup()
        raise

if __name__ == "__main__":
    main()