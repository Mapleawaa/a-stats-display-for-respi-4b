# Raspberry Pi ST7789V3 Display System

This project implements a web-controlled information display system using a Raspberry Pi and an ST7789V3-based display.

## Project Structure

```
raspberry_display_project/
├── app.py                    # Main Flask application
├── display_driver.py         # ST7789V3 display driver (using Adafruit CircuitPython library)
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── static/                   # Frontend static files
│   ├── style.css             # CSS styling
│   └── script.js             # Frontend JavaScript
├── templates/                # HTML templates
│   └── index.html            # Main frontend page
├── fonts/                    # Font files
│   └── default_font.ttf      # Default font (placeholder)
├── Adafruit_CircuitPython_ST7789/  # Adafruit CircuitPython library source
└── prompt.md                 # Original design document
```

## Setup Instructions

### On Raspberry Pi:

1. **Install UV Package Manager** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source ~/.bashrc
   ```

2. **Enable SPI interface** on the Raspberry Pi:
   ```bash
   sudo raspi-config
   # Navigate to: Interfacing Options -> SPI -> Enable
   ```

3. **Install project dependencies**:
   ```bash
   cd ~/raspberry_display_project
   uv pip install -r requirements.txt
   ```

4. **Connect your ST7789V3 display** to the Raspberry Pi following the pin connections from pi-connect.md:
   - VCC → 3.3V
   - GND → GND
   - SCL/CLK → GPIO 11 (SPI SCLK)
   - SDA/MOSI → GPIO 10 (SPI MOSI)
   - CS → GPIO 8 (SPI CE0)
   - DC → GPIO 25
   - RES → GPIO 27

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Access the web interface**:
   - From the Pi itself: http://localhost:5000
   - From another device on the same network: http://[Pi_IP_Address]:5000

## Key Changes from Original Design

- **Display Driver**: Updated to use Adafruit CircuitPython ST7789 library for better hardware compatibility
- **Dependencies**: Now uses Adafruit-Blinka and related libraries instead of raw spidev
- **GPIO Handling**: Uses CircuitPython's digitalio for more reliable GPIO operations

## Features

- Web-based control interface accessible from any device on the local network
- Display time, system information (CPU, memory, temperature), weather, and custom text
- Support for uploading and displaying images
- Clean and responsive web interface
- RESTful API for programmatic control
- Double buffering for smooth display updates

## API Endpoints

- `GET /api/display/current` - Get current display status
- `POST /api/display/text` - Display custom text
- `POST /api/display/system_info` - Display system information
- `POST /api/display/weather` - Display weather information
- `POST /api/display/time` - Display current time
- `POST /api/display/custom` - Display custom layout
- `POST /api/display/clear` - Clear the screen
- `POST /api/display/image` - Display an uploaded image
- `GET /api/display/status` - Get system status

## Hardware Requirements

- Raspberry Pi (3 or 4 recommended)
- ST7789V3-based display (240x280 resolution, 1.69-inch)
- Proper power supply for the Pi
- Network connection for web access

## Troubleshooting

- If you get SPI-related errors, ensure SPI is enabled in raspi-config
- For display initialization issues, verify the pin connections
- If the Adafruit library isn't working, ensure all dependencies are installed:
  ```bash
  pip3 install adafruit-circuitpython-st7789 Adafruit-Blinka
  ```
- If the web interface doesn't load, check that the firewall allows connections on port 5000