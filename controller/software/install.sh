#!/bin/bash
# ROV Control Software Installation Script

echo "Installing ROV control software dependencies..."

# Update system
sudo apt update

# Install Python dependencies
pip3 install -r requirements.txt

# Enable I2C interface
echo "Enabling I2C interface..."
sudo raspi-config nonint do_i2c 0

# Set up systemd service for auto-start (optional)
echo "Setting up systemd service..."
sudo cp rov_control.service /etc/systemd/system/
sudo systemctl daemon-reload

echo "Installation complete!"
echo ""
echo "To start the ROV control system:"
echo "  python3 rov_control.py"
echo ""
echo "To enable auto-start on boot:"
echo "  sudo systemctl enable rov_control"
echo "  sudo systemctl start rov_control"
echo ""
echo "To check I2C devices:"
echo "  sudo i2cdetect -y 1"