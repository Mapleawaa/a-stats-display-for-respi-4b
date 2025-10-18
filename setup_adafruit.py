#!/usr/bin/env python3
"""
Setup script to properly install the Adafruit ST7789 library for the Raspberry Pi display project
"""
import os
import shutil
import sys
from pathlib import Path

def copy_adafruit_library():
    """Copy the Adafruit CircuitPython ST7789 library to the project"""
    source_dir = Path("/Users/marecyra/项目/大项目/树莓派状态显示器/Adafruit_CircuitPython_ST7789")
    dest_dir = Path("/Users/marecyra/项目/大项目/树莓派状态显示器/adafruit_st7789")
    
    # Copy the main library file
    source_lib = source_dir / "adafruit_st7789.py"
    dest_lib = dest_dir / "adafruit_st7789.py"
    
    if source_lib.exists():
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copy2(source_lib, dest_lib)
        print(f"Copied {source_lib} to {dest_lib}")
    else:
        print(f"Source file not found: {source_lib}")
        return False
    
    return True

def create_package_init():
    """Create __init__.py to make adafruit_st7789 a proper package"""
    package_dir = Path("/Users/marecyra/项目/大项目/树莓派状态显示器/adafruit_st7789")
    init_file = package_dir / "__init__.py"
    
    with open(init_file, 'w') as f:
        f.write('"""Adafruit ST7789 library for Raspberry Pi display project"""\n')
    
    print(f"Created package init file: {init_file}")

if __name__ == "__main__":
    print("Setting up Adafruit ST7789 library for Raspberry Pi project...")
    
    if copy_adafruit_library():
        create_package_init()
        print("Adafruit ST7789 library setup completed successfully!")
    else:
        print("Failed to setup Adafruit library")
        sys.exit(1)