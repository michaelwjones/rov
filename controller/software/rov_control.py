#!/usr/bin/env python3
"""
ROV Control System
Main control script for underwater ROV with 3 thrusters
Reads button inputs and controls thrusters via Pololu Maestro
"""

import time
import RPi.GPIO as GPIO
from typing import Dict
import signal
import sys
from maestro import Controller as MaestroController, microseconds_to_target
from config import (
    BUTTON_PINS,
    THRUSTER_CHANNELS,
    PWM_SETTINGS,
    MAESTRO_CONFIG,
    SAFETY,
    SYSTEM,
    THRUSTERS
)


class ROVController:
    def __init__(self):
        """Initialize ROV controller with Maestro and GPIO"""

        # Pololu Maestro setup for thrusters
        print("Connecting to Pololu Maestro...")
        self.maestro = MaestroController(
            port=MAESTRO_CONFIG['port'],
            baud_rate=MAESTRO_CONFIG['baud_rate']
        )

        # Thruster channels from config
        self.channels = THRUSTER_CHANNELS

        # GPIO setup for buttons (BCM numbering)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Setup button pins with pull-up resistors
        print("Setting up GPIO buttons...")
        for name, pin in BUTTON_PINS.items():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        print(f"  Configured {len(BUTTON_PINS)} button inputs")

        # Current thruster states
        self.thruster_states = {
            'h1': 0.0,  # -1.0 to 1.0 (reverse to forward)
            'h2': 0.0,
            'v': 0.0
        }

        # Safety flags
        self.emergency_stop = False
        self.armed = False

        print("ROV Controller initialized")

    def arm_escs(self):
        """Arm ESCs with 3-second neutral signal"""
        print("\n" + "=" * 50)
        print("ARMING ESCs...")
        print("=" * 50)
        print("Sending neutral signal (1500µs) to all thrusters...")

        neutral_target = microseconds_to_target(PWM_SETTINGS['neutral'])

        # Send neutral to all thruster channels
        for name, channel in self.channels.items():
            self.maestro.setTarget(channel, neutral_target)
            print(f"  {name}: Channel {channel} - Neutral")

        # Wait 3 seconds for ESCs to arm
        print("\nWaiting 3 seconds for ESC arming...", end='', flush=True)
        for i in range(3):
            time.sleep(1)
            print('.', end='', flush=True)
        print(" ARMED!")

        # Apply startup safety delay
        if SAFETY['startup_delay'] > 0:
            print(f"\nSafety delay: {SAFETY['startup_delay']} seconds...", end='', flush=True)
            time.sleep(SAFETY['startup_delay'])
            print(" READY!")

        self.armed = True
        print("=" * 50)
        print("ROV READY FOR OPERATION")
        print("=" * 50 + "\n")

    def set_thruster_pwm(self, channel: int, power: float):
        """
        Set thruster power (-1.0 to 1.0)

        Args:
            channel: Maestro channel number
            power: -1.0 (full reverse) to 1.0 (full forward), 0.0 = neutral
        """
        # Safety checks
        if self.emergency_stop or not self.armed:
            power = 0.0

        # Clamp power to safe range
        power = max(-1.0, min(1.0, power))

        # Apply power limit (e.g., 0.10 = 10% of max power)
        power = power * SAFETY['power_limit']

        # Convert power to microseconds
        if power == 0:
            microseconds = PWM_SETTINGS['neutral']
        elif power > 0:
            # Forward: neutral to max_pulse
            pulse_range = PWM_SETTINGS['max_pulse'] - PWM_SETTINGS['neutral']
            microseconds = int(PWM_SETTINGS['neutral'] + (power * pulse_range))
        else:
            # Reverse: neutral to min_pulse
            pulse_range = PWM_SETTINGS['neutral'] - PWM_SETTINGS['min_pulse']
            microseconds = int(PWM_SETTINGS['neutral'] + (power * pulse_range))

        # Convert to Maestro target (quarter-microseconds) and send
        target = microseconds_to_target(microseconds)
        self.maestro.setTarget(channel, target)

    def read_buttons(self) -> Dict[str, bool]:
        """
        Read all button states

        Returns:
            Dictionary of button states (True = pressed)
        """
        button_states = {}
        for name, pin in BUTTON_PINS.items():
            # Buttons are pulled up, so pressed = LOW (False)
            button_states[name] = not GPIO.input(pin)
        return button_states

    def update_thrusters(self):
        """Main control loop - read button inputs and update thrusters"""
        buttons = self.read_buttons()

        # Horizontal thruster 1 control
        h1_power = 0.0
        if buttons['h1_forward']:
            h1_power = 1.0
        elif buttons['h1_back']:
            h1_power = -1.0

        # Apply direction multiplier from config
        h1_power *= THRUSTERS['horizontal_1']['direction_multiplier']

        # Horizontal thruster 2 control
        h2_power = 0.0
        if buttons['h2_forward']:
            h2_power = 1.0
        elif buttons['h2_back']:
            h2_power = -1.0

        # Apply direction multiplier from config
        h2_power *= THRUSTERS['horizontal_2']['direction_multiplier']

        # Vertical thruster control
        v_power = 0.0
        if buttons['v_up']:
            v_power = 1.0
        elif buttons['v_down']:
            v_power = -1.0

        # Apply direction multiplier from config
        v_power *= THRUSTERS['vertical']['direction_multiplier']

        # Update thruster states
        self.thruster_states['h1'] = h1_power
        self.thruster_states['h2'] = h2_power
        self.thruster_states['v'] = v_power

        # Send PWM signals to Maestro
        self.set_thruster_pwm(self.channels['horizontal_1'], h1_power)
        self.set_thruster_pwm(self.channels['horizontal_2'], h2_power)
        self.set_thruster_pwm(self.channels['vertical'], v_power)

    def emergency_stop_all(self):
        """Emergency stop - immediately stop all thrusters"""
        print("\n!!! EMERGENCY STOP ACTIVATED !!!")
        self.emergency_stop = True

        neutral_target = microseconds_to_target(PWM_SETTINGS['neutral'])

        # Send neutral to all channels
        for name, channel in self.channels.items():
            self.maestro.setTarget(channel, neutral_target)

        print("All thrusters stopped")

    def cleanup(self):
        """Clean shutdown - stop thrusters and close connections"""
        print("\n" + "=" * 50)
        print("Shutting down ROV controller...")
        print("=" * 50)

        # Stop all thrusters
        self.emergency_stop_all()
        time.sleep(0.2)  # Ensure signals are sent

        # Close Maestro connection
        self.maestro.close()

        # Cleanup GPIO
        GPIO.cleanup()

        print("Cleanup complete - ROV safely shut down")
        print("=" * 50)


