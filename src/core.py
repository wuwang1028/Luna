"""
Luna 核心逻辑模块
负责流程执行和任务调度
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from .profile import Profile, ProfileManager
from .utils import (
    setup_logger, validate_domain, read_file_lines,
    ask_yes_no, print_header, print_section, print_success,
    print_error, print_info, print_warning, write_file_lines
)
from .config import get_output_dir, get_log_file
from .tools_wrapper import get_tool_wrapper
from .data_processor import DataProcessor


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
        
        # 创建数据处理器
        data_processor = DataProcessor(target, output_dir)
        
        # 用于存储中间结果
        context = {
            'target': target,
            'output_dir': output_dir,
            'subdomains': [],
            'urls': [],
            'ips': [],
            'ports': [],
            'http_probes': []
        }
        
        # 执行每个工具
        for tool_config in profile.tools:
            tool_name = tool_config['name']
            alias = tool_config.get('alias', tool_name)
            params = tool_config['params']
            
            print_section(f"执行 {alias}")
            
            # 执行工具
            success = self._execute_tool(
                tool_name, alias, target, params, 
                output_dir, context, data_processor
            )
            
            if not success:
                print_error(f"{alias} 执行失败")
                # 根据工具类型决定是否继续
                if self._is_critical_tool(tool_name):
                    print_error("关键工具失败，终止流程")
                    return False
                else:
                    print_warning("非关键工具失败，继续执行")
            else:
                print_success(f"{alias} 执行完成")
        
        # 生成汇总
        summary = data_processor.generate_summary()
        self.logger.info(f"数据汇总: {summary}")
        
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
    
    def _execute_tool(self, tool_name: str, alias: str, target: str, 
                     params: Dict[str, Any], output_dir: Path, 
                     context: Dict[str, Any], data_processor: DataProcessor) -> bool:
        """
        执行单个工具
        
        Args:
            tool_name: 工具名称
            alias: 工具别名
            target: 目标
            params: 参数
            output_dir: 输出目录
            context: 上下文数据
            data_processor: 数据处理器
        
        Returns:
            bool: 是否成功
        """
        try:
            # 获取工具封装
            wrapper = get_tool_wrapper(tool_name, output_dir)
            
            # 准备目标输入
            tool_target = self._prepare_tool_target(tool_name, target, context)
            
            # 执行工具
            result = wrapper.execute(tool_target, params)
            
            if not result.success:
                self.logger.error(f"{alias} 执行失败: {result.error}")
                return False
            
            # 处理结果
            self._process_tool_result(tool_name, alias, result, context, data_processor)
            
            return True
            
        except Exception as e:
            self.logger.exception(f"执行 {alias} 时发生异常: {e}")
            return False
    
    def _prepare_tool_target(self, tool_name: str, target: str, context: Dict[str, Any]) -> str:
        """
        为工具准备目标输入
        
        Args:
            tool_name: 工具名称
            target: 原始目标
            context: 上下文数据
        
        Returns:
            str: 工具的目标输入（可能是文件路径）
        """
        # 子域名收集工具直接使用目标域名
        if tool_name in ['oneforall', 'puzzle']:
            return target
        
        # 目录挖掘工具使用子域名列表
        if tool_name in ['dirsearch', 'ffuf']:
            if context['subdomains']:
                # 创建子域名文件
                subdomain_file = context['output_dir'] / 'subdomains_for_scan.txt'
                # 为子域名添加http://前缀
                urls = [f"http://{sub}" for sub in context['subdomains']]
                write_file_lines(subdomain_file, urls)
                return str(subdomain_file)
            else:
                return target
        
        # HTTP探测工具
        if tool_name == 'httpx':
            # 如果有URL列表，使用URL列表
            if context['urls']:
                url_file = context['output_dir'] / 'urls_for_probe.txt'
                write_file_lines(url_file, context['urls'])
                return str(url_file)
            # 如果有子域名，使用子域名
            elif context['subdomains']:
                subdomain_file = context['output_dir'] / 'subdomains_for_probe.txt'
                urls = [f"http://{sub}" for sub in context['subdomains']]
                write_file_lines(subdomain_file, urls)
                return str(subdomain_file)
            else:
                return target
        
        # 端口扫描工具使用IP列表
        if tool_name in ['txportmap', 'fscan']:
            if context['ips']:
                ip_file = context['output_dir'] / 'ips_for_scan.txt'
                write_file_lines(ip_file, context['ips'])
                return str(ip_file)
            else:
                return target
        
        return target
    
    def _process_tool_result(self, tool_name: str, alias: str, result: Any,
                            context: Dict[str, Any], data_processor: DataProcessor):
        """
        处理工具执行结果
        
        Args:
            tool_name: 工具名称
            alias: 工具别名
            result: 工具执行结果
            context: 上下文数据
            data_processor: 数据处理器
        """
        data = result.data
        
        # 处理子域名收集结果
        if tool_name in ['oneforall', 'puzzle']:
            if tool_name == 'oneforall':
                subdomains = data_processor.process_subdomain_results(
                    oneforall_data=data
                )
            else:  # puzzle
                subdomains = data_processor.process_subdomain_results(
                    puzzle_data=data
                )
                # puzzle还会返回IP
                if 'ips' in data:
                    context['ips'].extend(data['ips'])
                    context['ips'] = list(set(context['ips']))  # 去重
            
            context['subdomains'].extend(subdomains)
            context['subdomains'] = list(set(context['subdomains']))  # 去重
            print_info(f"当前共有 {len(context['subdomains'])} 个子域名")
        
        # 处理目录挖掘结果
        elif tool_name in ['dirsearch', 'ffuf']:
            if tool_name == 'dirsearch':
                urls = data_processor.process_directory_results(dirsearch_data=data)
            else:  # ffuf
                urls = data_processor.process_directory_results(ffuf_data=data)
            
            context['urls'].extend(urls)
            context['urls'] = list(set(context['urls']))  # 去重
            print_info(f"当前共有 {len(context['urls'])} 个URL")
        
        # 处理HTTP探测结果
        elif tool_name == 'httpx':
            probes = data_processor.process_http_probe_results(data, alias)
            context['http_probes'].extend(probes)
            print_info(f"探测到 {len(probes)} 个HTTP服务")
        
        # 处理端口扫描结果
        elif tool_name in ['txportmap', 'fscan']:
            if tool_name == 'txportmap':
                ports = data_processor.process_port_scan_results(txportmap_data=data)
            else:  # fscan
                ports = data_processor.process_port_scan_results(fscan_data=data)
            
            context['ports'].extend(ports)
            print_info(f"当前共有 {len(context['ports'])} 个开放端口")
    
    def _is_critical_tool(self, tool_name: str) -> bool:
        """
        判断工具是否为关键工具（失败则终止流程）
        
        Args:
            tool_name: 工具名称
        
        Returns:
            bool: 是否为关键工具
        """
        # 子域名收集工具是关键工具
        critical_tools = ['oneforall', 'puzzle']
        return tool_name in critical_tools
