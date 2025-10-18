"""
配置文件 - 树莓派ST7789显示屏系统
包含硬件引脚定义、显示参数、网络配置等
"""

# ==================== 硬件配置 ====================

# SPI接口配置
SPI_SPEED = 24000000  # 24MHz SPI时钟速度
SPI_BUS = 0  # SPI总线编号

# GPIO引脚定义(BCM编号)
PIN_DC = 24      # 数据/命令选择引脚
PIN_RST = 25     # 硬件复位引脚
PIN_CS = 8       # 片选引脚(CE0)
PIN_BLK = 12     # PWM背光控制引脚
PIN_MOSI = 10    # SPI数据线(自动配置)
PIN_SCLK = 11    # SPI时钟线(自动配置)

# ==================== 显示屏参数 ====================

# 屏幕物理尺寸
DISPLAY_SIZE_INCH = 1.69

# 屏幕分辨率(根据旋转角度调整)
DISPLAY_ROTATION = 90  # 可选: 0, 90, 180, 270

# 不同旋转角度的分辨率配置
if DISPLAY_ROTATION in (0, 180):
    DISPLAY_WIDTH = 240
    DISPLAY_HEIGHT = 280
else:  # 90, 270度旋转
    DISPLAY_WIDTH = 280
    DISPLAY_HEIGHT = 240

# 显示偏移量(针对ST7789V3芯片特性)
DISPLAY_COL_START = 0
DISPLAY_ROW_START = 20

# 颜色配置
DISPLAY_BGR_MODE = True   # BGR颜色顺序
DISPLAY_INVERT = True     # 颜色反转

# 背光配置
BACKLIGHT_DEFAULT = 0.5   # 默认亮度(0.0-1.0)
BACKLIGHT_MIN = 0.01      # 最小亮度(0.0会完全关闭)
BACKLIGHT_MAX = 1.0       # 最大亮度

# ==================== 字体配置 ====================

# 默认字体路径
FONT_DEFAULT = "fonts/default_font.ttf"
FONT_SIZE_DEFAULT = 16
FONT_SIZE_LARGE = 24
FONT_SIZE_SMALL = 12

# 文本颜色(RGB格式)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 255, 0)

# ==================== 网络配置 ====================

# FastAPI服务器配置
SERVER_HOST = "0.0.0.0"  # 监听所有网络接口
SERVER_PORT = 8000
SERVER_RELOAD = True     # 开发模式下启用自动重载

# 跨域配置(CORS)
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
]

# ==================== 系统监控配置 ====================

# 更新间隔(秒)
SYSTEM_INFO_UPDATE_INTERVAL = 2
TIME_UPDATE_INTERVAL = 60

# 温度单位
TEMP_UNIT = "C"  # "C" 或 "F"

# ==================== 天气API配置 ====================

# 天气API配置(需要用户自行申请API密钥)
WEATHER_API_KEY = ""  # 留空,用户需自行配置
WEATHER_CITY = "Shanghai"
WEATHER_UPDATE_INTERVAL = 1800  # 30分钟

# ==================== 图片配置 ====================

# 上传图片限制
IMAGE_MAX_SIZE = 5 * 1024 * 1024  # 5MB
IMAGE_ALLOWED_FORMATS = ["PNG", "JPEG", "JPG", "BMP", "GIF"]

# ==================== 调试配置 ====================

DEBUG_MODE = True
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
