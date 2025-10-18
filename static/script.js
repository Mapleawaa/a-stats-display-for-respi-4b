// JavaScript交互逻辑 - 树莓派显示屏控制器

// API基础URL
const API_BASE = window.location.origin;

// 全局变量
let selectedImageFile = null;

// ==================== 初始化 ====================

document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成,初始化...');
    checkConnection();
    refreshStatus();

    // 每30秒检查一次连接状态
    setInterval(checkConnection, 30000);
});

// ==================== API通信函数 ====================

/**
 * 发送API请求
 */
async function apiRequest(endpoint, method = 'GET', body = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (body && method !== 'GET') {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || `HTTP ${response.status}`);
        }

        return data;
    } catch (error) {
        console.error('API请求失败:', error);
        throw error;
    }
}

/**
 * 上传文件
 */
async function uploadFile(endpoint, file) {
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || `HTTP ${response.status}`);
        }

        return data;
    } catch (error) {
        console.error('文件上传失败:', error);
        throw error;
    }
}

// ==================== 连接状态检查 ====================

async function checkConnection() {
    try {
        const data = await apiRequest('/api/status');
        updateConnectionStatus(true, data.driver_available);
    } catch (error) {
        updateConnectionStatus(false, false);
    }
}

function updateConnectionStatus(connected, driverAvailable) {
    const statusElement = document.getElementById('connection-status');

    if (connected && driverAvailable) {
        statusElement.textContent = '服务器已连接 · 驱动正常';
        statusElement.className = 'text-sm text-green-400';
    } else if (connected && !driverAvailable) {
        statusElement.textContent = '服务器已连接 · 驱动未初始化';
        statusElement.className = 'text-sm text-yellow-400';
    } else {
        statusElement.textContent = '服务器连接失败';
        statusElement.className = 'text-sm text-red-400';
    }
}

// ==================== 状态刷新 ====================

async function refreshStatus() {
    try {
        const data = await apiRequest('/api/display/current');

        if (data.status === 'success') {
            const displayData = data.data;

            // 更新显示状态
            document.getElementById('current-mode').textContent = displayData.mode || 'idle';
            document.getElementById('rotation').textContent = `${displayData.rotation || 90}°`;
            document.getElementById('display-resolution').textContent =
                `${displayData.width}x${displayData.height}`;

            // 更新亮度显示
            const brightness = Math.round((displayData.brightness || 0.5) * 100);
            document.getElementById('current-brightness').textContent = `${brightness}%`;

            // 更新最后更新时间
            const now = new Date();
            document.getElementById('last-update').textContent =
                now.toLocaleTimeString('zh-CN');

            addLog('状态刷新成功', 'success');
        }
    } catch (error) {
        addLog(`状态刷新失败: ${error.message}`, 'error');
    }
}

// ==================== 显示控制函数 ====================

/**
 * 显示文本
 */
async function displayText() {
    const text = document.getElementById('text-input').value.trim();

    if (!text) {
        addLog('请输入文本内容', 'warning');
        return;
    }

    const scale = parseInt(document.getElementById('text-scale').value);
    const color = parseInt(document.getElementById('text-color').value);

    try {
        const data = await apiRequest('/api/display/text', 'POST', {
            text: text,
            x: 10,
            y: 100,
            color: color,
            scale: scale,
            clear_screen: true
        });

        addLog(`✓ 已显示文本: "${text}"`, 'success');
        refreshStatus();
    } catch (error) {
        addLog(`✗ 显示文本失败: ${error.message}`, 'error');
    }
}

/**
 * 显示多行文本
 */
async function displayMultilineText() {
    const text = document.getElementById('multiline-input').value.trim();

    if (!text) {
        addLog('请输入多行文本内容', 'warning');
        return;
    }

    const lines = text.split('\n').filter(line => line.trim() !== '');
    const scale = parseInt(document.getElementById('text-scale').value);
    const color = parseInt(document.getElementById('text-color').value);

    try {
        const data = await apiRequest('/api/display/multiline', 'POST', {
            lines: lines,
            x: 10,
            y: 20,
            color: color,
            scale: scale,
            line_spacing: 25
        });

        addLog(`✓ 已显示 ${lines.length} 行文本`, 'success');
        refreshStatus();
    } catch (error) {
        addLog(`✗ 显示多行文本失败: ${error.message}`, 'error');
    }
}

/**
 * 显示系统信息
 */
async function displaySystemInfo() {
    try {
        const data = await apiRequest('/api/display/system_info', 'POST');
        addLog('✓ 已显示系统信息', 'success');

        // 同时更新右侧系统信息面板
        if (data.data) {
            updateSystemInfoPanel(data.data);
        }

        refreshStatus();
    } catch (error) {
        addLog(`✗ 显示系统信息失败: ${error.message}`, 'error');
    }
}

/**
 * 更新系统信息面板
 */
