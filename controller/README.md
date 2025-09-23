# Controller

Surface control interface for ROV operation.

## Inputs
- **Buttons**: 6 total (2 per thruster - forward/back)
  - Horizontal thruster 1: Forward/Back
  - Horizontal thruster 2: Forward/Back
  - Vertical thruster: Up/Down

## Processing
- **Computer**: Raspberry Pi 5 4GB (Raspberry Pi OS 64-bit) (located in controller enclosure)
- **PWM Generation**: Adafruit PWM hat (~16 channels available)
- **Current PWM Usage**: 3 channels (1 per thruster)

## Interface
- Buttons wired directly to Raspberry Pi GPIO pins
- Software: Complete - full power on/off control per thruster

## Connection
- Connected to vessel via tether (power + control signals)

## Notes
- All control processing happens on Raspberry Pi
- Plenty of PWM channels available for expansion
- Controller layout designed for intuitive operation