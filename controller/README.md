# Controller

Surface control interface for ROV operation.

## Inputs
- **Buttons**: 6 total (2 per thruster - forward/back)
  - Horizontal thruster 1: Forward/Back
  - Horizontal thruster 2: Forward/Back
  - Vertical thruster: Up/Down

## Processing
- **Computer**: Raspberry Pi 5 4GB (Raspberry Pi OS 64-bit) (located in controller enclosure)
- **PWM Generation**: Pololu Mini Maestro 12-channel servo controller
- **Current PWM Usage**: 3 channels (1 per thruster)
- **Available Expansion**: 9 additional channels for future features

## Interface
- Buttons wired directly to Raspberry Pi GPIO pins
- Software: Complete - full power on/off control per thruster

## Connection
- Connected to vessel via tether (power + control signals)

## Wiring: Raspberry Pi 5 → Pololu Maestro

### TTL Serial Connection
The Maestro communicates with the Pi via UART (TTL serial):

| Raspberry Pi 5 | → | Pololu Maestro |
|----------------|---|----------------|
| GPIO 14 (TX)   | → | RX pin         |
| GPIO 15 (RX)   | → | TX pin         |
| GND            | → | GND            |

**Important:**
- Maestro requires separate power supply (do NOT power from Pi)
- UART must be enabled in `/boot/firmware/config.txt`
- Serial console must be disabled for UART use

## Notes
- All control processing happens on Raspberry Pi
- TTL serial connection provides reliable PWM generation
- 12 channels total (9 available for expansion)
- Controller layout designed for intuitive operation
- No I2C required - simpler wiring than HAT-based solutions