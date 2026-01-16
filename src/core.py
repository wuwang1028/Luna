"""
Luna 核心逻辑模块
负责流程执行和任务调度
"""

import logging
from pathlib import Path
from typing import List, Optional

from .profile import Profile, ProfileManager
from .utils import (
    setup_logger, validate_domain, read_file_lines,
    ask_yes_no, print_header, print_section, print_success,
    print_error, print_info, print_warning
)
from .config import get_output_dir, get_log_file


class LunaCore:
    """Luna核心类"""
    
    def __init__(self):
        """初始化Luna核心"""
        self.logger = setup_logger("Luna", get_log_file())
    
    def run_profile(self, profile_name: str, targets: List[str]) -> bool:
        """
        运行流程
        
        Args:
            profile_name: 流程名称
            targets: 目标列表（域名）
        
        Returns:
            bool: 是否成功
        """
        # 加载流程
        profile = Profile.load(profile_name)
        if not profile:
            print_error(f"流程 '{profile_name}' 不存在")
            return False
        
        print_header(f"执行流程: {profile_name}")
        print(f"描述: {profile.description}")
        print(f"目标数量: {len(targets)}")
        print(f"工具数量: {len(profile.tools)}")
        
        # 检查流程是否有参数配置
        if not self._check_profile_params(profile):
            print_info("流程参数未配置，开始配置...")
            profile = self._configure_profile_params(profile)
            profile.save()
        else:
            # 询问是否使用上次的参数
            if not ask_yes_no("使用上次的参数?", default=True):
                print_info("重新配置参数...")
                profile = self._configure_profile_params(profile)
                
                if ask_yes_no("保存覆盖原参数?", default=True):
                    profile.save()
                    print_success("参数已更新")
        
        # 执行流程
        success_count = 0
        failed_count = 0
        
        for idx, target in enumerate(targets, 1):
            print_header(f"[{idx}/{len(targets)}] 处理目标: {target}")
            
            if self._execute_profile_for_target(profile, target):
                success_count += 1
                print_success(f"{target} 处理完成")
            else:
                failed_count += 1
                print_error(f"{target} 处理失败")
        
        # 总结
        print_header("执行完成")
        print(f"成功: {success_count}")
        print(f"失败: {failed_count}")
        
        return failed_count == 0
    
    def _check_profile_params(self, profile: Profile) -> bool:
        """
        检查流程是否已配置参数
        
        Args:
            profile: 流程对象
        
        Returns:
            bool: 是否已配置
        """
        for tool in profile.tools:
            params = tool.get('params', {})
            if not params:
                return False
            
            # 检查是否有必须配置的参数（值为None）
            for key, value in params.items():
                if value is None:
                    return False
        
        return True
    
    def _configure_profile_params(self, profile: Profile) -> Profile:
        """
        配置流程参数
        
        Args:
            profile: 流程对象
        
        Returns:
            Profile: 配置后的流程对象
        """
        from .profile import ProfileManager
        
        for tool in profile.tools:
            tool_name = tool['name']
            params = ProfileManager._configure_tool_params(tool_name)
            tool['params'] = params
        
        return profile
    
    def _execute_profile_for_target(self, profile: Profile, target: str) -> bool:
        """
        为单个目标执行流程
        
        Args:
            profile: 流程对象
            target: 目标域名
        
        Returns:
            bool: 是否成功
        """
        # 创建输出目录
        output_dir = get_output_dir(target)
        self.logger.info(f"开始处理目标: {target}")
        self.logger.info(f"输出目录: {output_dir}")
        
        # 执行每个工具
        for tool_config in profile.tools:
            tool_name = tool_config['name']
            alias = tool_config.get('alias', tool_name)
            params = tool_config['params']
            
            print_section(f"执行 {alias}")
            
            # TODO: 这里需要实现工具调用逻辑
            # 目前只是占位
            print_info(f"工具: {tool_name}")
            print_info(f"参数: {params}")
            print_warning("工具调用功能尚未实现")
            
            # 模拟成功
            print_success(f"{alias} 执行完成")
        
        return True
    
    def create_profile(self, name: Optional[str] = None, 
                      from_profile: Optional[str] = None) -> bool:
        """
        创建新流程
        
        Args:
            name: 流程名称
            from_profile: 基于哪个流程创建
        
        Returns:
            bool: 是否成功
        """
        try:
            profile = ProfileManager.create_profile_interactive(name, from_profile)
            profile.save()
            print_success(f"流程 '{profile.name}' 创建成功")
            return True
        except KeyboardInterrupt:
            print_error("\n创建已取消")
            return False
        except Exception as e:
            print_error(f"创建失败: {e}")
            self.logger.exception("创建流程时发生错误")
            return False
    
    def list_profiles(self):
        """列出所有流程"""
        profiles = ProfileManager.list_profiles()
        
        if not profiles:
            print_info("暂无流程")
            return
        
        print_header("可用流程")
        
        # 内置流程
        builtin = ['default', 'quick', 'deep']
        
        print("内置流程:")
        for name in builtin:
            if name in profiles:
                profile = Profile.load(name)
                if profile:
                    print(f"  - {name:<15} {profile.description}")
        
        # 自定义流程
        custom = [p for p in profiles if p not in builtin]
        if custom:
            print("\n自定义流程:")
            for name in custom:
                profile = Profile.load(name)
                if profile:
                    print(f"  - {name:<15} {profile.description}")
    
    def show_profile(self, name: str):
        """
        显示流程详情
        
        Args:
            name: 流程名称
        """
        profile = Profile.load(name)
        if not profile:
            print_error(f"流程 '{name}' 不存在")
            return
        
        profile.display()
    
    def delete_profile(self, name: str) -> bool:
        """
        删除流程
        
        Args:
            name: 流程名称
        
        Returns:
            bool: 是否成功
        """
        # 检查是否为内置流程
        if name in ['default', 'quick', 'deep']:
            print_error("不能删除内置流程")
            return False
        
        if not ProfileManager.profile_exists(name):
            print_error(f"流程 '{name}' 不存在")
            return False
        
        # 确认删除
        if not ask_yes_no(f"确定要删除流程 '{name}'?", default=False):
            print_info("已取消")
            return False
        
        if ProfileManager.delete_profile(name):
            print_success(f"流程 '{name}' 已删除")
            return True
        else:
            print_error("删除失败")
            return False
    
    def parse_targets(self, target: Optional[str] = None, 
                     target_file: Optional[str] = None) -> List[str]:
        """
        解析目标
        
        Args:
            target: 单个目标或逗号分隔的多个目标
            target_file: 目标文件路径
        
        Returns:
            List[str]: 目标列表
        """
        targets = []
        
        # 从命令行参数获取
        if target:
            # 支持逗号分隔
            for t in target.split(','):
                t = t.strip()
                if t and validate_domain(t):
                    targets.append(t)
                elif t:
                    print_warning(f"无效的域名: {t}")
        
        # 从文件获取
        if target_file:
            file_path = Path(target_file)
            if file_path.exists():
                lines = read_file_lines(file_path)
                for line in lines:
                    if validate_domain(line):
                        targets.append(line)
                    else:
                        print_warning(f"无效的域名: {line}")
            else:
                print_error(f"文件不存在: {target_file}")
        
        # 去重
        targets = list(set(targets))
        
        return targets
