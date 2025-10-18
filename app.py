"""
Main Flask application for Raspberry Pi ST7789V3 Display System
Provides REST API to control the display and serves the frontend
"""
import os
import json
from flask import Flask, request, jsonify, render_template, send_from_directory
import psutil
import platform
from datetime import datetime

# Import our display driver
from display_driver import ST7789V3Display
import config

app = Flask(__name__)

# Initialize display driver
try:
    display = ST7789V3Display()
except Exception as e:
    print(f"Error initializing display: {e}")
    print("Running in simulation mode (display commands will be logged)")
    display = None

# Store current display status
current_display_mode = "idle"
current_text = ""


@app.route('/')
def index():
    """Serve the main frontend page"""
    return render_template('index.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files (CSS, JS, images)"""
    return send_from_directory('static', filename)


@app.route('/api/display/current', methods=['GET'])
def get_current_display():
    """Get current display content status"""
    return jsonify({
        "status": "success",
        "mode": current_display_mode,
        "text": current_text,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/display/text', methods=['POST'])
def display_text():
    """Display text on screen"""
    global current_display_mode, current_text
    
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"status": "error", "message": "No text provided"}), 400
        
        current_text = text
        current_display_mode = "text"
        
        # Clear the display and show the text
        if display:
            display.clear_display()
            display.draw_text(text, 10, 100, font_size=20, color=config.PRIMARY_COLOR)
            display.update_display()
        else:
            print(f"SIMULATION: Would display text: {text}")
        
        return jsonify({
            "status": "success", 
            "message": f"Text displayed: {text}",
            "mode": current_display_mode
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/display/system_info', methods=['POST'])
def display_system_info():
    """Display system information (CPU, memory, temperature)"""
    global current_display_mode
    
    try:
        current_display_mode = "system_info"
        
        # Get system information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Try to get temperature (only works on Raspberry Pi)
        try:
            # This works on Raspberry Pi
            temp_result = os.popen('vcgencmd measure_temp').read()
            temperature = temp_result.replace('temp=', '').replace('\'C', '').strip()
        except:
            temperature = "N/A"
        
        # Format system info
        system_info = f"CPU: {cpu_percent}%\nMem: {memory.percent}%\nDisk: {disk.percent}%\nTemp: {temperature}C"
        
        if display:
            display.clear_display()
            display.draw_text("SYSTEM INFO", 20, 20, font_size=18, color=config.PRIMARY_COLOR)
            display.draw_text(system_info, 20, 60, font_size=16)
            display.update_display()
        else:
            print(f"SIMULATION: Would display system info: {system_info}")
        
        return jsonify({
            "status": "success",
            "message": "System info displayed",
            "mode": current_display_mode
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/display/weather', methods=['POST'])
def display_weather():
    """Display weather information (placeholder)"""
    global current_display_mode
    
    try:
        current_display_mode = "weather"
        
        # This would normally fetch from an API, but for now we'll use placeholder
        weather_info = "Weather: N/A\nTemp: --°C\nHumidity: --%"
        
        if display:
            display.clear_display()
            display.draw_text("WEATHER", 40, 20, font_size=20, color=config.SECONDARY_COLOR)
            display.draw_text(weather_info, 20, 80, font_size=16)
            display.update_display()
        else:
            print(f"SIMULATION: Would display weather: {weather_info}")
        
        return jsonify({
            "status": "success",
            "message": "Weather info displayed",
            "mode": current_display_mode
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/display/time', methods=['POST'])
def display_time():
    """Display current time and date"""
    global current_display_mode
    
    try:
        current_display_mode = "time"
        
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        time_info = f"{current_time}\n{current_date}"
        
        if display:
            display.clear_display()
            display.draw_text("TIME", 70, 40, font_size=18, color=config.PRIMARY_COLOR)
            display.draw_text(time_info, 20, 90, font_size=24)
            display.update_display()
        else:
            print(f"SIMULATION: Would display time: {time_info}")
        
        return jsonify({
            "status": "success",
            "message": "Time displayed",
            "mode": current_display_mode
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/display/custom', methods=['POST'])
def display_custom():
    """Display custom layout with provided data"""
    global current_display_mode
    
    try:
        data = request.get_json()
        layout = data.get('layout', {})
        
        current_display_mode = "custom"
        
        if display:
            display.clear_display()
            
            # Process the custom layout
            elements = layout.get('elements', [])
            for element in elements:
                element_type = element.get('type', '')
                x = element.get('x', 0)
                y = element.get('y', 0)
                
                if element_type == 'text':
                    text = element.get('content', '')
                    font_size = element.get('font_size', 16)
                    color_name = element.get('color', 'white')
                    
                    # Map color names to actual colors
                    color_map = {
                        'white': (255, 255, 255),
                        'red': (255, 0, 0),
                        'green': (0, 255, 0),
                        'blue': (0, 0, 255),
                        'yellow': (255, 255, 0),
                        'cyan': (0, 255, 255),
                        'magenta': (255, 0, 255),
                        'black': (0, 0, 0)
                    }
                    color = color_map.get(color_name, config.DEFAULT_TEXT_COLOR)
                    
                    display.draw_text(text, x, y, font_size=font_size, color=color)
            
            display.update_display()
        else:
            print(f"SIMULATION: Would display custom layout: {layout}")
        
        return jsonify({
            "status": "success",
            "message": "Custom display created",
            "mode": current_display_mode
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/display/clear', methods=['POST'])
def clear_display():
    """Clear the display"""
    global current_display_mode, current_text
    
    try:
        current_display_mode = "clear"
        current_text = ""
        
        if display:
            display.clear_display()
        else:
            print("SIMULATION: Would clear display")
        
        return jsonify({
            "status": "success",
            "message": "Display cleared",
            "mode": current_display_mode
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/display/image', methods=['POST'])
def display_image():
    """Display an uploaded image"""
    global current_display_mode
    
    try:
        if 'image' not in request.files:
            return jsonify({"status": "error", "message": "No image file provided"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"status": "error", "message": "No image file selected"}), 400
        
        # Save the image temporarily
        filename = file.filename
        filepath = os.path.join('static', 'temp', filename)
        
        # Create temp directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        file.save(filepath)
        
        current_display_mode = "image"
        
        if display:
            display.clear_display()
            display.show_image(filepath)
            display.update_display()
        else:
            print(f"SIMULATION: Would display image: {filepath}")
        
        return jsonify({
            "status": "success",
            "message": "Image displayed",
            "mode": current_display_mode
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/display/status', methods=['GET'])
def display_status():
    """Get the current status of the display system"""
    return jsonify({
        "status": "success",
        "current_mode": current_display_mode,
        "running": display is not None,
        "display_resolution": f"{config.DISPLAY_WIDTH}x{config.DISPLAY_HEIGHT}",
        "display_rotation": config.DISPLAY_ROTATION
    })


if __name__ == "__main__":
    print(f"Starting Raspberry Pi ST7789V3 Display Server...")
    print(f"Server will run on {config.SERVER_HOST}:{config.SERVER_PORT}")
    print(f"Display resolution: {config.DISPLAY_WIDTH}x{config.DISPLAY_HEIGHT}")
    print(f"Debug mode: {config.DEBUG_MODE}")
    
    # Start the Flask app
    app.run(host=config.SERVER_HOST, port=config.SERVER_PORT, debug=config.DEBUG_MODE)