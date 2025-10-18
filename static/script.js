/*
 * 树莓派 ST7789V3 信息显示屏系统 - 前端脚本
 */

// API base URL
const API_BASE = '/api';

// DOM elements
const elements = {
    showTimeBtn: document.getElementById('showTimeBtn'),
    showSysInfoBtn: document.getElementById('showSysInfoBtn'),
    showWeatherBtn: document.getElementById('showWeatherBtn'),
    clearScreenBtn: document.getElementById('clearScreenBtn'),
    customText: document.getElementById('customText'),
    sendTextBtn: document.getElementById('sendTextBtn'),
    imageUpload: document.getElementById('imageUpload'),
    uploadImageBtn: document.getElementById('uploadImageBtn'),
    textColorPicker: document.getElementById('textColorPicker'),
    statusMessages: document.getElementById('statusMessages'),
    currentMode: document.getElementById('currentMode'),
    statusIndicator: document.getElementById('statusIndicator'),
    ipAddress: document.getElementById('ipAddress')
};

// Initialize the application
function init() {
    setupEventListeners();
    updateDisplayStatus();
    getLocalIP();
    
    // Check connection status every 10 seconds
    setInterval(checkConnection, 10000);
}

// Set up event listeners
function setupEventListeners() {
    // Button event listeners
    elements.showTimeBtn.addEventListener('click', () => showTime());
    elements.showSysInfoBtn.addEventListener('click', () => showSystemInfo());
    elements.showWeatherBtn.addEventListener('click', () => showWeather());
    elements.clearScreenBtn.addEventListener('click', () => clearScreen());
    elements.sendTextBtn.addEventListener('click', () => sendCustomText());
    elements.uploadImageBtn.addEventListener('click', () => uploadImage());
    
    // Enter key in text area to send text
    elements.customText.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            sendCustomText();
        }
    });
}

// API request helper function
async function apiRequest(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(API_BASE + endpoint, options);
        const result = await response.json();
        
        return result;
    } catch (error) {
        console.error('API request failed:', error);
        return { status: 'error', message: 'Network error: ' + error.message };
    }
}

// Update status messages
function addStatusMessage(message, type = 'info') {
    const statusDiv = document.createElement('div');
    statusDiv.className = `status-message ${type}`;
    
    const timestamp = new Date().toLocaleTimeString();
    statusDiv.innerHTML = `<strong>[${timestamp}]</strong> ${message}`;
    
    elements.statusMessages.appendChild(statusDiv);
    
    // Auto scroll to bottom
    elements.statusMessages.scrollTop = elements.statusMessages.scrollHeight;
    
    // Keep only the last 20 messages
    if (elements.statusMessages.children.length > 20) {
        elements.statusMessages.removeChild(elements.statusMessages.firstChild);
    }
}

// Update current display mode
async function updateDisplayStatus() {
    try {
        const result = await apiRequest('/display/current');
        if (result.status === 'success') {
            elements.currentMode.textContent = result.mode || '未知';
        }
    } catch (error) {
        console.error('Failed to update display status:', error);
    }
}

// Check connection status
async function checkConnection() {
    try {
        const result = await apiRequest('/display/status');
        if (result.status === 'success') {
            elements.statusIndicator.textContent = '已连接';
            elements.statusIndicator.className = 'connected';
        } else {
            elements.statusIndicator.textContent = '断开连接';
            elements.statusIndicator.className = 'disconnected';
        }
    } catch (error) {
        elements.statusIndicator.textContent = '连接失败';
        elements.statusIndicator.className = 'disconnected';
    }
}

// Get local IP address
function getLocalIP() {
    // Try to get IP from the server (will be done via backend)
    // For now, we'll show a placeholder
    elements.ipAddress.textContent = window.location.hostname || 'localhost';
}

// API call functions
async function showTime() {
    addStatusMessage('发送显示时间请求...');
    
    const result = await apiRequest('/display/time', 'POST');
    
    if (result.status === 'success') {
        addStatusMessage(result.message, 'success');
        elements.currentMode.textContent = '时间';
    } else {
        addStatusMessage(`错误: ${result.message}`, 'error');
    }
}

async function showSystemInfo() {
    addStatusMessage('发送显示系统信息请求...');
    
    const result = await apiRequest('/display/system_info', 'POST');
    
    if (result.status === 'success') {
        addStatusMessage(result.message, 'success');
        elements.currentMode.textContent = '系统信息';
    } else {
        addStatusMessage(`错误: ${result.message}`, 'error');
    }
}

async function showWeather() {
    addStatusMessage('发送显示天气请求...');
    
    const result = await apiRequest('/display/weather', 'POST');
    
    if (result.status === 'success') {
        addStatusMessage(result.message, 'success');
        elements.currentMode.textContent = '天气';
    } else {
        addStatusMessage(`错误: ${result.message}`, 'error');
    }
}

async function clearScreen() {
    addStatusMessage('发送清屏请求...');
    
    const result = await apiRequest('/display/clear', 'POST');
    
    if (result.status === 'success') {
        addStatusMessage(result.message, 'success');
        elements.currentMode.textContent = '清屏';
    } else {
        addStatusMessage(`错误: ${result.message}`, 'error');
    }
}

async function sendCustomText() {
    const text = elements.customText.value.trim();
    
    if (!text) {
        addStatusMessage('请先输入要显示的文本', 'error');
        return;
    }
    
    addStatusMessage('发送自定义文本请求...');
    
    const result = await apiRequest('/display/text', 'POST', {
        text: text
    });
    
    if (result.status === 'success') {
        addStatusMessage(result.message, 'success');
        elements.currentMode.textContent = '文本';
    } else {
        addStatusMessage(`错误: ${result.message}`, 'error');
    }
}

async function uploadImage() {
    const fileInput = elements.imageUpload;
    const file = fileInput.files[0];
    
    if (!file) {
        addStatusMessage('请先选择一张图片', 'error');
        return;
    }
    
    // Check if file is an image
    if (!file.type.startsWith('image/')) {
        addStatusMessage('请选择有效的图片文件', 'error');
        return;
    }
    
    addStatusMessage('上传图片中...');
    
    const formData = new FormData();
    formData.append('image', file);
    
    try {
        const response = await fetch(API_BASE + '/display/image', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            addStatusMessage(result.message, 'success');
            elements.currentMode.textContent = '图片';
        } else {
            addStatusMessage(`错误: ${result.message}`, 'error');
        }
    } catch (error) {
        addStatusMessage(`上传错误: ${error.message}`, 'error');
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', init);