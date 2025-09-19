# ROV Control Software

Python control system for Raspberry Pi 5 with Adafruit PWM hat.

## Hardware Requirements
- Raspberry Pi 5 4GB
- Adafruit PCA9685 PWM hat
- 6 buttons (normally open, pull-up)

## Installation

1. **Install dependencies:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

2. **Test hardware:**
   ```bash
   python3 test_hardware.py
   ```

3. **Run control system:**
   ```bash
   python3 rov_control.py
   ```

## Pin Configuration

### Buttons (GPIO pins, BCM numbering)
- **H1 Forward**: GPIO 17
- **H1 Back**: GPIO 18
- **H2 Forward**: GPIO 19
- **H2 Back**: GPIO 20
- **V Up**: GPIO 21
- **V Down**: GPIO 22

### PWM Channels (PCA9685)
- **Horizontal 1**: Channel 0
- **Horizontal 2**: Channel 1
- **Vertical**: Channel 2


## Safety Features
- Emergency stop on Ctrl+C
- Full power operation (buttons control on/off)
- Startup delay before thruster activation
- Graceful shutdown with neutral PWM signals

## Configuration

Edit `config.py` to modify:
- Pin assignments
- PWM settings
- Safety limits
- System parameters

## Troubleshooting

### PWM Hat Not Found
```bash
sudo i2cdetect -y 1
```
Should show device at address 0x40.

### Enable I2C
```bash
sudo raspi-config
# Interface Options > I2C > Enable
```

### Test Individual Components
Use `test_hardware.py` to isolate issues.

## Auto-Start Service

To run automatically on boot:
```bash
sudo systemctl enable rov_control
sudo systemctl start rov_control
```

View logs:
```bash
sudo journalctl -u rov_control -f
```