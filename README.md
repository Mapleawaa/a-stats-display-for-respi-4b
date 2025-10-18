# 🍓 树莓派ST7789显示屏控制系统

基于树莓派4B和ST7789V3显示芯片的远程可控信息显示系统,提供友好的Web界面实现实时内容更新。

## 📋 项目概述

- **显示屏**: 1.69英寸 ST7789V3 (240×280分辨率)
- **硬件平台**: 树莓派4B
- **通信协议**: SPI
- **架构**: Web前端 + FastAPI后端 + 硬件驱动层

## ✨ 核心功能

- ✅ 实时文本显示(单行/多行)
- ✅ 系统状态监控(CPU/内存/温度/负载)
- ✅ 当前时间显示
- ✅ 图片上传与显示
- ✅ PWM背光亮度调节
- ✅ 响应式Web控制界面
- ✅ RESTful API接口
- ✅ 自动API文档(FastAPI Swagger)

## 🔌 硬件连接

| 显示屏引脚 | 树莓派BCM | 功能说明 |
|-----------|-----------|---------|
| GND       | GND       | 公共地线 |
| VCC       | 3.3V      | 电源(⚠️严禁使用5V) |
| SCL       | GPIO11    | SPI时钟线 |
| SDA       | GPIO10    | SPI数据线(MOSI) |
| DC        | GPIO24    | 数据/命令选择 |
| RES       | GPIO25    | 硬件复位 |
| CS        | GPIO8     | 片选(CE0) |
| BLK       | GPIO12    | PWM背光控制 |

详细接线说明请参考 `.docs/pi-connect.md`

## 📦 安装部署

### 1. 系统环境准备

确保树莓派已安装Raspberry Pi OS(推荐Bookworm或更新版本):

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 启用SPI接口
sudo raspi-config
# 选择: Interfacing Options -> SPI -> Enable

# 安装Python依赖
sudo apt install python3-pip python3-venv -y
```

### 2. 克隆项目

```bash
cd ~
git clone <repository-url>
cd 树莓派状态显示器
```

### 3. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
```

### 4. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 5. 配置调整(可选)

编辑 `config.py` 根据实际需求调整:
- 显示旋转角度
- 默认亮度
- 服务器端口
- 颜色配置等

## 🚀 运行项目

### 启动服务器

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动FastAPI服务
python app.py
```

服务器将在以下地址启动:
- Web界面: `http://<树莓派IP>:8000`
- API文档: `http://<树莓派IP>:8000/docs`

### 测试驱动(可选)

```bash
# 独立测试显示驱动
python display_driver.py
```

## 🌐 使用方法

### Web界面操作

1. 在同一局域网的设备上打开浏览器
2. 访问 `http://<树莓派IP>:8000`
3. 使用可视化界面控制显示内容:
   - **快速操作**: 一键显示时间/系统状态/清屏
   - **文本显示**: 输入单行或多行文本
   - **图片上传**: 支持PNG/JPG/BMP/GIF格式
   - **亮度控制**: 滑块调节背光亮度

### 键盘快捷键

- `Enter` - 发送文本(在文本框中)
- `Ctrl/Cmd + K` - 清空屏幕
- `Ctrl/Cmd + T` - 显示时间
- `Ctrl/Cmd + I` - 显示系统信息

## 🔧 API接口

### 显示控制

- `POST /api/display/text` - 显示单行文本
- `POST /api/display/multiline` - 显示多行文本
- `POST /api/display/system_info` - 显示系统信息
- `POST /api/display/time` - 显示当前时间
- `POST /api/display/image` - 上传并显示图片
- `POST /api/display/clear` - 清空屏幕
- `POST /api/display/brightness` - 设置亮度

### 状态查询

- `GET /api/status` - 服务器状态
- `GET /api/display/current` - 当前显示状态
- `GET /api/system/info` - 系统信息(不显示到屏幕)

完整API文档: `http://<树莓派IP>:8000/docs`

## 📁 项目结构

```
树莓派状态显示器/
├── app.py                    # FastAPI主程序
├── display_driver.py         # ST7789显示驱动封装
├── config.py                 # 配置文件
├── requirements.txt          # Python依赖
├── CLAUDE.md                 # AI助手项目文档
├── README.md                 # 项目说明
├── static/                   # 前端静态文件
│   ├── index.html           # Web界面
│   ├── style.css            # 样式表
│   └── script.js            # 交互逻辑
├── fonts/                    # 字体文件目录
└── .drivers/                 # Adafruit驱动库
    └── Adafruit_CircuitPython_ST7789/
```

## ⚙️ 配置说明

### 显示旋转

在 `config.py` 中修改 `DISPLAY_ROTATION`:
- `0` / `180` - 竖屏模式 (240×280)
- `90` / `270` - 横屏模式 (280×240)

### GPIO引脚映射

如需修改引脚,编辑 `config.py` 中的 `PIN_*` 常量,并确保硬件连接一致。

### 网络配置

- `SERVER_HOST` - 默认 `0.0.0.0` (监听所有接口)
- `SERVER_PORT` - 默认 `8000`
- `CORS_ORIGINS` - 允许跨域的源列表

## 🛠️ 故障排查

### 驱动初始化失败

**症状**: 启动时提示"显示驱动初始化失败"

**检查项**:
1. SPI接口是否已启用: `ls /dev/spi*`
2. 硬件连接是否正确(参考硬件连接表)
3. 电源是否为3.3V(误用5V会损坏硬件)
4. 执行 `sudo usermod -a -G spi,gpio $USER` 添加权限

### 权限错误

```bash
# 添加当前用户到相关组
sudo usermod -a -G spi,gpio,i2c $USER

# 重新登录生效
logout
```

### 网页无法访问

1. 检查防火墙: `sudo ufw allow 8000`
2. 确认服务器运行: `ps aux | grep uvicorn`
3. 检查IP地址: `hostname -I`

### 显示内容错乱

1. 检查 `config.py` 中的 `DISPLAY_ROW_START` 偏移量
2. 尝试不同的 `DISPLAY_ROTATION` 角度
3. 调整 `DISPLAY_BGR_MODE` 和 `DISPLAY_INVERT` 设置

## 🔐 安全建议

- 仅在受信任的局域网内运行
- 生产环境建议添加身份验证(修改 `app.py`)
- 定期更新系统和依赖包

## 📚 技术栈

- **后端**: Python 3.9+ · FastAPI · Uvicorn
- **前端**: HTML5 · Tailwind CSS · Vanilla JavaScript
- **驱动**: Adafruit CircuitPython ST7789
- **图像**: Pillow (PIL)
- **监控**: psutil

## 🤝 扩展开发

### 添加自定义显示模式

1. 在 `display_driver.py` 中添加新方法
2. 在 `app.py` 中创建对应的API端点
3. 更新前端界面添加触发按钮

### 集成天气API

参考 `config.py` 中的 `WEATHER_API_KEY` 配置说明,实现第三方天气数据获取。

## 📄 许可证

本项目遵循MIT许可证,详见LICENSE文件。

## 🙏 致谢

- [Adafruit CircuitPython ST7789](https://github.com/adafruit/Adafruit_CircuitPython_ST7789)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Tailwind CSS](https://tailwindcss.com/)

## 📮 联系方式

项目问题和建议请提交到GitHub Issues。

---

**版本**: 1.0.0
**最后更新**: 2025-10-18
