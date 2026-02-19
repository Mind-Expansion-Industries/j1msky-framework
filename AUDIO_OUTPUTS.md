# Audio Output Switching (Alexa + Jack + HDMI)

Use this script:

```bash
cd ~/Desktop/J1MSKY
./audio-output-switch.sh list
./audio-output-switch.sh alexa
./audio-output-switch.sh jack
./audio-output-switch.sh hdmi1
./audio-output-switch.sh hdmi2
```

## Current known sinks
- Alexa Bluetooth: `bluez_output.EC_0D_E4_92_37_5A.1`
- 3.5mm Jack: `alsa_output.platform-fe00b840.mailbox.stereo-fallback`
- HDMI 1: `alsa_output.platform-fef00700.hdmi.hdmi-stereo`

## HDMI 2 note
On Raspberry Pi, HDMI2 may only expose a sink when an active display/audio endpoint is connected.
If `hdmi2` says no sink found, plug a monitor/AVR into HDMI2 and run:

```bash
./audio-output-switch.sh hdmi2
```

## Keep Alexa + local outputs
You can switch anytime without breaking setup.

