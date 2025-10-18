"""
Display driver module for ST7789V3 screen on Raspberry Pi
This module handles communication with the ST7789V3 display using Adafruit CircuitPython library
"""
import time
import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import config

# Try to import the Adafruit ST7789 library
try:
    import adafruit_st7789
    ADAFRUIT_AVAILABLE = True
except ImportError:
    print("Adafruit ST7789 library not available. Using simulation mode.")
    ADAFRUIT_AVAILABLE = False


class ST7789V3Display:
    """Driver class for ST7789V3 display using Adafruit CircuitPython library"""
    
    def __init__(self):
        """Initialize the ST7789V3 display driver"""
        self.width = config.DISPLAY_WIDTH
        self.height = config.DISPLAY_HEIGHT
        self.rotation = config.DISPLAY_ROTATION
        
        # Create a memory image for double buffering
        self.buffer = Image.new('RGB', (self.width, self.height), config.BACKGROUND_COLOR)
        self.draw = ImageDraw.Draw(self.buffer)
        
        # Try to load the default font, fall back to default if not available
        try:
            self.default_font = ImageFont.truetype(config.FONT_PATH, config.DEFAULT_FONT_SIZE)
        except:
            self.default_font = ImageFont.load_default()
        
        # Initialize the display using Adafruit library if available
        if ADAFRUIT_AVAILABLE:
            try:
                # Create SPI bus
                spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
                
                # Create the display object
                reset_pin = digitalio.DigitalInOut(board.D27)  # Adjust pin as needed
                dc_pin = digitalio.DigitalInOut(board.D25)    # Adjust pin as needed
                cs_pin = digitalio.DigitalInOut(board.D8)    # Adjust pin as needed (CE0)
                
                self.display = adafruit_st7789.ST7789(
                    spi,
                    width=self.width,
                    height=self.height,
                    baudrate=40000000,  # 40MHz
                    polarity=0,
                    phase=0,
                    cs=cs_pin,
                    dc=dc_pin,
                    rst=reset_pin,
                    rotation=self.rotation
                )
                
                # Clear the display
                self.clear_display()
                print("Display initialized successfully using Adafruit library")
                
            except Exception as e:
                print(f"Failed to initialize display with Adafruit library: {e}")
                print("Running in simulation mode")
                self.display = None
        else:
            self.display = None
    
    def clear_display(self):
        """Clear the display to background color"""
        self.buffer = Image.new('RGB', (self.width, self.height), config.BACKGROUND_COLOR)
        self.draw = ImageDraw.Draw(self.buffer)
        
        # Send to physical display if available
        if self.display:
            try:
                # Create a blank image and show it
                blank_image = Image.new('RGB', (self.width, self.height), config.BACKGROUND_COLOR)
                self.display.image(blank_image)
            except Exception as e:
                print(f"Error clearing display: {e}")
    
    def draw_text(self, text, x, y, font_size=None, color=None, font_path=None):
        """Draw text on the screen buffer"""
        if color is None:
            color = config.DEFAULT_TEXT_COLOR
        if font_size is None:
            font_size = config.DEFAULT_FONT_SIZE
        
        # Load font if specified
        font = self.default_font
        if font_path:
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()
        elif font_size != config.DEFAULT_FONT_SIZE:
            try:
                font = ImageFont.truetype(config.FONT_PATH, font_size)
            except:
                font = ImageFont.load_default()
        
        # Draw text on buffer
        self.draw.text((x, y), text, fill=color, font=font)
    
    def draw_rectangle(self, x0, y0, x1, y1, fill=None, outline=None):
        """Draw a rectangle on the screen buffer"""
        self.draw.rectangle([x0, y0, x1, y1], fill=fill, outline=outline)
    
    def draw_line(self, x0, y0, x1, y1, fill=None, width=1):
        """Draw a line on the screen buffer"""
        self.draw.line([x0, y0, x1, y1], fill=fill, width=width)
    
    def draw_circle(self, x, y, radius, fill=None, outline=None):
        """Draw a circle on the screen buffer"""
        self.draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=fill, outline=outline)
    
    def show_image(self, image_path, x=0, y=0):
        """Display an image on the screen"""
        try:
            img = Image.open(image_path)
            img = img.convert('RGB')
            # Resize image to fit on screen if necessary
            img.thumbnail((self.width, self.height), Image.Resampling.LANCZOS)
            
            # Paste the image onto the buffer
            self.buffer.paste(img, (x, y))
        except Exception as e:
            print(f"Error showing image: {e}")
            # If there's an error, at least clear the area
            self.draw_rectangle(x, y, x + 100, y + 100, fill=config.BACKGROUND_COLOR)
    
    def update_display(self):
        """Update the physical display with the buffer contents"""
        if self.display:
            try:
                # Show the buffer image on the physical display
                self.display.image(self.buffer)
            except Exception as e:
                print(f"Error updating display: {e}")
        else:
            # In simulation mode, just print that we would update
            print("SIMULATION: Display buffer updated (not shown on physical display)")


# For testing purposes
if __name__ == "__main__":
    display = ST7789V3Display()
    
    # Clear the display
    display.clear_display()
    
    # Draw some text
    display.draw_text("Hello, ST7789V3!", 20, 50, font_size=24, color=config.PRIMARY_COLOR)
    display.draw_text("Raspberry Pi Display", 10, 100, font_size=16, color=config.SECONDARY_COLOR)
    
    # Draw some shapes
    display.draw_rectangle(10, 150, 100, 200, fill=config.SECONDARY_COLOR)
    display.draw_circle(150, 175, 25, outline=config.PRIMARY_COLOR, width=2)
    display.draw_line(10, 230, 230, 230, fill=config.ERROR_COLOR, width=2)
    
    # Update the display
    display.update_display()
    
    time.sleep(5)
    
    # Clear and show just text
    display.clear_display()
    display.draw_text("System Info Display", 10, 80, font_size=20, color=config.PRIMARY_COLOR)
    display.draw_text("Ready for commands!", 30, 120, font_size=16)
    display.update_display()