"""
ST7789V3显示屏驱动模块
基于Adafruit CircuitPython ST7789库封装,提供高级显示功能
"""

import board
import displayio
import digitalio
from fourwire import FourWire
from adafruit_st7789 import ST7789
from PIL import Image, ImageDraw, ImageFont
import io
import config


class DisplayDriver:
    """ST7789显示屏驱动类"""

    def __init__(self):
        """初始化显示驱动"""
        self.display = None
        self.splash = None
        self.current_mode = "idle"
        self._init_display()

    def _init_display(self):
        """初始化显示屏硬件"""
        try:
            # 释放任何已占用的显示资源
            displayio.release_displays()

            # 配置SPI接口
            spi = board.SPI()

            # 配置控制引脚
            tft_cs = board.CE0      # CS引脚
            tft_dc = board.D24      # DC引脚
            tft_rst = board.D25     # RST引脚
            backlight = board.D12   # 背光引脚

            # 创建FourWire SPI总线
            display_bus = FourWire(
                spi,
                command=tft_dc,
                chip_select=tft_cs,
                reset=tft_rst
            )

            # 初始化ST7789显示屏
            self.display = ST7789(
                display_bus,
                width=config.DISPLAY_WIDTH,
                height=config.DISPLAY_HEIGHT,
                colstart=config.DISPLAY_COL_START,
                rowstart=config.DISPLAY_ROW_START,
                rotation=config.DISPLAY_ROTATION,
                backlight_pin=backlight,
                bgr=config.DISPLAY_BGR_MODE,
                invert=config.DISPLAY_INVERT,
            )

            # 设置默认背光亮度
            self.set_brightness(config.BACKLIGHT_DEFAULT)

            # 创建显示组
            self.splash = displayio.Group()
            self.display.root_group = self.splash

            # 清空屏幕
            self.clear()

            print(f"✓ 显示屏初始化成功: {config.DISPLAY_WIDTH}x{config.DISPLAY_HEIGHT}")

        except Exception as e:
            print(f"✗ 显示屏初始化失败: {e}")
            raise

    def set_brightness(self, brightness: float):
        """
        设置背光亮度

        Args:
            brightness: 亮度值 (0.0-1.0)
        """
        brightness = max(config.BACKLIGHT_MIN, min(brightness, config.BACKLIGHT_MAX))
        if self.display:
            self.display.brightness = brightness

    def clear(self, color=0x000000):
        """
        清空屏幕

        Args:
            color: 背景颜色 (RGB565格式,默认黑色)
        """
        # 清空显示组
        while len(self.splash) > 0:
            self.splash.pop()

        # 绘制背景
        color_bitmap = displayio.Bitmap(config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = color
        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        self.splash.append(bg_sprite)

        self.current_mode = "idle"

    def show_text(self, text: str, x=10, y=10, color=0xFFFFFF, scale=2, clear_screen=True):
        """
        显示文本

        Args:
            text: 要显示的文本
            x: X坐标
            y: Y坐标
            color: 文本颜色 (RGB565格式)
            scale: 文本缩放比例
            clear_screen: 是否先清空屏幕
        """
        from adafruit_display_text import label
        import terminalio

        if clear_screen:
            self.clear()

        # 创建文本组
        text_group = displayio.Group(scale=scale, x=x, y=y)
        text_area = label.Label(terminalio.FONT, text=text, color=color)
        text_group.append(text_area)
        self.splash.append(text_group)

        self.current_mode = "text"

    def show_multiline_text(self, lines: list, x=10, y=10, color=0xFFFFFF, scale=1, line_spacing=20):
        """
        显示多行文本

        Args:
            lines: 文本行列表
            x: 起始X坐标
            y: 起始Y坐标
            color: 文本颜色
            scale: 文本缩放
            line_spacing: 行间距
        """
        from adafruit_display_text import label
        import terminalio

        self.clear()

        for i, line in enumerate(lines):
            text_group = displayio.Group(scale=scale, x=x, y=y + i * line_spacing)
            text_area = label.Label(terminalio.FONT, text=str(line), color=color)
            text_group.append(text_area)
            self.splash.append(text_group)

        self.current_mode = "multiline_text"

    def show_image_pil(self, pil_image: Image.Image):
        """
        显示PIL图像

        Args:
            pil_image: PIL Image对象
        """
        # 调整图像大小以适应屏幕
        pil_image = pil_image.resize((config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT))

        # 转换为RGB模式
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        # 转换为displayio.Bitmap
        bitmap = displayio.Bitmap(config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT, 65536)

        for y in range(config.DISPLAY_HEIGHT):
            for x in range(config.DISPLAY_WIDTH):
                r, g, b = pil_image.getpixel((x, y))
                # 转换为RGB565格式
                rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                bitmap[x, y] = rgb565

        # 创建palette(65536色)
        palette = displayio.Palette(65536)
        for i in range(65536):
            palette[i] = i

        self.clear()
        tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
        self.splash.append(tile_grid)

        self.current_mode = "image"

    def show_image_from_bytes(self, image_bytes: bytes):
        """
        从字节流显示图像

        Args:
            image_bytes: 图像字节数据
        """
        pil_image = Image.open(io.BytesIO(image_bytes))
        self.show_image_pil(pil_image)

    def show_image_from_path(self, image_path: str):
        """
        从文件路径显示图像

        Args:
            image_path: 图像文件路径
        """
        pil_image = Image.open(image_path)
        self.show_image_pil(pil_image)

    def draw_rectangle(self, x, y, width, height, color, fill=False):
        """
        绘制矩形

        Args:
            x, y: 左上角坐标
            width, height: 宽度和高度
            color: 颜色
            fill: 是否填充
        """
        rect_bitmap = displayio.Bitmap(width, height, 1)
        rect_palette = displayio.Palette(1)
        rect_palette[0] = color
        rect_sprite = displayio.TileGrid(rect_bitmap, pixel_shader=rect_palette, x=x, y=y)
        self.splash.append(rect_sprite)

    def get_status(self):
        """
        获取当前显示状态

        Returns:
            dict: 状态信息
        """
        return {
            "mode": self.current_mode,
            "width": config.DISPLAY_WIDTH,
            "height": config.DISPLAY_HEIGHT,
            "rotation": config.DISPLAY_ROTATION,
            "brightness": self.display.brightness if self.display else 0.0
        }

    def __del__(self):
        """析构函数,清理资源"""
        if self.display:
            displayio.release_displays()


# 全局驱动实例(单例模式)
_driver_instance = None


def get_driver() -> DisplayDriver:
    """
    获取显示驱动单例实例

    Returns:
        DisplayDriver: 驱动实例
    """
    global _driver_instance
    if _driver_instance is None:
        _driver_instance = DisplayDriver()
    return _driver_instance


def init_driver():
    """初始化驱动(用于程序启动时调用)"""
    return get_driver()


if __name__ == "__main__":
    # 测试代码
    print("初始化显示驱动...")
    driver = init_driver()

    print("显示测试文本...")
    driver.show_text("Hello Raspberry Pi!", x=30, y=100, scale=2)

    import time
    time.sleep(3)

    print("显示多行文本...")
    driver.show_multiline_text([
        "Line 1: System Info",
        "Line 2: Temperature",
        "Line 3: Memory Usage",
        "Line 4: Network"
    ])

    time.sleep(3)

    print("清空屏幕...")
    driver.clear()

    print("测试完成!")
