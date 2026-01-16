"""
Luna 工具函数模块
提供通用的辅助函数
"""

import os
import re
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .config import EMAIL_PATTERNS


def setup_logger(name: str, log_file: Optional[Path] = None, level=logging.INFO):
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件路径
        level: 日志级别
    
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件输出
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def is_email_related(subdomain: str) -> bool:
    """
    判断子域名是否为邮件相关域名
    
    Args:
        subdomain: 子域名
    
    Returns:
        bool: 是否为邮件相关域名
    """
    for pattern in EMAIL_PATTERNS:
        if re.match(pattern, subdomain, re.IGNORECASE):
            return True
    return False


def filter_email_domains(subdomains: List[str]) -> List[str]:
    """
    过滤掉邮件相关的子域名
    
    Args:
        subdomains: 子域名列表
    
    Returns:
        List[str]: 过滤后的子域名列表
    """
    filtered = [sub for sub in subdomains if not is_email_related(sub)]
    return filtered


def read_file_lines(file_path: Path) -> List[str]:
    """
    读取文件的所有行（去除空行和空白字符）
    
    Args:
        file_path: 文件路径
    
    Returns:
        List[str]: 文件行列表
    """
    if not file_path.exists():
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    return lines


def write_file_lines(file_path: Path, lines: List[str]):
    """
    将列表写入文件（每行一个元素）
    
    Args:
        file_path: 文件路径
        lines: 要写入的行列表
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(f"{line}\n")


def merge_and_deduplicate(lists: List[List[str]]) -> List[str]:
    """
    合并多个列表并去重
    
    Args:
        lists: 列表的列表
    
    Returns:
        List[str]: 合并去重后的列表
    """
    merged = []
    for lst in lists:
        merged.extend(lst)
    
    # 去重并保持顺序
    seen = set()
    result = []
    for item in merged:
        if item not in seen:
            seen.add(item)
            result.append(item)
    
    return result


def load_json(file_path: Path) -> Dict[str, Any]:
    """
    加载JSON文件
    
    Args:
        file_path: JSON文件路径
    
    Returns:
        Dict: JSON数据
    """
    if not file_path.exists():
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(file_path: Path, data: Dict[str, Any], indent: int = 2):
    """
    保存数据到JSON文件
    
    Args:
        file_path: JSON文件路径
        data: 要保存的数据
        indent: 缩进空格数
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def get_timestamp() -> str:
    """
    获取当前时间戳字符串
    
    Returns:
        str: 格式化的时间戳
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def validate_domain(domain: str) -> bool:
    """
    验证域名格式是否合法
    
    Args:
        domain: 域名
    
    Returns:
        bool: 是否合法
    """
    # 简单的域名格式验证
    pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    return bool(re.match(pattern, domain))


def ask_yes_no(question: str, default: bool = True) -> bool:
    """
    询问用户是/否问题
    
    Args:
        question: 问题文本
        default: 默认值
    
    Returns:
        bool: 用户的选择
    """
    suffix = "(Y/n)" if default else "(y/N)"
    while True:
        response = input(f"{question} {suffix}: ").strip().lower()
        
        if not response:
            return default
        
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("请输入 y 或 n")


def ask_input(question: str, default: Optional[str] = None, required: bool = False) -> str:
    """
    询问用户输入
    
    Args:
        question: 问题文本
        default: 默认值
        required: 是否必须输入
    
    Returns:
        str: 用户输入
    """
    if default:
        prompt = f"{question} (默认: {default}): "
    else:
        prompt = f"{question}: "
    
    while True:
        response = input(prompt).strip()
        
        if not response:
            if default:
                return default
            elif not required:
                return ""
            else:
                print("此项为必填项，请输入")
                continue
        
        return response


def ask_choice(question: str, choices: List[str], default: Optional[str] = None) -> str:
    """
    询问用户选择
    
    Args:
        question: 问题文本
        choices: 选项列表
        default: 默认值
    
    Returns:
        str: 用户选择
    """
    print(f"\n{question}")
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice}")
    
    if default:
        prompt = f"请选择 (默认: {default}): "
    else:
        prompt = "请选择: "
    
    while True:
        response = input(prompt).strip()
        
        if not response and default:
            return default
        
        try:
            index = int(response) - 1
            if 0 <= index < len(choices):
                return choices[index]
            else:
                print(f"请输入 1-{len(choices)} 之间的数字")
        except ValueError:
            # 尝试直接匹配选项
            if response in choices:
                return response
            print("输入无效，请重新输入")


def print_header(text: str):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_section(text: str):
    """打印章节"""
    print(f"\n{'-'*60}")
    print(f"  {text}")
    print(f"{'-'*60}\n")


def print_success(text: str):
    """打印成功信息"""
    print(f"[✓] {text}")


def print_error(text: str):
    """打印错误信息"""
    print(f"[✗] {text}")


def print_info(text: str):
    """打印信息"""
    print(f"[→] {text}")


def print_warning(text: str):
    """打印警告"""
    print(f"[!] {text}")
