# GPIO Projects Reference

Hardware projects using Raspberry Pi GPIO pins with practical examples.

## Pin Reference

```
3V3  (1)  (2)  5V
GPIO2  (3)  (4)  5V
GPIO3  (5)  (6)  GND
GPIO4  (7)  (8)  GPIO14
GND  (9)  (10) GPIO15
GPIO17 (11) (12) GPIO18
GPIO27 (13) (14) GND
GPIO22 (15) (16) GPIO23
3V3  (17) (18) GPIO24
GPIO10 (19) (20) GND
GPIO9  (21) (22) GPIO25
GPIO11 (23) (24) GPIO8
GND  (25) (26) GPIO7
GPIO0  (27) (28) GPIO1
GPIO5  (29) (30) GND
GPIO6  (31) (32) GPIO12
GPIO13 (33) (34) GND
GPIO19 (35) (36) GPIO16
GPIO26 (37) (38) GPIO20
GND  (39) (40) GPIO21
```

## LED Control

### Basic LED
```python
from gpiozero import LED
from time import sleep

led = LED(17)  # GPIO 17

led.on()
sleep(1)
led.off()
```

### PWM LED (Dimming)
```python
from gpiozero import PWMLED
from time import sleep

led = PWMLED(17)

# Fade in/out
while True:
    for brightness in range(0, 101):
        led.value = brightness / 100
        sleep(0.02)
    for brightness in range(100, -1, -1):
        led.value = brightness / 100
        sleep(0.02)
```

### RGB LED
```python
from gpiozero import RGBLED
from time import sleep

led = RGBLED(red=17, green=27, blue=22)

led.color = (1, 0, 0)  # Red
sleep(1)
led.color = (0, 1, 0)  # Green
sleep(1)
led.color = (0, 0, 1)  # Blue
sleep(1)
led.color = (1, 1, 0)  # Yellow
```

### Multiple LEDs (Traffic Light)
```python
from gpiozero import LED
from time import sleep

red = LED(17)
yellow = LED(27)
green = LED(22)

def traffic_cycle():
    red.on()
    sleep(3)
    red.off()
    yellow.on()
    sleep(1)
    yellow.off()
    green.on()
    sleep(3)
    green.off()
    yellow.on()
    sleep(1)
    yellow.off()
```

## Button Input

### Simple Button
```python
from gpiozero import Button
from signal import pause

button = Button(2)  # GPIO 2

button.when_pressed = lambda: print("Pressed!")
button.when_released = lambda: print("Released!")

pause()  # Keep program running
```

### Button with LED
```python
from gpiozero import LED, Button

led = LED(17)
button = Button(2)

# LED follows button
button.when_pressed = led.on
button.when_released = led.off

# Or toggle mode
button.when_pressed = led.toggle
```

### Hold Detection
```python
button = Button(2, hold_time=2)

def on_hold():
    print("Button held for 2 seconds!")
    # Trigger shutdown, etc.

button.when_held = on_hold
```

## Sensors

### Temperature/Humidity (DHT11/DHT22)
```python
import Adafruit_DHT

sensor = Adafruit_DHT.DHT22
pin = 4

humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
if humidity is not None and temperature is not None:
    print(f"Temp: {temperature:.1f}°C, Humidity: {humidity:.1f}%")
```

### Motion Sensor (PIR)
```python
from gpiozero import MotionSensor
from time import sleep

pir = MotionSensor(4)

pir.when_motion = lambda: print("Motion detected!")
pir.when_no_motion = lambda: print("No motion")
```

### Distance Sensor (HC-SR04)
```python
from gpiozero import DistanceSensor
from time import sleep

sensor = DistanceSensor(echo=17, trigger=18)

while True:
    print(f"Distance: {sensor.distance * 100:.1f} cm")
    sleep(1)
```

### Light Sensor (LDR with capacitor)
```python
from gpiozero import LightSensor

ldr = LightSensor(4)

print(f"Light value: {ldr.value}")
ldr.wait_for_dark()
print("It's dark!")
```

