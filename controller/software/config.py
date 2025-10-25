"""
ROV Configuration
Pin mappings and system settings
"""

# Pololu Mini Maestro 12-channel servo controller
# PWM channels (0-11 available on 12-channel version)
# This is the primary PWM solution for the ROV
# Connection: TTL serial via GPIO UART pins (not USB)
MAESTRO_CONFIG = {
    'port': '/dev/serial0',  # TTL serial port (UART on GPIO 14/15)
    'baud_rate': 9600,       # Serial baud rate (must match Maestro settings)
    'device_number': 0x0C,   # Pololu Protocol device number
    'wiring': {
        # Raspberry Pi 5 GPIO -> Pololu Maestro
        'pi_tx_gpio14': 'maestro_rx',  # GPIO 14 (TX) -> Maestro RX pin
        'pi_rx_gpio15': 'maestro_tx',  # GPIO 15 (RX) -> Maestro TX pin
        'pi_gnd': 'maestro_gnd'        # GND -> GND (required)
    },
    'notes': [
        'TTL serial connection (not USB)',
        'Maestro TX connects to Pi RX (GPIO 15)',
        'Maestro RX connects to Pi TX (GPIO 14)',
        'Shared GND connection required',
        'Maestro needs separate power supply (not from Pi)',
        'UART must be enabled in /boot/firmware/config.txt',
        'Serial console must be disabled for UART use'
    ]
}

THRUSTER_CHANNELS = {
    'horizontal_1': 0,  # Port thruster (left side)
    'horizontal_2': 1,  # Starboard thruster (right side)
    'vertical': 2       # Vertical thruster (up/down)
}

# Raspberry Pi 5 Hardware PWM Configuration (for testing only)
# IMPORTANT: Pi 5 can only use 2 PWM channels simultaneously
# This is NOT suitable for 3-thruster operation - use Pololu Maestro instead
RPI5_PWM = {
    'chip': 0,  # Using custom pwm-pi5 overlay (creates pwmchip0 with 4 channels)
    'channels': {
        # PWM Channel : GPIO Pin mapping
        0: 12,  # PWM0_CHAN0 → GPIO 12 (now available - buttons moved to GPIO 5/6)
        1: 13,  # PWM0_CHAN1 → GPIO 13 (now available - buttons moved to GPIO 5/6)
        2: 18,  # PWM0_CHAN2 → GPIO 18 (available)
        3: 19,  # PWM0_CHAN3 → GPIO 19 (still conflicts with h2_forward button)
    },
    'test_channels': {
        # Recommended channels for PWM testing (no button conflicts)
        'test_esc_1': 0,  # GPIO 12
        'test_esc_2': 1,  # GPIO 13
    },
    'max_simultaneous': 2,  # Only 2 PWM channels can be active at once
    'notes': [
        'Only one PWM pair (0-1 OR 2-3) can be active simultaneously',
        'GPIO 12/13 now available for PWM (buttons moved to GPIO 5/6)',
        'GPIO 19 still conflicts with h2_forward button',
        'Use channels 0-1 (GPIO 12/13) for PWM testing',
        'Requires dtoverlay=pwm-pi5 in /boot/firmware/config.txt (custom overlay)',
        'Custom overlay installed at /boot/firmware/overlays/pwm-pi5.dtbo',
        'Requires rpi-hardware-pwm library: sudo pip3 install rpi-hardware-pwm'
    ]
}

# GPIO pin assignments (BCM numbering)
# Note: GPIO 12, 13 moved from original design to avoid PWM conflicts
BUTTON_PINS = {
    'h1_forward': 5,    # Horizontal thruster 1 forward (was GPIO 12)
    'h1_back': 6,       # Horizontal thruster 1 back (was GPIO 13)
    'h2_forward': 19,   # Horizontal thruster 2 forward (PWM conflict - for buttons only)
    'h2_back': 20,      # Horizontal thruster 2 back
    'v_up': 21,         # Vertical thruster up
    'v_down': 16        # Vertical thruster down
}


# ESC PWM settings (microseconds)
PWM_SETTINGS = {
    'frequency': 50,        # Hz - standard for ESCs
    'neutral': 1500,        # Microseconds - stopped
    'min_pulse': 1000,      # Microseconds - full reverse
    'max_pulse': 2000,      # Microseconds - full forward
    'deadband': 50          # Microseconds around neutral
}

# Safety settings
SAFETY = {
    'max_power': 1.0,       # Full power available (1.0 = 100%)
    'power_limit': 0.10,    # Current power limit (0.10 = 10% of max)
    'startup_delay': 2.0,   # Seconds to wait before allowing thruster operation
    'heartbeat_timeout': 1.0,  # Seconds before emergency stop if no input
    'emergency_stop_gpio': 26  # GPIO pin for physical emergency stop button
}

# System settings
SYSTEM = {
    'update_rate': 20,      # Hz - main control loop frequency
    'debug_output': True,   # Print debug information
    'log_file': '/var/log/rov_control.log'
}

# Thruster configuration
THRUSTERS = {
    'horizontal_1': {
        'name': 'Port Horizontal',
        'direction_multiplier': 1,   # 1 or -1 to reverse direction
        'max_power': SAFETY['max_power']
    },
    'horizontal_2': {
        'name': 'Starboard Horizontal',
        'direction_multiplier': -1,  # Reverse for counter-rotating prop
        'max_power': SAFETY['max_power']
    },
    'vertical': {
        'name': 'Vertical',
        'direction_multiplier': 1,
        'max_power': SAFETY['max_power']
    }
}