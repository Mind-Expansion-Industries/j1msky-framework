#!/bin/bash
# Launch Thermal Wallpaper Studio

export REPLICATE_API_TOKEN=${REPLICATE_API_TOKEN:-REPLICATE_API_TOKEN_PLACEHOLDER}
export DISPLAY=:0
export XDG_RUNTIME_DIR=/run/user/1000

cd /home/m1ndb0t/Desktop/J1MSKY/apps/thermal-wallpaper-studio
python3 src/app.py "$@"
