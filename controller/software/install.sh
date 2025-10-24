#!/bin/bash
# ROV Control Software Installation Script

echo "Installing ROV control software dependencies..."
echo ""

# Update system
sudo apt update

# Install Python dependencies
echo "Installing Python packages..."
pip3 install -r requirements.txt

# Add user to dialout group for TTL serial access
echo ""
echo "Adding user to dialout group for serial port access..."
sudo usermod -a -G dialout $USER

# Check if UART is enabled
echo ""
echo "Checking UART configuration..."
if grep -q "dtparam=uart0=on" /boot/firmware/config.txt && grep -q "enable_uart=1" /boot/firmware/config.txt; then
    echo "✓ UART is already enabled in /boot/firmware/config.txt"
else
    echo "⚠ UART needs to be enabled in /boot/firmware/config.txt"
    echo ""
    echo "Add these lines to /boot/firmware/config.txt:"
    echo "  dtparam=uart0=on"
    echo "  enable_uart=1"
    echo ""
    echo "Then disable serial console via raspi-config:"
    echo "  sudo raspi-config"
    echo "  → Interface Options → Serial Port"
    echo "  → Login shell over serial: No"
    echo "  → Serial port hardware enabled: Yes"
    echo ""
    echo "Then reboot: sudo reboot"
fi

# Check if serial port exists
echo ""
echo "Checking for serial port..."
if [ -e "/dev/serial0" ]; then
    echo "✓ Serial port found: /dev/serial0"
elif [ -e "/dev/ttyAMA0" ]; then
    echo "✓ Serial port found: /dev/ttyAMA0"
else
    echo "✗ Serial port not found"
    echo "  Enable UART in /boot/firmware/config.txt and reboot"
fi

# Set up systemd service for auto-start (optional)
echo ""
echo "Setting up systemd service..."
if [ -f "rov_control.service" ]; then
    sudo cp rov_control.service /etc/systemd/system/
    sudo systemctl daemon-reload
    echo "✓ Systemd service installed"
else
    echo "⚠ rov_control.service not found - skipping"
fi

echo ""
echo "=========================================="
echo "Installation complete!"
echo "=========================================="
echo ""
echo "IMPORTANT: Log out and back in for serial permissions to take effect!"
echo ""
echo "Next steps:"
echo "  1. Wire Maestro to Pi:"
echo "     - Pi GPIO 14 (TX) → Maestro RX"
echo "     - Pi GPIO 15 (RX) → Maestro TX"
echo "     - GND → GND"
echo ""
echo "  2. Test connection:"
echo "     python3 test_pololu_pwm.py"
echo ""
echo "  3. Run control system:"
echo "     python3 rov_control.py"
echo ""
echo "To enable auto-start on boot:"
echo "  sudo systemctl enable rov_control"
echo "  sudo systemctl start rov_control"
echo ""
echo "To check serial ports:"
echo "  ls -la /dev/serial0 /dev/ttyAMA0"
echo ""