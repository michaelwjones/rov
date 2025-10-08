# Raspberry Pi 5 Hardware PWM Setup Guide

## Overview

This guide documents how to enable hardware PWM on GPIO 12 and 13 on a Raspberry Pi 5 for ESC (Electronic Speed Controller) control in the ROV project.

## Background

The standard `dtoverlay=pwm-2chan` overlay does not work reliably on Raspberry Pi 5. This requires a custom device tree overlay to properly configure the RP1 I/O controller.

## Prerequisites

- Raspberry Pi 5 running Raspberry Pi OS Bookworm or later
- SSH or terminal access to the Pi
- Basic familiarity with command line

## Installation Steps

### 1. Create the Custom Overlay

On the Raspberry Pi, create the overlay source file:

```bash
cat > /tmp/pwm-pi5.dts << 'EOF'
/dts-v1/;
/plugin/;

/*
 * Custom PWM overlay for Raspberry Pi 5
 * Enables hardware PWM on GPIO 12 and 13
 */

/{
    compatible = "brcm,bcm2712";

    fragment@0 {
        target = <&rp1_gpio>;
        __overlay__ {
            pwm_pins: pwm_pins {
                pins = "gpio12", "gpio13";
                function = "pwm0", "pwm0";
            };
        };
    };

    fragment@1 {
        target = <&rp1_pwm0>;
        __overlay__ {
            pinctrl-names = "default";
            pinctrl-0 = <&pwm_pins>;
            status = "okay";
        };
    };
};
EOF
```

**Alternative:** The source file is also available in this repository at:
```
controller/software/pwm-pi5-overlay.dts
```

You can copy it to the Pi using SCP:
```bash
scp controller/software/pwm-pi5-overlay.dts pi@raspberrypi.local:/tmp/
```

### 2. Compile the Overlay

Compile the device tree source to a binary overlay:

```bash
dtc -I dts -O dtb -o /tmp/pwm-pi5.dtbo /tmp/pwm-pi5.dts
```

This should complete without errors.

### 3. Install the Overlay

Copy the compiled overlay to the boot firmware overlays directory:

```bash
sudo cp /tmp/pwm-pi5.dtbo /boot/firmware/overlays/
```

Verify installation:

```bash
ls -la /boot/firmware/overlays/pwm-pi5.dtbo
```

You should see:
```
-rwxr-xr-x 1 root root 621 [date] /boot/firmware/overlays/pwm-pi5.dtbo
```

### 4. Enable the Overlay in Config

Edit the boot configuration:

```bash
sudo nano /boot/firmware/config.txt
```

Or with a GUI editor:

```bash
sudo geany /boot/firmware/config.txt
```

Add this line at the end of the file (after the `[all]` section):

```
# Enable hardware PWM on GPIO 12 and 13
dtoverlay=pwm-pi5
```

Save and exit.

### 5. Install the PWM Library

Install the Python library for controlling hardware PWM:

```bash
sudo pip3 install rpi-hardware-pwm --break-system-packages
```

Note: The `--break-system-packages` flag is required on Raspberry Pi OS Bookworm.

### 6. Reboot

Reboot the Raspberry Pi to load the overlay:

```bash
sudo reboot
```

### 7. Verify Installation

After reboot, verify the PWM chip is available:

```bash
ls -la /sys/class/pwm/
```

You should see `pwmchip0` with a link to the PWM hardware:

```
total 0
drwxr-xr-x  2 root root 0 [date] .
drwxr-xr-x 71 root root 0 [date] ..
lrwxrwxrwx  1 root root 0 [date] pwmchip0 -> ../../devices/platform/axi/1000120000.pcie/1f00098000.pwm/pwm/pwmchip0
```

Check the number of PWM channels available:

```bash
cat /sys/class/pwm/pwmchip0/npwm
```

Should output: `4` (4 PWM channels available)

### 8. Test PWM Functionality

Run a quick test to verify PWM is working:

