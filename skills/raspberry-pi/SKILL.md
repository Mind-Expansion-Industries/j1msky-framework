---
name: raspberry-pi
description: Complete Raspberry Pi control including GPIO hardware, system monitoring, automation, networking, media handling, and hardware projects. Use when working with Raspberry Pi hardware (GPIO, I2C, SPI, PWM), system administration on Pi OS, hardware projects (LEDs, sensors, motors), temperature monitoring, fan control, camera modules, audio output, network configuration, cron automation, or any Pi-specific tasks requiring hardware access or system-level operations.
---

# Raspberry Pi Control

Complete hardware and system control for Raspberry Pi 4/5/Zero with full GPIO, sensor, and automation capabilities.

## Quick Commands

| Task | Command |
|------|---------|
| CPU Temp | `cat /sys/class/thermal/thermal_zone0/temp` |
| GPU Temp | `vcgencmd measure_temp` |
| Throttle Status | `vcgencmd get_throttled` |
| Clock Speeds | `vcgencmd measure_clock arm` |
| Voltage | `vcgencmd measure_volts` |
| GPIO Status | `raspi-gpio get` |
| I2C Detect | `i2cdetect -y 1` |

## Hardware Interfaces

### GPIO (General Purpose I/O)
- **40-pin header** - All pins accessible
- **Voltage** - 3.3V logic (NOT 5V tolerant!)
- **PWM** - Hardware PWM on GPIO 12, 13, 18, 19
- **Libraries** - gpiozero (easy), RPi.GPIO (legacy), pigpio (advanced)

### I2C Bus
- **Pins** - GPIO 2 (SDA), GPIO 3 (SCL)
- **Enable** - `sudo raspi-config` → Interfacing → I2C
- **Scan** - `i2cdetect -y 1` to find devices
- **Common** - Displays, sensors, RTC, expanders

### SPI Bus
- **Pins** - GPIO 9-11 (MISO/MOSI/SCLK), GPIO 7-8 (CE0/CE1)
- **Enable** - `sudo raspi-config` → Interfacing → SPI
- **Speed** - Up to 125MHz

### UART/Serial
- **Pins** - GPIO 14 (TX), GPIO 15 (RX)
- **Disable console** - Required for general use
- **USB adapters** - Common for debugging other devices

## System Monitoring

See [references/system-monitoring.md](references/system-monitoring.md) for:
- Temperature tracking and alerting
- CPU/memory monitoring
- Disk usage tracking
- Network monitoring
- Custom metrics logging

## GPIO Projects

See [references/gpio-projects.md](references/gpio-projects.md) for:
- LED control patterns
- Button/switch reading
- PWM motor control
- Sensor integration
- Multi-device setups

## Automation

See [references/automation.md](references/automation.md) for:
- Cron scheduling
- Systemd services
- File watchers
- Startup scripts
- Remote triggers

## Scripts

Pre-built scripts in `scripts/`:

| Script | Purpose |
|--------|---------|
| `temp_monitor.py` | Continuous temp logging with alerts |
| `fan_control.py` | Automatic fan control based on temp |
| `gpio_blink.py` | Basic LED blink example |
| `i2c_scan.py` | Scan and identify I2C devices |
| `system_report.sh` | Full system health report |

Use scripts directly: `python3 scripts/temp_monitor.py`

## Safety Rules

**Always:**
- Power off before wiring changes
- Use current-limiting resistors on LEDs (220Ω-1KΩ)
- Verify pinout before connecting
- Start with low voltages/currents

**Never:**
- Connect 5V directly to GPIO pins (3.3V max)
- Source/sink more than 16mA per pin, 50mA total
- Hot-plug devices that draw significant power

## External Connections

- **USB ports** - Power + data (keyboard, storage, etc.)
- **Ethernet** - Gigabit wired networking
- **WiFi** - 2.4/5GHz (Pi 3/4/5)
- **Bluetooth** - BLE capable
- **Audio jack** - Analog audio out
- **HDMI** - Video + audio out
- **CSI** - Camera module connector
- **DSI** - Display connector

## Permissions

Hardware access requires group membership:
```
gpio  - GPIO pins
i2c   - I2C bus
spi   - SPI bus
video - Camera/GPU
audio - Audio devices
```

Check: `groups`  
Add: `sudo usermod -a -G gpio,i2c,spi,audio,video $USER`

## Common Patterns

### Read CPU Temperature
```python
with open('/sys/class/thermal/thermal_zone0/temp') as f:
    temp = int(f.read()) / 1000.0
```

### Control GPIO Pin
```python
from gpiozero import LED
led = LED(17)  # GPIO 17
led.on()
led.off()
```

### PWM Fan Control
```python
from gpiozero import PWMOutputDevice
fan = PWMOutputDevice(18)  # GPIO 18
fan.value = 0.5  # 50% speed
```

### Schedule with Cron
```bash
# Edit crontab
crontab -e

# Run every minute
* * * * * /usr/bin/python3 /path/to/script.py

# Run every 5 minutes
*/5 * * * * /usr/bin/python3 /path/to/script.py
```
