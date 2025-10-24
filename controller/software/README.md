# ROV Control Software

Python control system for Raspberry Pi 5 with Pololu Maestro servo controller via TTL serial.

## Hardware Requirements
- Raspberry Pi 5 4GB
- Pololu Mini Maestro 12-channel servo controller
- 6 buttons (normally open, pull-up)
- 3x jumper wires for TTL serial (TX, RX, GND)

## Wiring: Raspberry Pi 5 → Pololu Maestro

| Raspberry Pi 5 | Wire Color (suggested) | Pololu Maestro |
|----------------|------------------------|----------------|
| GPIO 14 (TX)   | Yellow                 | RX pin         |
| GPIO 15 (RX)   | Orange                 | TX pin         |
| GND            | Black                  | GND            |

**Important:**
- Maestro needs separate power supply - do NOT power from Pi
- Keep wires short to minimize interference
- Double-check TX→RX and RX→TX crossover

## Installation

1. **Enable UART on Raspberry Pi 5:**
   ```bash
   sudo nano /boot/firmware/config.txt
   ```

   Add these lines at the end:
   ```
   # Enable UART for Pololu Maestro
   dtparam=uart0=on
   enable_uart=1
   ```

   Disable serial console:
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options → Serial Port
   # "Would you like a login shell accessible over serial?" → No
   # "Would you like the serial port hardware enabled?" → Yes
   ```

   Reboot:
   ```bash
   sudo reboot
   ```

2. **Verify serial port exists:**
   ```bash
   ls -la /dev/serial0 /dev/ttyAMA0
   ```

3. **Install software dependencies:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

4. **Test hardware:**
   ```bash
   python3 test_pololu_pwm.py
   ```

5. **Run control system:**
   ```bash
   python3 rov_control.py
   ```

## Pin Configuration

### Buttons (GPIO pins, BCM numbering)
- **H1 Forward**: GPIO 5
- **H1 Back**: GPIO 6
- **H2 Forward**: GPIO 19
- **H2 Back**: GPIO 20
- **V Up**: GPIO 21
- **V Down**: GPIO 16

### Serial Communication (UART)
- **TX (Transmit)**: GPIO 14 → Maestro RX
- **RX (Receive)**: GPIO 15 → Maestro TX
- **Port**: `/dev/serial0` (or `/dev/ttyAMA0`)
- **Baud Rate**: 9600 (must match Maestro settings)

### PWM Channels (Pololu Maestro)
- **Horizontal 1**: Channel 0
- **Horizontal 2**: Channel 1
- **Vertical**: Channel 2
- **Available**: Channels 3-11 for expansion


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

### Serial Port Not Found
Check if UART is enabled:
```bash
ls -la /dev/serial0 /dev/ttyAMA0
```
Should show `/dev/serial0` or `/dev/ttyAMA0`.

If not found:
1. Check `/boot/firmware/config.txt` has `dtparam=uart0=on` and `enable_uart=1`
2. Verify serial console is disabled via `raspi-config`
3. Reboot after changes

### Maestro Connection Failed
Check wiring:
- Pi GPIO 14 (TX) → Maestro RX ✓
- Pi GPIO 15 (RX) → Maestro TX ✓
- GND → GND ✓
- Maestro has separate power supply

Check baud rate:
- Maestro must be configured for 9600 baud (default)
- Use Pololu Maestro Control Center (on Windows) to verify/change

### Permission Denied
Add user to dialout group for serial port access:
```bash
sudo usermod -a -G dialout $USER
```
Log out and back in for changes to take effect.

### Wrong Port
If `/dev/serial0` doesn't work, try `/dev/ttyAMA0` in `config.py`:
```python
MAESTRO_CONFIG = {
    'port': '/dev/ttyAMA0',  # Alternative serial port
    'baud_rate': 9600,
    ...
}
```

### Baud Rate Mismatch
Ensure Maestro baud rate matches config:
- Default: 9600 baud
- Check with Pololu Maestro Control Center software
- Update `config.py` if using different baud rate

### Test Individual Components
Use `test_pololu_pwm.py` to isolate issues.

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