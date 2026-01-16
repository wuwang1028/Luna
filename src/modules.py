"""
Luna 工具模块
各工具的具体实现
"""

import json
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional

from .tools_wrapper import ToolWrapper
from .utils import read_file_lines


class OneForAllWrapper(ToolWrapper):
    """OneForAll工具封装"""
    
    def __init__(self, output_dir: Path):
        super().__init__("oneforall", output_dir)
        self.module_dir = output_dir / "oneforall"
        self.module_dir.mkdir(parents=True, exist_ok=True)
    
    def build_command(self, target: str, params: Dict[str, Any]) -> List[str]:
        """构建OneForAll命令"""
        cmd = self._build_base_command()
        
        # 添加目标域名
        cmd.extend(["--target", target])
        
        # 添加参数
        if params.get("brute"):
            cmd.append("--brute")
        
        if params.get("dns"):
            cmd.append("--dns")
        
        if params.get("req"):
            cmd.append("--req")
        
        if params.get("valid"):
            cmd.append("--valid")
        
        # 字典路径
        if params.get("path"):
            cmd.extend(["--path", params["path"]])
        
        # 输出目录
        cmd.extend(["--output", str(self.module_dir)])
        
        return cmd
    
    def parse_output(self, output: str, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """解析OneForAll输出"""
        # OneForAll通常输出CSV文件到results目录
        # 文件名格式: {domain}_YYYY-MM-DD_HH-MM-SS.csv
        
        results_dir = self.tool_path.parent / "results"
        subdomains = []
        
        if results_dir.exists():
            # 查找最新的CSV文件
            csv_files = list(results_dir.glob("*.csv"))
            if csv_files:
                latest_csv = max(csv_files, key=lambda p: p.stat().st_mtime)
                self.logger.info(f"找到OneForAll结果文件: {latest_csv}")
                
                # 解析CSV
                try:
                    with open(latest_csv, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            subdomain = row.get('subdomain', row.get('domain', ''))
                            if subdomain:
                                subdomains.append(subdomain)
                    
                    # 移动文件到输出目录
                    target_file = self.module_dir / latest_csv.name
                    latest_csv.rename(target_file)
                    self.logger.info(f"结果文件已移动到: {target_file}")
                    
                except Exception as e:
                    self.logger.error(f"解析CSV失败: {e}")
        
        return {
            "subdomains": subdomains,
            "count": len(subdomains)
        }


class PuzzleWrapper(ToolWrapper):
    """puzzle工具封装"""
    
    def __init__(self, output_dir: Path):
        super().__init__("puzzle", output_dir)
        self.module_dir = output_dir / "puzzle"
        self.module_dir.mkdir(parents=True, exist_ok=True)
    
    def build_command(self, target: str, params: Dict[str, Any]) -> List[str]:
        """构建puzzle命令"""
        cmd = self._build_base_command()
        
        # 模式
        mode = params.get("mode", "domain")
        cmd.extend(["-m", mode])
        
        # 目标
        cmd.extend(["-d", target])
        
        # 输出文件
        output_file = self._prepare_output_file("puzzle_result.txt")
        cmd.extend(["-o", str(output_file)])
        
        # 超时
        timeout = params.get("timeout", 10)
        cmd.extend(["-t", str(timeout)])
        
        # 三级域名爆破
        if params.get("l3"):
            cmd.append("-l3")
        
        # Ping探测
        if params.get("ping"):
            cmd.append("-ping")
        
        # 端口爆破线程
        pt = params.get("pt", 500)
        cmd.extend(["-pt", str(pt)])
        
        # Web指纹线程
        wt = params.get("wt", 25)
        cmd.extend(["-wt", str(wt)])
        
        return cmd
    
    def parse_output(self, output: str, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """解析puzzle输出"""
        subdomains = []
        ips = []
        
        # 从输出文件读取
        result_file = self.module_dir / "puzzle_result.txt"
        if result_file.exists():
            lines = read_file_lines(result_file)
            
            for line in lines:
                # puzzle输出格式通常是: subdomain [IP]
                parts = line.split()
                if parts:
                    subdomain = parts[0]
                    subdomains.append(subdomain)
                    
                    # 提取IP
                    if len(parts) > 1:
                        ip = parts[1].strip('[]')
                        if ip:
                            ips.append(ip)
        
        return {
            "subdomains": subdomains,
            "ips": list(set(ips)),  # 去重
            "count": len(subdomains)
        }


class HttpxWrapper(ToolWrapper):
    """httpx工具封装"""
    
    def __init__(self, output_dir: Path):
        super().__init__("httpx", output_dir)
        self.module_dir = output_dir / "httpx"
        self.module_dir.mkdir(parents=True, exist_ok=True)
    
    def build_command(self, target: str, params: Dict[str, Any]) -> List[str]:
        """构建httpx命令"""
        cmd = self._build_base_command()
        
        # 目标可以是文件或单个URL
        if Path(target).exists():
            cmd.extend(["-l", target])
        else:
            cmd.extend(["-u", target])
        
        # 线程数
        threads = params.get("threads", 50)
        cmd.extend(["-threads", str(threads)])
        
        # 超时
        timeout = params.get("timeout", 10)
        cmd.extend(["-timeout", str(timeout)])
        
        # 状态码
        if params.get("status_code", True):
            cmd.append("-status-code")
        
        # 标题
        if params.get("title", True):
            cmd.append("-title")
        
        # 技术栈检测
        if params.get("tech_detect", False):
            cmd.append("-tech-detect")
        
        # 跟随重定向
        if params.get("follow_redirects", False):
            cmd.append("-follow-redirects")
        
        # JSON输出
        output_file = self._prepare_output_file("httpx_result.json")
        cmd.extend(["-json", "-o", str(output_file)])
        
        return cmd
    
    def parse_output(self, output: str, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """解析httpx输出"""
        results = []
        
        # 从JSON文件读取
        result_file = self.module_dir / "httpx_result.json"
        if result_file.exists():
            try:
                # httpx输出的是JSONL格式（每行一个JSON对象）
                with open(result_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                item = json.loads(line)
                                result = {
                                    'url': item.get('url', ''),
                                    'status_code': item.get('status-code', item.get('status_code', 0)),
                                    'title': item.get('title', ''),
                                    'content_length': item.get('content-length', item.get('content_length', 0)),
                                    'tech': item.get('tech', [])
                                }
                                results.append(result)
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                self.logger.error(f"解析httpx结果失败: {e}")
        
        return {
            "results": results,
            "count": len(results)
        }


class DirsearchWrapper(ToolWrapper):
    """dirsearch工具封装"""
    
    def __init__(self, output_dir: Path):
        super().__init__("dirsearch", output_dir)
        self.module_dir = output_dir / "dirsearch"
        self.module_dir.mkdir(parents=True, exist_ok=True)
    
    def build_command(self, target: str, params: Dict[str, Any]) -> List[str]:
        """构建dirsearch命令"""
        cmd = self._build_base_command()
        
        # 目标URL或文件
        if Path(target).exists():
            cmd.extend(["-l", target])
        else:
            cmd.extend(["-u", target])
        
        # 字典
        wordlist = params.get("wordlist")
        if wordlist:
            cmd.extend(["-w", wordlist])
        
        # 线程数
        threads = params.get("threads", 50)
        cmd.extend(["-t", str(threads)])
        
        # 超时
        timeout = params.get("timeout", 10)
        cmd.extend(["--timeout", str(timeout)])
        
        # 递归
        if params.get("recursive", False):
            cmd.append("-r")
            depth = params.get("recursion_depth", 2)
            cmd.extend(["--recursion-depth", str(depth)])
        
        # 排除状态码
        exclude_status = params.get("exclude_status", "404,403")
        cmd.extend(["-x", exclude_status])
        
        # JSON输出
        output_file = self._prepare_output_file("dirsearch_result.json")
        cmd.extend(["--format", "json", "-o", str(output_file)])
        
        return cmd
    
    def parse_output(self, output: str, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """解析dirsearch输出"""
        urls = []
        
        # 从JSON文件读取
        result_file = self.module_dir / "dirsearch_result.json"
        if result_file.exists():
            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # dirsearch的JSON格式可能不同，需要适配
                    if isinstance(data, dict):
                        for url, info in data.items():
                            urls.append(url)
                    elif isinstance(data, list):
                        for item in data:
                            if 'url' in item:
                                urls.append(item['url'])
            except Exception as e:
                self.logger.error(f"解析dirsearch结果失败: {e}")
        
        return {
            "urls": urls,
            "count": len(urls)
        }


class FfufWrapper(ToolWrapper):
    """ffuf工具封装"""
    
    def __init__(self, output_dir: Path):
        super().__init__("ffuf", output_dir)
        self.module_dir = output_dir / "ffuf"
        self.module_dir.mkdir(parents=True, exist_ok=True)
    
    def build_command(self, target: str, params: Dict[str, Any]) -> List[str]:
        """构建ffuf命令"""
        cmd = self._build_base_command()
        
        # 目标URL（需要包含FUZZ关键字）
        if "FUZZ" not in target:
            target = target.rstrip('/') + "/FUZZ"
        cmd.extend(["-u", target])
        
        # 字典
        wordlist = params.get("wordlist")
        if wordlist:
            cmd.extend(["-w", wordlist])
        
        # 线程数
        threads = params.get("threads", 40)
        cmd.extend(["-t", str(threads)])
        
        # 超时
        timeout = params.get("timeout", 10)
        cmd.extend(["-timeout", str(timeout)])
        
        # 匹配状态码
        mc = params.get("mc", "200,301,302,403")
        cmd.extend(["-mc", mc])
        
        # 递归
        if params.get("recursion", False):
            cmd.append("-recursion")
            depth = params.get("recursion_depth", 2)
            cmd.extend(["-recursion-depth", str(depth)])
        
        # JSON输出
        output_file = self._prepare_output_file("ffuf_result.json")
        cmd.extend(["-of", "json", "-o", str(output_file)])
        
        return cmd
    
    def parse_output(self, output: str, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """解析ffuf输出"""
        urls = []
        
        # 从JSON文件读取
        result_file = self.module_dir / "ffuf_result.json"
        if result_file.exists():
            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    results = data.get('results', [])
                    for item in results:
                        url = item.get('url', '')
                        if url:
                            urls.append(url)
            except Exception as e:
                self.logger.error(f"解析ffuf结果失败: {e}")
        
        return {
            "urls": urls,
            "results": urls,  # 兼容性
            "count": len(urls)
        }


class FscanWrapper(ToolWrapper):
    """fscan工具封装"""
    
    def __init__(self, output_dir: Path):
        super().__init__("fscan", output_dir)
        self.module_dir = output_dir / "fscan"
        self.module_dir.mkdir(parents=True, exist_ok=True)
    
    def build_command(self, target: str, params: Dict[str, Any]) -> List[str]:
        """构建fscan命令"""
        cmd = self._build_base_command()
        
        # 目标（IP或CIDR）
        cmd.extend(["-h", target])
        
        # 端口
        port = params.get("port", "top1000")
        cmd.extend(["-p", port])
        
        # 线程数
        threads = params.get("threads", 100)
        cmd.extend(["-t", str(threads)])
        
        # 超时
        timeout = params.get("timeout", 3)
        cmd.extend(["-time", str(timeout)])
        
        # 不Ping
        if params.get("no_ping", False):
            cmd.append("-np")
        
        # Web扫描
        if params.get("web_scan", True):
            cmd.append("-web")
        
        # 输出文件
        output_file = self._prepare_output_file("fscan_result.txt")
        cmd.extend(["-o", str(output_file)])
        
        return cmd
    
    def parse_output(self, output: str, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """解析fscan输出"""
        ports = []
        
        # 从输出文件读取
        result_file = self.module_dir / "fscan_result.txt"
        if result_file.exists():
            lines = read_file_lines(result_file)
            
            for line in lines:
                # 简单解析（fscan输出格式较复杂，这里只是示例）
                # 实际需要根据fscan的具体输出格式进行解析
                if "open" in line.lower():
                    # 提取IP和端口信息
                    # 这里需要根据实际输出格式调整
                    pass
        
        return {
            "ports": ports,
            "raw_output": output,
            "count": len(ports)
        }


class TXPortMapWrapper(ToolWrapper):
    """TXPortMap工具封装"""
    
    def __init__(self, output_dir: Path):
        super().__init__("txportmap", output_dir)
        self.module_dir = output_dir / "txportmap"
        self.module_dir.mkdir(parents=True, exist_ok=True)
    
    def build_command(self, target: str, params: Dict[str, Any]) -> List[str]:
        """构建TXPortMap命令"""
        cmd = self._build_base_command()
        
        # 目标（IP或文件）
        if Path(target).exists():
            cmd.extend(["-f", target])
        else:
            cmd.extend(["-h", target])
        
        # 端口范围
        port_range = params.get("port_range", "top1000")
        cmd.extend(["-p", port_range])
        
        # 线程数
        threads = params.get("threads", 1000)
        cmd.extend(["-t", str(threads)])
        
        # 超时
        timeout = params.get("timeout", 3)
        cmd.extend(["-timeout", str(timeout)])
        
        # 输出文件
        output_file = self._prepare_output_file("txportmap_result.txt")
        cmd.extend(["-o", str(output_file)])
        
        return cmd
    
    def parse_output(self, output: str, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """解析TXPortMap输出"""
        ports = []
        
        # 从输出文件读取
        result_file = self.module_dir / "txportmap_result.txt"
        if result_file.exists():
            lines = read_file_lines(result_file)
            
            for line in lines:
                # TXPortMap输出格式: IP:PORT SERVICE
                parts = line.split()
                if len(parts) >= 2:
                    ip_port = parts[0].split(':')
                    if len(ip_port) == 2:
                        port = {
                            'ip': ip_port[0],
                            'port': int(ip_port[1]),
                            'service': parts[1] if len(parts) > 1 else '',
                            'banner': ' '.join(parts[2:]) if len(parts) > 2 else ''
                        }
                        ports.append(port)
        
        return {
            "results": ports,
            "ports": ports,  # 兼容性
            "count": len(ports)
        }
