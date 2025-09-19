# Claude Code Project Documentation

## Project Overview
DIY underwater ROV (Remotely Operated Vehicle) for 50ft depth operation.

## Project Structure
- **vessel/** - Underwater vehicle hardware
- **tether/** - Connection systems
- **controller/** - Surface control (Pi + buttons)

## Technology Stack
- **Platform**: Raspberry Pi 5 + Python
- **Control**: GPIO buttons → PWM thrusters
- **Status**: Software complete, ready for hardware testing

## Key Design Decisions
- **Simplified control**: Buttons only (no potentiometers)
- **Full power operation**: On/off control per thruster
- **Modular design**: Easy pin changes via config files
- **Safety first**: Emergency stops and graceful shutdown

## Development Approach
- Hardware-first project (custom PVC vessel)
- Test individual components before integration
- Prefer simple, reliable solutions over complexity