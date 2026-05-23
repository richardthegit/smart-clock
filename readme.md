Clock (NTP) with Temperature and Humidity Display
=================================================

# Components Required

    1. ESP32 C3
    2. SSD13XX OLED screen
    3. AHTX0 sensor

# Deployment

    ./clone_dependencies.sh
    ./libs/deploy/deploy.py .

# Setup

Once deployed, connect:

    ./libs/deploy/connect.py

And use the repl to set the wifi:

    
    from rb.core.wifi import *
    configure_wifi()
