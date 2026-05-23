Automatic Light
===============

A simple light which responds to ambient levels before turning on automatically. It also uses the current time to turn off at sensible hours (i.e. after 11pm).

# Wiring for ESP32

Three components are required:

    1. ESP32 C3
    2. Phototransistor
    3. 10K ohm resistor
    4. 6 LED NeoPixel Strip 

## Phototransistor

Connect the collector (shorted leg) to **+3.3v**, and the emitter to ADC pin **GPIO 1** and **GND** via the resistor for pull-down.

## LED Strip

Power may come from the C3 using the **+5v** and **GND**. Control wire should connect to **GPIO 0**.

