#!/usr/bin/env python3
"""
Pololu Maestro Servo Controller Library
Simple Python interface for controlling servos and ESCs via Pololu Maestro

Supports both TTL serial (UART) and USB connections.
For TTL serial on Raspberry Pi 5:
  - Connect Maestro TX to Pi GPIO 15 (RX)
  - Connect Maestro RX to Pi GPIO 14 (TX)
  - Connect GND to GND
  - Maestro needs separate power supply
  - Enable UART in /boot/firmware/config.txt
"""

import serial
import time


class Controller:
    """
    Pololu Maestro servo controller interface

    Communicates with Pololu Maestro over TTL serial or USB using the Pololu Protocol.
    Supports 6, 12, 18, and 24 channel versions.

    Connection types:
      - TTL Serial (UART): Use /dev/serial0 or /dev/ttyAMA0 on Raspberry Pi
      - USB: Use /dev/ttyACM0 or /dev/ttyACM1 on Linux, COM port on Windows
    """

    def __init__(self, port='/dev/serial0', baud_rate=9600, device_number=0x0C):
        """
        Initialize connection to Pololu Maestro

        Args:
            port: Serial port path
                  TTL Serial: '/dev/serial0' or '/dev/ttyAMA0' (Raspberry Pi UART)
                  USB: '/dev/ttyACM0' (Linux), 'COM3' (Windows)
            baud_rate: Serial baud rate (default 9600, must match Maestro config)
            device_number: Pololu Protocol device number (default 0x0C for Maestro)
        """
        try:
            self.serial = serial.Serial(port, baud_rate, timeout=1)
            self.device_number = device_number
            time.sleep(0.1)  # Give serial connection time to stabilize
            print(f"Pololu Maestro connected on {port} at {baud_rate} baud")
        except serial.SerialException as e:
            raise ConnectionError(f"Failed to connect to Maestro on {port}: {e}")

    def setTarget(self, channel, target):
        """
        Set servo/ESC target position

        Args:
            channel: Channel number (0-11 for 12-channel Maestro)
            target: Target position in quarter-microseconds (e.g., 6000 = 1500us)
                   Typical range: 4000-8000 (1000us-2000us)

        For ESC control at 50Hz:
            - 1000us (4000) = Full reverse
            - 1500us (6000) = Neutral/stopped
            - 2000us (8000) = Full forward
        """
        # Pololu Protocol: 0x84, channel, target_low, target_high
        # Target is in quarter-microseconds (0.25us units)
        target = int(target)  # Ensure integer
        target_low = target & 0x7F  # Lower 7 bits
        target_high = (target >> 7) & 0x7F  # Upper 7 bits

        command = bytes([0x84, channel, target_low, target_high])
        self.serial.write(command)

    def setSpeed(self, channel, speed):
        """
        Set servo movement speed

        Args:
            channel: Channel number (0-11 for 12-channel Maestro)
            speed: Speed limit (0 = unlimited, 1-255 for slower speeds)
        """
        # Pololu Protocol: 0x87, channel, speed_low, speed_high
        speed_low = speed & 0x7F
        speed_high = (speed >> 7) & 0x7F

        command = bytes([0x87, channel, speed_low, speed_high])
        self.serial.write(command)

    def setAcceleration(self, channel, acceleration):
        """
        Set servo acceleration

        Args:
            channel: Channel number (0-11 for 12-channel Maestro)
            acceleration: Acceleration limit (0 = unlimited, 1-255 for slower acceleration)
        """
        # Pololu Protocol: 0x89, channel, accel_low, accel_high
        accel_low = acceleration & 0x7F
        accel_high = (acceleration >> 7) & 0x7F

        command = bytes([0x89, channel, accel_low, accel_high])
        self.serial.write(command)

    def getPosition(self, channel):
        """
        Get current servo position

        Args:
            channel: Channel number (0-11 for 12-channel Maestro)

        Returns:
            Current position in quarter-microseconds
        """
        # Pololu Protocol: 0x90, channel
        command = bytes([0x90, channel])
        self.serial.write(command)

        # Read 2-byte response
        response = self.serial.read(2)
        if len(response) == 2:
            position = response[0] + (response[1] << 8)
            return position
        else:
            return None

    def goHome(self):
        """
        Send all servos to home position (as configured in Maestro Control Center)
        """
        # Pololu Protocol: 0xA2
        command = bytes([0xA2])
        self.serial.write(command)

    def close(self):
        """
        Close serial connection to Maestro
        """
        if hasattr(self, 'serial') and self.serial.is_open:
            self.serial.close()
            print("Pololu Maestro connection closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Utility functions for ESC control
def microseconds_to_target(microseconds):
    """
    Convert microseconds to Maestro target value (quarter-microseconds)

    Args:
        microseconds: Pulse width in microseconds (e.g., 1500)

    Returns:
        Target value in quarter-microseconds (e.g., 6000)
    """
    return int(microseconds * 4)


def target_to_microseconds(target):
    """
    Convert Maestro target value to microseconds

    Args:
        target: Target value in quarter-microseconds (e.g., 6000)

    Returns:
        Pulse width in microseconds (e.g., 1500)
    """
    return target / 4.0
