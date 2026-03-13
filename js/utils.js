/**
 * 天光AI - 工具函数
 */

const Utils = {
    // 日志
    log(message, type = 'info') {
        const logContainer = document.getElementById('trainLog');
        if (!logContainer) return;

        const time = new Date().toLocaleTimeString();
        const entry = document.createElement('div');
        entry.className = `log-entry log-${type}`;
        entry.innerHTML = `<span class="log-time">[${time}]</span> ${message}`;
        logContainer.appendChild(entry);
        logContainer.scrollTop = logContainer.scrollHeight;
    },

    // 清空日志
    clearLog() {
        const logContainer = document.getElementById('trainLog');
        if (logContainer) logContainer.innerHTML = '';
    },

    // 通知
    notify(message, type = 'info') {
        const notification = document.getElementById('notification');
        if (!notification) return;

        notification.textContent = message;
        notification.className = `notification show ${type}`;

        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    },

    // 格式化数字
    formatNumber(num) {
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toFixed(2);
    },

    // 格式化时间
    formatTime(seconds) {
        if (seconds < 60) return `${Math.floor(seconds)}秒`;
        if (seconds < 3600) return `${Math.floor(seconds / 60)}分${Math.floor(seconds % 60)}秒`;
        return `${Math.floor(seconds / 3600)}小时${Math.floor((seconds % 3600) / 60)}分`;
    },

    // 本地存储
    storage: {
        get(key) {
            try {
                return JSON.parse(localStorage.getItem(`tianguang_${key}`));
            } catch {
                return null;
            }
        },
        set(key, value) {
            try {
                localStorage.setItem(`tianguang_${key}`, JSON.stringify(value));
                return true;
            } catch {
                return false;
            }
        },
        remove(key) {
            localStorage.removeItem(`tianguang_${key}`);
        }
    },

    // 文件下载
    downloadJSON(data, filename) {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    },

    // 文件读取
    readFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }
};

// 导出
window.Utils = Utils;
