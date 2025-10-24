# ROV Documentation

Documentation for the DIY underwater ROV project.

## Setup Guides

### Hardware Configuration

- **[Raspberry Pi 5 PWM Setup](pi5-pwm-setup.md)** - Complete guide for enabling hardware PWM on Pi 5 for ESC control

## Quick Links

### First-Time Pi Setup

If you're setting up a new Raspberry Pi 5 for the ROV:

1. Follow the [Raspberry Pi 5 PWM Setup Guide](pi5-pwm-setup.md)
2. Install ROV software dependencies (see project README)
3. Run hardware tests to verify configuration

### Test Scripts

Located in `controller/software/`:

- `test_input.py` - Test GPIO button inputs
- `test_pololu_pwm.py` - Test Pololu Maestro USB servo controller (production)
- `test_rpi_pwm.py` - Test Raspberry Pi native hardware PWM (development/testing only)

## Additional Documentation

- Project overview: See main [README.md](../README.md)
- Code instructions: See [CLAUDE.md](../CLAUDE.md)
