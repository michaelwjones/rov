# Vessel

The main underwater vehicle housing all the core components.

## Body
- **Material**: PVC construction
- **Buoyancy**: Positive buoyancy from sealed PVC pipes, adjustable with washers
- **Target**: Neutral buoyancy

## Lighting
- 2x waterproof flashlights (manual operation)

## Camera
- **Model**: Akaso EK7000 (GoPro analog)
- **Operation**: Manual

## Thrusters
- **Horizontal**: 2x Apisqueen U2 Mini 16V 130W (1 CW, 1 CCW)
- **Vertical**: 1x Apisqueen U2 Mini 16V 130W (CW)
- **ESCs**: Built-in on all thrusters
- **Control**: PWM from Raspberry Pi via Adafruit PWM hat

## Power
- **Supply**: TBD - Recommendations:
  - **16V Li-Po**: 4S (14.8V nominal) works well, compact
  - **18V Tool Battery**: DeWalt/Milwaukee, readily available
  - **12V + Step-up**: More common, need DC-DC converter to 16V
- **Requirements**: ~25A peak (all 3 thrusters max), ~8-12A typical
- **Distribution**: To thrusters via tether from surface controller

## Notes
- All components chosen for underwater operation
- Buoyancy can be fine-tuned with washers
- Thruster configuration provides 3-axis control