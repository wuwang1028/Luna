"""
Luna 工具调用封装模块
提供统一的工具调用接口
"""

import subprocess
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

from .config import get_tool_path, get_tool_type, TOOL_PATHS
from .utils import setup_logger


class ToolResult:
    """工具执行结果"""
    
    def __init__(self, success: bool, output: str = "", error: str = "", 
                 output_file: Optional[Path] = None, data: Optional[Dict] = None):
        """
        初始化工具结果
        
        Args:
            success: 是否成功
            output: 标准输出
            error: 错误输出
            output_file: 输出文件路径
            data: 解析后的数据
        """
        self.success = success
        self.output = output
        self.error = error
        self.output_file = output_file
        self.data = data or {}


class ToolWrapper(ABC):
    """工具封装基类"""
    
    def __init__(self, tool_name: str, output_dir: Path):
        """
        初始化工具封装
        
        Args:
            tool_name: 工具名称
            output_dir: 输出目录
        """
        self.tool_name = tool_name
        self.output_dir = output_dir
        self.tool_path = get_tool_path(tool_name)
        self.tool_type = get_tool_type(tool_name)
        self.logger = setup_logger(f"Luna.{tool_name}")
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查工具是否存在
        if not self.tool_path or not self.tool_path.exists():
            self.logger.warning(f"工具路径不存在: {self.tool_path}")
    
    @abstractmethod
    def build_command(self, target: str, params: Dict[str, Any]) -> List[str]:
        """
        构建命令行参数
        
        Args:
            target: 目标（域名或IP）
            params: 工具参数
        
        Returns:
            List[str]: 命令行参数列表
        """
        pass
    
    @abstractmethod
    def parse_output(self, output: str, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        解析工具输出
        
        Args:
            output: 工具的标准输出
            output_file: 输出文件路径
        
        Returns:
            Dict: 解析后的数据
        """
        pass
    
    def execute(self, target: str, params: Dict[str, Any], timeout: int = 300) -> ToolResult:
        """
        执行工具
        
        Args:
            target: 目标（域名或IP）
            params: 工具参数
            timeout: 超时时间（秒）
        
        Returns:
            ToolResult: 执行结果
        """
        self.logger.info(f"开始执行 {self.tool_name}")
        self.logger.info(f"目标: {target}")
        self.logger.info(f"参数: {params}")
        
        # 构建命令
        try:
            cmd = self.build_command(target, params)
            self.logger.debug(f"命令: {' '.join(cmd)}")
        except Exception as e:
            self.logger.error(f"构建命令失败: {e}")
            return ToolResult(success=False, error=str(e))
        
        # 执行命令
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.output_dir
            )
            
            stdout, stderr = process.communicate(timeout=timeout)
            returncode = process.returncode
            
            self.logger.debug(f"返回码: {returncode}")
            
            # 判断是否成功
            success = returncode == 0
            
            if not success:
                self.logger.error(f"执行失败: {stderr}")
            
            # 解析输出
            output_file = self._get_output_file()
            data = self.parse_output(stdout, output_file)
            
            return ToolResult(
                success=success,
                output=stdout,
                error=stderr,
                output_file=output_file,
                data=data
            )
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"执行超时（{timeout}秒）")
            process.kill()
            return ToolResult(success=False, error=f"执行超时（{timeout}秒）")
        
        except Exception as e:
            self.logger.exception(f"执行异常: {e}")
            return ToolResult(success=False, error=str(e))
    
    def _get_output_file(self) -> Optional[Path]:
        """
        获取输出文件路径（如果存在）
        
        Returns:
            Optional[Path]: 输出文件路径
        """
        # 子类可以重写此方法
        return None
    
    def _build_base_command(self) -> List[str]:
        """
        构建基础命令
        
        Returns:
            List[str]: 基础命令
        """
        if self.tool_type == "python":
            return ["python3", str(self.tool_path)]
        else:
            # Go工具直接执行
            return [str(self.tool_path)]
    
    def _prepare_output_file(self, filename: str) -> Path:
        """
        准备输出文件路径
        
        Args:
            filename: 文件名
        
        Returns:
            Path: 完整的输出文件路径
        """
        output_file = self.output_dir / filename
        
        # 特殊处理：puzzle如果文件存在会拒绝输出
        if self.tool_name == "puzzle" and output_file.exists():
            self.logger.warning(f"删除已存在的输出文件: {output_file}")
            output_file.unlink()
        
        return output_file


class DummyToolWrapper(ToolWrapper):
    """
    虚拟工具封装（用于测试）
    当工具不存在时使用
    """
    
    def build_command(self, target: str, params: Dict[str, Any]) -> List[str]:
        """构建虚拟命令"""
        return ["echo", f"Dummy tool: {self.tool_name} for {target}"]
    
    def parse_output(self, output: str, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """解析虚拟输出"""
        return {
            "tool": self.tool_name,
            "output": output.strip(),
            "note": "This is a dummy tool wrapper for testing"
        }


def get_tool_wrapper(tool_name: str, output_dir: Path) -> ToolWrapper:
    """
    获取工具封装实例
    
    Args:
        tool_name: 工具名称
        output_dir: 输出目录
    
    Returns:
        ToolWrapper: 工具封装实例
    """
    # 导入具体的工具封装类
    from .modules import (
        OneForAllWrapper, PuzzleWrapper, HttpxWrapper,
        DirsearchWrapper, FfufWrapper, FscanWrapper, TXPortMapWrapper
    )
    
    wrapper_map = {
        "oneforall": OneForAllWrapper,
        "puzzle": PuzzleWrapper,
        "httpx": HttpxWrapper,
        "dirsearch": DirsearchWrapper,
        "ffuf": FfufWrapper,
        "fscan": FscanWrapper,
        "txportmap": TXPortMapWrapper
    }
    
    wrapper_class = wrapper_map.get(tool_name)
    
    if wrapper_class:
        return wrapper_class(output_dir)
    else:
        # 返回虚拟封装
        return DummyToolWrapper(tool_name, output_dir)
