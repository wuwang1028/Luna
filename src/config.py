"""
Luna 配置管理模块
负责管理全局配置、路径和常量
"""

import os
from pathlib import Path

# Luna根目录
LUNA_ROOT = Path(__file__).parent.parent.absolute()

# 核心目录
TOOLS_DIR = LUNA_ROOT / "tools"
PROFILES_DIR = LUNA_ROOT / "profiles"
OUTPUTS_DIR = LUNA_ROOT / "outputs"
LOGS_DIR = LUNA_ROOT / "logs"
CONFIG_DIR = LUNA_ROOT / "config"

# 确保目录存在
for directory in [TOOLS_DIR, PROFILES_DIR, OUTPUTS_DIR, LOGS_DIR, CONFIG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# 工具路径映射
TOOL_PATHS = {
    "oneforall": TOOLS_DIR / "OneForAll-master" / "oneforall.py",
    "puzzle": TOOLS_DIR / "puzzle-master" / "puzzle",
    "httpx": TOOLS_DIR / "httpx-dev" / "httpx",
    "ffuf": TOOLS_DIR / "ffuf-master" / "ffuf",
    "dirsearch": TOOLS_DIR / "dirsearch-master" / "dirsearch.py",
    "fscan": TOOLS_DIR / "fscan-main" / "fscan",
    "txportmap": TOOLS_DIR / "TXPortMap-main" / "TxPortMap",
}

# 工具类型（Python或Go）
TOOL_TYPES = {
    "oneforall": "python",
    "puzzle": "go",
    "httpx": "go",
    "ffuf": "go",
    "dirsearch": "python",
    "fscan": "go",
    "txportmap": "go",
}

# 工具信息
TOOL_INFO = {
    "oneforall": {
        "name": "OneForAll",
        "language": "Python",
        "function": "子域名收集",
        "description": "专业子域名枚举工具，多数据源"
    },
    "puzzle": {
        "name": "puzzle",
        "language": "Go",
        "function": "子域名收集 + 综合扫描",
        "description": "一体化信息收集，可同时获取IP"
    },
    "httpx": {
        "name": "httpx",
        "language": "Go",
        "function": "HTTP探测",
        "description": "快速HTTP服务探测，获取状态码和标题"
    },
    "dirsearch": {
        "name": "dirsearch",
        "language": "Python",
        "function": "目录爆破",
        "description": "Web路径发现，支持递归"
    },
    "ffuf": {
        "name": "ffuf",
        "language": "Go",
        "function": "目录爆破/Web模糊测试",
        "description": "高速模糊测试，功能强大"
    },
    "fscan": {
        "name": "fscan",
        "language": "Go",
        "function": "内网综合扫描",
        "description": "端口扫描+漏洞检测+爆破"
    },
    "txportmap": {
        "name": "TXPortMap",
        "language": "Go",
        "function": "端口扫描",
        "description": "快速端口扫描和指纹识别"
    }
}

# 邮件域名过滤规则
EMAIL_PATTERNS = [
    r'^mail\.',
    r'^smtp\.',
    r'^pop\.',
    r'^pop3\.',
    r'^imap\.',
    r'^webmail\.',
    r'^email\.',
    r'^mx\.',
    r'^mx[0-9]+\.',
]

# 日志配置
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_LEVEL = 'INFO'

# 默认参数配置
DEFAULT_PARAMS = {
    "oneforall": {
        "brute": True,
        "dns": True,
        "req": True,
        "port": "default",
        "valid": True,
        "path": None  # 字典路径，需要用户指定
    },
    "puzzle": {
        "mode": "domain",
        "timeout": 10,
        "l3": False,
        "ping": False,
        "pt": 500,
        "wt": 25
    },
    "httpx": {
        "threads": 50,
        "timeout": 10,
        "status_code": True,
        "title": True,
        "tech_detect": False,
        "follow_redirects": False
    },
    "dirsearch": {
        "threads": 50,
        "timeout": 10,
        "recursive": False,
        "recursion_depth": 2,
        "exclude_status": "404,403",
        "wordlist": None  # 字典路径，需要用户指定
    },
    "ffuf": {
        "threads": 40,
        "timeout": 10,
        "mc": "200,301,302,403",
        "recursion": False,
        "recursion_depth": 2,
        "wordlist": None  # 字典路径，需要用户指定
    },
    "fscan": {
        "threads": 100,
        "timeout": 3,
        "port": "top1000",
        "no_ping": False,
        "web_scan": True
    },
    "txportmap": {
        "port_range": "top1000",
        "threads": 1000,
        "timeout": 3
    }
}


def get_tool_path(tool_name):
    """获取工具路径"""
    return TOOL_PATHS.get(tool_name)


def get_tool_type(tool_name):
    """获取工具类型"""
    return TOOL_TYPES.get(tool_name)


def get_tool_info(tool_name):
    """获取工具信息"""
    return TOOL_INFO.get(tool_name, {})


def get_default_params(tool_name):
    """获取工具默认参数"""
    return DEFAULT_PARAMS.get(tool_name, {}).copy()


def get_output_dir(domain):
    """获取域名的输出目录"""
    output_dir = OUTPUTS_DIR / domain
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def get_log_file(domain=None):
    """获取日志文件路径"""
    if domain:
        return LOGS_DIR / f"{domain}.log"
    else:
        return LOGS_DIR / "luna.log"
