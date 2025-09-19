# Tether

Connection systems between vessel and surface controller.

## Video Feed (Separate System)
- **Camera Cable**: 15 meter underwater camera cable
- **Connection**: USB to WiFi device (independent of control system)
- **Output**: Wireless broadcast to phone
- **Purpose**: Live view from vessel

## Power & Control Tether
- **Control Signals**: PWM to thrusters from Raspberry Pi
- **Power**: TBD power supply to vessel (16V for thrusters)
- **Length**: TBD (targeting 50ft operating depth)

## Notes
- Video and control are separate systems
- Video range limited to 15m by camera cable
- Control tether carries both power and PWM signals
- Raspberry Pi located in surface controller, not underwater