def signal_handler(sig, frame):
    """Handle Ctrl+C and SIGTERM gracefully"""
    print("\n\nShutdown signal received...")
    if 'rov' in globals():
        rov.cleanup()
    sys.exit(0)


def main():
    """Main program entry point"""
    global rov

    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Initialize ROV controller
        print("\n" + "=" * 50)
        print("ROV CONTROL SYSTEM")
        print("=" * 50)

        rov = ROVController()

        # Arm ESCs (3 second neutral signal + safety delay)
        rov.arm_escs()

        # Display configuration
        print("Configuration:")
        print(f"  Maestro Port: {MAESTRO_CONFIG['port']}")
        print(f"  Update Rate: {SYSTEM['update_rate']} Hz")
        print(f"  PWM Range: {PWM_SETTINGS['min_pulse']}-{PWM_SETTINGS['max_pulse']}µs")
        print(f"  Power Limit: {SAFETY['power_limit']*100:.0f}% (adjust in config.py)")
        print()
        print("Button Mapping:")
        print(f"  H1 Forward: GPIO {BUTTON_PINS['h1_forward']}")
        print(f"  H1 Back:    GPIO {BUTTON_PINS['h1_back']}")
        print(f"  H2 Forward: GPIO {BUTTON_PINS['h2_forward']}")
        print(f"  H2 Back:    GPIO {BUTTON_PINS['h2_back']}")
        print(f"  V Up:       GPIO {BUTTON_PINS['v_up']}")
        print(f"  V Down:     GPIO {BUTTON_PINS['v_down']}")
        print()
        print("Press Ctrl+C to stop")
        print("=" * 50 + "\n")

        # Calculate loop delay for desired update rate
        loop_delay = 1.0 / SYSTEM['update_rate']

        # Main control loop
        last_debug_time = 0
        while True:
            # Update thrusters based on button inputs
            rov.update_thrusters()

            # Debug output (if enabled)
            if SYSTEM['debug_output']:
                current_time = time.time()
                if current_time - last_debug_time >= 1.0:  # Every 1 second
                    states = rov.thruster_states
                    print(f"[{time.strftime('%H:%M:%S')}] Thrusters - "
                          f"H1: {states['h1']:+.2f} | "
                          f"H2: {states['h2']:+.2f} | "
                          f"V: {states['v']:+.2f}")
                    last_debug_time = current_time

            # Sleep to maintain update rate
            time.sleep(loop_delay)

    except KeyboardInterrupt:
        # Handled by signal_handler
        pass
    except Exception as e:
        print(f"\n!!! ERROR: {e} !!!")
        if 'rov' in locals():
            rov.cleanup()
        raise


if __name__ == "__main__":
    main()
