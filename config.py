"""
Configuration file for Raspberry Pi ST7789V3 Display System
"""
import os

# Display configuration
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 280
DISPLAY_ROTATION = 90  # 0, 90, 180, 270

# SPI Configuration
SPI_PORT = 0
SPI_DEVICE = 0
SPI_SPEED_HZ = 40000000  # 40MHz

# GPIO Configuration (BCM numbering)
LCD_DC_PIN = 25  # Data/Command
LCD_RST_PIN = 27  # Reset
LCD_CS_PIN = 8    # Chip Select (CE0, which is GPIO 8)

# Font configuration
FONT_PATH = os.path.join(os.path.dirname(__file__), 'fonts', 'default_font.ttf')
DEFAULT_FONT_SIZE = 16
DEFAULT_TEXT_COLOR = (255, 255, 255)  # White

# Server configuration
SERVER_HOST = '0.0.0.0'  # Listen on all interfaces
SERVER_PORT = 5000
DEBUG_MODE = True

# Default colors
BACKGROUND_COLOR = (0, 0, 0)  # Black
PRIMARY_COLOR = (0, 255, 0)    # Green
SECONDARY_COLOR = (0, 128, 255)  # Blue
ERROR_COLOR = (255, 0, 0)      # Red