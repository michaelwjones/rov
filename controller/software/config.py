"""
ROV Configuration
Pin mappings and system settings
"""

# PWM channels on Adafruit PCA9685 hat (0-15 available)
THRUSTER_CHANNELS = {
    'horizontal_1': 0,  # Port thruster (left side)
    'horizontal_2': 1,  # Starboard thruster (right side)
    'vertical': 2       # Vertical thruster (up/down)
}

# GPIO pin assignments (BCM numbering)
BUTTON_PINS = {
    'h1_forward': 12,   # Horizontal thruster 1 forward
    'h1_back': 13,      # Horizontal thruster 1 back
    'h2_forward': 19,   # Horizontal thruster 2 forward
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
    'max_power': 1.0,       # Full power available
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