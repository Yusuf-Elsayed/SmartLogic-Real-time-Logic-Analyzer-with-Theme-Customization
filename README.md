# SmartLogic: Real-Time Logic Analyzer

## Project Overview

SmartLogic is a real-time logic analyzer developed using the Atmega32 microcontroller and a Python GUI. It facilitates the real-time monitoring of signals from 8 channels, providing users with an intuitive interface for analysis.

## Features

- **Real-Time Monitoring:** View signals, amplitudes, and waveforms.
- **Channel Statistics:** Access frequency and duty cycle information.
- **Two-Way Communication:** UART connection between Atmega32 and Python GUI.
- **User-Friendly Interface:** Easily toggle channels, LEDs, and switch between dark, light, or system themes.

## Hardware Setup

- **Microcontroller:** Atmega32
- **Channels:** 8 channels (Port A)
- **Resistances:** 8 channels with 100-ohm resistors
- **Communication Interface:** USB TTL

## Software Components

### Embedded Code (C)

- **Initialization:** Configure microcontroller and UART.
- **Sampling and Sending:** Monitor signals, take time snaps, and send data frames.
- **UART Communication:** Establish communication with Python GUI.

### Python GUI

- **Initialization:** Set up GUI window, UART communication, and themes.
- **Channel Configuration:** Buttons for each channel and LED control.
- **Plotting and Visualization:** Real-time waveform plots and channel statistics.
- **Theme Selection:** Switch between dark, light, or system themes.

## Project Execution

1. **Microcontroller Setup:**
   - Upload C code to Atmega32 using avrDude or a similar tool.

2. **GUI Setup:**
   - Install Python and required libraries.
   - Run the Friendly User Python script for the GUI.

3. **Interaction:**
   - GUI communicates with Atmega32 over UART.
   - Users interact with the GUI for signal analysis.

## Authors

- Yusuf Elsayed
- Youssef Khaled
- Hager Ahmed
- Mai Kamel

## Contributing

Feel free to contribute by opening issues or pull requests.

