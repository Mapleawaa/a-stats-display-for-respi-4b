"""
FastAPI后端服务 - 树莓派ST7789显示屏控制系统
提供RESTful API接口,响应前端请求并控制显示屏
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import psutil
import os
import time
from datetime import datetime

import config
import display_driver


# ==================== 数据模型 ====================

class TextDisplayRequest(BaseModel):
    """文本显示请求"""
    text: str
    x: int = 10
    y: int = 10
    color: int = 0xFFFFFF
    scale: int = 2
    clear_screen: bool = True


class MultiLineTextRequest(BaseModel):
    """多行文本显示请求"""
    lines: List[str]
    x: int = 10
    y: int = 10
    color: int = 0xFFFFFF
    scale: int = 1
    line_spacing: int = 20


class BrightnessRequest(BaseModel):
    """亮度控制请求"""
    brightness: float


class CustomDisplayRequest(BaseModel):
    """自定义显示请求"""
    content_type: str  # "text", "image", "system_info"
    data: dict


# ==================== FastAPI应用初始化 ====================

app = FastAPI(
    title="树莓派ST7789显示屏控制API",
    description="提供显示屏控制、系统监控、图像显示等功能",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 全局变量:显示驱动实例
driver = None


# ==================== 启动和关闭事件 ====================

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化显示驱动"""
    global driver
    try:
        print("正在初始化显示驱动...")
        driver = display_driver.init_driver()
        driver.show_text("System Ready", x=50, y=120, scale=2)
        print("✓ 显示驱动初始化成功")
    except Exception as e:
        print(f"✗ 显示驱动初始化失败: {e}")
        print("警告: 系统将在模拟模式下运行(API可用,但不会实际控制显示屏)")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    global driver
    if driver:
        driver.clear()
        print("✓ 显示驱动已清理")


# ==================== 工具函数 ====================

def get_system_info() -> dict:
    """获取系统状态信息"""
    try:
        # CPU温度(仅树莓派)
        temp = "N/A"
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp_raw = int(f.read().strip())
                temp = f"{temp_raw / 1000:.1f}°C"
        except:
            pass

        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)

        # 内存使用
        mem = psutil.virtual_memory()
        mem_used = mem.used / (1024 ** 3)  # GB
        mem_total = mem.total / (1024 ** 3)  # GB

        # 磁盘使用
        disk = psutil.disk_usage('/')
        disk_used = disk.used / (1024 ** 3)  # GB
        disk_total = disk.total / (1024 ** 3)  # GB

        # 系统负载
        load_avg = os.getloadavg()

        return {
            "cpu_temp": temp,
            "cpu_percent": f"{cpu_percent}%",
            "memory": f"{mem_used:.1f}G / {mem_total:.1f}G",
            "memory_percent": f"{mem.percent}%",
            "disk": f"{disk_used:.1f}G / {disk_total:.1f}G",
            "disk_percent": f"{disk.percent}%",
            "load_avg": f"{load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统信息失败: {str(e)}")


# ==================== API路由 ====================

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回前端页面"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>前端页面未找到</h1><p>请确保static/index.html存在</p>",
            status_code=404
        )


@app.get("/api/status")
async def get_status():
    """获取API服务状态"""
    return {
        "status": "running",
        "driver_available": driver is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/display/current")
async def get_current_display():
    """获取当前显示状态"""
    if not driver:
        raise HTTPException(status_code=503, detail="显示驱动未初始化")

    return {
        "status": "success",
        "data": driver.get_status()
    }


@app.post("/api/display/text")
async def display_text(request: TextDisplayRequest):
    """显示文本"""
    if not driver:
        raise HTTPException(status_code=503, detail="显示驱动未初始化")

    try:
        driver.show_text(
            text=request.text,
            x=request.x,
            y=request.y,
            color=request.color,
            scale=request.scale,
            clear_screen=request.clear_screen
        )
        return {"status": "success", "message": "文本已显示"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"显示文本失败: {str(e)}")


@app.post("/api/display/multiline")
async def display_multiline_text(request: MultiLineTextRequest):
    """显示多行文本"""
    if not driver:
        raise HTTPException(status_code=503, detail="显示驱动未初始化")

    try:
        driver.show_multiline_text(
            lines=request.lines,
            x=request.x,
            y=request.y,
            color=request.color,
            scale=request.scale,
            line_spacing=request.line_spacing
        )
        return {"status": "success", "message": "多行文本已显示"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"显示多行文本失败: {str(e)}")


@app.post("/api/display/system_info")
async def display_system_info():
    """显示系统信息"""
    if not driver:
        raise HTTPException(status_code=503, detail="显示驱动未初始化")

    try:
        info = get_system_info()
        lines = [
            "=== System Info ===",
            f"CPU: {info['cpu_percent']}",
            f"Temp: {info['cpu_temp']}",
            f"Mem: {info['memory']}",
            f"({info['memory_percent']})",
            f"Disk: {info['disk_percent']}",
            f"Load: {info['load_avg']}",
            f"{info['timestamp']}"
        ]
        driver.show_multiline_text(lines, x=10, y=20, scale=1, line_spacing=28)
        return {"status": "success", "message": "系统信息已显示", "data": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"显示系统信息失败: {str(e)}")


@app.post("/api/display/time")
async def display_time():
    """显示当前时间"""
    if not driver:
        raise HTTPException(status_code=503, detail="显示驱动未初始化")

    try:
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y-%m-%d")

        lines = [
            "=== Current Time ===",
            "",
            date_str,
            "",
            time_str
        ]
        driver.show_multiline_text(lines, x=30, y=60, scale=2, line_spacing=35)
        return {"status": "success", "message": "时间已显示"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"显示时间失败: {str(e)}")


@app.post("/api/display/clear")
async def clear_display():
    """清空显示屏"""
    if not driver:
        raise HTTPException(status_code=503, detail="显示驱动未初始化")

    try:
        driver.clear()
        return {"status": "success", "message": "屏幕已清空"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空屏幕失败: {str(e)}")


@app.post("/api/display/image")
async def display_image(file: UploadFile = File(...)):
    """上传并显示图片"""
    if not driver:
        raise HTTPException(status_code=503, detail="显示驱动未初始化")

    try:
        # 读取上传的图片
        contents = await file.read()

        # 检查文件大小
        if len(contents) > config.IMAGE_MAX_SIZE:
            raise HTTPException(status_code=413, detail="图片文件过大")

        # 显示图片
        driver.show_image_from_bytes(contents)

        return {
            "status": "success",
            "message": "图片已显示",
            "filename": file.filename,
            "size": len(contents)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"显示图片失败: {str(e)}")


@app.post("/api/display/brightness")
async def set_brightness(request: BrightnessRequest):
    """设置背光亮度"""
    if not driver:
        raise HTTPException(status_code=503, detail="显示驱动未初始化")

    try:
        driver.set_brightness(request.brightness)
        return {
            "status": "success",
            "message": "亮度已设置",
            "brightness": request.brightness
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置亮度失败: {str(e)}")


@app.get("/api/system/info")
async def get_system_info_api():
    """获取系统信息(不显示到屏幕)"""
    return {
        "status": "success",
        "data": get_system_info()
    }


# ==================== 主程序入口 ====================

if __name__ == "__main__":
    print("=" * 50)
    print("树莓派ST7789显示屏控制系统")
    print("=" * 50)
    print(f"服务器地址: http://{config.SERVER_HOST}:{config.SERVER_PORT}")
    print(f"API文档: http://localhost:{config.SERVER_PORT}/docs")
    print("=" * 50)

    uvicorn.run(
        "app:app",
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        reload=config.SERVER_RELOAD
    )
