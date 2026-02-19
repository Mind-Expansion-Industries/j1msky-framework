#!/bin/bash
#
# System Report - Full Raspberry Pi health report
# Usage: ./system_report.sh [--full]

set -e

FULL=false
if [ "$1" == "--full" ]; then
    FULL=true
fi

echo "═══════════════════════════════════════════════════════════════"
echo "              🥧 RASPBERRY PI SYSTEM REPORT"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Date/Time
echo "📅 Date: $(date)"
echo "⏱️   Uptime: $(uptime -p 2>/dev/null || uptime)"
echo ""

# System Info
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│ SYSTEM INFORMATION                                          │"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""

# Model detection
if [ -f /proc/device-tree/model ]; then
    MODEL=$(tr -d '\0' < /proc/device-tree/model)
    echo "   Model: $MODEL"
elif [ -f /proc/cpuinfo ]; then
    MODEL=$(grep "Model" /proc/cpuinfo | head -1 | cut -d: -f2 | sed 's/^ *//')
    echo "   Model: $MODEL"
fi

# Serial and revision
if [ -f /proc/cpuinfo ]; then
    SERIAL=$(grep Serial /proc/cpuinfo | cut -d: -f2 | sed 's/^ *//')
    REVISION=$(grep Revision /proc/cpuinfo | cut -d: -f2 | sed 's/^ *//')
    echo "   Serial: $SERIAL"
    echo "   Revision: $REVISION"
fi

# OS Info
if [ -f /etc/os-release ]; then
    source /etc/os-release
    echo "   OS: $PRETTY_NAME"
fi

# Kernel
echo "   Kernel: $(uname -r)"
echo ""

# Temperature
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│ TEMPERATURE                                                 │"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""

CPU_TEMP="N/A"
if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
    CPU_TEMP=$(awk '{printf "%.1f", $1/1000}' /sys/class/thermal/thermal_zone0/temp)
fi

GPU_TEMP="N/A"
if command -v vcgencmd > /dev/null 2>&1; then
    GPU_TEMP=$(vcgencmd measure_temp 2>/dev/null | cut -d= -f2 | cut -d\' -f1 || echo "N/A")
fi

echo -n "   CPU: ${CPU_TEMP}°C "
if [ "$CPU_TEMP" != "N/A" ]; then
    CPU_INT=$(echo "$CPU_TEMP" | cut -d. -f1)
    if [ "$CPU_INT" -lt 60 ]; then
        echo "🟢"
    elif [ "$CPU_INT" -lt 80 ]; then
        echo "🟡"
    else
        echo "🔴"
    fi
else
    echo ""
fi

echo "   GPU: ${GPU_TEMP}°C"

# Throttling status
if command -v vcgencmd > /dev/null 2>&1; then
    THROTTLE=$(vcgencmd get_throttled 2>/dev/null | cut -d= -f2 || echo "unknown")
    if [ "$THROTTLE" != "0x0" ] && [ "$THROTTLE" != "unknown" ]; then
        echo "   ⚠️  Throttling: $THROTTLE"
    fi
fi
echo ""

# CPU Info
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│ CPU                                                         │"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""

echo "   Load: $(cut -d' ' -f1-3 /proc/loadavg)"
echo "   Cores: $(nproc)"

if command -v vcgencmd > /dev/null 2>&1; then
    CLOCK=$(vcgencmd measure_clock arm 2>/dev/null | cut -d= -f2 || echo "N/A")
    if [ "$CLOCK" != "N/A" ]; then
        CLOCK_MHZ=$((CLOCK / 1000000))
        echo "   Clock: ${CLOCK_MHZ} MHz"
    fi
    
    VOLTS=$(vcgencmd measure_volts 2>/dev/null | cut -d= -f2 || echo "N/A")
    echo "   Core Voltage: $VOLTS"
fi
echo ""

# Memory
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│ MEMORY                                                      │"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""

free -h | grep -E "^Mem:" | awk '{
    total=$2
    used=$3
    free=$4
    avail=$7
    printf "   Total: %s\n", total
    printf "   Used:  %s\n", used
    printf "   Free:  %s\n", free
    printf "   Avail: %s\n", avail
}'
echo ""

# Storage
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│ STORAGE                                                     │"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""

df -h / | tail -1 | awk '{
    size=$2
    used=$3
    avail=$4
    pct=$5
    printf "   Root: %s used / %s total (%s)\n", used, size, pct
    printf "   Available: %s\n", avail
}'
echo ""

# Network
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│ NETWORK                                                     │"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""

# IP addresses
hostname -I 2>/dev/null | tr ' ' '\n' | while read ip; do
    [ -n "$ip" ] && echo "   IP: $ip"
done

# Interface stats
if $FULL; then
    echo ""
    for iface in eth0 wlan0; do
        if [ -d "/sys/class/net/$iface" ]; then
            RX=$(cat /sys/class/net/$iface/statistics/rx_bytes 2>/dev/null | awk '{printf "%.2f MB", $1/1024/1024}')
            TX=$(cat /sys/class/net/$iface/statistics/tx_bytes 2>/dev/null | awk '{printf "%.2f MB", $1/1024/1022}')
            echo "   $iface: RX $RX | TX $TX"
        fi
    done
fi
echo ""

# Hardware Interfaces (if available)
if $FULL; then
    echo "┌─────────────────────────────────────────────────────────────┐"
    echo "│ HARDWARE INTERFACES                                         │"
    echo "└─────────────────────────────────────────────────────────────┘"
    echo ""
    
    # GPIO
    if groups | grep -q gpio; then
        echo "   ✅ GPIO access enabled"
    else
        echo "   ❌ GPIO access not available"
    fi
    
    # I2C
    if [ -e /dev/i2c-1 ]; then
        echo "   ✅ I2C enabled (/dev/i2c-1)"
    else
        echo "   ❌ I2C not enabled"
    fi
    
    # SPI
    if [ -e /dev/spidev0.0 ]; then
        echo "   ✅ SPI enabled"
    else
        echo "   ❌ SPI not enabled"
    fi
    
    # Camera
    if [ -e /dev/video0 ]; then
        echo "   ✅ Camera detected"
    else
        echo "   ❌ Camera not detected"
    fi
    echo ""
fi

# Top Processes (if full)
if $FULL; then
    echo "┌─────────────────────────────────────────────────────────────┐"
    echo "│ TOP PROCESSES                                               │"
    echo "└─────────────────────────────────────────────────────────────┘"
    echo ""
    ps aux --sort=-%cpu | head -6 | tail -5 | awk '{
        printf "   %-8s %5s %5s %s\n", $1, $3, $4, $11
    }'
    echo ""
fi

echo "═══════════════════════════════════════════════════════════════"
echo "                    Report Complete ✅"
echo "═══════════════════════════════════════════════════════════════"