```bash
python3 << 'EOF'
from rpi_hardware_pwm import HardwarePWM
import time

# Test GPIO 12 (channel 0)
print("Testing GPIO 12 (PWM channel 0)...")
pwm = HardwarePWM(pwm_channel=0, hz=50, chip=0)
pwm.start(7.5)  # 1500us neutral signal
print("  PWM started - GPIO 12 should output 50Hz signal")
time.sleep(2)
pwm.stop()
print("  PWM stopped")

# Test GPIO 13 (channel 1)
print("\nTesting GPIO 13 (PWM channel 1)...")
pwm = HardwarePWM(pwm_channel=1, hz=50, chip=0)
pwm.start(7.5)  # 1500us neutral signal
print("  PWM started - GPIO 13 should output 50Hz signal")
time.sleep(2)
pwm.stop()
print("  PWM stopped")

print("\nPWM test complete!")
EOF
```

If both tests complete without errors, PWM is working correctly.

## Usage in ROV Software

### Python Code Example

```python
from rpi_hardware_pwm import HardwarePWM

# PWM configuration for ESCs
FREQUENCY = 50  # Hz - standard for ESCs
PWM_CHIP = 0    # Custom overlay creates pwmchip0

# Initialize PWM channels
pwm_ch0 = HardwarePWM(pwm_channel=0, hz=FREQUENCY, chip=PWM_CHIP)  # GPIO 12
pwm_ch1 = HardwarePWM(pwm_channel=1, hz=FREQUENCY, chip=PWM_CHIP)  # GPIO 13

# ESC pulse widths (microseconds)
PULSE_MIN = 1000      # Full reverse
PULSE_NEUTRAL = 1500  # Stop
PULSE_MAX = 2000      # Full forward

# Convert pulse width to duty cycle
def pulse_to_duty(pulse_us):
    period_us = 1_000_000 / FREQUENCY  # 20,000 us at 50Hz
    return (pulse_us / period_us) * 100

# Arm ESCs with neutral signal
neutral_duty = pulse_to_duty(PULSE_NEUTRAL)
pwm_ch0.start(neutral_duty)  # 7.5% duty cycle
pwm_ch1.start(neutral_duty)

# Wait for ESC arming
time.sleep(2)

# Send forward command (2000us = 10% duty cycle)
forward_duty = pulse_to_duty(PULSE_MAX)
pwm_ch0.change_duty_cycle(forward_duty)
pwm_ch1.change_duty_cycle(forward_duty)

# Send reverse command (1000us = 5% duty cycle)
reverse_duty = pulse_to_duty(PULSE_MIN)
pwm_ch0.change_duty_cycle(reverse_duty)
pwm_ch1.change_duty_cycle(reverse_duty)

# Stop PWM
pwm_ch0.stop()
pwm_ch1.stop()
```

### Using ROV Test Scripts

The ROV project includes dedicated test scripts:

**Test Raspberry Pi PWM:**
```bash
cd ~/rov/controller/software
python3 test_rpi_pwm.py
```

This will test:
- PWM initialization on GPIO 12 and 13
- ESC arming sequence
- Forward, reverse, and neutral signals

## Technical Details

### GPIO Pin Mapping

| PWM Channel | GPIO Pin | Function |
|-------------|----------|----------|
| 0           | 12       | ESC 1    |
| 1           | 13       | ESC 2    |
| 2           | 18       | Available (not configured in this overlay) |
| 3           | 19       | Available (not configured in this overlay) |

### PWM Chip Details

- **Chip Number:** 0 (not 2 as some documentation suggests)
- **Number of Channels:** 4 total (only 2 configured in this overlay)
- **Max Simultaneous Channels:** 2 (Pi 5 hardware limitation)
- **Frequency Range:** 1 Hz - 125 MHz (ESCs typically use 50 Hz)

### ESC Signal Specifications

For standard ESC control at 50Hz (20ms period):

