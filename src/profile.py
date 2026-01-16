"""
Luna 流程管理模块
负责流程的创建、加载、保存和管理
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .config import PROFILES_DIR, TOOL_INFO, get_default_params
from .utils import (
    load_json, save_json, ask_yes_no, ask_input, 
    ask_choice, print_header, print_section, print_success,
    print_error, print_info
)


class Profile:
    """流程类"""
    
    def __init__(self, name: str, description: str = "", tools: List[Dict] = None):
        """
        初始化流程
        
        Args:
            name: 流程名称
            description: 流程描述
            tools: 工具列表
        """
        self.name = name
        self.description = description
        self.tools = tools or []
        self.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.updated_at = self.created_at
    
    def add_tool(self, tool_name: str, params: Dict[str, Any], 
                 alias: Optional[str] = None, description: str = ""):
        """
        添加工具到流程
        
        Args:
            tool_name: 工具名称
            params: 工具参数
            alias: 工具别名（用于多次调用同一工具）
            description: 工具用途描述
        """
        order = len(self.tools) + 1
        
        tool_config = {
            "name": tool_name,
            "order": order,
            "alias": alias,
            "description": description,
            "params": params
        }
        
        self.tools.append(tool_config)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tools": self.tools
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Profile':
        """从字典创建流程"""
        profile = cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            tools=data.get("tools", [])
        )
        profile.created_at = data.get("created_at", profile.created_at)
        profile.updated_at = data.get("updated_at", profile.updated_at)
        return profile
    
    def save(self):
        """保存流程到文件"""
        file_path = PROFILES_DIR / f"{self.name}.json"
        self.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_json(file_path, self.to_dict())
        print_success(f"流程已保存到: {file_path}")
    
    @classmethod
    def load(cls, name: str) -> Optional['Profile']:
        """
        从文件加载流程
        
        Args:
            name: 流程名称
        
        Returns:
            Profile: 流程对象，如果不存在则返回None
        """
        file_path = PROFILES_DIR / f"{name}.json"
        if not file_path.exists():
            return None
        
        data = load_json(file_path)
        return cls.from_dict(data)
    
    def display(self):
        """显示流程详情"""
        print_header(f"流程: {self.name}")
        print(f"描述: {self.description}")
        print(f"创建时间: {self.created_at}")
        print(f"最后修改: {self.updated_at}")
        print(f"\n包含的工具 ({len(self.tools)}个):")
        
        for tool in self.tools:
            tool_name = tool['name']
            alias = tool.get('alias')
            desc = tool.get('description', '')
            params = tool.get('params', {})
            
            display_name = f"{tool_name} (别名: {alias})" if alias else tool_name
            print(f"\n  {tool['order']}. {display_name}")
            if desc:
                print(f"     用途: {desc}")
            print(f"     参数:")
            for key, value in params.items():
                print(f"       - {key}: {value}")


class ProfileManager:
    """流程管理器"""
    
    @staticmethod
    def list_profiles() -> List[str]:
        """
        列出所有流程
        
        Returns:
            List[str]: 流程名称列表
        """
        profiles = []
        for file_path in PROFILES_DIR.glob("*.json"):
            profiles.append(file_path.stem)
        return sorted(profiles)
    
    @staticmethod
    def profile_exists(name: str) -> bool:
        """
        检查流程是否存在
        
        Args:
            name: 流程名称
        
        Returns:
            bool: 是否存在
        """
        file_path = PROFILES_DIR / f"{name}.json"
        return file_path.exists()
    
    @staticmethod
    def delete_profile(name: str) -> bool:
        """
        删除流程
        
        Args:
            name: 流程名称
        
        Returns:
            bool: 是否成功删除
        """
        file_path = PROFILES_DIR / f"{name}.json"
        if not file_path.exists():
            return False
        
        file_path.unlink()
        return True
    
    @staticmethod
    def create_profile_interactive(name: Optional[str] = None, 
                                   from_profile: Optional[str] = None) -> Profile:
        """
        交互式创建流程
        
        Args:
            name: 流程名称（如果为None则询问）
            from_profile: 基于哪个流程创建（如果为None则从头创建）
        
        Returns:
            Profile: 创建的流程对象
        """
        print_header("创建新流程")
        
        # 获取流程名称
        if not name:
            while True:
                name = ask_input("流程名称", required=True)
                if ProfileManager.profile_exists(name):
                    print_error(f"流程 '{name}' 已存在，请使用其他名称")
                else:
                    break
        
        # 获取流程描述
        description = ask_input("流程描述 (可选)", default="")
        
        # 如果基于现有流程创建
        if from_profile:
            base_profile = Profile.load(from_profile)
            if not base_profile:
                print_error(f"流程 '{from_profile}' 不存在")
                from_profile = None
        
        # 选择工具
        if from_profile:
            print_info(f"基于流程 '{from_profile}' 创建")
            tools = ProfileManager._select_tools_from_existing(base_profile)
        else:
            tools = ProfileManager._select_tools()
        
        # 创建流程对象
        profile = Profile(name=name, description=description)
        
        # 配置每个工具的参数
        print_section("配置工具参数")
        
        # 处理同一工具多次调用
        tool_counts = {}
        for tool_name in tools:
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
        
        tool_instances = {}
        for tool_name in tools:
            # 如果工具被多次使用，需要设置别名
            if tool_counts[tool_name] > 1:
                instance_num = tool_instances.get(tool_name, 0) + 1
                tool_instances[tool_name] = instance_num
                
                if instance_num == 1:
                    print_info(f"检测到 {tool_name} 被添加了{tool_counts[tool_name]}次")
                
                alias = ask_input(
                    f"为 {tool_name} (第{instance_num}次调用) 设置别名",
                    default=f"{tool_name}_{instance_num}"
                )
            else:
                alias = None
            
            # 配置参数
            params = ProfileManager._configure_tool_params(
                tool_name, 
                from_profile=base_profile if from_profile else None
            )
            
            # 获取用途描述
            tool_desc = ask_input(f"{tool_name} 用途描述 (可选)", default="")
            
            # 添加到流程
            profile.add_tool(tool_name, params, alias, tool_desc)
        
        return profile
    
    @staticmethod
    def _select_tools() -> List[str]:
        """
        选择要使用的工具
        
        Returns:
            List[str]: 工具名称列表
        """
        print_section("选择工具")
        
        # 显示可用工具
        tools = list(TOOL_INFO.keys())
        print("可用工具:")
        for i, tool_name in enumerate(tools, 1):
            info = TOOL_INFO[tool_name]
            print(f"  {i}. {tool_name:<15} - {info['function']}")
            print(f"     {info['description']}")
        
        # 用户选择
        while True:
            selection = ask_input(
                "\n请选择要使用的工具 (用逗号分隔, 如: 1,3,5 或 puzzle,httpx,ffuf)",
                required=True
            )
            
            selected_tools = []
            try:
                # 尝试解析为数字
                indices = [int(x.strip()) for x in selection.split(',')]
                for idx in indices:
                    if 1 <= idx <= len(tools):
                        selected_tools.append(tools[idx - 1])
                    else:
                        print_error(f"无效的编号: {idx}")
                        selected_tools = []
                        break
            except ValueError:
                # 尝试解析为工具名
                names = [x.strip() for x in selection.split(',')]
                for name in names:
                    if name in tools:
                        selected_tools.append(name)
                    else:
                        print_error(f"未知的工具: {name}")
                        selected_tools = []
                        break
            
            if selected_tools:
                # 显示选择的工具
                print("\n已选择:")
                for i, tool_name in enumerate(selected_tools, 1):
                    info = TOOL_INFO[tool_name]
                    print(f"  {i}. {tool_name} ({info['function']})")
                
                # 确认顺序
                if ask_yes_no("\n是否调整执行顺序?", default=False):
                    selected_tools = ProfileManager._reorder_tools(selected_tools)
                
                return selected_tools
            else:
                print_error("请重新选择")
    
    @staticmethod
    def _select_tools_from_existing(base_profile: Profile) -> List[str]:
        """
        从现有流程选择工具
        
        Args:
            base_profile: 基础流程
        
        Returns:
            List[str]: 工具名称列表
        """
        print("原流程包含的工具:")
        for i, tool in enumerate(base_profile.tools, 1):
            tool_name = tool['name']
            alias = tool.get('alias')
            display_name = f"{tool_name} (别名: {alias})" if alias else tool_name
            print(f"  {i}. {display_name}")
        
        if ask_yes_no("\n是否修改工具组合?", default=False):
            return ProfileManager._select_tools()
        else:
            # 保持原有工具
            return [tool['name'] for tool in base_profile.tools]
    
    @staticmethod
    def _reorder_tools(tools: List[str]) -> List[str]:
        """
        调整工具执行顺序
        
        Args:
            tools: 工具列表
        
        Returns:
            List[str]: 调整后的工具列表
        """
        print("\n当前顺序:")
        for i, tool in enumerate(tools, 1):
            print(f"  {i}. {tool}")
        
        new_order = ask_input(
            "输入新顺序 (用逗号分隔编号, 如: 2,1,3)",
            required=True
        )
        
        try:
            indices = [int(x.strip()) - 1 for x in new_order.split(',')]
            reordered = [tools[i] for i in indices if 0 <= i < len(tools)]
            
            if len(reordered) == len(tools):
                return reordered
            else:
                print_error("顺序无效，保持原顺序")
                return tools
        except (ValueError, IndexError):
            print_error("输入无效，保持原顺序")
            return tools
    
    @staticmethod
    def _configure_tool_params(tool_name: str, from_profile: Optional[Profile] = None) -> Dict[str, Any]:
        """
        配置工具参数
        
        Args:
            tool_name: 工具名称
            from_profile: 基础流程（如果有）
        
        Returns:
            Dict: 工具参数
        """
        print_section(f"配置 {tool_name}")
        
        # 获取默认参数
        default_params = get_default_params(tool_name)
        
        # 如果基于现有流程，尝试获取原参数
        base_params = None
        if from_profile:
            for tool in from_profile.tools:
                if tool['name'] == tool_name:
                    base_params = tool.get('params', {})
                    break
        
        # 使用基础参数或默认参数
        params = base_params.copy() if base_params else default_params.copy()
        
        # 交互式配置参数
        if ask_yes_no("使用默认参数?", default=True):
            # 只询问关键参数
            params = ProfileManager._ask_key_params(tool_name, params)
        else:
            # 询问所有参数
            params = ProfileManager._ask_all_params(tool_name, params)
        
        return params
    
    @staticmethod
    def _ask_key_params(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        询问关键参数
        
        Args:
            tool_name: 工具名称
            params: 当前参数
        
        Returns:
            Dict: 更新后的参数
        """
        # 定义每个工具的关键参数
        key_params = {
            "oneforall": ["path"],  # 字典路径
            "puzzle": ["timeout"],
            "httpx": ["threads", "timeout"],
            "dirsearch": ["wordlist", "threads"],
            "ffuf": ["wordlist", "threads"],
            "fscan": ["port", "threads"],
            "txportmap": ["port_range"]
        }
        
        keys = key_params.get(tool_name, [])
        
        for key in keys:
            if key in params:
                current = params[key]
                if current is None:
                    # 必须输入的参数
                    params[key] = ask_input(f"{key}", required=True)
                else:
                    # 可选参数
                    new_value = ask_input(f"{key}", default=str(current))
                    # 尝试转换类型
                    if isinstance(current, int):
                        try:
                            params[key] = int(new_value)
                        except ValueError:
                            params[key] = new_value
                    elif isinstance(current, bool):
                        params[key] = new_value.lower() in ['true', 'yes', 'y', '1']
                    else:
                        params[key] = new_value
        
        return params
    
    @staticmethod
    def _ask_all_params(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        询问所有参数
        
        Args:
            tool_name: 工具名称
            params: 当前参数
        
        Returns:
            Dict: 更新后的参数
        """
        print("当前参数:")
        for key, value in params.items():
            print(f"  {key}: {value}")
        
        print("\n逐个配置参数 (直接回车保持默认值):")
        
        for key, current in params.items():
            if current is None:
                params[key] = ask_input(f"{key}", required=True)
            else:
                new_value = ask_input(f"{key}", default=str(current))
                # 尝试转换类型
                if isinstance(current, int):
                    try:
                        params[key] = int(new_value)
                    except ValueError:
                        params[key] = new_value
                elif isinstance(current, bool):
                    params[key] = new_value.lower() in ['true', 'yes', 'y', '1']
                else:
                    params[key] = new_value
        
        return params