## Motors

### DC Motor with H-Bridge (L298N)
```python
from gpiozero import Motor
from time import sleep

motor = Motor(forward=17, backward=18)

motor.forward(speed=0.5)  # 50% speed
sleep(2)
motor.backward()
sleep(2)
motor.stop()
```

### Servo Motor
```python
from gpiozero import Servo
from time import sleep

servo = Servo(17)

servo.min()   # Full left
sleep(1)
servo.mid()   # Center
sleep(1)
servo.max()   # Full right
```

### Precise Servo Control
```python
from gpiozero import AngularServo
from time import sleep

servo = AngularServo(17, min_angle=-90, max_angle=90)

servo.angle = -45
sleep(1)
servo.angle = 45
```

### Stepper Motor (28BYJ-48)
```python
from gpiozero import OutputDevice
from time import sleep

# ULN2003 driver pins
IN1 = OutputDevice(17)
IN2 = OutputDevice(18)
IN3 = OutputDevice(27)
IN4 = OutputDevice(22)

sequence = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

def step(steps, delay=0.001):
    for _ in range(steps):
        for seq in sequence:
            IN1.value = seq[0]
            IN2.value = seq[1]
            IN3.value = seq[2]
            IN4.value = seq[3]
            sleep(delay)

step(512)  # ~360 degrees
```

## Relays

### Controlling High Voltage
```python
from gpiozero import OutputDevice
from time import sleep

relay = OutputDevice(17, active_high=False)  # Active-low relay

relay.on()   # Connect
sleep(5)
relay.off()  # Disconnect
```

## Buzzer

### Active Buzzer
```python
from gpiozero import Buzzer
from time import sleep

bz = Buzzer(17)

bz.on()
sleep(1)
bz.off()
```

### Passive Buzzer (Tones)
```python
from gpiozero import TonalBuzzer
from time import sleep

bz = TonalBuzzer(17)

bz.play("C4")
sleep(0.5)
bz.play("E4")
sleep(0.5)
bz.play("G4")
sleep(0.5)
bz.stop()
```

## Displays

### 16x2 LCD (I2C)
```python
from RPLCD.i2c import CharLCD

lcd = CharLCD('PCF8574', 0x27)

lcd.write_string('Hello, World!')
lcd.cursor_pos = (1, 0)
lcd.write_string('Line 2')
```

### 7-Segment Display
```python
from gpiozero import LEDBoard
from time import sleep

# Common cathode wiring
segments = LEDBoard(a=17, b=18, c=27, d=22, e=23, f=24, g=25)

DIGITS = {
    0: (1, 1, 1, 1, 1, 1, 0),
    1: (0, 1, 1, 0, 0, 0, 0),
    2: (1, 1, 0, 1, 1, 0, 1),
    # ... add more
}

def show_digit(n):
    for seg, val in zip(['a','b','c','d','e','f','g'], DIGITS[n]):
        getattr(segments, seg).value = val
```

## Advanced Patterns

### Debounced Button
```python
from gpiozero import Button

button = Button(2, bounce_time=0.05)  # 50ms debounce
```

### Callback with Args
```python
from functools import partial

def button_action(device, message):
    print(f"{device.pin}: {message}")

button.when_pressed = partial(button_action, button, "Hello!")
```

### Async GPIO (with asyncio)
```python
import asyncio
from gpiozero import Button

button = Button(2)

async def button_watcher():
    while True:
        await asyncio.to_thread(button.wait_for_press)
        print("Button pressed!")
        await asyncio.sleep(0.1)  # Debounce

asyncio.run(button_watcher())
```

### Cleanup on Exit
```python
from gpiozero import LED
from signal import signal, SIGTERM, SIGINT

led = LED(17)

def cleanup(signum, frame):
    led.off()
    print("Clean exit")
    exit(0)

signal(SIGTERM, cleanup)
signal(SIGINT, cleanup)
```