function updateSystemInfoPanel(info) {
    const container = document.getElementById('system-info');
    container.innerHTML = `
        <div class="space-y-3 text-sm">
            <div class="flex justify-between py-2 border-b border-gray-700">
                <span class="text-gray-400">CPU:</span>
                <span class="font-mono">${info.cpu_percent}</span>
            </div>
            <div class="flex justify-between py-2 border-b border-gray-700">
                <span class="text-gray-400">温度:</span>
                <span class="font-mono">${info.cpu_temp}</span>
            </div>
            <div class="flex justify-between py-2 border-b border-gray-700">
                <span class="text-gray-400">内存:</span>
                <span class="font-mono text-xs">${info.memory}</span>
            </div>
            <div class="flex justify-between py-2 border-b border-gray-700">
                <span class="text-gray-400">磁盘:</span>
                <span class="font-mono text-xs">${info.disk_percent}</span>
            </div>
            <div class="flex justify-between py-2">
                <span class="text-gray-400">负载:</span>
                <span class="font-mono text-xs">${info.load_avg}</span>
            </div>
        </div>
    `;
}

/**
 * 显示时间
 */
async function displayTime() {
    try {
        const data = await apiRequest('/api/display/time', 'POST');
        addLog('✓ 已显示当前时间', 'success');
        refreshStatus();
    } catch (error) {
        addLog(`✗ 显示时间失败: ${error.message}`, 'error');
    }
}

/**
 * 清空屏幕
 */
async function clearDisplay() {
    try {
        const data = await apiRequest('/api/display/clear', 'POST');
        addLog('✓ 屏幕已清空', 'success');
        refreshStatus();
    } catch (error) {
        addLog(`✗ 清空屏幕失败: ${error.message}`, 'error');
    }
}

// ==================== 图片处理 ====================

/**
 * 预览图片
 */
function previewImage(event) {
    const file = event.target.files[0];

    if (!file) {
        return;
    }

    // 检查文件大小(5MB)
    if (file.size > 5 * 1024 * 1024) {
        addLog('图片文件过大,请选择小于5MB的图片', 'error');
        event.target.value = '';
        return;
    }

    // 检查文件类型
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 'image/gif'];
    if (!validTypes.includes(file.type)) {
        addLog('不支持的图片格式,请选择PNG/JPG/BMP/GIF格式', 'error');
        event.target.value = '';
        return;
    }

    selectedImageFile = file;

    // 显示预览
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('preview-img').src = e.target.result;
        document.getElementById('image-preview').classList.remove('hidden');
        addLog(`图片已选择: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`, 'info');
    };
    reader.readAsDataURL(file);
}

/**
 * 上传并显示图片
 */
async function uploadImage() {
    if (!selectedImageFile) {
        addLog('请先选择图片', 'warning');
        return;
    }

    try {
        addLog('正在上传图片...', 'info');
        const data = await uploadFile('/api/display/image', selectedImageFile);

        addLog(`✓ 图片已上传并显示: ${data.filename}`, 'success');
        refreshStatus();
    } catch (error) {
        addLog(`✗ 图片上传失败: ${error.message}`, 'error');
    }
}

// ==================== 亮度控制 ====================

/**
 * 更新亮度标签
 */
function updateBrightnessLabel(value) {
    document.getElementById('brightness-value').textContent = `${value}%`;
}

/**
 * 设置亮度
 */
async function setBrightness() {
    const brightness = parseInt(document.getElementById('brightness-slider').value) / 100;

    try {
        const data = await apiRequest('/api/display/brightness', 'POST', {
            brightness: brightness
        });

        addLog(`✓ 亮度已设置为 ${Math.round(brightness * 100)}%`, 'success');
        refreshStatus();
    } catch (error) {
        addLog(`✗ 设置亮度失败: ${error.message}`, 'error');
    }
}

// ==================== 日志系统 ====================

/**
 * 添加日志
 */
function addLog(message, type = 'info') {
    const container = document.getElementById('log-container');

    // 如果是第一条日志,清空提示文本
    if (container.children.length === 1 &&
        container.children[0].textContent === '等待操作...') {
        container.innerHTML = '';
    }

    const timestamp = new Date().toLocaleTimeString('zh-CN');
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    logEntry.innerHTML = `
        <span class="text-gray-400">[${timestamp}]</span>
        <span class="ml-2">${message}</span>
    `;

    container.insertBefore(logEntry, container.firstChild);

    // 限制日志条数(最多50条)
    while (container.children.length > 50) {
        container.removeChild(container.lastChild);
    }
}

// ==================== 键盘快捷键 ====================

document.addEventListener('keydown', function(e) {
    // Enter键发送文本
    if (e.key === 'Enter' && !e.shiftKey) {
        const activeElement = document.activeElement;

        if (activeElement.id === 'text-input') {
            e.preventDefault();
            displayText();
        }
    }

    // Ctrl/Cmd + K 清空屏幕
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        clearDisplay();
    }

    // Ctrl/Cmd + T 显示时间
    if ((e.ctrlKey || e.metaKey) && e.key === 't') {
        e.preventDefault();
        displayTime();
    }

    // Ctrl/Cmd + I 显示系统信息
    if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
        e.preventDefault();
        displaySystemInfo();
    }
});

// ==================== 工具函数 ====================

/**
 * 防抖函数
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 打印初始化信息
console.log('树莓派显示屏控制器已加载');
console.log('快捷键:');
console.log('  Enter - 发送文本(在文本框中)');
console.log('  Ctrl/Cmd + K - 清空屏幕');
console.log('  Ctrl/Cmd + T - 显示时间');
console.log('  Ctrl/Cmd + I - 显示系统信息');
