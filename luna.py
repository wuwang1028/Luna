#!/usr/bin/env python3
"""
Luna - 信息收集工具集成平台
主程序入口
"""

import sys
import click
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.core import LunaCore
from src.utils import print_error, print_info, print_header


@click.group()
@click.version_option(version='0.1.0', prog_name='Luna')
def cli():
    """
    Luna - 信息收集工具集成平台
    
    一个模块化的信息收集工具集成平台，支持流程管理、参数绑定和批量处理。
    """
    pass


@cli.command()
@click.option('--profile', '-p', required=True, help='流程名称')
@click.option('--target', '-t', help='目标域名（单个或逗号分隔的多个）')
@click.option('--target-file', '-f', help='目标文件路径（每行一个域名）')
def run(profile, target, target_file):
    """
    运行流程
    
    示例:
    
        luna run --profile default --target example.com
        
        luna run --profile default --target-file domains.txt
        
        luna run -p quick -t example.com,test.com
    """
    if not target and not target_file:
        print_error("请指定目标: --target 或 --target-file")
        sys.exit(1)
    
    core = LunaCore()
    
    # 解析目标
    targets = core.parse_targets(target, target_file)
    
    if not targets:
        print_error("没有有效的目标")
        sys.exit(1)
    
    print_info(f"共 {len(targets)} 个目标")
    
    # 运行流程
    success = core.run_profile(profile, targets)
    
    sys.exit(0 if success else 1)


@cli.command()
@click.argument('name', required=False)
@click.option('--from', 'from_profile', help='基于现有流程创建')
def create(name, from_profile):
    """
    创建新流程
    
    示例:
    
        luna create my-scan
        
        luna create my-scan --from default
        
        luna create  # 交互式创建
    """
    core = LunaCore()
    success = core.create_profile(name, from_profile)
    sys.exit(0 if success else 1)


@cli.command()
def list():
    """
    列出所有流程
    
    示例:
    
        luna list
    """
    core = LunaCore()
    core.list_profiles()


@cli.command()
@click.argument('name')
def show(name):
    """
    显示流程详情
    
    示例:
    
        luna show default
        
        luna show my-scan
    """
    core = LunaCore()
    core.show_profile(name)


@cli.command()
@click.argument('name')
def delete(name):
    """
    删除流程
    
    示例:
    
        luna delete my-scan
    """
    core = LunaCore()
    success = core.delete_profile(name)
    sys.exit(0 if success else 1)


@cli.command()
@click.argument('name')
def edit(name):
    """
    编辑流程（暂未实现）
    
    示例:
    
        luna edit my-scan
    """
    print_error("此功能暂未实现")
    print_info("您可以使用 'luna show <name>' 查看流程详情")
    print_info("然后使用 'luna create <new-name> --from <name>' 基于现有流程创建新流程")
    sys.exit(1)


def main():
    """主函数"""
    try:
        cli()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(130)
    except Exception as e:
        print_error(f"发生错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