| Signal      | Pulse Width | Duty Cycle | Function      |
|-------------|-------------|------------|---------------|
| Full Reverse| 1000 µs     | 5.0%       | Maximum reverse |
| Neutral     | 1500 µs     | 7.5%       | Stopped       |
| Full Forward| 2000 µs     | 10.0%      | Maximum forward |

## Troubleshooting

### PWM chip not found after reboot

**Check if overlay is listed in config.txt:**
```bash
cat /boot/firmware/config.txt | grep pwm
```

Should show: `dtoverlay=pwm-pi5`

**Check if overlay file exists:**
```bash
ls -la /boot/firmware/overlays/pwm-pi5.dtbo
```

**Check kernel messages for errors:**
```bash
dmesg | grep -i pwm
```

### Library error: "Need to add 'dtoverlay=pwm-2chan'"

The `rpi-hardware-pwm` library checks for `pwm-2chan` in config.txt, but the custom `pwm-pi5` overlay works correctly. This is a library validation issue, not an actual problem. The PWM will still function.

To verify PWM is working despite the warning:
```bash
ls /sys/class/pwm/pwmchip0
cat /sys/class/pwm/pwmchip0/npwm
```

### Only pwmchip0 exists, no pwmchip2

This is **correct** for the custom overlay. Use `chip=0` in your code, not `chip=2`.

### Cannot compile overlay - dtc command not found

Install device tree compiler:
```bash
sudo apt-get update
sudo apt-get install device-tree-compiler
```

### Permission denied when copying to /boot/firmware/overlays/

Use `sudo`:
```bash
sudo cp /tmp/pwm-pi5.dtbo /boot/firmware/overlays/
```

## Important Notes

### Button Pin Conflicts

The ROV control system uses GPIO buttons. To avoid conflicts with PWM pins:

- **Buttons moved from GPIO 12/13 to GPIO 5/6**
- Original button assignments conflicted with PWM channels
- See `controller/software/config.py` for current pin mappings

### Hardware Limitations

**Pi 5 can only activate 2 PWM channels simultaneously.** This means:

- ✅ Can test 2 ESCs with native PWM
- ❌ Cannot control all 3 ROV thrusters with native PWM
- ✅ Use Adafruit PCA9685 PWM hat for 3+ thruster operation

### Production Recommendation

For the ROV production system, **continue using the Adafruit PCA9685 PWM hat** because:

1. Supports 16 PWM channels (far more than needed)
2. No GPIO pin conflicts
3. Works identically on Pi 4 and Pi 5
4. Proven reliable for ESC control
5. I2C interface doesn't consume GPIO pins

The native Pi 5 PWM is useful for:
- Testing and development
- Single or dual thruster configurations
- Learning about hardware PWM

## Configuration Files

After setup, your configuration should have:

**`/boot/firmware/config.txt`:**
```ini
[all]
dtparam=uart0=on

# Enable hardware PWM on GPIO 12 and 13
dtoverlay=pwm-pi5
```

**`controller/software/config.py`:**
```python
RPI5_PWM = {
    'chip': 0,  # Using custom pwm-pi5 overlay
    'channels': {
        0: 12,  # PWM0_CHAN0 → GPIO 12
        1: 13,  # PWM0_CHAN1 → GPIO 13
    },
    'notes': [
        'Requires dtoverlay=pwm-pi5 in /boot/firmware/config.txt',
        'Custom overlay installed at /boot/firmware/overlays/pwm-pi5.dtbo'
    ]
}
```

## References

- **Overlay Source File:** `controller/software/pwm-pi5-overlay.dts`
- **Test Script:** `controller/software/test_rpi_pwm.py`
- **Configuration:** `controller/software/config.py`
- **Pi 5 RP1 Documentation:** https://datasheets.raspberrypi.com/rp1/rp1-peripherals.pdf

## Version History

| Date       | Version | Changes |
|------------|---------|---------|
| 2025-10-08 | 1.0     | Initial setup guide created |

---

**Document maintained by:** ROV Development Team
**Last updated:** October 8, 2025
